import tkinter as tk
from tkinter import ttk

def submit():
    port_size = entry_port_size.get()
    port_location = port_location_var.get()
    budget = budget_slider.get()
    camera_perf = camera_var.get()
    battery_life = entry_battery.get()
    dimensions = entry_dimensions.get()
    transmission = transmission_var.get()
    storage = entry_storage.get()
    air_water_sensors = air_water_var.get()
    noise_level = noise_slider.get()
    charging = entry_charging.get()
    root.destroy()

# --- Setup ---
root = tk.Tk()
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # Per Windows: scala correttamente l'interfaccia
except:
    pass
root.title("Drone Port Configuration")
root.geometry("520x850")
root.configure(bg="#0d1b2a")

label_fg = "#ffffff"
bg_color = "#0d1b2a"
entry_bg = "#1b263b"
accent_color = "#415a77"

# --- Layout Helper ---
def add_label_input(label_text, widget):
    label = tk.Label(root, text=label_text, fg=label_fg, bg=bg_color, font=("Segoe UI", 10))
    label.pack(anchor="w", padx=20, pady=(10, 0))
    widget.pack(fill="x", padx=20, pady=5)

# --- Widgets ---
entry_port_size = tk.Entry(root, bg=entry_bg, fg=label_fg, insertbackground=label_fg)
add_label_input("Port Size:", entry_port_size)

port_locations = ["Baltic Sea", "West Mediterranean", "Central Mediterranean", "Adriatic Sea", 
                  "Great North Sea", "Celtic Sea", "Iberian Cost", "Aegean Sea", "Black Sea"]
port_location_var = tk.StringVar(value="Baltic Sea")
port_location_dropdown = tk.OptionMenu(root, port_location_var, *port_locations)
port_location_dropdown.config(bg=entry_bg, fg=label_fg, activebackground=accent_color, highlightbackground=entry_bg)
add_label_input("Port Location:", port_location_dropdown)

tk.Label(root, text="Budget (€):", fg=label_fg, bg=bg_color).pack(anchor="w", padx=20, pady=(10, 0))
budget_slider = tk.Scale(root, from_=0, to=20000, orient="horizontal", bg=entry_bg, fg=label_fg,
                         troughcolor=accent_color, highlightthickness=0)
budget_slider.pack(fill="x", padx=20, pady=5)

camera_var = tk.StringVar(value="Average")
camera_dropdown = tk.OptionMenu(root, camera_var, "Low", "Average", "High", "Very High")
camera_dropdown.config(bg=entry_bg, fg=label_fg, activebackground=accent_color, highlightbackground=entry_bg)
add_label_input("Camera Performance:", camera_dropdown)

entry_battery = tk.Entry(root, bg=entry_bg, fg=label_fg, insertbackground=label_fg)
add_label_input("Battery Life (minutes):", entry_battery)

entry_dimensions = tk.Entry(root, bg=entry_bg, fg=label_fg, insertbackground=label_fg)
add_label_input("Dimensions (cm³):", entry_dimensions)

transmission_var = tk.StringVar(value="Average")
transmission_dropdown = tk.OptionMenu(root, transmission_var, "No Transmission", "Slow", "Average", "High")
transmission_dropdown.config(bg=entry_bg, fg=label_fg, activebackground=accent_color, highlightbackground=entry_bg)
add_label_input("Data Transmission:", transmission_dropdown)

entry_storage = tk.Entry(root, bg=entry_bg, fg=label_fg, insertbackground=label_fg)
add_label_input("Storage (GB):", entry_storage)

air_water_var = tk.IntVar()
tk.Checkbutton(root, text="Air/Water Sensors Available", variable=air_water_var,
               bg=bg_color, fg=label_fg, activebackground=bg_color, selectcolor=entry_bg).pack(anchor="w", padx=20, pady=10)

tk.Label(root, text="Noise Level (dB):", fg=label_fg, bg=bg_color).pack(anchor="w", padx=20, pady=(10, 0))
noise_slider = tk.Scale(root, from_=30, to=100, orient="horizontal", bg=entry_bg, fg=label_fg,
                        troughcolor=accent_color, highlightthickness=0)
noise_slider.pack(fill="x", padx=20, pady=5)

entry_charging = tk.Entry(root, bg=entry_bg, fg=label_fg, insertbackground=label_fg)
add_label_input("Charging Time (min):", entry_charging)

tk.Button(root, text="Submit", command=submit, bg=accent_color, fg=label_fg,
          activebackground="#1b263b", font=("Segoe UI", 10, "bold")).pack(pady=20)

root.mainloop()
