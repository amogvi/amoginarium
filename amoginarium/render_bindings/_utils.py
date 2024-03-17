"""
_utils.py
17. March 2024

a few functions for rendering

Author:
Nilusink
"""
from OpenGL.GL import glBindTexture, glTexParameteri, glTexImage2D, glEnable
from OpenGL.GL import glGenTextures
from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT
from OpenGL.GL import GL_TEXTURE_WRAP_T, GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGBA
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glTranslate, glDisable, glEnd
from OpenGL.GL import glMatrixMode, glLoadIdentity, glBegin, glTexCoord2f
from OpenGL.GL import glVertex, glFlush
from OpenGL.GL import GL_MODELVIEW, GL_QUADS
from PIL import Image

import os


def load_texture(
    filename: str,
    size: tuple[int, int] | None = None
) -> tuple[int, tuple[int]]:
    """
    load an image texture

    :returns: texture_id, (width, height)
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"failed to load texture \"{filename}\"")

    im = Image.open(filename)

    if size is not None:
        im = im.resize(size)

    # Flip the image vertically (since OpenGL's origin is at bottom-left)
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


# from OpenGL.GL import glEnable, glBlendFunc, glTexParameteri, glBegin, glGenTextures, glPixelStorei, glBindTexture, glTexParameter
# from OpenGL.GL import glDisable, glTexImage2D, glPushMatrix, glTranslatef, glMatrixMode, glLoadIdentity, glTranslate, glScale, glVertex
# from OpenGL.GL import glTexCoord2f, glVertex2f, glEnd, glPopMatrix, glColor3f, glTexCoord
# from OpenGL.GL import GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_NEAREST, GL_UNPACK_ALIGNMENT, GL_RGBA, GL_PROJECTION
# from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_DEPTH_TEST, GL_CULL_FACE, GL_LIGHTING
# from OpenGL.GL import GL_TEXTURE_MIN_FILTER, GL_LINEAR, GL_RED
# from OpenGL.GL import GL_UNSIGNED_BYTE, GL_QUADS
# # from freetype import Face

# import pygame as pg

# # from icecream import ic


# type Color = tuple[float, float, float] | tuple[float, float, float, float]


# def render_text(
#     text: str,
#     x: int,
#     y: int,
#     font: pg.font.Font
# ) -> None:
#     img = font.render("Hello", True, (255, 255, 255))
#     w, h = img.get_size()

#     texture = glGenTextures(1)
#     glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
#     glBindTexture(GL_TEXTURE_2D, texture)
#     glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
#     glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#     data = pg.image.tostring(img, "RGBA", 1)
#     glTexImage2D(GL_TEXTURE_2D, 0, 4, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

#     glBindTexture(GL_TEXTURE_2D, texture)
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     glTranslate(-1, -1, 0)
#     glScale(2 / 600, 2 / 400, 1)
#     glEnable(GL_BLEND)
#     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#     glEnable(GL_TEXTURE_2D)
#     glDisable(GL_DEPTH_TEST)
#     glDisable(GL_CULL_FACE)
#     glDisable(GL_LIGHTING)
#     glBegin(GL_QUADS)
#     x0, y0 = 10, 10
#     w, h = img.get_size()
#     for dx, dy in [(0, 0), (0, 1), (1, 1), (1, 0)]:
#         glVertex(x0 + dx * w, y0 + dy * h, 0)
#         glTexCoord(dy, 1 - dx)
#     glEnd()

# # def render_text(
# #     text: str,
# #     x: int,
# #     y: int,
# #     color: tuple[float, float, float]
# # ) -> None:
# #     glColor3f(*color)

# #     glEnable(GL_BLEND)
# #     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
# #     glEnable(GL_TEXTURE_2D)
# #     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
# #     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

# #     for char in text:
# #         if char != ' ':
# #             font.load_char(char)
# #             glyph = font.glyph
# #             bitmap = glyph.bitmap
# #             width, height = glyph.bitmap.width, glyph.bitmap.rows

# #             glTexImage2D(
# #                 GL_TEXTURE_2D,
# #                 0,
# #                 GL_RED,
# #                 width, height,
# #                 0,
# #                 GL_RED,
# #                 GL_UNSIGNED_BYTE,
# #                 bitmap.buffer
# #             )

# #             glPushMatrix()
# #             glTranslatef(x + glyph.bitmap_left, y - glyph.bitmap_top, 0)

# #             glBegin(GL_QUADS)
# #             glTexCoord2f(0, 0); glVertex2f(0, 0)
# #             glTexCoord2f(1, 0); glVertex2f(width, 0)
# #             glTexCoord2f(1, 1); glVertex2f(width, height)
# #             glTexCoord2f(0, 1); glVertex2f(0, height)
# #             glEnd()

# #             glPopMatrix()

# #         x += glyph.advance.x // 64

# #     glDisable(GL_BLEND)
# #     glDisable(GL_TEXTURE_2D)
