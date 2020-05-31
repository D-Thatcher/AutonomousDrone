import time
import os
import datetime
import sys
import subprocess
sys.path.append('/home/nvidia/.local/lib/python2.7/site-packages')

def preparatory_work():
    today = datetime.date.today()
    path_today = "/mnt/usb/" +  str(today)
    if not os.path.ismount('/mnt/usb'):
        mount_usb()
    t = time.time()
    while not os.path.exists(path_today):
        if int(time.time() - t) > 30:
            break
    delete_previous_day_folders(today)
    if not os.path.exists(path_today):
        os.makedirs(path_today)
        os.makedirs(path_today + "/all_frames/all_frames/")
        os.makedirs(path_today + "/all_frames/log/")
    framenum = find_its_max_frame(path_today) + 1
    return today, path_today, framenum 

def mount_usb():
    time_now = time.time()
    output = None
    done = 0
    if os.path.exists("/mnt/usb"):
        os.system("sudo rm -r /mnt/usb")
    os.system("sudo mkdir /mnt/usb")
    while done == 0:
        try:
            output = subprocess.check_output("ls /dev/dm-0", shell=True)
            print(output)
            done = 1
        except subprocess.CalledProcessError as e:
            output = e.output
            print(output)
        if (time.time() - time_now) > 60:
            write_to_error_file(4)
    done = 0
    while done == 0:
        try:
            output = subprocess.check_output("sudo umount /dev/dm-0", shell=True)
            print(output)
            done = 1
        except subprocess.CalledProcessError as e:
            output = e.output
            print(output)
        if (time.time() - time_now) > 60:
            write_to_error_file(4)
    done = 0
    while done == 0:
        try:
            output = subprocess.check_output("sudo mount /dev/dm-0 /mnt/usb", shell=True)
            print(output)
            done = 1
        except subprocess.CalledProcessError as e:
            output = e.output
            print(output)
        if (time.time() - time_now) > 60:
            write_to_error_file(4)

def delete_previous_day_folders(today):
    list_days = os.listdir("/mnt/usb/")
    for days in list_days:
        path_to_day = "/mnt/usb/" + days
        try:
            length = len([i for i in os.listdir(path_to_day + "/all_frames/all_frames/")])
        #If there's an exception, it's because there are no folders    
        except:
            length = 0
        if length == 0 and str(days) != (today):
            os.system("sudo rm -r " + path_to_day)
            print("sudo rm -r " + path_to_day)
        else:
            if str(days) != str(today):
                write_to_error_file(3)

def find_usb_percent_full():
    output = subprocess.check_output("df /dev/dm-0", shell=True)
    percent = str(output).split()[-2][:-1]
    return percent

def write_to_error_file(error): 
    #ERROR 1: The USB is filling up (it is at least 75% full).
    #ERROR 2: The USB is almost completely full (95%) and recording frames has stopped.
    #ERROR 3: There are folders from at least one previous day that haven't been pushed for some reason.
    #ERROR 4: nousb
    with open("/home/nvidia/ping_errors/errors.txt", 'w') as the_file:
        the_file.write("!error" + str(error) + "!")

def find_its_max_frame(path_today):
    folder_list = os.listdir(path_today + '/all_frames/all_frames/')
    length = len(folder_list)
    if length == 0:
        return -1
    num_list = [int(i[6:]) for i in folder_list]
    num_list.sort()
    folder = num_list[-1]
    num_frame = len(os.listdir(path_today + '/all_frames/all_frames/folder' + str(folder) + '/'))
    framenum = folder * 1000 + num_frame - 1
    return framenum

def usb_storage_check():
    try:
        percent = find_usb_percent_full()
        print(str(percent) + "% full")
    except:
        percent = 0
        print("Cannot allocate memory")
    if 90 > int(percent) >= 75:
        write_to_error_file(1)
    if int(percent) >= 90:
        write_to_error_file(2)
        remove_redundant_data("/mnt/usb/", 30)


def remove_redundant_data(path_init, num):
    path = get_oldest_folder(path_init)
    folder_list = os.listdir(path)
    while len(folder_list) == 0:
        os.system('sudo rm -rf {}'.format(path[:-22]))
        path = get_oldest_folder(path_init)
        folder_list = os.listdir(path)
    if len(folder_list) <= num:
        for folder in folder_list:
            os.system('sudo rm -rf {}{}'.format(path, folder))
    else:
        folder_list = [int(i[6:]) for i in folder_list]
        folder_list.sort()
        for i in range(num):
            os.system('sudo rm -rf {}{}{}'.format(path, 'folder', str(folder_list[i])))

def get_oldest_folder(path):
    frame_date_list = os.listdir(path)
    frame_date_list.sort()
    frame_folders_path = path + frame_date_list[0] + "/all_frames/all_frames/"
    return frame_folders_path

