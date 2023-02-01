from datetime import datetime, timedelta
import pygame
import pygame_menu
from chess.constants import WIDTH, HEIGHT, SQUARE_SIZE
from chess.game import Game

FPS = 60
clock = None


def get_row_col_from_mouse(pos):
    """Get position of mouse click
    :param pos:
    :return x,y:
    """
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def gameloop(win):
    """Game runs here
    :param win:
    """
    global clock

    run = True
    clock = pygame.time.Clock()
    game = Game(win)

    while run:
        clock.tick(FPS)  # max 60fps in game

        for event in pygame.event.get():  # loop checks if user did something
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
            if event.type == pygame.MOUSEBUTTONDOWN:  # on mouse click
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        if not game.display_check:
            start_time = datetime.now()
        else:
            if datetime.now() - start_time > timedelta(seconds=1.5):
                game.display_check = False

        game.update()  # updates screen

    pygame.quit()


def menu(win):
    """Create menu with pygame_menu package
    :param win:
    """
    my_theme = pygame_menu.themes.THEME_DARK.copy()
    my_theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
    my_theme.title_offset = (170, 100)
    my_theme.title_font_size = 80
    my_theme.title_font = pygame_menu.font.FONT_MUNRO
    my_theme.widget_font_size = 40
    my_theme.widget_font = pygame_menu.font.FONT_8BIT
    my_theme.widget_offset = (0, 50)

    my_menu = pygame_menu.Menu("pygame_chess", 800, 800, theme=my_theme)
    my_menu.add.image(image_path="assets/chess_menu.png", image_id="chess_menu", scale=(0.65, 0.65),
                      padding=(0, 0, 100, 0))
    my_menu.add.button("play", gameloop, win)
    my_menu.add.button("exit", pygame_menu.events.EXIT)
    my_menu.mainloop(win)


def main():
    """pygame inits itself and then creates window and title of window,
    window parameter is passed to other functions, and used throughout the game
    """
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("pygame_chess")
    menu(win)


if __name__ == '__main__':
    main()
