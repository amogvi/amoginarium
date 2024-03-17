"""
_calculations.py
17. March 2024

defines a functions that perform some kind of calculation

Author:
Nilusink
"""
from contextlib import suppress
from ._vectors import Vec2
import math as m


def calculate_launch_angle(
    position_delta: Vec2,
    target_velocity: Vec2,
    launch_speed: float,
    recalculate: int = 10,
    aim_type: str = "low"
) -> Vec2:
    """
    :param position_delta: the position delta between cannon and target
    :param target_velocity: the current velocity of the target, pass empty Vec3 if no velocity is known
    :param launch_speed: the projectile muzzle speed
    :param recalculate: how often the position is being recalculated, basically a precision parameter
    :param aim_type: either "high" - "h" or "low" - "l". Defines if the lower or higher curve should be aimed for
    :return: where to aim
    """
    if recalculate < 0:
        recalculate = 0

    aim_type = max if aim_type.lower() in ("high", "h") else min

    # constants
    g = 9.81

    # approximate where the target will be (this is not an exact method!!!)
    a_time = position_delta.length / launch_speed
    a_pos = position_delta + target_velocity * a_time

    solutions: list[float] = []
    for _ in range(recalculate + 1):
        solutions.clear()

        # calculate possible launch angles
        x, y = a_pos.xy

        a = (g / 2) * (x / launch_speed) ** 2
        b = a + y

        with suppress(ValueError):
            z1 = (x + m.sqrt(x ** 2 - 4 * a * b)) / (2 * a)
            solutions.append(m.atan(z1))

        with suppress(ValueError):
            z2 = (x - m.sqrt(x ** 2 - 4 * a * b)) / (2 * a)
            solutions.append(m.atan(z2))

        if not solutions:
            raise ValueError("no possible launch angle found")

        # recalculate the probable position of the target using the now
        # calculated angle
        angle = aim_type(solutions)
        v_x = launch_speed * m.cos(angle)

        a_time = x / v_x
        a_pos = position_delta + target_velocity * a_time

    return Vec2.from_polar(aim_type(solutions), 1)
