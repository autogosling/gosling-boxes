import copy 
import json
import os
import reconstruct_specs

DEFAULT_BAR_DATA = "https://resgen.io/api/v1/tileset_info/?d=UvVPeLHuRDiYA3qwFlm7xQ"
DEFAULT_BAR_TRACK = {
      "layout": "linear",
      "width": 800,
      "height": 180,
      "data": {
        "url": "https://resgen.io/api/v1/tileset_info/?d=UvVPeLHuRDiYA3qwFlm7xQ",
        "type": "multivec",
        "row": "sample",
        "column": "position",
        "value": "peak",
        "categories": ["sample 1"],
        "binSize": 5
      },
      "mark": "bar",
      "x": {"field": "start", "type": "genomic", "axis": "bottom"},
      "xe": {"field": "end", "type": "genomic"},
      "y": {"field": "peak", "type": "quantitative", "axis": "right"},
      "size": {"value": 5}
    }


EXTRACTED_INFO_PATH = "../data/extracted"
def create_filenames(example):
    filenames = {
        "box":os.path.join(EXTRACTED_INFO_PATH,"bounding_box",example+".json"),
        "layout":os.path.join(EXTRACTED_INFO_PATH,"layouts",example+".json"),
        "mark":os.path.join(EXTRACTED_INFO_PATH,"marks",example+".json")
    }
    return filenames   


def read_info(filenames):
    box_infos = []
    infos = {}
    for key in filenames.keys():
        infos[key] = json.loads(open(filenames[key]).read())
    for i in range(len(infos["box"])):
        new_box = {}
        for key in infos.keys():
            if key == "box":
                new_box["width"] = infos["box"][i]["width"]
                new_box["height"] = infos["box"][i]["height"]
            else:
                new_box[key] = infos[key][i]
        box_infos.append(new_box)

    return box_infos, infos["box"]
def create_track(track_info):
    new_track = copy.deepcopy(DEFAULT_BAR_TRACK)
    for key in track_info.keys():
        new_track[key] = track_info[key]
    return new_track


def make_spec(track_hierarchy, track_infos):
    for v0 in track_hierarchy["views"]:
        for v1 in v0["views"]:
            for v2 in v1["views"]:
                new_tracks = []
                for t in v2["tracks"]:
                    new_tracks.append(create_track(track_infos[t]))
                v2["tracks"] = new_tracks
    return track_hierarchy

ex_track_info = {"layout":"linear",
                "mark":"line",
                "width":400,
                "height":210}

#print(assemble_views([ex_track_info]))

test_files = create_filenames("complex_hierarchy")
infos_structure = read_info(test_files)
#print(infos_structure)
hierarychy = reconstruct_specs.reconstruct_bounding_box(infos_structure[1])
print(hierarychy)
idx = reconstruct_specs.map_to_index(hierarychy)
print(idx)
spec = make_spec(idx,infos_structure[0])
print(json.dumps(spec))


