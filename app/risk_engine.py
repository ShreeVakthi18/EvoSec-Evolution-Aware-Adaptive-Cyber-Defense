"""
Behavioral risk engine for EAACD.

This module preserves the ORIGINAL detection semantics from the prototype:

  - critical endpoints = anything containing "admin", "delete", "payment",
    OR any endpoint accessed fewer than N times that has received a
    destructive method (DELETE/POST).
  - risk score per user = sum of:
        +critical_endpoint_weight   for each historical action against a
                                     critical endpoint
        +destructive_method_weight  for each historical DELETE/POST action
        +high_volume_weight         if the user has more than N total actions
        +admin_without_login_weight if the user touched /admin* without a
                                     prior /login in their history
  - classification thresholds: NORMAL < SUSPICIOUS < ATTACKER

The only behavioral change from the prototype is that thresholds/weights are
now configurable (app.config.settings) instead of hard-coded, and state is
kept under a lock with bounded size/TTL so the process does not grow memory
unboundedly. The scoring formula itself, and the resulting classifications
for the documented test scenarios (TC-01..TC-05), are unchanged.
"""
from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Literal

from app.config import settings

Status = Literal["NORMAL", "SUSPICIOUS", "ATTACKER"]

_DESTRUCTIVE_METHODS = {"DELETE", "POST"}
_CRITICAL_KEYWORDS = ("admin", "delete", "payment")


@dataclass
class EndpointStat:
    count: int = 0
    methods: set[str] = field(default_factory=set)


@dataclass
class Action:
    path: str
    method: str
    timestamp: float


class BehaviorStore:
    """
    Thread-safe, bounded, TTL-evicting store for endpoint stats and per-user
    behavioral history.

    The original prototype used two unbounded module-level dicts with no
    locking. Under concurrent requests (FastAPI runs middleware handlers
    concurrently across requests) that is a race condition, and a
    long-running process would grow memory forever as new client IPs
    appeared. This class keeps the same data shape and detection formula,
    but adds:
      - a lock around all read/modify/write sequences
      - an LRU-style eviction of the oldest-seen users once max_tracked_users
        is exceeded
      - a per-user history cap (max_history_per_user) so a single abusive
        client cannot grow one entry without bound
      - idle-TTL eviction so stale sessions are cleaned up
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.endpoint_stats: dict[str, EndpointStat] = {}
        # OrderedDict lets us evict least-recently-touched users cheaply.
        self._user_behavior: "OrderedDict[str, list[Action]]" = OrderedDict()
        self._last_seen: dict[str, float] = {}

    # ---------------------------------------------------------------
    # Recording
    # ---------------------------------------------------------------
    def record(self, user_id: str, path: str, method: str) -> None:
        now = time.time()
        with self._lock:
            self._evict_stale(now)

            stat = self.endpoint_stats.setdefault(path, EndpointStat())
            stat.count += 1
            stat.methods.add(method)

            history = self._user_behavior.setdefault(user_id, [])
            history.append(Action(path=path, method=method, timestamp=now))
            if len(history) > settings.max_history_per_user:
                # Drop oldest entries first; keeps the "high volume" signal
                # meaningful while bounding memory for a single user.
                del history[: len(history) - settings.max_history_per_user]

            self._user_behavior.move_to_end(user_id)
            self._last_seen[user_id] = now

            self._evict_overflow()

    def _evict_stale(self, now: float) -> None:
        ttl = settings.user_idle_ttl_seconds
        stale = [uid for uid, ts in self._last_seen.items() if now - ts > ttl]
        for uid in stale:
            self._user_behavior.pop(uid, None)
            self._last_seen.pop(uid, None)

    def _evict_overflow(self) -> None:
        max_users = settings.max_tracked_users
        while len(self._user_behavior) > max_users:
            oldest_uid, _ = self._user_behavior.popitem(last=False)
            self._last_seen.pop(oldest_uid, None)

    # ---------------------------------------------------------------
    # Reads (return copies so callers never mutate shared state directly)
    # ---------------------------------------------------------------
    def critical_endpoints(self) -> list[str]:
        with self._lock:
            critical = []
            for path, stat in self.endpoint_stats.items():
                if any(word in path for word in _CRITICAL_KEYWORDS):
                    critical.append(path)
                elif (
                    stat.count < settings.critical_endpoint_min_requests
                    and stat.methods & _DESTRUCTIVE_METHODS
                ):
                    critical.append(path)
            return critical

    def history_for(self, user_id: str) -> list[Action]:
        with self._lock:
            return list(self._user_behavior.get(user_id, []))

    def all_users(self) -> list[str]:
        with self._lock:
            return list(self._user_behavior.keys())

    def request_count(self, user_id: str) -> int:
        with self._lock:
            return len(self._user_behavior.get(user_id, []))


store = BehaviorStore()


def classify_user(risk: int) -> Status:
    if risk >= settings.risk_attacker_threshold:
        return "ATTACKER"
    if risk >= settings.risk_suspicious_threshold:
        return "SUSPICIOUS"
    return "NORMAL"


def detect_suspicious_user(user_id: str) -> int:
    """Compute the cumulative risk score for a user. Formula preserved from
    the original prototype; weights are now configurable."""
    history = store.history_for(user_id)
    critical_endpoints = set(store.critical_endpoints())

    risk = 0
    for action in history:
        if action.path in critical_endpoints:
            risk += settings.risk_critical_endpoint_weight
        if action.method in _DESTRUCTIVE_METHODS:
            risk += settings.risk_destructive_method_weight

    if len(history) > settings.risk_high_volume_request_count:
        risk += settings.risk_high_volume_weight

    paths = [a.path for a in history]
    if any("/admin" in p for p in paths) and "/login" not in paths:
        risk += settings.risk_admin_without_login_weight

    return risk


def is_critical_path(path: str) -> bool:
    return any(word in path for word in _CRITICAL_KEYWORDS)


def dashboard_snapshot() -> list[dict]:
    """Build the payload consumed by /dashboard-data (same shape as before)."""
    result = []
    for user_id in store.all_users():
        risk = detect_suspicious_user(user_id)
        status = classify_user(risk)
        result.append(
            {
                "user": user_id,
                "requests": store.request_count(user_id),
                "risk": risk,
                "status": status,
            }
        )
    return result
