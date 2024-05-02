from jge.axes.tuned_axis import AxisTuning, TunedAxis
from jge.axes.stepper_axis import StepperVals, StepperAxis

from Plugins.device_decorators import stick, throttle, is_paddle_pulled


# handle axes ------------------------------------------------------------------

# NOTE
# 1. DCS F-16 has horrible built-in deadzones, so use a tuned axis to get out of
#    it
# 2. also autopilot won't work correctly at that point, due to a small physical
#    stick deflection inputting quite a lot in game, so have the option to
#    disable the axes.

# i find the jet has a bit of a built in curve on roll too, so attempt to
# neutralize that with an inverse curve
roll_tuning = AxisTuning(-0.2, deadzone_pt=(0.008, 0.036))
roll_axis = TunedAxis(1, roll_tuning)

pitch_tuning = AxisTuning(deadzone_pt=(0.01, 0.08))
pitch_axis = TunedAxis(2, pitch_tuning)

axes_disabled = False

# disable axes when AP switch is pressed
@throttle.button(48)  # T7 forward
def ap_fwd(event):
	if event.is_pressed:
		global axes_disabled
		axes_disabled = True

@throttle.button(49)  # T7 aft
def ap_aft(event):
	if event.is_pressed:
		global axes_disabled
		axes_disabled = True

# re-enable axes
@stick.button(17)  # CMS thumb button
def paddle_reset(event, joy):
	global axes_disabled

    # momentarily re-enable when paddle is pulled. this lets me use the jet's
    # actual paddle switch (which i mapped in game) make small adjustments to
    # autopilot
	if is_paddle_pulled(joy):
		if event.is_pressed:
			axes_disabled = False
		else:
			axes_disabled = True
	else:
		if event.is_pressed:
			axes_disabled = False

@stick.axis(1)
def roll_moved(event):
	if axes_disabled:
		roll_axis.set(0)
	else:
		roll_axis.set(event.value)

@stick.axis(2)
def pitch_moved(event):
	if axes_disabled:
		pitch_axis.set(0)
	else:
		pitch_axis.set(event.value)

# handle elevation axis and TGP zoom axis -------------------------------------- 

# do heavy curvature for elevation so it will go quite fast when looking far up
# or down for targets that are close and at an extreme altitude difference
elev_vals = StepperVals.FromRange(31, (-1.0, 1.0), curvature=0.5)
elev_axis = StepperAxis(4, elev_vals)

tgp_zoom_vals = StepperVals.FromRange(10, (-1.0, 1.0))
tgp_axis = StepperAxis(5, tgp_zoom_vals)

@throttle.button(14)  # thumb rotary encoder forward
def inc_elev(event, joy):
	if event.is_pressed:
		if is_paddle_pulled(joy):
			tgp_axis.next_index()
		else:
			elev_axis.next_index()
	
@throttle.button(15)  # thumb rotary encoder aft
def dec_elev(event, vjoy, joy):
	if event.is_pressed:
		if is_paddle_pulled(joy):
			tgp_axis.prev_index()
		else:
			elev_axis.prev_index()
