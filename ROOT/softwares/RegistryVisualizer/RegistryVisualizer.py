from .. import software_api
import tkinter as tk

app_icon = "RegistryVisualizer.png"
software_name = "Registry visualizer"
software_dir = "RegistryVisualizer"
is_GUI = True
min_size = None
max_size = None
default_size = None

def on_app_launch(frame:tk.Tk, width:int=100, height:int=100):
	# -------------------- "WINDOW" CREATION --------------------
	overall_frame = tk.Frame(
		frame,
		width=width,
		height=height
	)
	main_canvas = tk.Canvas(
		overall_frame,
		width=width - 15,
		height=height
	)
	main_canvas.place(x=0, y=0)

	scrollbar = tk.Scrollbar(overall_frame, orient=tk.VERTICAL, command=main_canvas.yview)
	scrollbar.place(height=height, x=width - 15, y=0)

	main_canvas.configure(yscrollcommand=scrollbar.set)
	main_canvas.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

	main_frame = tk.Frame(
		overall_frame,
		width=width,
		height=height
	)
	main_canvas.create_window((0, 0),
		window=main_frame,
		anchor="nw",
		width=width,
		height=height
	)
	scrollbar.lift()

	# -------------------- MAIN CODE --------------------
	title = tk.Label(
		main_frame,
		text = "REGISTRY VISUALIZER",
		font = ("Impact", 18)
	)
	title.pack()

	for key in software_api.REGISTRY:
		globals()[f"registry_{key}"] = tk.Label(
			main_frame,
			text = f"\"{key}\" : {software_api.REGISTRY[key]}",
		)
		globals()[f"registry_{key}"].pack()

	main_frame.pack()
	overall_frame.pack()
