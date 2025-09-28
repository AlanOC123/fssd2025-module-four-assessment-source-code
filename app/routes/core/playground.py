from flask import render_template
from ..route_schemas import core_schema

def playground():
    return render_template('pages/playground.html')

test_route = core_schema(rule="/playground", endpoint="playground", methods=["GET"], view_func=playground)