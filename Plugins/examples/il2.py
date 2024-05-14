from Plugins.device_decorators import stick, throttle, is_paddle_pulled

from jge.utils.easing_functions import SmoothStart, EasingGenerator
from jge.axes.stepper_axis import StepperVals, StepperAxis
from jge.axes.relative_axis import RelativeAxis
from jge.axes.axis_button import AxisButton
from jge.sticky_buttons import StickyButtons

# prop pitch axis --------------------------------------------------------------

pp_easing = EasingGenerator.ConstantTime(SmoothStart(2), 1, 50, 0.05)
pp_rel_axis = RelativeAxis(8, pp_easing)

pp_stepper_vals = StepperVals.FromSpecificVals([2550, 2700, 3000], (1000, 3000))
pp_stepper_axis = StepperAxis(8, pp_stepper_vals, 2)


@stick.hat(1)
def adj_pp(event, joy):
    if is_paddle_pulled(joy):
        return

    # JG hat switches are [x, y], +1 is up/right and -1 is down/left
    if event.value == (0, 1):  # up
        pp_rel_axis.press(1)
    elif event.value == (0, -1):  # down
        pp_rel_axis.press(-1)
    elif event.value == (0, 0):  # center
        # NOTE this works for my hat, because if you press any diagonals,
        # then it activates the center, because it's only a 4-way hat
        pp_rel_axis.release()


@stick.button(6)  # master mode forward
def max_pp(event, joy):
    if is_paddle_pulled(joy):
        return

    if event.is_pressed:
        pp_stepper_axis.go_to_max_index()


@stick.button(7)  # master mode aft
def step_pp_lower(event, joy):
    if is_paddle_pulled(joy):
        return

    if event.is_pressed:
        # NOTE go to previous value, not index! this is in case the axis moved
        # from relative axis manipulation
        pp_stepper_axis.prev_value()


# wingspan axis ----------------------------------------------------------------
# 109, 190, 262, 110, ju88, he111 wingspans in ft are [32, 34, 41, 53, 59, 74]
# but since the 109 and 190 wingspans are so close, you can just do 33 for both

wingspan_stepper_vals = StepperVals.FromSpecificVals([33, 41, 53, 59, 74], (30, 100))
wingspan_stepper_axis = StepperAxis(7, wingspan_stepper_vals, 0)
wingspan_axis_button = AxisButton(0.25)
wingspan_easing = EasingGenerator.ConstantTime(SmoothStart(2), 2, 50, 0.05)


@throttle.axis(1)  # front slew x axis
def front_slew_x_moved(event, joy):
    if not is_paddle_pulled(joy):
        return

    wingspan_axis_button.update(event.value)
    state = wingspan_axis_button.get_state()
    if state == AxisButton.State.PressedHigh:
        wingspan_stepper_axis.next_index()
    elif state == AxisButton.State.PressedLow:
        wingspan_stepper_axis.prev_index()


# flaps hold -------------------------------------------------------------------

# flaps sometimes need held for a long time in certain planes, so do a "sticky"
# button when paddle is pulled

sticky_flaps = StickyButtons([10, 11])


@throttle.button(28)  # bottom thumb hat down
def flaps_dn(event, joy):
    if event.is_pressed:
        sticky_flaps.release_all()
        sticky_flaps.press(11)
    else:
        if is_paddle_pulled(joy):
            return
        sticky_flaps.release(11)


@throttle.button(30)  # bottom thumb hat up
def flaps_up(event, joy):
    if event.is_pressed:
        sticky_flaps.release_all()
        sticky_flaps.press(10)
    else:
        if is_paddle_pulled(joy):
            return
        sticky_flaps.release(10)


# trim hold --------------------------------------------------------------------

sticky_trim = StickyButtons([12, 13])


@stick.button(9)  # trim hat up
def trim_nose_dn(event, joy):
    if event.is_pressed:
        sticky_trim.release_all()
        sticky_trim.press(13)
    else:
        # always release this trim direction
        sticky_trim.release(13)


@stick.button(11)  # trim hat dn
def trim_nose_up(event, joy):
    if event.is_pressed:
        sticky_trim.release_all()
        sticky_trim.press(12)
    else:
        if is_paddle_pulled(joy):
            return
        sticky_trim.release(12)
