import random
import tkinter as tk

# OPTIONAL SOUND (WORKS BEST ON WINDOWS)
try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    HAS_WINSOUND = False


# =========================
# CONSTANTS
# =========================
BOARD_W = 10
BOARD_H = 20

CELL_SIZE = 26

BASE_TICK_MS = 450
FAST_TICK_MS = 80

# SOMETIMES A "FAST" PIECE SPAWNS (FALLS MUCH FASTER)
FAST_PIECE_CHANCE = 0.18

BG_COLOR = "black"
DOT_COLOR = "#222222"
BLOCK_OUTLINE = "#EEEEEE"
TEXT_COLOR = "#EEEEEE"


# =========================
# SHAPES
# =========================

# - WE STORE A BASE SHAPE (IN A 4x4 GRID)
# - THEN WE COMPUTE ROTATIONS AND MIRRORING USING MATH
BASE_SHAPES = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(1, 1), (2, 1), (1, 2), (2, 2)],
    "T": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "J": [(1, 0), (1, 1), (1, 2), (0, 2)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
}


# =========================
# TRANSFORMS (4x4)
# =========================
def NORMALIZE_CELLS(CELLS):
    # AFTER ROTATION/MIRRORING, THE SHAPE MAY SHIFT INSIDE THE 4x4 GRID.
    # NORMALIZE MOVES IT BACK SO ITS TOP-LEFT CORNER STARTS AT (0,0).
    MIN_X = min(x for x, _ in CELLS)
    MIN_Y = min(y for _, y in CELLS)
    return [(x - MIN_X, y - MIN_Y) for x, y in CELLS]


def ROTATE_90(CELLS):
    # ROTATION IN A 4x4 GRID:
    # (x,y) -> (3-y, x)
    return [(3 - y, x) for x, y in CELLS]


def MIRROR_X(CELLS):
    # HORIZONTAL MIRROR (LEFT/RIGHT) IN A 4x4 GRID:
    # (x,y) -> (3-x, y)
    return [(3 - x, y) for x, y in CELLS]


def SHAPE_CELLS(TYPE, ROT_IDX, MIRRORED):
    # TAKE A BASE SHAPE, OPTIONALLY MIRROR IT, THEN ROTATE IT ROT_IDX TIMES.
    CELLS = BASE_SHAPES[TYPE][:]
    if MIRRORED:
        CELLS = MIRROR_X(CELLS)

    # IN THE OLD VERSION YOU USED MODULO ON "NUMBER OF ROTATIONS":
    # IF YOU ROTATE MORE TIMES THAN AVAILABLE, MODULO "WRAPS AROUND".
    # HERE ALL SHAPES SUPPORT UP TO 4 ROTATIONS, SO WE USE ROT_IDX % 4.
    for _ in range(ROT_IDX % 4):
        CELLS = ROTATE_90(CELLS)

    return NORMALIZE_CELLS(CELLS)


# =========================
# GAME LOGIC
# =========================
# CREATE LIST OF LISTS (PER THE W*H):
# EACH LIST IS A ROW OF CELLS IN THE BOARD.
# DEFAULT OF EACH CELL IS 0 (EMPTY).
def NEW_BOARD():
    return [[0 for _ in range(BOARD_W)] for _ in range(BOARD_H)]


def PIECE_CELLS(TYPE, ROT_IDX, MIRRORED, PX, PY):
    # CONVERT RELATIVE SHAPE CELLS INTO ABSOLUTE BOARD CELLS BY ADDING (PX,PY)
    REL = SHAPE_CELLS(TYPE, ROT_IDX, MIRRORED)
    return [(PX + dx, PY + dy) for dx, dy in REL]


# CHECK WHETHER THE PIECE CAN BE PLACED AT A SPECIFIC POSITION:
# - NOT OUTSIDE THE BOARD
# - NOT COLLIDING WITH LOCKED CELLS
def CAN_PLACE(BOARD, TYPE, ROT_IDX, MIRRORED, PX, PY):
    for (X, Y) in PIECE_CELLS(TYPE, ROT_IDX, MIRRORED, PX, PY):
        if X < 0 or X >= BOARD_W or Y < 0 or Y >= BOARD_H:
            return False
        if BOARD[Y][X] != 0:
            return False
    return True


# DEFAULT OF EACH CELL IS 0 (EMPTY).
# THIS FUNCTION "LOCKS" THE PIECE BY SETTING THOSE CELLS TO 1 (FILLED).
def LOCK_PIECE(BOARD, TYPE, ROT_IDX, MIRRORED, PX, PY):
    for (X, Y) in PIECE_CELLS(TYPE, ROT_IDX, MIRRORED, PX, PY):
        BOARD[Y][X] = 1


# WHEN A ROW IS FULL -> DELETE IT (CLEAR THE LINE)
def CLEAR_LINES(BOARD):
    NEW_ROWS = [ROW for ROW in BOARD if any(CELL == 0 for CELL in ROW)]
    CLEARED = BOARD_H - len(NEW_ROWS)
    for _ in range(CLEARED):
        NEW_ROWS.insert(0, [0 for _ in range(BOARD_W)])
    return NEW_ROWS, CLEARED


# =========================
# RENDERING (80s STYLE OUTLINE)
# =========================
class Screen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TETRIS 80S PLUS")

        self.canvas = tk.Canvas(
            self.root,
            width=BOARD_W * CELL_SIZE,
            height=BOARD_H * CELL_SIZE,
            bg=BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack()

        self.hud = tk.Label(
            self.root,
            text="SCORE: 0   MODE: NORMAL   MIRROR: OFF",
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            font=("Courier New", 13)
        )
        self.hud.pack(pady=6)

    def DRAW_DOT_GRID(self):
        DOT_R = 1
        for Y in range(BOARD_H):
            for X in range(BOARD_W):
                CX = X * CELL_SIZE + CELL_SIZE / 2
                CY = Y * CELL_SIZE + CELL_SIZE / 2
                self.canvas.create_oval(
                    CX - DOT_R, CY - DOT_R, CX + DOT_R, CY + DOT_R,
                    fill=DOT_COLOR, outline=""
                )

    def DRAW_BLOCK(self, X, Y):
        X1 = X * CELL_SIZE
        Y1 = Y * CELL_SIZE
        X2 = X1 + CELL_SIZE
        Y2 = Y1 + CELL_SIZE

        # OUTER FRAME
        self.canvas.create_rectangle(X1 + 2, Y1 + 2, X2 - 2, Y2 - 2, outline=BLOCK_OUTLINE)

        # INNER FRAME (GIVES "ASCII BOX" FEEL)
        self.canvas.create_rectangle(X1 + 6, Y1 + 6, X2 - 6, Y2 - 6, outline=BLOCK_OUTLINE)

    def RENDER(self, BOARD, ACTIVE_CELLS, SCORE, FAST_MODE, MIRRORED, GAME_OVER):
        self.canvas.delete("all")
        self.DRAW_DOT_GRID()

        # LOCKED CELLS
        for Y in range(BOARD_H):
            for X in range(BOARD_W):
                if BOARD[Y][X] != 0:
                    self.DRAW_BLOCK(X, Y)

        # ACTIVE PIECE CELLS
        for (X, Y) in ACTIVE_CELLS:
            self.DRAW_BLOCK(X, Y)

        MODE = "FAST" if FAST_MODE else "NORMAL"
        MIR = "ON" if MIRRORED else "OFF"
        self.hud.config(text=f"SCORE: {SCORE}   MODE: {MODE}   MIRROR: {MIR}")

        if GAME_OVER:
            self.canvas.create_text(
                (BOARD_W * CELL_SIZE) / 2,
                (BOARD_H * CELL_SIZE) / 2,
                text="GAME OVER\nPRESS R TO RESTART",
                font=("Courier New", 22),
                fill=TEXT_COLOR,
                justify="center"
            )


# =========================
# APP / LOOP
# =========================
class TetrisGame:
    def __init__(self):
        self.SCREEN = Screen()
        self.SOUND_ENABLED = True

        self.RESET_GAME()

        # CONTROLS
        self.SCREEN.root.bind("<Left>", lambda e: self.MOVE(-1, 0))
        self.SCREEN.root.bind("<Right>", lambda e: self.MOVE(1, 0))
        self.SCREEN.root.bind("<Down>", lambda e: self.MOVE(0, 1))
        self.SCREEN.root.bind("<Up>", lambda e: self.ROTATE())
        self.SCREEN.root.bind("<space>", lambda e: self.HARD_DROP())

        self.SCREEN.root.bind("m", lambda e: self.TOGGLE_MIRROR())
        self.SCREEN.root.bind("M", lambda e: self.TOGGLE_MIRROR())

        self.SCREEN.root.bind("r", lambda e: self.RESET_GAME())
        self.SCREEN.root.bind("R", lambda e: self.RESET_GAME())

        self.SCREEN.root.bind("s", lambda e: self.TOGGLE_SOUND())
        self.SCREEN.root.bind("S", lambda e: self.TOGGLE_SOUND())

        self.TICK()

    def BEEP(self, KIND="CLICK"):
        if not self.SOUND_ENABLED:
            return

        if HAS_WINSOUND:
            if KIND == "LOCK":
                winsound.Beep(500, 40)
            elif KIND == "CLEAR":
                winsound.Beep(800, 70)
            elif KIND == "GAMEOVER":
                winsound.Beep(220, 250)
            else:
                winsound.Beep(600, 20)
        else:
            # FALLBACK (MAC/LINUX): TK BELL
            try:
                self.SCREEN.root.bell()
            except Exception:
                pass

    def RESET_GAME(self):
        self.BOARD = NEW_BOARD()
        self.SCORE = 0
        self.GAME_OVER = False
        self.SPAWN_NEW()

        self.SCREEN.RENDER(
            self.BOARD,
            self.ACTIVE_CELLS(),
            self.SCORE,
            self.FAST_MODE,
            self.MIRRORED,
            self.GAME_OVER
        )

    def TOGGLE_SOUND(self):
        self.SOUND_ENABLED = not self.SOUND_ENABLED
        self.BEEP("CLICK")

    def SPAWN_NEW(self):
        self.TYPE = random.choice(list(BASE_SHAPES.keys()))
        self.ROT_IDX = 0
        self.MIRRORED = False

        self.PX = 3
        self.PY = 0

        # SOMETIMES SPAWN A FAST-FALLING PIECE
        self.FAST_MODE = (random.random() < FAST_PIECE_CHANCE)
        self.CURRENT_TICK_MS = FAST_TICK_MS if self.FAST_MODE else BASE_TICK_MS

        if not CAN_PLACE(self.BOARD, self.TYPE, self.ROT_IDX, self.MIRRORED, self.PX, self.PY):
            self.GAME_OVER = True
            self.BEEP("GAMEOVER")

    def ACTIVE_CELLS(self):
        if self.GAME_OVER:
            return []
        return PIECE_CELLS(self.TYPE, self.ROT_IDX, self.MIRRORED, self.PX, self.PY)

    def MOVE(self, DX, DY):
        if self.GAME_OVER:
            return

        NX = self.PX + DX
        NY = self.PY + DY

        if CAN_PLACE(self.BOARD, self.TYPE, self.ROT_IDX, self.MIRRORED, NX, NY):
            self.PX, self.PY = NX, NY
        else:
            # IF WE TRIED TO GO DOWN AND FAILED -> LOCK
            if DX == 0 and DY == 1:
                LOCK_PIECE(self.BOARD, self.TYPE, self.ROT_IDX, self.MIRRORED, self.PX, self.PY)
                self.BEEP("LOCK")

                self.BOARD, CLEARED = CLEAR_LINES(self.BOARD)
                if CLEARED > 0:
                    self.SCORE += 100 * (CLEARED ** 2)
                    self.BEEP("CLEAR")

                self.SPAWN_NEW()

    def ROTATE(self):
        if self.GAME_OVER:
            return

        NROT = self.ROT_IDX + 1
        if CAN_PLACE(self.BOARD, self.TYPE, NROT, self.MIRRORED, self.PX, self.PY):
            self.ROT_IDX = NROT
            self.BEEP("CLICK")
            return

        # SIMPLE "KICK" (TRY SHIFT LEFT/RIGHT ON ROTATION)
        for KX in (-1, 1, -2, 2):
            if CAN_PLACE(self.BOARD, self.TYPE, NROT, self.MIRRORED, self.PX + KX, self.PY):
                self.PX += KX
                self.ROT_IDX = NROT
                self.BEEP("CLICK")
                return

    def TOGGLE_MIRROR(self):
        if self.GAME_OVER:
            return

        NEW_M = not self.MIRRORED
        if CAN_PLACE(self.BOARD, self.TYPE, self.ROT_IDX, NEW_M, self.PX, self.PY):
            self.MIRRORED = NEW_M
            self.BEEP("CLICK")
            return

        # IF IT DOESN'T FIT, TRY LITTLE KICKS
        for KX in (-1, 1, -2, 2):
            if CAN_PLACE(self.BOARD, self.TYPE, self.ROT_IDX, NEW_M, self.PX + KX, self.PY):
                self.PX += KX
                self.MIRRORED = NEW_M
                self.BEEP("CLICK")
                return

    def HARD_DROP(self):
        if self.GAME_OVER:
            return
        while CAN_PLACE(self.BOARD, self.TYPE, self.ROT_IDX, self.MIRRORED, self.PX, self.PY + 1):
            self.PY += 1
        self.MOVE(0, 1)  # FORCE LOCK

    def TICK(self):
        # ALWAYS RENDER
        self.SCREEN.RENDER(
            self.BOARD,
            self.ACTIVE_CELLS(),
            self.SCORE,
            self.FAST_MODE,
            self.MIRRORED if not self.GAME_OVER else False,
            self.GAME_OVER
        )

        if not self.GAME_OVER:
            self.MOVE(0, 1)

        # NEXT TICK (DYNAMIC SPEED)
        NEXT_MS = 250 if self.GAME_OVER else self.CURRENT_TICK_MS
        self.SCREEN.root.after(NEXT_MS, self.TICK)

    def START(self):
        self.SCREEN.root.mainloop()


if __name__ == "__main__":
    GAME = TetrisGame()
    GAME.START()
