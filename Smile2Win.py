from GUI import MainGUI
from Participant import Participant, ParticipantsList

import tkinter as tk
from PIL import ImageTk, Image



if __name__ == '__main__':
    participants = ParticipantsList()
    main_gui = MainGUI()
    main_gui.show_welcome_screen()
    main_gui.start_gui()