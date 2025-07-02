import sys
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QAction
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QMainWindow,
    QDialog, QLabel, QVBoxLayout, QComboBox, QPushButton,
    QFileDialog, QWidget, QHBoxLayout, QTabWidget, QFormLayout,
    QLineEdit, QSpinBox, QGraphicsEllipseItem, QGraphicsRectItem,
    QMenuBar
)
from PySide6.QtSvgWidgets import QGraphicsSvgItem
import os
from PySide6.QtWidgets import QMenu


class SvgViewer(QGraphicsView):
    def __init__(self, svg_path):
        super().__init__()
        self.setRenderHints(self.renderHints() |
                            QPainter.Antialiasing |
                            QPainter.SmoothPixmapTransform)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.svg_item = QGraphicsSvgItem(svg_path)
        self.scene.addItem(self.svg_item)

        # self.setDragMode(QGraphicsView.ScrollHandDrag) # Removed or commented out to implement custom left-click panning
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 10.0

        # Hotspots - list of dictionaries
        self.hotspots_data = [
            # Original switches (now with 'current_position' state)
            {"rect": QRectF(262.5, 392.269, 20.026, 20.026), "type": "switch", "name": "Switch 1", "current_position": "default"},
            {"rect": QRectF(284.528, 364.949, 20.026, 20.026), "type": "switch", "name": "Switch 2", "current_position": "default"},
            {"rect": QRectF(321.788, 337.689, 20.026, 20.026), "type": "switch", "name": "Switch 3", "current_position": "default"},
            # UPDATED Switch 4 coordinates
            {"rect": QRectF(293.538, 264.652 ,20.026, 20.026), "type": "switch", "name": "Switch 4", "current_position": "default"},
            {"rect": QRectF(225.748, 219.489, 20.026, 20.026), "type": "switch", "name": "Switch 5", "current_position": "default"},
            {"rect": QRectF(226.748, 259.489, 20.026, 20.026), "type": "switch", "name": "Switch 6", "current_position": "default"},
            {"rect": QRectF(228.748, 300.489, 20.026, 20.026), "type": "switch", "name": "Switch 7", "current_position": "default"},
            {"rect": QRectF(353.748, 265.489, 20.026, 20.026), "type": "switch", "name": "Switch 8", "current_position": "default"},
            # {"rect": QRectF(236.93, 268.489, 20.026, 20.026), "type": "switch", "name": "Switch 6", "current_position": "default"},
            {"rect": QRectF(525.50, 308.99, 20.026, 20.026), "type": "switch", "name": "Switch 9", "current_position": "default"},
            {"rect": QRectF(693.50, 303.99, 19.026, 29.026), "type": "switch", "name": "Switch 10", "current_position": "default"},
            {"rect": QRectF(810.50, 303.99, 19.026, 29.026), "type": "switch", "name": "Switch 11", "current_position": "default"},
            {"rect": QRectF(840.50, 308.99, 20.026, 20.026), "type": "switch", "name": "Switch 12", "current_position": "default"},
            {"rect": QRectF(880.50, 230.99, 20.026, 20.026), "type": "switch", "name": "Switch 13", "current_position": "default"},
            {"rect": QRectF(911.50, 260.99, 20.026, 20.026), "type": "switch", "name": "Switch 14", "current_position": "default"},
            {"rect": QRectF(940.50, 261.99, 20.026, 29.026), "type": "switch", "name": "Switch 15", "current_position": "default"},
            {"rect": QRectF(889.50, 406.99, 20.026, 20.026), "type": "switch", "name": "Switch 16", "current_position": "default"},
            {"rect": QRectF(914.50, 371.99, 20.026, 20.026), "type": "switch", "name": "Switch 17", "current_position": "default"},
            {"rect": QRectF(944.50, 364.99, 20.026, 29.026), "type": "switch", "name": "Switch 18", "current_position": "default"},
            
            # Frequency hotspot: User needs to provide Inkscape values for this one as well if it's off
            {"rect": QRectF(582.658, 317.621 - (45.508 / 2), 85.789, 45.508), "type": "frequency", "name": "Frequency Settings"},
            
            # Example hotspot (remains unchanged - user can remove or update with Inkscape values)
            {"rect": QRectF(100, 100, 50, 50), "type": "example", "name": "Example Hotspot"},
            
            # PLL control hotspot (existing, now with 'current_state')
            {"rect": QRectF(477.498, 280.155 - (24.621 / 2), 46.104, 24.621), "type": "pll_control", "name": "PLL Control 1", "current_state": "disabled"},
            # NEW PLL control hotspot
            {"rect": QRectF(725.358, 208.405 - (24.621 / 2), 46.104, 24.621), "type": "pll_control", "name": "PLL Control 2", "current_state": "disabled"},
            # NEW PLL control hotspot (from the last request)
            {"rect": QRectF(729.258, 437.175 - (24.621 / 2), 46.104, 24.621), "type": "pll_control", "name": "PLL Control 3", "current_state": "disabled"},
        ]

        # Offset for non-switch hotspots to adjust clicking position
        self.non_switch_hotspot_offset_x = 0.0
        self.non_switch_hotspot_offset_y = 0.0

        # Overlay switch states - now a dictionary for individual tracking
        self.switch_overlay_items = {}
        
        # PLL dot overlays - now a dictionary for individual tracking
        self.pll_dot_items = {}

        # Panning variables
        self.panning = False
        self.last_mouse_pos = QPointF()

        # Initialize switch and PLL overlays based on their initial state
        for hotspot_data in self.hotspots_data:
            if hotspot_data["type"] == "switch":
                if hotspot_data["current_position"] != "default":
                    self.update_switch_overlay(hotspot_data)
            elif hotspot_data["type"] == "pll_control":
                # Call update for PLL controls to show initial (red) state
                self.update_pll_dot_overlay(hotspot_data)

        # --- ADD THIS CODE TO HIGHLIGHT A SPECIFIC HOTSPOT ---
        for hotspot_data in self.hotspots_data:
            if hotspot_data["name"] == "Switch 1":
                highlight_rect = QGraphicsRectItem(hotspot_data["rect"])
                highlight_rect.setBrush(QBrush(QColor(255, 0, 0, 100))) # Red with 100 alpha (transparency)
                highlight_rect.setPen(QPen(QColor(255, 0, 0), 2)) # Red border, 2 pixels wide
                highlight_rect.setZValue(9) # Place it below overlays (ZValue 10) but above the SVG (ZValue 0 implicitly)
                self.scene.addItem(highlight_rect)
                break # Found Switch 1, no need to check others
        # --- END OF ADDED CODE ---


    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom = zoom_in_factor
        else:
            zoom = zoom_out_factor

        new_scale = self.scale_factor * zoom
        if self.min_scale <= new_scale <= self.max_scale:
            self.scale(zoom, zoom)
            self.scale_factor = new_scale

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())

        if event.button() == Qt.RightButton:
            hotspot_found = False
            for hotspot_data in self.hotspots_data:
                current_hotspot_rect = hotspot_data["rect"]

                # Apply offset only to non-switch hotspots
                if hotspot_data["type"] != "switch":
                    current_hotspot_rect = QRectF(
                        hotspot_data["rect"].x() + self.non_switch_hotspot_offset_x,
                        hotspot_data["rect"].y() + self.non_switch_hotspot_offset_y,
                        hotspot_data["rect"].width(),
                        hotspot_data["rect"].height()
                    )

                if current_hotspot_rect.contains(scene_pos):
                    hotspot_found = True
                    if hotspot_data["type"] == "switch":
                        # Pass the entire hotspot_data for this specific switch
                        self.show_switch_dialog(scene_pos, hotspot_data)
                    elif hotspot_data["type"] == "frequency":
                        self.show_frequency_dialog(scene_pos)
                    elif hotspot_data["type"] == "pll_control":
                        # Pass the entire hotspot_data for this specific PLL
                        self.show_pll_dialog(scene_pos, hotspot_data)
                    break # Exit loop once a hotspot is found
            if not hotspot_found: # Only call super if no hotspot was clicked
                super().mousePressEvent(event)
        elif event.button() == Qt.LeftButton:
            self.panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor) # Change cursor to indicate panning
            event.accept() # Accept the event to prevent propagation
        else:
            super().mousePressEvent(event) # Call super for other buttons

    def mouseMoveEvent(self, event):
        if self.panning and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_mouse_pos = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.panning:
            self.panning = False
            self.setCursor(Qt.ArrowCursor) # Revert cursor to normal
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # show_switch_dialog now accepts hotspot_data
    def show_switch_dialog(self, scene_pos, hotspot_data):
        menu = QMenu(self)
        up_action = menu.addAction("RF2")
        down_action = menu.addAction("RF1")

        selected_action = menu.exec(self.viewport().mapToGlobal(self.mapFromScene(scene_pos)))
        if selected_action == up_action:
            hotspot_data["current_position"] = "up" # Update the state for this specific switch
            self.update_switch_overlay(hotspot_data) # Pass the full data to update overlay
        elif selected_action == down_action:
            hotspot_data["current_position"] = "down" # Update the state for this specific switch
            self.update_switch_overlay(hotspot_data) # Pass the full data to update overlay

    # update_switch_overlay now accepts hotspot_data
    def update_switch_overlay(self, hotspot_data):
        switch_name = hotspot_data["name"]
        position = hotspot_data["current_position"]
        hotspot_rect = hotspot_data["rect"]

        # Remove existing overlay for this specific switch, if any
        if switch_name in self.switch_overlay_items and self.switch_overlay_items[switch_name]:
            self.scene.removeItem(self.switch_overlay_items[switch_name])
            self.switch_overlay_items[switch_name] = None

        if position and position != "default": # Only draw if a specific state is set
            svg_file = f"switch_{position}.svg"
            if not os.path.exists(svg_file):
                print(f"[ERROR] File not found: {svg_file}")
                return
            print(f"[DEBUG] Loading: {svg_file} for {switch_name}")

            item = QGraphicsSvgItem(svg_file)
            item.setFlags(QGraphicsSvgItem.GraphicsItemFlag.ItemClipsToShape)
            item.setZValue(10)
            
            item.setPos(hotspot_rect.topLeft())

            bounding_box = item.renderer().viewBoxF()
            if bounding_box.width() > 0 and bounding_box.height() > 0:
                scale_x = hotspot_rect.width() / bounding_box.width()
                scale_y = hotspot_rect.height() / bounding_box.height()
                item.setScale(min(scale_x, scale_y))

            self.scene.addItem(item)
            self.switch_overlay_items[switch_name] = item # Store it in the dictionary

    def show_frequency_dialog(self, scene_pos):
        dialog = QDialog(self)
        dialog.setWindowTitle("Configure Frequency")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout()
        label = QLabel("What frequency to use?")
        combo = QComboBox()
        combo.addItems([
            "1.843 MHz", "3.276 MHz", "7.120 MHz", "10.550 MHz", "13.560 MHz",
            "16.755 MHz", "18.910 MHz", "21.450 MHz", "24.000 MHz", "27.120 MHz"
        ])
        custom_input = QLineEdit()
        custom_input.setPlaceholderText("Enter custom frequency (MHz)")

        read_button = QPushButton("Read")
        write_button = QPushButton("Write")

        layout.addWidget(label)
        layout.addWidget(combo)
        layout.addWidget(custom_input)
        layout.addWidget(read_button)
        layout.addWidget(write_button)
        dialog.setLayout(layout)

        def on_read():
            print("Reading frequency...")

        def on_write():
            selected = custom_input.text().strip() or combo.currentText()
            print(f"Writing frequency: {selected}")

        read_button.clicked.connect(on_read)
        write_button.clicked.connect(on_write)

        dialog.move(self.viewport().mapToGlobal(self.mapFromScene(scene_pos)))
        dialog.exec()

    # show_pll_dialog now accepts hotspot_data
    def show_pll_dialog(self, scene_pos, hotspot_data):
        menu = QMenu(self)
        enable_action = menu.addAction("PLL Enable")
        disable_action = menu.addAction("PLL Disable")

        selected_action = menu.exec(self.viewport().mapToGlobal(self.mapFromScene(scene_pos)))
        if selected_action == enable_action:
            hotspot_data["current_state"] = "enabled" # Update state for this specific PLL
            self.update_pll_dot_overlay(hotspot_data) # Pass full data
            print(f"{hotspot_data['name']} Enabled")
        elif selected_action == disable_action:
            hotspot_data["current_state"] = "disabled" # Update state for this specific PLL
            self.update_pll_dot_overlay(hotspot_data) # Pass full data
            print(f"{hotspot_data['name']} Disabled")

    # update_pll_dot_overlay now accepts hotspot_data
    def update_pll_dot_overlay(self, hotspot_data):
        pll_name = hotspot_data["name"]
        pll_state = hotspot_data["current_state"]
        hotspot_rect = hotspot_data["rect"]

        # Remove existing overlay for this specific PLL, if any
        if pll_name in self.pll_dot_items and self.pll_dot_items[pll_name]:
            self.scene.removeItem(self.pll_dot_items[pll_name])
            self.pll_dot_items[pll_name] = None

        dot_size = 8
        # Reverting to original dot position logic using a small offset from top-left
        dot_x = hotspot_rect.x() + (dot_size * 0.2)
        dot_y = hotspot_rect.y() + (dot_size * 0.2)

        self.pll_dot_items[pll_name] = QGraphicsEllipseItem(dot_x, dot_y, dot_size, dot_size)
        
        # Set dot color based on PLL enabled state
        if pll_state == "enabled":
            self.pll_dot_items[pll_name].setBrush(QBrush(QColor(144, 238, 144))) # Lighter Green
        else: # Default or "disabled"
            self.pll_dot_items[pll_name].setBrush(QBrush(QColor("red")))   # Red for disabled

        self.pll_dot_items[pll_name].setZValue(10)
        self.scene.addItem(self.pll_dot_items[pll_name])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AD JIG Configurator")
        self.resize(1000, 800)

        self.viewer = SvgViewer("background.svg")

        # Create Menu Bar
        menu_bar = self.menuBar()
        # Apply black background and white text to the menu bar
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: black;
                color: white;
            }
            QMenuBar::item {
                background-color: transparent; /* Ensure items don't have separate background */
                color: white;
            }
            QMenuBar::item:selected { /* Style for selected item */
                background-color: #555;
            }
            QMenu {
                background-color: black; /* Background for dropdown menus */
                color: white;
                border: 1px solid #333;
            }
            QMenu::item:selected { /* Style for selected item in dropdown */
                background-color: #555;
            }
        """)

        # File Menu
        file_menu = menu_bar.addMenu("File")
        
        # Load Settings Action
        load_action = QAction("Load Settings", self)
        load_action.setShortcut("Ctrl+L") # Optional: Add a shortcut
        load_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(load_action)

        # Settings Menu
        settings_menu = menu_bar.addMenu("Settings")

        # Communication Action
        comm_action = QAction("Communication", self)
        comm_action.setShortcut("Ctrl+C") # Optional: Add a shortcut
        comm_action.triggered.connect(self.open_comm_dialog)
        settings_menu.addAction(comm_action)

        # Removed black_bar and button_bar components from previous versions

        main_layout = QVBoxLayout()
        # Removed black_bar and button_bar from layout
        main_layout.addWidget(self.viewer)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Settings File", "", "All Files (*)")
        if file_path:
            print(f"Selected file: {file_path}")

    
    def open_comm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Communication Configuration")
        dialog.setMinimumWidth(400)

        tab_widget = QTabWidget()

        # UART Tab
        uart_tab = QWidget()
        uart_form = QFormLayout()

        uart_port = QComboBox()
        uart_port.addItems(["COM1", "COM2", "COM3", "COM4"])

        uart_baud = QComboBox()
        uart_baud.addItems(["9600", "19200", "38400", "57600", "115200"])

        uart_data_bits = QComboBox()
        uart_data_bits.addItems(["5", "6", "7", "8"])

        uart_parity = QComboBox()
        uart_parity.addItems(["None", "Even", "Odd", "Mark", "Space"])

        uart_stop_bits = QComboBox()
        uart_stop_bits.addItems(["1", "1.5", "2"])

        uart_form.addRow("Port:", uart_port)
        uart_form.addRow("Baud Rate:", uart_baud)
        uart_form.addRow("Data Bits:", uart_data_bits)
        uart_form.addRow("Parity:", uart_parity)
        uart_form.addRow("Stop Bits:", uart_stop_bits)
        uart_tab.setLayout(uart_form)

        # Ethernet Tab
        eth_tab = QWidget()
        eth_form = QFormLayout()

        ip_address = QLineEdit("192.168.0.100")
        port = QSpinBox()
        port.setRange(1, 65535)
        port.setValue(502)

        unit_id = QSpinBox()
        unit_id.setRange(1, 247)
        unit_id.setValue(1)

        timeout = QSpinBox()
        timeout.setRange(100, 10000)
        timeout.setValue(1000)

        eth_form.addRow("IP Address:", ip_address)
        eth_form.addRow("Port:", port)
        eth_form.addRow("Unit ID:", unit_id)
        eth_form.addRow("Timeout (ms):", timeout)
        eth_tab.setLayout(eth_form)

        tab_widget.addTab(uart_tab, "UART")
        tab_widget.addTab(eth_tab, "Ethernet")

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())