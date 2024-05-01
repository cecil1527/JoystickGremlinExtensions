from enum import Enum


class AxisButton:

    class State(Enum):
        NoChange = 0
        Released = 1
        PressedLow = 2
        PressedHigh = 3

    def __init__(self, threshold: float) -> None:
        """
        handles having an axis "act like a button".

        Args:
            * threshold (float) [0, 1]: axis value over which it's considered
              "pressed"
        
        NOTE: no actual vjoy buttons get pressed because sometimes you'll want
        to use this to call another function instead
        """        

        self._threshold = threshold
        self._state = AxisButton.State.NoChange
        
        self._raw_value = 0
        self._prev_raw_value = 0

    def update(self, axis_val: float) -> None:
        """
        Args:
            * axis_val (float): continually feed in the axis's current value.
        """        

        # update raw value
        self._prev_raw_value = self._raw_value
        if self._threshold <= axis_val <= 1.0:
            self._raw_value = 1
        elif -1.0 <= axis_val <= -self._threshold:
            self._raw_value = -1
        else:
            self._raw_value = 0

        # the value we care about is from the change of the raw value
        #
        # NOTE this is because you don't want to continually press something
        # hundreds of times/sec as the axis jitters/moves if the axis is above a
        # threshold. so you can't use the raw value. you need to use whether the
        # raw value flipped or not 
        
        if self._prev_raw_value == self._raw_value:
            self._state = AxisButton.State.NoChange
            return
        
        # else the value changed
        
        if self._raw_value == 0:
            self._state = AxisButton.State.Released
        elif self._raw_value == 1:
            self._state = AxisButton.State.PressedHigh
        elif self._raw_value == -1:
            self._state = AxisButton.State.PressedLow

    def get_state(self):
        """
        check the AxisButton's state.

        Returns:
            AxisButton.State: the state tells if button was freshly pressed low,
            pressed high, released, or had no change.
        """        

        return self._state
    

if __name__ == "__main__":
    axis_button = AxisButton(0.25)

    axis_button.update(0.1)
    assert(axis_button.get_state() == AxisButton.State.NoChange)
    axis_button.update(0.2)
    assert(axis_button.get_state() == AxisButton.State.NoChange)
    axis_button.update(0.3)
    assert(axis_button.get_state() == AxisButton.State.PressedHigh)
    axis_button.update(0.4)
    assert(axis_button.get_state() == AxisButton.State.NoChange)
    axis_button.update(0.5)
    assert(axis_button.get_state() == AxisButton.State.NoChange)
    axis_button.update(0.2)
    assert(axis_button.get_state() == AxisButton.State.Released)
    axis_button.update(0)
    assert(axis_button.get_state() == AxisButton.State.NoChange)
    axis_button.update(-0.8)
    assert(axis_button.get_state() == AxisButton.State.PressedLow)
