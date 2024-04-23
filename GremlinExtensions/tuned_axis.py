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
    def __init__(self, axis_id: int, right_tuning: AxisTuning, 
                 left_tuning: AxisTuning = None, is_slider: bool = False, 
                 device_id: int = 1) -> None:
        """
        applies tuning to axis input vals to generate transformed output vals

        Args:
            * axis_id (int): vjoy axis ID 
            * right_tuning (AxisTuning): tuning used for right side.
            * left_tuning (AxisTuning, optional): optional tuning for left side.
              if None is provided, right's conjugate is used automatically.
              Defaults to None.
            * is_slider (bool, optional): if True, then input gets normalized
              between [0, 1], and only right tuning is used. output will still
              range from [-1, 1]. Defaults to False.
            * device_id (int, optional): vjoy device ID. Defaults to 1.
        
        NOTE there's a separate standalone python script to display a UI with
        graphs to show how the transformations work, since it's hard to
        visualize.

        NOTE if you want asymmetrical tuning for left side, pay attention to the
        signs on the deadzone and saturation points! +/- signs matter. all x/y
        coords should probably be negative for the left side.
        """
        
        self._right_tuning = right_tuning
        self._left_tuning = left_tuning if left_tuning else right_tuning.conjugate()
        
        self._is_slider = is_slider
        self._axis = VjoyAxis(axis_id, device_id)

    def _calc_slider_output(self, input: float) -> float:
        '''
        will normalize input and unnormalize output to map right tuning over
        the controller's entire range
        '''
        input = utils.normalize(input, -1, 1)
        output = self._right_tuning._transform_input(input)
        output = utils.unnormalize(output, -1, 1)
        return output

    def calc_output(self, input: float) -> float:
        """
        apply transformation to input and calculate output

        Args:
            input (float) [-1, 1]: raw controller value

        Returns:
            float [-1, 1]: input transformed to output
        """

        if self._is_slider:
            return self._calc_slider_output(input)

        # else we calculate output for an axis with a center
        if input < 0:
            return self._left_tuning._transform_input(input)
        else:
            return self._right_tuning._transform_input(input)

    def set(self, input: float) -> None:
        """
        calculate output and set vjoy axis's value to it

        Args:
            input (float) [-1, 1]: raw controller value
        """        

        ''''''
        self._axis.set_val(self.calc_output(input))


if __name__ == "__main__":
    tuning = AxisTuning(-0.5, deadzone_pt=(0.01, 0.1), saturation_pt=(0.9, 1))
    
    tuned_axis = TunedAxis(1, tuning)
    xs = [i / 100.0 for i in range(-100, 101, 1)]
    ys = [tuned_axis.calc_output(x) for x in xs]
    print("\ncentered axis")
    for x, y in zip(xs, ys):
        print(f"{x},{y}")

    slider_axis = TunedAxis(1, tuning, is_slider=True)
    ys = [slider_axis.calc_output(x) for x in xs]
    print("\nslider axis")
    for x, y in zip(xs, ys):
        print(f"{x},{y}")