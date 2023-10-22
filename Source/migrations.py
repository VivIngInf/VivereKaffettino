import vlc

try:
    # Specifica il percorso del tuo file MP3
    file_path = '../Resources/Audio/BGMusic.mp3'

    player = vlc.MediaPlayer(file_path)
    player.play()
except:
    print("Il tuo sistema non può mandare in output la musica. Sei in connessione SSH?")

input("Inserisci la tua scelta: ")