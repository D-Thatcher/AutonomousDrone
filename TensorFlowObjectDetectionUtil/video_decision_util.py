import sys
import time
sys.path.append('/home/nvidia/.local/lib/python2.7/site-packages')

def find_out_playing_video(video_counter, video_map, queue_threshold, detection):
    for name in video_counter:
        if name in detection['names']:
            video_counter[name].append(1)
        else:
            video_counter[name].append(0)
        video_counter[name].pop(0)
    last_prediction = ''
    
    for name in video_counter:
        if sum(video_counter[name]) >= queue_threshold[name]:
            find_video = 0
            for video in video_map:
                if name in video_map[video]:
                    last_prediction = last_prediction + ' ' + video
                    find_video = 1
                    break
    last_prediction = last_prediction + ' ' + str(time.time()) 
    return last_prediction, video_counter

def need_to_sleep(start, end):
    time_now = int(time.strftime("%H%M%S", time.localtime()))
    if start< time_now or time_now < end:
        return True
    return False
