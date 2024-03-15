from OpenGL.GL import glBindTexture, glTexParameteri, glTexImage2D, glEnable
from OpenGL.GL import glMatrixMode, glLoadIdentity, glTranslate, glDisable
from OpenGL.GL import glVertex, glBegin, glTexCoord2f, glEnd, glGenTextures
from OpenGL.GL import glFlush, glClearColor, glClear, glBlendFunc
from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT
from OpenGL.GL import GL_TEXTURE_WRAP_T, GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGBA
from OpenGL.GL import GL_UNSIGNED_BYTE, GL_MODELVIEW, GL_QUADS
from OpenGL.GL import GL_PROJECTION, GL_COLOR_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_BUFFER_BIT, GL_BLEND
from OpenGL.GL import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GLU import gluOrtho2D

# from OpenGL.GL import *
# from OpenGL.GLU import *

from PIL.Image import open, FLIP_TOP_BOTTOM
import pygame


class Thingie1:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.sprite = "assets/images/bg1/layers/1.png"
        self.lastsprite = ""
        self.img_data = 0
        self.load()

    def load(self):
        if self.sprite != self.lastsprite:
            im = open(self.sprite)

            # Flip the image vertically (since OpenGL's origin is at bottom-left)
            im = im.transpose(FLIP_TOP_BOTTOM)

            self.width, self.height = im.size[0], im.size[1]
            self.img_data = im.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
            self.lastsprite = self.sprite

            self.Texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.Texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, self.img_data)
            glEnable(GL_TEXTURE_2D)
        else:
            return

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslate(self.x, self.y, 0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.Texture)
        glBegin(GL_QUADS)

        glVertex(0, 0, 0)
        glTexCoord2f(0, 0)
        glVertex(self.width, 0, 0)
        glTexCoord2f(0, 1)
        glVertex(self.width, self.height, 0)
        glTexCoord2f(1, 1)
        glVertex(0, self.height, 0)
        glTexCoord2f(1, 0)

        glEnd()
        glDisable(GL_TEXTURE_2D)
        glFlush()


pygame.init()
pygame.display.set_mode((1920, 1080), pygame.DOUBLEBUF | pygame.OPENGL)

if True:
    glClearColor(*(0, 0, 0, 255))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1920, 1080, 0)
    # Thing1 = Thingie1(200,200)
    Thing2 = Thingie1(0,0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    while True:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        Thing2.load()
        # Thing1.load()

        Thing2.draw()
        # Thing1.draw()
        pygame.display.flip()
