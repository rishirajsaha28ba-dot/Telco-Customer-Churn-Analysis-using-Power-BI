import unittest

from clipper import SpikeDetector


class SpikeDetectorTests(unittest.TestCase):
    def feed(self, detector, counts, start=0, step=10):
        return [detector.add_bucket(c, start + i * step) for i, c in enumerate(counts)]

    def test_quiet_chat_never_fires(self):
        d = SpikeDetector()
        self.assertFalse(any(self.feed(d, [3, 4, 2, 5, 3, 4, 2, 3])))

    def test_burst_above_baseline_fires(self):
        d = SpikeDetector()
        fired = self.feed(d, [4, 5, 4, 6, 5, 60])
        self.assertEqual(fired, [False, False, False, False, False, True])

    def test_below_min_msgs_does_not_fire(self):
        d = SpikeDetector(min_msgs=15)
        self.assertFalse(any(self.feed(d, [1, 1, 1, 10])))

    def test_cooldown_suppresses_repeat_clips(self):
        d = SpikeDetector(cooldown=60)
        fired = self.feed(d, [4, 4, 4, 50, 80, 90], step=10)
        self.assertEqual(sum(fired), 1)

    def test_second_spike_after_cooldown_fires_again(self):
        d = SpikeDetector(cooldown=60)
        fired = self.feed(d, [4, 4, 4, 50, 4, 4, 4, 4, 4, 4, 4, 4, 60], step=10)
        self.assertEqual(sum(fired), 2)


if __name__ == "__main__":
    unittest.main()
