import pygame

from OpenGL.GL import *  # noqa: F403
from OpenGL.GLU import gluPerspective, gluLookAt

def tex_coord(x, y, n=4):
    """Calculate texture coordinates for a given (x, y) position in an n x n texture atlas."""
    m = 1.0 / n
    dx, dy = x * m, y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

def loadTexture(name, nearest=False):
    """Load and configure a texture from an image file."""
    textureSurface = pygame.image.load(f'testImgs/{name}.png')
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
    width, height = textureSurface.get_size()

    glEnable(GL_TEXTURE_2D)
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    # Set texture parameters for wrapping and filtering
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    if nearest:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    else:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)
    return texid

class Cube:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    @property
    def tex_coords(self):
        # Top, bottom, side*4
        return [tex_coord(*(0, 0)), tex_coord(*(1, 0))] + [tex_coord(*(2, 0))] * 4

    def verts(self):
        # Return the 8 corner vertices of a cube centered at (x, y, z).
        return (
            (1+self.x, -1+self.y, -1+self.z), (1+self.x, 1+self.y, -1+self.z), (-1+self.x, 1+self.y, -1+self.z), (-1+self.x, -1+self.y, -1+self.z),
            (1+self.x, -1+self.y, 1+self.z), (1+self.x, 1+self.y, 1+self.z), (-1+self.x, -1+self.y, 1+self.z), (-1+self.x, 1+self.y, 1+self.z)
        )

    # Define edges for wireframe rendering
    edges = ((0,1), (0,3), (0,4), (2,1), (2,3), (2,7), (6,3), (6,4), (6,7), (5,1), (5,4), (5,7))
    """A tuple of indices referring to the verts() function, which returns the cube's corner points

    What idx of vertex (in the verts func) goes for each edge of the shape"""

    # Define surfaces for solid rendering
    surfaces = ((0,1,2,3), (3,2,7,6), (6,7,5,4), (4,5,1,0), (1,5,7,2), (4,0,3,6))
    """A tuple of indices referring to the verts() function, which returns the cube's corner points

    What idx of vertex (in the verts func) goes for each solid surface (face)"""

    def render(self):
        """Render a textured cube."""
        glBegin(GL_QUADS)
        block = self.tex_coords
        for i, surface in enumerate(self.surfaces):
            for j, vertex in enumerate(surface):
                glTexCoord2f(block[i][2*j], block[i][2*j+1])
                glVertex3fv(self.verts()[vertex])
        glEnd()
        
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verts()[vertex])
        glEnd()

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
screen = pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

glMatrixMode(GL_PROJECTION)
gluPerspective(45, display[0]/display[1], 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

# Center mouse
displayCenter = [screen.get_size()[i] // 2 for i in range(2)]
pygame.mouse.set_pos(displayCenter)
pygame.mouse.set_visible(False)

objs = [
    Cube(x, y, z) for x, y, z in [(0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2), (-4, 0, 0)]
]

loadTexture('mars')
up_down_angle = 0.0
paused = False
run = True

# Main loop
while run:
    mouseMove = [0, 0]
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_RETURN]):
            run = False
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_PAUSE, pygame.K_p]:
            paused = not paused
            pygame.mouse.set_pos(displayCenter)
        if not paused and event.type == pygame.MOUSEMOTION:
            mouseMove = [event.pos[i] - displayCenter[i] for i in range(2)]
            pygame.mouse.set_pos(displayCenter)

    if not paused:
        keypress = pygame.key.get_pressed()
        glLoadIdentity()
        up_down_angle += mouseMove[1] * 0.1
        glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        glPushMatrix()
        glLoadIdentity()

        # Movement controls
        move_speed = 0.1
        if keypress[pygame.K_w]:
            glTranslatef(0, 0, move_speed)
        if keypress[pygame.K_s]:
            glTranslatef(0, 0, -move_speed)
        if keypress[pygame.K_d]:
            glTranslatef(-move_speed, 0, 0)
        if keypress[pygame.K_a]:
            glTranslatef(move_speed, 0, 0)
        if keypress[pygame.K_LSHIFT]:
            glTranslatef(0, 0.5, 0)
        if keypress[pygame.K_SPACE]:
            glTranslatef(0, -0.5, 0)

        # Apply rotation
        glRotatef(mouseMove[0] * 0.1, 0.0, 1.0, 0.0)
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()
        glMultMatrixf(viewMatrix)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        
        # Render cubes
        for o in objs:
            o.render()
        
        glDisable(GL_TEXTURE_2D)

        glColor4f(0.5, 0.5, 0.5, 1)
        glBegin(GL_QUADS)
        glVertex3f(-10, -10, -2)
        glVertex3f(10, -10, -2)
        glVertex3f(10, 10, -2)
        glVertex3f(-10, 10, -2)
        glEnd()

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

pygame.quit()
