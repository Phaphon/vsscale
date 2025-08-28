from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException
import ctypes
# ===== CONFIG =====
RTU_PORT = "/dev/ttySC0"   # Change to your serial port, e.g. "/dev/ttySC0" or "COM3"
RTU_BAUD = 9600
RTU_STOPBITS = 1
RTU_BYTESIZE = 8
RTU_PARITY = "N"            # N,E,O
SLAVE_ID = 1
TIMEOUT = 1                 # seconds
# ==================

def _read_weight():
    address = 0x00
    count = 1
    """Function 03: Read Holding Registers"""
    rr = client.read_holding_registers(address, count, slave=SLAVE_ID)
    ret = ctypes.c_int16(rr.registers[0]).value 
    if isinstance(rr, ModbusIOException) or rr.isError():
        print(f"❌ Read failed at address {address}: {rr}")
        return None
    else:
        print(f"✅ Read success at address {address}: {ret}")
        return ret

def _set_zero():
    address = 0x60
    value = 0b00000001
    """Function 06: Write Single Register"""
    wr = client.write_register(address, value, slave=SLAVE_ID)
    if isinstance(wr, ModbusIOException) or wr.isError():
        print(f"❌ Write failed at address {address}: {wr}")
        return False
    else:
        print(f"✅ Write success at address {address}: {value}")
        return True

print(f"Connecting to Modbus RTU on {RTU_PORT} at {RTU_BAUD} baud...")

client = ModbusSerialClient(
    method='rtu',
    port=RTU_PORT,
    baudrate=RTU_BAUD,
    stopbits=RTU_STOPBITS,
    bytesize=RTU_BYTESIZE,
    parity=RTU_PARITY,
    timeout=TIMEOUT
)

def read_weight():
    if not client.connect():
        print("❌ Connection failed.")
    else:
        print("✅ Connected.")

    try:
        return _read_weight()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

def set_zero():
    if not client.connect():
        print("❌ Connection failed.")
    else:
        print("✅ Connected.")

    try:
        return _set_zero()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()