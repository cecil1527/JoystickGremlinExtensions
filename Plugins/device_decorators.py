import gremlin

# putting all devices in a single module for easier editing of UUIDs in case
# they ever change.

stick = gremlin.input_devices.JoystickDecorator(
    "RIGHT VPC Stick MT-50",
    "{557F56C0-FDE9-11EE-8005-444553540000}",
    "Default"
)

throttle = gremlin.input_devices.JoystickDecorator(
    "LEFT VPC Throttle MT-50CM2",
    "{2F0AFA80-FDE9-11EE-8003-444553540000}",
    "Default"
)

pedals = gremlin.input_devices.JoystickDecorator(
    "MFG Crosswind V2",
    "{BAF058E0-2812-11EE-8002-444553540000}",
    "Default"
)
