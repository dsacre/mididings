import unittest
from mididings import *
from mididings.main import test_run


class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        config(data_offset = 0)
        self.noteon1 = MidiEvent(TYPE_NOTEON, 0, 0, 66, 23)
        self.noteon2 = MidiEvent(TYPE_NOTEON, 0, 0, 42, 127)
        self.noteon3 = MidiEvent(TYPE_NOTEON, 0, 1, 23, 127)
        self.ctrl1 = MidiEvent(TYPE_CTRL, 0, 0, 23, 42)
        self.prog1 = MidiEvent(TYPE_PROGRAM, 0, 0, 0, 7)

    def tearDown(self):
        pass

    def testFork(self):
        r = test_run(Fork([ Pass(), Pass() ]), self.noteon1)
        assert len(r) == 2
        assert r[0] == r[1] == self.noteon1
        r = test_run(Fork([ Pass(), Discard() ]), self.ctrl1)
        assert len(r) == 1
        assert r[0] == self.ctrl1

    def testPassDiscard(self):
        r = test_run(Pass(), self.noteon1)
        assert len(r) == 1
        assert r[0] == self.noteon1
        r = test_run(Discard(), self.noteon1)
        assert len(r) == 0

    def testInvertedFilter(self):
        p = ~VelocityFilter(64, 127)
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        r = test_run(p, self.noteon2)
        assert len(r) == 0
        r = test_run(p, self.prog1)
#        assert len(r) == 1
        assert len(r) == 0

    def testTypeFilter(self):
        p = TypeFilter(TYPE_PROGRAM)
        r = test_run(p, self.noteon1)
        assert len(r) == 0
        r = test_run(p, self.prog1)
        assert len(r) == 1
        pp = ~p
        r = test_run(pp, self.noteon1)
        assert len(r) == 1
        r = test_run(pp, self.prog1)
        assert len(r) == 0

    def testPortFilter(self):
        p = PortFilter(0)
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        p = PortFilter(1)
        r = test_run(p, self.noteon1)
        assert len(r) == 0

    def testVelocityFilter(self):
        p = VelocityFilter(64, 127)
        r = test_run(p, self.noteon1)
        assert len(r) == 0
        r = test_run(p, self.noteon2)
        assert len(r) == 1
        r = test_run(p, self.prog1)
#        assert len(r) == 1
        assert len(r) == 0

    def testTypeSplit(self):
        p = TypeSplit({ TYPE_NOTE: Port(1), TYPE_PROGRAM: Port(2) })
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        assert r[0].port_ == 1
        r = test_run(p, self.prog1)
        assert len(r) == 1
        assert r[0].port_ == 2
        r = test_run(p, self.ctrl1)
        assert len(r) == 0

    def testChannelSplit(self):
        p = ChannelSplit({ 0: Discard(), (1, 2): Pass() })
        r = test_run(p, self.noteon1)
        assert len(r) == 0
        r = test_run(p, self.noteon3)
        assert len(r) == 1
        assert r[0] == self.noteon3

    def testKeySplit(self):
        p = KeySplit(55, Channel(3), Channel(7))
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        assert r[0].channel_ == 7
        r = test_run(p, self.noteon2)
        assert len(r) == 1
        assert r[0].channel_ == 3
        r = test_run(p, self.prog1)
        assert len(r) == 0

    def testCall(self):
        def foo(ev):
            assert ev.port == 0
            assert ev.channel == 0
            assert ev.note == 66
            assert ev.velocity == 23
            ev.velocity = 42
        def bar(ev):
            assert ev.velocity == 42
        p = Call(foo) >> Call(bar)
        r = test_run(p, self.noteon1)

    def testDataOffset(self):
        config(data_offset = 1)
        p = Channel(6)
        ev = MidiEvent(TYPE_PROGRAM, 1, 1, 0, 42)
        assert ev.channel_ == 0
        assert ev.data2 == 41
        def foo(ev):
            assert ev.channel == 1
            assert ev.channel_ == 0
            assert ev.program == 42
            assert ev.data2 == 41
            ev.channel = 6
        r = test_run(p, ev)
        assert r[0].channel_ == 5

    def testPatchSwitch(self):
        p = {
            0:  TypeSplit({
                    TYPE_PROGRAM:  PatchSwitch(),
                    ~TYPE_PROGRAM: Channel(7),
                }),
            1: Channel(13),
        }
        events = [
            MidiEvent(TYPE_NOTEON, 0, 0, 69, 123),
            MidiEvent(TYPE_PROGRAM, 0, 0, 0, 1),
            MidiEvent(TYPE_NOTEON, 0, 0, 23, 42),
            MidiEvent(TYPE_NOTEOFF, 0, 0, 69, 0)
        ]
        r = test_run(p, events)
        assert len(r) == 3
        assert r[0].type_ == TYPE_NOTEON
        assert r[0].channel_ == 7
        assert r[1].type_ == TYPE_NOTEON
        assert r[1].channel_ == 13
        assert r[2].type_ == TYPE_NOTEOFF
        assert r[2].channel_ == 7


if __name__ == "__main__":
    unittest.main()
