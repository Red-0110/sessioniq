from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange


class SessionForm(FlaskForm):
    activity_id = SelectField("Activity", coerce=int, validators=[DataRequired()])
    session_date = DateField("Date", default=date.today, validators=[DataRequired()])

    duration_min = IntegerField("Duration (minutes)", validators=[DataRequired(), NumberRange(min=1, max=1440)])
    rpe = IntegerField("RPE (1–10)", validators=[DataRequired(), NumberRange(min=1, max=10)])

    notes = TextAreaField("Notes (optional)")
    submit = SubmitField("Save session")
