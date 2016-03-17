import math


class TrigonometryMixin(object):

    @staticmethod
    def degree_distance(d1, d2):
        dmin, dmax = sorted([d1, d2])
        delta1, delta2 = dmax - dmin, 360 + dmin - dmax
        return min(delta1, delta2)

    @staticmethod
    def anti_clockwise_degree_distance(start_degree, stop_degree):
        if start_degree == stop_degree:
            return 0
        if start_degree > 180:
            delta = 360 - start_degree
        else:
            delta = 0 - start_degree
        return (stop_degree + delta) % 360

    def find_scale_degree(self, start_degree, stop_degree, scales, scale):
        dist = self.anti_clockwise_degree_distance(start_degree, stop_degree)
        diff = max(scales) - min(scales)
        ratio = float(dist) / diff
        return (stop_degree - ratio * scale) % 360

    @staticmethod
    def find_rotation_angle(degree):
        """ Takes indicator degree and returns rotation angle for indicator. """
        # Degree could be negative values such as -45.
        degree = (360 + degree) % 360
        quotient, remainder = divmod(degree, 90)
        if quotient == 0:
            return -(90 - remainder)
        elif quotient == 1:
            return remainder
        elif quotient == 2:
            return 90 + remainder
        elif quotient == 3:
            return -(90 + 90 - remainder)
        raise RuntimeError('Unexpected degree: {}'.format(degree))

    @staticmethod
    def degree_to_pos(degree, radius, center=None):
        radian = math.radians(degree)
        x = round(math.cos(radian) * radius)
        y = -round(math.sin(radian) * radius)
        if center:
            center_x, center_y = center
            x += center_x
            y += center_y
        return int(x), int(y)
