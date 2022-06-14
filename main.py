import time

import pygame
from numpy import cos, sin, array, pi
from functools import cache
from numba import njit, prange


class Camera:
    def __init__(self, x, y, view_angle, width, height, direction):
        self.x = x
        self.y = y
        self.view_angle = view_angle
        self.width = width
        self.height = height
        self.right_border = direction - view_angle / 2
        self.d_angle = self.view_angle / self.width
        self.direction = direction
        self.rotation_speed = 1000
        self.movement_speed = 2
        self.no_forward = False
        self.no_backward = False

    def rotate_right(self, n=1.0):
        self.right_border -= n * self.d_angle * self.rotation_speed
        self.direction -= n * self.d_angle * self.rotation_speed

    def rotate_left(self, n=1.0):
        self.right_border += n * self.d_angle * self.rotation_speed
        self.direction += n * self.d_angle * self.rotation_speed

    def move_forward(self, n=1.0):
        if not self.no_forward:
            self.y += sin(self.direction) * n * self.movement_speed
            self.x += cos(self.direction) * n * self.movement_speed

    def move_backward(self, n=1.0):
        if not self.no_backward:
            self.y -= sin(self.direction) * n * self.movement_speed
            self.x -= cos(self.direction) * n * self.movement_speed

    def render(self, screen, polygons):
        self.no_forward = False
        self.no_backward = False
        for i in range(self.width):
            x = self.width - i - 1
            current_angle = self.right_border + i * self.d_angle
            color = BLACK
            dist = -2
            for x1, y1, x2, y2, c_color in polygons:
                c_dist = distance(self.x, self.y, current_angle, x1, y1, x2, y2)
                if c_dist is not None:
                    if 0 >= c_dist >= -0.5:
                        self.no_backward = True
                    if 0 <= c_dist and (c_dist < dist or dist < 0):
                        dist = c_dist
                        color = c_color
            if dist > 0:
                color = tuple(round(i / max(1, dist ** 0.7)) for i in color)
                pygame.draw.line(screen, color, (x, self.height / 2 - 200 / dist), (x, self.height / 2 + 200 / dist), 3)
                if 0 <= dist <= 0.5:
                    self.no_forward = True
            elif dist == 0:
                screen.fill(color)


# Поворот точки против часовой на угол
@njit
def rotate(x, y, h_angle):
    # x, y = (sum(i) for i in array([x, y]) * array([[cos(h_angle), -sin(h_angle)], [sin(h_angle), cos(h_angle)]]))
    x1 = x * cos(h_angle) - y * sin(h_angle)
    y1 = y * cos(h_angle) + x * sin(h_angle)
    return x1, y1


@cache
@njit
def distance(x_, y_, angle_, x1, y1, x2, y2):
    x1 -= x_
    y1 -= y_
    x2 -= x_
    y2 -= y_
    x1, y1 = rotate(x1, y1, -angle_)
    x2, y2 = rotate(x2, y2, -angle_)
    if y1 * y2 <= 0:
        if x1 == x2:
            return x1
        elif y1 == y2:
            return min(x1, x2)
        else:
            dx = x2 - x1
            dy = y2 - y1
            return x1 + dx * (abs(y1) / abs(dy))
    return None


WIDTH = 600
HEIGHT = 401
FPS = 100

# Задаём цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

polygons = [(2, 0, 100, 0, WHITE), (0, -2, 0, -4, GREEN), (-4, 4, 4, 4, WHITE), (4, 4, 4, -4, GREEN),
            (4, -4, -4, -4, BLUE), (-4, -4, -4, 4, RED)]
cam = Camera(0, 0, pi / 3, WIDTH, HEIGHT, 0)

# Создаем игру и окно
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D")
clock = pygame.time.Clock()

# Цикл игры
running = True

next_time = time.time()
while running:
    previous_time = next_time
    next_time = time.time()
    d_time = next_time - previous_time
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pressed_keys = list(pygame.key.get_pressed())
    if pressed_keys[80]:
        cam.rotate_left(d_time)
    elif pressed_keys[79]:
        cam.rotate_right(d_time)
    if pressed_keys[82]:
        cam.move_forward(d_time)
    elif pressed_keys[81]:
        cam.move_backward(d_time)
    # Обновление
    screen.fill(BLACK)
    # Рендеринг
    cam.render(screen, polygons)

    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()
