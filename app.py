import sys
import os
import re
import pyautogui
import tkinter as tk
from datetime import datetime
from flask import Flask, request
from threading import Thread
from werkzeug.serving import make_server
from pystray import Icon, MenuItem as item, Menu
from PIL import Image
import win32event
import win32api
import winerror

# --- prevent dublicate Startup ---
mutex = win32event.CreateMutex(None, False, "Global\\MyUniqueBarcodeAppMutex")
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    print("Another instance is already running.")
    sys.exit(0)


# --- Flask App Setup ---
app = Flask(__name__)

# --- Global Configuration ---
config = {
    "host": "0.0.0.0",
    "port": 5000,
    "slice": "[:]"
}

flask_server = None  # Global server reference

# --- Flask Server Thread Class ---
class FlaskServer(Thread):
    """Runs Flask server in a background thread so GUI stays responsive."""
    def __init__(self, app, host, port):
        super().__init__(daemon=True)
        self.server = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

# --- Flask Route to Receive Barcode ---
@app.route('/', methods=['GET', 'POST'])
def receive_barcode():
    barcode = request.args.get('content', '') if request.method == 'GET' else request.form.get('content', '')

    try:
        digits = ''.join(re.findall(r'\d', barcode))  # Extract only digits
        digits_only = eval(f"digits{config['slice']}")  # Apply slicing rule
    except Exception as e:
        print(f"[ERROR] Failed to process barcode: {e}")
        digits_only = ''

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if digits_only:
        pyautogui.write(digits_only, interval=0.1)
    else:
        print(f"[{timestamp}] Invalid or empty barcode: '{barcode}'")

    return f"OK – {request.method} content: {barcode}", 200

# --- Path Utility for PyInstaller Support ---
def resource_path(relative_path):
    """Get absolute path to resource (works in dev and PyInstaller)."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Tray App Quit Action ---
def quit_app(icon, item):
    """Shutdown server and exit the application."""
    global flask_server
    if flask_server:
        flask_server.shutdown()
    icon.stop()
    sys.exit()

# --- Tray App Settings Window ---
def open_settings(icon, item):
    def settings_window():
        """Opens a settings window to change host, port, and slicing."""
        def save_settings():
            try:
                new_host = host_var.get()
                new_port = int(port_var.get())
                new_slice = slice_var.get()

                global flask_server
                if new_host != config['host'] or new_port != config['port']:
                    flask_server.shutdown()
                    flask_server = FlaskServer(app, new_host, new_port)
                    flask_server.start()
                    print(f"[INFO] Flask server restarted on {new_host}:{new_port}")

                config['host'] = new_host
                config['port'] = new_port
                config['slice'] = new_slice

                print("[INFO] Settings updated:", config)
                window.destroy()
            except Exception as e:
                print("[ERROR] Invalid settings:", e)

        def cancel_settings():
            window.destroy()

        # Create Tkinter Settings Window
        window = tk.Tk()
        window.title("Barcode App Settings")
        window.resizable(False, False)
        #window.iconbitmap(resource_path("icon.ico"))  # Optional: set app icon

        tk.Label(window, text="Host:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Label(window, text="Port:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Label(window, text="Slice (e.g. [-5:], [:4]):").grid(row=2, column=0, sticky='e', padx=5, pady=5)

        host_var = tk.StringVar(value=config['host'])
        port_var = tk.StringVar(value=str(config['port']))
        slice_var = tk.StringVar(value=config['slice'])

        tk.Entry(window, textvariable=host_var, width=20).grid(row=0, column=1, padx=5)
        tk.Entry(window, textvariable=port_var, width=20).grid(row=1, column=1, padx=5)
        tk.Entry(window, textvariable=slice_var, width=20).grid(row=2, column=1, padx=5)

        button_frame = tk.Frame(window)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Save", width=10, command=save_settings).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Cancel", width=10, command=cancel_settings).grid(row=0, column=1, padx=5)

        window.mainloop()

    Thread(target=settings_window).start()

# --- Setup System Tray Icon and Menu ---
def setup_tray():
    icon_path = resource_path("icon.png")
    image = Image.open(icon_path)

    menu = Menu(
        item('Settings', open_settings),
        item('Quit', quit_app)
    )

    icon = Icon("Barcode App", image, "Barcode App Running", menu)
    icon.run()

# --- Entry Point ---
if __name__ == '__main__':
    flask_server = FlaskServer(app, config['host'], config['port'])
    flask_server.start()
    setup_tray()
