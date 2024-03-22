"""
_opengl.py
21. March 2024

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
import numpy as np
import os

from ..logic import Vec2, Color, convert_coord
from ._base_renderer import BaseRenderer
from ..base._linked import global_vars


class OpenGLRenderer(BaseRenderer):
    @staticmethod
    def set_color(color):
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

    @staticmethod
    def load_texture(filename, size, mirror=""):
        # check if file exists
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"failed to load texture \"{filename}\"")

        # for debugging
        loading_texture = f"{filename}, mirror: \"{mirror}\""
        ic(loading_texture)

        im = Image.open(filename)

        if size is not None:
            im = im.resize(convert_coord(size))

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
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data
        )
        glEnable(GL_TEXTURE_2D)

        return texture_id, (width, height)

    @staticmethod
    def draw_textured_quad(texture_id, pos, size, convert_global=True):
        pos = convert_coord(pos, Vec2)
        size = convert_coord(size, Vec2)

        # convert to screen realtive coords and size
        if convert_global:
            pos = global_vars.translate_screen_coord(pos)
            size = global_vars.translate_scale(size)

        # reset color
        glColor3f(1, 1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslate(*pos.xy, 0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glBegin(GL_QUADS)

        # draw rectangle and texture
        glVertex(0, 0, 0)
        glTexCoord2f(0, 0)
        glVertex(size.x, 0, 0)
        glTexCoord2f(0, 1)
        glVertex(size.x, size.y, 0)
        glTexCoord2f(1, 1)
        glVertex(0, size.y, 0)
        glTexCoord2f(1, 0)

        glEnd()
        glDisable(GL_TEXTURE_2D)
        glFlush()

    def draw_circle(
            self,
            center,
            radius,
            num_segments,
            color,
            convert_global=True
    ):
        center = convert_coord(center, Vec2)

        # convert to screen realtive coords and size
        if convert_global:
            center = global_vars.translate_screen_coord(center)
            radius = global_vars.translate_scale(radius)

        glLoadIdentity()  # reset previous glTranslate statements
        glTranslate(center.x, center.y, 0)

        self.set_color(color)

        glBegin(GL_POLYGON)

        for i in range(num_segments):
            cosine = radius * np.cos(i*2*np.pi / num_segments)
            sine = radius * np.sin(i*2*np.pi / num_segments)
            glVertex2f(cosine, sine)

        glEnd()

    def draw_rect(
            self,
            start,
            size,
            color,
            convert_global=True
    ):
        start = convert_coord(start, Vec2)
        size = convert_coord(size, Vec2)

        if convert_global:
            start = global_vars.translate_screen_coord(start)
            size = global_vars.translate_scale(size)

        glLoadIdentity()  # reset previous glTranslate statements
        glTranslate(start.x, start.y, 0)

        self.set_color(color)

        glBegin(GL_POLYGON)
        glVertex2f(0, 0)
        glVertex2f(size.x, 0)
        glVertex2f(size.x, size.y)
        glVertex2f(0, size.y)
        glEnd()

    def draw_dashed_circle(
            self,
            center,
            radius,
            num_segments,
            color,
            thickness=1,
            convert_global=True
    ):
        center = convert_coord(center, Vec2)

        if convert_global:
            center = global_vars.translate_screen_coord(center)
            radius = global_vars.translate_scale(radius)

        glLoadIdentity()
        glTranslate(center.x, center.y, 0)

        self.set_color(color)

        for i in range(num_segments):
            i1 = i * 2
            i2 = i1 + 1

            cosine1 = np.cos(i1*2*np.pi / num_segments)
            sine1 = np.sin(i1*2*np.pi / num_segments)

            cosine2 = np.cos(i2*2*np.pi / num_segments)
            sine2 = np.sin(i2*2*np.pi / num_segments)

            glBegin(GL_POLYGON)
            glVertex2f(cosine1 * radius, sine1 * radius)
            glVertex2f(
                cosine1 * (radius + thickness),
                sine1 * (radius + thickness)
            )
            glVertex2f(
                cosine2 * (radius + thickness),
                sine2 * (radius + thickness)
            )
            glVertex2f(cosine2 * radius, sine2 * radius)
            glEnd()

    def draw_line(
            self,
            start,
            end,
            color,
            global_position=True,
            convert_global=True
    ):
        """
        draw a simple line
        """
        start = convert_coord(start, Vec2)
        end = convert_coord(end, Vec2)

        if convert_global:
            start = global_vars.translate_screen_coord(start)
            end = global_vars.translate_scale(end)

        if global_position:
            glLoadIdentity()  # reset previous glTranslate statements

        self.set_color(color)

        glBegin(GL_LINES)
        glVertex2f(*start.xy)
        glVertex2f(*end.xy)
        glEnd()
