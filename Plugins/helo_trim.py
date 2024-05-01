from gremlin.user_plugin import *

from jge.easing_functions import EasingGenerator, SmoothStep
from jge.axes.tuned_axis import AxisTuning, TunedAxis
from jge.axes.trimmed_axis import Scaling, TrimmedAxis

from Plugins.device_decorators import stick, pedals, is_paddle_pulled

# JG user plugins can display simple UI widgets like this:
# https://whitemagic.github.io/JoystickGremlin/user_plugins/
# file is `gremlin.user_plugin.py` in JG repo
x_curvature = FloatVariable(
    "X Curvature",
    "",
    initial_value = 0.0,
    min_value = -1.0,
    max_value = 1.0,
    is_optional = False
)
y_curvature = FloatVariable(
    "Y Curvature",
    "",
    initial_value = 0.0,
    min_value = -1.0,
    max_value = 1.0,
    is_optional = False
)
z_curvature = FloatVariable(
    "Z Curvature",
    "",
    initial_value = 0.0,
    min_value = -1.0,
    max_value = 1.0,
    is_optional = False
)

# TODO the only variables i ever change per airframe are curvature values, so
# it's all the further i'm taking this plugin's UI for now.

# setup ------------------------------------------------------------------------

easing = EasingGenerator.ConstantTime(SmoothStep(2, 2), 1, 0.75, 50)
x_axis = TrimmedAxis(TunedAxis(1, AxisTuning(x_curvature.value)), smooth_trim_easing=easing)
y_axis = TrimmedAxis(TunedAxis(2, AxisTuning(y_curvature.value)), smooth_trim_easing=easing)
z_axis = TrimmedAxis(TunedAxis(3, AxisTuning(z_curvature.value)), smooth_trim_easing=easing)

def reset_trim():
    '''helper function to reset trim on all axes'''
    x_axis.trim_smooth(0)
    y_axis.trim_smooth(0)
    z_axis.trim_smooth(0)

# handle axis movement ---------------------------------------------------------

@stick.axis(1)
def roll_moved(event):
    x_axis.set_vjoy(event.value, Scaling.Dynamic)

@stick.axis(2)
def pitch_moved(event):
    y_axis.set_vjoy(event.value, Scaling.Dynamic)

@pedals.axis(6)  # it's technically crosswind axis 6 even though it's labeled as axis 3 in JG UI. weird.
def rudder_moved(event):
    z_axis.set_vjoy(event.value, Scaling.Dynamic)

# handle position trimming -----------------------------------------------------

@stick.button(18)  # pinky button
def position_trim(event, joy):
    # NOTE always check if the event was a press, else you'll get a double
    # activation! (one on press and on on release!)
    if event.is_pressed:
        if is_paddle_pulled(joy):
            # reset trim if my paddle is pulled
            reset_trim()
        else:
            # only trim stick axes
            x_axis.trim_smooth()
            y_axis.trim_smooth()

# handle HAT switch trimming ---------------------------------------------------

# i tried out different methods, but ended up really liking the simple, instant
# "step" trimming, because it makes it easy to have consistent trim values

@stick.button(9)  # trim hat U
def trim_forward(event, joy):
    if event.is_pressed:
        if is_paddle_pulled(joy):
            # reset trim if my paddle is pulled
            reset_trim()
        else:
            # else trim forward like normal
            y_axis.inc_trim(-0.1)

@stick.button(11)  # trim hat D
def trim_aft(event, joy):
    if event.is_pressed:
        if is_paddle_pulled(joy):
            # trim rudder if my paddle is pulled. i normally don't like rudder
            # trim, but do i need it sometimes, so shift state it
            z_axis.trim_smooth()
        else:
            # else trim aft like normal
            y_axis.inc_trim(0.1)

@stick.button(12)  # trim hat L
def trim_left(event):
    if event.is_pressed:
        x_axis.inc_trim(-0.1)

@stick.button(10)  # trim hat R
def trim_right(event):
    if event.is_pressed:
        x_axis.inc_trim(0.1)
