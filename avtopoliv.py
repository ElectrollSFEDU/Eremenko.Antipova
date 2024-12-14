from PyQt5 import QtWidgets, QtCore
import sys
import serial
import serial.tools.list_ports

class ArduinoControlApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.arduino = None
        self.is_relay_on = False  # Track relay state
        self.is_pump_on = False   # Track pump state

    def initUI(self):
        self.setWindowTitle('Управление Arduino')
        self.setGeometry(100, 100, 500, 400)

        # Запретить изменение размера окна
        self.setFixedSize(self.size())  # Устанавливаем фиксированный размер окна

        # Dropdown for COM ports
        self.port_label = QtWidgets.QLabel('COM Порт:', self)
        self.port_label.setGeometry(20, 20, 100, 20)

        self.port_dropdown = QtWidgets.QComboBox(self)
        self.port_dropdown.setGeometry(100, 20, 150, 20)
        self.refresh_ports()

        self.refresh_button = QtWidgets.QPushButton('Обновить', self)
        self.refresh_button.setGeometry(260, 20, 100, 20)
        self.refresh_button.clicked.connect(self.refresh_ports)

        # Connect button
        self.connect_button = QtWidgets.QPushButton('Подключиться', self)
        self.connect_button.setGeometry(100, 60, 100, 30)
        self.connect_button.clicked.connect(self.connect_to_arduino)

        # Data display
        self.data_label = QtWidgets.QLabel('Данные с датчиков:', self)
        self.data_label.setGeometry(20, 100, 150, 20)

        self.data_display = QtWidgets.QTextEdit(self)
        self.data_display.setGeometry(20, 130, 450, 150)
        self.data_display.setReadOnly(True)

        # Pump control buttons
        self.pump_on_button = QtWidgets.QPushButton('Включить помпу', self)
        self.pump_on_button.setGeometry(20, 300, 120, 30)
        self.pump_on_button.clicked.connect(self.toggle_pump_state)

        self.pump_off_button = QtWidgets.QPushButton('Выключить помпу', self)
        self.pump_off_button.setGeometry(160, 300, 120, 30)
        self.pump_off_button.clicked.connect(self.turn_off_pump)

        # Manual control buttons
        self.manual_toggle_button = QtWidgets.QPushButton('Автополив: Выключен', self)
        self.manual_toggle_button.setGeometry(300, 300, 160, 30)
        self.manual_toggle_button.clicked.connect(self.toggle_relay_state)

        # Clear and save buttons
        self.clear_button = QtWidgets.QPushButton('Очистить поле', self)
        self.clear_button.setGeometry(20, 340, 120, 30)
        self.clear_button.clicked.connect(self.clear_data_display)

        self.save_button = QtWidgets.QPushButton('Сохранить данные', self)
        self.save_button.setGeometry(160, 340, 120, 30)
        self.save_button.clicked.connect(self.save_data_to_file)
        
    def refresh_ports(self):
        """Refresh the list of available COM ports."""
        self.port_dropdown.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_dropdown.addItem(port.device)

    def connect_to_arduino(self):
        """Connect to the selected COM port."""
        selected_port = self.port_dropdown.currentText()
        try:
            self.arduino = serial.Serial(selected_port, 9600, timeout=1)
            self.data_display.append(f'Подключено к {selected_port}')
            self.connect_button.setEnabled(False)  # Disable the connect button
            self.start_reading()
        except Exception as e:
            self.data_display.append(f'Ошибка подключения: {e}')

    def start_reading(self):
        """Start reading data from Arduino."""
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.read_data)
        self.timer.start(1000)  # Read every second

    def read_data(self):
        """Read and display data from Arduino."""
        if self.arduino and self.arduino.in_waiting > 0:
            try:
                data = self.arduino.readline().decode('utf-8').strip()
                self.data_display.append(f'Данные с датчиков: {data}')
            except Exception as e:
                self.data_display.append(f'Ошибка чтения данных: {e}')

    def send_command(self, command):
        """Send a command to Arduino."""
        if self.arduino:
            try:
                self.arduino.write((command + '\n').encode('utf-8'))
                self.data_display.append(f'Отправлена команда: {command}')
            except Exception as e:
                self.data_display.append(f'Ошибка отправки команды: {e}')
        else:
            self.data_display.append('Arduino не подключено.')

    def clear_data_display(self):
        """Clear the data display field."""
        self.data_display.clear()

    def save_data_to_file(self):
        """Save the data from the display to a text file."""
        try:
            with open('sensor_data.txt', 'w', encoding='utf-8') as file:
                file.write(self.data_display.toPlainText())
            self.data_display.append('Данные сохранены в sensor_data.txt')
        except Exception as e:
            self.data_display.append(f'Ошибка сохранения данных: {e}')

    def toggle_relay_state(self):
        """Toggle the relay state and update the button label."""
        if self.is_relay_on:
            self.send_command('AUTO_OFF')
            self.manual_toggle_button.setText('Автополив: Выключен')
            self.is_relay_on = False
        else:
            self.send_command('AUTO_ON')
            self.manual_toggle_button.setText('Автополив: Включен')
            self.is_relay_on = True

    def toggle_pump_state(self):
        """Toggle the pump state and update the pump button."""
        if self.is_pump_on:
            self.send_command('OFF')
            self.pump_on_button.setText('Включить помпу')
            self.is_pump_on = False
        else:
            self.send_command('ON')
            self.pump_on_button.setText('Выключить помпу')
            self.is_pump_on = True

    def turn_off_pump(self):
        """Turn off the pump if it is on."""
        if self.is_pump_on:
            self.send_command('OFF')
            self.pump_on_button.setText('Включить помпу')
            self.is_pump_on = False
            self.data_display.append('Помпа выключена.')
        else:
            self.data_display.append('Помпа уже выключена.')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = ArduinoControlApp()
    main_window.show()
    sys.exit(app.exec_())
