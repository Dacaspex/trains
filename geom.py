import math
from pygame import Vector2


class Geom:
    @staticmethod
    def full_angle_to_horizon(vector: Vector2) -> float:
        return math.radians(Vector2(1, 0).angle_to(vector) % 360)

    @staticmethod
    def intersects_line_segment_line_segment(p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2) -> (bool, list):
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y
        D = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if D == 0:  # parallel
            return False, []
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / D
        if ua < 0 or ua > 1:  # out of range
            return False, []
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / D
        if ub < 0 or ub > 1:  # out of range
            return False, []
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        return True, [Vector2(x, y)]

    @staticmethod
    def intersects_line_segment_circle_segment(p1: Vector2, p2: Vector2, center: Vector2, radius: float,
                                               start_angle: float, stop_angle: float, epsilon: float = 0.01) -> (
            bool, list):
        intersections_found, intersections = Geom.intersects_line_circle(p1, p2, center, radius, epsilon)
        if len(intersections) == 0 or len(intersections) == 1:
            return intersections_found, intersections
        else:
            i1 = intersections[0]
            i2 = intersections[1]
            i1_on_lin_segment = not (
                    i1.x < p1.x and i1.x < p2.x or
                    i1.x > p1.x and i1.x > p2.x or
                    i1.y > p1.y and i1.y > p2.y or
                    i1.y < p1.y and i1.y < p2.y)
            i2_on_line_segment = not (
                    i2.x < p1.x and i2.x < p2.x or
                    i2.x > p1.x and i2.x > p2.x or
                    i2.y > p1.y and i2.y > p2.y or
                    i2.y < p1.y and i2.y < p2.y)
            i1_angle = Geom.full_angle_to_horizon(i1 - center)
            i2_angle = Geom.full_angle_to_horizon(i2 - center)
            i1_on_circle_segment = Geom._satisfies_angles(start_angle, stop_angle, i1_angle)
            i2_on_circle_segment = Geom._satisfies_angles(start_angle, stop_angle, i2_angle)

            true_intersections = []
            if i1_on_lin_segment and i1_on_circle_segment:
                true_intersections.append(i1)
            if i2_on_line_segment and i2_on_circle_segment:
                true_intersections.append(i2)

            return len(true_intersections) > 0, true_intersections

    @staticmethod
    def intersects_circle_segment_circle_segment(a_center: Vector2, a_radius: float, a_start_angle: float,
                                                 a_stop_angle: float, b_center: Vector2, b_radius: float,
                                                 b_start_angle: float, b_stop_angle: float, epsilon: float = 0.01) -> (
            bool, list):
        intersections_found, intersections = Geom.intersects_circle_circle(a_center, a_radius, b_center, b_radius, epsilon)

        if not intersections_found:
            return False, []

        i1 = intersections[0]
        i2 = intersections[1]

        i1_angle_circle_a = Geom.full_angle_to_horizon(i1 - a_center)
        i2_angle_circle_a = Geom.full_angle_to_horizon(i2 - a_center)
        i1_angle_circle_b = Geom.full_angle_to_horizon(i1 - b_center)
        i2_angle_circle_b = Geom.full_angle_to_horizon(i2 - b_center)
        i1_satisfies_a_angles = Geom._satisfies_angles(a_start_angle, a_stop_angle, i1_angle_circle_a)
        i2_satisfies_a_angles = Geom._satisfies_angles(a_start_angle, a_stop_angle, i2_angle_circle_a)
        i1_satisfies_b_angles = Geom._satisfies_angles(b_start_angle, b_stop_angle, i1_angle_circle_b)
        i2_satisfies_b_angles = Geom._satisfies_angles(b_start_angle, b_stop_angle, i2_angle_circle_b)

        true_intersections = []
        if i1_satisfies_a_angles and i1_satisfies_b_angles:
            true_intersections.append(i1)
        if i2_satisfies_a_angles and i2_satisfies_b_angles:
            true_intersections.append(i2)

        return len(true_intersections) > 0, true_intersections

    @staticmethod
    def intersects_line_segment_circle(p1: Vector2, p2: Vector2, center: Vector2, radius: float, epsilon: float = 0.01) -> (bool, list):
        return Geom.intersects_line_segment_circle_segment(p1, p2, center, radius, 0, 2 * math.pi, epsilon)

    @staticmethod
    def intersects_circle_segment_circle(a_center: Vector2, a_radius: float, a_start_angle: float,
                                                 a_stop_angle: float, b_center: Vector2, b_radius: float, epsilon: float = 0.01) -> (bool, list):
        return Geom.intersects_circle_segment_circle_segment(a_center, a_radius, a_start_angle, a_stop_angle, b_center, b_radius, 0, 2 * math.pi, epsilon)

    @staticmethod
    def intersects_circle_circle(a_center: Vector2, a_radius: float, b_center: Vector2, b_radius: float,
                                 epsilon: float = 0.01) -> (bool, list):
        """
        Computes the intersection points between two circles given by a_center with a_radius and b_center with b_radius.
        Implementation based on
        https://www.petercollingridge.co.uk/tutorials/computational-geometry/circle-circle-intersections/
        :param a_center: Center of circle A
        :param a_radius: Radius of circle A
        :param b_center: Center of circle B
        :param b_radius: Radius of circle B
        :param epsilon: Epsilon value
        :return: 1. The number of intersections found; 2. The first intersection, or None; 3. The second intersection,
            or None
        """
        # Compute distance between centers
        dx = a_center.x - b_center.x
        dy = a_center.y - b_center.y
        d = math.sqrt(dx * dx + dy * dy)

        # TODO: introduce epsilon here
        if d > a_radius + b_radius:
            return False, []
        if d < math.fabs(a_radius - b_radius):
            return False, []

        # assumption that circles with the same center and radii are not valid input and never overlap
        if d == 0:
            return False, []

        # Compute a and h values, as described in the documentation link
        a = ((a_radius * a_radius) - (b_radius * b_radius) + (d * d)) / (2 * d)
        h = math.sqrt((a_radius * a_radius) - (a * a))

        # Compute the coordinate of the line of intersection and the connecting vector between A and B
        v = (b_center - a_center).normalize()
        p = a_center + v * a

        # Compute the intersection points based on the intersection line
        p1 = p + h * VectorUtil.rotate_clockwise(v)
        p2 = p + h * VectorUtil.rotate_counter_clockwise(v)

        return True, [p1, p2]

    @staticmethod
    def intersects_line_circle(p1: Vector2, p2: Vector2, center: Vector2, radius: float, epsilon: float = 0.01) -> (
            bool, list):
        """
        Computes the intersection point(s) between a line given by p1 and p2, and a circle given by center and radius.
        Based on https://stackoverflow.com/questions/23016676/line-segment-and-circle-intersection
        :param p1: Line point 1
        :param p2: Line point 2
        :param center: Center of the circle
        :param radius: Radius of the circle
        :param epsilon: Epsilon value
        :return: 1. The number of intersections found; 2. The first intersection, or None; 3. The second intersection,
            or None
        """
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        A = dx * dx + dy * dy
        B = 2 * (dx * (p1.x - center.x) + dy * (p1.y - center.y))
        C = (p1.x - center.x) ** 2 + (p1.y - center.y) ** 2 - radius ** 2
        det = B * B - 4 * A * C
        if A <= epsilon or det < 0:
            return False, []
        elif det == 0:
            t = -B / (2 * A)
            i1 = Vector2(p1.x + t * dx, p1.y + t * dy)
            return True, [i1]
        else:
            t1 = ((-B + math.sqrt(det)) / (2 * A))
            t2 = ((-B - math.sqrt(det)) / (2 * A))
            i1 = Vector2(p1.x + t1 * dx, p1.y + t1 * dy)
            i2 = Vector2(p1.x + t2 * dx, p1.y + t2 * dy)
            return True, [i1, i2]

    @staticmethod
    def _satisfies_angles(start_angle, stop_angle, intersection_angle) -> bool:
        if start_angle < stop_angle and start_angle < intersection_angle < stop_angle:
            return True
        elif start_angle > stop_angle and (start_angle < intersection_angle or intersection_angle < stop_angle):
            return True
        return False


class VectorUtil:
    @staticmethod
    def from_angle(angle: float):
        return Vector2(math.cos(angle), math.sin(angle))

    @staticmethod
    def rotate_clockwise(vector: Vector2, angle: float = math.pi / 2):
        return vector.rotate_rad(-angle)

    @staticmethod
    def rotate_counter_clockwise(vector: Vector2, angle: float = math.pi / 2):
        return vector.rotate_rad(angle)
