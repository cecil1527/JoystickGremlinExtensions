"""
these classes will mock the JG classes and get loaded automatically in
`gremlin_interface.py` so i can run each JG extension as a standalone python
script
"""


class MockAxis:
    def __init__(self, id: int) -> None:
        self.id = id
        self.value = 0.0


class MockButton:
    def __init__(self, id: int) -> None:
        self.id = id
        self.is_pressed = False


class MockDevice:
    def __init__(self, id) -> None:
        self.id = id

    def button(self, id) -> MockButton:
        return MockButton(id)

    def axis(self, id) -> MockButton:
        return MockAxis(id)


class MockProxy:
    def __init__(self) -> None:
        pass

    def __getitem__(self, id) -> MockDevice:
        return MockDevice(id)


def VJoyProxy():
    return MockProxy()
