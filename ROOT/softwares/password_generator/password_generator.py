from .. import software_api
import tkinter as tk
from PIL import Image, ImageTk
import os

app_icon = "logo.png"
software_name = "Password Generator"
software_dir = "password_generator"
is_GUI = True
min_size = None
max_size = None

def on_app_launch(frame:tk.Frame, width:int, height:int):
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	background_color = "#0E1349"
	frame.config(bg=background_color)
	# Generating left frame (image)
	left_frame = tk.Frame(
		frame,
		bg = background_color
	)
	canvas = tk.Canvas(
		left_frame,
		width=frame.winfo_width(),
		height=frame.winfo_width(),
		bg=background_color,
		bd=0,
		highlightthickness=0
	)
	globals()["image"] = tk.PhotoImage(
		file=app_icon
	).zoom(4).subsample(32, 32)
	canvas.create_image(
		frame.winfo_width() // 2,
		frame.winfo_height(),
		image=globals()["image"]
	)
	canvas.pack()
	left_frame.grid(row=0, column=0)

	# Generating right frame (main)
	right_frame = tk.Frame(
		frame,
		bg = background_color
	)

	# Right frame contents
	label_title = tk.Label(
		right_frame,
		text="Mot de passe",
		bg=background_color,
		font=("Arial", 50),
		fg="white"
	)
	label_title.pack()

	# Result box
	globals()["inputbox"] = tk.Entry(
		right_frame,
		bg=background_color,
		font=("Arial", 30),
		fg="white"
	)
	globals()["inputbox"].pack(fill=tk.X, pady=20)

	# Button to send
	pwd_button = tk.Button(
		right_frame,
		text="Générer",
		bg=background_color,
		font=("Arial", 27),
		fg="white",
		command=password_generate
	)
	pwd_button.pack(pady=25)

	right_frame.grid(row=0, column=1)

	os.chdir("../../../")


def password_generate():
	import random
	import string
	password_min = 30
	password_max = 64
	all_strings = string.ascii_letters + string.punctuation + string.digits
	password = "".join([random.choice(all_strings) for _ in range(random.randint(password_min, password_max))])
	globals()["inputbox"].delete(0, tk.END)
	globals()["inputbox"].insert(0, password)
	software_api.notify(software_name, "Password generated.")

"""class App:

	def __init__(self, window:tk.Frame):
		self.window = window
		self.width = self.window.winfo_width()
		self.height = self.window.winfo_height()

		# ajouter une frame principale
		self.frame = tk.Frame(self.window, bg=)

		# creation d'une ref' image
		self.image = tk.PhotoImage(
			file=f"ROOT/softwares/{software_dir}/{app_icon}"
		).zoom(30).subsample(32, 32)

		# creer une rightframe
		self.rightframe = tk.Frame(self.frame, bg="#0E1349")

		# creer une leftframe
		self.leftframe = tk.Frame(self.frame, bg="#0E1349")

		# creation des composants
		self.create_widget()

		# on place la leftframe à gauche
		self.leftframe.grid(row=0, column=0, sticky=tk.W)

		# on place la rightframe sur la boite à droite
		self.rightframe.grid(row=0, column=1, sticky=tk.W)

		# empacter la frame
		self.frame.pack(expand=tk.YES)

	def create_widget(self):
		self.create_title()
		self.create_entry()
		self.create_button_gen()
		self.create_canvas()

	def create_canvas(self):
		# creation d'image (canvas)
		canvas = tk.Canvas(self.leftframe, width=self.width, height=self.height, bg="#0E1349", bd=0, highlightthickness=0)
		canvas.create_image(self.width // 2, self.height // 2, image=self.image)
		canvas.pack()

	def create_title(self):
		# ajouter d'un titre
		label_title = tk.Label(self.rightframe, text="Mot de passe", bg="#0E1349", font=("Arial", 50), fg="#FFFFFF")
		label_title.pack(expand=tk.YES)

	def create_entry(self):
		# création d'un champs/d'une entrée/d'un input
		self.inputbox = tk.Entry(self.rightframe, bg="#0E1349", font=("Arial", 30), fg="#FFFFFF")
		self.inputbox.pack(expand=tk.YES, fill=tk.X, pady=20)

	def create_button_gen(self):
		# création d'un bouton
		pwd_button = tk.Button(self.rightframe, text="Générer", bg="#0E1349", font=("Arial", 27), fg="#FFFFFF",
		                    command=self.password_generate)
		pwd_button.pack(pady=25)

	def copy_to_clipboard(self):
		self.window.clipboard_clear()
		self.window.clipboard_append(self.inputbox.get())

	def password_generate(self):
		import random
		import string
		password_min = 30
		password_max = 64
		all_strings = string.ascii_letters + string.punctuation + string.digits
		password = "".join([random.choice(all_strings) for _ in range(random.randint(password_min, password_max))])
		self.inputbox.delete(0, tk.END)
		self.inputbox.insert(0, password)
"""

