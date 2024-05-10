import threading
import time
from enum import Enum

from jge import utils
from jge.axes.tuned_axis import TunedAxis, AxisTuning
from jge.easing_functions import EasingGenerator


class Scaling(Enum):
    """type of scaling you want done"""

    Nil = 1  # no scaling (coef of 1)
    Static = 2  # static scaling coef. does not change with controller pos
    Dynamic = 3  # dynamic scaling coef. changes with controller pos


class TrimmedAxis:
    def __init__(
        self,
        tuned_axis: TunedAxis,
        clamp_output: bool = False,
        dyn_scaling_degree: float = 2,
        dyn_scaling_delay: float = 0.2,
        smooth_trim_easing: EasingGenerator = None,
        trim_hat_easing: EasingGenerator = None,
    ):
        """
        this class was primarily created to address the shortcomings of
        helicopter trim using a conventional joystick (non-FFB joystick).

        there is a UI to display graphs to show how it all works, since it's
        hard to visualize.

        Args:
            * tuned_axis (TunedAxis): tuned axis to use.
            * clamp_output (bool, optional): clamps output to stay below tuned
              axis's y saturation. Defaults to False.
            * dyn_scaling_degree (float, optional): dynamic scaling coef
              blending is done using a polynomial of this degree. Defaults to 2.
            * dyn_scaling_delay (float, optional): the physical controller range
              to delay dynamic coef scaling. Defaults to 0.2.
            * smooth_trim_easing (EasingGenerator): easing generator that will
              be used when calling trim_smooth(). Defaults to None.
            * trim_hat_easing (EasingGenerator): easing generator that will be
              used with trim hat. Defaults to None.

        Further explanation:

        1. clamp output: i'm not exactly sure what the desired behavior should
           be when trimming with saturation points. the problem is if you
           specify a y-saturation, then you're saying you don't want the vjoy
           axis to ever go above 0.8 (for example). but when you trim, you will
           definitely be able to hit more than 0.8 on the "close" side. so if
           you don't want that to happen, set clamp output to true.

        1. the dynamic scaling degree and delay only affect dynamic scaling, so
           if you use static scaling, these parameters have no effect.

        1. a dynamic scaling delay of 0.2 means that no dynamic scaling will
           take place for 20% stick forward and 20% stick aft (or left/right),
           which means it should feel *exactly* like it used to when in that
           range. once you exceed that range, scaling will be ramped on however
           heavily is required to reach full in-game axis input with full stick
           deflection.

        1. easing generators are only required if you plan on using smooth trim
           or the trim hat. if you're not going to use them, the generators can
           stay None
        """

        self._tuned_axis = tuned_axis
        self._tuned_axis._left_tuning = self._tuned_axis._right_tuning
        # TODO i'm only going to support symmetrically tuned axes for now
        self._clamp_output = clamp_output

        self._dyn_scaling_degree = utils.clamp(dyn_scaling_degree, 0, 10)
        self._dyn_scaling_delay = utils.clamp(dyn_scaling_delay, 0, 1)

        if smooth_trim_easing:
            self._smooth_trim_easing = smooth_trim_easing.copy()
        if trim_hat_easing:
            self._trim_hat_easing = trim_hat_easing.copy()

        self._trim_offset = 0
        self._max_scaling_coef = 0
        self.set_trim(0)

        # vals for internal bookkeeping
        self._prev_raw_input = 0
        self._prev_scaling = Scaling.Dynamic
        self._output_blocked = False
        self._is_hat_pressed = False

    def set_trim(self, trim: float = None) -> None:
        """
        instantly sets trim value and does some additional bookkeeping

        Args:
            trim (float, optional): if None, trim is automatically set using the
            vjoy axis's current value. Defaults to None.
        """

        if trim is None:
            # use the vjoy axis's current value
            self._trim_offset = self._tuned_axis._axis.get_val()
        else:
            self._trim_offset = trim

        self._trim_offset = utils.clamp(self._trim_offset, -1, 1)
        self._recalc_max_scaling_coef()

    def _recalc_max_scaling_coef(self):
        """recalcs max scaling coef. call this after setting trim"""

        # NOTE axes are symmetrical for now (same tuning for left and right).
        # max output is +-saturation.y and the required input to do that is
        # saturation.x
        y_sat = self._tuned_axis._right_tuning.saturation_pt.y

        # the max distance we'll have to go is abs(trim) + y saturation
        max_dist = abs(self._trim_offset) + y_sat

        # scaling coef is the ratio of this distance to the distance with 0 trim
        self._max_scaling_coef = max_dist / y_sat

        # NOTE if the scaling is correct, the far saturation point should not
        # move as we trim!

    def _calc_dynamic_scaling_coef(self, raw_input: float) -> float:
        """
        calculate dynamic scaling coef based on input

        Args:
            input (float): raw controller input

        Returns:
            float: dynamic scaling coef
        """

        # it's easist to use abs(input) since scaling coef is always positive
        raw_input = abs(raw_input)

        # if we're below the scaling delay, return no scaling at all (coef = 1)
        if raw_input < self._dyn_scaling_delay:
            return 1

        # else calc a "dynamic" scaling coef.

        # it's easiest to deal with normalized inputs/outputs ranging from [0,
        # 1] which can be denormalized later on.

        # the normalized range over which scaling occurs
        # 1. would normally be [0, 1]
        # 2. but if we have a saturation setting, (for example where you want
        #    the axis value to max out at just 90% of stick deflection), then
        #    you'll see that after we trim, it'll take full stick deflection to
        #    hit full axis value, instead of just 90%
        # 3. so the "proper" range to use is [0, saturation.x]
        #
        # TODO this is still not quite right. the problem is idk exactly what i
        # want the desired behavior to be.

        # norm_input = utils.normalize(raw_input, self._dyn_scaling_delay, 1)
        norm_input = utils.normalize(
            raw_input,
            self._dyn_scaling_delay,
            self._tuned_axis._right_tuning.saturation_pt.x,
        )
        # NOTE norm_input will now be [0, 1]

        # apply power (norm_input is still [0, 1])
        norm_input = norm_input**self._dyn_scaling_degree
        # TODO this could actually be replaced with any smoothing function. it's
        # currently equivalent to smooth start. i don't think it makes sense to
        # use anything else though. (if changed remember to update UI graphs!)

        # use the normalized input to lerp the scaling coef
        # 1. input of 0 -> scaling coef of 1 (no scaling)
        # 2. input of 1 -> max scaling coef
        dyn_scaling_coef = utils.lerp(0, 1, 1, self._max_scaling_coef, norm_input)

        # NOTE if you adjust normalized range above by saturation.x (to get
        # desired saturation point behavior), then coef can go over max, so
        # clamp it
        dyn_scaling_coef = utils.clamp(dyn_scaling_coef, 1, self._max_scaling_coef)

        return dyn_scaling_coef

    def _get_scaling_coef(self, raw_input: float, scaling_type: Scaling) -> float:
        """return scaling coefficient based on the scaling type"""
        if scaling_type == Scaling.Nil:
            return 1
        if scaling_type == Scaling.Static:
            return self._max_scaling_coef
        if scaling_type == Scaling.Dynamic:
            return self._calc_dynamic_scaling_coef(raw_input)

    def calc_output(self, raw_input: float, scaling_type: Scaling) -> float:
        """
        calculates output based on scaling type

        Args:
            * raw_input (float) [-1, 1]: controller's raw input value.
            * scaling_type (Scaling): scaling type we want done

        Returns:
            float: output for vjoy
        """

        output = self._tuned_axis.calc_output(raw_input)
        scaling_coef = self._get_scaling_coef(raw_input, scaling_type)
        output *= scaling_coef
        output += self._trim_offset

        if self._clamp_output:
            # clamp so output can never be more than desired y saturation
            y_sat = self._tuned_axis._right_tuning.saturation_pt.y
            output = utils.clamp(output, -y_sat, y_sat)

        return output

    def set_vjoy(self, raw_input: float, scaling_type: Scaling):
        """
        calculates output based on scaling type and sets vjoy axis's value

        Args:
            * raw_input (float) [-1, 1]: controller's raw input value
            * scaling_type (Scaling): scaling type we want done
        """

        # always update prev raw input so we know when the physical stick gets
        # centered (for central pos trim mode)
        self._prev_raw_input = raw_input
        self._prev_scaling = scaling_type

        if self._output_blocked:
            return

        output = self.calc_output(raw_input, scaling_type)

        # set the axis's value directly
        self._tuned_axis._axis.set_val(output)

    def inc_trim(self, delta: float):
        """
        instantly increments trim by the specified amount
        """
        self.set_trim(self._trim_offset + delta)

    def trim_timed(self, trim: float = None, time_s: float = 0.3):
        """
        sets trim and blocks output for the duration to give you time to
        recenter your controller

        Args:
            * trim (float, optional) [-1, 1]: if None, trim is automatically set
              using the vjoy axis's current value. Defaults to None.
            * time_s (float, optional): duration to block outputs for. Defaults
              to 0.3.
        """

        # set trim and start thread to sleep
        self._output_blocked = True
        self.set_trim(trim)
        threading.Thread(target=self.__async_trim_timed, args=[time_s]).start()

    def __async_trim_timed(self, time_s: float):
        time.sleep(time_s)
        self._output_blocked = False
        self.set_vjoy(self._prev_raw_input, self._prev_scaling)

    def trim_smooth(self, trim: float = None):
        """
        smoothly sets trim over a duration to give you time to counteract the
        effects

        NOTE: requires the smooth trim easing generator to be set!

        Args:
            * trim (float, optional) [-1, 1]: if None, trim is automatically set
              using the vjoy axis's current value. Defaults to None.
        """

        threading.Thread(target=self.__async_trim_smooth, args=[trim]).start()

    def __async_trim_smooth(self, trim: float):
        if trim is None:
            trim = self._tuned_axis._axis.get_val()

        starting_trim = self._trim_offset
        trim_delta = trim - starting_trim
        sign = 1 if trim_delta >= 0 else -1
        trim_delta = abs(trim_delta)

        self._smooth_trim_easing.reset()
        self._smooth_trim_easing.set_magnitude(trim_delta)

        for _ in range(self._smooth_trim_easing.get_num_steps()):
            output = sign * self._smooth_trim_easing.get_output()
            self.set_trim(starting_trim + output)
            self.set_vjoy(self._prev_raw_input, self._prev_scaling)
            time.sleep(self._smooth_trim_easing.get_sleep_time())

    def trim_central(self, trim: float = None, center: float = 0.05):
        """
        sets trim and blocks output until the controller is returned to a
        position less than center

        Args:
            * trim (float, optional) [-1, 1]: if None, trim is automatically set
              using the vjoy axis's current value. Defaults to None.
            * center (float, optional) [0, 1]: allowable margin for considering
              the axis centered. Defaults to 0.05.
        """

        self._output_blocked = True
        self.set_trim(trim)
        threading.Thread(target=self.__async_trim_central, args=[center]).start()

    def __async_trim_central(self, center: float):
        # while output is blocked, check if we can unblock it, else sleep
        while self._output_blocked:
            if abs(self._prev_raw_input) < center:
                self._output_blocked = False
                self.set_vjoy(self._prev_raw_input, self._prev_scaling)
            else:
                time.sleep(0.020)

    def press_trim_hat(self, direction: int):
        """
        smoothly adjusts trim like a jet's trim hat would.

        NOTE this requires the trim hat easing generator to be set!

        Args:
            * direction (int): should be -1 or 1
        """

        self._is_hat_pressed = True
        threading.Thread(target=self.__async_trim_hat, args=[direction]).start()

    def release_trim_hat(self):
        self._is_hat_pressed = False

    def __async_trim_hat(self, direction: int):
        self._trim_hat_easing.reset()
        while self._is_hat_pressed:
            trim_delta = direction * self._trim_hat_easing.get_output()
            self.inc_trim(trim_delta)
            time.sleep(self._trim_hat_easing.get_sleep_time())


class CentralTrimmerBundle:
    def __init__(self, axes_list, centers_list):
        """
        this is a class made to handle a bundle of central trimmer axes since
        you'll probably want to wait until all axes are centered before
        unblocking output.

        Args:
            * axes_list (List[TrimmedAxis]): list of trim axes to include in
              this bundle
            * centers_list (List[float]): list of centers required for each axis
              to be considered centered. ALL axes have to be below their
              respective value to clear output blocking
        """

        assert len(axes_list) == len(centers_list)

        self._axes = axes_list
        self._centers = centers_list

        self._centers_need_checked = False

    def trim_central(self, trims_list=None):
        """
        sets trim and blocks output until all controllers have been centered

        Args:
            * trims_list (List[float]): list of trim values to set for each
              axis. setting this to None uses the vjoy axis's current val for
              each axis in the bundle.
        """

        if trims_list is None:
            trims_list = [None] * len(self._axes)

        self._centers_need_checked = True

        # block output and set trim on all axes
        for axis, trim in zip(self._axes, trims_list):
            axis._output_blocked = True
            axis.set_trim(trim)

        threading.Thread(target=self.__async_trim_central).start()

    def __async_trim_central(self):
        # while output is blocked, check if we can unblock it, else sleep
        while self._centers_need_checked:
            time.sleep(0.020)
            self._check_centers()

    def _check_centers(self):
        for axis, center in zip(self._axes, self._centers):
            if abs(axis._prev_raw_input) > center:
                # if just a single axis is out of tolerances, return
                return

        # else they were all within their respective center, so clear output
        # blocking on all of them
        for axis in self._axes:
            axis._output_blocked = False

        self._centers_need_checked = False


if __name__ == "__main__":
    from jge.easing_functions import SmoothStep

    tuning = AxisTuning(0.5)
    tuned_axis = TunedAxis(1, tuning)

    trimmed_axis = TrimmedAxis(
        tuned_axis,
        smooth_trim_easing=EasingGenerator.ConstantRate(SmoothStep(2, 2), 1, 20, 1),
    )

    trimmed_axis.set_vjoy(0, Scaling.Dynamic)
    trimmed_axis.inc_trim(0.1)

    trimmed_axis.set_trim(0)
    trimmed_axis.trim_smooth(0.1)
    trimmed_axis.trim_smooth(-0.2)
    trimmed_axis.trim_smooth(0.3)
    trimmed_axis.trim_smooth(-0.4)
