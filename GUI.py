import tkinter as tk
from tkinter import ttk

def submit():
    """Collects all input values from the GUI widgets."""
    port_size = entry_port_size.get()
    port_location = port_location_var.get()
    budget = entry_budget.get()
    camera_perf = camera_var.get()
    battery_life = entry_battery.get()
    dimensions = entry_dimensions.get()
    transmission = transmission_var.get()
    storage = entry_storage.get()
    # Changed from air_water_var.get() (IntVar for Checkbutton) to air_water_combo_var.get() (StringVar for Combobox)
    air_water_sensors = air_water_combo_var.get()
    noise_level = noise_slider.get()
    charging = entry_charging.get()

    print("--- Form Data ---")
    print(f"Port Size: {port_size}")
    print(f"Port Location: {port_location}")
    print(f"Budget: {budget}")
    print(f"Camera Performance: {camera_perf}")
    print(f"Battery Life: {battery_life}")
    print(f"Dimensions: {dimensions}")
    print(f"Data Transmission: {transmission}")
    print(f"Storage: {storage}")
    print(f"Air/Water Sensors: {air_water_sensors}")
    print(f"Noise Level: {noise_level}")
    print(f"Charging Time: {charging}")
    print("-----------------")
    # For demonstration, we print data. You might want to process it further.
    # root.destroy() # You might not want to destroy the window immediately after submit
                     # unless that's your intended behavior for the final app.

# --- Setup ---
root = tk.Tk()
root.title("Drone Port Configuration")
# Adjust geometry for a 2-column layout. Width needs to be larger.
root.geometry("1100x800") # Increased width and height further for much larger font/widgets
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1) # For Windows: scales interface correctly
except Exception:
    pass
root.configure(bg="#0d1b2a") # Apply main background color

# --- Color and Style Definitions ---
label_fg = "#ffffff"       # White text for labels
bg_color = "#0d1b2a"       # Dark blue/black background
entry_bg = "#1b263b"       # Slightly lighter blue for input fields
accent_color = "#415a77"   # Accent color for sliders/buttons
button_active_bg = "#293d56" # Darker accent for button active state

# --- Configure ttk Styles ---
style = ttk.Style()
style.theme_use('clam') # 'clam' is often a good base for custom styling

# Significantly increased font size for most widgets
base_font = ("Segoe UI", 18) # FURTHER INCREASED font size
button_font = ("Segoe UI", 18, "bold") # Increased font size for button

# General style for all Ttk widgets to match the dark theme
style.configure('.', background=bg_color, foreground=label_fg, font=base_font)

# Style for Labels
style.configure('TLabel', background=bg_color, foreground=label_fg)

# Style for Entries
style.configure('TEntry', fieldbackground=entry_bg, foreground=label_fg, borderwidth=1, relief="flat", font=("Helvetica", 18))
style.map('TEntry',
    fieldbackground=[('focus', accent_color)],
    foreground=[('focus', label_fg)])

# Style for Combobox
# The font for text inside dropdown list is affected by 'TCombobox' style itself.
style.configure('TCombobox', fieldbackground=entry_bg, foreground=label_fg, selectbackground=entry_bg,
                selectforeground=label_fg, borderwidth=1, relief="flat", arrowcolor=label_fg, font=("Helvetica", 18))
style.map('TCombobox',
    fieldbackground=[('readonly', entry_bg), ('focus', accent_color)],
    selectbackground=[('readonly', accent_color), ('focus', accent_color)],
    selectforeground=[('readonly', label_fg), ('focus', label_fg)])

# Important: To control the font of the dropdown *list items*, sometimes a specific style is needed.
# This often uses the element option for the TCombobox.
# 'TCombobox.TListbox' is a common internal element for the dropdown list.
# This might not always work directly if the theme doesn't expose it easily.
# If this doesn't visually change the list, it's a theme limitation for this element.
style.configure('TCombobox.TListbox', font=base_font, background=entry_bg, foreground=label_fg,
                selectbackground=accent_color, selectforeground=label_fg)


# Style for Scale (Slider - Noise Level)
style.configure('Horizontal.TScale', background=bg_color, foreground=label_fg,
                troughcolor=entry_bg, sliderrelief="flat", sliderthickness=35) # Increased slider thickness further
style.map('Horizontal.TScale',
    background=[('active', bg_color)],
    foreground=[('active', label_fg)],
    troughcolor=[('active', accent_color)],
    slidercolor=[('active', label_fg)])

# Style for Checkbuttons (will be removed, but kept for reference if needed for other places)
style.configure('TCheckbutton', background=bg_color, foreground=label_fg,
                indicatorbackground=entry_bg, indicatorforeground=accent_color,
                focusthickness=0, borderwidth=0, font=base_font)
style.map('TCheckbutton',
    background=[('active', bg_color)],
    foreground=[('active', label_fg)],
    indicatorbackground=[('selected', accent_color), ('active', entry_bg)])


# Style for Buttons
style.configure('TButton', background=accent_color, foreground=label_fg,
                font=button_font, borderwidth=0, relief="flat")
style.map('TButton',
    background=[('active', button_active_bg)],
    foreground=[('active', label_fg)])


# --- Main Content Frame ---
content_frame = ttk.Frame(root)
content_frame.pack(fill="both", expand=True, padx=40, pady=30) # Increased padding for the whole frame

# --- Configure grid columns in content_frame ---
content_frame.grid_columnconfigure(0, weight=0) # Label for left widget
content_frame.grid_columnconfigure(1, weight=1) # Left widget
content_frame.grid_columnconfigure(2, weight=0, minsize=100) # Spacer column, increased minsize for a larger gap
content_frame.grid_columnconfigure(3, weight=0) # Label for right widget
content_frame.grid_columnconfigure(4, weight=1) # Right widget


# --- Layout Helper for Grid ---
def add_grid_label_input(label_text, widget, row, col_offset):
    label = ttk.Label(content_frame, text=label_text, font=("Helvetica", 18))
    label.grid(row=row, column=col_offset, sticky="w", padx=(0, 25), pady=(20, 10)) # Increased pady and right padx for label
    widget.grid(row=row, column=col_offset + 1, sticky="ew", padx=(25, 0), pady=(20, 10)) # Increased pady and left padx for widget

# --- Widgets ---
# Define StringVars and IntVars BEFORE they are used in widget creation
port_location_var = tk.StringVar(value="Baltic Sea", )
camera_var = tk.StringVar(value="Average")
transmission_var = tk.StringVar(value="Average")
# Changed from IntVar for Checkbutton to StringVar for Combobox
air_water_combo_var = tk.StringVar(value="Yes") # Default value for the new Combobox

current_row = 0

# Port Size
entry_port_size = ttk.Entry(content_frame)
add_grid_label_input("Port Size:", entry_port_size, row=current_row, col_offset=0)

# Port Location
port_locations = ["Baltic Sea", "West Mediterranean", "Central Mediterranean", "Adriatic Sea",
                  "Great North Sea", "Celtic Sea", "Iberian Cost", "Aegean Sea", "Black Sea"]
port_location_combobox = ttk.Combobox(content_frame, textvariable=port_location_var, values=port_locations,
                                     state="readonly", font=("Helvetica", 18))
port_location_combobox.set(port_locations[0])
add_grid_label_input("Port Location:", port_location_combobox, row=current_row, col_offset=3)
current_row += 1

# Budget
entry_budget = ttk.Entry(content_frame)
add_grid_label_input("Budget (€):", entry_budget, row=current_row, col_offset=0)

# Camera Performance
camera_options = ["Low", "Average", "High", "Very High"]
camera_combobox = ttk.Combobox(content_frame, textvariable=camera_var, values=camera_options,
                               state="readonly", font=("Helvetica", 18))
camera_combobox.set(camera_options[1])
add_grid_label_input("Camera Performance:", camera_combobox, row=current_row, col_offset=3)
current_row += 1

# Battery Life
entry_battery = ttk.Entry(content_frame)
add_grid_label_input("Battery Life (minutes):", entry_battery, row=current_row, col_offset=0)

# Dimensions
entry_dimensions = ttk.Entry(content_frame)
add_grid_label_input("Dimensions (cm³):", entry_dimensions, row=current_row, col_offset=3)
current_row += 1

# Data Transmission
transmission_options = ["No Transmission", "Slow", "Average", "High"]
transmission_combobox = ttk.Combobox(content_frame, textvariable=transmission_var, values=transmission_options,
                                     state="readonly", font=("Helvetica", 18))
transmission_combobox.set(transmission_options[2])
add_grid_label_input("Data Transmission:", transmission_combobox, row=current_row, col_offset=0)

# Storage
entry_storage = ttk.Entry(content_frame)
add_grid_label_input("Storage (GB):", entry_storage, row=current_row, col_offset=3)
current_row += 1

# --- Riorganizzazione degli ultimi widget ---

# Row for Air/Water Sensors (now a Combobox) and Charging Time
# Left: Air/Water Sensors (Combobox)
air_water_options = ["Yes", "No"]
air_water_sensor_combobox = ttk.Combobox(content_frame, textvariable=air_water_combo_var, values=air_water_options,
                                         state="readonly", font=("Helvetica", 18))
air_water_sensor_combobox.set(air_water_options[1]) # Default to "No"
add_grid_label_input("Air/Water Sensors:", air_water_sensor_combobox, row=current_row, col_offset=0)


# Right: Charging Time
entry_charging = ttk.Entry(content_frame)
add_grid_label_input("Charging Time (min):", entry_charging, row=current_row, col_offset=3)
current_row += 1

# Noise Level (Slider: Spans all columns for better visual width, as sliders typically need more space)
ttk.Label(content_frame, text="Noise Level (dB):").grid(row=current_row, column=0, columnspan=5, sticky="w", padx=20, pady=(30, 0)) # Increased pady for separation
noise_slider = ttk.Scale(content_frame, from_=30, to=100, orient="horizontal")
noise_slider.grid(row=current_row + 1, column=0, columnspan=5, sticky="ew", padx=20, pady=10)
current_row += 2 # Takes two rows (label + slider)


# Submit Button (spans all columns for centering)
ttk.Button(content_frame, text="Submit", command=submit).grid(
    row=current_row, column=0, columnspan=5, pady=40) # Increased pady

root.mainloop()