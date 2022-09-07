import pygame
pygame.init()
import time
import math
from utils import blit_sub_text, scale_image, blit_rotate_center, blit_text_center
pygame.font.init()


GRASS = scale_image(pygame.image.load("imgs/bg.jpg"), 1)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH_LOC = (130, 250)
FINISH_MASK = pygame.mask.from_surface(FINISH)

GREY_CAR = scale_image(pygame.image.load("imgs/grey-car.png"), 0.55)
WHITE_CAR = scale_image(pygame.image.load("imgs/white-car.png"), 0.55)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)

WIDTH, HEIGHT =  TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vroom Vroom Skrt Skrt")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)
SUB_TEXT = pygame.font.SysFont("comicsans", 25)

FPS = 60
PATH = [(153, 120), (107, 88), (70, 481), (318, 731), (418, 521), (498, 460), (606, 576), (613, 715), (734, 399), (439, 361), 
        (436, 269), (697, 258), (738, 123), (581, 71), (327, 83), (288, 256),(273, 378),(170, 259)]


def pause(player_car, computer_car, game):
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    paused = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

                elif event.key == pygame.K_n:
                    game.reset()
                    computer_car.reset()
                    player_car.reset()
                    computer_car.game_over()
                    paused = False


         

        WIN.blit(GRASS, (0, 0))
        blit_sub_text(WIN, MAIN_FONT, "GAME IS PAUSED")

        blit_text_center(WIN, SUB_TEXT, "Press C to continue, press N to start a new game, or press Q to exit.")
        

        pygame.display.update()
        clock.tick(5)


class GameInfo:
    LEVELS = 5

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)

        

        

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left = False, right = False ):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()
    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):    
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMG = GREY_CAR 
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce_back(self):
        self.vel = -self.vel
        self.move()

class PlayerCar2(AbstractCar):
    IMG = RED_CAR 
    START_POS = (150, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce_back(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    IMG = WHITE_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel) 
        self.path = path
        self.current_point = 0 
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (0, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        #self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)
        
        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

    def bounce_back(self):
        self.vel = -self.vel
        self.move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.4
        self.current_point = 0
        self.rotation_vel = self.rotation_vel + (level - 1) * 0.45

    def game_over(self):
        self.reset()
        self.vel = self.max_vel
        self.current_point = 0
        self.rotation_vel = 3




def draw(win, images, player_car, computer_car, player2_car, game):
    for img, pos in images:
        win.blit(img, pos)

    level_info = MAIN_FONT.render(f"Level {game.level}", 1, (255, 255, 255))
    win.blit(level_info, (10, HEIGHT - level_info.get_height() - 90))

    vel_info = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_info, (10, HEIGHT - vel_info.get_height() - 10))    

    time_text = MAIN_FONT.render(f"Time: {game.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 50))   

    player_car.draw(win)
    computer_car.draw(win)
    #player2_car.draw(win)
    pygame.display.update()


def move_player(player_car): 
    keys = pygame.key.get_pressed() 
    moved = False


    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

def move_player2(player2_car): 
    keys = pygame.key.get_pressed() 
    moved = False


    if keys[pygame.K_LEFT]:
        player2_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player2_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player2_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player2_car.move_backward()

    if not moved:
        player2_car.reduce_speed()

def collision_manager(player_car, player2_car, computer_car, game):
    if player2_car.collide(TRACK_BORDER_MASK) != None:
        player2_car.bounce_back()

    player2_finish_poi_collide = player2_car.collide(FINISH_MASK, *FINISH_LOC)
    if player2_finish_poi_collide != None:
        if player2_finish_poi_collide[1] == 0:
            player2_car.bounce_back()
        else:
            player2_wins = True
            while player2_wins:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        break
                    if event.type == pygame.KEYDOWN:
                        game.next_level()
                        player2_car.reset()
                        player2_wins = False
                WIN.blit(GRASS, (0, 0))
                blit_sub_text(WIN, MAIN_FONT, "PROCEED TO THE NEXT LEVEL")     
                blit_text_center(WIN, SUB_TEXT, f"Press any key to proceed to the next level! Proceeding to level {game.level}!")   
                pygame.display.update()
                clock.tick(5) 

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce_back()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_LOC)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce_back()
        else:
            player_wins = True
            while player_wins:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        break
                    if event.type == pygame.KEYDOWN:
                        game.next_level()
                        player_car.reset()
                        computer_car.next_level(game.level)
                        player_wins = False
                if game.level < 5:
                    WIN.blit(GRASS, (0, 0))
                    blit_sub_text(WIN, MAIN_FONT, "PROCEED TO THE NEXT LEVEL")     
                    blit_text_center(WIN, SUB_TEXT, f"Press any key to proceed to the next level! Proceeding to level {game.level}!")   
                    pygame.display.update()
                    clock.tick(5)                        

    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_LOC)
    if computer_finish_poi_collide != None:
        computer_wins = True
        while computer_wins:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.KEYDOWN:
                    game.reset()
                    computer_car.reset()
                    player_car.reset()
                    computer_wins = False
                    computer_car.game_over()

            WIN.blit(GRASS, (0, 0))
            blit_sub_text(WIN, MAIN_FONT, "GAME OVER")     
            blit_text_center(WIN, SUB_TEXT, f"Press any key to try again! You lost at level {game.level}!")   
            pygame.display.update()
            clock.tick(5)

    

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_LOC), (TRACK_BORDER, (0, 0)) ]
player_car = PlayerCar(5, 5)
computer_car = ComputerCar(3, 3, PATH)
player2_car = PlayerCar2(5, 5)
game = GameInfo()

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car, player2_car, game)

    while not game.started:
        WIN.blit(GRASS, (0, 0))
        blit_text_center(WIN, SUB_TEXT, f"Press any key to start level {game.level}!")
        pause_instruction = SUB_TEXT.render("Press P to bring up the Pause Menu while in-game.", 1, (190, 190, 190))
        WIN.blit(pause_instruction, (WIN.get_width()/2 - pause_instruction.get_width()/2, HEIGHT - pause_instruction.get_height() - 340)) 
        blit_sub_text(WIN, MAIN_FONT, "Car Racers!!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause(player_car, computer_car, game)

        #if event.type == pygame.MOUSEBUTTONDOWN:
            #pos = pygame.mouse.get_pos()
            #computer_car.path.append(pos)

    move_player(player_car)
    computer_car.move()
    collision_manager(player_car, player2_car, computer_car, game)
    move_player2(player2_car)

    if game.game_finished():
        game_finish = True
        while game_finish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break
                if event.type == pygame.KEYDOWN:
                    game.reset()
                    player_car.reset()
                    computer_car.reset()
            WIN.blit(GRASS, (0, 0))
            blit_sub_text(WIN, MAIN_FONT, "YOU WIN!")     
            blit_text_center(WIN, SUB_TEXT, f"Congratulations on winning! Press any key to reset the game")   
            pygame.display.update()
            clock.tick(5)

#print(computer_car.path)
pygame.quit()

