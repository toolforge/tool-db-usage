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


LEAGACY_USERS = {
    'p50380g40014': 'UNKNOWN',
    'p50380g50491': 'tools.tb-dev',
    'p50380g50494': 'UNKNOWN',
    'p50380g50497': 'liagent-php',
    'p50380g50512': 'UNKNOWN',
    'p50380g50551': 'UNKNOWN',
    'p50380g50552': 'UNKNOWN',
    'p50380g50553': 'suggestbot',
    'p50380g50592': 'UNKNOWN',
    'p50380g50692': 'dplbot',
    'p50380g50728': 'hostbot',
    'p50380g50729': 'grantsbot',
    'p50380g50769': 'tools.wikiviewstats',
    'p50380g50816': 'tools.popularpages',
    'p50380g50824': 'UNKNOWN',
    'p50380g50838': 'UNKNOWN',
    'p50380g50900': 'UNKNOWN',
    'p50380g50921': 'tools.wikiminiatlas',
}


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


def owner_usage(owner, cached=True):
    cache_key = 'owner_usage:{}'.format(owner)
    data = CACHE.load(cache_key) if cached else None
    if data is None:
        data = []
        for host in ('c1.labsdb', 'c3.labsdb'):
            conn = utils.dbconnect('information_schema', host)
            try:
                with conn.cursor() as cursor:
                    sql = """SELECT
                        table_schema
                        , table_name
                        , SUM( data_length + index_length ) as total_bytes
                        , SUM( table_rows ) as row_count
                        FROM information_schema.TABLES
                        WHERE table_schema like %s
                        ORDER BY table_schema, table_name"""
                    cursor.execute(sql, '{}_%'.format(owner))
                    for row in cursor.fetchall():
                        row['host'] = host
                        data.append(row)
            finally:
                conn.close()
    return data


def decode_owner(owner):
    """Return a link to the owner of the tablespace."""
    if owner[0] == 'u':
        # normal user
        cn = utils.uid_to_cn(owner[1:])
    elif owner[0] == 's':
        # "service group" == tool
        cn = utils.uid_to_cn(owner[1:])
    else:
        # legacy service group
        cn = LEAGACY_USERS.get(owner, owner)
    return cn
