from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_driver import CrcCalculator
from sensirion_i2c_sf06_lf.device import Sf06LfDevice
from sensirion_i2c_sf06_lf.commands import InvFlowScaleFactors
import time

# def ...(port, baudrate) -> Generator
with ShdlcSerialPort(port="COM5", baudrate=115200) as port:
    device = Scc1ShdlcDevice(ShdlcConnection(port))
    device.set_sensor_type(3) # Flow sensor, thank goodness for docstrings.
    channel = I2cChannel(device.get_i2c_transceiver(), slave_address=0x08, crc=CrcCalculator(8, 0x32, 0xff, 0x0))

    sensor = Sf06LfDevice(channel)

    try:
        sensor.stop_continuous_measurement()
        time.sleep(0.1)
    except BaseException:
        ... # TODO: error handling
    (product_identifier, serial_number) = sensor.read_product_identifier()
    print(f"{product_identifier}\n{serial_number}")
    sensor.start_h2o_continuous_measurement()
    for i in range(500):
        try:
            time.sleep(0.02)
            (flow, temp, flags) = sensor.read_measurement_data(InvFlowScaleFactors.SLF3C_1300F)
            print(flow, temp, flags)
        except BaseException:
            continue
    sensor.stop_continuous_measurement()