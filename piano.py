import pygame

def draw_piano(size, active_notes):
    #print(active_notes)
    surface = pygame.Surface(size)

    # Most modern pianos have a row of 52 white keys and 36 black keys, 88 total
    TOTAL_KEYS = 88
    TOTAL_WHITE_KEYS = 52
    WHITE_KEY_WIDTH = size[0] / TOTAL_WHITE_KEYS
    BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * 2/3
    WHITE_KEY_HEIGHT = size[1]
    BLACK_KEY_HEIGHT = WHITE_KEY_HEIGHT * 5/7
    OCTAVE_COUNT = 7

    black_keys_pattern = [0, 1, 0] + [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0] * OCTAVE_COUNT + [0]

    white = 0
    for k in range(TOTAL_KEYS):
        is_active = k in active_notes

        if not black_keys_pattern[k]:
            key_rect = [white * WHITE_KEY_WIDTH, 0, 
                        WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT]
            pygame.draw.rect(surface, "lime" if is_active else "white", key_rect)
            pygame.draw.rect(surface, (96,96,96), key_rect, 1)
            white += 1

    white = 0
    for k in range(TOTAL_KEYS):
        is_active = k in active_notes
        if black_keys_pattern[k]:
            key_rect = [white * WHITE_KEY_WIDTH - BLACK_KEY_WIDTH/2, -4,
                        BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT]
            pygame.draw.rect(surface, 'red' if is_active else 'black', key_rect, 0, 3)
        else:
            white += 1

    return surface
