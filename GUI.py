import tkinter as tk
from GUI_helper import *
from PIL import ImageTk, Image, ImageFont, ImageDraw
import cv2


class MainGUI:
    def __init__(self, game_core):
        self.__game_core = game_core
        self.__root = tk.Tk()
        self.__setup_root()
        self.__add_top_bar()  # Call this first to ensure it's at the top
        self.__add_player_text_box()  # This will now be below the top bar
        self.__add_left_canvas()
        self.__build_main_window()
        self.__video_capture = None
        self.__cam_activated = False
        self.__player_text_box_index = None
        
        self.__player_cards = []

    ### GAME'S GENERAL WINDOW SETTINGS ###
    def __setup_root(self):
        self.__root.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
        self.__root.title("Smile2Win")
        self.__root.configure(bg=MAIN_WINDOW_COLOR)

        # Hide default windows controls and border.
        hwnd: int = get_handle(self.__root)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style &= ~(WS_CAPTION | WS_THICKFRAME)
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)

    def __add_top_bar(self):
        self.__top_canvas = tk.Canvas(self.__root, bg=TOP_BAR_COLOR, height=TOP_BAR_HEIGHT, width=TOP_BAR_WIDTH,
                                      highlightbackground="#131e40")
        self.__top_canvas.create_text(25, 40, text="Smile2Win", fill="#204691", font=("Arial Bold", 20, "bold"),
                                      anchor=tk.W)
        self.__top_canvas.create_text(2000, 40, text="X", fill="#204691", font=("Arial Bold", 20, "bold"), anchor=tk.E)

        self.__top_canvas.bind("<Button 1>", lambda event_args: self.__check_click(event_args.x, event_args.y))
        self.__top_canvas.pack(fill=tk.X)  # Pack the top bar to fill the width

    def __check_click(self, x, y):
        if 1970 <= x <= 2030 and 10 <= y <= 70:
            self.stop_gui()

    ### CAMERA ###
    def __add_camera(self):
        tmp_image = Image.open("Resources/background.png")
        tmp_image = tmp_image.resize((CAMERA_WIDTH, CAMERA_HEIGHT))
        self.__img = ImageTk.PhotoImage(tmp_image)
        self.__camera = tk.Label(self.__root, image=self.__img, highlightthickness=4)
    
    def activate_camera(self):
        self.__video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.__video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
        self.__video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
        self.__cam_activated = True
        self.__root.after(1000, lambda: self.__capture_video())
        
    def deactivate_camera(self):
        self.__video_capture.release()
        self.__video_capture = None
        self.__cam_activated = False

    def __capture_video(self):
        if self.__cam_activated and self.__video_capture:
            self.__last_frame = self.__video_capture.read()[1]
            tmp_frame_rgb = cv2.cvtColor(self.__last_frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to an image that tkinter can handle
            image_to_display = Image.fromarray(tmp_frame_rgb)
            image_to_display.thumbnail((CAMERA_WIDTH, CAMERA_HEIGHT))

            # Create a PhotoImage and update the tkinter label with the new image
            img_tk = ImageTk.PhotoImage(image=image_to_display)
            self.__camera.config(image=img_tk)
            self.__camera.image = img_tk

            self.__root.after(10, lambda: self.__capture_video())

    ### WELCOME SCREEN ###
    def show_welcome_screen(self):
        self.activate_camera()
        self.__top_canvas.pack(fill=tk.BOTH)
        self.__WS_header = tk.Label(self.__root, text="Smile2Win", fg="white", bg=MAIN_WINDOW_COLOR,
                                    font=("Arial Bold", 45))
        self.__WS_header.pack(pady=(120, 30))

        self.__welcome_statement = "Hello!\n"
        self.__WS_statement = tk.Label(self.__root, text=self.__welcome_statement, fg="white", bg=MAIN_WINDOW_COLOR,
                                       font=("Arial", 25))
        self.__WS_statement.pack(pady=(30, 0))

        self.__camera.configure(bg=MAIN_WINDOW_COLOR, highlightthickness=0)
        self.__camera.place(x=(WINDOW_WIDTH - CAMERA_WIDTH) // 2, y=930)
        self.__root.after(2500, lambda: self.update_welcome_statement())

    def names_setup(self):
        self.__WS_statement.destroy()
        self.__face_setup_canvas = tk.Canvas(self.__root, height=350, width=350, bg="#2a3966", highlightthickness=3)
        self.__face_img = tk.Label(self.__root, highlightcolor="#2a3966", bg="#2a3966")

        self.__participant_name = tk.Label(self.__root, font=("Arial Rounded MT Bold", 30), text="",
                                           bg=MAIN_WINDOW_COLOR, fg="white")

        tmp_image = Image.open("Resources/recording_mic.png")
        self.__mic_icon_img = ImageTk.PhotoImage(tmp_image)
        self.__mic_icon_id = tk.Label(self.__root, image=self.__mic_icon_img)

        tmp_image_2 = Image.open("Resources/v_icon.png")
        self.__done_icon_img = ImageTk.PhotoImage(tmp_image_2)
        self.__done_icon_id = self.__face_setup_canvas.create_image(230, 60, anchor=tk.NW, image=self.__done_icon_img,
                                                                    state="hidden")
        self.__participant_name.pack(pady=(50, 0))

    def end_names_setup(self):
        self.__face_setup_canvas.destroy()
        self.__WS_header.destroy()
        self.__participant_name.destroy()
        self.__face_img.destroy()
        self.__show_game_screen()
        self.__game_core.start_playing_game()

    def start_listening_names(self, toggle):
        """
        This function is called everytime a participant wants to say his name.
        """
        if toggle == 1:
            x_cord = (WINDOW_WIDTH - 170) // 2 + 300
            y_cord = 390
            self.__mic_icon_id.place(x=x_cord, y=y_cord)
            self.__face_setup_canvas.configure(highlightbackground="red")

        elif toggle == 0:
            if self.__mic_icon_id.winfo_viewable:
                self.__mic_icon_id.place_forget()
                self.__face_setup_canvas.configure(highlightbackground="white")

        elif toggle == 2:
            self.__face_setup_canvas.itemconfigure(self.__mic_icon_id, state='hidden')
            self.__face_setup_canvas.configure(highlightbackground="#32db2c")
            self.__face_setup_canvas.itemconfigure(self.__done_icon_id, state='normal')

    def update_welcome_statement(self, scene=0, txt=None):
        if scene == 0:
            self.__welcome_statement = "Let's get to know you first! :)"
            self.__root.after(1, lambda: self.update_welcome_statement(scene + 1))

        elif scene == 1:
            self.__welcome_statement = "We are taking a picture for you\n" \
                                       "Look at the camera with a smile! :)"
            self.__root.after(1, lambda: self.update_welcome_statement(scene + 1))

        elif scene == 2:
            self.__game_core.extract_faces()

        elif txt:
            self.__welcome_statement = txt

        self.__WS_statement.configure(text=self.__welcome_statement)

    def set_spoken_name(self, spoken_name):
        self.__participant_name.configure(text=spoken_name)

    def display_face(self, face_img):
        tmp_frame_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

        # Convert the frame to an image that tkinter can handle
        image_to_display = Image.fromarray(tmp_frame_rgb)
        image_to_display.thumbnail((350, 350))
        
        new_width = image_to_display.width
        new_height = image_to_display.height

        # This is shared for the face & face's frame.
        x_cord = (WINDOW_WIDTH - new_width) // 2
        y_cord = self.__WS_header.winfo_y() + self.__WS_header.winfo_height()

        self.__face_setup_canvas.config(width=new_width + 4, height=new_height + 4)
        self.__face_setup_canvas.place(x=x_cord - 2, y=y_cord - 2)
        self.__face_img.place(x=x_cord, y=y_cord)

        # Updating location of spoken name
        self.__participant_name.pack(pady=(y_cord, 0))

        # Create a PhotoImage and update the tkinter label with the new image
        img_tk = ImageTk.PhotoImage(image=image_to_display)
        self.__face_img.config(image=img_tk)
        self.__face_img.image = img_tk

    ### GAME'S MAIN WINDOW ###
    def __build_main_window(self):
        self.__game_header = tk.Label(self.__root, text="Concept", fg="white", bg=MAIN_WINDOW_COLOR,
                                       font=("Arial Bold", 40))

        self.question_str = "The game's concept should be said in this phase over and over then again the fox is good but not really?"

        self.__bot_text = tk.Label(self.__root, text=self.question_str, fg="white",
                                   bg=MAIN_WINDOW_COLOR,
                                   font=("Coolvetica", 20), anchor=tk.W, justify="left", 
                                   wraplength=BOT_TEXT_MAX_WIDTH)

    def __show_game_screen(self):
        self.__left_canvas.pack(side=tk.LEFT, fill=tk.Y)
        self.__camera.place(anchor=tk.NW, y=TOP_BAR_HEIGHT + 40, x=(LEFT_CANVAS_WIDTH - CAMERA_WIDTH) // 2)
        self.__game_header.place(x=LEFT_CANVAS_WIDTH + 60, y=TOP_BAR_HEIGHT + 30)
        self.__bot_text.place(x=LEFT_CANVAS_WIDTH + 60, y=TOP_BAR_HEIGHT + 170)

        self.__reposition_player_text_box()

    def __add_left_canvas(self):
        self.__left_canvas = tk.Canvas(self.__root, bg=LEFT_CANVAS_COLOR, height=LEFT_CANVAS_HEIGHT,
                                       width=LEFT_CANVAS_WIDTH,
                                       highlightthickness=0)
        self.__left_canvas.pack_propagate(False)
        self.__add_camera()

    def __add_player_text_box(self):
        self.__player_text_box = tk.Text(self.__root, bg=MAIN_WINDOW_COLOR, 
                                         highlightthickness=0, width=40, height=5, borderwidth=0,
                                         wrap=tk.WORD, state="disabled")
        self.__player_text_box.tag_configure("white", foreground="white")
        self.__player_text_box.tag_configure("white", font=("Coolvetica", 17))

    def __reposition_player_text_box(self):
        padding_y_top = self.__bot_text.winfo_y() + self.__bot_text.winfo_height() 
        self.__player_text_box.pack(side=tk.LEFT, fill=tk.BOTH, padx=(60, 60), pady=(padding_y_top, 60), expand=True)  # Pack the text box to the right
        self.__player_text_box.config(bg=LEFT_CANVAS_COLOR)
        self.__player_text_box.see(tk.END)


    def update_participants_cards(self, participants_info):

        # First, remove any old cars.
        for card in self.__player_cards:
            self.__left_canvas.delete(card)
            
        self.__cards_font = ImageFont.truetype("arial.ttf", 40)
        pos_x = 315
        pos_y = self.__camera.winfo_height() + self.__camera.winfo_y()
        for p_info in participants_info:
            image, name, score = p_info
            card = self.__build_single_card(image, name, str(score))
            tk_image = ImageTk.PhotoImage(card)
    
            # Store a reference to the image to avoid garbage collection (otherwise it won't show)
            self.__player_cards.append(tk_image)
            
            # Add the image to the Tkinter canvas at the given position
            self.__left_canvas.create_image(pos_x, pos_y, image=tk_image)

            pos_y += CARD_HEIGHT + 20

            self.__player_cards.append(card)

    def __build_single_card(self, image, name, score):
        """Creates a new card with the specified image, name, and score."""
        # Create a blank card using the predefined macros
        card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), CARD_NORMAL_BG)
        draw = ImageDraw.Draw(card)

        # Image coming from the cv2, make it RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert the NumPy array to a PIL Image
        image_pil = Image.fromarray(image)

        image_pil = image_pil.resize((CARD_HEIGHT, CARD_HEIGHT))  # Resize to fit card height (square)
        card.paste(image_pil, (0, 0))  # Paste image at the top-left corner

        # Calculate positions for name and score
        name_x = CARD_HEIGHT + 10  # Position the name just to the right of the image
        name_y = 10  # Place the name near the top-left (not centered)

        score_x = CARD_WIDTH - SCORE_SQUARE_SIZE  # Place score square on the far right
        score_y = 0

        # Draw the name text at the top-left, next to the image
        draw.text((name_x, name_y), name, font=self.__cards_font, fill=CARD_TEXT_COLOR)

        # Draw the score square
        draw.rectangle(
            [score_x, score_y, score_x + SCORE_SQUARE_SIZE, score_y + SCORE_SQUARE_SIZE],
            fill=CARD_SCORE_BG
        )

        # Use font.getbbox to get the text dimensions
        bbox = draw.textbbox((0, 0), score, font=self.__cards_font)  # Get bounding box of score text
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate centered position for the score text inside the score square
        score_text_x = score_x + (SCORE_SQUARE_SIZE - text_width) // 2
        score_text_y = score_y + (SCORE_SQUARE_SIZE - text_height) // 2 - 10

        # Draw the score text in the center of the score square
        draw.text((score_text_x, score_text_y), score, font=self.__cards_font, fill=CARD_TEXT_COLOR)

        # Return the created card
        return card

    def update_bot_text(self, new_header, new_text):
        self.__game_header.config(text=new_header)
        self.__bot_text.config(text=new_text)
        self.__reposition_player_text_box()

    def insert_player_text(self, new_text, replace=False):
        self.__player_text_box.config(state="normal")

        current_index = self.__player_text_box.index("insert")
        if replace and self.__player_text_box_index:
            self.__player_text_box.delete(self.__player_text_box_index, current_index)
        
        self.__player_text_box.insert(tk.END, new_text, "white")
        self.__player_text_box.see(tk.END)

        if not replace:
            self.__player_text_box_index = self.__player_text_box.index("insert")

        self.__player_text_box.config(state="disabled")

    ### GUI'S GENERAL METHODS ###
    def start_gui(self):
        self.__root.mainloop()

    def stop_gui(self):
        self.__video_capture.release()
        self.__root.destroy()
        self.__game_core.end_game()

    def take_shot(self):
        return self.__last_frame
