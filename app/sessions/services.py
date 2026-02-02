from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Optional

from ..models import Session


@dataclass(frozen=True)
class DailyPoint:
    day: date
    load: int
    minutes: int


@dataclass(frozen=True)
class WeeklyPoint:
    week_start: date  # Monday
    load: int
    minutes: int


def week_start(d: date) -> date:
    """Return Monday of the week for a given date."""
    return d - timedelta(days=d.weekday())


def daterange(start: date, end: date) -> Iterable[date]:
    """Inclusive date range [start, end]."""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def fetch_sessions(user_id: int, start: date, end: date, activity_id: Optional[int] = None) -> list[Session]:
    q = Session.query.filter(Session.user_id == user_id)
    q = q.filter(Session.session_date >= start, Session.session_date <= end)
    if activity_id is not None:
        q = q.filter(Session.activity_id == activity_id)
    return q.order_by(Session.session_date.asc(), Session.created_at.asc()).all()


def daily_series(sessions: list[Session], start: date, end: date) -> list[DailyPoint]:
    """Return day-by-day totals, filling missing days with zeros."""
    by_day: dict[date, dict[str, int]] = {}
    for s in sessions:
        by_day.setdefault(s.session_date, {"load": 0, "minutes": 0})
        by_day[s.session_date]["load"] += s.load
        by_day[s.session_date]["minutes"] += int(s.duration_min)

    out: list[DailyPoint] = []
    for d in daterange(start, end):
        agg = by_day.get(d, {"load": 0, "minutes": 0})
        out.append(DailyPoint(day=d, load=agg["load"], minutes=agg["minutes"]))
    return out


def rolling_sum(points: list[DailyPoint], window_days: int) -> list[int]:
    """Rolling sum over the last `window_days` days (including the current day)."""
    if window_days <= 0:
        raise ValueError("window_days must be > 0")

    loads = [p.load for p in points]
    out = []
    running = 0
    for i, v in enumerate(loads):
        running += v
        if i >= window_days:
            running -= loads[i - window_days]
        out.append(running)
    return out


def weekly_series(points: list[DailyPoint]) -> list[WeeklyPoint]:
    """Aggregate daily points into weekly points (weeks start on Monday)."""
    by_week: dict[date, dict[str, int]] = {}
    for p in points:
        ws = week_start(p.day)
        by_week.setdefault(ws, {"load": 0, "minutes": 0})
        by_week[ws]["load"] += p.load
        by_week[ws]["minutes"] += p.minutes

    out = []
    for ws in sorted(by_week.keys()):
        out.append(WeeklyPoint(week_start=ws, load=by_week[ws]["load"], minutes=by_week[ws]["minutes"]))
    return out


def acwr(rolling_7: int, rolling_28: int) -> Optional[float]:
    """Acute:Chronic Workload Ratio using rolling sums (7 and 28)."""
    if rolling_28 == 0:
        return None
    return rolling_7 / rolling_28
