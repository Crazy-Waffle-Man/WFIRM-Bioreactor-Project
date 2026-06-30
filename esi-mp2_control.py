import serial
import time


def initialize_serial(port, baudrate=9600, timeout=1):
    """Initialize the serial connection."""
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"Connected to {port}")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def send_command(ser, command):
    """Send a command to the device and read the response."""
    if not ser:
        print("Serial port not initialized.")
        return None

    try:
        # Append a carriage return (\r) to the command
        full_command = command + '\r'
        ser.write(full_command.encode('ascii'))
        time.sleep(0.1)  # Allow time for the device to respond

        response = ser.read(ser.in_waiting).decode('ascii').strip()
        return response
    except Exception as e:
        print(f"Error sending command: {e}")
        return None

def get_status(ser):
    """Get the status of the device."""
    response = send_command(ser, "X81")
    return response

def set_motor_speed(ser, speed):
    """Set the motor speed in steps per second."""
    if not (0 <= speed <= 3200):
        print("Speed must be between 0 and 3200 steps per second.")
        return None

    command = f"X81E{speed}"
    response = send_command(ser, command)
    return response

def move_clockwise(ser):
    """Move the motor clockwise."""
    response = send_command(ser, "X81C+")
    return response

def move_counter_clockwise(ser):
    """Move the motor counter-clockwise."""
    response = send_command(ser, "X81C-")
    return response

def abort_movement(ser):
    """Abort/stop motor movement."""
    response = send_command(ser, "X81!")
    return response

if __name__ == "__main__":
    port_name = 'COM17'

    # Initialize the serial connection
    ser = initialize_serial(port_name)

    if ser:
        set_motor_speed(ser, 1600)
        move_clockwise(ser)
        time.sleep(2)
        move_counter_clockwise(ser)
        time.sleep(2)
        abort_movement(ser)
        
        print('Program finished!')
        

        # Close the serial connection
        ser.close()