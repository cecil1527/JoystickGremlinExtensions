import gremlin

from jge.utils.lut import LookupTable
from jge.gremlin_interface import VjoyAxis, VjoyButton
from jge.utils.easing_functions import EasingGenerator, SmoothStart, SmoothStep
from jge.axes.axis_button import AxisButton
from jge.axes.stepper_axis import StepperVals, StepperAxis
from jge.axes.toggle_axis import ToggleAxis
from jge.axes.relative_axis import RelativeAxis
from jge.axes.lut_axis import LutAxis
from jge.axes.tuned_axis import AxisTuning, TunedAxis
from jge.axes.trimmed_axis import CentralTrimmerBundle, Scaling, TrimmedAxis
from jge.buttons.double_click_toggle import DoubleClickToggle
from jge.buttons.chain import Chain
from jge.buttons.macro import MacroEntries, Macro
from jge.buttons.tempo import Tempo

# https://whitemagic.github.io/JoystickGremlin/user_plugins/

# list the devices you need to reference in this plugin
t50j = gremlin.input_devices.JoystickDecorator(
    "RIGHT VPC Stick MT-50", "{557F56C0-FDE9-11EE-8005-444553540000}", "Default"
)

t50t = gremlin.input_devices.JoystickDecorator(
    "LEFT VPC Throttle MT-50CM2", "{2F0AFA80-FDE9-11EE-8003-444553540000}", "Default"
)

# test simply pressing a vjoy button with my VjoyButton wrapper ----------------
vjoy_button_1 = VjoyButton(1, 1)


@t50t.button(16)  # mic-z
def press_btn(event):
    if event.is_pressed:
        # log in JG like this. the messages show up in joystick gremlin -> tools
        # -> log display -> user tab
        gremlin.util.log("joystick button 1 pressed")
        vjoy_button_1.press()
    else:
        gremlin.util.log("joystick button 1 released")
        vjoy_button_1.release()
        paddle_double_click.release()


# test simply setting a vjoy axis's value with my VjoyAxis wrapper -------------
vjoy_axis_3 = VjoyAxis(1, 1)


@t50t.axis(6)  # base lever
def set_axis(event):
    gremlin.util.log(f"joystick axis 3: {event.value}")
    vjoy_axis_3.set_val(event.value)


# test double click toggle -----------------------------------------------------
paddle_double_click = DoubleClickToggle(1, 0.200)


@t50t.button(4)  # uncage pinky button
def double_click(event):
    if event.is_pressed:
        paddle_double_click.press()
    else:
        paddle_double_click.release()


# test axis button -------------------------------------------------------------
axis_button = AxisButton(0.25)


@t50t.axis(1)  # from slew x-axis
def slew_moved(event, vjoy):
    axis_button.update(event.value)
    state = axis_button.get_state()

    # press a couple vjoy buttons for this example, though you can use the axis
    # button's state to trigger anything you'd like
    if state == AxisButton.State.PressedHigh:
        vjoy[1].button(1).is_pressed = True
    elif state == AxisButton.State.PressedLow:
        vjoy[1].button(2).is_pressed = True
    elif state == AxisButton.State.Released:
        vjoy[1].button(1).is_pressed = False
        vjoy[1].button(2).is_pressed = False


# test stepper axis ------------------------------------------------------------
wingspan_stepper_vals = StepperVals.FromSpecificVals([33, 41, 53, 59, 74], (30, 120))
wingspan_stepper = StepperAxis(1, wingspan_stepper_vals, 0)


@t50t.button(14)  # thumb rotary
def inc_wingspan(event):
    if event.is_pressed:
        wingspan_stepper.next_index()


@t50t.button(15)  # thumb rotary
def dec_wingspan(event):
    if event.is_pressed:
        wingspan_stepper.prev_index()


# test toggle axis -------------------------------------------------------------
rwr_vol = ToggleAxis(2, 0)


@t50t.button(54)  # base encoder (E2)
def inc_rwr(event):
    if event.is_pressed:
        rwr_vol.step_axis(0.1)


@t50t.button(55)  # base encoder (E2)
def dec_rwr(event):
    if event.is_pressed:
        rwr_vol.step_axis(-0.1)


@t50t.button(53)  # base encoder (E2) push
def toggle_rwr(event):
    if event.is_pressed:
        rwr_vol.toggle_to(-0.9)


# test relative axis -----------------------------------------------------------
rel_ax_easing = EasingGenerator.ConstantTime(SmoothStart(2), 2, 20)
range_axis = RelativeAxis(3, rel_ax_easing)


@t50j.button(4)  # bottom thumb hat forward
def range_inc(event):
    if event.is_pressed:
        range_axis.press(1)
    else:
        range_axis.release()


@t50j.button(5)  # bottom thumb hat aft
def range_dec(event):
    if event.is_pressed:
        range_axis.press(-1)
    else:
        range_axis.release()


# test LUT axis ----------------------------------------------------------------
lut = LookupTable.FromPoints(
    [
        # flat spot right of center
        (0.01, 0.05),
        (0.5, 0.05),
        (1, 1),
    ],
    make_symmetrical=True,
)
lut_axis = LutAxis(2, lut)


@t50t.axis(2)  # slew y
def slew_axis(event):
    lut_axis.set(event.value)


# test tuned axis --------------------------------------------------------------
tuned_axis = TunedAxis(5, AxisTuning(0.5))


@t50t.axis(5)  # right throttle
def right_throttle_moved(event):
    tuned_axis.set(event.value)


slider_axis = TunedAxis(4, AxisTuning(-0.5), is_slider=True)


@t50t.axis(4)  # left throttle
def left_throttle_moved(event):
    slider_axis.set(event.value)


# test trim axis ---------------------------------------------------------------
tuning = AxisTuning(0.5)
trim_eg_ct = EasingGenerator.ConstantTime(SmoothStep(2, 2), 1, 20)
trim_eg_cr = EasingGenerator.ConstantRate(SmoothStep(2, 2), 0.5, 20)
hat_eg_ct = EasingGenerator.ConstantTime(SmoothStart(2), 1, 20, 0.05)

x_trimmed_axis = TrimmedAxis(
    TunedAxis(6, tuning), smooth_trim_easing=trim_eg_ct, trim_hat_easing=hat_eg_ct
)

y_trimmed_axis = TrimmedAxis(
    TunedAxis(7, tuning), smooth_trim_easing=trim_eg_ct, trim_hat_easing=hat_eg_ct
)

central_trim_bundle = CentralTrimmerBundle(
    [x_trimmed_axis, y_trimmed_axis], [0.05, 0.05]
)


@t50j.button(18)  # pinky button
def trim(event, joy):
    if event.is_pressed:
        if joy[t50j.device_guid].button(19).is_pressed:
            # instantly reset trim if my paddle is pulled
            x_trimmed_axis.set_trim(0)
            y_trimmed_axis.set_trim(0)
            # (though you could use any other method of applying trim (central,
            # timed, or smooth))
        else:
            # apply trim using one of these methods

            # central trimming mode

            # doing it this way makes the axes independent
            # x_trimmed_axis.trim_central()
            # y_trimmed_axis.trim_central()

            # to get central trim behavior where both axes must be centered,
            # you'll have to use a bundle!
            central_trim_bundle.trim_central()

            # timed mode
            # x_trimmed_axis.trim_timed()
            # y_trimmed_axis.trim_timed()

            # smooth mode
            # x_trimmed_axis.trim_smooth()
            # y_trimmed_axis.trim_smooth()


# handling axis input


@t50j.axis(1)
def roll_moved(event):
    x_trimmed_axis.set_vjoy(event.value, Scaling.Dynamic)


@t50j.axis(2)
def pitch_moved(event):
    y_trimmed_axis.set_vjoy(event.value, Scaling.Dynamic)


# using a trim HAT


@t50j.button(9)  # trim up
def trim_up(event):
    if event.is_pressed:
        y_trimmed_axis.press_trim_hat(1)
    else:
        y_trimmed_axis.release_trim_hat()


@t50j.button(11)  # trim up
def trim_dn(event):
    if event.is_pressed:
        y_trimmed_axis.press_trim_hat(-1)
    else:
        y_trimmed_axis.release_trim_hat()


@t50j.button(10)  # trim up
def trim_right(event):
    if event.is_pressed:
        x_trimmed_axis.press_trim_hat(1)
    else:
        x_trimmed_axis.release_trim_hat()


@t50j.button(12)  # trim up
def trim_left(event):
    if event.is_pressed:
        x_trimmed_axis.press_trim_hat(-1)
    else:
        x_trimmed_axis.release_trim_hat()


# test macros ------------------------------------------------------------------

entries1 = MacroEntries.FromShorthand([1, 2, 3, 4, 5, 1.0, 6, 7, 8, 9, 10])
macro1 = Macro(entries1, True)


@t50t.button(85)  # B1
def b1(event):
    if event.is_pressed:
        macro1.press()
    else:
        macro1.release()


entries2 = MacroEntries.FromShorthand(["a", "b", "c"])
macro2 = Macro(entries2, False)


@t50t.button(86)  # B2
def b2(event):
    if event.is_pressed:
        macro2.press()
    else:
        macro2.release()


# test chain -------------------------------------------------------------------

macro3 = Macro(MacroEntries.FromShorthand([1, 2, 3, 4]))
macro4 = Macro(MacroEntries.FromShorthand([11, 12, 13, 14]))

chain = Chain([macro3, macro4])


@t50t.button(87)  # B3
def b3(event):
    if event.is_pressed:
        chain.run_next()


# test tempo -------------------------------------------------------------------

tempo = Tempo(macro3, macro4, 0.5)


@t50t.button(88)  # B4
def b4(event):
    if event.is_pressed:
        tempo.press()
    else:
        tempo.release()
