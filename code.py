# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

import time
import board
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix

BLINK = True
DEBUG = False

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print("    Metro Minimal Clock")
print("Time will be set for {}".format(secrets["timezone"]))

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # amber
color[3] = 0x85FF00  # greenish

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.show(group)

if not DEBUG:
    font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
else:
    font = terminalio.FONT

hours_label = Label(font)
colon_label = Label(font)
minutes_label = Label(font)
minutes_label2 = Label(font)

def update_time(*, hours=None, minutes=None, show_colon=False):
    now = time.localtime()  # Get the time values we need
    if hours is None:
        hours = now[3]
    if hours >= 18 or hours < 6:  # evening hours to morning
        hours_label.color = color[1]
    else:
        hours_label.color = color[3]  # daylight hours
    if hours > 12:  # Handle times later than 12:59
        hours -= 12
    elif not hours:  # Handle times between 0:00 and 0:59
        hours = 12

    if minutes is None:
        minutes = now[4]

    colon = ":"
    if BLINK:
        colon_label.color = color[2] if show_colon or now[5] % 2 else color[0]
    else:
        colon_label.color = color[0]

   
    #We need a label for each colour we're going to display. Starting with colon.
    colon_label.text = "{colon}".format(
        colon=colon
    )
    cbbx, cbby, cbbwidth, cbbh = colon_label.bounding_box
    # Center the label
    colon_label.x = round(display.width / 2 - cbbwidth / 2)
    colon_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(cbbx, cbby, cbbwidth, cbbh))
        print("Label x: {} y: {}".format(colon_label.x, colon_label.y))  
    
    #Hours label
    hours_label.text = "{hours}".format(
        hours=hours)
    hbbx, hbby, hbbwidth, hbbh = hours_label.bounding_box
    # Center the label
    hours_label.x = round(display.width / 2 - (cbbwidth + hbbwidth))
    hours_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(hbbx, hbby, hbbwidth, hbbh))
        print("Label x: {} y: {}".format(hours_label.x, hours_label.y))
 
  #Minutes label
    minutes_label.text = "{minutes:02d}".format(
        minutes=minutes
    )
    mbbx, mbby, mbbwidth, mbbh = minutes_label.bounding_box
    # Center the label
    minutes_label.x = round(display.width / 2 + cbbwidth)
    minutes_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(mbbx, mbby, mbbwidth, mbbh))
        print("Label x: {} y: {}".format(minutes_label.x, minutes_label.y))
 
    #Second minutes label
    minutes_label2.text = "{minutes:02d}".format(
        minutes=minutes
    )
    m2bbx, m2bby, m2bbwidth, m2bbh = minutes_label2.bounding_box
    # Center the label
    minutes_label2.x = round(display.width / 2 + cbbwidth + mbbwidth)
    minutes_label2.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(m2bbx, m2bby, m2bbwidth, m2bbh))
        print("Label x: {} y: {}".format(minutes_label2.x, minutes_label2.y))


last_check = None
update_time(show_colon=True)  # Display whatever time is on the board
group.append(hours_label)  # add the clock label to the group
group.append(colon_label)  # add the clock label to the group
group.append(minutes_label)  # add the clock label to the group

while True:
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True
            )  # Make sure a colon is displayed while updating
            network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    update_time()
    time.sleep(1)

