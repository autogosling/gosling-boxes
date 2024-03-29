from ast import parse
import json
from itertools import permutations, product
from operator import le
import os
import copy

import argparse
import re
import sys


MARKERS = ["point", "line", "area", "bar"]
OUTPUT_PATH = "generated_specs"


def read_spec(spec_file):
    with open(spec_file) as f:
        return json.load(f)


def find_views(spec):
    return spec["views"]


def find_tracks(views):
    return views["tracks"]


def permute_views(view_spec):
    # pass in a spec
    if "views" not in view_spec.keys():
        return [view_spec]
    views = find_views(view_spec)
    deep_views = [permute_views(v) for v in views]
    perm = list(permutations(range(len(views))))
    perm_views = []
    prods_views = list(product(*deep_views))
    for prod in prods_views:
        for p in perm:
            copy_spec = copy.deepcopy(view_spec)
            copy_spec["views"] = [prod[i] for i in p]
            perm_views.append(copy_spec)
    # print(perm_views)
    return perm_views


def scale_track(track, scale):
    track = copy.deepcopy(track)
    if "width" in track.keys():
        track["width"] *= scale
    if "height" in track.keys():
        track["height"] *= scale
    return track


def scale_width_track(track, scale):
    track = copy.deepcopy(track)
    if "width" in track.keys():
        track["width"] *= scale
    return track


def scale_all_views(views, scale):
    if "views" in views.keys():
        scaled_views = [scale_all_views(v, scale) for v in views["views"]]
        views = copy.deepcopy(views)
        views["views"] = scaled_views
    elif "tracks" in views.keys():
        scaled_tracks = [scale_track(t, scale) for t in views["tracks"]]
        views = copy.deepcopy(views)
        views["tracks"] = scaled_tracks
    return views


def get_scales(scale_str):
    res = scale_str.split(";")
    return [float(s) for s in res]


def scale_width_views(views, scale):
    if "views" in views.keys():
        scaled_views = [scale_width_views(v, scale) for v in views["views"]]
        views = copy.deepcopy(views)
        views["views"] = scaled_views
    elif "tracks" in views.keys():
        scaled_tracks = [scale_width_track(t, scale) for t in views["tracks"]]
        views = copy.deepcopy(views)
        views["tracks"] = scaled_tracks
    return views


def change_track_marker(track):
    #print("track ", track.keys())
    if "mark" not in track.keys():
        return [track]
    if track["mark"] in MARKERS:
        tracks = []
        for mark in MARKERS:
            track_cp = copy.deepcopy(track)
            track_cp["mark"] = mark
            tracks.append(track_cp)
        return tracks
    return [track]


def change_view_marker(view):
    if "views" not in view.keys():
        tracks = view["tracks"]
        track_mark_changes = [change_track_marker(t) for t in tracks]
        track_prods = product(*track_mark_changes)
        views = []
        for tp in track_prods:
            view_cp = copy.deepcopy(view)
            view_cp["tracks"] = tp
            views.append(view_cp)
        return views
    else:
        deep_views = view["views"]
        view_marker = [change_view_marker(v) for v in deep_views]
        view_prods = product(*view_marker)
        new_views = []
        for vp in view_prods:
            view_cp = copy.deepcopy(view)
            view_cp["views"] = vp
            new_views.append(view_cp)
        return new_views


def write_spec(spec_dict, output_path):
    with open(output_path, "w") as f:
        json.dump(spec_dict, f)


test_tracks = """
            {
              "row": {
                "field": "sample",
                "type": "nominal"
              },
              "width": 240,
              "height": 200,
              "data": {
                "url": "https://resgen.io/api/v1/tileset_info/?d=UvVPeLHuRDiYA3qwFlm7xQ",
                "type": "multivec",
                "row": "sample",
                "column": "position",
                "value": "peak",
                "categories": [
                  "sample 1",
                  "sample 2",
                  "sample 3",
                  "sample 4"
                ]
              },
              "mark": "area",
              "x": {
                "field": "position",
                "type": "genomic",
                "domain": {
                  "chromosome": "5"
                },
                "linkingId": "detail-2",
                "axis": "top"
              },
              "y": {
                "field": "peak",
                "type": "quantitative"
              },
              "color": {
                "field": "sample",
                "type": "nominal"
              },
              "style": {
                "background": "red",
                "backgroundOpacity": 0.1
              }
            }
"""

test_views = """
        {
      "arrangement": "serial",
      "spacing": 20,
      "views": [
        {
          "layout": "linear",
          "tracks": [
            {
              "row": {
                "field": "sample",
                "type": "nominal"
              },
              "width": 240,
              "height": 200,
              "data": {
                "url": "https://resgen.io/api/v1/tileset_info/?d=UvVPeLHuRDiYA3qwFlm7xQ",
                "type": "multivec",
                "row": "sample",
                "column": "position",
                "value": "peak",
                "categories": [
                  "sample 1",
                  "sample 2",
                  "sample 3",
                  "sample 4"
                ]
              },
              "mark": "area",
              "x": {
                "field": "position",
                "type": "genomic",
                "domain": {
                  "chromosome": "2"
                },
                "linkingId": "detail-1",
                "axis": "top"
              },
              "y": {
                "field": "peak",
                "type": "quantitative"
              },
              "color": {
                "field": "sample",
                "type": "nominal"
              },
              "style": {
                "background": "blue",
                "backgroundOpacity": 0.1
              }
            }
          ]
        },
        {
          "layout": "linear",
          "tracks": [
            {
              "row": {
                "field": "sample",
                "type": "nominal"
              },
              "width": 240,
              "height": 200,
              "data": {
                "url": "https://resgen.io/api/v1/tileset_info/?d=UvVPeLHuRDiYA3qwFlm7xQ",
                "type": "multivec",
                "row": "sample",
                "column": "position",
                "value": "peak",
                "categories": [
                  "sample 1",
                  "sample 2",
                  "sample 3",
                  "sample 4"
                ]
              },
              "mark": "area",
              "x": {
                "field": "position",
                "type": "genomic",
                "domain": {
                  "chromosome": "5"
                },
                "linkingId": "detail-2",
                "axis": "top"
              },
              "y": {
                "field": "peak",
                "type": "quantitative"
              },
              "color": {
                "field": "sample",
                "type": "nominal"
              },
              "style": {
                "background": "red",
                "backgroundOpacity": 0.1
              }
            }
          ]
        }
      ]
    }
"""

# print(scale_all_views(json.loads(test_views),0.8))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, metavar="<filename>")
    parser.add_argument("-pv", "--permute-views", action="store_true")
    parser.add_argument("-cm", "--change-marker", action="store_true")
    parser.add_argument("-s", "--scale")
    parser.add_argument("-sw", "--scale-width")
    args = parser.parse_args(sys.argv[1:])
    filename = os.path.splitext(os.path.basename(args.file))[0]
    output_dir = os.path.join(OUTPUT_PATH, filename)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    template_spec = read_spec(args.file)
    specs = {filename: template_spec}
    if args.permute_views:
        new_specs = {}
        for f in specs.keys():
            s = specs[f]
            perm_vs = permute_views(s)
            for i, pv in enumerate(perm_vs):
                new_specs[f+"_p_%d" % i] = pv
        specs = new_specs
    if args.change_marker:
        new_specs = {}
        for f in specs.keys():
            s = specs[f]
            cm_vs = change_view_marker(s)
            for i, pv in enumerate(cm_vs):
                new_specs[f+"_m_%d" % i] = pv
        specs = new_specs
    if args.scale_width is not None:
        scales = get_scales(args.scale_width)
        new_specs = {}
        for s in scales:
            for f in specs.keys():
                sp = specs[f]
                s_str = str(s).replace(".", "_")
                s_spec = scale_width_views(sp, s)
                new_specs[f+"_sw_%s" % s_str] = s_spec
        specs = new_specs
    if args.scale is not None:
        scales = get_scales(args.scale)
        new_specs = {}
        for s in scales:
            for f in specs.keys():
                sp = specs[f]
                s_str = str(s).replace(".", "_")
                s_spec = scale_all_views(sp, s)
                new_specs[f+"_s_%s" % s_str] = s_spec
        specs = new_specs

    for f in specs.keys():
        write_spec(specs[f], os.path.join(output_dir, f+".json"))
