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
import werkzeug.middleware.proxy_fix

import db_usage


# Create the Flask application
app = flask.Flask(__name__)

# Add the ProxyFix middleware which reads X-Forwarded-* headers
app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(app.wsgi_app)


HOSTS = {
    "ToolsDB": "tools.db.svc.wikimedia.cloud",
}


@app.route("/")
def index():
    """Application landing page."""
    cached = "purge" not in flask.request.args
    usage = {
        name: db_usage.dbusage(host, cached=cached)
        for name, host in HOSTS.items()
    }
    return flask.render_template("index.html", usage=usage)


@app.route("/owner/<name>")
def owner_usage(name):
    cached = "purge" not in flask.request.args
    usage = db_usage.owner_usage(name, HOSTS, cached=cached)
    return flask.render_template("owner.html", name=name, usage=usage)


@app.template_filter("owner")
def owner_name(s):
    return db_usage.decode_owner(s)


@app.template_filter("owner_url")
def owner_url(s):
    owner = db_usage.decode_owner(s)
    if owner and owner.startswith("tools."):
        base = "https://toolsadmin.wikimedia.org/tools/id/"
        page = owner[6:]
    else:
        base = "https://wikitech.wikimedia.org/wiki/User:"
        page = owner
    return "{}{}".format(base, page)
