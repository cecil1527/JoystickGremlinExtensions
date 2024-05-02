import gremlin
from gremlin.user_plugin import *

from jge.axes.toggle_axis import ToggleAxis

'''
this plugin is useful for a rotary encoder. turn it one way to increase the
axis, turn it the other way to decrease the axis, and push it in to toggle the
axis to a different value.
'''

mode = ModeVariable(
    "Mode",
    ""
)

inc_btn = PhysicalInputVariable(
    "Volume Increase",
    "",
    valid_types = [gremlin.common.InputType.JoystickButton, gremlin.common.InputType.JoystickHat]
)

dec_btn = PhysicalInputVariable(
    "Volume Decrease",
    "",
    valid_types = [gremlin.common.InputType.JoystickButton, gremlin.common.InputType.JoystickHat]
)

toggle_btn = PhysicalInputVariable(
    "Volume Toggle",
    "",
    valid_types = [gremlin.common.InputType.JoystickButton, gremlin.common.InputType.JoystickHat]
)

# NOTE it seems JG float variable limits don't work correctly, so we're doing
# all integer values

inc_val = IntegerVariable(
    "Volume Increment Value (%)",
    "",
    initial_value = 10,
    min_value = -100,
    max_value = 100,
)

toggle_val = IntegerVariable(
    "Volume Toggle Value (%)",
    "",
    initial_value = -90,
    min_value = -100,
    max_value = 100,
)

vjoy_axis = IntegerVariable(
    "vJoy Axis Number",
    "",
    initial_value = 1,
    min_value = 1,
    max_value = 8,
)

# ------------------------------------------------------------------------------

vol_axis = ToggleAxis(vjoy_axis.value)
inc = inc_val.value / 100.0
tog = toggle_val.value / 100.0

inc_decorator = inc_btn.create_decorator(mode.value)
dec_decorator = dec_btn.create_decorator(mode.value)
toggle_decorator = toggle_btn.create_decorator(mode.value)

@inc_decorator.button(inc_btn.input_id)
def inc_vol(event):
    if event.is_pressed:
        vol_axis.step_axis(inc)

@dec_decorator.button(dec_btn.input_id)
def dec_vol(event):
    if event.is_pressed:
        vol_axis.step_axis(-inc)

@toggle_decorator.button(toggle_btn.input_id)
def toggle_vol(event):
    if event.is_pressed:
        vol_axis.toggle_to(tog)
        