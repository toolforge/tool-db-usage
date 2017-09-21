# -*- coding: utf-8 -*-
#
# This file is part of Tool DB Usage
#
# Copyright (C) 2017 Bryan Davis and contributors
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import flask
import toolforge
import werkzeug.contrib.fixers

import db_usage


# Create the Flask application
app = flask.Flask(__name__)

# Add the ProxyFix middleware which reads X-Forwarded-* headers
app.wsgi_app = werkzeug.contrib.fixers.ProxyFix(app.wsgi_app)

# Always use TLS
app.before_request(toolforge.redirect_to_https)


@app.route('/')
def index():
    """Application landing page."""
    cached = 'purge' not in flask.request.args
    usage = {
        'c1.labsdb': db_usage.dbusage('c1.labsdb', cached=cached),
        'c3.labsdb': db_usage.dbusage('c3.labsdb', cached=cached),
    }
    return flask.render_template('index.html', usage=usage)


@app.template_filter('owner')
def owner(s):
    return db_usage.decode_owner(s)
