# mock_print.py
from vsscale_label_Ori import print_label

def main():
    # พอร์ตที่ต่อกับเครื่องพิมพ์ (ตรวจสอบด้วยคำสั่ง: ls /dev/ttyUSB*)
    port = "/dev/ttySC1"
    baud = 115200

    # --- ข้อมูลจำลองสำหรับทดสอบการพิมพ์ ---
    header_text = "Header"            # ชื่อไฟล์ .BMP ของหัวกระดาษ (ในเครื่อง)
    table_text = "Table"              # ชื่อไฟล์ .BMP ของตาราง (ในเครื่อง)
    product_name = "สินค้า"  # ชื่อสินค้า (จะถูกพิมพ์แบบหมุน)
    pd_item_number = "ITEM-00123"
    pd_date = "2025-10-09"
    mat_size = "2.5x1200"
    mat_grade = "SS400"
    pd_weight = "1250.6 kg"
    pd_item_remark = "test"

    print("🖨️ เริ่มสั่งปริ้นฉลากตัวอย่าง...")

    try:
        print_label(
            port=port,
            baud=baud,
            header_text=header_text,
            table_text=table_text,
            product_name=product_name,
            pd_item_number=pd_item_number,
            pd_date=pd_date,
            mat_size=mat_size,
            mat_grade=mat_grade,
            pd_weight=pd_weight,
            pd_item_remark=pd_item_remark,
        )
        print("✅ การสั่งพิมพ์เสร็จสมบูรณ์")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดระหว่างพิมพ์: {e}")

if __name__ == "__main__":
    main()
