import tkinter as tk
from tkinter import ttk
import serial
from tkinter import font as tkfont
from PIL import ImageGrab
import numpy as np
import cv2

# pyinstaller --one-file -w app.py in powershell

def get_dominant_screen_color(scale_factor=0.1):
    # Grab the screen image
    screen = ImageGrab.grab()
    # Resize the image to speed up the process
    screen = screen.resize((int(screen.width * scale_factor), int(screen.height * scale_factor)))
    # Convert the image to numpy array
    screen = np.array(screen)
    # Calculate the mean of the image
    mean_color = np.mean(screen, axis=(0, 1))
    # Convert the mean color to integer
    mean_color = mean_color.astype(int)
    
    hsv_mean_color = cv2.cvtColor(np.uint8([[mean_color]]), cv2.COLOR_RGB2HSV)
    
    # increase the saturation and value
    hsv_mean_color[0][0][1] = 255
    hsv_mean_color[0][0][2] = 255
    
    # convert back to RGB
    mean_color = cv2.cvtColor(hsv_mean_color, cv2.COLOR_HSV2RGB)
    mean_color = mean_color[0][0]
    
    return tuple(mean_color)

def parse_rgb(rgb):
    if rgb[0] == "#":
        rgb = rgb[1:]
    return tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))

def send_command(command):
    try:
        ser.write(command.encode())
        status_label.config(text="Command sent: " + command)
    except:
        status_label.config(text="Error: Failed to send data.")
        try:
            ser.close()
        except:
            pass

def send_rgb(speed, rgb):
    speed = 21 - speed
    rgb = parse_rgb(rgb)
    if rgb:
        send_command("2," + str(speed) + "," + str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2]))
    else:
        status_label.config(text="No input provided.")
    selected_mode.set("solid")
    
def send_immersive(speed):
    rgb = get_dominant_screen_color()
    if rgb:
        send_command("3," + str(21 - speed) + "," + str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2]))
        selected_mode.set("immersive")
    else:
        status_label.config(text="Error: No color detected.")


def send_rainbow(speed):
    speed = 21 - speed
    send_command("0," + str(speed) + ",0,0,0")
    selected_mode.set("rainbow")
    

def send_pulse(speed, rgb):
    speed = 21 - speed
    rgb = parse_rgb(rgb)
    if rgb:
        send_command("1," + str(speed) + "," + str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2]))
    else:
        status_label.config(text="No input provided.")
    selected_mode.set("pulse")
    

def on_closing():
    try:
        ser.close()
    except:
        pass
    root.destroy()
    
def update_color():
    r = red_scale.get()
    g = green_scale.get()
    b = blue_scale.get()
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    color_display.config(bg=hex_color)
    color_var.set(hex_color)
    status_label.config(text="RGB: " + str((r, g, b)))

def periodic_update():
    if selected_mode.get() == "immersive":
        send_immersive(speed_var.get())
    # Schedule this function to be called again after 1000 milliseconds (1 second)
    root.after(1500, periodic_update)

# Call periodic_update initially when setting up your application

try:
    ser = serial.Serial('COM4', 9600)
except Exception as e:
    print("Error: Could not open serial port -", e)

root = tk.Tk()
root.title("Smart Lights")

selected_mode = tk.StringVar(value="rainbow")

periodic_update()

root.protocol("WM_DELETE_WINDOW", on_closing)

custom_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
custom_font_normal = tkfont.Font(family="Helvetica", size=12)

# Style
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton",
                font=('Helvetica', 12),
                padding=10,
                background="#008CBA",
                foreground="white",
                borderwidth=0,)

style.map("TButton",
          background=[('active', '#005f7f')],
          relief=[('pressed', 'flat')])



# Using grid for mode label
mode_label = tk.Label(root, text="Lighting effect:", font=custom_font)
mode_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=10)  # Placed at the top with west alignment
mode_label_display = tk.Label(root, textvariable=selected_mode, font=custom_font_normal)
mode_label_display.grid(row=0, column=1, columnspan=3, sticky="w", padx=10, pady=10)  # Placed at the top with west alignment

# RGB scales
red_scale = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, label="Red", command=lambda x: update_color())
red_scale.grid(row=2, column=0, padx=10)
red_scale.set(0)  # Set initial red value for purple
green_scale = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, label="Green", command=lambda x: update_color())
green_scale.grid(row=2, column=1, padx=10)
green_scale.set(0)   # Set initial green value for purple
blue_scale = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, label="Blue", command=lambda x: update_color())
blue_scale.grid(row=2, column=2, padx=10)
blue_scale.set(0)  # Set initial blue value for purple

# Styling the scales
for scale in (red_scale, green_scale, blue_scale):
    scale.config(troughcolor="#008CBA", sliderlength=20, width=20, length=120, highlightthickness=0)
    
red_scale.config(troughcolor="#ED1A33")
green_scale.config(troughcolor="#00A859")
blue_scale.config(troughcolor="#1A21ED")
    
color_var = tk.StringVar(value="#000000")  # Default color

# Color display
color_display = tk.Canvas(root, width=600, height=30, bg="#000000")  # Default purple background
color_display.grid(row=1, column=0, columnspan=4, pady=10, padx=10)

# Speed control in line with RGB scales
speed_var = tk.IntVar(value=10)
speed_scale = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, label="Speed", variable=speed_var)
speed_scale.grid(row=2, column=3, padx=10, pady=10)

# Styling the speed scale
speed_scale.config(troughcolor="#6E6E6E", sliderlength=20, width=20, length=120, highlightthickness=0)

# Button controls
rgb_button = ttk.Button(root, text="Solid", command=lambda: send_rgb(speed_var.get(), color_var.get()))
rgb_button.grid(row=5, column=0, padx=10, pady=10)
rainbow_button = ttk.Button(root, text="Rainbow", command=lambda: send_rainbow(speed_var.get()))
rainbow_button.grid(row=5, column=1, padx=10)
pulse_button = ttk.Button(root, text="Pulse", command=lambda: send_pulse(speed_var.get(), color_var.get()))
pulse_button.grid(row=5, column=2, padx=10)

# Add a button for Immersive mode
immersive_button = ttk.Button(root, text="Immersive", command=lambda: send_immersive(speed_var.get()))
immersive_button.grid(row=5, column=3, padx=10)

status_label = tk.Label(root, text="")
status_label.grid(row=6, column=0, columnspan=4, pady=10)

root.mainloop()
