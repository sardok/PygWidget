import pygame
import pygame.sprite
import pygame.gfxdraw
import pygame.font
import pygame.locals

from pygwidget.colors import NEON_GREEN
from pygwidget.mixins import TrigonometryMixin

INDICATOR_DIRECTION_CLOCKWISE = - 1
INDICATOR_DIRECTION_ANTI_CLOCKWISE = 1


class Speedometer(TrigonometryMixin, pygame.sprite.Sprite):
    def __init__(self, x, y, scales, width=None, start_degree=0, stop_degree=180,
                 background_color=None, background_image_path=None,
                 label_color=None, font_name=None, indicator_image_path=None,
                 scale_anchor_x=None, scale_anchor_y=None, scale_radius=None,
                 indicator_color=None, indicator_anchor_height=None,
                 indicator_length=None, labels=None, label_height=None):
        super(Speedometer, self).__init__()
        # Set degree values
        self.start_degree = start_degree
        self.stop_degree = stop_degree
        self.indicator_degree = self.stop_degree

        # Label properties
        self.label_height = label_height or 25
        self.label_color = label_color or NEON_GREEN
        font_name = font_name or 'freesansbold.ttf'
        label_font = pygame.font.Font(font_name, self.label_height)
        labels = labels if labels is not None else scales
        self.labels = [label_font.render(str(s), True, self.label_color)
                       for s in labels]

        # Scale colors
        self.indicator_color = indicator_color or self.label_color

        # Setup main surface
        if background_image_path:
            image = pygame.image.load(background_image_path).convert_alpha()
            self.image = image
            self.bgimage = image.copy()
            self.bgcolor = None
            if not (scale_anchor_x and scale_anchor_y and
                        (indicator_length or indicator_image_path)):
                raise RuntimeError(
                    ('If background image is given, indicator properties such '
                     'as x, y and length (or image) must be provided as well.'))
            self.scale_anchor = (scale_anchor_x, scale_anchor_y)
            self.scale_radius = scale_radius
        else:
            width = width or 400
            scale_offset = (0, self.label_height)
            self.scale_radius = scale_radius or indicator_length or width / 2
            scale_max_height = self._calculate_scale_height(
                self.start_degree, self.stop_degree, self.scale_radius)

            height = scale_max_height + scale_offset[1] * 2
            self.image = pygame.Surface([width, height])
            self.bgimage = None
            self.bgcolor = background_color or pygame.Color('black')
            self.scale_anchor = (width / 2 + scale_offset[0],
                                 self.scale_radius + scale_offset[1])

        if indicator_image_path:
            self.indicator_image = pygame.image.load(indicator_image_path)
            self.indicator_length = self.indicator_image.get_rect().height
            if self.scale_radius is None:
                self.scale_radius = self.indicator_length
        else:
            self.indicator_image = None
            self.indicator_length = indicator_length or self.scale_radius

        if not self.scale_radius:
            raise RuntimeError(
                ('Cannot determine scale radius, either provide scale_radius or'
                 ' indicator_length or indicator_image_path'))

        self.indicator_anchor_height = indicator_anchor_height or 0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Setup scale surface
        self.scales = scales
        self.scale_units = None
        self.scale_unit_image = None

        # Target value, where indicator would want to point
        self.target_value = None

        self._check_scale_types()
        self._draw_statics()
        self._draw_indicator(self.indicator_degree)

    def _check_scale_types(self):
        xs = [isinstance(s, int) for s in self.scales]
        if not (len(self.scales) > 0 and all(xs)):
            raise RuntimeError('"scales" must be list of integers.')

    def _calculate_scale_height(self, d1, d2, radius):
        """ Returns height needed for scale part by starting from anchor position.

         If given degrees are between 0 and 180, then bottom half of the scale
         is not needed.
        """
        dmin, dmax = sorted([d1, d2])
        if 0 <= dmin <= dmax <= 180:
            return radius

        _, y1 = self.degree_to_pos(d1, radius)
        _, y2 = self.degree_to_pos(d2, radius)
        return radius + max(y1, y2)

    def _rotate_image(self, image, angle):
        """ See pygame.transform.rotate doc about angle parameter. """
        return pygame.transform.rotate(image, angle)

    def _update_indicator_slice_pos(self, offset):
        new_degree = (self.indicator_degree + offset) % 360
        self.indicator_degree = new_degree

    def _orient_indicator_image(self, degree):
        dl = abs(self.indicator_length - self.indicator_anchor_height)
        indicator_center = (self.indicator_length / 2) - dl
        return self.degree_to_pos(degree, indicator_center, self.scale_anchor)

    def _draw_indicator_image(self, angle):
        rotation_angle = self.find_rotation_angle(self.indicator_degree)
        indicator = self._rotate_image(self.indicator_image, rotation_angle)
        center = self._orient_indicator_image(angle)
        r = indicator.get_rect().copy()
        r.center = center
        self.image.blit(indicator, r)

    def _draw_indicator_raw(self, angle):
        """ Draws indicator by means of pygame draw functions. """
        x, y = self.degree_to_pos(
            angle, self.scale_radius, self.scale_anchor)
        center_x, center_y = self.scale_anchor
        pygame.gfxdraw.line(
            self.image, center_x, center_y, x, y, self.indicator_color)
        r = int(round(self.scale_radius * 0.02))
        pygame.gfxdraw.filled_circle(
            self.image, center_x, center_y, r, self.indicator_color)

    def _draw_indicator(self, degree=None):
        degree = degree or self.indicator_degree
        if self.indicator_image:
            self._draw_indicator_image(degree)
        else:
            self._draw_indicator_raw(degree)

    def _draw_labels(self):
        dist = self.anti_clockwise_degree_distance(
            self.start_degree, self.stop_degree)
        step = dist / (len(self.labels) - 1)
        label_angles = [self.stop_degree - step * x
                        for x in range(0, len(self.labels))]

        for label, degree in zip(self.labels, label_angles):
            self._draw_scale_unit(degree)
            # Find center point for the label box
            r = label.get_rect()
            radius = self.scale_radius - self.label_height - r.width / 2
            xl, yl = self.degree_to_pos(degree, radius, self.scale_anchor)
            r.center = (xl, yl)
            self.image.blit(label, r)

    def _draw_scale_unit_line(self, degree, height, color):
        dr = height / 2
        x1, y1 = self.degree_to_pos(
            degree, self.scale_radius - dr, self.scale_anchor)
        x2, y2 = self.degree_to_pos(
            degree, self.scale_radius + dr, self.scale_anchor)
        pygame.gfxdraw.line(self.image, x1, y1, x2, y2, color)

    def _draw_scale_unit_image(self, degree):
        rotation_angle = self.find_rotation_angle(degree)
        rotated = self._rotate_image(self.scale_unit_image, rotation_angle)

        pos = self.degree_to_pos(
            degree, self.scale_radius, self.scale_anchor)
        r = rotated.get_rect()
        r.center = pos
        self.image.blit(rotated, r)

    def _draw_scale_unit(self, degree, height=None):
        """ Draws scale units by using either given image or draw functions. """
        height = height or self.label_height
        if self.scale_unit_image:
            self._draw_scale_unit_image(degree)
        else:
            self._draw_scale_unit_line(degree, height, self.label_color)

    def _draw_scale(self):
        pass

    def _draw_background(self):
        if self.bgcolor:
            self.image.fill(self.bgcolor)
        else:
            self.image.blit(self.bgimage, (0, 0))

    def _draw_statics(self):
        self._draw_background()
        self._draw_scale()
        self._draw_labels()

    def _get_and_update_indicator_degree(self, direction):
        angle = self.indicator_degree
        self._update_indicator_slice_pos(direction)
        return angle

    def _move_towards_target_value(self, value=None):
        target_value = value if value is not None else self.target_value
        scale_degree = self.find_scale_degree(
            self.start_degree, self.stop_degree, self.scales, target_value)
        target_degree = int(round(scale_degree))

        if target_degree == self.indicator_degree:
            # We are already pointing to the target value
            return

        ind_delta = self.anti_clockwise_degree_distance(
            self.start_degree, self.indicator_degree)
        tar_delta = self.anti_clockwise_degree_distance(
            self.start_degree, target_degree)
        if ind_delta < tar_delta:
            self._update_indicator_slice_pos(INDICATOR_DIRECTION_ANTI_CLOCKWISE)
        else:
            self._update_indicator_slice_pos(INDICATOR_DIRECTION_CLOCKWISE)

        self._draw_statics()
        self._draw_indicator()

    def _set_target_value(self, value):
        """ Sets the value as target. If given value is out of range, set to
         min or max value. """
        try:
            value = int(value)
            smin = min(self.scales)
            smax = max(self.scales)
            if smin <= value <= smax:
                self.target_value = value
            elif abs(value - smin) < abs(smax - value):
                self.target_value = smin
            else:
                self.target_value = smax
        except (TypeError, ValueError):
            pass

    def update(self, value):
        if value:
            self._set_target_value(value)
        if self.target_value is not None:
            self._move_towards_target_value()
