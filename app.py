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
import os
import pymysql
import toolforge
import werkzeug.contrib.fixers


# Create the Flask application
app = flask.Flask(__name__)

# Add the ProxyFix middleware which reads X-Forwarded-* headers
app.wsgi_app = werkzeug.contrib.fixers.ProxyFix(app.wsgi_app)

# Always use TLS
app.before_request(toolforge.redirect_to_https)


def connect(db, host, **kwargs):
    return pymysql.connect(
        database=db,
        host=host,
        read_default_file=os.path.expanduser("~/replica.my.cnf"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        **kwargs
    )


def dbusage(host):
    conn = connect('information_schema', host)
    try:
        with conn.cursor() as cursor:
            sql = """SELECT
                table_schema
                , sum( data_length ) as data_bytes
                , sum( index_length ) as index_bytes
                , sum( table_rows ) as row_count
                , count(1) as tables
                FROM information_schema.TABLES
                WHERE table_schema regexp '^[psu][0-9]'
                GROUP BY table_schema
                ORDER BY data_bytes DESC"""
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


@app.route('/')
def index():
    """Application landing page."""
    usage = dbusage('c1.labsdb')
    return flask.render_template('index.html', usage=usage)
