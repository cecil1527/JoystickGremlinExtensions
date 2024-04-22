from gremlin_interface import VjoyAxis
from utils import LookupTable

class LutAxis:
    def __init__(self, axis_id: int, lut: LookupTable, device_id: int = 1) -> None:
        """
        A simple axis that uses a lookup table to linearly interpolate output
        values.

        Args:
            * axis_id (int): vjoy axis ID
            * lut (LookupTable): lookup table to use
            * device_id (int, optional): vjoy device ID. Defaults to 1.
        
        Examples:
        
        * a throttle axis where you want a little flat spot at full MIL
        
        * a slew axis where you want a flat spot on either side of center (so
          you can easily hit the slowest cursor speed)
        
        * if you want to quickly jump out of the F-16's built-in deadzone, and
          then have the axis be linear (or add more points to emulate a curve)
          from there on out
        """        
        self._axis = VjoyAxis(axis_id, device_id)
        self._lut = lut
    
    def set(self, input: float) -> None:
        '''calculates output and sets vjoy axis's value'''
        output = self._lut.output(input)
        self._axis.set_val(output)