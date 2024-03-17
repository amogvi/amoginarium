"""
_utils.py
17. March 2024

a few functions for rendering

Author:
Nilusink
"""
from OpenGL.GL import glBindTexture, glTexParameteri, glTexImage2D, glEnable
from OpenGL.GL import glGenTextures, glVertex2f, glColor3f, glColor4f
from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT
from OpenGL.GL import GL_TEXTURE_WRAP_T, GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGBA
from OpenGL.GL import GL_UNSIGNED_BYTE, GL_POLYGON
from OpenGL.GL import glTranslate, glDisable, glEnd
from OpenGL.GL import glMatrixMode, glLoadIdentity, glBegin, glTexCoord2f
from OpenGL.GL import glVertex, glFlush
from OpenGL.GL import GL_MODELVIEW, GL_QUADS
from icecream import ic
from PIL import Image
import typing as tp
import numpy as np
import os

from ..logic import Vec2


type Color3 = tuple[float, float, float]
type Color4 = tuple[float, float, float, float]
type Color = Color3 | Color4


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
    color: Color
) -> None:
    """
    draw a circle
    """
    glLoadIdentity()  # reset previous glTranslate statements
    glTranslate(center.x, center.y, 0)

    if len(color) == 3:
        glColor3f(*color)

    elif len(color) == 4:
        glColor4f(*color)

    else:
        raise ValueError("Invalid color: ", color)

    glBegin(GL_POLYGON)

    for i in range(100):
        cosine = radius * np.cos(i*2*np.pi / num_segments)
        sine = radius * np.sin(i*2*np.pi / num_segments)
        # ic(center.xy, cosine, sine)
        glVertex2f(cosine, sine)

    glEnd()


def draw_rect(
    start: Vec2,
    size: Vec2,
    color: Color
) -> None:
    """
    draw a rectangle
    """
    glLoadIdentity()  # reset previous glTranslate statements
    glTranslate(start.x, start.y, 0)

    if len(color) == 3:
        glColor3f(*color)

    elif len(color) == 4:
        glColor4f(*color)

    else:
        raise ValueError("Invalid color: ", color)

    glBegin(GL_POLYGON)
    glVertex2f(0, 0)
    glVertex2f(size.x, 0)
    glVertex2f(size.x, size.y)
    glVertex2f(0, size.y)
    glEnd()
