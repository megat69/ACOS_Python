from colormap import rgb2hex, hex2rgb
from functools import partial, update_wrapper

def pass_fx():
	pass

def blend_colors_in(window, color, destination_color, *widgets, ms_between:int=5,\
            change_window:bool=True, foreground:bool=False):
	# If the colors match, we stop here
	if sum(hex2rgb(color)) == sum(hex2rgb(destination_color)):
		return
	forwards = sum(hex2rgb(color)) < sum(hex2rgb(destination_color))


	# If they don't, we add 1 to each of them
	color = list(hex2rgb(color))
	for channel in range(len(color)):
		if color[channel] < hex2rgb(destination_color)[channel] and forwards:
			color[channel] += 1
		elif color[channel] > hex2rgb(destination_color)[channel] and not forwards:
			color[channel] -= 1

	# We modify the background of the window and widgets
	if change_window is True:
		window.config(bg = rgb2hex(*color))
	for widget in widgets:
		if foreground is False:
			widget.config(bg = rgb2hex(*color))
		else:
			widget.config(fg = rgb2hex(*color))

	# We recursively call the function
	window.after(
		ms_between,
		update_wrapper(
			partial(
				blend_colors_in,
				window,
				rgb2hex(*color),
				destination_color,
				*widgets,
				ms_between = ms_between,
				change_window = change_window,
				foreground = foreground
			), pass_fx
		)
	)
