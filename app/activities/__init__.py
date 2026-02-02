from flask import Blueprint

bp = Blueprint("activities", __name__)

from . import routes  # noqa: E402,F401
