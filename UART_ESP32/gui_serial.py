import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QTextEdit, QLineEdit, QGroupBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class SerialReaderThread(QThread):
    data_received = pyqtSignal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.is_running = True
    
    def run(self):
        while self.is_running and self.serial_port.is_open:
            if self.serial_port.in_waiting:
                try:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    if data:
                        self.data_received.emit(data)
                except:
                    pass
    def stop(self):
        self.is_running = False

class SerialGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("ESP32 Control Center - PyQt5")
        self.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout()
        
        # --- Group 1: Koneksi ---
        conn_group = QGroupBox("Koneksi Serial")
        conn_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.toggle_conn)
        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(self.btn_connect)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # --- Group 2: Kontrol LED (Penambahan Baru) ---
        ctrl_group = QGroupBox("Kontrol LED Hardware")
        ctrl_layout = QHBoxLayout()
        
        self.btn_led1 = QPushButton("LED 1 TOGGLE")
        self.btn_led1.clicked.connect(lambda: self.send_command("1"))
        
        self.btn_led2 = QPushButton("LED 2 TOGGLE")
        self.btn_led2.clicked.connect(lambda: self.send_command("2"))
        
        ctrl_layout.addWidget(self.btn_led1)
        ctrl_layout.addWidget(self.btn_led2)
        ctrl_group.setLayout(ctrl_layout)
        layout.addWidget(ctrl_group)

        # --- Group 3: Monitoring & Log ---
        log_group = QGroupBox("Monitoring Terminal")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(p.device)

    def toggle_conn(self):
        if self.serial_port is None or not self.serial_port.is_open:
            try:
                self.serial_port = serial.Serial(self.port_combo.currentText(), 115200)
                self.thread = SerialReaderThread(self.serial_port)
                self.thread.data_received.connect(self.update_log)
                self.thread.start()
                self.btn_connect.setText("Disconnect")
                self.update_log("Connected!")
            except Exception as e:
                self.update_log(f"Error: {e}")
        else:
            self.thread.stop()
            self.serial_port.close()
            self.btn_connect.setText("Connect")
            self.update_log("Disconnected.")

    def send_command(self, cmd):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(cmd.encode())
            self.update_log(f"Sent: {cmd}")

    def update_log(self, text):
        self.log_text.append(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SerialGUI()
    gui.show()
    sys.exit(app.exec_())