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
# Create a palette with all the colours of the rainbow.
# Including pink, which nature somehow forgot to put in real rainbows?
# Pedants can change it to indigo by editing the hex codes for colours [6] and [7].
color = displayio.Palette(9)
color[0] = 00000000  # black background
color[1] = 0xCC0000  # red
color[2] = 0xFF6F00  # orange
color[3] = 0xFFFF00  # yellow
color[4] = 0x00FF00  # green
color[5] = 0x0000FF  # blue
color[6] = 0x6600CD  # purple
color[7] = 0xE80064  # pink
color[8] = 0xE80064  # pink

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.show(group)

if not DEBUG:
    font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
else:
    font = terminalio.FONT

hours_label = Label(font)
hours_second_digit_label = Label(font)
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

    if DEBUG:
        print("Hours is {} and minutes is {}".format(hours, minutes))

    # Make everything colourful. 
    colon = ":"
    if BLINK:
        if show_colon or now[5] % 2:
            update_colours()
            colon_label.color = color[7]  
        else: 
            colon_label.color = 0x000000
    else:
        colon_label.color = color[1]
    hours_label.color = color[5]
    hours_second_digit_label.color = color[6]
    minutes_label.color = color[1]
    minutes_second_digit_label.color = color[2]

    # We need a label for each digit of the display because they're all different colours.
   
    if (hours // 10) == 1:
        hours_label.text = "{hours}".format(hours=(hours // 10))
        hbbx, hbby, hbbwidth, hbbh = hours_label.bounding_box
        hours_label.x = 0
        hours_label.y = display.height // 2
        if DEBUG:
            print("Label bounding box: {},{},{},{}".format(hbbx, hbby, hbbwidth, hbbh))
            print("Label x: {} y: {}".format(hours_label.x, hours_label.y))

    hours_second_digit_label.text = "{hours}".format(hours=(hours % 10))
    h2bbx, h2bby, h2bbwidth, h2bbh = hours_second_digit_label.bounding_box
    if (hours // 10) == 1:
        hours_second_digit_label.x = hbbwidth
    else:
        hours_second_digit_label.x = 0
    hours_second_digit_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(h2bbx, h2bby, h2bbwidth, h2bbh))
        print(
            "Label x: {} y: {}".format(
                hours_second_digit_label.x, hours_second_digit_label.y
            )
        )

    colon_label.text = "{colon}".format(colon=colon)
    cbbx, cbby, cbbwidth, cbbh = colon_label.bounding_box
    colon_label.x = (hours_second_digit_label.x + h2bbwidth)
    colon_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(cbbx, cbby, cbbwidth, cbbh))
        print("Label x: {} y: {}".format(colon_label.x, colon_label.y))
    
    minutes_label.text = "{minutes}".format(minutes=(minutes // 10))
    mbbx, mbby, mbbwidth, mbbh = minutes_label.bounding_box
    # Center the label
    minutes_label.x = (colon_label.x + cbbwidth)
    minutes_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(mbbx, mbby, mbbwidth, mbbh))
        print("Label x: {} y: {}".format(minutes_label.x, minutes_label.y))

    minutes_second_digit_label.text = "{minutes}".format(minutes=(minutes % 10))
    m2bbx, m2bby, m2bbwidth, m2bbh = minutes_second_digit_label.bounding_box
    # Center the label
    minutes_second_digit_label.x = (minutes_label.x + mbbwidth)
    minutes_second_digit_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(m2bbx, m2bby, m2bbwidth, m2bbh))
        print(
            "Label x: {} y: {}".format(
                minutes_second_digit_label.x, minutes_second_digit_label.y
            )
        )

#If there's a way of doing this with a loop let me know.
def update_colours():
    global color
    color[8] = color[1]
    color[1] = color[2]
    color[2] = color[3]
    color[3] = color[4]
    color[4] = color[5]
    color[5] = color[6]
    color[6] = color[7]
    color[7] = color[8]

last_check = None
update_time(show_colon=True)
colour_change_interval = 2
colour_change_timer = 0
group.append(hours_label)
group.append(hours_second_digit_label)
group.append(colon_label)
group.append(minutes_label)
group.append(minutes_second_digit_label)

while True:
    #This handles display while the clock is syncing to the internet.
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True
            )  # Make sure a colon is displayed while updating
            network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
    #This runs the clock once it's getting internet time.
    update_time()
    #colour_change_timer += 1
    #if colour_change_timer >= colour_change_interval:
    #    update_colours()
    #    colour_change_timer = 0
    time.sleep(1)
