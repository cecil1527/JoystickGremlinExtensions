import gremlin
from gremlin.user_plugin import *

from jge.utils import utils
from jge.utils.lut import LookupTable
from jge.axes.lut_axis import LutAxis
from jge.utils.smoothing import ExponentialSmoothing, PassthroughSmoothing

# https://whitemagic.github.io/JoystickGremlin/user_plugins_code/

mode = ModeVariable("Mode", "")

controller_axis = PhysicalInputVariable(
    "Controller Axis",
    "Which physical axis would you like to control zoom?",
    valid_types=[gremlin.common.InputType.JoystickAxis],
)

vjoy_axis_num = IntegerVariable(
    "vJoy Axis",
    "Which vJoy axis would you like to use for zoom?",
    initial_value=1,
    min_value=1,
    max_value=8,
    is_optional=False,
)

min_fov = IntegerVariable(
    "Min FoV",
    "Minimum field of view in game.",
    initial_value=20,
    min_value=0,
    max_value=180,
    is_optional=False,
)

max_fov = IntegerVariable(
    "Max FoV",
    "Maximum field of view in game.",
    initial_value=140,
    min_value=0,
    max_value=180,
    is_optional=False,
)

centered_fov = IntegerVariable(
    "Centered FoV",
    "What field of view would you like when the slider is centered?",
    initial_value=80,
    min_value=0,
    max_value=180,
    is_optional=False,
)

use_smoothing = BoolVariable(
    "Smooth Axis",
    "Whether to smooth the axis or not.",
    initial_value=False,
    is_optional=False,
)

smoothing_coef = IntegerVariable(
    "Smoothing Coefficient (%)",
    "Alpha smoothing coefficient. Lower is more smoothing. Values should range [0, 100]",
    initial_value=10,
    min_value=0,
    max_value=100,
    is_optional=False,
)

passthrough_region = IntegerVariable(
    "Passthrough Region (%)",
    "Smoothing passthrough region, where no smoothing occurs above the absolute value of this value. Value should range [0, 100]",
    initial_value=95,
    min_value=0,
    max_value=100,
    is_optional=False,
)

# setup ------------------------------------------------------------------------

# calc the axis value for our desired FOV when axis is centered
fov_val = utils.lerp(min_fov.value, -1, max_fov.value, 1, centered_fov.value)

# JG float variables are broken, so i'm using ints as percents instead :(
coef = smoothing_coef.value / 100.0
pasthrough = passthrough_region.value / 100.0
smoothing = PassthroughSmoothing(ExponentialSmoothing(coef), pasthrough)

zoom_axis = LutAxis(
    vjoy_axis_num.value,
    LookupTable.FromPoints(
        (-1, -1),
        (0, fov_val),
        (1, 1),
    ),
)
axis_dectorator = controller_axis.create_decorator(mode.value)

# you can define decoratored functions in branches. this way we get whatever
# behavior the user wants, but only have to evaluate it once
if use_smoothing.value:

    @axis_dectorator.axis(controller_axis.input_id)
    def zoom_moved(event):
        smooted_input = smoothing(event.value)
        zoom_axis.set(smooted_input)
else:

    @axis_dectorator.axis(controller_axis.input_id)
    def zoom_moved(event):
        zoom_axis.set(event.value)
