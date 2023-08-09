import tkinter as tk
from GUI_helper import *
from PIL import ImageTk, Image
import cv2


class MainGUI:
    def __init__(self, game_core):
        self.__game_core = game_core
        self.__root = tk.Tk()
        self.__setup_root()
        self.__add_top_bar()
        self.__add_left_canvas()
        self.__build_main_window()
        self.__video_capture = None
        self.__cam_activated = False

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

    def __add_left_canvas(self):
        self.__left_canvas = tk.Canvas(self.__root, bg=LEFT_CANVAS_COLOR, height=LEFT_CANVAS_HEIGHT,
                                       width=LEFT_CANVAS_WIDTH,
                                       highlightthickness=0)
        self.__add_camera()

    def __add_camera(self):
        tmp_image = Image.open("the_image.png")
        tmp_image = tmp_image.resize((CAMERA_WIDTH, CAMERA_HEIGHT))
        self.__img = ImageTk.PhotoImage(tmp_image)
        self.__camera = tk.Label(self.__root, image=self.__img, highlightthickness=4)

    def activate_camera(self):
        self.__video_capture = cv2.VideoCapture(0)
        self.__video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
        self.__video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
        self.__cam_activated = True
        self.__root.after(1000, lambda: self.__capture_video())

    def deactivate_camera(self):
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

    def __build_main_window(self):
        self.__question_title = tk.Label(self.__root, text="Question", fg="white", bg=MAIN_WINDOW_COLOR,
                                         font=("Arial Bold", 40))

        self.question_str = "The quick brown fox jumps over the "
        self.__question_text = tk.Label(self.__root, text=break_str(self.question_str, LINE_MAX_CHARS), fg="white",
                                        bg=MAIN_WINDOW_COLOR,
                                        font=("Coolvetica", 28), anchor=tk.W, justify="left")

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


    def update_welcome_statement(self, scene=0):
        if scene == 0:
            self.__welcome_statement = "Let's get to know you first! :)"
            self.__root.after(4000, lambda: self.update_welcome_statement(scene + 1))
        elif scene == 1:
            self.__welcome_statement = "I will ask for the name of each one of you.\n" \
                                       "When it's your turn, simply say your name out loud."
            self.__root.after(8000, lambda: self.update_welcome_statement(scene + 1))
        elif scene == 2:
            self.__welcome_statement = "In case you don't want to participate in the competition,\n" \
                                       "then you can declare that as well."
            self.__root.after(8000, lambda: self.update_welcome_statement(scene + 1))
        elif scene == 3:
            self.__game_core.extract_faces()
        elif scene == 4:
            self.__welcome_statement = "Waiting for at least two persons to be present .."

        self.__WS_statement.configure(text=self.__welcome_statement)

    def __show_game_screen(self):
        self.__left_canvas.pack(anchor=tk.W)
        self.__camera.place(anchor=tk.NW, y=TOP_BAR_HEIGHT + 40, x=(LEFT_CANVAS_WIDTH - CAMERA_WIDTH) // 2)
        self.__question_title.place(x=LEFT_CANVAS_WIDTH + 60, y=TOP_BAR_HEIGHT + 30)
        self.__question_text.place(x=LEFT_CANVAS_WIDTH + 60, y=TOP_BAR_HEIGHT + 170)

    def start_gui(self):
        self.__root.mainloop()

    def stop_gui(self):
        self.__root.quit()

    def take_shot(self):
        return self.__last_frame

    def names_setup(self):
        self.__WS_statement.destroy()
        self.__face_setup_canvas = tk.Canvas(self.__root, height=200, width=330, bg="#2a3966", highlightthickness=3)
        self.__face_setup_canvas.pack()
        self.__face_img = tk.Label(self.__root, highlightcolor="#2a3966", bg="#2a3966")

        self.__participant_name = tk.Label(self.__root, font=("Arial Rounded MT Bold", 30), text="",
                                           bg=MAIN_WINDOW_COLOR, fg="white")

        tmp_image = Image.open("recording_mic.png")
        self.__mic_icon_img = ImageTk.PhotoImage(tmp_image)
        self.__mic_icon_id = self.__face_setup_canvas.create_image(230, 60, anchor=tk.NW, image=self.__mic_icon_img,
                                                                   state="hidden")

        tmp_image_2 = Image.open("v_icon.png")
        self.__done_icon_img = ImageTk.PhotoImage(tmp_image_2)
        self.__done_icon_id = self.__face_setup_canvas.create_image(230, 60, anchor=tk.NW, image=self.__done_icon_img,
                                                                    state="hidden")

        x_cord = (WINDOW_WIDTH - 170) // 2 - 35
        y_cord = 390
        self.__face_img.place(x=x_cord, y=y_cord)
        self.__participant_name.pack(pady=(50, 0))

    def display_face(self, face_img):
        tmp_frame_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

        # Convert the frame to an image that tkinter can handle
        image_to_display = Image.fromarray(tmp_frame_rgb)
        image_to_display.thumbnail((170, 170))

        # Create a PhotoImage and update the tkinter label with the new image
        img_tk = ImageTk.PhotoImage(image=image_to_display)

        self.__face_img.config(image=img_tk)
        self.__face_img.image = img_tk

    def set_spoken_name(self, spoken_name):
        self.__participant_name.configure(text=spoken_name)

    def start_listening(self, toggle):
        if toggle == 0:
            self.__face_setup_canvas.itemconfigure(self.__mic_icon_id, state='hidden')
            self.__face_setup_canvas.itemconfigure(self.__done_icon_id, state='hidden')
            self.__face_setup_canvas.configure(highlightbackground="white")
        elif toggle == 1:
            self.__face_setup_canvas.itemconfigure(self.__mic_icon_id, state='normal')
            self.__face_setup_canvas.configure(highlightbackground="red")
        elif toggle == 2:
            self.__face_setup_canvas.itemconfigure(self.__mic_icon_id, state='hidden')
            self.__face_setup_canvas.configure(highlightbackground="#32db2c")
            self.__face_setup_canvas.itemconfigure(self.__done_icon_id, state='normal')
