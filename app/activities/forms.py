from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ActivityForm(FlaskForm):
    name = StringField("Activity name", validators=[DataRequired(), Length(min=1, max=80)])
    category = StringField("Category (optional)", validators=[Length(max=40)])
    submit = SubmitField("Add activity")
