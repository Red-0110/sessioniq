from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from . import bp
from .forms import ActivityForm
from ..extensions import db
from ..models import Activity


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ActivityForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        category = form.category.data.strip() if form.category.data else None

        # Prevent duplicates per user (case-insensitive)
        exists = (
            Activity.query.filter(Activity.user_id == current_user.id)
            .filter(Activity.name.ilike(name))
            .first()
        )
        if exists:
            flash("You already have an activity with that name.", "error")
            return redirect(url_for("activities.index"))

        a = Activity(user_id=current_user.id, name=name, category=category)
        db.session.add(a)
        db.session.commit()

        flash("Activity added.", "success")
        return redirect(url_for("activities.index"))

    activities = (
        Activity.query.filter_by(user_id=current_user.id)
        .order_by(Activity.name.asc())
        .all()
    )
    return render_template("activities/index.html", form=form, activities=activities)
