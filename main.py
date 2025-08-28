import vsscale_weight_controller 
import vsscale_label  


print(vsscale_weight_controller.read_weight())   #vsscale_weight_controller.read_weight() return 8bit int value of weight
print(vsscale_weight_controller.set_zero())     #vsscale_weight_controller.set_zero() set weight scale to be zero (auto reset register when zero is set) return bool
vsscale_label.print_label(
    port="/dev/ttySC1",
    baud=115200,
    header_text="header_747_270.bmp",
    table_text="table_vj_mono_2_270.bmp",
    product_name="วงท่อ 4.0X68",
    pd_item_number="2401015-115",
    pd_date="19/25/2025",
    mat_size="CDR4.6",
    mat_grade="SW485",
    pd_weight="2250",
    pd_item_remark="T04-015"
) #print label 