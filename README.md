# Export your image diary from BeReal

I was tired to every day press download on my BeReals in order to have them locally so I created these scripts to help me with it.
Works for Android phones. Tested on Linux/Ubuntu computer. This is not affiliated with or endorsed by [BeReal](https://bereal.com/), use at your own risk.

## Requirements
1) Enable USB-debugging on Android phone and connect to computer
2) Install adb tools and make sure phone is visible with `adb devices`
3) Extract correct mouse locations from a transferred screenshot:
    - Tap to open settings
    - Tap to download
    - Tap to switch between cameras
    - Swipe locations for next image
4) Setup phone to be ready to start

## How to use
Execute `automate_save.py` with python for the script. The other one `bereal_change_time.py` can be used to add meta-informations about the time to the images.

## Known limitations
This only works for Android. Some individual settings need to be taken (inserting pixel positions) and this script needs to be executed from the command line. A depiction of the locations can be found in `example-image.png`. In case it crashes just restart and continue.
