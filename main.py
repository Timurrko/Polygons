import time

import pygame
from numpy import cos, sin, pi, arange
from numba import njit


class Camera:
    def __init__(self, x, y, view_angle, width, height, direction):
        self.x = x
        self.y = y
        self.view_angle = view_angle
        self.width = width
        self.height = height
        self.d_angle = self.view_angle / self.width
        self.direction = direction
        self.rotation_speed = 1000
        self.movement_speed = 2
        self.no_forward = False
        self.no_backward = False

    def rotate_right(self, n=1.0):
        self.direction = (self.direction - n * self.d_angle * self.rotation_speed) % (2 * pi)

    def rotate_left(self, n=1.0):
        self.direction = (self.direction + n * self.d_angle * self.rotation_speed) % (2 * pi)

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
        right_border = self.direction - self.view_angle / 2
        for i in range(self.width):
            x = self.width - i - 1
            current_angle = right_border + i * self.d_angle
            color = BLACK
            dist = -2
            for x1, y1, x2, y2, c_color in polygons:
                c_dist = distance(self.x, self.y, current_angle, x1, y1, x2, y2)
                if c_dist is not None:
                    if 0 > c_dist >= -0.5:
                        self.no_backward = True
                    elif 0 <= c_dist and (c_dist < dist or dist < 0):
                        dist = c_dist
                        color = c_color
            if dist > 0:
                ko = max(1, dist)
                color = tuple(round(i / ko) for i in color)
                half_height = self.height / 2
                pygame.draw.line(screen, color, (x, half_height - 200 / ko), (x, half_height + 200 / ko), 3)
                if 0 <= dist <= 0.5:
                    self.no_forward = True
            elif dist == 0:
                screen.fill(color)


# Поворот точки против часовой на угол
@njit
def rotate(x, y, h_angle):
    x1 = x * cos(h_angle) - y * sin(h_angle)
    y1 = y * cos(h_angle) + x * sin(h_angle)
    return x1, y1


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
            return x1 + dx * abs(y1 / dy)
    return None


WIDTH = 600
HEIGHT = 401
FPS = 30

# Задаём цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# polygons = [(5 * cos(i), 5 * sin(i), 5 * cos(i + pi/32), 5 * sin(i + pi/32), WHITE) for i in arange(0, 3 * pi / 2,
# pi/32)]
polygons = [(-3, 3, -3, -13, RED), (-3, 3, 13, 3, RED), (13, 3, 13, -1, RED), (13, -1, 13, -3, GREEN),
            (13, -3, 13, -13, RED), (13, -13, -3, -13, RED), (-3, -3, 3, -3, WHITE), (3, 3, 3, 0.5, BLUE),
            (3, -9, 3, -0.5, BLUE), (5, 3, 5, -9, BLUE), (-1, -5, 1, -5, WHITE), (1, -5, 1, -7, WHITE),
            (-1, -7, 1, -7, WHITE), (-1, -7, -1, -11, WHITE), (-1, -11, 1, -11, WHITE), (1, -11, 1, -9, WHITE),
            (3, -11, 9, -11, WHITE), (9, -11, 9, -13, WHITE), (11, -13, 11, -9, WHITE), (7, -9, 9, -9, WHITE),
            (9, -9, 7, -7, WHITE), (7, -6, 7, -9, WHITE), (9, -6, 11, -6, WHITE), (11, -6, 11, -7, WHITE),
            (11, -7, 9, -7, WHITE), (9, -7, 9, -6, WHITE), (9, -4, 7, -4, WHITE), (7, -4, 7, 0, WHITE),
            (7, 0, 9, -2, WHITE), (13, -3, 10, -3, WHITE), (13, -1, 10, -1, WHITE), (7, 1, 11, 1, WHITE)]
cam = Camera(0, 0, pi / 3, WIDTH, HEIGHT, 0)

# Создаем игру и окно
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)
text = font.render("Найдите выход", True, GREEN)
# Цикл игры
running = True

next_time = time.time()
while running:
    previous_time = next_time
    next_time = time.time()
    d_time = next_time - previous_time
    # if d_time > 0.02:
    #     print(d_time)
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
    if 10 <= cam.x <= 13 and -3 <= cam.y <= -1 and - pi / 6 <= cam.direction <= pi / 6:
        text = font.render("Выход найден!", True, GREEN)
    screen.blit(text, [232, 250])

    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()
