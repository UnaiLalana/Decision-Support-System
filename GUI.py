import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QSlider, QPushButton, QVBoxLayout, QFormLayout
)


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
        self.slider.valueChanged.connect(self.update_label)
        self.slider.valueChanged.connect(self.valueChanged.emit) # Emit the signal

        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

    def update_label(self, value):
        self.value_label.setText(f"{self.label_text}: {value}")

    def value(self):
        return self.slider.value()


class DronePortConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Port Configuration")
        # Set a fixed size for a mobile-like feel, or use minimumSizeHint
        self.setFixedSize(400, 700) # Example size, adjust as needed
        self.setStyleSheet("background-color: #1e1e2f; color: #ffffff; font-family: 'Segoe UI';")

        # Main Layout
        self.main_layout = QVBoxLayout()
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
        self.port_size_entry = self._create_styled_entry()
        self.form_layout.addRow("Port Size:", self.port_size_entry)

        self.port_location_combo = self._create_styled_combobox(["Baltic Sea", "West Mediterranean", "Central Mediterranean"])
        self.form_layout.addRow("Port Location:", self.port_location_combo)

        self.budget_entry = self._create_styled_entry()
        self.form_layout.addRow("Budget (€):", self.budget_entry)

        self.camera_combo = self._create_styled_combobox(["Low", "Average", "High"])
        self.form_layout.addRow("Camera Performance:", self.camera_combo)

        self.battery_entry = self._create_styled_entry()
        self.form_layout.addRow("Battery Life (min):", self.battery_entry)

        self.dimensions_entry = self._create_styled_entry()
        self.form_layout.addRow("Dimensions (cm³):", self.dimensions_entry)

        self.transmission_combo = self._create_styled_combobox(["No Transmission", "Slow", "Average", "High"])
        self.form_layout.addRow("Data Transmission:", self.transmission_combo)

        self.storage_entry = self._create_styled_entry()
        self.form_layout.addRow("Storage (GB):", self.storage_entry)

        self.air_water_combo = self._create_styled_combobox(["Yes", "No"])
        self.form_layout.addRow("Air/Water Sensors:", self.air_water_combo)

        self.charging_entry = self._create_styled_entry()
        self.form_layout.addRow("Charging Time (min):", self.charging_entry)

        # Add the form layout to the main layout
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

        self.setLayout(self.main_layout)

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
        port_size = self.port_size_entry.text()
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    drone_port_config = DronePortConfig()
    drone_port_config.show()
    sys.exit(app.exec())
