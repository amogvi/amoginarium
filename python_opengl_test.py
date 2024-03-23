import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT
from OpenGL.GL import *
from OpenGL.GLUT import *
from pygame.font import Font

def text_to_texture(text, font, color):
    rendered_text = font.render(text, True, color)
    width, height = rendered_text.get_size()
    image = pygame.image.tostring(rendered_text, "RGBA", True)
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    return texture_id, width, height

def render_text(texture_id, x, y, width, height):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(x, y)
    glTexCoord2f(1, 1); glVertex2f(x + width, y)
    glTexCoord2f(1, 0); glVertex2f(x + width, y + height)
    glTexCoord2f(0, 0); glVertex2f(x, y + height)
    glEnd()
    
    glDisable(GL_BLEND)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    font = Font(None, 48)
    text = "Hello, World!"
    color = (255, 255, 255)
    
    texture_id, width, height = text_to_texture(text, font, color)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, display[0], 0, display[1], -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        glColor3f(1, 1, 1)
        render_text(texture_id, 100, 100, width, height)
        
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
