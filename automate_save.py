### Script to save all BeReal pictures ###
#
#   Author: Julius Bergmann
#   
#   Automates saving process by simulating touch presses and transferring data
#   Preparation:
#      1) Enable USB-debugging on Android phone and connect to computer
#      2) Install adb tools and make sure phone is visible with "adb devices"
#      3) Extract correct mouse locations from a transferred screenshot:
#           - Tap to open settings
#           - Tap to download
#           - Tap to switch between cameras
#           - Swipe locations for next image
#      4) Setup phone to be ready to start

### Needed pixel positions (X,Y) - insert if not present ###

loc_swap_camera = (250, 550)         # Swapping protrayed camera on main pic (tap small image)
loc_open_settings = (1000, 175)      # Open settings (three small dots)
loc_download = (800, 450)            # Download (in sub-menu of settings)
loc_swipe_left = (150, 1000)         # Position on left side of main image, used for swiping
loc_swipe_right = (900, 1000)        # Position on right side of main image, used for swiping

### Other settings
bereal_saved_dir = "BeReal_saved"                     # Files will be saved in this folder in the current wkdir
loc_screenshot = "image.png"                           # In case screenshot wants to be taken to extract pixel position, this needs to be a valid location in wkdir
phone_loc_screenshot = "/sdcard/Pictures/image.png"    # In case screenshot wants to be taken to extract pixel position, this needs to be a valid location on phone

# Imports
import numpy as np, os, subprocess, time, cv2, re

# Some workspace settings
wkdir = os.path.split(__file__)[0]
bereal_saved_dir = os.path.join(wkdir, bereal_saved_dir)
loc_screenshot = os.path.join(wkdir, loc_screenshot)
if not os.path.isdir(bereal_saved_dir): os.mkdir(bereal_saved_dir)

### adb functions to interact with android phone
# check if phone is connected
def adb_devices(debug=False):
    res = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_out = res.stdout.decode("utf-8").split("\n")[:-2]
    connected_devices = len(res_out)-1
    if debug: print(f"Found {connected_devices} connected device(s): {res_out[1:]}")
    return connected_devices


# capture screen on phone and transfer to pc
def adb_capture_screen(loc, phone_loc=phone_loc_screenshot, debug=False):
    subprocess.run(["adb", "shell", "screencap", phone_loc])
    subprocess.run(["adb", "pull", phone_loc, loc])
    if debug: print(f"      Phone: Screenshot saved to {loc}")


# simulate tap on phone
def adb_click(x, y, debug=False):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
    if debug: print(f"      Phone: Clicked on ({x},{y})")


# simulate swipe movement
def adb_swipe(x1, y1, x2, y2, duration=100, debug=False):
    subprocess.run(["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])
    if debug: print(f"      Phone: Swiped from ({x1},{y1}) to ({x2},{y2})")


### CV2 functions for image processing
# check if two images are the same, used for when swapping camera didn't work
def cv2_check_similar(loc1, loc2, debug=False):
    img1, img2 = cv2.imread(loc1), cv2.imread(loc2)
    if img1.size != img2.size:
        res = False
    else:
        difference = cv2.subtract(img1, img2)
        res = not np.any(difference)
    if debug: print(f"      CV2: Images similar: {res}")
    return res


### BeReal functions to automate BeReal specific tasks
# swipe next image on bereal
def bereal_swipe_next(swipe_right=True, delay=200, debug=False):
    if swipe_right:
        adb_swipe(loc_swipe_left[0], loc_swipe_left[1], loc_swipe_right[0], loc_swipe_right[1], debug=False)
    else:
        adb_swipe(loc_swipe_right[0], loc_swipe_right[1], loc_swipe_left[0], loc_swipe_left[1], debug=False)
    if debug: print(f"   BeReal: Swiped to next image")
    time.sleep(delay*1e-3)  # sleep to give the system some time


# change camera direction on bereal
def bereal_swap_camera(delay=100, debug=False):
    adb_click(loc_swap_camera[0], loc_swap_camera[1], debug=False)
    if debug: print(f"   BeReal: Changed camera")
    time.sleep(delay*1e-3)  # sleep to give the system some time


# download
def bereal_download(delay=1000, debug=False):
    adb_click(loc_open_settings[0], loc_open_settings[1], debug=False)
    adb_click(loc_download[0], loc_download[1], debug=False)
    if debug: print(f"   BeReal: Downloaded")
    time.sleep(delay*1e-3)  # sleep to give the system some time


# get all files which are listed under bereal in download folder
def bereal_adb_list_saved(loc="sdcard/Download", bereal_prefix="be"):
    loc_search = os.path.join(loc, f"{bereal_prefix}*")
    res = subprocess.run(["adb", "shell", "ls", loc_search], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 1: return None
    else: return res.stdout.decode("utf-8").split("\n")[:-1]


# transfer several files over to the location folder and delete them afterwards
def bereal_adb_transfer_delete(loc, phone_loc_array, add=False, debug=False):
    for i_phone_loc in phone_loc_array:
        file_name = os.path.split(i_phone_loc)[1]
        file_name = re.sub(r' \(.*\)', '-2', file_name)
        if add: file_name = file_name.replace(".jpeg", "-2.jpeg")
        subprocess.run(["adb", "pull", i_phone_loc, os.path.join(loc,file_name)], stdout=subprocess.PIPE)
        subprocess.run(["adb", "shell", "rm", f'"{i_phone_loc}"'], stdout=subprocess.PIPE)
        if debug: print(f"      Phone: Transferred and deleted {i_phone_loc}")


# one time swipe and double save together
def bereal_save_one(swipe_right=True, debug=False, num=None):
    bereal_download()
    bereal_swap_camera()
    bereal_download()
    bereal_swap_camera()

    bereal_photos = bereal_adb_list_saved()
    bereal_adb_transfer_delete(bereal_saved_dir, bereal_photos)
    similar = cv2_check_similar(os.path.join(bereal_saved_dir, os.path.split(bereal_photos[1])[1]), os.path.join(bereal_saved_dir, os.path.split(bereal_photos[1])[1].replace(".jpeg", "-2.jpeg")))
    while similar:
        bereal_download()
        bereal_swap_camera()
        bereal_photos = bereal_adb_list_saved()
        bereal_adb_transfer_delete(bereal_saved_dir, bereal_photos, add=True)
        similar = cv2_check_similar(os.path.join(bereal_saved_dir, os.path.split(bereal_photos[0])[1]), os.path.join(bereal_saved_dir, os.path.split(bereal_photos[0])[1].replace(".jpeg", "-2.jpeg")))
        if debug: print(f"BeReal: Replaced wrong duplicate, both images are now different: {not similar}")

    bereal_swipe_next(swipe_right)
    if debug and num != None: print(f"BeReal: Saved image {num}: {bereal_photos[0][23:38]}")
    elif debug: print(f"BeReal: Saved image {bereal_photos[0][23:38]}")


# main function
if __name__ == "__main__":
    # Test if device is connected
    devices = adb_devices(debug=True)
    if devices != 1:
        print("Error: Device not found or too many devices connected. Ensure that only one Android phone is connected")
        exit(1)
    
    # Test if pixel variables are set
    if not len(loc_swap_camera) or not len(loc_download) or not len(loc_open_settings) or not len(loc_swipe_left) or not len(loc_swipe_right):
        print("Error: Not all pixel positions have been set.")
        text = input("Would you like to transfer a screenshot in order to extract the locations? Make sure the settings menu is open to be able to get all locations from one image!\n(yes/no) - ")  # Python 3
        if text.lower() in ["yes", "y"]:
            adb_capture_screen(loc_screenshot, phone_loc_screenshot, debug=True)
        exit()
    
    # ask user how many images should be taken
    text = input("How many images should be saved?\n(number or ""all"") - ")  # Python 3
    num_save = 100000  # initialize as big number for "all"
    try:
        num_save = int(text)
    except:
        if text.lower() != "all":
            print(f"Error: Wrong formatting for input: {text}")
            exit()
    
    # ask user which direction should be swiped
    text = input("In which direction should be swiped?\n(left/right) - ")  # Python 3
    if text.lower() in ["left", "l"]: swipe_right = False
    elif text.lower() in ["right", "r"]: swipe_right = True
    else:
        print(f"Error: Wrong formatting for input: {text}")
        exit()

    # loop over all images
    for i_num in range(num_save):
        bereal_save_one(swipe_right=swipe_right, debug=True, num=i_num)

    # bereal_save_one(debug=True)