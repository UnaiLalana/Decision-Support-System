import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QSlider, QPushButton, QVBoxLayout, QFormLayout,
    QScrollArea  # Import QScrollArea
)

import drone_selector
import location


class ModernSlider(QWidget):
    """Custom Widget for a modern-looking slider with label."""
    valueChanged = Signal(int)

    def __init__(self, label_text, min_val, max_val, initial_val, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.min_val = min_val
        self.max_val = max_val

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.value_label = QLabel(f"{self.label_text}: {initial_val}")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("color: #ffffff; font-size: 16px; margin-bottom: 5px;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(initial_val)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #4e94f3;
                height: 8px;
                background: #2b2b40; /* Default background for the groove */
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4e94f3;
                border: 1px solid #4e94f3;
                width: 20px;
                height: 20px;
                margin: -6px 0; /* Center the handle vertically */
                border-radius: 10px;
            }
             /* Corrected: Swap add-page and sub-page for left-to-right fill */
             QSlider::sub-page:horizontal {
                background: #3a6fd9; /* Color for the filled part (left of handle) */
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #2b2b40; /* Color for the unfilled part (right of handle) */
                border-radius: 4px;
            }
        """)
        # Connect the valueChanged signal to the update_label method
        self.slider.valueChanged.connect(self.update_label)
        # Connect the valueChanged signal to emit the custom signal
        self.slider.valueChanged.connect(self.valueChanged.emit)

        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

    def update_label(self, value):
        """Updates the label text to show the current slider value."""
        self.value_label.setText(f"{self.label_text}: {value}")

    def value(self):
        """Returns the current value of the slider."""
        return self.slider.value()


class DronePortConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Port Configuration")
        # Removed fixed size to allow scrolling
        self.setFixedSize(400, 700)
        self.setStyleSheet("background-color: #1e1e2f; color: #ffffff; font-family: 'Segoe UI';")

        # --- Create Scroll Area ---
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True) # Allow the widget inside to resize
        self.scroll_area.setStyleSheet("border: none;") # Optional: Remove border around scroll area

        # --- Create a container widget for the scrollable content ---
        self.container_widget = QWidget()
        self.scroll_area.setWidget(self.container_widget)

        # Main Layout for the container widget
        self.main_layout = QVBoxLayout(self.container_widget) # Set layout for the container widget
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15) # Increased spacing for mobile feel

        # Form Layout for inputs
        self.form_layout = QFormLayout()
        # Using AllNonFixedFieldsGrow as per user's successful fix
        self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)
        self.form_layout.setLabelAlignment(Qt.AlignLeft)
        self.form_layout.setVerticalSpacing(15)
        self.form_layout.setHorizontalSpacing(20)


        # --- Widgets ---
        self.port_size_combo = self._create_styled_combobox(["Small", "Medium", "Big", "Very Big"])
        self.form_layout.addRow("Port Size:", self.port_size_combo)

        self.port_location_combo = self._create_styled_combobox(["Baltic Sea", "West Mediterranean", "Central Mediterranean", "Adriatic Sea",
                  "Great North Sea", "Celtic Sea", "Iberian Cost", "Aegean Sea", "Black Sea"])
        self.form_layout.addRow("Port Location:", self.port_location_combo)

        self.budget_entry = self._create_styled_entry()
        self.form_layout.addRow("Budget (€):", self.budget_entry)

        self.camera_combo = self._create_styled_combobox(["Low", "Average", "High", "Very High"])
        self.form_layout.addRow("Camera Performance:", self.camera_combo)

        self.battery_entry = self._create_styled_entry()
        self.form_layout.addRow("Battery Life (min):", self.battery_entry)

        self.dimensions_entry = self._create_styled_entry()
        self.form_layout.addRow("Dimensions (cm³):", self.dimensions_entry)

        self.cargo_combo = self._create_styled_combobox(["No", "Low Weight", "High Weight"])
        self.form_layout.addRow("Cargo Capacity:", self.cargo_combo)

        self.transmission_combo = self._create_styled_combobox(["No Transmission", "Slow", "Average", "High"])
        self.form_layout.addRow("Data Transmission:", self.transmission_combo)

        self.storage_entry = self._create_styled_entry()
        self.form_layout.addRow("Storage (GB):", self.storage_entry)

        self.air_water_combo = self._create_styled_combobox(["Yes", "No"])
        self.form_layout.addRow("Air/Water Sensors:", self.air_water_combo)

        self.night_combo = self._create_styled_combobox(["Yes", "No", "Occasionally"])
        self.form_layout.addRow("Night usage", self.night_combo)

        self.charging_entry = self._create_styled_entry()
        self.form_layout.addRow("Charging Time (min):", self.charging_entry)

        # Add the form layout to the main layout of the container widget
        self.main_layout.addLayout(self.form_layout)

        # --- Noise Level Slider ---
        # Using the custom modern slider widget
        self.noise_slider_widget = ModernSlider("Noise Level (dB)", 30, 100, 65)
        self.main_layout.addWidget(self.noise_slider_widget)

        # Add some stretch to push the button to the bottom
        self.main_layout.addStretch()

        # --- Submit Button ---
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4e94f3;
                color: #ffffff;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 18px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #3a6fd9;
            }
            QPushButton:pressed {
                background-color: #2c5cb3;
            }
        """)
        self.submit_button.clicked.connect(self.submit_form)
        self.main_layout.addWidget(self.submit_button, alignment=Qt.AlignCenter) # Center the button

        # Set the scroll area as the main layout for the window
        self.window_layout = QVBoxLayout(self)
        self.window_layout.addWidget(self.scroll_area)
        self.window_layout.setContentsMargins(0, 0, 0, 0) # Remove margins around the scroll area


    def _create_styled_entry(self):
        """Helper to create consistently styled QLineEdit."""
        entry = QLineEdit()
        entry.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b40;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #4e94f3;
                border-radius: 5px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #4e94f3;
            }
        """)
        return entry

    def _create_styled_combobox(self, items):
        """Helper to create consistently styled QComboBox."""
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet("""
            QComboBox {
                background-color: #2b2b40;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #4e94f3;
                border-radius: 5px;
                font-size: 16px;
            }
            QComboBox::drop-down {
                border: 0px; /* Remove the default arrow border */
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png); /* You might need a custom arrow image */
                /* Or use a font icon if available */
            }
             QComboBox:focus {
                border: 2px solid #4e94f3;
            }
             QComboBox QAbstractItemView {
                background-color: #2b2b40;
                color: #ffffff;
                selection-background-color: #4e94f3;
            }
        """)
        return combo

    def submit_form(self):
        print("--- Form Submitted ---")
        # Access the values from the input fields
        port_size = self.port_size_combo.currentText()
        port_location = self.port_location_combo.currentText()
        budget = self.budget_entry.text()
        camera_performance = self.camera_combo.currentText()
        battery_life = self.battery_entry.text()
        dimensions = self.dimensions_entry.text()
        data_transmission = self.transmission_combo.currentText()
        storage = self.storage_entry.text()
        air_water_sensors = self.air_water_combo.currentText()
        charging_time = self.charging_entry.text()
        noise_level = self.noise_slider_widget.value() # Get value from custom widget
        night_vision = self.night_combo.currentText()
        cargo = self.cargo_combo.currentText()

        # Print the values (you can replace this with your backend logic)
        print("Port Size:", port_size)
        print("Port Location:", port_location)
        print("Budget:", budget)
        print("Camera Performance:", camera_performance)
        print("Battery Life:", battery_life)
        print("Dimensions:", dimensions)
        print("Data Transmission:", data_transmission)
        print("Storage:", storage)
        print("Air/Water Sensors:", air_water_sensors)
        print("Charging Time:", charging_time)
        print("Noise Level:", noise_level)
        print("Night Vision:", night_vision) # Added print for Night Vision




        resolution_map = {
            "Low": "480p",
            "Average": "720p",
            "High": "1080p",
            "Very High": "4K"
        }
        # Get the numerical value, default to 0 if text is not found (shouldn't happen with combobox)
        camera_performance_mapped = resolution_map.get(camera_performance, "480p") # Default to "480p"


        # Collect data into a dictionary
        user_input_from_ui = {
            "Port Size": port_size,
            "Port Location": port_location,
            "Budget (€)": budget,
            "Camera Performance": camera_performance_mapped, # Use the mapped value
            "Battery Life (min)": battery_life,
            "Dimensions (cm³)": dimensions, # Check this key name, might need to match backend exactly
            "Data Transmission": data_transmission,
            "Storage (GB)": storage,
            "Air/Water Sensors": air_water_sensors,
            "Charging Time (min)": charging_time,
            "Noise level": noise_level,
            "Night Vision": night_vision, # Include Night Vision in the dictionary
            "Cargo": cargo
            # Add other fields from the UI here if you add them later
        }

        weights_gui = { # Not yet implemented in the GUI
            "Payload Capacity": 0.7,
            # Add weights for other features if fuzzy logic is extended
        }

        res = drone_selector.get_top_drones(transform_user_input(user_input_from_ui), weights_gui)
        for drone in res:
            print(f"\nDrone ID: {drone['Drone ID']}")
            print(f"Total Score: {drone['Total Score (%)']}%")
            for expl in drone["Explanation"]:
                print("-", expl)


def transform_user_input(user_input_gui):
    radius_map = {
        "Small": [1, 150],
        "Medium": [5, 400],
        "Big": [7, 600],
        "Very Big": [10, 800]
    }

    transmission_map = {
        "No Transmission": [0, 0],
        "Slow": [1, 20],
        "Average": [1, 50],
        "High": [1, 85]
    }

    loc = location.get_historical_weather_open_meteo(user_input_gui["Port Location"])
    wind = loc["average_max_wind_kmh"]
    temp = loc["average_min_temp_C"]
    rtt = transmission_map.get(user_input_gui["Data Transmission"])[0]
    speed = transmission_map.get(user_input_gui["Data Transmission"])[1]
    user_input = {
        "Flight Radius": radius_map.get(user_input_gui["Port Size"][0], 0),
        "Flight height": radius_map.get(user_input_gui["Port Size"][1], 0),
        "Thermal/Night Camera": 0.0 if user_input_gui["Night Vision"] != "No" else 1.0,
        "Max wind resistance": wind,
        "Budgets options": user_input_gui["Budget (€)"],
        "Camera Quality": user_input_gui["Camera Performance"],
        "ISO range": 25600 if user_input_gui["Night Vision"] == "Yes" else (
            6400 if user_input_gui["Night Vision"] == "Occasionally" else 3200),
        "Battery Life": user_input_gui["Battery Life (min)"],
        "Payload Capacity": 1 if user_input_gui["Cargo"] == "No" else (
            10 if user_input_gui["Cargo"] == "Low Weight" else 23),
        "Dimensions": user_input_gui["Dimensions (cm³)"],
        "Real-time data transmission": rtt,
        "Transmission bandwidth": speed,
        "Data storage ability": user_input_gui["Storage (GB)"],
        "Air/Water quality sensor availability": 1 if user_input_gui["Air/Water Sensors"] == "Yes" else 0,
        "Noise level": user_input_gui["Noise level"],
        "Operating Temperature": temp,
        "Class Identification Label": get_drone_class_from_volume(user_input_gui["Dimensions (cm³)"]),
        "Charging Time": user_input_gui["Charging Time (min)"],
        "Automatic Landing/Takeoff": 1,
        "GPS Supported Systems": "GPS+Galileo",
        "Automated Path Finding": 1 if int(user_input_gui["Budget (€)"]) >= 8000 else 0,
    }

    return user_input

def get_drone_class_from_volume(volume_cm3: float) -> str:
        """
        Determines the drone class (C0 to C4) based on its volume in cm³.

        Args:
            volume_cm3 (float): The volume of the drone in cubic centimeters.

        Returns:
            str: The corresponding drone class (e.g., "C0", "C1", "C2", "C3", "C4").
                 Returns "Unknown" if the input volume is not a valid number.
        """
        try:
            volume = float(volume_cm3)
        except (ValueError, TypeError):
            print(f"Warning: Invalid volume input '{volume_cm3}'. Returning 'Unknown'.")
            return "Unknown"

        if volume <= 0:
            # Drones must have a positive volume. Assign to smallest class or handle as error.
            # For this function, we'll assign to C0 as the smallest possible class.
            return "C0"
        elif volume <= 5000:  # Up to 5000 cm³
            return "C0"
        elif volume <= 8750:  # From 5001 cm³ to 8750 cm³
            return "C1"
        elif volume <= 12500:  # From 8751 cm³ to 12500 cm³
            return "C2"
        elif volume <= 16250:  # From 12501 cm³ to 16250 cm³
            return "C3"
        else:  # Greater than 16250 cm³ (up to 20000 and beyond)
            return "C4"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    drone_port_config = DronePortConfig()
    drone_port_config.show()
    sys.exit(app.exec())
