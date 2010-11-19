#
# skeleton.py - An example showing the basic structure of a complex setup with
# multiple scenes and various other features.
#

from mididings import *
from mididings.extra import *

# some classes are defined in separate modules because they depend on
# additional Python packages to be installed. uncomment these imports if you
# need them
#from mididings.extra.osc import OSCInterface
#from mididings.extra.inotify import AutoRestart


config(
    # uncomment this to use the JACK MIDI backend instead of ALSA sequencer
    #backend='jack',

    # you can assign names to input/output ports...
    out_ports=['spam', 'ham', 'eggs'],
    # ...or just change the number of ports available
    #in_ports=2,

    # when using a patchbay like QjackCtl, a small delay allows ports to be
    # connected before any MIDI events are sent
    #start_delay=0.5,
)

hook(
    # some functions (like scene switching) can be controlled via OSC.
    # this is needed for the livedings GUI, for example.
    # by default, UDP port 56418 is used to control mididings, and mididings
    # will send notification to port 56419.
    #OSCInterface(),

    # uncomment this if you want mididings to restore the previously active
    # scene when it is restarted
    #MemorizeScene('scene.txt'),

    # mididings can automatically watch this script (and modules it imports)
    # for changes, and restart itself automatically
    #AutoRestart(),
)


# in this example, we use the control to switch scenes in response to program
# change events
control = Filter(PROGRAM) >> SceneSwitch()

# use the pre and post patches to print all incoming and outgoing events.
# pre also filters out program changes, as these are already handled by the
# control patch and probably meaningless for individual scenes
pre = Print('input', portnames='in') >> ~Filter(PROGRAM)
post = Print('output', portnames='out')


# define some sounds/outputs.
# by using OutputTemplate() instead of Output(), we allow additional
# parameters (like volume) to be specified later, when these sounds are used
# in patches.
spam1 = Output('spam', 1)               # channel 1 on port 'spam'
spam2 = Output('spam', 2)               # channel 2 on port 'spam'
ham1  = OutputTemplate('ham', 1, None)  # channel 1 on port 'ham'
eggs1 = OutputTemplate('eggs', 1, 23)   # channel 1, program 23 on port 'eggs'
eggs2 = OutputTemplate('eggs', 1, 42)   # channel 1, program 42 on port 'eggs'


## now define some patches using the sounds defined above
dummy_1 = KeySplit('c3', spam1, spam2)
dummy_2a = ham1(64) // eggs1(127)
dummy_2b = ham1(96) // (Transpose(12) >> eggs2(64))


# finally, assign scene names and program numbers to these patches...
scenes = {
    1:  Scene("Dummy Scene", dummy_1),
    2:  SceneGroup("Dummy SceneGroup", [
            Scene("Subscene A", dummy_2a),
            Scene("Subscene B", dummy_2b),
        ]),
    # ...
}


# ...and start the whole thing...
run(
    control=control,
    pre=pre,
    post=post,
    scenes=scenes,
)
