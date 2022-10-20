from ast import parse
import json
from itertools import permutations, product
from operator import le
import os
import copy

import argparse
import re
import sys


MARKERS = ["point", "line", "area","bar"]
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
    #print(perm_views)
    return perm_views


def scale_track(track):
    return


def scale_all_tracks(tracks):
    return


def scale_all_views(views):
    return


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, metavar="<filename>")
    parser.add_argument("-pv", "--permute-views", action="store_true")
    parser.add_argument("-cm", "--change-marker", action="store_true")
    args = parser.parse_args(sys.argv[1:])
    filename = os.path.splitext(os.path.basename(args.file))[0]
    output_dir = os.path.join(OUTPUT_PATH,filename)
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
    template_spec = read_spec(args.file)
    if args.permute_views:
      perm_vs = permute_views(template_spec)
      for i,pv in enumerate(perm_vs):
        write_spec(pv,os.path.join(output_dir,filename+"_p_%d.json"%i))
    if args.change_marker:
      cm_vs = change_view_marker(template_spec)
      for i,pv in enumerate(cm_vs):
        write_spec(pv,os.path.join(output_dir,filename+"_m_%d.json"%i))


