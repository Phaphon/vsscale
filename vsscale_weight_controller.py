import random
import ctypes

# ===== CONFIG =====
USE_MOCK = False   # 👈 เปลี่ยนเป็น False ถ้ามีเครื่องจริง
RTU_PORT = "/dev/ttySC0"
RTU_BAUD = 9600
RTU_STOPBITS = 1
RTU_BYTESIZE = 8
RTU_PARITY = "N"
SLAVE_ID = 1
TIMEOUT = 1
# ==================

if not USE_MOCK:
    from pymodbus.client import ModbusSerialClient
    from pymodbus.exceptions import ModbusIOException

    print(f"Connecting to Modbus RTU on {RTU_PORT} at {RTU_BAUD} baud...")

    client = ModbusSerialClient(
        port=RTU_PORT,
        baudrate=RTU_BAUD,
        stopbits=RTU_STOPBITS,
        bytesize=RTU_BYTESIZE,
        parity=RTU_PARITY,
        timeout=TIMEOUT
    )

    def _read_weight():
        address = 0x00
        count = 1
        rr = client.read_holding_registers(address, count, slave=SLAVE_ID)
        if rr.isError():
            print(f"❌ Read failed at address {address}: {rr}")
            return None
        ret = ctypes.c_int16(rr.registers[0]).value
        #print(f"✅ Read success at address {address}: {ret}")
        return ret

    def _set_zero():
        address = 0x60
        value = 0b00000001
        wr = client.write_register(address, value, slave=SLAVE_ID)
        if wr.isError():
            print(f"❌ Write failed at address {address}: {wr}")
            return False
        print(f"✅ Write success at address {address}: {value}")
        return True

    def read_weight():
        if not client.connect():
            print("❌ Connection failed.")
            return None
        try:
            return _read_weight()
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        finally:
            client.close()

    def set_zero():
        if not client.connect():
            print("❌ Connection failed.")
            return False
        try:
            return _set_zero()
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            client.close()

else:
    # ----- MOCK MODE -----
    def read_weight():
        # คืนค่าน้ำหนักสุ่ม 2000–2500
        ret = random.randint(2000, 2500)
        #print(f"🎭 [MOCK] Read weight: {ret}")
        return ret

    def set_zero():
        #print("🎭 [MOCK] Set weight to zero.")
        return True
