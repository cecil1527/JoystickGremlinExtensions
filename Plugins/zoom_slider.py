from gremlin.user_plugin import *

import imports

import utils
from utils import LookupTable
from lut_axis import LutAxis

from device_decorators import throttle


min_fov = IntegerVariable(
    "Min FoV",
    "Minimum field of view in game.",
    initial_value = 20,
    min_value = 0,
    max_value = 160,
    is_optional = False
)
max_fov = IntegerVariable(
    "Max FoV",
    "Maximum field of view in game.",
    initial_value = 140,
    min_value = 0,
    max_value = 160,
    is_optional = False
)
centered_fov = IntegerVariable(
    "Centered FoV",
    "What field of view would you like when the slider is centered?",
    initial_value = 80,
    min_value = 0,
    max_value = 160,
    is_optional = False
)


# figure out the desired FOV's value for the LUT
fov_val = utils.lerp(
    min_fov.value, -1, 
    max_fov.value, 1, 
    centered_fov.value
)

zoom_axis = LutAxis(8, LookupTable.FromPoints(
    (-1, -1),
    (0, fov_val),
    (1, 1),
))

@throttle.axis(3)  # zoom slider
def zoom_moved(event):
    zoom_axis.set(event.value)