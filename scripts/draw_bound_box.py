from traceback import print_tb
from PIL import Image, ImageDraw
import json

IMG_DIR = "../data/extracted/screenshot/"
BOX_DIR = "../data/extracted/bounding_box/"
BOX_KEYS = ["x", "y", "width", "height"]

def check_box_keys(keys):
    for k in BOX_KEYS:
        if k not in keys:
            return False
    return True

def load_boxes(box_file):
    f = open(box_file)
    data = json.load(f)
    f.close()
    return data

def draw_boxes(img_file, box_file, output_file):
    box_data = load_boxes(box_file)
    print(box_data)
    with Image.open(img_file) as im:
        draw = ImageDraw.Draw(im)
        for box in box_data:
            if check_box_keys(box.keys()):
                box_info = [box["x"], box["y"],box["x"]+box["width"], box["y"]+box["height"]]
                draw.rectangle(box_info, outline="red", width=3)
        im.save(output_file,"PNG")            


draw_boxes(IMG_DIR+"example.jpeg", BOX_DIR+"example.json", "test_box.png")