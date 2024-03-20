"""
_utils.py
17. March 2024

a few functions for rendering

Author:
Nilusink
"""
from OpenGL.GL import glTranslate, glMatrixMode, glLoadIdentity, glTexCoord2f
from OpenGL.GL import glBindTexture, glTexParameteri, glTexImage2D, glEnable
from OpenGL.GL import glGenTextures, glVertex2f, glColor3f, glColor4f, glEnd
from OpenGL.GL import glDisable, glBegin, glVertex, glFlush
from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT, GL_LINES
from OpenGL.GL import GL_TEXTURE_WRAP_T, GL_TEXTURE_MIN_FILTER, GL_POLYGON
from OpenGL.GL import GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGBA, GL_QUADS
from OpenGL.GL import GL_UNSIGNED_BYTE, GL_MODELVIEW
from icecream import ic
from PIL import Image
import typing as tp
import numpy as np
import os

from ..logic import Vec2, Color


type Color3 = tuple[float, float, float]
type Color4 = tuple[float, float, float, float]
type tColor = Color3 | Color4


def set_color(color: Color | tColor) -> None:
    """
    set gColor
    """
    # color as Color class
    if isinstance(color, Color):
        if color.is_rgba:
            glColor4f(*color.rgba1)

        else:
            glColor3f(*color.rgb1)

    # color as tuple
    else:
        if len(color) == 3:
            glColor3f(*color)

        elif len(color) == 4:
            glColor4f(*color)

        else:
            raise ValueError("Invalid color: ", color)


def load_texture(
    filename: str,
    size: tuple[int, int] | None = None,
    mirror: tp.Literal["x", "y", "xy"] = "",
) -> tuple[int, tuple[int]]:
    """
    load an image texture

    :returns: texture_id, (width, height)
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"failed to load texture \"{filename}\"")

    # for debugging
    loading_texture = f"{filename}, mirror: \"{mirror}\""
    ic(loading_texture)

    im = Image.open(filename)

    if size is not None:
        im = im.resize(size)

    if "x" in mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)

    # Flip the image vertically (since OpenGL's origin is at bottom-left)
    if "y" not in mirror:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)

    width, height = im.size[0], im.size[1]
    img_data = im.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glEnable(GL_TEXTURE_2D)

    return texture_id, (width, height)


def draw_textured_quad(
    texture_id: int,
    x, y,
    width, height
) -> None:
    # reset color
    glColor3f(1, 1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslate(x, y, 0)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)

    glVertex(0, 0, 0)
    glTexCoord2f(0, 0)
    glVertex(width, 0, 0)
    glTexCoord2f(0, 1)
    glVertex(width, height, 0)
    glTexCoord2f(1, 1)
    glVertex(0, height, 0)
    glTexCoord2f(1, 0)

    glEnd()
    glDisable(GL_TEXTURE_2D)
    glFlush()


def draw_circle(
    center: Vec2,
    radius: float,
    num_segments: int,
    color: Color | tColor
) -> None:
    """
    draw a circle
    """
    glLoadIdentity()  # reset previous glTranslate statements
    glTranslate(center.x, center.y, 0)

    set_color(color)

    glBegin(GL_POLYGON)

    for i in range(num_segments):
        cosine = radius * np.cos(i*2*np.pi / num_segments)
        sine = radius * np.sin(i*2*np.pi / num_segments)
        glVertex2f(cosine, sine)

    glEnd()


def draw_rect(
    start: Vec2,
    size: Vec2,
    color: Color | tColor
) -> None:
    """
    draw a rectangle
    """
    glLoadIdentity()  # reset previous glTranslate statements
    glTranslate(start.x, start.y, 0)

    set_color(color)

    glBegin(GL_POLYGON)
    glVertex2f(0, 0)
    glVertex2f(size.x, 0)
    glVertex2f(size.x, size.y)
    glVertex2f(0, size.y)
    glEnd()


def draw_line(
    start: Vec2,
    end: Vec2,
    color: Color | tColor,
    global_position: bool = True
) -> None:
    """
    draw a simple line
    """
    if global_position:
        glLoadIdentity()  # reset previous glTranslate statements

    set_color(color)

    glBegin(GL_LINES)
    glVertex2f(*start.xy)
    glVertex2f(*end.xy)
    glEnd()


def draw_dashed_circle(
    center: Vec2,
    radius: float,
    num_segments: int,
    color: Color | tColor,
    thickness: int = 1
) -> None:
    glLoadIdentity()
    glTranslate(center.x, center.y, 0)

    set_color(color)

    for i in range(num_segments):
        i1 = i * 2
        i2 = i1 + 1

        cosine1 = np.cos(i1*2*np.pi / num_segments)
        sine1 = np.sin(i1*2*np.pi / num_segments)

        cosine2 = np.cos(i2*2*np.pi / num_segments)
        sine2 = np.sin(i2*2*np.pi / num_segments)

        # draw_line(
        #     Vec2.from_cartesian(cosine1, sine1),
        #     Vec2.from_cartesian(cosine2, sine2),
        #     color
        # )

        # glBegin(GL_LINES)
        # glVertex2f(cosine1, sine1)
        # glVertex2f(cosine2, sine2)
        # glEnd()

        glBegin(GL_POLYGON)
        glVertex2f(cosine1 * radius, sine1 * radius)
        glVertex2f(cosine1 * (radius + thickness), sine1*(radius + thickness))
        glVertex2f(cosine2 * (radius + thickness), sine2*(radius + thickness))
        glVertex2f(cosine2 * radius, sine2 * radius)
        glEnd()
