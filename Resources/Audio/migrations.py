import pygame

def play_background_music(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play(-1)

# Specifica il percorso del tuo file MP3
file_path = './BGMusic.mp3'

play_background_music(file_path)
input()
pygame.mixer.stop()