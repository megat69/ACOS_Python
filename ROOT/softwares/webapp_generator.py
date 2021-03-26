from cefpython3 import cefpython as cef
import ctypes

try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk
import sys
import os
import platform
import logging as _logging

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

# Globals
logger = _logging.getLogger("tkinter_.py")

# Constants
# Tk 8.5 doesn't support png images
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"

def launch(frame, URL, **settings):
	logger.setLevel(_logging.CRITICAL)
	stream_handler = _logging.StreamHandler()
	formatter = _logging.Formatter("[%(filename)s] %(message)s")
	stream_handler.setFormatter(formatter)
	logger.addHandler(stream_handler)
	logger.info("CEF Python {ver}".format(ver=cef.__version__))
	logger.info("Python {ver} {arch}".format(
		ver=platform.python_version(), arch=platform.architecture()[0]))
	logger.info("Tk {ver}".format(ver=tk.Tcl().eval('info patchlevel')))
	assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"
	sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
	# Tk must be initialized before CEF otherwise fatal error (Issue #306)
	app = MainFrame(frame, URL)
	if MAC:
		settings["external_message_pump"] = True
	cef.Initialize(settings=settings)

class MainFrame(tk.Frame):
	def __init__(self, frame, URL):
		self.browser_frame = None
		self.frame = frame

		# Root
		tk.Grid.rowconfigure(frame, 0, weight=1)
		tk.Grid.columnconfigure(frame, 0, weight=1)

		# MainFrame
		tk.Frame.__init__(self, frame)
		self.master.bind("<Configure>", self.on_frame_configure)
		self.setup_icon()
		self.bind("<Configure>", self.on_configure)
		self.bind("<FocusIn>", self.on_focus_in)
		self.bind("<FocusOut>", self.on_focus_out)

		# BrowserFrame
		self.browser_frame = BrowserFrame(self, None, URL)
		self.browser_frame.grid(row=1, column=0,
		                        sticky=(tk.N + tk.S + tk.E + tk.W))
		tk.Grid.rowconfigure(self, 1, weight=1)
		tk.Grid.columnconfigure(self, 0, weight=1)

		# Pack MainFrame
		self.pack(fill=tk.BOTH, expand=tk.YES)

	def on_frame_configure(self, _):
		logger.debug("MainFrame.on_frame_configure")
		if self.browser_frame:
			self.browser_frame.on_frame_configure()

	def on_configure(self, event):
		logger.debug("MainFrame.on_configure")
		if self.browser_frame:
			width = event.width
			height = event.height
			self.browser_frame.on_mainframe_configure(width, height)

	def on_focus_in(self, _):
		logger.debug("MainFrame.on_focus_in")

	def on_focus_out(self, _):
		logger.debug("MainFrame.on_focus_out")

	def get_browser(self):
		if self.browser_frame:
			return self.browser_frame.browser
		return None

	def get_browser_frame(self):
		if self.browser_frame:
			return self.browser_frame
		return None

	def setup_icon(self):
		resources = os.path.join(os.path.dirname(__file__), "resources")
		icon_path = os.path.join(resources, "tkinter" + IMAGE_EXT)
		if os.path.exists(icon_path):
			self.icon = tk.PhotoImage(file=icon_path)
			# noinspection PyProtectedMember
			self.master.call("wm", "iconphoto", self.master._w, self.icon)

class BrowserFrame(tk.Frame):

	def __init__(self, mainframe, navigation_bar=None, URL="https://google.com"):
		self.navigation_bar = navigation_bar
		self.URL = URL
		self.closing = False
		self.browser = None
		tk.Frame.__init__(self, mainframe)
		self.mainframe = mainframe
		self.bind("<FocusIn>", self.on_focus_in)
		self.bind("<FocusOut>", self.on_focus_out)
		self.bind("<Configure>", self.on_configure)
		"""For focus problems see Issue #255 and Issue #535. """
		self.focus_set()

	def embed_browser(self):
		window_info = cef.WindowInfo()
		rect = [0, 0, self.winfo_width(), self.winfo_height()]
		window_info.SetAsChild(self.get_window_handle(), rect)
		self.browser = cef.CreateBrowserSync(window_info,  url=self.URL)
		assert self.browser
		self.browser.SetClientHandler(LifespanHandler(self))
		self.browser.SetClientHandler(LoadHandler(self))
		self.browser.SetClientHandler(FocusHandler(self))
		self.message_loop_work()

	def get_window_handle(self):
		if MAC:
			# Do not use self.winfo_id() on Mac, because of these issues:
			# 1. Window id sometimes has an invalid negative value (Issue #308).
			# 2. Even with valid window id it crashes during the call to NSView.setAutoresizingMask:
			#    https://github.com/cztomczak/cefpython/issues/309#issuecomment-661094466
			#
			# To fix it using PyObjC package to obtain window handle. If you change structure of windows then you
			# need to do modifications here as well.
			#
			# There is still one issue with this solution. Sometimes there is more than one window, for example when application
			# didn't close cleanly last time Python displays an NSAlert window asking whether to Reopen that window. In such
			# case app will crash and you will see in console:
			# > Fatal Python error: PyEval_RestoreThread: NULL tstate
			# > zsh: abort      python tkinter_.py
			# Error messages related to this: https://github.com/cztomczak/cefpython/issues/441
			#
			# There is yet another issue that might be related as well:
			# https://github.com/cztomczak/cefpython/issues/583

			# noinspection PyUnresolvedReferences
			from AppKit import NSApp
			# noinspection PyUnresolvedReferences
			import objc
			logger.info("winfo_id={}".format(self.winfo_id()))
			# noinspection PyUnresolvedReferences
			content_view = objc.pyobjc_id(NSApp.windows()[-1].contentView())
			logger.info("content_view={}".format(content_view))
			return content_view
		elif self.winfo_id() > 0:
			return self.winfo_id()
		else:
			raise Exception("Couldn't obtain window handle")

	def message_loop_work(self):
		cef.MessageLoopWork()
		self.after(10, self.message_loop_work)

	def on_configure(self, _):
		if not self.browser:
			self.embed_browser()

	def on_frame_configure(self):
		# Root <Configure> event will be called when top window is moved
		if self.browser:
			self.browser.NotifyMoveOrResizeStarted()

	def on_mainframe_configure(self, width, height):
		if self.browser:
			if WINDOWS:
				ctypes.windll.user32.SetWindowPos(
					self.browser.GetWindowHandle(), 0,
					0, 0, width, height, 0x0002)
			elif LINUX:
				self.browser.SetBounds(0, 0, width, height)
			self.browser.NotifyMoveOrResizeStarted()

	def on_focus_in(self, _):
		logger.debug("BrowserFrame.on_focus_in")
		if self.browser:
			self.browser.SetFocus(True)

	def on_focus_out(self, _):
		logger.debug("BrowserFrame.on_focus_out")
		"""For focus problems see Issue #255 and Issue #535. """
		if LINUX and self.browser:
			self.browser.SetFocus(False)

	def on_frame_close(self):
		logger.info("BrowserFrame.on_frame_close")
		if self.browser:
			logger.debug("CloseBrowser")
			self.browser.CloseBrowser(True)
			self.clear_browser_references()
			cef.Shutdown()

	def clear_browser_references(self):
		# Clear browser references that you keep anywhere in your
		# code. All references must be cleared for CEF to shutdown cleanly.
		self.browser = None

class LifespanHandler(object):

	def __init__(self, tkFrame):
		self.tkFrame = tkFrame

	def OnBeforeClose(self, browser, **_):
		logger.debug("LifespanHandler.OnBeforeClose")
		#self.tkFrame.quit()

class LoadHandler(object):

	def __init__(self, browser_frame):
		self.browser_frame = browser_frame

	def OnLoadStart(self, browser, **_):
		pass

class FocusHandler(object):
	"""For focus problems see Issue #255 and Issue #535. """

	def __init__(self, browser_frame):
		self.browser_frame = browser_frame

	def OnTakeFocus(self, next_component, **_):
		logger.debug("FocusHandler.OnTakeFocus, next={next}"
		             .format(next=next_component))

	def OnSetFocus(self, source, **_):
		logger.debug("FocusHandler.OnSetFocus, source={source}"
		             .format(source=source))
		if LINUX:
			return False
		else:
			return True

	def OnGotFocus(self, **_):
		logger.debug("FocusHandler.OnGotFocus")
		if LINUX:
			self.browser_frame.focus_set()

