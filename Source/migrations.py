import vlc

# Specifica il percorso del tuo file MP3
file_path = '../Resources/Audio/BGMusic.mp3'

player = vlc.MediaPlayer(file_path)
player.play()

input()