import math
from pygame import Vector2


class Geom:
    @staticmethod
    def full_angle_to_horizon(vector: Vector2) -> float:
        return math.radians(Vector2(1, 0).angle_to(vector) % 360)

    @staticmethod
    def intersects_line_segment_line_segment(p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2) -> (bool, Vector2):
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y
        D = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if D == 0:  # parallel
            return False, None
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / D
        if ua < 0 or ua > 1:  # out of range
            return False, None
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / D
        if ub < 0 or ub > 1:  # out of range
            return False, None
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        return True, Vector2(x, y)

    @staticmethod
    def intersects_line_segment_circle_segment(p1: Vector2, p2: Vector2, center: Vector2, radius: float,
                                               start_angle: float, stop_angle: float, epsilon: float = 0.01) -> (
            bool, Vector2):
        intersections_found, i1, i2 = Geom.intersects_line_circle(p1, p2, center, radius, epsilon)
        if intersections_found == 0:
            return False, None
        elif intersections_found == 1:
            return True, i1
        else:
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
            i1_on_circle_segment = start_angle <= Geom.full_angle_to_horizon(i1 - center) <= stop_angle
            i2_on_circle_segment = start_angle <= Geom.full_angle_to_horizon(i2 - center) <= stop_angle

            if i1_on_lin_segment and i1_on_circle_segment:
                return True, i1
            elif i2_on_line_segment and i2_on_circle_segment:
                return True, i2
            else:
                return False, None

    @staticmethod
    def intersects_circle_segment_circle_segment(a_center: Vector2, a_radius: float, a_start_angle: float,
                                                 a_stop_angle: float, b_center: Vector2, b_radius: float,
                                                 b_start_angle: float, b_stop_angle: float, epsilon: float = 0.01) -> (
            int, Vector2):
        # https://www.petercollingridge.co.uk/tutorials/computational-geometry/circle-circle-intersections/

        # ChatGPT
        # Calculate the coordinates of the center of the first circle segment
        x1 = a_center.x
        y1 = a_center.y
        x2 = b_center.x
        y2 = b_center.y
        r1 = a_radius
        r2 = b_radius
        start_angle1 = a_start_angle
        end_angle1 = a_stop_angle
        start_angle2 = b_start_angle
        end_angle2 = b_stop_angle

        cx1 = x1 + r1 * math.cos(math.radians(start_angle1 + (end_angle1 - start_angle1) / 2))
        cy1 = y1 + r1 * math.sin(math.radians(start_angle1 + (end_angle1 - start_angle1) / 2))

        # Calculate the coordinates of the center of the second circle segment
        cx2 = x2 + r2 * math.cos(math.radians(start_angle2 + (end_angle2 - start_angle2) / 2))
        cy2 = y2 + r2 * math.sin(math.radians(start_angle2 + (end_angle2 - start_angle2) / 2))

        # Calculate the distance between the centers of the two circle segments
        distance = math.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)

        # Check if the two circle segments are separate or if one is completely contained within the other
        if distance >= r1 + r2 or distance <= abs(r1 - r2):
            return 0, None

        # Calculate the angle between the line connecting the centers and the x-axis for the first circle segment
        theta1 = math.atan2(cy1 - y1, cx1 - x1)

        # Calculate the angle between the line connecting the centers and the x-axis for the second circle segment
        theta2 = math.atan2(cy2 - y2, cx2 - x2)

        # Calculate the angles of the intersection points
        delta_theta = math.acos((r1 ** 2 + distance ** 2 - r2 ** 2) / (2 * r1 * distance))

        # Calculate the intersection points
        i1 = Vector2(x1 + r1 * math.cos(theta1 + delta_theta), y1 + r1 * math.sin(theta1 + delta_theta))
        i2 = Vector2(x1 + r1 * math.cos(theta1 - delta_theta), y1 + r1 * math.sin(theta1 - delta_theta))

        return 2, i2

    @staticmethod
    def intersects_line_circle(p1: Vector2, p2: Vector2, center: Vector2, radius: float, epsilon: float = 0.01) -> (
            int, Vector2, Vector2):
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
            return 0, None, None
        elif det == 0:
            t = -B / (2 * A)
            i1 = Vector2(p1.x + t * dx, p1.y + t * dy)
            return 1, i1, None
        else:
            t1 = ((-B + math.sqrt(det)) / (2 * A))
            t2 = ((-B - math.sqrt(det)) / (2 * A))
            i1 = Vector2(p1.x + t1 * dx, p1.y + t1 * dy)
            i2 = Vector2(p1.x + t2 * dx, p1.y + t2 * dy)
            return 2, i1, i2


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
