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

import db_usage.utils as utils


CACHE = utils.Cache()


def dbusage(host, cached=True):
    """Get a list of database usage records for a given host."""
    cache_key = 'dbusage:{}'.format(host)
    data = CACHE.load(cache_key) if cached else None
    if data is None:
        conn = utils.dbconnect('information_schema', host)
        try:
            with conn.cursor() as cursor:
                sql = """SELECT
                    SUBSTRING_INDEX(table_schema, '_', 1) as owner
                    , SUM( data_length + index_length ) as total_bytes
                    , SUM( table_rows ) as row_count
                    , COUNT(1) as tables
                    FROM information_schema.TABLES
                    WHERE table_schema regexp '^[psu][0-9]'
                    GROUP BY owner
                    ORDER BY total_bytes DESC"""
                cursor.execute(sql)
                data = cursor.fetchall()
        finally:
            conn.close()
        CACHE.save(cache_key, data)
    return data
