# What is Joystick Gremlin Extensions?
JGE is a handful of python modules meant to be used in JG user plugins. There are axis modules and button modules.

# Dependencies
At the time of writing:
1. [Joystick Gremlin v13.3](https://whitemagic.github.io/JoystickGremlin/download/)
1. [Dear PyGUI v1.11.1](https://pypi.org/project/dearpygui/)
    * This is only required if you want to run the tuned/trimmed axis UI to visualize what's going on.

# Usage
1. Put the `jge` folder next to JG's `Plugins` folder in `C:\Users\<name>\joystick gremlin`
1. Then you can either:
    1. Use a premade modular plugins found in the `Plugins` folder.
    1. Use a premade designated plugin found in `Plugins/examples` folder.
    #### Because there are 2 main ways of doing user plugins:
    1. Make little reusable ones to piece together a JG profile with a handful of small, reusable plugins.
    1. Make a designated one for a specific game/airframe, where you'd only run that particular plugin when flying DCS F-16, for example.
1. Or you can make your own plugin, using JGE modules.
    1. [If you're unfamiliar with writing your own JG user plugins, go here.](https://whitemagic.github.io/JoystickGremlin/user_plugins/)

# Axis Modules

## Tuned Axis
This is essentially DCS axis tuning, except:
1. Curvature is a different sigmoid function. 
    * I'm just not sure what DCS uses. If I ever figure it out, I'll replace the current sigmoid function so curvature values will be directly transferrable.
    * The function I use requires curvature values to be higher than DCS to get a similar curve. 
        * Example: If you're used to a curvature of 20 in DCS, it won't be 0.20 in JGE, it'll be something more like 0.45.
1. Deadzone isn't a single value, but is a point instead. I like this better because:
    * It can be used to create a deadzone.
    * It can also be used to get you out of a deadzone.
        * Example: DCS F-16 has an unfortunate built-in deadzone. The Tuned Axis makes it easy to say, "Hey, within the first 1% of my physical joystick movement, I want you to output 8% to the game (to get me out of the game's built-in deadzone), and then follow my curvature value from there on out."

There is a UI to play around with, since it can be hard to visualize the chain of transformations that will get applied. Just run `jge/ui/trimmed_axis_ui.py`

![axis tuning](https://github.com/cecil1527/JoystickGremlinExtensions/assets/4644033/79fc444d-f0c0-4a45-916c-faea66ba2f5d)

## Trimmed Axis

The primary goal of this project was to address the shortcomings of trimming a helicopter in DCS with a conventional (spring) joystick.

It's obviously not necessary to use this. You can get used to how DCS handles helicopter trim, but it's not great.

#### Some graphs to show how it works. 
* You can play with these graphs yourself by running `jge/ui/trimmed_axis_ui.py`
* The graph represents a single physical axis (so pick pitch or roll to visualize)
* Horizontal axis represents what the physical axis is doing.
* Vertical axis represents the vJoy axis's output, which is what the game will see.

#### This is the way DCS currently works. 
* Input is not scaled at all. It just gets offset by trim.
* If you trim, then you will *never* be able to hit max deflection in game in the *far* direction. 
* Worst case: if you trim full forward, even if you pull full back in real life, the game will only ever read a neutral joystick position.

![no scaling](https://github.com/cecil1527/JoystickGremlinExtensions/assets/4644033/2086de7e-f736-46f9-b590-6b67c2cebe17)

#### A simple way to fix this is with static scaling.
* Static scaling gets applied to input so that after the trim offset is applied, full real life stick deflection can still achieve full in-game deflection. 
* The problem now is that axis sensitivity has been increased. Worst case: trimming full forward means the axis will feel twice as sensitive.

![static scaling](https://github.com/cecil1527/JoystickGremlinExtensions/assets/4644033/c26f8336-9ddf-4ad6-8169-97528a02e002)

#### We can fix the problems of static scaling by *dynamically* scaling. 
* We define a region around zero input to defer static scaling. This region is customizable.
* The result is no scaling around neutral and then smoothly easing into static scaling, reaching max output by the time we hit max input.

![dynamic scaling](https://github.com/cecil1527/JoystickGremlinExtensions/assets/4644033/26dbc1ba-45f2-4fb2-a9a1-4cc03c35a3f9)

#### And here it is all at once.
* Notice how even though dynamic scaling (green line) introduces a bit of a curve, it will still feel alright, because it clings to DCS default (blue line) while you're in the deferred scaling region.
* So if you customize it just right, it should feel mostly exactly the same, because you'll spend most of your time with the stick near center (or within 20% of it for example), but you still have the option of pulling full back and being able to input full aft into the game without having to fiddle with trim in an emergency.

![all at once](https://github.com/cecil1527/JoystickGremlinExtensions/assets/4644033/d3bd1ee6-509b-441c-94ec-cfe6ffcea924)

#### And of course trim can be applied to any tuned axis you'd like. 
* It works with any deadzone point, curvature setting, and saturation point.

![trimming tuned axis](https://github.com/cecil1527/JoystickGremlinExtensions/assets/4644033/c17cfc1d-c5b5-4a5a-bb4b-6e2beeee9fb7)

#### Trimmed axis has other quality of life features too. 
* When trimming, you need some method to either ignore inputs or ease into the new trim position, because if the trim were to get instantly applied, you'd have double input into the game at that moment, and that's no good.
* DCS has two options:
    1. Ignore input for a short time.
    1. Ignore input until the stick is recentered.
* The trimmed axis module has these options, where the time and margin for center are customizeable, but it also has the option to `smoothly go from one trim value to another`, which I quite like.

#### The last thing I should mention is how to use a Trimmed Axis with DCS.

1. Set up the trimmed axis as a JG user plugin in a profile of your choice, and confirm that it works using the JG input viewer.
    * Press the gear icon on a user plugin once you add it to customize it.
1. Tell DCS that you have a FFB stick, so it stops applying an offset to your input every time you trim.
    * The python trim axis will handle the offsets for trimming.
1. Map DCS axes to whichever vJoy axes you're using for pitch/roll/rudder.
    * And make sure the corresponding physical axes are no longer mapped!
1. You may still need to map the trim button in DCS (because some airframes configure SAS channels when you press trim)

## A bunch of other axis modules

These are a lot simpler than the two axis modules above.

1. **Axis Button**: Activates "low" or "high" depending on the position of the axis.

1. **LUT Axis**: Uses a look up table to transform axis values. 
    * Useful if you want an easy to define flat spot in a throttle axis or a slew axis.

1. **Relative Axis**: JG already has a relative axis, but it moves at a constant velocity. I wanted the ability to use custom easing functions.

1. **Stepper Axis**: Steps through whatever axis values you want. There are helper functions to create the list of values. Examples: 
    * Step through specific RPM values on a prop pitch axis.
    * Step through specific wingspan values on a gunsight axis.
    * Step through a radar elevation axis, with curvature. So the axis is slow in the middle and gets faster as you get near gimbal limits to be able to more easily look up/down.

1. **Toggle Axis**: Toggles between some value and its previous value. 
    * Useful for making a volume axis so you can easy toggle mute or a really low volume.

# Button Modules

JG has a lot of this functionality already, but these modules tend to expose more to the user. You can pass any callable into them and you can conditionally reset a chain, for example.

1. **Double-Click Toggle**: Toggles a vjoy button on when double-clicked. Single clicks result in normal press/release.
    * Useful for conditionally holding a button, like a G-Limit override.
1. **Sticky Buttons**: Buttons that stick on, with helper functions to release the rest.
    * Useful when you need to hold a button for a long time, but never want to hold two conflicting buttons at once.
1. **Macro**: Press/release vjoy buttons or keyboard keys in rapid succession.
    * Use the namespace `MacroEntries` which contains a helper function for creating a sequence of macro entries using shorthand.
1. **Tempo**: A container that executes one action when short pressed, and executes another when held.
1. **Chain**: A container that executes a sequence of actions, one per press, before resetting.