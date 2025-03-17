import fitz  # PyMuPDF
import json

# 打开PDF文件路径
local_pdf_path = "fgdj0046的位置标注结果/fgdj0046.pdf"

# 加载JSON文件
local_json_path = "fgdj0046的位置标注结果/fgdj0046.json"
with open(local_json_path, 'r') as file:
    data = json.load(file)

content = data['pages'][0]

text_bbox_percentage = content['bbox']

def percent_to_pixel(bbox_percentage, page_width, page_height):
    """将百分比格式的bbox转换为像素值"""
    left = bbox_percentage[0] * page_width
    top = bbox_percentage[1] * page_height
    right = left + (bbox_percentage[2] * page_width)
    bottom = top + (bbox_percentage[3] * page_height)
    return [left, top, right, bottom]



# 处理并保存带有红色框的PDF
doc = fitz.open(local_pdf_path)
page = doc.load_page(0)
page_width = page.rect.width
page_height = page.rect.height

# 绘制单词边界框（红色）
for idx, bbox_percent in enumerate(text_bbox_percentage):
    bbox = percent_to_pixel(bbox_percent, page_width, page_height)
    annot = page.add_rect_annot(bbox)
    annot.set_colors(stroke=[1, 0, 0])  # 红色
    annot.update()

    point = fitz.Point(bbox[0], bbox[1])
    page.insert_text(point, str(idx + 1), fontsize=8, color=(1, 0, 0))

# 保存带有红色框的PDF文档
output_red_pdf_path = "fgdj0046的位置标注结果/annotated_with_red_boxes_fgdj0046.pdf"
doc.save(output_red_pdf_path)
doc.close()
