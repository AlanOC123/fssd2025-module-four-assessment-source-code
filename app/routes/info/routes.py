"""
Defines the routes for the 'info' blueprint.

This blueprint handles serving static informational pages to logged-in
users, such as the 'About' and 'Sitemap' pages.
"""

from flask import render_template
from . import info_bp
from flask_login import login_required, current_user


@info_bp.get(rule='/about', endpoint='about')
@login_required
def about():
    """
    Renders the static 'About' page.

    **Route:** /info/about
    **Method:** GET
    **Protection:** @login_required

    This route simply renders the 'about.html' template, passing in
    the 'current_user' for the base template context.
    """
    return render_template('pages/info/about.html', current_user=current_user)

@info_bp.get(rule='/sitemap', endpoint='sitemap')
@login_required
def sitemap():
    """
    Renders the static 'Sitemap' page.

    **Route:** /info/sitemap
    **Method:** GET
    **Protection:** @login_required

    This route simply renders the 'sitemap.html' template, passing in
    the 'current_user' for the base template context.
    """
    return render_template('pages/info/sitemap.html', current_user=current_user)
