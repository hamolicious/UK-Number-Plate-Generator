import pygame
from pygame.math import Vector3 as Vec, Vector2 as Vec2
from time import time
from math import radians, sqrt
from random import randint, choice
import string
import os

path = 'Plates/'
if not os.path.exists(path):
    os.mkdir(path)
else:
    for file in os.listdir(path):
        os.remove(path + file)

pygame.init()
pygame.font.init()
size = (600, 600)
screen = pygame.display.set_mode(size)
screen.fill([255, 255, 255])
pygame.display.set_icon(screen)
clock, fps = pygame.time.Clock(), 0

delta_time = 0 ; frame_start_time = 0

def get(v):
    return (int(v.x), int(v.y), int(v.z))

def distance_sorter(polygon):
    p = Vec()
    for v in polygon:
        p.x += v[0] ; p.y += v[1] ; p.z += v[2]
    p.x /= 4 ; p.y /= 4 ; p.z /= 4

    return p.distance_to(Vec(300, 300, -50))

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class Plate:
    def __init__(self, px, py, pz, rx, ry, rz, sx, sy, sz):
        self.pos = Vec(px, py, pz)
        self.rotation = Vec(rx, ry, rz)
        self.size = Vec(sx, sy, sz)

        self.load_image()
        self.image_size = Vec2(self.image.get_size())
        self.plate = ''

        self.font = pygame.font.Font('UKNumberPlate.ttf', 290)

        self.verts = [
            Vec(-1, -1, -1),
            Vec(-1, -1, 1),
            Vec(1, -1, 1),
            Vec(1, -1, -1),

            Vec(-1, 1, -1),
            Vec(-1, 1, 1),
            Vec(1, 1, 1),
            Vec(1, 1, -1),
        ]
        self.faces = [
            (3, 7, 6, 2),
            (4, 3, 7, 8),
            (1, 4, 8, 5),
            (2, 1, 5, 6),
            (2, 3, 4, 1),
            (6, 7, 8, 5)
        ]

    def load_image(self):
        self.image = pygame.image.load('blankNumPlate.jpg')

    def generate_number(self):
        no_iqz = string.ascii_uppercase.replace('I', '').replace('Q', '').replace('Z', '')

        plate = choice(no_iqz) + choice(no_iqz)
        plate += choice(string.digits) + choice(string.digits)
        plate += ' '

        plate += choice(no_iqz) + choice(no_iqz) + choice(no_iqz)

        self.plate = plate
        return plate

    def add_number(self):
        lbl = self.font.render(self.generate_number(), True, [0, 0, 0])
        self.image.blit(lbl, (120, 50))

    def display(self, screen):
        self.load_image()
        self.add_number()

        polygon = []

        verts = []
        for v in self.verts:
            cv = Vec(v.x, v.y, v.z)

            cv.x *= self.size.x ; cv.y *= self.size.y ; cv.z *= self.size.z

            cv = cv.rotate_x_rad(radians(self.rotation.x))
            cv = cv.rotate_y_rad(radians(self.rotation.y))
            cv = cv.rotate_z_rad(radians(self.rotation.z))

            cv.x += self.pos.x ; cv.y += self.pos.y ; cv.z += self.pos.z

            verts.append(cv)

        ps = []
        front = None
        for i1, i2, i3, i4 in map(lambda f : tuple([i-1 for i in f]), self.faces):
            polygon = [
                get(verts[i1]),
                get(verts[i2]),
                get(verts[i3]),
                get(verts[i4])
            ]

            if self.faces[2] == (i1+1, i2+1, i3+1, i4+1):
                front = polygon

            ps.append(polygon)

        ps.sort(key=distance_sorter, reverse=True)

        for p in ps:
            check = p
            p = list(map(lambda elem : elem[:2], p))
            pygame.draw.polygon(screen, [150, 150, 0], p)
            pygame.draw.polygon(screen, [0, 0, 0], p, 1)

            if check == front:
                top_left = Vec2(p[0])
                top_right = Vec2(p[1])
                bottom_right = Vec2(p[2])
                bottom_left = Vec2(p[3])

                start = Vec2(p[0])
                end = Vec2(p[1])
                current = Vec2(p[0])

                x_move = (end - start).normalize()
                y_move = (bottom_left - top_left).normalize()

                while True:
                    current += x_move
                    draw = True

                    uv = Vec2(translate(current.x, start.x, end.x, 0, self.image_size.x), translate(current.y, top_left.y, bottom_left.y, 0, self.image_size.y))

                    try:
                        c = self.image.get_at((int(uv.x), int(uv.y)))
                    except IndexError:
                        draw = False

                    if draw:
                        screen.set_at((int(current.x), int(current.y)), c)

                    if abs(current.x - end.x) + abs(current.y - end.y) < 1:
                        start += y_move
                        end += y_move

                        current = Vec2(start.x, start.y)

                    if abs(start.x - bottom_left.x) + abs(start.y - bottom_left.y) < 1:
                        break

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    frame_start_time = time()
    screen.fill(0)

    scale = randint(3, 6) / 10
    plate = Plate(300, 300, 300, randint(-45, 45), randint(-45, 45), 0, 200 * scale, 42 * scale, 5 * scale)
    plate.display(screen)

    pygame.image.save(screen, path + plate.plate.replace(' ', '_').lower() + '.png')

    pygame.display.update()
    clock.tick(fps)
    delta_time = time() - frame_start_time
    pygame.display.set_caption(f'Framerate: {int(clock.get_fps())}')
