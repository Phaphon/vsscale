# vsscale_label.py
from PIL import Image, ImageDraw, ImageFont
import time

try:
    import serial
except ImportError:
    serial = None  # กัน error ถ้าไม่มี pyserial ตอน mock

# ===== CONFIG =====
USE_MOCK_LABEL = True   # 🔹 เปลี่ยนเป็น False ถ้าใช้งานจริง
# ==================

def print_label(
    port,
    baud,
    header_text,
    table_text,
    product_name,
    pd_item_number,
    pd_date,
    mat_size,
    mat_grade,
    pd_weight,
    pd_item_remark,
    font_path="/usr/share/fonts/truetype/tlwg/Waree.ttf",
    font_size=34
):
    # --- MOCK MODE ---
    if USE_MOCK_LABEL:
        print("🎭 [MOCK] Print label:")
        print(f"  Header: {header_text}, Table: {table_text}")
        print(f"  Product: {product_name}")
        print(f"  Item: {pd_item_number}, Date: {pd_date}")
        print(f"  Size/Grade: {mat_size}/{mat_grade}")
        print(f"  Weight: {pd_weight}, Remark: {pd_item_remark}")
        return True

    # --- REAL MODE ---
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        print("⚠️ Warning: Cannot load font, using default PIL font.")
        font = ImageFont.load_default()

    # --- Create rotated product_name bitmap ---
    dummy_img = Image.new("1", (1, 1), 1)
    draw = ImageDraw.Draw(dummy_img)
    text_width, text_height = draw.textsize(product_name, font=font)

    img = Image.new("1", (text_width, text_height), 1)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), product_name, font=font, fill=0)
    img = img.transpose(Image.ROTATE_270)

    width_bytes = (img.width + 7) // 8
    img_data = bytearray()
    pixels = img.load()
    for y in range(img.height):
        for x_byte in range(width_bytes):
            byte_val = 0
            for bit in range(8):
                x = x_byte * 8 + bit
                if x < img.width:
                    if pixels[x, y] != 0:  # white pixel
                        byte_val |= (1 << (7 - bit))
            img_data.append(byte_val)

    # --- Send commands to printer ---
    with serial.Serial(port, baud, timeout=2) as s:
        def send(cmd):
            s.write((cmd + "\r\n").encode("ascii"))
            time.sleep(0.01)

        send("SIZE 50 mm,80 mm")
        send("CLS")
        send(f"PUTBMP 0,0,\"{header_text}\"")
        send(f"PUTBMP 0,190,\"{table_text}\"")
        send(f"TEXT 265,350,\"3\",90,1,1,\"{pd_item_number}\"")
        send(f"TEXT 220,350,\"3\",90,1,1,\"{pd_date}\"")
        send(f"TEXT 180,350,\"3\",90,1,1,\"{mat_size}/{mat_grade}\"")
        send(f"TEXT 140,350,\"5\",90,1,1,\"{pd_weight}\"")
        send(f"TEXT 70,350,\"2\",90,2,2,\"{pd_item_remark}\"")
        s.write(f"BITMAP 290,350,{width_bytes},{img.height},1,".encode("ascii"))
        s.write(img_data)
        send("PRINT 1")

    print("✅ Label sent to printer.")
    return True