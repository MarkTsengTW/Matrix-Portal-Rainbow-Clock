# Rainbow Clock for Adafruit Matrix Portal
# Based on John Park and Kattni Rembor's Metro Minimal Clock. With added rainbows.

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

# Import your Circuitpython secrets
try:
    from secrets import secrets
except ImportError:
    print("Failed to load details from secrets.py")
    raise
print("Time will be set for {}".format(secrets["timezone"]))

# Initialise the matrix
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# Set up for writing coloured labels. (Here we spell colour with a u when we can, and with no u when we have to!)
group = displayio.Group()
bitmap = displayio.Bitmap(64, 32, 2)
# Create a palette with all the colours of the rainbow.
# Including pink, which nature somehow forgot to put in real rainbows?
# Pedants can change it to indigo by editing the hex codes for colours [6] and [7].
# The colours are adjusted look nicer on the Adafruit LED matrix.
color = displayio.Palette(9)
color[0] = 00000000  # black background
color[1] = 0xAA0000  # red
color[2] = 0xF04800  # orange
color[3] = 0xFFD500  # yellow
color[4] = 0x00FF00  # green
color[5] = 0x0000FF  # blue
color[6] = 0x6600CD  # purple
color[7] = 0xE80064  # pink
color[8] = 0xE80064  # An extra space so we can rotate the colours.

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.show(group)

if not DEBUG:
    font = bitmap_font.load_font("/IBMPlexMono-Medium-24_mt.bdf")
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
    if hours > 12:  # No military time thanks. Comment this out if you join the army.
        hours -= 12
    elif not hours:  # Make midnight 12am rather than zero am.
        hours = 12
    if minutes is None:
        minutes = now[4]
  
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
    # I haven't worked out how to center multiple labels as a group so I'll start with arbitrary space on the left.
    #The amount of space decreases if it's 12am or 12pm.
    offset = 8
    offset_2_hours_digits = 2

    # This label appears if the hours are 11 or 12.
    if (hours // 10) >= 1:
        hours_label.text = "{hours}".format(hours=(hours // 10))
        hbbx, hbby, hbbwidth, hbbh = hours_label.bounding_box
        hours_label.x = offset_2_hours_digits
        hours_label.y = display.height // 2

    hours_second_digit_label.text = "{hours}".format(hours=(hours % 10))
    h2bbx, h2bby, h2bbwidth, h2bbh = hours_second_digit_label.bounding_box
    # The spacing is conditional on whether the hours are one or two digits.
    if (hours // 10) >= 1:
        hours_second_digit_label.x = (hours_label.x + hbbwidth)
    else:
        hours_second_digit_label.x = offset
    hours_second_digit_label.y = display.height // 2

    colon_label.text = "{colon}".format(colon=colon)
    cbbx, cbby, cbbwidth, cbbh = colon_label.bounding_box
    colon_label.x = (hours_second_digit_label.x + h2bbwidth)
    colon_label.y = display.height // 2

    minutes_label.text = "{minutes}".format(minutes=(minutes // 10))
    mbbx, mbby, mbbwidth, mbbh = minutes_label.bounding_box
    minutes_label.x = (colon_label.x + cbbwidth + 1) # Another arbitrary offset for the colon. I should edit the font!
    minutes_label.y = display.height // 2

    minutes_second_digit_label.text = "{minutes}".format(minutes=(minutes % 10))
    m2bbx, m2bby, m2bbwidth, m2bbh = minutes_second_digit_label.bounding_box
    minutes_second_digit_label.x = (minutes_label.x + mbbwidth + 1) # Another arbitrary offset. The number 4 is too big!
    minutes_second_digit_label.y = display.height // 2

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

# Get ready to run the clock
last_check = None
update_time(show_colon=True)
group.append(hours_label)
group.append(hours_second_digit_label)
group.append(colon_label)
group.append(minutes_label)
group.append(minutes_second_digit_label)

# Main loop
while True:
    #This if statement updates the time from the internet once an hour and also handles display while the clock is syncing to the internet.
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True
            )  # Make sure a colon is displayed while updating
            network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
    #This runs the clock during the remainder of the hour.
    update_time()
    time.sleep(1)
