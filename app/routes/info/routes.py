from flask import render_template
from . import info_bp
from flask_login import login_required, current_user


@info_bp.get(rule='/about', endpoint='about')
@login_required
def about():
    return render_template('pages/info/about.html', current_user=current_user)

@info_bp.get(rule='/sitemap', endpoint='sitemap')
@login_required
def sitemap():
    return render_template('pages/info/sitemap.html', current_user=current_user)
