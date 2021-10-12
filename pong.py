import pygame
import random
import time
from elements import Paddle, Ball, Wall, GoalLine

pygame.init()

# ----------- Screen & Game Variable Setup ------------

screenWidth = 1300
screenHeight = 800

fieldWidth = 0
fieldHeight = 0
fieldPos = (0, 0)
ball_size = 10
paddle_vel = 20
last_hit = 0
win_score = 10
largest_score = 0

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Pong: The Remake')

clock = pygame.time.Clock()
runGame = True

# ------------ Colours ------------

WHITE = (255, 255, 255)
GREY = (230, 230, 230)
MED_GREY = (170, 170, 170)
NAVY_BLUE = (0, 20, 40)
MINT_GREEN = (135, 225, 150)
LAVENDER = (195, 145, 230)


# -------- Text Font Variables --------

score_font = pygame.font.Font('fonts/FreeSansBold.ttf', 64)
label_font = pygame.font.Font('fonts/FreeSans.ttf', 32)
small_label_font = pygame.font.Font('fonts/FreeSans.ttf', 20)
title_font = pygame.font.Font('fonts/FreeSansBold.ttf', 90)
sub_font = pygame.font.Font('fonts/FreeSansBold.ttf', 40)
sub2_font = pygame.font.Font('fonts/FreeSansBold.ttf', 30)

# ------- SFXs and Music -------
bounceSound = pygame.mixer.Sound('audio/ball_bounce.wav')
music = pygame.mixer.music.load('audio/waiting.mp3')
pygame.mixer.music.set_volume(0.4)

# Class for general screen & field
class Window:
    def __init__(self, net_colour, fieldInfo=(), mode=0):
        self.mode = mode if mode in [0, 1, 2] else 0
        self.net_colour = net_colour
        self.fieldWidth = fieldInfo[0]
        self.fieldHeight = fieldInfo[1]
        self.fieldPos = fieldInfo[2]
        self.round = 1

    def draw_net(self, x, y, dash_size, length, spacing, facing='v'):
        rotation = facing if facing in ['h', 'v'] else 'v' # horizontal/vertical, default vertical
        dashCount = int(length / (dash_size + spacing))
        net_colour = self.net_colour
        def draw_dash(dash_x, dash_y):
            pygame.draw.rect(screen, net_colour, [dash_x, dash_y, dash_size, dash_size])
        for i in range(dashCount):
            draw_dash(x, y)
            if rotation == 'h':
                x += (dash_size + spacing)
            elif rotation == 'v':
                y += (dash_size + spacing)

    def draw_field(self, bg_colour):
        screen.fill(bg_colour)
        # --------------------- 2-player map ---------------------
        if self.mode == 0 or self.mode == 1:
            dash_size = 10
            dash_spacing = 15
            net_length = self.fieldHeight
            x = screenWidth / 2 - dash_size / 2
            y = dash_size
            self.draw_net(x, y, dash_size, net_length, dash_spacing,'v')

        # --------------------- 4-player map ---------------------
        elif self.mode == 2:
            dash_size = 5
            dash_spacing = 10
            net_length = 400
            x_values = [400, 450 + dash_spacing,
                        900, 450 + dash_spacing]
            y_values = [200 + dash_spacing, 150,
                        200 + dash_spacing, 650]

            for i in range(len(x_values)): # start with left player, go clockwise
                rotation = 'v' if i % 2 == 0 else 'h'
                x = x_values[i]
                y = y_values[i]
                self.draw_net(x, y, dash_size, net_length, dash_spacing, rotation)

# ------------------------------------------ Game Logic Functions ------------------------------------------

# Initial ball setup, and re-setup ball after every goal
def setBall(size, baseVel, mode, roundNum):
    global last_hit
    last_hit = 0
    x = screenWidth / 2 - size / 2
    y = screenHeight / 2 - size / 2
    face = random.randint(1, 2)
    neg = random.choice([-1, 1]) if mode == 2 else 1 if roundNum % 2 == 0 else -1
    # variable 'face' determines if x or y direction gets randomized; the other direction manages overall velocity
    if not mode == 2:
        x_vel = random.randint(int(baseVel / 2), baseVel)/2 * neg
        y_vel = (baseVel - x_vel)/2 * random.choice([-1, 1])
    else:
        x_vel = (random.randint(10, baseVel) / 2) * neg if face == 2 else baseVel/2 * neg
        y_vel = (random.randint(2, baseVel) / 2) * random.choice([-1, 1]) if face == 1 else random.choice([-baseVel, baseVel])
    ball = Ball(screen, x, y, size, x_vel, y_vel, WHITE)
    return ball

# opponent movement ai
def opponent_movement(ball, paddle, walls, direction='v'):
    facing = direction if direction in ['v', 'h'] else 'v'  # facing either vertically or horizontally
    if facing == 'h':
        if ball.x + 250 >= paddle.shape.centerx:
            if paddle.shape.centery + 30 < ball.y and paddle.shape.bottom + paddle.vel <= walls[1].shape.top:
                paddle.moveDown()
            if paddle.shape.centery - 30 > ball.y and paddle.shape.top - paddle.vel >= walls[0].shape.bottom:
                paddle.moveUp()
        else:
            if paddle.shape.centery < screenHeight / 2:
                paddle.moveDown()
            if paddle.shape.centery > screenHeight / 2:
                paddle.moveUp()
    else:
        if ball.y + 200 <= paddle.shape.centery or ball.y - 200 >= paddle.shape.centery:
            if paddle.shape.centerx < screenWidth / 2:
                paddle.moveRight()
            if paddle.shape.centerx > screenWidth / 2:
                paddle.moveLeft()
        else:
            if paddle.shape.centerx < ball.x and paddle.shape.right + paddle.vel <= walls[3].shape.left:
                paddle.moveRight()
            if paddle.shape.centerx > ball.x and paddle.shape.left - paddle.vel >= walls[2].shape.right:
                paddle.moveLeft()

# Detects when the ball's velocity needs to change to imitate a bounce
def checkBounce(ball, paddles, walls, check_wall):
    global last_hit
    if ball.shape.colliderect(paddles[0].shape):
        ball.bounce(bounceSound, 'h')
        ball.shape.left = paddles[0].shape.right
        last_hit = 1
    if ball.shape.colliderect(paddles[1].shape):
        ball.bounce(bounceSound, 'h')
        ball.shape.right = paddles[1].shape.left
        last_hit = 2
    try:
        if ball.shape.colliderect(paddles[2].shape):
            ball.bounce(bounceSound, 'v')
            ball.shape.top = paddles[2].shape.bottom
            last_hit = 3

        if ball.shape.colliderect(paddles[3].shape):
            ball.bounce(bounceSound, 'v')
            ball.shape.bottom = paddles[3].shape.top
            last_hit = 4

    except IndexError:
        pass

    if check_wall:
        if ball.shape.colliderect(walls[0].shape):
            ball.bounce(bounceSound, 'v')
            ball.shape.top = walls[0].shape.bottom
        if ball.shape.colliderect(walls[1].shape):
            ball.bounce(bounceSound, 'v')
            ball.shape.bottom = walls[1].shape.top

    ball.dimensions(True)

# Function to check when a player has scored a goal
def checkGoal(window, ball, players, goals):
    global ball_size, last_hit
    reset_ball = False
    if ball.shape.right < goals[0].shape.left:
        reset_ball = True
    if ball.shape.left > goals[1].shape.right:
        reset_ball = True
    try:
        if ball.shape.top < goals[2].shape.bottom:
            reset_ball = True
        if ball.shape.bottom > goals[3].shape.top:
            reset_ball = True

    except IndexError:
        pass
    if reset_ball:
        index = last_hit - 1 if last_hit != 0 else -1 if window.mode == 2 else window.round % 2
        players[index].score += 1 if index >= 0 else 0
        window.round += 1
        newBall = setBall(ball_size, 22, window.mode, window.round)
        draw_player_scores(players, window.mode)
        pygame.display.update()
        time.sleep(1)
        return newBall
    else:
        return False

# Display keystrokes on screen, as well as when each key is being pressed
def draw_keystroke(char, x, y, key_pressed=False):
    colour = WHITE if key_pressed else MED_GREY
    keystroke = sub_font.render(f'[ {char} ]', False, colour)
    screen.blit(keystroke, (x, y))

# ------------------------------------------ Game Setup/Navigation Functions ------------------------------------------

def blitPhrases(phrases, positions):  # Function to add multiple phrases to the screen with less lines of code
    for i in range(len(phrases)):
        screen.blit(phrases[i], positions[i])

def setup(mode):
    global fieldWidth, fieldHeight, fieldPos, ball_size, paddle_vel
    fieldWidth = 800 if mode == 2 else screenWidth
    fieldHeight = 800
    fieldPos = ((screenWidth - fieldWidth) / 2, (screenHeight - fieldHeight) / 2)
    window = Window(GREY, (fieldWidth, fieldHeight, fieldPos), mode)
    p2_comp = False if mode == 1 else True
    paddle_width = 15
    paddle_length = 100

    # Left-side paddle position
    x_valueL = 300 if mode == 2 else 150
    y_valueL = screenHeight / 2 - paddle_length / 2

    # Top-side paddle position
    x_valueU = screenWidth / 2 - paddle_length / 2
    y_valueU = 50

    # ---------- Define Paddles ----------
    p1 = Paddle(screen, x_valueL, y_valueL, paddle_width, paddle_length, paddle_vel, WHITE, 'h')
    p2 = Paddle(screen, screenWidth - x_valueL - paddle_width, y_valueL, paddle_width, paddle_length, paddle_vel, WHITE, 'h', p2_comp)
    p3 = Paddle(screen, x_valueU, y_valueU, paddle_length, paddle_width, paddle_vel, WHITE, 'v', True)
    p4 = Paddle(screen, x_valueU, screenHeight - y_valueU - paddle_width, paddle_length, paddle_width, paddle_vel, WHITE, 'v', True)
    playerLst = [p1, p2, p3, p4] if mode == 2 else [p1, p2]

    # ---------- Ball ----------
    ball = setBall(ball_size, 22, window.mode, window.round)

    # ---------- Walls ----------
    wall_length  = screenWidth - x_valueL * 2 + 100
    wall_width = 30
    if not mode == 2:
        top_wall = Wall(screen, x_valueL - 50, 10 - wall_width, wall_length, wall_width, WHITE)
        bottom_wall = Wall(screen, x_valueL - 50, screenHeight - 10, wall_length, wall_width, WHITE)
        left_wall = None
        right_wall = None
    else:
        top_wall = Wall(screen, p1.shape.right, p3.shape.bottom, screenWidth - 2 * p1.shape.right, 1, WHITE)
        bottom_wall = Wall(screen, p1.shape.right, p4.shape.top, screenWidth - 2 * p1.shape.right, 1, WHITE)
        left_wall = Wall(screen, p1.shape.right, p3.shape.bottom, 1, screenHeight - 2 * p3.shape.bottom, WHITE)
        right_wall = Wall(screen, p2.shape.left, p3.shape.bottom, 1, screenHeight - 2 * p3.shape.bottom, WHITE)

    walls = [top_wall, bottom_wall, left_wall, right_wall] if mode == 2 else [top_wall, bottom_wall]

    # ---------- Goal Lines ----------
    goal_width = 10
    p1_goal = GoalLine(screen, fieldPos[0] - goal_width, fieldPos[1], goal_width, fieldHeight, WHITE)
    p2_goal = GoalLine(screen, fieldWidth + fieldPos[0], fieldPos[1], goal_width, fieldHeight, WHITE)
    p3_goal = GoalLine(screen, fieldPos[0], fieldPos[1], fieldWidth, goal_width, WHITE)
    p4_goal = GoalLine(screen, fieldPos[0], fieldHeight + fieldPos[1] - goal_width, fieldWidth, goal_width, WHITE)

    goals = [p1_goal, p2_goal, p3_goal, p4_goal] if mode == 2 else [p1_goal, p2_goal]
    return window, playerLst, ball, walls, goals

def draw_welcome():
    run = True
    blink_count = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Spacebar = Play Game
                    run = False
                    return True
                if event.key == pygame.K_x: # x = Exit Game
                    run = False
                    return False
        screen.fill(NAVY_BLUE)

        # ------------------------ Title Screen ------------------------
        subtitle_text = label_font.render(': The Remake', False, WHITE)
        subtitle_width = subtitle_text.get_width()
        title_text = title_font.render('PONG', False, WHITE)
        title_width = title_text.get_width()
        title_xy = (screenWidth / 2 - title_width / 2 - subtitle_width / 2, 300)
        subtitle_xy = (screenWidth/2 + 30, 340)

        name_text = small_label_font.render('by Caden Chan', False, WHITE)
        name_xy = (subtitle_xy[0] + 60, 370)

        button_text = sub_font.render('[SPACE]', False, MINT_GREEN)
        button_xy = 620, 450

        prompt1_text = sub_font.render('Click', False, WHITE)
        prompt1_xy = 520, 450

        prompt2_text = sub_font.render('To Play', False, WHITE)
        prompt2_width = prompt2_text.get_width()
        prompt2_xy = (screenWidth / 2 - prompt2_width / 2, 490)

        quit_text = small_label_font.render('Quit: [X]', False, WHITE)
        quit_xy = screenWidth - 120, screenHeight - 50

        blitPhrases([title_text, subtitle_text, name_text, quit_text], [title_xy, subtitle_xy, name_xy, quit_xy])
        if blink_count % 20 <= 10 :  # Makes certain elements "blink" on the screen
            screen.blit(prompt1_text, prompt1_xy)
            screen.blit(prompt2_text, prompt2_xy)
            screen.blit(button_text, button_xy)
        blink_count += 1
        clock.tick(20)
        pygame.display.update()

# Create a tag for each player (e.g. P1, P2 COMP3, etc.)
def player_label(label, x, y, colour):
    text = small_label_font.render(label, False, colour)
    screen.blit(text, (x, y))

# Draw the main menu
def draw_mainMenu(blink_count):
    pong_text = title_font.render('PONG', False, WHITE)
    pong_width = pong_text.get_width()
    pong_xy = screenWidth / 2 - pong_width / 2, 10

    title_text = sub_font.render('Select A Game Mode', False, WHITE)
    title_width = title_text.get_width()
    title_xy = screenWidth / 2 - title_width / 2, 170

    sub1_text = sub2_font.render('Traditional Pong', False, LAVENDER)
    sub1_xy = 250, 320
    sub2_text = sub2_font.render('4-Player Field (NEW!)', False, MINT_GREEN)
    sub2_width = sub2_text.get_width()
    sub2_xy = screenWidth - sub1_xy[0] - sub2_width, 320

    option1_text = label_font.render('Player vs Computer', False, WHITE)
    option1_width = option1_text.get_width()
    option1_xy = sub1_xy[0] - sub2_width/2 + option1_width/2 - 10, 400

    option2_text = label_font.render('Player vs Player', False, WHITE)
    option2_xy = option1_xy[0] + 20, 560

    option3_text = label_font.render('4-Player FFA', False, WHITE)
    option3_width = option3_text.get_width()
    option3_xy = sub2_xy[0] + 60, 400

    guide_text = label_font.render(f'First to {win_score} points wins!', False, WHITE)
    guide_width = guide_text.get_width()
    guide_xy = screenWidth / 2 - guide_width / 2, 720

    quit_text = small_label_font.render('Quit: [X]', False, WHITE)
    quit_xy = screenWidth - 120, screenHeight - 50

    screen.fill(NAVY_BLUE)
    pygame.draw.line(screen, WHITE, (screenWidth/2, 300), (screenWidth/2, 690), 3)
    blitPhrases([pong_text, title_text, sub1_text, sub2_text, option1_text, option2_text, option3_text, quit_text, guide_text],
                [pong_xy, title_xy, sub1_xy, sub2_xy, option1_xy, option2_xy, option3_xy, quit_xy, guide_xy])

    button1 = sub_font.render('[ 1 ]', False, LAVENDER)
    button1_width = button1.get_width()
    button1_xy = option1_xy[0] + option1_width/2 - button1_width/2, 440
    button2 = sub_font.render('[ 2 ]', False, LAVENDER)
    button2_xy = button1_xy[0], 600
    button3 = sub_font.render('[ 3 ]', False, MINT_GREEN)
    button3_width = button3.get_width()
    button3_xy = option3_xy[0] + option3_width / 2 - button3_width/2, 440

    if blink_count % 20 <= 10:  # These elements blink on the screen
        screen.blit(button1, button1_xy)
        screen.blit(button2, button2_xy)
        screen.blit(button3, button3_xy)

    pygame.display.update()

def mainMenu(preset_mode=-1):
    pygame.mixer.music.play(-1)
    blink_count = 0
    mode = -1
    preset_mode = preset_mode if preset_mode in [-1, 0, 1, 2] else 0
    run = True
    runMain = True
    if preset_mode == -1:
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    runMain = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        run = False
                        runMain = False
            draw_mainMenu(blink_count)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:  # Player vs Computer
                mode = 0
            if keys[pygame.K_2]:  # Player vs Player
                mode = 1
            if keys[pygame.K_3]:  # Player vs Computer vs Computer vs Computer
                mode = 2
            if not mode == -1:
                run = False
            blink_count += 1
            clock.tick(20)
    else:
        mode = preset_mode

    window, playerLst, ball, walls, goals = setup(mode)
    pygame.mixer.music.stop()
    return window, playerLst, ball, walls, goals, runMain

# Visual message indicating a win or loss
def end_message(playerNum, mode, blink_count):
    if not playerNum:
        return
    if mode == 1:
        msg = f'Player {playerNum} Wins!'
    else:
        msg = 'You Win!' if playerNum == 1 else 'You Lost!'

    end_text = score_font.render(f'{msg}', False, WHITE)
    text_width = end_text.get_width()
    end_xy = (screenWidth / 2 - text_width / 2, 250)

    button = label_font.render('[SPACE]', False, LAVENDER)
    button_xy = 680, 420

    button1 = label_font.render('[ESC]', False, LAVENDER)
    button1_xy = 700, 470

    # Prompt the user to play again
    end_text2 = label_font.render('Play Again? ________', False, WHITE)
    text2_width = end_text2.get_width()
    end_xy2 = (screenWidth/2 - text2_width / 2, 420)

    # Prompt the user to return to the main menu
    menu_text = label_font.render('Main Menu? ______', False, WHITE)
    menu_width = menu_text.get_width()
    menu_xy = (screenWidth / 2 - menu_width / 2, 470)

    blitPhrases([end_text, end_text2, menu_text], [end_xy, end_xy2, menu_xy])
    if blink_count % 20 <= 10:
        screen.blit(button, button_xy)
        screen.blit(button1, button1_xy)


# ------------------------------------------ Game Scoring Functions ------------------------------------------

def draw_player_scores(players, mode):
    x_values = [480, 780, 630, 630] if mode == 2 else [550, 710]
    y_values = [370, 370, 220, 520] if mode == 2 else [50, 50]
    for i in range(len(x_values)):
        player_text = score_font.render(f'{players[i].score}', False, WHITE)
        screen.blit(player_text, (x_values[i], y_values[i]))

def check_scores(players):
    global win_score
    for i in range(len(players)):
        if players[i].score == win_score:
            return i + 1
    return False

# ------- Main Loop -------
def main():
    window, players, ball, walls, goals, runMain = mainMenu()
    global paddle_vel, largest_score
    blink_count = 0
    run = runMain
    game_run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    window, players, ball, walls, goals, runMain = mainMenu()
                    game_run = True
                    if not runMain:
                        run = False
                if event.key == pygame.K_SPACE and not game_run:
                    window, players, ball, walls, goals, runMain = mainMenu(window.mode)
                    game_run = True

        if game_run:  # If a round of pong is running
            window.draw_field(bg_colour=NAVY_BLUE)
            keys = pygame.key.get_pressed()
            # player 1 movement
            q_pressed = False
            a_pressed = False
            if keys[pygame.K_q]:
                players[0].moveUp()
                q_pressed = True
            if keys[pygame.K_a]:
                players[0].moveDown()
                a_pressed = True
            if window.mode == 2:
                draw_keystroke('q', 460, 500, key_pressed=q_pressed)
                draw_keystroke('a', 460, 550, key_pressed=a_pressed)
                player_label('P1', 440, 400, MINT_GREEN)
                player_label('COMP1', 820, 400, LAVENDER)
                player_label('COMP2', 610, 200, LAVENDER)
                player_label('COMP3', 610, 600, LAVENDER)
                menu_text1 = small_label_font.render('Return to main', False, WHITE)
                menu_text2 = small_label_font.render('menu: [ESC]', False, WHITE)
                menu_xy1 = screenWidth - 200, screenHeight - 100
                menu_xy2 = screenWidth - 200, screenHeight - 70
                screen.blit(menu_text1, menu_xy1)
                screen.blit(menu_text2, menu_xy2)
            else:
                draw_keystroke('q', 550, 680, key_pressed=q_pressed)
                draw_keystroke('a', 550, 730, key_pressed=a_pressed)
                player_label('P1', 555, 140, MINT_GREEN)
                menu_text = small_label_font.render('Return to main menu: [ESC]', False, WHITE)
                menu_xy = 870, 750
                screen.blit(menu_text, menu_xy)
            try:
                if not players[1].comp:
                    p_pressed = False
                    sc_pressed = False
                    # player 2 movement
                    if keys[pygame.K_p]:
                        players[1].moveUp()
                        p_pressed = True
                    if keys[pygame.K_SEMICOLON]:
                        players[1].moveDown()
                        sc_pressed = True
                    draw_keystroke('p', 680, 680, key_pressed=p_pressed)
                    draw_keystroke(';', 680, 730, key_pressed=sc_pressed)
                    player_label('P2', 715, 140, LAVENDER)
                else:
                    if not window.mode == 2:
                        player_label('COMP1', 700, 140, LAVENDER)

            except IndexError:
                continue

            # ---- Game logic for collision boundaries of the paddles ----
            if players[0].shape.top <= walls[0].shape.bottom:
                players[0].shape.top = walls[0].shape.bottom
            if players[0].shape.bottom >= walls[1].shape.top:
                players[0].shape.bottom = walls[1].shape.top
            if players[1].shape.top <= walls[0].shape.bottom:
                players[1].shape.top = walls[0].shape.bottom
            if players[1].shape.bottom >= walls[1].shape.top:
                players[1].shape.bottom = walls[1].shape.top
            try:
                if players[2].shape.left <= walls[2].shape.right:
                    players[2].shape.left = walls[2].shape.right
                if players[2].shape.right >= walls[3].shape.left:
                    players[2].shape.right = walls[3].shape.left
                if players[3].shape.left <= walls[2].shape.right:
                    players[3].shape.left = walls[2].shape.right
                if players[3].shape.right >= walls[3].shape.left:
                    players[3].shape.right = walls[3].shape.left
            except IndexError:
                pass
            for player in players:
                # keep the dimensions of the paddles consistent
                player.dimensions(True)
            for player in players:
                # Move all non-player paddle accordingly
                if player.comp:
                    opponent_movement(ball, player, walls, player.facing)
                player.draw()
            ball.move()
            ball.draw()

            if window.mode == 2:
                for goal in goals:
                    goal.draw()
            if not window.mode == 2:
                for wall in walls:
                    wall.draw()
            check_wall = False if window.mode == 2 else True
            checkBounce(ball, players, walls[:3], check_wall=check_wall)
            newBall = checkGoal(window, ball, players, goals)

            if newBall:
                ball = newBall

            draw_player_scores(players, window.mode)
            largest_score = check_scores(players)
            if largest_score:
                game_run = False
                time.sleep(1)
        pygame.display.update()
        game_end(window, largest_score, blink_count)
        blink_count += 1

        clock.tick(20)

# Call function when someone reaches the objective of 10 points
def game_end(window, score, blink_count):
    screen.fill(NAVY_BLUE)
    end_message(score, window.mode, blink_count)

if draw_welcome():
     main()
pygame.quit()
