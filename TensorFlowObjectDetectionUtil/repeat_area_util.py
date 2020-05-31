import sys
sys.path.append('/home/nvidia/.local/lib/python2.7/site-packages')


def iou_calculator(b1,b2):
    area1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
    area2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
    xi_min = max(b1[0], b2[0])
    yi_min = max(b1[1], b2[1])
    xi_max = min(b1[2], b2[2])
    yi_max = min(b1[3], b2[3])
    inter_area = (yi_max - yi_min) * (xi_max - xi_min)
    union_area = area1 + area2 - inter_area
    iou = float(inter_area)/float(union_area)
    return iou 

def update_bb_recorder(bb, de_bb):
    new_bb_recorder = bb
    for i in range(len(de_bb)):
        find_repeat = False
        for j in range(len(bb)):
            iou = iou_calculator(de_bb[i], bb[j][0])
            if iou >= 0.9:
                find_repeat = True
                new_bb_recorder[j] = [de_bb[i], bb[j][1]+2]
                break
        if not find_repeat:
            new_bb_recorder.append([de_bb[i], 2])
    new_b_r = []
    for bbox in new_bb_recorder:
        show_count = bbox[1] - 1
        if show_count < 1:
            continue
        if show_count > 720:
            new_b_r.append([bbox[0],720])
        else:       
            new_b_r.append([bbox[0], show_count])  
    return new_b_r

def box_not_repeated(box, repeats):
    for bb in repeats:
        if iou_calculator(bb, box) >= 0.9:
            return False
    return True

def update_repeat_area_variables(bb_recorder, new_bboxes):
    repeat_bbox = []
    bb_recorder = update_bb_recorder(bb_recorder, new_bboxes)
    for bbox_re in bb_recorder:
        if bbox_re[1] > 360:
            repeat_bbox.append(bbox_re[0])
    return bb_recorder, repeat_bbox

