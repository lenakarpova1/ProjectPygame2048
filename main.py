import sys
import os
import pygame
import random
import sqlite3

pygame.init()
size = width, height = 620, 480
screen = pygame.display.set_mode(size)
pygame.display.set_caption('2048')
clock = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 24)


# словарь со всеми используемыми цветами
colors = {0: (204, 192, 179),
          2: (238, 228, 218),
          4: (237, 224, 200),
          8: (242, 177, 121),
          16: (245, 149, 99),
          32: (246, 124, 95),
          64: (246, 94, 59),
          128: (237, 207, 114),
          256: (237, 204, 97),
          512: (237, 200, 80),
          1024: (237, 197, 63),
          2048: (237, 194, 46),
          'light text': (249, 246, 242),
          'dark text': (119, 110, 101),
          'other': (0, 0, 0),
          'bg': (187, 173, 160)}

board_cells = [[0 for _ in range(4)] for _ in range(4)]
game_over_one = False
game_over_two = False
create_new_value = True
init_count = 0
moving = 0
score = 0
max_score = 0
username = None


# заставка игры
def draw_screensaver():
    global username, max_score
    img = pygame.image.load('photo_2048.jpg')
    pygame.mixer.music.load(os.path.join('data', 'music_one.mp3'))
    pygame.mixer.music.play(-1)
    name_user = 'введите имя'
    flag = False
    while not flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.unicode.isalpha():
                    if name_user == 'введите имя':
                        name_user = event.unicode
                    else:
                        name_user += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    name_user = name_user[:-1]
                elif event.key == pygame.K_RETURN:  # проверяем, сохранено ли такое имя и начинаем игру
                    con = sqlite3.connect("users_score.db")
                    cur = con.cursor()
                    res_name = cur.execute(f"""SELECT name, score FROM score WHERE name = '{name_user}'""").fetchone()

                    if not res_name:  # добавление имени в базу данных
                        cur.execute(f"""INSERT INTO score(name) VALUES('{name_user}')""")
                        con.commit()
                        username = name_user
                        flag = True
                        pygame.mixer.music.stop()
                    else:  # переход к игре
                        username = name_user
                        if res_name[1]:
                            max_score = res_name[1]
                        flag = True
                        pygame.mixer.music.stop()

        screen.blit(pygame.transform.scale(img, (620, 570)), (0, -45))
        font = pygame.font.SysFont(None, 50)
        text_name = font.render(name_user, True, (253, 245, 230))
        screen.blit(text_name, (210, 280))
        pygame.display.update()


draw_screensaver()


def draw_over():
    font_text2 = pygame.font.SysFont(None, 32)
    pygame.draw.rect(screen, (187, 170, 149), [5, 235, 380, 90], 0, 10)
    game_over_text1 = font.render('Game Over!', True, 'white')
    game_over_text2 = font_text2.render('Нажмите Enter для перезапуска', True, 'white')
    screen.blit(game_over_text1, (120, 245))
    screen.blit(game_over_text2, (20, 285))
    pass


# слияние клеток со значениями
def make_step(mov, board):
    global score
    unification_cells = [[0 for _ in range(4)] for _ in range(4)]
    if mov == 'up':
        for i in range(4):
            for j in range(4):
                step = 0
                if i > 0:
                    for x in range(i):  # проверяем есть ли пустые ячейки сверху
                        if board[x][j] == 0:
                            step += 1
                    if step > 0:  # если есть пустые ячейки, то двигаем клетки наверх
                        board[i - step][j] = board[i][j]
                        board[i][j] = 0
                    if board[i - step - 1][j] == board[i - step][j] and unification_cells[i - step][j] == 0 \
                            and unification_cells[i - step - 1][j] == 0:  # новое значение при слиянии двух одинаковых
                        board[i - step - 1][j] *= 2
                        score += board[i - step - 1][j]
                        board[i - step][j] = 0
                        unification_cells[i - step - 1][j] = 1  # объединять ячейку в текущем ходе больше нельзя

    elif mov == 'down':
        for i in range(3):
            for j in range(4):
                step = 0
                for x in range(i + 1):  # проверяем есть ли пустые ячейки снизу
                    if board[3 - x][j] == 0:
                        step += 1
                if step > 0:  # если есть пустые ячейки, то двигаем клетки вниз
                    board[2 - i + step][j] = board[2 - i][j]
                    board[2 - i][j] = 0
                if 3 - i + step <= 3:  # если это не нижняя строчка
                    if board[2 - i + step][j] == board[3 - i + step][j] and unification_cells[3 - i + step][j] == 0 \
                            and unification_cells[2 - i + step][j] == 0:  # новое значение при слиянии двух одинаковых
                        board[3 - i + step][j] *= 2
                        score += board[3 - i + step][j]
                        board[2 - i + step][j] = 0
                        unification_cells[3 - i + step][j] = 1

    elif mov == 'right':
        for i in range(4):
            for j in range(4):
                step = 0
                for y in range(j):
                    if board[i][3 - y] == 0:
                        step += 1
                if step > 0:
                    board[i][3 - j + step] = board[i][3 - j]
                    board[i][3 - j] = 0
                if 4 - j + step <= 3:
                    if board[i][4 - j + step] == board[i][3 - j + step] and unification_cells[i][4 - j + step] == 0 \
                            and unification_cells[i][3 - j + step] == 0:  # новое значение при слиянии двух одинаковых
                        board[i][4 - j + step] *= 2
                        score += board[i][4 - j + step]
                        board[i][3 - j + step] = 0
                        unification_cells[i][4 - j + step] = 1

    elif mov == 'left':
        for i in range(4):
            for j in range(4):
                step = 0
                for y in range(j):
                    if board[i][y] == 0:
                        step += 1
                if step > 0:
                    board[i][j - step] = board[i][j]
                    board[i][j] = 0
                if board[i][j - step] == board[i][j - step - 1] and unification_cells[i][j - step] == 0 \
                        and unification_cells[i][j - step - 1] == 0:  # новое значение при слиянии двух одинаковых
                    board[i][j - step - 1] *= 2
                    score += board[i][j - step - 1]
                    board[i][j - step] = 0
                    unification_cells[i][j - step] = 1

    return board


# добавление рандомно новых клеток со значениями
def new_cells(board):
    count = 0
    flag = False
    while any(0 in row for row in board) and count < 1:
        row = random.randint(0, 3)
        col = random.randint(0, 3)
        if board[row][col] == 0:
            count += 1
            if random.randint(1, 10) == 10:
                board[row][col] = 4
            else:
                board[row][col] = 2
    if count < 1:
        flag = True
    return board, flag


# рисуем полотно для клетчатого поля
def draw_board():
    global username
    pygame.draw.rect(screen, colors['bg'], [10, 100, 370, 370])
    score_text = font.render(f'Счёт: {score}', True, (119, 110, 101))
    max_score_text = font.render(f'Максимальный счёт: {max_score}', True, (119, 110, 101))
    name_text = font.render(f'User: {username}', True, (119, 110, 101))
    best_text = font.render('Топ игроков', True, (97, 90, 81))
    screen.blit(score_text, (20, 20))
    screen.blit(max_score_text, (20, 60))
    screen.blit(name_text, (400, 440))
    screen.blit(best_text, (400, 40))

    con = sqlite3.connect("users_score.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT name, score FROM score WHERE score > 0""").fetchall()
    result.sort(key=lambda x: -x[1])
    result = result[:10]  # лучшие 10 игроков
    delta_y = 35
    for elem in result:
        res_text = font.render(f'{elem[0]}:  {elem[1]}', True, (119, 110, 101))
        screen.blit(res_text, (400, 65 + delta_y))
        delta_y += 30


# рисуем поле с пустыми клеточками
def draw_cell(board):
    for i in range(4):
        for j in range(4):
            value = board[i][j]
            if value > 8:
                value_color = colors['light text']
            else:
                value_color = colors['dark text']
            if value <= 2048:
                color = colors[value]
            else:
                color = colors['other']

            pygame.draw.rect(screen, color, [j * 90 + 20, i * 90 + 110, 80, 80], 0, 2)

            if value > 0:
                value_len = len(str(value))
                font = pygame.font.Font('freesansbold.ttf', 48 - (5 * value_len))
                value_text = font.render(str(value), True, value_color)
                text_rect = value_text.get_rect(center=(j * 90 + 60, i * 90 + 150))
                screen.blit(value_text, text_rect)


# проверка на наличие клеток, которые можно соединить
def check_board(board):
    for x in range(4):
        for y in range(4):
            if board[x][y] == 0:
                return False
    for x in range(4):
        for y in range(3):
            if board[x][y] == board[x][y + 1] or board[y][x] == board[y + 1][x]:
                return False
    return True


run = True
pygame.mixer.music.load(os.path.join('data', 'music_two.mp3'))
pygame.mixer.music.play(-1)
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if username and score > max_score:
                con = sqlite3.connect("users_score.db")
                cur = con.cursor()
                cur.execute(f"""UPDATE score SET score = {score} WHERE name = '{username}'""")
                con.commit()
                con.close()
            else:
                con = sqlite3.connect("users_score.db")
                cur = con.cursor()
                cur.execute(f"""UPDATE score SET score = {max_score} WHERE name = '{username}'""")
                con.commit()
                con.close()
            print('Игра окончена')
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                moving = 'up'
            elif event.key == pygame.K_DOWN:
                moving = 'down'
            elif event.key == pygame.K_RIGHT:
                moving = 'right'
            elif event.key == pygame.K_LEFT:
                moving = 'left'

            if game_over_one and game_over_two:
                if event.key == pygame.K_RETURN:
                    if username and score > max_score:
                        con = sqlite3.connect("users_score.db")
                        cur = con.cursor()
                        cur.execute(f"""UPDATE score SET score = {score} WHERE name = '{username}'""")
                        con.commit()
                        con.close()
                    else:
                        con = sqlite3.connect("users_score.db")
                        cur = con.cursor()
                        cur.execute(f"""UPDATE score SET score = {max_score} WHERE name = '{username}'""")
                        con.commit()
                        con.close()
                    board_cells = [[0 for _ in range(4)] for _ in range(4)]
                    create_new_value = True
                    init_count = 0
                    score = 0
                    moving = ''
                    game_over_one = False
                    game_over_two = False

    screen.fill(pygame.Color((219, 215, 210)))
    clock.tick(fps)
    draw_board()
    draw_cell(board_cells)

    if create_new_value or init_count < 2:  # добавления новых значений
        board_cells, game_over_one = new_cells(board_cells)
        create_new_value = False
        init_count += 1

    if moving != '':  # проверяем направление для движения клеток со значениями
        board_cells = make_step(moving, board_cells)
        game_over_two = check_board(board_cells)
        moving = ''
        create_new_value = True

    if game_over_one and game_over_two:
        draw_over()

    if score > max_score:
        max_score = score

    pygame.display.flip()

pygame.quit()

