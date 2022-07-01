import math
from shapely.geometry import Point, Polygon, LineString

THETA = 2 * math.pi / 5
HALF_THETA = math.pi / 5
HALF_COMPLEMENT = 3 * math.pi / 10

PHI = (1 + math.sqrt(5)) / 2


def pfmt(point: Point, separator: str = ','):
    return f'{point.x:.1f}{separator}{point.y:.1f}'


def apothem_for_side(side: float) -> float:
    return side * math.tan(HALF_COMPLEMENT) / 2


def side_for_apothem(apothem: float) -> float:
    return 2 * apothem / math.tan(HALF_COMPLEMENT)


def radius_for_side(side: float) -> float:
    a = apothem_for_side(side)
    return math.sqrt(side ** 2 / 4 + a ** 2)


class RegularPentagon:
    def __init__(self, side_length, cx=0, cy=0):
        self.side_length = side_length
        self.p_center = Point(cx, cy)
        self.radius = side_length / math.sqrt(3 - PHI)
        self.apothem = self.radius * PHI / 2
        h_shift = side_length * (PHI - 1) / 2
        v_shift = side_length * math.sqrt(2 + PHI) / 2
        half_side = self.side_length / 2
        self.p_bottom_left = Point(self.p_center.x - half_side, self.p_center.y + self.apothem)
        self.p_bottom_right = Point(self.p_center.x + half_side, self.p_bottom_left.y)
        self.p_left = Point(self.p_bottom_left.x - h_shift, self.p_bottom_left.y - v_shift)
        self.p_right = Point(self.p_bottom_right.x + h_shift, self.p_left.y)
        self.p_top = Point(self.p_center.x, self.p_center.y - self.radius)

    def iter_clockwise(self):
        yield self.p_top
        yield self.p_right
        yield self.p_bottom_right
        yield self.p_bottom_left
        yield self.p_left

    @property
    def polygon(self):
        return Polygon(list(self.iter_clockwise()))

    @property
    def b_top(self):
        return LineString([self.p_center, self.p_top])

    @property
    def b_right(self):
        return LineString([self.p_center, self.p_right])

    @property
    def b_left(self):
        return LineString([self.p_center, self.p_left])

    @property
    def b_bottom_right(self):
        return LineString([self.p_center, self.p_bottom_right])

    @property
    def b_bottom_left(self):
        return LineString([self.p_center, self.p_bottom_left])

    @property
    def s_up_right(self):
        return LineString([self.p_top, self.p_right])

    @property
    def s_up_left(self):
        return LineString([self.p_top, self.p_left])

    @property
    def s_down_right(self):
        return LineString([self.p_right, self.p_bottom_right])

    @property
    def s_down_left(self):
        return LineString([self.p_left, self.p_bottom_left])

    @property
    def s_bottom(self):
        return LineString([self.p_bottom_left, self.p_bottom_right])

    def svg_polygon_path(self):
        return ' '.join(f'{p.x:.1f},{p.y:.1f}' for p in self.iter_clockwise())

    @property
    def h(self):
        return self.radius * (PHI - 1) / 2

    @property
    def rho(self):
        return self.h * PHI / 2

    def concentric_child(self):
        return RegularPentagon(self.side_length * (3 - PHI) / 2, self.p_center.x, self.p_center.y)

    def pentagram_points(self):
        yield self.p_top
        yield self.p_bottom_right
        yield self.p_left
        yield self.p_right
        yield self.p_bottom_left
        yield self.p_top


def draw_phlogiston(frame: RegularPentagon):
    rho = frame.rho
    inner = frame.concentric_child()
    place = inner.s_up_left.interpolate(rho)
    yield f'M {place.x:.2f} {place.y:.2f}'
    place = inner.s_up_right.interpolate(rho)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    place = LineString([inner.p_right, inner.p_top]).interpolate(rho)
    yield f'L {place.x:.2f} {place.y:.2f}'
    branch_right = LineString([inner.p_right, inner.p_center])
    branch_left = LineString([inner.p_left, inner.p_center])
    place = branch_right.interpolate(rho)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    x_shaft_right = inner.p_bottom_right.x - rho
    x_shaft_left = inner.p_bottom_left.x + rho
    shaft_base_right = Point(x_shaft_right, frame.p_bottom_right.y)
    shaft_base_left = Point(x_shaft_left, frame.p_bottom_left.y)
    shaft_width = x_shaft_right - x_shaft_left
    shaft_radius = shaft_width / 2
    shaft_anchor_right = Point(x_shaft_right, inner.p_bottom_right.y - shaft_radius)
    shaft_anchor_left = Point(x_shaft_left, inner.p_bottom_left.y + shaft_radius)
    armpit_right = Point(x_shaft_right, inner.p_right.y)
    armpit_left = Point(x_shaft_left, inner.p_left.y)
    shaft_wall_right = LineString([armpit_right, shaft_base_right])
    shaft_wall_left = LineString([armpit_left, shaft_base_left])
    place = shaft_wall_right.intersection(branch_right)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = shaft_anchor_right
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = Point(inner.p_bottom_right.x, place.y)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = Point(place.x, place.y + shaft_width)
    yield f'A {shaft_radius:.2f} {shaft_radius:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    place = Point(x_shaft_right, place.y)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = shaft_base_right
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = shaft_base_left
    yield f'A {shaft_radius:.2f} {shaft_radius:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    place = shaft_anchor_left
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = Point(inner.p_bottom_left.x, place.y)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = Point(place.x, place.y - shaft_width)
    yield f'A {shaft_radius:.2f} {shaft_radius:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    place = Point(x_shaft_left, place.y)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = shaft_wall_left.intersection(branch_left)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = branch_left.interpolate(rho)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = LineString([inner.p_left, inner.p_top]).interpolate(rho)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    yield 'z'


def draw_variant(frame: RegularPentagon):
    rho = frame.rho
    inner = frame.concentric_child()
    place = inner.s_up_left.interpolate(rho)
    yield f'M {place.x:.2f} {place.y:.2f}'
    place = inner.s_up_right.interpolate(rho)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    place = LineString([inner.p_right, inner.p_top]).interpolate(rho)
    yield f'L {place.x:.2f} {place.y:.2f}'
    branch_ur = LineString([inner.p_right, inner.p_center])
    branch_dr = LineString([inner.p_bottom_right, inner.p_center])
    branch_ul = LineString([inner.p_left, inner.p_center])
    branch_dl = LineString([inner.p_bottom_left, inner.p_center])
    place = branch_ur.interpolate(rho)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    x_shaft_right = inner.p_bottom_right.x - rho
    x_shaft_left = inner.p_bottom_left.x + rho
    shaft_wall_right = LineString([Point(x_shaft_right, frame.p_top.y), Point(x_shaft_right, frame.p_bottom_right.y)])
    shaft_wall_left = LineString([Point(x_shaft_left, frame.p_top.y), Point(x_shaft_left, frame.p_bottom_left.y)])
    place = branch_ur.intersection(shaft_wall_right)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = branch_dr.intersection(shaft_wall_right)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = branch_dr.interpolate(rho)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = Point(x_shaft_right, inner.p_bottom_right.y)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    place = Point(x_shaft_left, place.y)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = branch_dl.interpolate(rho)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    place = branch_dl.intersection(shaft_wall_left)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = branch_ul.intersection(shaft_wall_left)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = branch_ul.interpolate(rho)
    yield f'L {place.x:.2f} {place.y:.2f}'
    place = LineString([inner.p_left, inner.p_top]).interpolate(rho)
    yield f'A {rho:.2f} {rho:.2f} 0 1 1 {place.x:.2f} {place.y:.2f}'
    yield 'z'
