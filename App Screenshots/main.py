import serial

# Open serial port
ser = serial.Serial('COM1', 9600)  # Adjust port and baud rate as needed

try:
    while True:
        # Read data from serial port
        data = ser.readline().strip()
        if data:
            print("Received:", data.decode('utf-8'))  # Decode bytes to string
except KeyboardInterrupt:
    print("Exiting...")
    ser.close()  # Close serial port on keyboard interrupt
