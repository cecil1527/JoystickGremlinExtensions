from jge.gremlin_interface import VjoyButton


class StickyButtons:
    def __init__(self, button_ids, device_id: int = 1) -> None:
        """
        handles a group of vjoy buttons that you can have stick on, with helper
        functions to do additional things like release all buttons.

        Args:
            * button_ids (List[int]): vjoy button IDs to put into this group
            * device_id (int, optional): vjoy device ID. Defaults to 1.
        
        Example: use anytime you need buttons to stick on, and want the ability
        to easily release all buttons before turning another button on so they
        don't conflict/fight one another.
        """        

        self._buttons = {}
        for b_id in button_ids:
            self._buttons[b_id] = VjoyButton(b_id, device_id)

    def press(self, button_id: int) -> None:
        '''press the button corresponding to the ID'''
        self._buttons[button_id].press()
    
    def release(self, button_id: int) -> None:
        '''release the button corresponding to the ID'''
        self._buttons[button_id].release()

    def release_all(self) -> None:
        '''release all buttons'''
        for b in self._buttons.values():
            b.release()


if __name__ == "__main__":
    sticky_buttons = StickyButtons([1, 2, 3])
    sticky_buttons.press(1)
    sticky_buttons.release(1)
    sticky_buttons.press(1)
    sticky_buttons.press(2)
    sticky_buttons.release_all()