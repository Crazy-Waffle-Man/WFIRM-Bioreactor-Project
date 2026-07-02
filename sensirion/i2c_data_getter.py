from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection

from sensirion_uart_scc1.drivers.scc1_slf3x import Scc1Slf3x
from sensirion_uart_scc1.drivers.slf_common import get_flow_unit_label
from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice
from time import sleep

def read_data_from_sensor(max_reads: int = -1, verbose: bool = False):
    print("Called rdfs")
    with ShdlcSerialPort(port=input("Sensor port: "), baudrate=115200) as port:
        print("Entered with block")
        device = Scc1ShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("Init device")
        sleep(5)
        device.set_sensor_type(Scc1Slf3x.SENSOR_TYPE) # Error here
        sleep(5)
        print("Set sensor type")
        sensor = Scc1Slf3x(device)
        print("Sensor init")
        # sensor.stop_continuous_measurement()
        sleep(5)
        print("serial_number:", sensor.serial_number)
        print("product id:", sensor.product_id)
        print("Flow;\tTemperature;\t Flag")
        flow_scale, unit = sensor.get_flow_unit_and_scale() # pyright: ignore[reportGeneralTypeIssues]
        sleep(5)
        sensor.start_continuous_measurement(interval_ms=2)
        sleep(5)
        try:
            if max_reads == -1:
                while True:
                    remaining, lost, data = sensor.read_extended_buffer()
                    if verbose:
                        print(f"Remaining bytes {remaining} and {lost}-sample lost")
                        print()
                    for flow, temperature, flag in data:
                        if verbose:
                            print(f'{flow / flow_scale} {get_flow_unit_label(unit)};\t{temperature / 200} C;\t {flag}')
                        yield flow / flow_scale
            else:
                for _ in range(max_reads):
                    remaining, lost, data = sensor.read_extended_buffer()
                    if verbose:
                        print(f"Remaining bytes {remaining} and {lost}-sample lost")
                        print()
                    for flow, temperature, flag in data:
                        if verbose:
                            print(f'{flow / flow_scale} {get_flow_unit_label(unit)};\t{temperature / 200} C;\t {flag}')
                        yield flow / flow_scale
        finally:
            sensor.stop_continuous_measurement()

if __name__ == "__main__":
    read_data_from_sensor(verbose=True)