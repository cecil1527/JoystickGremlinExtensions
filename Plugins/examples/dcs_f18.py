from jge.utils.lut import LookupTable
from jge.axes.lut_axis import LutAxis
from jge.buttons.double_click_toggle import DoubleClickToggle
from jge.buttons.macro import MacroEntries, Macro
from jge.buttons.chain import Chain
from jge.buttons.tempo import Tempo

from Plugins.device_decorators import stick, throttle, is_paddle_pulled

# paddle toggle for G-limit override -------------------------------------------
# so you don't have to hold the paddle during a fight
paddle_toggle = DoubleClickToggle(1, 0.3)


@stick.button(17)  # thumb CMS button
def paddle(event):
    if event.is_pressed:
        paddle_toggle.press()
    else:
        paddle_toggle.release()


# toggling airbrake ------------------------------------------------------------
# since it auto retracts under high alpha or when flaps are out


@throttle.button(5)  # airbrake right
def toggle_airbrake(event, vjoy):
    if event.is_pressed:
        vjoy[1].button(5).is_pressed = not vjoy[1].button(5).is_pressed


# disable toggle if i press any of my regular airbrake buttons
@throttle.button(6)  # airbrake in
def release_airbrake1(event, vjoy):
    if event.is_pressed:
        vjoy[1].button(5).is_pressed = False


@throttle.button(7)  # airbrake out
def release_airbrake2(event, vjoy):
    if event.is_pressed:
        vjoy[1].button(5).is_pressed = False


# slow slew --------------------------------------------------------------------

# flat spot at minimum slew speed so it's easy to fine tune TGP position
#
# NOTE DCS F-18 requires a little over 1% to actually move the TGP.
min_spd = 0.011
lut = LookupTable.FromPoints(
    # do 1% deadzone, then min speed from 1%-15%, and max out at (1, 1).
    # make_symmetrical will autofill the negative values of the LUT.
    [(0.01, 0), (0.01, min_spd), (0.15, min_spd), (1, 1)],
    make_symmetrical=True,
)
x_slew = LutAxis(4, lut)
y_slew = LutAxis(5, lut)


@throttle.axis(1)
def x_slew_moved(event):
    x_slew.set(event.value)


@throttle.axis(2)
def y_slew_moved(event):
    y_slew.set(event.value)


# macros for switching MFD pages -----------------------------------------------

# L18, L17
left_rwr_macro = Macro(MacroEntries.FromShorthand([33, 34]))
# L18, L5
left_stores_macro = Macro(MacroEntries.FromShorthand([33, 35]))
# L18, L6
left_tgp_macro = Macro(MacroEntries.FromShorthand([33, 36]))
# R18, R4
right_radar_macro = Macro(MacroEntries.FromShorthand([37, 38]))
# R18, R6
right_tgp_macro = Macro(MacroEntries.FromShorthand([37, 39]))

# the first macro should be the first one you want to call (ex: the right MFD
# defaults to radar in the jet, so the first macro we want is the one to swap
# right MFD to TGP)
right_chain = Chain([right_tgp_macro, right_radar_macro])
left_chain = Chain([left_stores_macro, left_tgp_macro])

# a tempo will let me bring up RWR on left MFD using a long press. on short
# presses, the left chain will run
left_tempo = Tempo(left_chain.run_next, left_rwr_macro, delay_s=0.3)

# hat values are stored as a tuple of (x_dir, y_dir). store the old hat pos, so
# we always know where we came from.
old_hat_pos = (0, 0)


@stick.hat(1)  # TMS hat
def t50j_hat(event, joy):
    # NOTE there's no need to do check if event.is_pressed, since releasing the
    # hat will have an event.value of (0, 0)

    # i only ever want to do stuff if my paddle is pulled
    if not is_paddle_pulled(joy):
        return

    # keep track of the old hat position, so we know if we released when coming
    # from certain directions
    global old_hat_pos

    if event.value == (0, 0):  # center
        if old_hat_pos == (-1, 0):
            # release tempo if we came from left
            left_tempo.release()

    elif event.value == (-1, 0):  # left
        left_tempo.press()

    elif event.value == (1, 0):  # right
        right_chain.run_next()

    # always update old hat pos
    old_hat_pos = event.value


# reset chains if either mastermode button is pressed, since the F-18 always
# resets the MFDs to default when you swap mastermodes.
@stick.button(6)  # mastermode forward
def t50j_b6(event):
    if event.is_pressed:
        left_chain.reset()
        right_chain.reset()


@stick.button(7)  # mastermode aft
def t50j_b7(event):
    if event.is_pressed:
        left_chain.reset()
        right_chain.reset()
