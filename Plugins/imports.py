# NOTE only use this file if you're saving your Plugins and jge folder to a
# nonstandard spot.
#
# if you put ypur Plugins and jge folder in `c:/users/<name>/joystick gremlin`,
# then you can ignore this file.
#
# to use: put this file in `c:/users/<name>/joystick gremlin`, which is JG's
# default profile save location. you should see a config.json and other JG files
# already in there. and put `import imports` at the top of any user plugin you
# write.
#
# NOTE this works because the default profile save location is already part of
# JG's environment's sys.path, but not much else is. we can use that fact to
# insert more of our own paths before the rest of the user plugins run. then
# they'll be able to import the Joystick Gremlin Extension modules, because
# python will know which folders to check when looking for imported modules


import sys

def insert_if_not_present(path: str) -> None:
    if path not in sys.path:
        sys.path.insert(0, path)

# add the location that contains your Plugins and jge folder to sys.path so we
# can freely import python modules from it
insert_if_not_present("D:/Stuff/@Flight Sim Stuff/@Cockpit/Joystick Gremlin/")
# now we can do `import imports` at the top of any JG user plugin we write, and
# will be able to import python modules from this location
