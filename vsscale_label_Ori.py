# tsc_label.py
from PIL import Image, ImageDraw, ImageFont
import serial
import time

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
    font = ImageFont.truetype(font_path, font_size)

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


        print("data")
        print("header_text:",header_text)
        print("table_text:",table_text)
        print("product_name:",product_name)
        print("pd_item_number:",pd_item_number)
        print("pd_date:",pd_date)
        print("mat_size:",mat_size)
        print("mat_grade:",mat_grade)
        print("pd_weight:",pd_weight)
        print("pd_item_remark:",pd_item_remark)

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
        print("Label sent to printer.")
