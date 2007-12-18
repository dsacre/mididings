import unittest
from mididings import *
import mididings
from _mididings import MidiEvent, MidiEventType

mididings.misc._CHANNEL_OFFSET = 0
mididings.misc._PROGRAM_OFFSET = 0


def make_event(type, port, channel, data1, data2):
    ev = MidiEvent()
    ev.type = type
    ev.port = port
    ev.channel = channel
    ev.data1 = data1
    ev.data2 = data2
    return ev


class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        self.noteon1 = make_event(MidiEventType.NOTEON, 0, 0, 66, 23)
        self.noteon2 = make_event(MidiEventType.NOTEON, 0, 0, 42, 127)
        self.pgmchange1 = make_event(MidiEventType.PGMCHANGE, 0, 0, 0, 7)

    def tearDown(self):
        pass

    def testPass(self):
        r = test_run(Pass(), self.noteon1)
        assert len(r) == 1
        assert r[0] == self.noteon1

    def testFork(self):
        r = test_run(Fork([ Pass(), Pass() ]), self.noteon1)
        assert len(r) == 2
        assert r[0] == r[1] == self.noteon1

    def testVelocityFilter(self):
        p = VelocityFilter(64, 127)
        r = test_run(p, self.noteon1)
        assert len(r) == 0
        r = test_run(p, self.noteon2)
        assert len(r) == 1
        r = test_run(p, self.pgmchange1)
        assert len(r) == 1

    def testInvertedFilter(self):
        p = ~VelocityFilter(64, 127)
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        r = test_run(p, self.noteon2)
        assert len(r) == 0
        r = test_run(p, self.pgmchange1)
        assert len(r) == 1

    def testProgramChangeGate(self):
        p = ProgramChangeGate()
        r = test_run(p, self.noteon1)
        assert len(r) == 0
        r = test_run(p, self.pgmchange1)
        assert len(r) == 1
        pp = ~p
        r = test_run(pp, self.noteon1)
        assert len(r) == 1
        r = test_run(pp, self.pgmchange1)
        assert len(r) == 0

    def testKeySplit(self):
        p = KeySplit(55, Channel(3), Channel(7))
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        assert r[0].channel == 7
        r = test_run(p, self.noteon2)
        assert len(r) == 1
        assert r[0].channel == 3
        r = test_run(p, self.pgmchange1)
        assert len(r) == 1
        assert r[0] == self.pgmchange1


if __name__ == "__main__":
    unittest.main()
