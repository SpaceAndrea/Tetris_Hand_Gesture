from settings import *
import random


class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos):
        self.tetromino = tetromino
        self.pos = vec(pos) + INIT_POS_OFFSET
        self.next_pos = vec(pos) + NEXT_POS_OFFSET
        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = tetromino.image
        self.rect = self.image.get_rect()

        self.sfx_image = self.image.copy()
        self.sfx_image.set_alpha(110)
        self.sfx_speed = random.uniform(0.2, 0.6)
        self.sfx_cycles = random.randrange(6, 8)
        self.cycle_counter = 0

        self.next_pos = vec(pos) + NEXT_POS_OFFSET #visualizzare il tetromino in "hold"

    def sfx_end_time(self):
        if self.tetromino.tetris.app.anim_trigger:
            self.cycle_counter += 1
            if self.cycle_counter > self.sfx_cycles:
                self.cycle_counter = 0
                return True

    def sfx_run(self):
        self.image = self.sfx_image
        self.pos.y -= self.sfx_speed
        self.image = pg.transform.rotate(self.image, pg.time.get_ticks() * self.sfx_speed)

    def is_alive(self):
        if not self.alive:
            if not self.sfx_end_time():
                self.sfx_run()
            else:
                self.kill()

    def rotate(self, pivot_pos):
        translated = self.pos - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def set_rect_pos(self):
        pos = [self.next_pos, self.pos][self.tetromino.current]
        self.rect.topleft = pos * TILE_SIZE

    def update(self):
        self.is_alive()
        self.set_rect_pos()

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
                y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True


class Tetromino:
    def __init__(self, tetris, current=True):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.image = random.choice(tetris.app.images)
        self.blocks = [Block(self, pos) for pos in TETROMINOES[self.shape]]
        self.landing = False
        self.current = current
        self.rotation_state = 0  # Stato di rotazione (0, 1, 2, 3)

    #TENTATIVO NUMERO 1 (BASE):
    # def rotate(self):
    #     pivot_pos = self.blocks[0].pos
    #     new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

    #     if not self.is_collide(new_block_positions):
    #         for i, block in enumerate(self.blocks):
    #             block.pos = new_block_positions[i]

    #TENTATIVO NUMERO 2:
    # def rotate(self):
    #     pivot_pos = self.blocks[0].pos
    #     new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

    #     if not self.is_collide(new_block_positions):
    #         for i, block in enumerate(self.blocks):
    #             block.pos = new_block_positions[i]
    #     else:
    #         # Tentativo di wall kick spostando il pezzo a destra di un blocco
    #         kick_offset = vec(1, 0)  # Sposta di un blocco a destra
    #         kicked_positions = [pos + kick_offset for pos in new_block_positions]
    #         if not self.is_collide(kicked_positions):
    #             for i, block in enumerate(self.blocks):
    #                 block.pos = kicked_positions[i]
    #         else:
    #             # Tentativo di wall kick spostando il pezzo a sinistra di un blocco
    #             kick_offset = vec(-1, 0)  # Sposta di un blocco a sinistra
    #             kicked_positions = [pos + kick_offset for pos in new_block_positions]
    #             if not self.is_collide(kicked_positions):
    #                 for i, block in enumerate(self.blocks):
    #                     block.pos = kicked_positions[i]
        
    #     # Controlla se la nuova posizione dei blocchi colliderebbe con qualcosa
    #     if not self.is_collide(new_block_positions):
    #         for i, block in enumerate(self.blocks):
    #             block.pos = new_block_positions[i]
    #     else:
    #         # Tentativo di wall kick - Sposta il pezzo a destra
    #         kicked_positions = [pos + vec(1, 0) for pos in new_block_positions]
    #         if not self.is_collide(kicked_positions):
    #             for i, block in enumerate(self.blocks):
    #                 block.pos = kicked_positions[i]
    #         else:
    #             # Tentativo di wall kick - Sposta il pezzo a sinistra
    #             kicked_positions = [pos + vec(-1, 0) for pos in new_block_positions]
    #             if not self.is_collide(kicked_positions):
    #                 for i, block in enumerate(self.blocks):
    #                     block.pos = kicked_positions[i]

    #TENTATIVO NUMERO 3:
    def rotate(self):
        pivot_pos = self.blocks[0].pos  # Considera il primo blocco come pivot
        new_block_positions = []
        
        for block in self.blocks:
            translated = block.pos - pivot_pos  # Trasla il blocco in modo che il pivot sia l'origine
            rotated = translated.rotate(90)  # Ruota il blocco di 90 gradi
            new_pos = rotated + pivot_pos  # Trasla il blocco ruotato indietro alla posizione originale
            new_block_positions.append(new_pos)

        # Tentativi di Wall Kick
        wall_kicks = [
            vec(0, 0),  # Nessuno spostamento (tentativo iniziale)
            vec(1, 0),  # 1 a destra
            vec(-1, 0), # 1 a sinistra
            vec(0, -1), # 1 in alto
            vec(1, -1), # 1 a destra e 1 in alto
            vec(-1, -1) # 1 a sinistra e 1 in alto
        ]

        for kick in wall_kicks:
            kicked_positions = [pos + kick for pos in new_block_positions]
            if not self.is_collide(kicked_positions):
                for i, block in enumerate(self.blocks):
                    block.pos = kicked_positions[i]
                return  # Rotazione riuscita, esci dalla funzione

        # Se nessuna delle posizioni "kicked" funziona, la rotazione viene annullata


    def is_collide(self, block_positions):
        return any(map(Block.is_collide, self.blocks, block_positions))

    def move(self, direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.pos + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_positions)

        if not is_collide:
            for block in self.blocks:
                block.pos += move_direction
        elif direction == 'down':
            self.landing = True

    def update(self):
        self.move(direction='down')