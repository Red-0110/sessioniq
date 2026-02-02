from datetime import date, timedelta

from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user

from . import bp
from ..models import Activity
from ..sessions.services import (
    fetch_sessions,
    daily_series,
    rolling_sum,
    weekly_series,
    acwr,
)


@bp.route("/")
def home():
    return redirect(url_for("main.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    # Filter: activity_id can be "all" (default) or an integer
    activity_id_raw = request.args.get("activity_id", "all").strip().lower()
    activity_id = None if activity_id_raw in ("all", "", "none") else int(activity_id_raw)

    # Default time window: last 90 days
    end = date.today()
    start = end - timedelta(days=90)

    activities = (
        Activity.query.filter_by(user_id=current_user.id)
        .order_by(Activity.name.asc())
        .all()
    )

    sessions = fetch_sessions(current_user.id, start=start, end=end, activity_id=activity_id)

    daily = daily_series(sessions, start=start, end=end)
    roll7 = rolling_sum(daily, window_days=7)
    roll28 = rolling_sum(daily, window_days=28)
    weekly = weekly_series(daily)

    latest_7 = roll7[-1] if roll7 else 0
    latest_28 = roll28[-1] if roll28 else 0
    ratio = acwr(latest_7, latest_28)

    # Chart.js payload
    labels = [p.day.isoformat() for p in daily]
    loads = [p.load for p in daily]
    r7 = roll7
    r28 = roll28

    selected_activity_name = "All activities"
    if activity_id is not None:
        match = next((a for a in activities if a.id == activity_id), None)
        selected_activity_name = match.name if match else "Selected activity"

    # ---- Insights ----
    weekly_loads = [w.load for w in weekly]
    wow = None
    trend_4w = None

    if len(weekly_loads) >= 2:
        last = weekly_loads[-1]
        prev = weekly_loads[-2]
        wow = None if prev == 0 else (last - prev) / prev

    if len(weekly_loads) >= 4:
        last4 = weekly_loads[-4:]
        first_half = (last4[0] + last4[1]) / 2
        second_half = (last4[2] + last4[3]) / 2
        trend_4w = None if first_half == 0 else (second_half - first_half) / first_half

    return render_template(
        "dashboard.html",
        activities=activities,
        activity_id_raw=activity_id_raw,
        selected_activity_name=selected_activity_name,
        start=start,
        end=end,
        weekly=weekly,
        latest_7=latest_7,
        latest_28=latest_28,
        ratio=ratio,
        wow=wow,
        trend_4w=trend_4w,
        chart_labels=labels,
        chart_loads=loads,
        chart_r7=r7,
        chart_r28=r28,
    )
