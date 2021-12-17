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
color = displayio.Palette(8)  # Create a color palette
color[0] = 0x000000  # black
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # orange
color[3] = 0x85FF00  # yellow
color[4] = 0x00FF00  # green
color[5] = 0x0000FF  # blue
color[6] = 0xFF00FF  # purple
color[7] = 0xFF40AA  # pink

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
minutes_second_digit_label = Label(font)

def update_time(*, hours=None, minutes=None, show_colon=False):
    now = time.localtime()  # Get the time values we need
    if hours is None:
        hours = now[3]
    if hours > 12:  # Handle times later than 12:59
        hours -= 12
    elif not hours:  # Handle times between 0:00 and 0:59
        hours = 12

    if minutes is None:
        minutes = now[4]

    colon = ":"
    if BLINK:
        colon_label.color = color[3] if show_colon or now[5] % 2 else color[0]
    else:
        colon_label.color = color[0]

    if DEBUG: 
        print("Hours is {} and minutes is {}".format(hours, minutes))

    hours_label.color = color[1]
    minutes_label.color = color[4]
    minutes_second_digit_label.color = color[5]

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

    #First minutes label.
    minutes_label.text = "{minutes}".format(
    minutes = (minutes // 10)
    )
    mbbx, mbby, mbbwidth, mbbh = minutes_label.bounding_box
    # Center the label
    minutes_label.x = round(display.width / 2 + cbbwidth)
    minutes_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(mbbx, mbby, mbbwidth, mbbh))
        print("Label x: {} y: {}".format(minutes_label.x, minutes_label.y))

    #Second minutes label
    minutes_second_digit_label.text = "{minutes}".format(
        minutes = (minutes % 10)
    )
    m2bbx, m2bby, m2bbwidth, m2bbh = minutes_second_digit_label.bounding_box
    # Center the label
    minutes_second_digit_label.x = round(display.width / 2 + cbbwidth + mbbwidth)
    minutes_second_digit_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(m2bbx, m2bby, m2bbwidth, m2bbh))
        print("Label x: {} y: {}".format(minutes_second_digit_label.x, minutes_second_digit_label.y))


last_check = None
update_time(show_colon=True)  
group.append(hours_label)  
group.append(colon_label)  
group.append(minutes_label)  
group.append(minutes_second_digit_label)  

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

