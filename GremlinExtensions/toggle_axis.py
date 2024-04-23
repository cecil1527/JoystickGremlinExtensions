from gremlin_interface import VjoyAxis
import utils


class ToggleAxis:

    def __init__(self, axis_id: int, initial_val: float = 0, 
                 axis_range = (-1.0, 1.0), device_id: int = 1) -> None:
        """
        an axis that can toggle between some value and its previous value

        Args:
            * axis_id (int): vjoy axis ID
            * initial_val (float, optional): initial vjoy axis value. Defaults
              to 0.
            * axis_range (Tuple[float, float], optional): vjoy axis range.
              Defaults to (-1.0, 1.0).
            * device_id (int, optional): vjoy device ID. Defaults to 1.
        
        Example: a volume axis (for radios or RWR) controlled by a throttle base
        encoder. rotating the encoded can inc/dec the volume, while pressing it
        can toggle between some low volume (or muted) and its previous value.
        """        
        
        self._axis = VjoyAxis(axis_id, device_id)
        self._axis_range = axis_range

        self._old_val = 0

        self._axis.set_val(initial_val)

    def step_axis(self, step: float) -> None:
        '''steps axis val, catching OOB values'''
        
        current_val = self._axis.get_val()
        new_val = utils.clamp(current_val + step, 
                              self._axis_range[0], self._axis_range[1])
        self._axis.set_val(new_val)

    def toggle_to(self, val) -> None:
        '''toggle to val, unless it's already there, in which case it'll toggle
        back to its old val'''

        epsilon = 1E-4
        current_val = self._axis.get_val()
        if abs(current_val - val) < epsilon:
            # we're already toggled, so go back
            self._axis.set_val(self._old_val)
        else:
            # we need to toggle, so store current axis val, and go to toggle val
            self._old_val = self._axis.get_val()
            self._axis.set_val(val)
