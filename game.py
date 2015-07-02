from __future__ import print_function, division

from operator import itemgetter
import sys
import pygame
import random
from pygame.locals import *

GREEN = 0, 255, 0
WHITE = 255, 255, 255
BLACK = 0, 0, 0
YELLOW = 255, 255, 0
BLUE = 0, 0, 255

BIRD_SIZE = 30
SCREEN_SIZE = 600
TUBE_HOLE_HEIGH = 200
TUBE_WIDTH = 100
MIN_TUBE_HEIGH = 20
BETWEEN_TUBE = 225
TICK = 60
INV_TICK = 1/60

GRAVITY_ACC = 1500
SPEED_ON_JUMP = -600

X_VEL = -150

BIRD_X = SCREEN_SIZE / 2
BIRD_HALF = BIRD_SIZE / 2

class State:
    def __init__(self, y=SCREEN_SIZE/2, yvel=0, tubes=None):
        if tubes is None:
            tubes = [(SCREEN_SIZE*1.5, _generate_tube_hole(), False),
                     (SCREEN_SIZE*1.5 + TUBE_WIDTH + BETWEEN_TUBE, _generate_tube_hole(), False),
                     (SCREEN_SIZE*1.5 + TUBE_WIDTH*2 + BETWEEN_TUBE * 2, _generate_tube_hole(), False)]
        self.y = y
        self.speed = yvel
        self.tubes = tubes


def draw(state):
    for tube_x, tube_h, tube_passed in state.tubes:
        pygame.draw.rect(DISPLAY, GREEN, (tube_x, 0, TUBE_WIDTH, tube_h))
        x1 = tube_h + TUBE_HOLE_HEIGH
        pygame.draw.rect(DISPLAY, GREEN, (tube_x, x1, TUBE_WIDTH, SCREEN_SIZE-x1))

    pygame.draw.rect(DISPLAY, BLUE, ((SCREEN_SIZE - BIRD_SIZE) / 2, state.y - BIRD_SIZE / 2,
                                     BIRD_SIZE, BIRD_SIZE))
    pygame.display.update()


def _wrecked_into_tube(bird_y, tubes):
    center = SCREEN_SIZE / 2
    for tube_x, tube_h, tube_passed in tubes:
        if tube_x - BIRD_HALF < center < tube_x + BIRD_HALF + TUBE_WIDTH:
            if bird_y - BIRD_HALF < tube_h or bird_y + BIRD_HALF > tube_h + TUBE_HOLE_HEIGH:
                return True
    return False


def _generate_tube_hole():
    return random.uniform(MIN_TUBE_HEIGH, SCREEN_SIZE-TUBE_HOLE_HEIGH-2*MIN_TUBE_HEIGH)


def advance(state, action, dt):
    """ Return a new state and a reward tuple
    """
    if action:
        speed = SPEED_ON_JUMP
    else:
        speed = state.speed + GRAVITY_ACC * dt
    y = state.y + state.speed * dt

    reward = 0
    new_tubes = []
    for tube_x, tube_h, tube_passed in state.tubes[::-1]:
        new_tube_x = tube_x + X_VEL * dt
        while new_tube_x < -TUBE_WIDTH:
            new_tube_x += (TUBE_WIDTH + BETWEEN_TUBE) * 3
        if new_tube_x + TUBE_WIDTH < BIRD_X-BIRD_HALF and not tube_passed:
            reward = 1
            tube_passed = True
        new_tubes.append((new_tube_x, tube_h, tube_passed))

    new_state = State(y, speed, sorted(new_tubes, key=itemgetter(0)))
    if new_state.y > SCREEN_SIZE or new_state.y < 0 or \
        _wrecked_into_tube(new_state.y, new_state.tubes):
        reward = -1
        new_state = State()

    return new_state, reward


if __name__ == '__main__':
    pygame.init()

    DISPLAY = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), 0, 32)
    clock = pygame.time.Clock()

    DISPLAY.fill(WHITE)
    state = State()

    reward_map = {0: WHITE, 1: YELLOW, -1: BLACK}
    reward = 0
    score = 0
    best_score = 0
    while True:
        DISPLAY.fill(reward_map[reward])
        jump = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key ==pygame.K_SPACE:
                    jump = True

        new_state, reward = advance(state, jump, dt=INV_TICK)
        if reward == 1:
            score += 1
        elif reward == -1:
            best_score = max(best_score, score)
            score = 0
        pygame.display.set_caption("score: %d (best %d)" % (score, best_score))
        draw(new_state)
        state = new_state
        clock.tick(TICK)