import serial
import time
import tkinter as tk
from tkinter import messagebox

def initialize_serial(port, baudrate=9600, timeout=1) -> serial.Serial | None:
    """Initialize the serial connection."""
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"Connected to {port}")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def send_command(ser: serial.Serial, command) -> str | None:
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

def get_status(ser) -> str | None:
    """Get the status of the device."""
    response = send_command(ser, "X81")
    return response

def set_motor_speed(ser, speed) -> str | None:
    """Set the motor speed in steps per second."""
    if speed > 3200:
        speed = 3200
        print("Maximum speed exceeded. Speed has been reset to 3200 steps/s.")
    elif speed < 0:
        speed = 0
        print("Invalid speed input. Speed has been reset to 0 steps/s.")

    command = f"X81E{speed}"
    response = send_command(ser, command)
    return response

def move_clockwise(ser) -> str | None:
    """Move the motor clockwise."""
    response = send_command(ser, "X81C+")
    return response

def move_counter_clockwise(ser) -> str | None:
    """Move the motor counter-clockwise."""
    response = send_command(ser, "X81C-")
    return response

def abort_movement(ser) -> str | None:
    """Abort/stop motor movement."""
    response = send_command(ser, "X81!")
    return response

def create_gui(serial_connection):
    """Create the GUI for controlling the motor."""
    direction = ["clockwise"]  # List to store the current direction
    motor_running = [False]

    def update_speed(event=None) -> None:
        try:
            speed = int(speed_entry.get())
            if speed > 3200:
                speed = 3200
                print("Maximum speed exceeded. Speed has been reset to 3200 steps/s.")
            elif speed < 0:
                speed = 0
                print("Invalid speed input. Speed has been reset to 0 steps/s.")

            set_motor_speed(serial_connection, speed)
            if motor_running[0]:
                start_motor()
            # messagebox.showinfo("Success", f"Motor speed updated to {speed} steps/s")
        except ValueError:
            messagebox.showerror("Error", "Invalid speed input")

    def start_motor() -> None:
        try:
            speed = int(speed_entry.get())
            if speed > 3200:
                speed = 3200
                print("Maximum speed exceeded. Speed has been reset to 3200 steps/s.")
            elif speed < 0:
                speed = 0
                print("Invalid speed input. Speed has been reset to 0 steps/s.")

            set_motor_speed(serial_connection, speed)
            if direction[0] == "clockwise":
                move_clockwise(serial_connection)
            else:
                move_counter_clockwise(serial_connection)
            motor_running[0] = True
            # messagebox.showinfo("Success", f"Motor started at {speed} steps/s, moving {direction[0]}")
        except ValueError:
            messagebox.showerror("Error", "Invalid speed input")

    def stop_motor() -> None:
        abort_movement(serial_connection)
        motor_running[0] = False
        # messagebox.showinfo("Info", "Motor stopped")

    def change_direction() -> None:
        if motor_running[0]:
            if direction[0] == "clockwise":
                direction[0] = "counter-clockwise"
                move_counter_clockwise(serial_connection)
            else:
                direction[0] = "clockwise"
                move_clockwise(serial_connection)
        else:
            if direction[0] == "clockwise":
                direction[0] = "counter-clockwise"
            else:
                direction[0] = "clockwise"
            # messagebox.showinfo("Info", f"Motor direction changed to {direction[0]}")

    root = tk.Tk()
    root.title("Motor Controller")

    tk.Label(root, text="Motor Speed (steps/s):").pack(pady=5)
    speed_entry = tk.Entry(root)
    speed_entry.pack(pady=5)
    speed_entry.bind("<Return>", lambda event: start_motor())

    start_button = tk.Button(root, text="Start Motor", command=start_motor)
    start_button.pack(pady=5)

    stop_button = tk.Button(root, text="Stop Motor", command=stop_motor)
    stop_button.pack(pady=5)

    direction_button = tk.Button(root, text="Change Direction", command=change_direction)
    direction_button.pack(pady=5)

    root.geometry("300x180")
    root.mainloop()

if __name__ == "__main__":
    # Replace 'COM3' with the actual port name for your device
    port_name = 'COM13'

    # Initialize the serial connection
    ser = initialize_serial(port_name)

    if ser:
        # Start the GUI
        create_gui(ser)

        # Close the serial connection when done
        ser.close()