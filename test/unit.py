import unittest
from mididings import *
from mididings.main import test_run, test_run_patches


class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        config(data_offset = 0, verbose = False)
        self.noteon1 = MidiEvent(NOTEON, 0, 0, 66, 23)
        self.noteon2 = MidiEvent(NOTEON, 0, 0, 42, 127)
        self.noteon3 = MidiEvent(NOTEON, 0, 1, 23, 127)
        self.ctrl1 = MidiEvent(CTRL, 0, 0, 23, 42)
        self.prog1 = MidiEvent(PROGRAM, 0, 0, 0, 7)

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
        assert len(r) == 0

    def testFilter(self):
        p = Filter(PROGRAM)
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
        p = ~PortFilter(1)
        r = test_run(p, self.noteon1)
        assert len(r) == 1

    def testVelocityFilter(self):
        p = VelocityFilter(64, 127)
        r = test_run(p, self.noteon1)
        assert len(r) == 0
        r = test_run(p, self.noteon2)
        assert len(r) == 1
        r = test_run(p, self.prog1)
        assert len(r) == 0

    def testSplit(self):
        p = Split({ NOTE: Channel(1), PROGRAM: Channel(2) })
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        assert r[0].channel_ == 1
        r = test_run(p, self.prog1)
        assert len(r) == 1
        assert r[0].channel_ == 2
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
        assert len(r) == 2
        assert r[0].channel_ == 3
        assert r[1].channel_ == 7

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

    def testGenerateEvent(self):
        p = CtrlChange(23, 42)
        event = MidiEvent(NOTEON, 0, 8, 15, 16)
        r = test_run(p, event)
        assert len(r) == 1
        assert r[0] == MidiEvent(CTRL, 0, 8, 23, 42)

    def testDataOffset(self):
        config(data_offset = 1)
        p = Channel(6)
        ev = MidiEvent(PROGRAM, 0, 0, 0, 41)
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

    def testSanitize(self):
        def foo(ev):
            assert False
        p = Port(42) >> Sanitize() >> Call(foo)
        test_run(p, self.noteon1)
        p = Velocity(+666) >> Sanitize()
        r = test_run(p, self.noteon1)
        assert len(r) == 1
        assert r[0].data2 == 127

    def testPatchSwitch(self):
        p = {
            0:  Split({
                    PROGRAM:  PatchSwitch(),
                    ~PROGRAM: Channel(7),
                }),
            1: Channel(13),
        }
        events = [
            MidiEvent(NOTEON, 0, 0, 69, 123),
            MidiEvent(PROGRAM, 0, 0, 0, 1),
            MidiEvent(NOTEON, 0, 0, 23, 42),
            MidiEvent(NOTEOFF, 0, 0, 69, 0)
        ]
        r = test_run_patches(p, events)
        assert len(r) == 3
        assert r[0].type_ == NOTEON
        assert r[0].channel_ == 7
        assert r[1].type_ == NOTEON
        assert r[1].channel_ == 13
        assert r[2].type_ == NOTEOFF
        assert r[2].channel_ == 7

    def testNamedPorts(self):
        config(out_ports = ['foo', 'bar', 'baz'])
        r = test_run(Port('bar'), self.noteon1)
        assert len(r) == 1
        assert r[0].port_ == 1


if __name__ == "__main__":
    unittest.main()
