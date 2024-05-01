import jge.utils as utils
from jge.gremlin_interface import VjoyAxis


class StepperVals:
    '''
    A namespace to contain helper functions for making vjoy axis vals in various
    ways
    '''

    @staticmethod
    def FromSpecificVals(specific_vals,  val_range,  axis_range = (-1.0, 1.0)):
        """
        maps specific_vals in val_range to axis_range. 
        
        Args:
            * specific_vals (List[float]): list of specific values you want to
              step through
            * val_range (Tuple[float, float]): range of actual values this axis
              will control
            * axis_range (Tuple[float, float], optional): range of vjoy axis.
              Defaults to (-1.0, 1.0).

        Returns:
            List[float]: vjoy axis values to be used with stepper axis
        
        Example: specific_vals are engine RPMs (2400, 2700, 3000), and engine
        RPM val_range goes from 1000 to 3000, this function will generate the
        vjoy axis values required to visit those specific engine RPMs.
        """    


        vals = [utils.lerp(val_range[0], axis_range[0], 
                           val_range[1], axis_range[1], v) for v in specific_vals]
        return vals

    @staticmethod
    def FromRange(num_vals: int, val_range, axis_range = (-1.0, 1.0), 
                   curvature: float = 0):
        """
        maps values in val_range to axis_range, with curvature applied.

        Args:
            * num_vals (int): number of values you want
            * val_range (Tuple[float, float]): range of actual values this axis
              will control
            * axis_range (Tuple[float, float], optional): range of vjoy axis.
              Defaults to (-1.0, 1.0).
            * curvature (float, optional): curvature to apply to the values.
              Defaults to 0.

        Returns:
            List[float]: vjoy axis values to be used with stepper axis
        
        Example: you want to control a radar antenna with 2 buttons (maybe a
        rotary encoder). num_vals should probably be odd, so you'll have a
        middle value. val_range will be -1 to 1 (for full axis range), but maybe
        you want a heavy curvature of 50% (0.5), so you can fine tune the
        antenna when it's looking forward, and have it pan more quickly as it
        reaches its limits.
        """

        step = (val_range[1] - val_range[0]) / (num_vals - 1)
        # these are the vals we want to map over the axis range
        vals = [val_range[0] + step * i for i in range(0, num_vals)]
        # the vals mapped over the axis range
        vals = [utils.lerp(val_range[0], axis_range[0], 
                           val_range[1], axis_range[1], v) for v in vals]
        # the vals after curvature is applied
        vals = [utils.sigmoid(v, curvature) for v in vals]
        return vals


class StepperAxis:
    
    def __init__(self, axis_id: int, axis_vals, initial_idx: int = None, 
                 device_id: int = 1) -> None:
        """
        The StepperAxis steps through a list of axis values, setting the vjoy
        axis to those values. Use StepperVals class to help make axis_vals list.

        Args:
            * axis_id (int): vjoy axis ID
            * axis_vals (List[float]): vjoy axis vals (use helper functions
              above to make lists of vals)
            * initial_idx (int, optional): _description_. Defaults to None.
            * device_id (int, optional): _description_. Defaults to 1.

        Example: A WW2 gyro gunsight has a wingspan selection between 30 and
        120ft. You'd like to step through at values of: [33, 41, 53, 59, 74],
        which correspond to the wingspans of Bf-109/Fw-190, Me-262, Bf-110,
        Ju-88, He-111. Using a stepper axis lets you select the vjoy axis values
        that correspond to these wingspans.

        You can do similar things for prop pitch, engine RPM, antenna elevation,
        etc.
        """

        self._axis = VjoyAxis(axis_id, device_id)
        self._vals = axis_vals
        
        self._idx = 0
        # use middle if one wasn't provided
        i = len(self._vals) // 2 if initial_idx is None else initial_idx
        self.go_to_index(i)

    def go_to_index(self, idx: int) -> None:
        '''go to index. sets corresponding vjoy value. clamps to remain in
        bounds'''
        self._idx = utils.clamp(idx, 0, len(self._vals) - 1)
        self._axis.set_val(self._vals[self._idx])

    def go_to_max_index(self):
        '''go to max index and set vjoy axis'''
        self.go_to_index(len(self._vals) - 1)

    def go_to_min_index(self):
        '''go to min index and set vjoy axis'''
        self.go_to_index(0)

    def next_index(self):
        '''go to next index and set vjoy axis'''
        self.go_to_index(self._idx + 1)

    def prev_index(self):
        '''go to prev index and set vjoy axis'''
        self.go_to_index(self._idx - 1)

    def next_value(self):
        '''uses the vjoy axis's current value to increment to the next value
        (instead of using our internal index). this is useful if you've moved
        the axis by some other means (like using a relative axis)'''
        self.go_to_index(utils.binary_ceil_excl(self._vals, self._axis.get_val()))

    def prev_value(self):
        '''uses the vjoy axis's current value to decrement to the prev value'''
        self.go_to_index(utils.binary_floor_excl(self._vals, self._axis.get_val()))

    def toggle_default_idx(self, default_idx: int, other_idx: int, 
                           epsilon: float = 1e-3):
        """
        goes to default_idx, unless it's already there, at which point it
        selects other_idx

        Args:
            * default_idx (int): default value's index 
            * other_idx (int): other value's index
            * epsilon (float): allowable floating point error for determining
              distance between points
        
        Example: I had an idea for emulating "BMS style" zoom, where the game
        has a FOV range of 20-140° and you want to step through FOVs in 20°
        increments, but you'd like to have a button that can take you back to a
        default of 80°, unless you're already there, at which point you'd like
        it to toggle zoom and go to 20° instead.
        """

        # NOTE we'll use the axis's actual value in case the user moved the axis
        # through another means (like using a RelativeAxis)

        current_val = self._axis.get_val()
        default_val = self._vals[default_idx]
        if abs(current_val - default_val) < epsilon:
            # we're close enough to default, so go to other idx
            self.go_to_index(other_idx)
        else:
            self.go_to_index(default_idx)


if __name__ == "__main__":
    print(StepperVals.FromSpecificVals([2400, 2700, 3000], (1000, 3000)))
    print(StepperVals.FromRange(31, (0, 1000), curvature=0.5))