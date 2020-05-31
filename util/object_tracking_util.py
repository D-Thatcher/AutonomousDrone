from __future__ import unicode_literals
import cv2
import numpy as np
from scipy import spatial
from itertools import tee, izip



def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def do_kdtree(combined_x_y_arrays, points):
    """
    Returns the np array of indices of points in combined_x_y_arrays that are closest to points

    e.g.
    combined_x_y_arrays <-
       array([[92.14673117, 13.77534758],
       [98.54777011, 33.85032899],
       [56.09304457,  8.00195266],
       [26.65179454, 70.34241889],
       [57.20960077,  7.37334471],
       [83.45449933, 94.33560961],
       [53.05171069, 24.39858403],
       [48.3750993 , 81.5119219 ],
       [76.22763828, 25.2616434 ],
       [65.19508197, 32.29815772]])

    points <- [[93, 14],[77,24],[66,32]]

    returns array([0, 8, 9])

    """
    mytree = spatial.cKDTree(combined_x_y_arrays)
    dist, indexes = mytree.query(points)
    return dist, indexes


def centers(bboxes_before, bboxes_after):
    # Replace all bboxes with their centers

    # (bymin, bxmin, bymax, bxmax) = bboxes_before[0,:,0],bboxes_before[0,:,1],bboxes_before[0,:,2],bboxes_before[0,:,3]
    # (aymin, axmin, aymax, axmax) = bboxes_after[0,:,0],bboxes_after[0,:,1],bboxes_after[0,:,2],bboxes_after[0,:,3]

    (bymin, bxmin, bymax, bxmax) = bboxes_before[:, 0], bboxes_before[:, 1], bboxes_before[:,2], bboxes_before[:, 3]
    (aymin, axmin, aymax, axmax) = bboxes_after[:, 0], bboxes_after[:, 1], bboxes_after[:, 2], bboxes_after[:, 3]

    areas_before = (bymax-bymin)*(bxmax-bxmin)
    areas_after = (aymax-aymin)*(axmax-axmin)


    center_before_x= (bxmin+bxmax)/2.
    center_before_y = (bymin+bymax)/2.

    center_before_x = np.expand_dims(center_before_x,1)
    center_before_y = np.expand_dims(center_before_y,1)

    center_before = np.hstack((center_before_x,center_before_y))

    center_after_x = (axmin + axmax) / 2.
    center_after_y = (aymin + aymax) / 2.

    center_after_x = np.expand_dims(center_after_x, 1)
    center_after_y = np.expand_dims(center_after_y, 1)

    center_after = np.hstack((center_after_x, center_after_y))


    return center_before,center_after, areas_before, areas_after



def check_within(val, threshold):
    if val < 0 : raise ValueError("Unexpected val "+str(val))
    if (abs(1 - val)<threshold) or (val < threshold):
        return False
    return True

def check_all_within(vals, threshold=0.05):
    ret = True
    for upck in vals:
        ret = ret and check_within(upck, threshold)
    return ret

def any_shape_entry_zero(shp):
    return not all(shp)


def draw_line_between_shortest(img, bboxes_before, bboxes_after, classes_before, classes_after, lo_trail):
    """
    :param img: Image to draw on (debugging)
    :param bboxes_before: Allow for change in area calculation
    :param bboxes_after:  Allow for change in area calculation and
    :param classes_before:
    :param classes_after:
    :return:
    """
    change_in_area = {}
    area = {}

    if img is None:
        print('None')
        return area, change_in_area

    if any_shape_entry_zero(classes_before.shape) or any_shape_entry_zero(classes_after.shape): return area, change_in_area

    h,w = img.shape[:2]

    center_before, center_after, areas_before, areas_after = centers(bboxes_before, bboxes_after)

    # Classes that are present, both before and after
    drawable_classes= set(list(classes_before)).intersection(set(list(classes_after)))


    drawable_classes = np.array(list(drawable_classes))

    # if a trail wasn't appending to, pop it by checking this index set
    shouldnt_pop = set()

    for drawable_class in drawable_classes:

        to_idx_before = np.where(classes_before == drawable_class)[0]
        to_idx_after = np.where(classes_after == drawable_class)[0]

        if to_idx_before.shape[0] == 0 or (to_idx_after.shape[0] == 0):
            return area, change_in_area

        center_before_curr = center_before[to_idx_before,:]
        center_after_curr = center_after[to_idx_after,:]

        areas_before_curr = areas_before[to_idx_before]
        areas_after_curr = areas_after[to_idx_after]

        num_bbox_before = areas_before_curr.shape
        num_bbox_after = areas_after_curr.shape



        did_swap = False
        if num_bbox_before < num_bbox_after:
            did_swap = True
            temp_center = center_after_curr.copy()
            center_after_curr = center_before_curr.copy()
            center_before_curr = temp_center



        dist, indexes = do_kdtree(center_before_curr, center_after_curr)

        closest_points_to_center_after_curr = center_before_curr[indexes]

        num_pts, _ =center_after_curr.shape

        change_in_area[drawable_class] = []
        area[drawable_class] = []




        for ii in range(num_pts):
            p1 = closest_points_to_center_after_curr[ii,:]
            p2 = center_after_curr[ii,:]

            abefore =areas_before_curr[ii]
            aafter =areas_after_curr[ii]
            # print('areas_after_curr.shape',areas_after_curr.shape)
            # print("Area Before ",abefore)
            # print("Area After ",aafter)
            # if abefore < aafter:
            #     print('increasing\n')
            # else:
            #     print('decreasing\n')



            # Continue if anything is too close to the edge
            # if not (check_all_within(p1) and check_all_within(p2)):
            #     continue

            # Set a threshold for how big a line can be TODO -> replace with how big a line can grow
            if dist[ii] > 0.09:
                continue

            change_in_area[drawable_class].append(aafter - abefore)
            area[drawable_class].append(aafter)

            p1 = (int(p1[0]*w),int(p1[1]*h))
            p2 = (int(p2[0]*w),int(p2[1]*h))

            if not did_swap:
                did_append = False
                for it, trail in enumerate(lo_trail):
                    if p1 == trail[-1]:
                        trail.append(p2)
                        did_append = True
                        shouldnt_pop.add(it)

                if not did_append:
                    # if len(lo_trail)>0: lo_trail.pop(0)
                    lo_trail.append([p2])
                    shouldnt_pop.add(len(lo_trail)-1)


            else:
                did_append = False
                for it, trail in enumerate(lo_trail):
                    if p2 == trail[-1]:
                        trail.append(p1)
                        did_append = True
                        shouldnt_pop.add(it)


                if not did_append:
                    # if len(lo_trail)>0: lo_trail.pop(0)
                    lo_trail.append([p1])
                    shouldnt_pop.add(len(lo_trail)-1)

    for curr_trail in lo_trail:
        for p_i, p_ii in pairwise(curr_trail):
            cv2.arrowedLine(img, p_i, p_ii, (0, 255, 0), 3, tipLength=0.5)

    # new_lo_trail = []
    for curr_it in range(len(lo_trail)):
        if curr_it not in shouldnt_pop or (len(lo_trail[curr_it])>5):
            lo_trail[curr_it].pop(0)


    lo_trail[:] = (i for i in lo_trail if len(i)>0)


    return area, change_in_area





def draw_line_between_shortest_old(img, bboxes_before, bboxes_after, classes_before, classes_after):
    """
    :param img: Image to draw on (debugging)
    :param bboxes_before: Allow for change in area calculation
    :param bboxes_after:  Allow for change in area calculation and
    :param classes_before:
    :param classes_after:
    :return:
    """
    change_in_area = {}
    area = {}

    if img is None:
        print('None')
        return area, change_in_area

    if any_shape_entry_zero(classes_before.shape) or any_shape_entry_zero(classes_after.shape): return area, change_in_area


    h,w = img.shape[:2]

    center_before, center_after, areas_before, areas_after = centers(bboxes_before, bboxes_after)

    # There must be at least two of each class to consider drawing
    # drawable_classes= set(list(np.squeeze(classes_before,axis=0))).intersection(set(list(np.squeeze(classes_after,axis=0))))
    drawable_classes= set(list(classes_before)).intersection(set(list(classes_after)))

    # if len(drawable_classes) == 0:
    #     print('No drawable')
    #     return area, change_in_area



    drawable_classes = np.array(list(drawable_classes))

    for drawable_class in drawable_classes:

        to_idx_before = np.where(classes_before == drawable_class)[0]
        to_idx_after = np.where(classes_after == drawable_class)[0]
        if to_idx_before.shape[0] == 0 or (to_idx_after.shape[0] == 0):
            print('Zero shape')
            return

        center_before_curr = center_before[to_idx_before,:]
        center_after_curr = center_after[to_idx_after,:]

        areas_before_curr = areas_before[to_idx_before]
        areas_after_curr = areas_after[to_idx_after]

        # If a bbox of the same class is introduced, there might be a disagreement between num bbox before and after
        # For now, let's simply return if this is the case
        num_bbox_before = areas_before_curr.shape
        num_bbox_after = areas_after_curr.shape



        did_swap = False
        if num_bbox_before < num_bbox_after:
            did_swap = True
            temp_center = center_after_curr.copy()
            center_after_curr = center_before_curr.copy()
            center_before_curr = temp_center



        dist, indexes = do_kdtree(center_before_curr, center_after_curr)

        closest_points_to_center_after_curr = center_before_curr[indexes]

        num_pts, _ =center_after_curr.shape

        change_in_area[drawable_class] = []
        area[drawable_class] = []


        for ii in range(num_pts):
            p1 = closest_points_to_center_after_curr[ii,:]
            p2 = center_after_curr[ii,:]

            abefore =areas_before_curr[ii]
            aafter =areas_after_curr[ii]
            print('areas_after_curr.shape',areas_after_curr.shape)
            print("Area Before ",abefore)
            print("Area After ",aafter)
            if abefore < aafter:
                print('increasing\n')
            else:
                print('decreasing\n')



            # Continue if anything is too close to the edge
            # if not (check_all_within(p1) and check_all_within(p2)):
            #     continue

            # Set a threshold for how big a line can be TODO -> replace with how big a line can grow
            if dist[ii] > 0.09:
                print('continue')
                continue

            change_in_area[drawable_class].append(aafter - abefore)
            area[drawable_class].append(aafter)

            p1 = (int(p1[0]*w),int(p1[1]*h))
            p2 = (int(p2[0]*w),int(p2[1]*h))

            lineThickness = 3
            if did_swap:
                cv2.arrowedLine(img, p2, p1, (0, 255, 0), lineThickness, tipLength=0.5)
            else:
                cv2.arrowedLine(img, p1, p2, (0, 255, 0), lineThickness,tipLength=0.5)

    return area, change_in_area











def get_bbox_area(bbox):

    """
    Assume box unpacks to normalized(ymin, xmin, ymax, xmax)
    If any of the four floats are within 0.01 of boundary, ret <- False

    """
    THRESHOLD=0.05

    (ymin, xmin, ymax, xmax) = bbox


    ret =check_all_within(bbox,threshold=THRESHOLD)

    return ret, (xmax-xmin)*(ymax-ymin)





def write_text(img, msg):
    h,w,_ = img.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (w//2 - 2*len(msg),h//2)
    fontScale = 1
    fontColor = (255, 255, 255)
    lineType = 2

    cv2.putText(img, msg,
                bottomLeftCornerOfText,
                font,
                fontScale,
                fontColor,
                lineType)




