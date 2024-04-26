# put this file in `c:/users/<name>/joystick gremlin`, which is JG's default
# profile save location. you should see a config.json and other JG files already
# in there.

import sys

def insert_if_not_present(path: str) -> None:
    if path not in sys.path:
        sys.path.insert(0, path)

# add these locations to sys.path so we can freely import python modules from them
insert_if_not_present("D:/Stuff/@Flight Sim Stuff/@Cockpit/Joystick Gremlin/GremlinExtensions")
insert_if_not_present("D:/Stuff/@Flight Sim Stuff/@Cockpit/Joystick Gremlin/Plugins")
# now we can do `import imports` at the top of any JG user plugin we write, and
# will be able to import python modules from these locations

# NOTE this works because the default profile save location (the spot you should
# put this file) is already part of JG's environment's sys.path, which we can
# use to insert more of our own paths before the rest of the user plugins run,
# where they'll try importing GremlinExtensions modules
