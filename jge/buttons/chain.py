class Chain:
    def __init__(self, list_of_callables):
        """
        a chain is a list of callables, where repeated button presses run each
        callable. this continues until the end is reached, at which point the
        chain resets back to its beginning.

        Args:
            list_of_callables:
        """

        self._callables = list_of_callables
        self._index = -1

    def __call__(self) -> None:
        self.run_next()

    def reset(self):
        """resets the chain to the beginning"""
        self._index = 0

    def _get_circular_index(self, idx: int) -> int:
        """
        returns an index that's definitely in bounds.

        this will always return between [0, max_idx], looping around if it has
        to
        """

        max_idx = len(self._callables) - 1

        # loop the index around
        if idx < 0:
            return max_idx
        elif idx > max_idx:
            return 0
        else:
            return idx

    def _set_index(self, idx: int) -> None:
        self._index = self._get_circular_index(idx)

    def _inc_and_run(self, increment: int):
        # check if the callable is still running. this safeguards against
        # calling a bunch of macros at the same time if you mash the chain
        # button, for example.
        if self._callables[self._index].is_running():
            return

        # else increment index and run callable
        self._set_index(self._index + increment)
        callable = self._callables[self._index]
        callable()

    def run_prev(self):
        """run previous chain callable"""
        self._inc_and_run(-1)

    def run_next(self):
        """run next chain callable"""
        self._inc_and_run(1)
