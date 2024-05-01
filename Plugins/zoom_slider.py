import gremlin
from gremlin.user_plugin import *

from jge import utils
from jge.utils import LookupTable
from jge.axes.lut_axis import LutAxis

# https://whitemagic.github.io/JoystickGremlin/user_plugins_code/

mode = ModeVariable(
    "Mode",
    ""
)

controller_axis = PhysicalInputVariable(
    "Controller Axis",
    "Which physical axis would you like to control zoom?",
    # valid_types = [gremlin.types.InputType.JoystickAxis]
)

vjoy_axis_num = IntegerVariable(
    "vJoy Axis",
    "Which vJoy axis would you like to use for zoom?",
    initial_value = 1,
    min_value = 1,
    max_value = 8,
    is_optional = False
)

min_fov = IntegerVariable(
    "Min FoV",
    "Minimum field of view in game.",
    initial_value = 20,
    min_value = 0,
    max_value = 180,
    is_optional = False
)

max_fov = IntegerVariable(
    "Max FoV",
    "Maximum field of view in game.",
    initial_value = 140,
    min_value = 0,
    max_value = 180,
    is_optional = False
)

centered_fov = IntegerVariable(
    "Centered FoV",
    "What field of view would you like when the slider is centered?",
    initial_value = 80,
    min_value = 0,
    max_value = 180,
    is_optional = False
)

# figure out the desired FOV's value for the LUT
fov_val = utils.lerp(
    min_fov.value, -1, 
    max_fov.value, 1, 
    centered_fov.value
)

zoom_axis = LutAxis(vjoy_axis_num.value, LookupTable.FromPoints(
    (-1, -1),
    (0, fov_val),
    (1, 1),
))

axis_dectorator = controller_axis.create_decorator(mode.value)

@axis_dectorator.axis(controller_axis.input_id)
def zoom_moved(event):
    zoom_axis.set(event.value)