from flask import render_template, redirect, url_for, flash, abort, request, Response
from flask_login import login_required, current_user

from . import bp
from .forms import SessionForm
from ..extensions import db
from ..models import Session, Activity


def _owned_session_or_404(session_id: int) -> Session:
    s = Session.query.get_or_404(session_id)
    if s.user_id != current_user.id:
        abort(403)
    return s


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    activities = (
        Activity.query.filter_by(user_id=current_user.id)
        .order_by(Activity.name.asc())
        .all()
    )

    if not activities:
        flash("Create an activity first (e.g., Tennis, Climbing, Strength).", "info")
        return redirect(url_for("activities.index"))

    form = SessionForm()
    form.activity_id.choices = [(a.id, a.name) for a in activities]

    if form.validate_on_submit():
        s = Session(
            user_id=current_user.id,
            activity_id=form.activity_id.data,
            session_date=form.session_date.data,
            duration_min=form.duration_min.data,
            rpe=form.rpe.data,
            notes=(form.notes.data.strip() if form.notes.data else None),
        )
        db.session.add(s)
        db.session.commit()
        flash("Session saved.", "success")
        return redirect(url_for("sessions.index"))

    sessions = (
        Session.query.filter_by(user_id=current_user.id)
        .order_by(Session.session_date.desc(), Session.created_at.desc())
        .limit(100)
        .all()
    )

    return render_template("sessions/index.html", form=form, sessions=sessions)


@bp.route("/<int:session_id>/edit", methods=["GET", "POST"])
@login_required
def edit(session_id: int):
    s = _owned_session_or_404(session_id)

    activities = (
        Activity.query.filter_by(user_id=current_user.id)
        .order_by(Activity.name.asc())
        .all()
    )
    if not activities:
        flash("Create an activity first.", "info")
        return redirect(url_for("activities.index"))

    form = SessionForm(obj=s)
    form.activity_id.choices = [(a.id, a.name) for a in activities]

    if request.method == "GET":
        form.activity_id.data = s.activity_id

    if form.validate_on_submit():
        s.activity_id = form.activity_id.data
        s.session_date = form.session_date.data
        s.duration_min = form.duration_min.data
        s.rpe = form.rpe.data
        s.notes = (form.notes.data.strip() if form.notes.data else None)

        db.session.commit()
        flash("Session updated.", "success")
        return redirect(url_for("sessions.index"))

    return render_template("sessions/edit.html", form=form, session=s)


@bp.route("/<int:session_id>/delete", methods=["POST"])
@login_required
def delete(session_id: int):
    s = _owned_session_or_404(session_id)
    db.session.delete(s)
    db.session.commit()
    flash("Session deleted.", "success")
    return redirect(url_for("sessions.index"))


@bp.route("/export.csv", methods=["GET"])
@login_required
def export_csv():
    # Optional activity filter: /sessions/export.csv?activity_id=all OR integer
    activity_id_raw = request.args.get("activity_id", "all").strip().lower()
    activity_id = None if activity_id_raw in ("all", "", "none") else int(activity_id_raw)

    q = Session.query.filter(Session.user_id == current_user.id).order_by(Session.session_date.asc())
    if activity_id is not None:
        q = q.filter(Session.activity_id == activity_id)

    rows = q.all()

    def esc(v):
        if v is None:
            return ""
        s = str(v)
        if any(c in s for c in [",", '"', "\n", "\r"]):
            s = '"' + s.replace('"', '""') + '"'
        return s

    header = "date,activity,minutes,rpe,load,notes\n"
    lines = [header]
    for s in rows:
        lines.append(
            ",".join(
                [
                    esc(s.session_date),
                    esc(s.activity.name if s.activity else ""),
                    esc(s.duration_min),
                    esc(s.rpe),
                    esc(s.load),
                    esc(s.notes),
                ]
            )
            + "\n"
        )

    csv_text = "".join(lines)
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sessioniq_sessions.csv"},
    )
