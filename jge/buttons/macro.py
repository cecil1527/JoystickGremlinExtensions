import threading
import time

from jge.gremlin_interface import KeyboardKey, VjoyButton


DEFAULT_WAIT_S = 0.050


def _is_proper_entry(entry) -> bool:
    """returns if the entry is an instance of a macro entry class type"""
    return (
        isinstance(entry, Wait) or isinstance(entry, Button) or isinstance(entry, Key)
    )


def _insert_waits(callables, wait_time_s):
    """
    * ensures that waits exist between all other entries. if a wait doesn't
      exist, then it gets inserted.
    * the sequence is guaranteed to end in a wait as well
    """

    i = 0
    while i < len(callables) - 1:
        i += 1

        entry = callables[i - 1]
        if isinstance(entry, Wait):
            continue

        wait = callables[i]
        if not isinstance(wait, Wait):
            callables.insert(i, Wait(wait_time_s))

    # always make sure a wait is at the end? i guess it only matters if the
    # macro will repeat
    if not isinstance(callables[-1], Wait):
        callables.append(Wait(wait_time_s))


class Wait:
    def __init__(self, time_s: float) -> None:
        """
        waits cause the macro to sleep for the specified duration

        Args:
            time_s (float): how long to sleep for in seconds
        """
        self._time_s = time_s

    def __call__(self) -> None:
        time.sleep(self._time_s)

    def __str__(self) -> str:
        return f"Wait: {self._time_s}"


class Button:
    def __init__(self, id: int, value: bool, device_id: int = 1) -> None:
        """
        a bundle of a vjoy button and the value to set it to

        Args:
            * id (int): the vjoy button ID
            * value (bool): the value to set the button to
            * device_id (int, optional): the vjoy device ID. Defaults to 1.
        """

        self._button = VjoyButton(id, device_id)
        self._value = value

        # NOTE these are only for debugging
        self._id = id
        self._device_id = device_id

    def __call__(self) -> None:
        self._button.set_pressed(self._value)

    def __str__(self) -> str:
        return f"Button: {self._id} {self._value} (device: {self._device_id})"


class Key:
    def __init__(self, key: str, value: bool) -> None:
        """
        a bundle of a keyboard key and the value to set it to

        Args:
            * key (str): a char/string representation of the keyboard key
            * value (bool): the value to set the keyboard key to
        """
        self._key = KeyboardKey(key)
        self._value = value

    def __call__(self) -> None:
        self._key.set_pressed(self._value)

    def __str__(self) -> str:
        return f"Key: {self._key._key} {self._value}"


class MacroEntries:
    """a namespace for macro entry helper functions"""

    @staticmethod
    def FromShorthand(
        shorthand_list,
        insert_waits: bool = True,
        wait_time_s: float = DEFAULT_WAIT_S,
        device_id: int = 1,
    ):
        """
        a helper function to make a list of macro entries using shorthand. the
        available shorthand is as follows:

        * Wait = single float
        * vJoy Button press/release = single int
        * vJoy Set button value = tuple of (int, bool)
        * Keyboard key = char/string (like "a" or "f10") or modifier + char
          string (like "leftcontrol + c").

          for all non-character key names, look at the bottom of this file:
          https://github.com/WhiteMagic/JoystickGremlin/blob/r13/gremlin/macro.py#L923

        * and finally any specific macro entry passed in will be taken at face
          value

        Args:
            * shorthand_list:
            * insert_waits (bool, optional): whether to automatically insert
              waits between each generated macro entry. Defaults to True.
            * wait_time_s (float, optional): how long the waits should be.
              Defaults to DEFAULT_WAIT_S.
            * device_id (int, optional): vjoy device ID (for vjoy button
              presses). Defaults to 1.
        """

        callables = []

        for entry in shorthand_list:
            if _is_proper_entry(entry):
                # take proper instances of macro entry types
                callables.append(entry)

            # else check for shorthands

            elif isinstance(entry, float):
                # floats are wait times
                callables.append(Wait(entry))

            elif isinstance(entry, int):
                # ints are press/release of a vjoy button id
                callables.append(Button(entry, True, device_id))
                callables.append(Button(entry, False, device_id))

            elif isinstance(entry, tuple):
                # tuples are (vjoy button id, value)
                callables.append(Button(entry[0], entry[1], device_id))

            elif isinstance(entry, str):
                # strings are keyboard keys
                if "+" in entry:
                    # we have a keyboard press with modifiers (ex: "leftshift + a")

                    # append list of modifiers and button
                    keys = entry.split("+")
                    # append presses on the way forward
                    for key in keys:
                        callables.append(Key(key, True))
                    # and releases on the way back
                    for key in reversed(keys):
                        callables.append(Key(key, False))
                else:
                    # we have an individual key, so do a simple press/release
                    callables.append(Key(entry, True))
                    callables.append(Key(entry, False))

        if insert_waits:
            _insert_waits(callables, wait_time_s)

        return callables


class Macro:
    def __init__(self, callables, repeat: bool = False):
        """
        a macro is a list of callables that get called in rapid succession.

        Args:
            * callables: list of callables for the macro to execute
            * repeat (bool, optional): whether or not the macro should repeat if
              the button is still held upon completion. Defaults to False.
        """

        self._callables = callables
        self._repeat = repeat

        self._thread = threading.Thread()
        self._pressed = False

    def __call__(self):
        self.press()
        self.release()

    def __run_async(self):
        while True:
            for entry in self._callables:
                entry()

            if not (self._pressed and self._repeat):
                break
            # else repeat the macro again

    def is_running(self):
        """returns if the macro is currently running"""
        return self._thread.is_alive()

    def press(self):
        self._pressed = True

        # don't run multiple times at once!
        if self.is_running():
            return

        self._thread = threading.Thread(target=self.__run_async)
        self._thread.start()

    def release(self):
        self._pressed = False


if __name__ == "__main__":
    macro_entries = MacroEntries.FromShorthand(
        [
            1,
            2,
            3,
            0.123,
            4,
            0.250,
            6,
            (7, True),
            (8, True),
            "b",
            "t",
            "leftcontrol + v",
        ],
        wait_time_s=0.555,
        device_id=3,
    )
    for e in macro_entries:
        print(e)

    macro = Macro(macro_entries, True)

    entries = MacroEntries.FromShorthand([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    macro1 = Macro(entries, True)
    print("running macro")
    macro1.press()
    macro1.release()
