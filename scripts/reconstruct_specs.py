
import draw_bound_box
from draw_bound_box import BOX_DIR
def circular_to_box(bbox):
    return [bbox["cx"]-bbox["outerRadius"],bbox["cx"]+bbox["outerRadius"], bbox["cy"]-bbox["outerRadius"], bbox["cy"]+bbox["outerRadius"]]

def rect_to_box(bbox):
    return [bbox["x"], bbox["x"]+bbox["width"],bbox["y"],bbox["y"]+bbox["height"]]

def get_ys(box):
    return box[2],box[3]

def get_xs(box):
    return box[0],box[1]

def reconstruct_vertical(boxes):
    if len(boxes) <= 1:
        return boxes
    sorted_boxes = sorted(boxes,key=get_ys)
    vert_hierarchy = []
    curr_y_low = 0
    curr_y_high = 0
    curr_layer = []
    for box in sorted_boxes:
        box_y_low, box_y_high = get_ys(box)
        if box_y_low >= curr_y_high:
            vert_hierarchy.append(curr_layer)
            curr_layer = [box]
            curr_y_low = box_y_low
            curr_y_high = box_y_high
        else:
            curr_layer.append(box)
            curr_y_high = max(curr_y_high,box_y_high)
    vert_hierarchy.append(curr_layer)
    return vert_hierarchy[1:]

def reconstruct_overlay(vert_view):
    if len(vert_view) <= 1:
        return vert_view
    sorted_boxes = sorted(vert_view,key=get_xs)
    overlay_hierarchy = []
    curr_x_low = 0
    curr_x_high = 0
    curr_view = []
    for box in vert_view:
        box_x_low, box_x_high = get_xs(box)
        if box_x_low >= curr_x_high:
            overlay_hierarchy.append(curr_view)
            curr_view = [box]
            curr_x_low = box_x_low
            curr_x_high = box_x_high
        else:
            curr_view.append(box)
            curr_x_high = max(curr_x_high,box_x_high)
    overlay_hierarchy.append(curr_view)
    return overlay_hierarchy[1:]


def reconstruct_bounding_box(bboxes):
    boxes = []
    for bbox in bboxes:
        if bbox.keys() == draw_bound_box.BOX_KEYS:
            boxes.append(rect_to_box(bbox))
        elif bbox.keys() == draw_bound_box.CIR_KEYS:
            boxes.append(circular_to_box(bbox))
    #print(boxes)
    vert_hierarchy = reconstruct_vertical(boxes)
    #print(vert_hierarchy)
    overlay_hierarchy = [reconstruct_overlay(v) for v in vert_hierarchy]
    print(overlay_hierarchy)
    return overlay_hierarchy

test_bboxes = draw_bound_box.load_boxes(BOX_DIR+"example_sim_layout_p_0_sw_1_0_s_1_0.json")
structure = reconstruct_bounding_box(test_bboxes)