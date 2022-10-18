from ast import parse
import json
from itertools import permutations, product
import os
import copy

import argparse
import sys


MARKERS = ["point", "line", "area","bar"]


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
    print("deep views", deep_views)
    perm = list(permutations(range(len(views))))
    print(perm)
    perm_views = []
    prods_views = list(product(*deep_views))
    print("prod_views ", prods_views)
    for prod in prods_views:
        for p in perm:
            copy_spec = copy.deepcopy(view_spec)
            copy_spec["views"] = [prod[i] for i in p]
            perm_views.append(copy_spec)
    print(perm_views)
    return perm_views


def scale_track(track):
    return


def scale_all_tracks(tracks):
    return


def scale_all_views(views):
    return


def change_track_marker(track):
  if track["mark"] in MARKERS:
    tracks = []
    for mark in MARKERS:
      track_cp = copy.deepcopy(track)
      track_cp["mark"] = mark
      tracks.append(track_cp)
    return tracks
  return []


def write_spec(spec_dict, output_path):
    with open(output_path, "w") as f:
        json.dump(spec_dict, f)


test_views = {}
test_views["views"] = [
    {
        "layout": "linear",
        "tracks": [
            {
                "row": {"field": "sample", "type": "nominal"},
                "width": 240,
                "height": 200,
                "data": {
                    "url": "https://resgen.io/api/v1/tileset_info/?d=UvVPeLHuRDiYA3qwFlm7xQ",
                    "type": "multivec",
                    "row": "sample",
                    "column": "position",
                    "value": "peak",
                    "categories": ["sample 1", "sample 2", "sample 3", "sample 4"]
                },
                "mark": "area",
                "x": {
                        "field": "position",
                        "type": "genomic",
                        "domain": {"chromosome": "2"},
                        "linkingId": "detail-1",
                        "axis": "top"
                },
                "y": {"field": "peak", "type": "quantitative"},
                "color": {"field": "sample", "type": "nominal"},
                "style": {"background": "blue", "backgroundOpacity": 0.1}
            }
        ]
    },
    {
        "layout": "linear",
        "tracks": [{
            "row": {"field": "sample", "type": "nominal"},
            "width": 240,
            "height": 200,
            "data": {
                  "url": "https://resgen.io/api/v1/tileset_info/?d=UvVPeLHuRDiYA3qwFlm7xQ",
                  "type": "multivec",
                  "row": "sample",
                "column": "position",
                "value": "peak",
                "categories": ["sample 1", "sample 2", "sample 3", "sample 4"]
            },
            "mark": "area",
            "x": {
                "field": "position",
                "type": "genomic",
                "domain": {"chromosome": "5"},
                "linkingId": "detail-2",
                "axis": "top"
            },
            "y": {"field": "peak", "type": "quantitative"},
            "color": {"field": "sample", "type": "nominal"},
            "style": {"background": "red", "backgroundOpacity": 0.1}
        }]
    }
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, metavar="<filename>")
    parser.add_argument("-pv", "--permute-views", action="store_true")
    args = parser.parse_args(sys.argv[1:])
    print(args)
    template_spec = read_spec(args.file)
    if args.permute_views:
        perm_vs = permute_views(template_spec)


# test_name = "sim_layout"
# test_path = "generated_specs"
# spec_path = "train_specs/example_sim_layout.json"
# sample_spec = read_spec(spec_path)
# perm_vs = permute_views(sample_spec)
# # print(perm_vs)
# # print(len(perm_vs))
# for i,pv in enumerate(perm_vs):
#     write_spec(pv,os.path.join(test_path,test_name+"_%d.json"%i))
