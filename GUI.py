import os
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QSlider, QPushButton, QVBoxLayout, QFormLayout,
    QScrollArea, QMessageBox, QFrame  # Import QScrollArea
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

    def load_weights_from_file(self):
        filepath = "weights.conf"
        weights = {}
        if not os.path.exists(filepath):
            print(f"Error: Weight configuration file '{filepath}' not found.")
            print("Please create the file with the correct weights.")
            # Return an empty dict or raise an error, depending on desired behavior
            # For now, let's return a default (empty) dict to avoid crashing
            return {}

        with open(filepath, 'r') as f:
            # Skip comment lines
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                try:
                    # Expecting format: "Criterion Name": Value
                    # Find the first colon to split key and value
                    parts = line.split(':', 1)
                    if len(parts) != 2:
                        print(f"Warning: Skipping malformed line in weights file: {line}")
                        continue

                    key_str = parts[0].strip()
                    value_str = parts[1].strip()

                    # Remove quotes from the key string if present
                    if key_str.startswith('"') and key_str.endswith('"'):
                        key = key_str[1:-1]
                    else:
                        key = key_str  # Or raise an error if quotes are mandatory

                    weight = float(value_str)
                    weights[key] = weight
                except ValueError:
                    print(f"Warning: Skipping line with invalid weight value: {line}")
                except Exception as e:
                    print(f"An unexpected error occurred while parsing line: {line} - {e}")
        return weights


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
        }

        weights_gui = self.load_weights_from_file()

        res = drone_selector.get_top_drones(transform_user_input(user_input_from_ui), weights_gui)
        for drone in res:
            print(f"\nDrone ID: {drone['Drone ID']}")
            print(f"Total Score: {drone['Total Score (%)']}%")
            for expl in drone["Explanation"]:
                print("-", expl)
        if res:
            # Create and show the results window
            self.results_window = ResultsWindow(res)  # Pass self as parent
            self.results_window.show()
        else:
            QMessageBox.information(self, "No Results", "No drones were recommended based on your criteria.")


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
    radAndHeigh = radius_map.get(user_input_gui["Port Size"], -1)
    radius = radAndHeigh[0]
    height = radAndHeigh[1]
    user_input = {
        "Flight Radius": radius,
        "Flight height": height,
        "Thermal/Night Camera": 0.0 if user_input_gui["Night Vision"] == "No" else 1.0,
        "Max wind resistance": wind,
        "Budgets options": user_input_gui["Budget (€)"],
        "Camera Quality": user_input_gui["Camera Performance"],
        "ISO range": 25600 if user_input_gui["Night Vision"] == "Yes" else (
            6400 if user_input_gui["Night Vision"] == "Occasionally" else 3200),
        "Battery Life": user_input_gui["Battery Life (min)"],
        "Payload Capacity": 0 if user_input_gui["Cargo"] == "No" else (
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


class ResultsWindow(QWidget):
    """A new window to display the top drone recommendations with collapsible explanations."""

    def __init__(self, top_drones, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Drone Recommendation Results")
        self.setMinimumSize(700, 500)  # Use minimum size, let layout expand
        self.resize(900, 700)  # Set a good initial size
        self.setStyleSheet("background-color: #1e1e2f; color: #ffffff; font-family: 'Segoe UI';")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        title_label = QLabel("Top Drone Recommendations")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4e94f3;")
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)

        if not top_drones:
            no_results_label = QLabel("No drones found matching your criteria.")
            no_results_label.setStyleSheet("font-size: 18px; color: #ff6b6b;")
            no_results_label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(no_results_label)
            self.main_layout.addStretch()  # Push content up if no results
        else:
            results_scroll_area = QScrollArea(self)
            results_scroll_area.setWidgetResizable(True)
            results_scroll_area.setStyleSheet(
                "QScrollArea { border: none; } QScrollBar:vertical { border: none; background: #2b2b40; width: 10px; margin: 0px 0px 0px 0px; } QScrollBar::handle:vertical { background: #4e94f3; min-height: 20px; border-radius: 5px; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; } QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical { background: none; } QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }")

            results_container = QWidget()
            results_layout = QVBoxLayout(results_container)
            results_layout.setSpacing(15)
            results_layout.setContentsMargins(0, 0, 0, 0)

            for i, drone in enumerate(top_drones):
                drone_frame = QFrame()
                drone_frame.setStyleSheet("""
                    QFrame {
                        background-color: #2b2b40;
                        border: 1px solid #4e94f3;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                drone_layout = QVBoxLayout(drone_frame)
                drone_layout.setSpacing(8)  # Slightly reduced spacing within a drone card

                rank_label = QLabel(f"Rank {i + 1}")
                rank_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
                drone_layout.addWidget(rank_label)

                id_label = QLabel(
                    f"Drone ID: <span style='color: #4e94f3; font-weight: bold;'>{drone.get('Drone ID', 'N/A')}</span>")
                id_label.setStyleSheet("font-size: 16px;")
                id_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                drone_layout.addWidget(id_label)

                score_label = QLabel(
                    f"Total Score: <span style='color: #a8dadc; font-weight: bold;'>{drone.get('Total Score (%)', 'N/A')}%</span>")
                score_label.setStyleSheet("font-size: 16px;")
                drone_layout.addWidget(score_label)



                price_val = drone.get('Price', 'N/A')
                price_text = f"€{price_val:.2f}" if isinstance(price_val, (int, float)) else "N/A"
                price_label = QLabel(f"Price: <span style='color: #66bb6a; font-weight: bold;'>{price_text}</span>")
                price_label.setStyleSheet("font-size: 16px;")
                drone_layout.addWidget(price_label)

                # --- Collapsible Explanations ---
                explanations = drone.get('Explanation', [])
                if explanations:
                    # Toggle Button
                    explanation_toggle_button = QPushButton("▼ Explanations")
                    explanation_toggle_button.setCheckable(True)  # Makes it act like a toggle
                    explanation_toggle_button.setChecked(False)  # Start unchecked (collapsed)
                    explanation_toggle_button.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: #4e94f3;
                            border: none;
                            text-align: left;
                            padding: 5px 0px;
                            font-size: 14px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            color: #3a6fd9;
                        }
                        QPushButton:checked {
                            /* Optional: different style when expanded */
                        }
                    """)
                    drone_layout.addWidget(explanation_toggle_button)

                    # Container for explanation labels
                    explanations_container = QWidget()
                    explanations_layout_inner = QVBoxLayout(explanations_container)
                    explanations_layout_inner.setContentsMargins(15, 5, 0,
                                                                 5)  # Indent explanations, add top/bottom margin
                    explanations_layout_inner.setSpacing(3)  # Spacing between explanation lines

                    for expl_text in explanations:
                        expl_label = QLabel(f"• {expl_text}")  # Using a bullet point
                        expl_label.setStyleSheet("font-size: 13px; color: #c0c0d0;")  # Slightly dimmer text
                        expl_label.setWordWrap(True)
                        expl_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        explanations_layout_inner.addWidget(expl_label)

                    explanations_container.setLayout(explanations_layout_inner)
                    explanations_container.setVisible(False)  # Initially hidden
                    drone_layout.addWidget(explanations_container)

                    # Connect button to toggle visibility and text
                    def create_toggle_lambda(button, container):
                        return lambda checked: (
                            container.setVisible(checked),
                            button.setText("▲ Explanations" if checked else "▼ Explanations")
                        )

                    explanation_toggle_button.toggled.connect(
                        create_toggle_lambda(explanation_toggle_button, explanations_container))

                else:
                    no_expl_label = QLabel("No specific explanations provided.")
                    no_expl_label.setStyleSheet("font-size: 14px; font-style: italic; color: #888899;")
                    drone_layout.addWidget(no_expl_label)

                drone_layout.addStretch(1)  # Add stretch inside each drone card if needed
                results_layout.addWidget(drone_frame)

            results_layout.addStretch(1)  # Pushes drone cards to the top if they don't fill the scroll area
            results_scroll_area.setWidget(results_container)
            self.main_layout.addWidget(results_scroll_area)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b; /* A more distinct red */
                color: #ffffff;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
                margin-top: 10px; /* Reduced margin slightly */
            }
            QPushButton:hover {
                background-color: #e63946; /* Darker red on hover */
            }
            QPushButton:pressed {
                background-color: #d62828; /* Even darker when pressed */
            }
        """)
        close_button.clicked.connect(self.close)
        self.main_layout.addWidget(close_button, alignment=Qt.AlignCenter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    drone_port_config = DronePortConfig()
    drone_port_config.show()
    sys.exit(app.exec())
