# app/main/__init__.py

import os
from flask import Blueprint, current_app, url_for
from ..models import Permission

main = Blueprint('main', __name__)

# adding the Permission class
# to the template context
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@main.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

# Browser by default store static files in cache.
# His, don't reload files that have been changed.
# This function override url_for, and add to file link, creation time.
# Browser forced to reload static files when do request.
def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(current_app.root_path, 
                                    endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

from . import views, errors
