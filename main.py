import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

def tex_coord(x, y, n=4):
    """ Return the bounding vertices of the texture square."""
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side."""
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = [
        (top),
        (bottom),
        (side),
        (side),
        (side),
        (side),
    ]
    """result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)"""
    return result

#block type names and location on template go here
BLOCK1 = tex_coords((3, 0), (3, 0), (3, 0))

def verts(x, y, z, n):
    vertices = (
        (1+(2*x), -1+(2*y), -1+(2*z)),
        (1+(2*x), 1+(2*y), -1+(2*z)),
        (-1+(2*x), 1+(2*y), -1+(2*z)),
        (-1+(2*x), -1+(2*y), -1+(2*z)),
        (1+(2*x), -1+(2*y), 1+(2*z)),
        (1+(2*x), 1+(2*y), 1+(2*z)),
        (-1+(2*x), -1+(2*y), 1+(2*z)),
        (-1+(2*x), 1+(2*y), 1+(2*z))
        )
    return(vertices)

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )


forced = False
def Cube(vx,vy,vz,block):
    if not forced:
        glBegin(GL_QUADS)
        y = 0
        for surface in surfaces:
            x = 0
            y+=1
            for vertex in surface:
                x+=1
                glTexCoord2f(block[y-1][2*(x-1)], block[y-1][(2*x)-1])
                #print(block[y-1][2*(x-1)], block[y-1][(2*x)-1])
                glVertex3fv(verts(vx,vy,vz,1)[vertex])
        glEnd()
        
        
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(verts(vx,vy,vz,1)[vertex])
        glEnd()
    else:
        texX = 0.75
        texY = 0.25
        glBegin(GL_QUADS)
        glTexCoord2f(0.0+texX, 0.0)
        glVertex3f(-1.0, -1.0,  1.0)
        glTexCoord2f(0.25+texX, 0.0)
        glVertex3f(1.0, -1.0,  1.0)
        glTexCoord2f(0.25+texX, 0.25)
        glVertex3f(1.0,  1.0,  1.0)
        glTexCoord2f(0.0+texX, 0.25)
        glVertex3f(-1.0,  1.0,  1.0)
        glEnd()

def loadTexture():
    textureSurface = pygame.image.load('testImgs/mars.png')
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
    width = textureSurface.get_width()
    height = textureSurface.get_height()

    glColor3f(0.5, 0.5, 0.5)
    glEnable(GL_TEXTURE_2D)
    texid = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    return texid

pygame.init()
display = (800, 600)
screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

sphere = gluNewQuadric() 

glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

# init mouse movement and center mouse on screen
displayCenter = [screen.get_size()[i] // 2 for i in range(2)]
mouseMove = [0, 0]
pygame.mouse.set_pos(displayCenter)

loadTexture()

up_down_angle = 0.0
paused = False
run = True
pygame.mouse.set_visible(False)
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                run = False
            if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
                paused = not paused
                pygame.mouse.set_pos(displayCenter) 
        if not paused: 
            if event.type == pygame.MOUSEMOTION:
                mouseMove = [event.pos[i] - displayCenter[i] for i in range(2)]
            pygame.mouse.set_pos(displayCenter)    

    if not paused:
        # get keys
        keypress = pygame.key.get_pressed()
    
        # init model view matrix
        glLoadIdentity()

        # apply the look up and down
        up_down_angle += mouseMove[1]*0.1
        glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        # init the view matrix
        glPushMatrix()
        glLoadIdentity()

        # apply the movment 
        if keypress[pygame.K_w]:
            glTranslatef(0,0,0.1)
        if keypress[pygame.K_s]:
            glTranslatef(0,0,-0.1)
        if keypress[pygame.K_d]:
            glTranslatef(-0.1,0,0)
        if keypress[pygame.K_a]:
            glTranslatef(0.1,0,0)
        if keypress[pygame.K_LSHIFT]:
            glTranslatef(0,0.5,0)
        if keypress[pygame.K_SPACE]:
            glTranslatef(0,-0.5,0)

        # apply the left and right rotation
        glRotatef(mouseMove[0]*0.1, 0.0, 1.0, 0.0)

        # multiply the current matrix by the get the new view matrix and store the final view matrix 
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        # apply view matrix
        glPopMatrix()
        glMultMatrixf(viewMatrix)

        #glLightfv(GL_LIGHT0, GL_POSITION, [1, -1, 1, 0])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glPushMatrix()


        glEnable(GL_TEXTURE_2D)
        Cube(0,0,0,BLOCK1)
        Cube(1,0,0,BLOCK1)
        Cube(0,1,0,BLOCK1)
        Cube(0,0,1,BLOCK1)
        Cube(-2,0,0,BLOCK1)
        
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
