import pygame
import numpy as np
from pieces import Piece, Pawn, Rook, Bishop, Queen, King, Knight
from engine import suggest_move, suggest_random_move,game_state
import time 



class UIState:
    def __init__(self):
        self.mouse_over_cell = None
        self.dragging = False
        self.selected_cell = None
        self.valid_cells = None
        self.score = 0.0

        pass


def load_sprites():
    return {
        "ROOK_WHITE": pygame.image.load(
            "sprites/100x100_rookwhite.png"
        ).convert_alpha(),
        "ROOK_BLACK": pygame.image.load(
            "sprites/100x100_rookblack.png"
        ).convert_alpha(),
        "KNIGHT_WHITE": pygame.image.load(
            "sprites/100x100_knightwhite.png"
        ).convert_alpha(),
        "KNIGHT_BLACK": pygame.image.load(
            "sprites/100x100_knightblack.png"
        ).convert_alpha(),
        "BISHOP_WHITE": pygame.image.load(
            "sprites/100x100_bishopwhite.png"
        ).convert_alpha(),
        "BISHOP_BLACK": pygame.image.load(
            "sprites/100x100_bishopblack.png"
        ).convert_alpha(),
        "QUEEN_WHITE": pygame.image.load(
            "sprites/100x100_queenwhite.png"
        ).convert_alpha(),
        "QUEEN_BLACK": pygame.image.load(
            "sprites/100x100_queenblack.png"
        ).convert_alpha(),
        "KING_WHITE": pygame.image.load(
            "sprites/100x100_kingwhite.png"
        ).convert_alpha(),
        "KING_BLACK": pygame.image.load(
            "sprites/100x100_kingblack.png"
        ).convert_alpha(),
        "PAWN_WHITE": pygame.image.load(
            "sprites/100x100_pawnwhite.png"
        ).convert_alpha(),
        "PAWN_BLACK": pygame.image.load(
            "sprites/100x100_pawnblack.png"
        ).convert_alpha(),
    }


def map_piece_to_sprite_tag(piece):
    if piece is None:
        return None

    c = None
    if isinstance(piece, Pawn):
        c = "PAWN"
    if isinstance(piece, Rook):
        c = "ROOK"
    if isinstance(piece, Knight):
        c = "KNIGHT"
    if isinstance(piece, Bishop):
        c = "BISHOP"
    if isinstance(piece, Queen):
        c = "QUEEN"
    if isinstance(piece, King):
        c = "KING"

    if piece.is_white():
        return c + "_WHITE"

    return c + "_BLACK"

def draw_check_highlight(screen, row, col):
    # soft red glow
    glow = pygame.Surface((100, 100), pygame.SRCALPHA)
    glow.fill((220, 50, 50, 80))   # soft red with alpha

    x = col * 100
    y = 700 - row * 100

    screen.blit(glow, (x, y))
    pygame.draw.rect(screen, (180, 30, 30), (x, y, 100, 100), 2)


def draw_checker_pattern(screen, uiState,board):
    COLOR_WHITE = (240, 220, 190)
    COLOR_BLACK = (160, 110, 95)

    screen.fill(COLOR_WHITE)

    winChance = 1.0 / (1.0 + np.exp(-uiState.score / 8.0))

    whiteRatio = 800 * winChance
    pygame.draw.rect(screen, (255, 255, 255), (800, 800 - whiteRatio, 20, whiteRatio))
    pygame.draw.rect(screen, (0, 0, 0), (800, 0, 20, 800 - whiteRatio))

    # Draw check board
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 1:
                continue

            x = col * 100
            y = 700 - row * 100
            pygame.draw.rect(screen, COLOR_BLACK, pygame.Rect(x, y, 100, 100))

    # Draw valid cells
    if uiState.valid_cells is not None:
        for cell in uiState.valid_cells:
            row, col = cell
            x = col * 100 + 50
            y = 700 - row * 100 + 50
            pygame.draw.circle(screen, (196, 196, 196), (x, y), 35)

    for is_white in (True, False):
        if board.is_king_check(is_white):
            king = board.find_king(is_white)
            row, col = king.cell
            draw_check_highlight(screen, row, col)

        


    # Highlight cell if any
    if uiState.dragging:
        row, col = uiState.selected_cell
        x = col * 100
        y = 700 - row * 100
        pygame.draw.rect(screen, (128, 0, 0), pygame.Rect(x, y, 100, 100), 3)

    if uiState.mouse_over_cell is not None:
        row, col = uiState.mouse_over_cell
        x = col * 100
        y = 700 - row * 100
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x, y, 100, 100), 3)

    if uiState.dragging:
        if uiState.mouse_over_cell is not None:
            row, col = uiState.mouse_over_cell
            xFrom = col * 100 + 50
            yFrom = 700 - row * 100 + 50
            row, col = uiState.selected_cell
            xTo = col * 100 + 50
            yTo = 700 - row * 100 + 50
            pygame.draw.line(screen, (255, 0, 0), (xFrom, yFrom), (xTo, yTo), 3)

    
    

def draw_board(screen, sprites, board):
    for row in range(8):
        for col in range(8):
            piece = board.get_cell((row, col))
            if piece is not None:
                tag = map_piece_to_sprite_tag(piece)
                sprite_to_draw = sprites[tag]

                x = col * 100
                y = 700 - row * 100
                screen.blit(sprite_to_draw, (x, y - 5))


def get_cell_under_mouse(uiState):
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

    x, y = [int(v // 100) for v in mouse_pos]
    if x >= 0 and y >= 0 and x <= 7 and y <= 7:
        uiState.mouse_over_cell = (7 - y, x)
    else:
        uiState.mouse_over_cell = None

    return uiState



def draw_text(screen,text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def draw_end_text(screen, text, width, height):
    font = pygame.font.SysFont("arial", 72, bold=True)
    text_surface = font.render(text, True, (220, 20, 20))
    rect = text_surface.get_rect(center=(width // 2, height // 2))
    screen.blit(text_surface, rect)



def run_game(board, manual=False):
    # Initialize Pygame
    pygame.init()

    # Set up the game window
    screen = pygame.display.set_mode((820, 800))

    sprites = load_sprites()

    pygame.display.set_caption("Hello Pygame")

    # Game loop
    running = True
    uiState = UIState()

    nextMove = None
    whitesTurn = True
    
    mode="playing"
    font_big = pygame.font.Font(None, 80)
    font_small = pygame.font.Font(None, 32)

    game_over = False
    result = None

    while running:
        if nextMove is None and not manual :
            #KI DENKZEIT
            t0 = time.time()
            nextMove = suggest_move(board)
            print("AI took", time.time() - t0, "seconds")
            #nextMove = suggest_random_move(board)
            #print("Next Move is ", nextMove)
            board.set_cell(nextMove.cell, nextMove.piece)
            uiState.score = nextMove.score
            displayScore = np.tanh(uiState.score / 8.0) * 4.0
            #print(f"Current Evaluation: {+displayScore:.2f}")
            whitesTurn = False
            
            #Check if the game is over after a move 
            result=game_state(board,whitesTurn)
            if result is not None and not game_over:
                game_over = True
                game_result = result

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and mode=="playing":
                piece = board.get_cell(uiState.mouse_over_cell)
                if piece and piece.white == whitesTurn:
                    uiState.dragging = True
                    uiState.valid_cells = piece.get_valid_cells()
                    uiState.selected_cell = uiState.mouse_over_cell

            if event.type == pygame.MOUSEBUTTONUP and uiState.dragging and mode=="playing":
                uiState.dragging = False

                if uiState.selected_cell != uiState.mouse_over_cell:
                    for valid_cell in uiState.valid_cells:
                        if (
                            uiState.mouse_over_cell[0] == valid_cell[0]
                            and uiState.mouse_over_cell[1] == valid_cell[1]
                        ):

                            piece = board.get_cell(uiState.selected_cell)
                            print(uiState.selected_cell, uiState.valid_cells)
                            print(piece)

                            piece.board.set_cell(uiState.mouse_over_cell, piece)
                            # eval = board.evaluate()
                            # print(f"White score: {eval:.4f}")
                            nextMove = None
                            whitesTurn = not whitesTurn
                            #Check if the game is over after a move 
                            result=game_state(board,whitesTurn)
                            print(result)
                            if result is not None and not game_over:
                                game_over = True
                                game_result = result
                uiState.valid_cells = None
            
            #Game paused when pressing esc button 
            if event.type ==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if mode=="playing":
                        mode="paused"
                        print("game paused")
                    elif mode=="paused":
                        mode="playing"
                        print("game resumed")
        
        

        draw_checker_pattern(screen, uiState,board)
        draw_board(screen, sprites, board)
        uiState = get_cell_under_mouse(uiState)

        #Pausing and resuming the Game 
        if mode=="paused" and not game_over:

            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            title_surf=font_big.render("PAUSED", True, (255, 255, 255))
            title_rect=title_surf.get_rect(center=(410, 320)) 
            screen.blit(title_surf, title_rect)
        
        #Checkmate/Stalemate Symbol if the game is over 
        if game_over:
            overlay = pygame.Surface((800, 800))
            overlay.set_alpha(255)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            if game_result == "checkmate":
                draw_end_text(screen, "CHECKMATE", 800, 800)
            elif game_result == "stalemate":
                draw_end_text(screen, "STALEMATE", 800, 800)

        pygame.display.flip()

        # Flip the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
