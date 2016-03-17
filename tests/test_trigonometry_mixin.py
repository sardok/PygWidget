import pytest
from pygwidget.mixins import TrigonometryMixin


class TestTrigonometryMixin(object):
    mixin = TrigonometryMixin()

    @pytest.mark.parametrize('start_degree, stop_degree, expected', [
        (0, 90, 90),
        (0, 180, 180),
        (150, 180, 30),
        (330, 90, 120),
        (330, 150, 180),
        (300, 150, 210),
        (315, 225, 270),
        (330, 30, 60),
        (330, 330, 0),
        (330, 315, 345),
        (330, 360, 30),
        (330, 0, 30),
    ])
    def test_degree_distance(self, start_degree, stop_degree, expected):
        result = self.mixin.anti_clockwise_degree_distance(
            start_degree, stop_degree)
        assert expected == result

    @pytest.mark.parametrize(
        'start_degree, stop_degree, scales, scale, expected', [
            (0,  180, [0, 1, 2], 1, 90),
            (0, 180, range(0, 100, 10), 45, 90),
            (330, 180, range(0, 100, 10), 90, 330),
            (45, 135, [0, 1, 2], 1, 90),
            (330, 210, range(0, 9), 1, 180),
            (325, 215, range(0, 210, 20), 100, 90)
        ])
    def test_find_scale_degree(self, start_degree, stop_degree, scales, scale,
                               expected):
        result = self.mixin.find_scale_degree(
            start_degree, stop_degree, scales, scale)
        assert expected == result

    @pytest.mark.parametrize('degree, expected', [
        (90, 0),
        (0, -90),
        (180, 90),
        (45, -45),
        (135, 45),
        (225, 135),
        (270, -180),
        (315, -135),
        (-45, -135),
        (330, -120),
        (-30, -120)
    ])
    def test_find_rotation_angle(self, degree, expected):
        assert self.mixin.find_rotation_angle(degree) == expected
