import sys
import serial
import json
import serial.tools.list_ports
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from generated_ui import Ui_MainWindow  # Import your generated UI module


class SerialMonitorApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.serial_port = None
        self.format_mode = "string"
        self.data_bits_mapping = {"5": serial.FIVEBITS, "6": serial.SIXBITS, "7": serial.SEVENBITS, "8": serial.EIGHTBITS}
        self.parity_mapping = {
            "No Parity": serial.PARITY_NONE,
            "Even Parity": serial.PARITY_EVEN,
            "Odd Parity": serial.PARITY_ODD
        }
        self.stop_bits_mapping = {
            "1": serial.STOPBITS_ONE,
            "1.5": serial.STOPBITS_ONE_POINT_FIVE,
            "2": serial.STOPBITS_TWO
        }

        self.pushButton.clicked.connect(self.connect_serial) #declaring push buttons
        self.pushButton_2.clicked.connect(self.send_command)
        self.pushButton_3.clicked.connect(self.refresh_ports)
        self.pushButton_4.clicked.connect(self.clear_response) 
        self.pushButton_5.clicked.connect(self.disconnect_serial)
        self.pushButton_6.clicked.connect(self.fetch_json_data)
        self.pushButton_7.clicked.connect(self.submit_json_data)
        self.pushButton_9.clicked.connect(self.clear_table)
        self.pushButton_8.clicked.connect(self.fetch_second_json_data)
        self.pushButton_10.clicked.connect(self.submit_json_data_2)
        self.pushButton_11.clicked.connect(self.clear_table_2)

        self.comboBox_3.addItems(["String", "Hex"])
        self.comboBox_4.addItems(self.data_bits_mapping.keys())  # Use data_bits_mapping keys
        self.comboBox_5.addItems(self.parity_mapping.keys())  # Use parity_mapping keys
        self.comboBox_6.addItems(self.stop_bits_mapping.keys())  # Use stop_bits_mapping keys
        self.comboBox_3.currentIndexChanged.connect(self.change_format_mode)
        self.comboBox_7.addItems(["String", "Hex", "Chart"])
        self.comboBox_7.currentIndexChanged.connect(self.change_output_format)

        

        self.checkBox.stateChanged.connect(self.on_carriage_return_changed)
        self.checkBox_2.stateChanged.connect(self.on_new_line_changed)

        self.append_r = True  # Initialize to True by default
        self.append_n = True  # Initialize to True by default

        self.checkBox.setChecked(True)
        self.checkBox_2.setChecked(True)

        self.output_format = "string"
        self.update_ports()
        self.update_baud_rates()
        self.enable_dark_mode()

    def on_carriage_return_changed(self, state):
        self.append_r = state == QtCore.Qt.Checked

    def on_new_line_changed(self, state):
        self.append_n = state == QtCore.Qt.Checked

    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
            self.textEdit_2.clear()
            self.textEdit_2.append("Disconnected from serial port.")
        

    def update_baud_rates(self): #function to select baud rates
        baud_rates = ["9600","19200","38400", "57600","115200","256000"]  # Add more if needed
        self.comboBox_2.addItems(baud_rates)

    def update_ports(self):  # Updated method to show COM port names
        self.comboBox.clear()
        ports = serial.tools.list_ports.comports()
        self.comboBox.addItems([f"{port.device} - {port.description}" for port in ports])

    

    def connect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port=None
        
        selected_port_info = self.comboBox.currentText()
        selected_baud = int(self.comboBox_2.currentText())
        selected_data_bits = self.get_selected_data_bits()
        selected_parity = self.parity_mapping[self.comboBox_5.currentText()]
        selected_stop_bits = self.get_selected_stop_bits()

        try:
            port_parts = selected_port_info.split(' - ')
            if len(port_parts)==2:
                selected_port = port_parts[0]
                self.serial_port = serial.Serial(
                    port=selected_port,
                    baudrate=selected_baud,
                    bytesize=selected_data_bits,
                    parity=selected_parity,
                    stopbits=selected_stop_bits,
                    timeout=1
                )
                self.textEdit_2.clear()
                self.textEdit_2.append(f"Connected to {selected_port_info} at {selected_baud} baud .")
            else:
                raise Exception("Invalid port format")
        except Exception as e:
            self.textEdit_2.clear()
            self.textEdit_2.append(f"Error: {str(e)}")


    def change_format_mode(self):
        selected_index = self.comboBox_3.currentIndex()
        if selected_index == 0:
            self.format_mode = "string"
        elif selected_index == 1:
            self.format_mode = "hex"
    
    def get_selected_data_bits(self):
        selected_data_bits = self.data_bits_mapping[self.comboBox_4.currentText()] #This uses the selected text as a key to access a value from the data_bits_mapping dictionary
        return selected_data_bits                                                  #This accesses the currently selected text from comboBox_4
                                                                                   #The currentText() method retrieves the text of the currently selected item in the combo box.


    def get_selected_stop_bits(self):
        selected_stop_bits = self.stop_bits_mapping[self.comboBox_6.currentText()]
        return selected_stop_bits



    def change_output_format(self):
        selected_index = self.comboBox_7.currentIndex()
        if selected_index == 0:
            self.output_format = "string"
        elif selected_index == 1:
            self.output_format = "hex"
        elif selected_index == 2:
            self.output_format = "chart"

    def on_carriage_return_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.append_r = True
        else:
            self.append_r = False

    def on_new_line_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.append_n = True
        else:
            self.append_n = False
    
    def send_command(self):
        if self.serial_port and self.serial_port.is_open:
            command = self.textEdit.toPlainText()

            if self.format_mode == "hex":
                command = bytes.fromhex(command.replace(' ', ''))
            else:
                command = command.encode('utf-8')

            if self.append_r:
                command += bytes([0x0D])  # Add \r (0x0D) if append_r is True

            if self.append_n:
                command += bytes([0x0A])  # Add \n (0x0A) if append_n is True

            self.serial_port.write(command)

            response = self.serial_port.read_all()

            if self.output_format == "hex":
                response_text = ' '.join(format(byte, "02X") for byte in response)
            elif self.output_format == "chart":
                response_text = ""
                for byte in response:
                    if byte >= 32 and byte <= 126:
                        response_text += chr(byte)
                    else:
                        response_text += '.'
            else:
                response_text = response.decode("utf-8")

            # Append the response to the previous content and add a newline
            self.textEdit_2.append(response_text) # Use append to add new lines
        else:
            self.textEdit_2.clear()
            self.textEdit_2.append("Not connected to a serial port.")

    def clear_response(self):
        self.textEdit_2.clear()

    def refresh_ports(self):
        self.update_ports()

    def receive_response(self):
        response = b""
        while True:
            chunk = self.serial_port.read(64)
            if not chunk:
                break
            response += chunk
        response_decoded = response.decode(errors="ignore")

        if self.format_mode == "hex":
            response_hex=" ".join(format(byte,"02X") for byte in response)
            response_decoded = response_hex  + response_decoded

        response_lines = response_decoded.splitlines()
        formatted_response = "\n".join(response_lines)
        return formatted_response
    
    def fetch_json_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                # Send a command to request the JSON data from SPIFFS
                self.serial_port.write(b'ReadJSON\r\n')

                # Initialize an empty string to store received JSON data
                json_data_str = ""

                # Keep reading lines from the serial port until an empty line is received
                while True:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if not line:
                        break
                    json_data_str += line

                # Check if the received data is not empty
                if json_data_str:
                    # Parse the received JSON data
                    json_data = json.loads(json_data_str)

                    # Display the JSON data in the table widget
                    self.display_json_data(json_data)
                else:
                    self.textEdit_2.clear()
                    self.textEdit_2.append("No JSON data received.")

            except Exception as e:
                self.textEdit_2.clear()
                self.textEdit_2.append(f"Error: {str(e)}")
        else:
            self.textEdit_2.clear()
            self.textEdit_2.append("Not connected to a serial port.")


    def display_json_data(self, json_data):
    # Clear the existing content in the table widget
        self.tableWidget.clear()

    # Set the number of rows and columns in the table widget based on the JSON data
        self.tableWidget.setRowCount(len(json_data))
        self.tableWidget.setColumnCount(3)  # Three columns for Key, Old Value, and New Label

    # Set the headers for the table widget
        self.tableWidget.setHorizontalHeaderLabels(["Key", "Old Value", "New Label"])

    # Populate the table widget with the key-value pairs from the JSON data
        row = 0
        for key, value in json_data.items():
            key_item = QtWidgets.QTableWidgetItem(key)
            old_value_item = QtWidgets.QTableWidgetItem(str(value))
            new_label_item = QtWidgets.QTableWidgetItem()
        # Set the "New Label" column as editable
            new_label_item.setFlags(new_label_item.flags() | QtCore.Qt.ItemIsEditable)

            self.tableWidget.setItem(row, 0, key_item)
            self.tableWidget.setItem(row, 1, old_value_item)
            self.tableWidget.setItem(row, 2, new_label_item)
            row += 1

    def submit_json_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                updated_json_data = {}
                for row in range(self.tableWidget.rowCount()):
                    key_item = self.tableWidget.item(row, 0)
                    old_value_item = self.tableWidget.item(row, 1)
                    new_label_item = self.tableWidget.item(row, 2)

                    if key_item and new_label_item:
                        key = key_item.text()
                        old_value = old_value_item.text()
                        new_label = new_label_item.text()

                        # Use the new label if it's not empty; otherwise, use the old value
                        updated_json_data[key] = new_label if new_label else old_value

                # Send the updated JSON data to the ESP32
                updated_json_data_str = json.dumps(updated_json_data)
                self.serial_port.write(f'UpdateJSON:{updated_json_data_str}\r\n'.encode('utf-8'))

                self.textEdit_2.clear()
                self.textEdit_2.append("Updated JSON data sent to ESP32.")

            except Exception as e:
                self.textEdit_2.clear()
                self.textEdit_2.append(f"Error: {str(e)}")
        else:
            self.textEdit_2.clear()
            self.textEdit_2.append("Not connected to a serial port.")

    def clear_table(self):
       self.tableWidget.clearContents()
       self.tableWidget.setRowCount(0)

    def fetch_second_json_data(self):
        if self.serial_port and self.serial_port.is_open:
           try:
            # Send a command to request the second JSON data from SPIFFS
              self.serial_port.write(b'ReadSecondJSON\r\n')

            # Initialize an empty string to store received JSON data
              json_data_str = ""
 
            # Keep reading lines from the serial port until an empty line is received
              while True:
                  line = self.serial_port.readline().decode('utf-8').strip()
                  if not line:
                      break
                  json_data_str += line

            # Check if the received data is not empty
              if json_data_str:
                # Parse the received JSON data
                  json_data = json.loads(json_data_str)

                # Display the JSON data in the table widget
                  self.display_json_data_2(json_data)
              else:
                  self.textEdit_2.clear()
                  self.textEdit_2.append("No JSON data received.")

           except Exception as e:
                 self.textEdit_2.clear()
                 self.textEdit_2.append(f"Error: {str(e)}")
        else:
             self.textEdit_2.clear()
             self.textEdit_2.append("Not connected to a serial port.")

    def display_json_data_2(self, json_data_2):
    # Clear the existing content in tableWidget2
        self.tableWidget_2.clearContents()
        self.tableWidget_2.setRowCount(0)

    # Set the number of rows and columns in tableWidget2 based on the JSON data
        self.tableWidget_2.setRowCount(len(json_data_2))
        self.tableWidget_2.setColumnCount(3)  # Three columns for Key, Old Value, and New Label

    # Set the headers for tableWidget2
        self.tableWidget_2.setHorizontalHeaderLabels(["Key", " Value", "New Label"])

    # Populate tableWidget2 with the key-value pairs from the JSON data
        row = 0
        for key, value in json_data_2.items():
            key_item = QtWidgets.QTableWidgetItem(key)
            old_value_item = QtWidgets.QTableWidgetItem(str(value))
            new_label_item = QtWidgets.QTableWidgetItem()

        # Set the "New Label" column as editable
            new_label_item.setFlags(new_label_item.flags() | QtCore.Qt.ItemIsEditable)

            self.tableWidget_2.setItem(row, 0, key_item)
            self.tableWidget_2.setItem(row, 1, old_value_item)
            self.tableWidget_2.setItem(row, 2, new_label_item)
            row += 1

#function to represent submission of json data to esp spiffs from application
    def submit_json_data_2(self):
        if self.serial_port and self.serial_port.is_open:
           try:
              updated_json_data = {}
              for row in range(self.tableWidget_2.rowCount()):
                  key_item = self.tableWidget_2.item(row, 0)
                  old_value_item = self.tableWidget_2.item(row, 1)
                  new_label_item = self.tableWidget_2.item(row, 2)

                  if key_item and new_label_item:
                      key = key_item.text()
                      old_value = old_value_item.text()
                      new_label = new_label_item.text()

                    # Use the new label if it's not empty; otherwise, use the old value
                      updated_json_data[key] = new_label if new_label else old_value

            # Send the updated JSON data to the ESP32 (change the command as needed)
              updated_json_data_str = json.dumps(updated_json_data)
              self.serial_port.write(f'UpdateJSON2:{updated_json_data_str}\r\n'.encode('utf-8'))

              self.textEdit_2.clear()
              self.textEdit_2.append("Updated JSON data 2 sent to ESP32.")

           except Exception as e:
               self.textEdit_2.clear()
               self.textEdit_2.append(f"Error: {str(e)}")
        else:
            self.textEdit_2.clear()
        self.textEdit_2.append("Not connected to a serial port.")
   
    def clear_table_2(self):
        self.tableWidget_2.clearContents()
        self.tableWidget_2.setRowCount(0)

    def enable_dark_mode(self):
        # Define a dark color palette
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

        # Apply the dark palette to the application
        self.setPalette(dark_palette)

        # Set the stylesheet to enhance dark mode appearance (optional)
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

        self.update_widget_styles(self)

        # Update the appearance of widgets (e.g., buttons, text boxes) as needed
    def update_widget_styles(self, widget):
        # Recursively update widget styles
            if isinstance(widget, QtWidgets.QLabel):
               widget.setStyleSheet("color: white;")
            elif isinstance(widget, QtWidgets.QPushButton):
               widget.setStyleSheet(" color: black;")
            elif isinstance(widget, QtWidgets.QComboBox):
                combo_box_style = "color: black;"
                combo_box_style += "background-color: #ffffff;"  # Background color for the combo box
                widget.setStyleSheet(combo_box_style)
            elif isinstance(widget,QtWidgets.QCheckBox):
                widget.setStyleSheet("color:white")

            for child_widget in widget.findChildren(QtWidgets.QWidget):
                self.update_widget_styles(child_widget)
    
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SerialMonitorApp()
    window.show()
    sys.exit(app.exec_())