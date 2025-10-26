from .route_schemas import core_schema
from flask_login import login_required
from flask import redirect, url_for

@login_required
def index():
    return redirect(url_for('app.home'))

index_route = core_schema(rule="/", endpoint="index", view_func=index, methods=["GET"])