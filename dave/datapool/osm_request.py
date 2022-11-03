# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import time
from collections import namedtuple
from urllib.parse import urlencode
from xml.etree.ElementTree import fromstring

import geopandas as gpd
import pandas as pd
from pandas.io.common import urlopen
from shapely.geometry import LineString, Point
from six import string_types

from dave.datapool.read_data import get_data_path
from dave.io.database_io import db_availability, from_mongo, search_database
from dave.settings import dave_settings


def osm_request(data_type, area):
    """
    This function requests OSM data from database or OSM directly
    """
    data_param = dave_settings()["osm_tags"][data_type]
    # create database collection name
    collection = f"osm_{data_type}_{dave_settings()['osm_area']}"
    if db_availability(collection_name=collection):
        request_data = from_mongo(
            database=search_database(collection=collection),
            collection=collection,
            filter_method="eq",
            filter_param=f"{where.split('=')[0]}",
            filter_value=f"{where.split('=')[1]}",
        )  # !!! noch umändern zu geometrical filtering based on area (intersect?)
    else:
        request_data = gpd.GeoDataFrame([])
        for osm_type in data_param[2]:
            # create tags
            tags = (
                f'{data_param[0]}~"{"|".join(data_param[1])}"'
                if isinstance(data_param[1], list)
                else f"{data_param[0]}"
            )
            # get data from OSM directly via API query
            data, meta_data = query_osm(osm_type, area, recurse="down", tags=tags)
            request_data = pd.concat([request_data, data], ignore_index=True)
    return request_data, meta_data

    # !!! hier function hin schreiben die entscheidet ob aus Dataenbank (is available) oder direct von OSM
    # !!! in target area query umschreiben


# --- request directly from OSM via Overpass API and geopandas_osm package

# This functions are based on the geopandas_osm python package, which was published under the
# following license:

# The MIT License (MIT)

# Copyright (c) 2014 Jacob Wasserman

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


OSMData = namedtuple("OSMData", ("nodes", "waynodes", "waytags", "relmembers", "reltags"))
_crs = "epsg:4326"

# Tags to remove so we don't clobber the output. This list comes from
# osmtogeojson's index.js (https://github.com/tyrasd/osmtogeojson)
uninteresting_tags = set(
    [
        "source",
        "source_ref",
        "source:ref",
        "history",
        "attribution",
        "created_by",
        "tiger:county",
        "tiger:tlid",
        "tiger:upload_uuid",
    ]
)


# http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
def query_osm(typ, bbox=None, recurse=None, tags="", raw=False, meta=False, **kwargs):
    """
    Query the Overpass API to obtain OpenStreetMap data.

    See also:
    http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide

    The OSM XML data is parsed into an intermediate set of DataFrames.
    By passing in 'render=False', this will return these DataFrames stored
    as the OSMData namedtuple. If render is True, then the DataFrames
    are built into their corresponding geometries.

    Parameters
    ----------
    typ : {'node', 'way', 'relation'}
        The type of OSM data to query
    bbox : (min lon, min lat, max lon, max lat) bounding box
        Optional bounding box to restrict the query. Unless the query
        is extremely restricted, you usually want to specify this.
        It can be retrieved from GeoPandas objects as 'df.total_bounds' or
        from Shapely objects as 'geom.bounds'
    recurse : {'up, 'down', 'uprel', 'downrel'}
        This is used to get more data than the original query. If 'typ' is
        'way', you'll usually want this set to 'down' which grabs all nodes
        of the matching ways
    tags : string or list of query strings
        See also the OverpassQL (referenced above) for more tag options
        Examples:
            tags='highway'
                Matches objects with a 'highway' tag
            tags='highway=motorway' <-- Matches ob
                Matches objects where the 'highway' tag is 'motorway'
            tags='name~[Mm]agazine'
                Match if the 'name' tag matches the regular expression

            Specify a list of tag requests to match all of them
            tags=['highway', 'name~"^Magazine"']
                Match tags that have 'highway' and where 'name' starts
                with 'Magazine'

    raw : boolean, default False
        Return the raw XML data returned by the request
    render : boolean, default True
        Parse the output and return a final GeoDataFrame
    meta : boolean, default False
        Indicates whether to query the metadata with each OSM object. This
        includes the changeset, timestamp, uid, user, and version.

    Returns
    -------
    df - GeoDataFrame
    Note that there's probably a bit more filtering required to get the
    exact desired data. For example if you only want ways, you may want
    to grab only the linestrings like:
        >>> df = df[df.type == 'LineString']

    """
    url = _build_url(typ, bbox, recurse, tags, meta)
    # add time delay because osm doesn't alowed more than 1 request per second.
    time_delay = dave_settings()["osm_time_delay"]

    # TODO: Raise on non-200 (or 400-599)
    # with urlopen(url) as response:
    #     content = response.read()
    while True:
        try:
            with urlopen(url) as response:
                content = response.read()
                if response.getcode() == 200:
                    break
        except Exception as inst:
            print(f'\n Retry OSM query because of "{inst}"')
            # add time delay
            time.sleep(time_delay)

    # get meta informations
    meta_data = pd.read_excel(get_data_path("osm_meta.xlsx", "data"), sheet_name=None)

    if raw:
        return content, meta_data
    return read_osm(content, **kwargs), meta_data


def _build_url(typ, bbox=None, recurse=None, tags="", meta=False):
    recurse_map = {
        "up": "<",
        "uprel": "<<",
        "down": ">",
        "downrel": ">>",
    }
    if recurse is None:
        recursestr = ""
    else:
        try:
            recursestr = recurse_map[recurse]
        except KeyError:
            raise ValueError(
                "Unrecognized recurse value '{}'. "
                "Must be one of: {}.".format(recurse, ", ".join(recurse_map.keys()))
            )

    # Allow tags to be a single string
    if isinstance(tags, string_types) and tags:
        tags = [tags]
    queries = "".join("[{}]".format(t) for t in tags)

    # Overpass QL takes the bounding box as
    # (min latitude, min longitude, max latitude, max longitude)
    if bbox is None:
        bboxstr = ""
    else:
        # bboxstr = "({})".format(
        #','.join(str(b) for b in (bbox[1], bbox[0], bbox[3], bbox[2])))
        bboxstr = '(poly:"{}")'.format(
            " ".join("{c[1]} {c[0]}".format(c=c) for c in bbox.exterior.coords)
        )

    if meta:
        metastr = "meta"
    else:
        metastr = ""

    query = "({typ}{bbox}{queries};{recurse};);out {meta};".format(
        typ=typ, bbox=bboxstr, queries=queries, recurse=recursestr, meta=metastr
    )

    url = "".join(["http://www.overpass-api.de/api/interpreter?", urlencode({"data": query})])

    return url


def read_osm(content, render=True, **kwargs):
    """
    Parse OSM XML data and store as several DataFrames. Optionally "render"
    the DataFrames to GeoDataFrames.

    """
    doc = fromstring(content)

    nodes = read_nodes(doc)
    waynodes, waytags = read_ways(doc)
    relmembers, reltags = read_relations(doc)

    # check if all requested variables are empty
    # if nodes.empty and waynodes.empty and waytags.empty and relmembers.empty and reltags.empty:

    data = OSMData(nodes, waynodes, waytags, relmembers, reltags)

    if render:
        data = render_to_gdf(data, **kwargs)
    return data


def read_nodes(doc):
    #   Example:
    #   <node id="1705717514" lat="42.3630798" lon="-71.0997601">
    #       <tag k="crossing" v="zebra"/>
    #       <tag k="highway" v="crossing"/>
    #       <tag k="source" v="Bing"/>
    #   </node>
    nodes = [_element_to_dict(xmlnode) for xmlnode in doc.findall("node")]
    nodes = _dict_to_dataframe(nodes)
    if not nodes.empty:
        nodes["lon"] = nodes["lon"].astype(float)
        nodes["lat"] = nodes["lat"].astype(float)

    return nodes


def _element_to_dict(element):
    d = element.attrib.copy()
    for t in element.findall("tag"):
        k = t.attrib["k"]
        if k not in uninteresting_tags:
            d[k] = t.attrib["v"]

    return d


def _dict_to_dataframe(d):
    df = pd.DataFrame.from_dict(d)
    if "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def read_ways(doc):
    #   Example:
    #   <way id="8614593">
    #       <nd ref="61326730"/>
    #       <nd ref="61326036"/>
    #       <nd ref="61321194"/>
    #       <tag k="attribution" v="Office of Geographic and Environmental Information (MassGIS)"/>
    #       <tag k="condition" v="fair"/>
    #       <tag k="created_by" v="JOSM"/>
    #       <tag k="highway" v="residential"/>
    #       <tag k="lanes" v="2"/>
    #       <tag k="massgis:way_id" v="171099"/>
    #       <tag k="name" v="Centre Street"/>
    #       <tag k="source" v="massgis_import_v0.1_20071008165629"/>
    #       <tag k="width" v="13.4"/>
    #   </way>
    waytags = []
    waynodes = []
    for xmlway in doc.findall("way"):
        wayid = xmlway.attrib["id"]
        for i, xmlnd in enumerate(xmlway.findall("nd")):
            d = xmlnd.attrib.copy()
            d["id"] = wayid
            d["index"] = i
            waynodes.append(d)

        tags = _element_to_dict(xmlway)
        waytags.append(tags)

    waynodes = _dict_to_dataframe(waynodes)
    waytags = _dict_to_dataframe(waytags)

    return waynodes, waytags


def read_relations(doc):
    # Example:
    #   <relation id="1933745">
    #     <member type="way" ref="134055159" role="outer"/>
    #     <member type="way" ref="260533047" role="outer"/>
    #     <member type="way" ref="142867799" role="outer"/>
    #     <member type="way" ref="134063352" role="outer"/>
    #     <member type="way" ref="142803038" role="outer"/>
    #     <member type="way" ref="134056144" role="outer"/>
    #     <member type="way" ref="134056141" role="outer"/>
    #     <tag k="admin_level" v="8"/>
    #     <tag k="boundary" v="administrative"/>
    #     <tag k="name" v="Cambridge"/>
    #     <tag k="type" v="boundary"/>
    #     <tag k="wikipedia" v="en:Cambridge, Massachusetts"/>
    #   </relation>
    reltags = []
    relmembers = []
    for xmlrel in doc.findall("relation"):
        relid = xmlrel.attrib["id"]
        for i, xmlmember in enumerate(xmlrel.findall("member")):
            d = xmlmember.attrib.copy()
            d["id"] = relid
            d["index"] = i
            relmembers.append(d)

        tags = _element_to_dict(xmlrel)
        reltags.append(tags)

    relmembers = _dict_to_dataframe(relmembers)
    reltags = _dict_to_dataframe(reltags)
    return relmembers, reltags


def render_to_gdf(osmdata, drop_untagged=True):
    nodes = render_nodes(osmdata.nodes, drop_untagged)
    ways = render_ways(osmdata.nodes, osmdata.waynodes, osmdata.waytags)

    # set landuse tag from origin relation at relation members who has no landuse tag
    if (ways is not None) and ("landuse" in ways.keys()) and (not osmdata.relmembers.empty):
        for i, way in ways.iterrows():
            # get and add origin relation id
            rel_id = osmdata.relmembers[osmdata.relmembers.ref == way.id].iloc[0].id
            ways.at[i, "relation_id"] = rel_id
            # get and add origin relation landuse if needed
            rel_landuse = osmdata.reltags[osmdata.reltags.id == rel_id].iloc[0].landuse
            if str(way.landuse) == "nan":
                ways.at[i, "landuse"] = rel_landuse

    if ways is not None:
        nodes = pd.concat([nodes, ways], ignore_index=True)
        nodes = nodes.set_geometry("geometry", crs=_crs)

    return nodes


def render_nodes(nodes, drop_untagged=True):
    # check if their are nodes
    if not nodes.empty:
        # Drop nodes that have no tags, convert lon/lat to points
        if drop_untagged:
            nodes = nodes.dropna(subset=nodes.columns.drop(["id", "lon", "lat"]), how="all")
        points = [Point(x["lon"], x["lat"]) for i, x in nodes.iterrows()]
        nodes = nodes.drop(["lon", "lat"], axis=1)
        nodes = nodes.set_geometry(points, crs=_crs)

    return nodes


def render_ways(nodes, waynodes, waytags):
    if waynodes is None or waynodes.empty:
        return None

    node_points = nodes[["id", "lon", "lat"]]

    def wayline(df):
        # df = df.sort_index(by='index')[['lon', 'lat']]  # for older pandas version
        df = df.sort_values(by="index")[["lon", "lat"]]
        if len(df) > 1:
            return LineString(df.values)

    # Group the ways and create a LineString for each one.  way_lines is a
    # Series where the index is the way id and the value is the LineString.
    # Merge it with the waytags to get a single GeoDataFrame of ways
    waynodes = waynodes.merge(node_points, left_on="ref", right_on="id", suffixes=("", "_nodes"))
    way_lines = waynodes.groupby("id").apply(wayline)
    ways = waytags.set_index("id").set_geometry(way_lines, crs=_crs)
    ways.reset_index(inplace=True)

    return ways
