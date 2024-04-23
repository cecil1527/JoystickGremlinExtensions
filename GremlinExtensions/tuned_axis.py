import utils
from gremlin_interface import VjoyAxis
from utils import Vec2


class AxisTuning:
    def __init__(self, curvature: float, 
                 invert: bool = False, 
                 deadzone_pt = (0, 0), 
                 saturation_pt = (1, 1), 
                 ) -> None:
        """
        holds tuning values for an axis

        Args:
            * curvature (float) [-1, 1]: curvature to apply to the response
              curve. NOTE this is a different sigmoid function than what DCS
              uses! curvature values will have to be higher here to get a
              similar effect.
            * invert (bool, optional): whether axis is inverted or not. Defaults
              to False.
            * deadzone_pt (tuple, optional): point where the deadzone stops.
              Defaults to (0, 0).
            * saturation_pt (tuple, optional): point where saturation begins.
              Defaults to (1, 1).
        """        
        self.curvature = curvature
        self.inverted_coef = -1 if invert else 1
        self.deadzone_pt = Vec2.From(deadzone_pt)
        self.saturation_pt = Vec2.From(saturation_pt)
        
        self.origin_pt = Vec2(0, 0)
        self.max_pt = Vec2(1, 1)
        if self.saturation_pt.x < 0:
            self.max_pt *= -1

    def conjugate(self):
        '''returns another AxisTuning instance, but with opposite signs on points'''
        invert = False if self.inverted_coef == 1 else True
        return AxisTuning(self.curvature, invert, 
                          self.deadzone_pt * -1, self.saturation_pt * -1)

    def _transform_input(self, x: float) -> float:
        '''apply transformation to input to calculate output'''
        if utils.is_between(x, self.origin_pt.x, self.deadzone_pt.x):
            # lerp between origin and deadzone end point
            p = Vec2.LerpX(self.origin_pt, self.deadzone_pt, x)
            y = p.y
        
        elif utils.is_between(x, self.deadzone_pt.x, self.saturation_pt.x):
            # do middle curved section
            norm_x = utils.normalize(x, self.deadzone_pt.x, self.saturation_pt.x)
            norm_y = utils.sigmoid(norm_x, self.curvature)
            y = utils.unnormalize(norm_y, self.deadzone_pt.y, self.saturation_pt.y)
        
        else:
            # lerp between saturation point and max
            p = Vec2.LerpX(self.saturation_pt, self.max_pt, x)
            y = p.y
        
        y *= self.inverted_coef
        return y


class TunedAxis:
    def __init__(self, axis_id: int, left_tuning: AxisTuning, right_tuning: AxisTuning, 
                 device_id: int = 1) -> None:
        """
        applies tuning to axis input vals to generate output vals
        
        it's recommended to make right tuning first, then call
        right_tuning.conjugate() to get the opposing side. this is because +/-
        signs matter for the deadzone point and saturation point.

        NOTE there's a separate standalone python script to display a UI with
        graphs to show how it all works, since it can be hard to visualize.

        Args:
            * axis_id (int): vjoy axis ID 
            * left_tuning (AxisTuning): independent left tuning 
            * right_tuning (AxisTuning): independent right tuning 
            * device_id (int, optional): vjoy device ID. Defaults to 1.
        """
        
        self._left_tuning = left_tuning
        self._right_tuning = right_tuning
        self._axis = VjoyAxis(axis_id, device_id)

    def calc_output(self, input_val: float) -> float:
        '''apply transformation to input and calculate output'''
        if input_val < 0:
            return self._left_tuning._transform_input(input_val)
        else:
            return self._right_tuning._transform_input(input_val)

    def set(self, input_val: float) -> None:
        '''calculate output and set vjoy axis's value to it'''
        self._axis.set_val(self.calc_output(input_val))


class SliderAxis:
    def __init__(self, axis_id: int, tuning: AxisTuning, device_id: int = 1) -> None:
        """
        this is similar to a tuned axis except it normalizes the input value to
        the range [0, 1]. this has the effect of using a single tuning for the
        entire physical axis's range, which is most useful for sliders or
        throttles, hence the name.

        Args:
            * axis_id (int): vjoy axis ID
            * tuning (AxisTuning): axis tuning to be applied
            * device_id (int, optional): vjoy device ID. Defaults to 1.
        """
        
        self._tuning = tuning
        self._axis = VjoyAxis(axis_id, device_id)

    def calc_output(self, input_val: float) -> float:
        '''apply transformation to input to calculate output'''
        
        input_val = utils.normalize(input_val, -1, 1)
        return self._tuning._transform_input(input_val)

    def set(self, input_val: float) -> None:
        '''calculate and set output'''
        self._axis.set_val(self.calc_output(input_val))


if __name__ == "__main__":
    r_tuning = AxisTuning(-0.5, deadzone_pt=(0.01, 0.1), saturation_pt=(0.9, 1))
    l_tuning = r_tuning.conjugate()
    
    tuned_axis = TunedAxis(1, l_tuning, r_tuning)
    xs = [i / 100.0 for i in range(-100, 101, 1)]
    ys = [tuned_axis.calc_output(x) for x in xs]
    print("\ntuned axis")
    for x, y in zip(xs, ys):
        print(f"{x},{y}")

    slider_axis = SliderAxis(1, r_tuning)
    ys = [slider_axis.calc_output(x) for x in xs]
    print("\nslider axis")
    for x, y in zip(xs, ys):
        print(f"{x},{y}")