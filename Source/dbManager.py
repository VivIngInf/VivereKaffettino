# -*- coding: utf-8 -*-


import simpleaudio as sa
import curses
import time
import random

from Modules.Interface.createDatabase import CreateAll
from Modules.Interface.dropAll import DropAll
from Modules.Interface.persistent import CreatePersistent

startTime = 0

asciiArt = """
  ___  ___      __  __   _   _  _   _   ___ ___ ___  \t
 |   \| _ )    |  \/  | /_\ | \| | /_\ / __| __| _ \ \t
 | |) | _ \    | |\/| |/ _ \| .` |/ _ \ (_ | _||   | \t
 |___/|___/    |_|  |_/_/ \_\_|\_/_/ \_\___|___|_|_\ \t
"""

try:
    # Specifica il percorso del tuo file MP3
    file_path = '../Resources/Audio/BGMusic.wav'

    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
except:
    print("\033[91mIl tuo sistema non puo' mandare in output la musica. Sei in connessione SSH?\033[0m")


def main(stdscr):

    global startTime


    selectedSomething = False
    error = False
    waitTime = 2

    # Configurazione iniziale di curses
    curses.curs_set(0)  # Nasconde il cursore
    stdscr.nodelay(1)   # Abilita il modalità non bloccante per la lettura di input

    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    # Lista delle opzioni
    options = ["Genera tabelle", "Genera elementi persistenti", "Elimina tabelle", "Esci"]
    selected_option = 0  # Opzione selezionata inizialmente

    while True:

        stdscr.clear()  # Pulisce lo schermo

        height, width = stdscr.getmaxyx()

        # Stampa l'ASCII art
        stdscr.addstr(0, 0, asciiArt, curses.color_pair(1) | curses.A_BOLD)

        # Stampa le opzioni con il cerchio verde solo nella selezionata
        for i, option in enumerate(options):
            if i == selected_option:
                stdscr.addstr(i + 7, 1, "● ", curses.color_pair(1) | curses.A_BOLD)
                stdscr.addstr(option, curses.color_pair(1) | curses.A_BOLD)
            else:
                stdscr.addstr(i + 7, 0, "○ " + option)

        if time.time() - startTime >= waitTime:
            selectedSomething = False
            if error is True:
                exit(-1)
            

        if selectedSomething is True or error is True:
            perc = ((time.time() - startTime) * 100) / 3

            if error:
                stdscr.addstr(12, 0, "Errore: Il DB non è ancora stato creato!\nIl programma verrà abortito.", curses.color_pair(2) | curses.A_BOLD)
            elif perc > 0:
                stdscr.addstr(12, 1, "Loading: ", curses.color_pair(1) | curses.A_BOLD)   

                loadString = ""
                i = 0            

                while i < int(perc/5):
                    i += 1
                    loadString += "██"

                stdscr.addstr(12, 10, loadString, curses.color_pair(1) | curses.A_BOLD)

        # Legge l'input da tastiera
        key = stdscr.getch()
        
        if key == curses.KEY_UP and selectedSomething is False and error is False:
            selected_option = (selected_option - 1) % len(options)
        elif key == curses.KEY_DOWN and selectedSomething is False and error is False:
            selected_option = (selected_option + 1) % len(options)
        elif key == 10 and selectedSomething is False and error is False:  # 10 corrisponde all'invio
            match selected_option:
                case 0:
                    CreateAll()
                    selectedSomething = True
                    startTime = time.time()
                case 1:
                    try:
                        CreatePersistent()
                        selectedSomething = True
                    except:
                        selectedSomething = False
                        error = True
                    finally:
                        startTime = time.time()
                case 2:
                    DropAll()
                    selectedSomething = True
                    startTime = time.time()
                case 3:
                    return  # Uscire dalla funzione e quindi dal programma
            
        stdscr.refresh()

try:
    curses.wrapper(main)
except:
    print("\033[91m ERRORE! Allarga il terminale per piacere!\033[0m")