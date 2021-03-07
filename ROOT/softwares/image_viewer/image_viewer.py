from .. import software_api
import tkinter as tk

app_icon = "ArtGallery.png"
software_name = "Art Gallery"
software_dir = "image_viewer"
is_GUI = True

def on_app_launch(frame:tk.Tk):
	disclaimer = tk.Label(frame, text=f"{software_name} is not done yet...").pack()
