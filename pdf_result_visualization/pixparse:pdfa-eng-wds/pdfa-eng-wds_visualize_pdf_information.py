# 红色黄色框在不同一个pdf中
import fitz  # PyMuPDF
import json

# 打开PDF文件路径
local_pdf_path = "0759470的位置标注结果/0759470.pdf"

# 加载JSON文件
local_json_path = "0759470的位置标注结果/0759470.json"
with open(local_json_path, 'r') as file:
    data = json.load(file)

content = data['pages'][0]

words_bbox_percentage = content['words']['bbox']
lines_bbox_percentage = content['lines']['bbox']
images_bbox_percentage = content['images_bbox']
images_bbox_no_text_overlap_percentage = content['images_bbox_no_text_overlap']

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
for idx, bbox_percent in enumerate(words_bbox_percentage):
    bbox = percent_to_pixel(bbox_percent, page_width, page_height)
    annot = page.add_rect_annot(bbox)
    annot.set_colors(stroke=[1, 0, 0])  # 红色
    annot.update()

    point = fitz.Point(bbox[0], bbox[1])
    page.insert_text(point, str(idx + 1), fontsize=8, color=(1, 0, 0))

# 保存带有红色框的PDF文档
output_red_pdf_path = "0759470的位置标注结果/annotated_with_red_boxes_0759470.pdf"
doc.save(output_red_pdf_path)
doc.close()

# 处理并保存带有黄色框的PDF
doc = fitz.open(local_pdf_path)
page = doc.load_page(0)

# 绘制行边界框（黄色）
for idx, bbox_percent in enumerate(lines_bbox_percentage):
    bbox = percent_to_pixel(bbox_percent, page_width, page_height)
    annot = page.add_rect_annot(bbox)
    annot.set_colors(stroke=[1, 1, 0])  # 黄色
    annot.update()

    point = fitz.Point(bbox[0], bbox[1])
    page.insert_text(point, str(idx + 1), fontsize=8, color=(1, 1, 0))

# 保存带有黄色框的PDF文档
output_yellow_pdf_path = "0759470的位置标注结果/annotated_with_yellow_boxes_0759470.pdf"
doc.save(output_yellow_pdf_path)
doc.close()


# 处理并保存带有绿色框的PDF
doc = fitz.open(local_pdf_path)
page = doc.load_page(0)
# 绘制图像边界框（绿色）
for idx, bbox_percent in enumerate(images_bbox_percentage):
    bbox = percent_to_pixel(bbox_percent, page_width, page_height)
    annot = page.add_rect_annot(bbox)
    annot.set_colors(stroke=[0, 1, 0])  # 绿色
    annot.update()

    point = fitz.Point(bbox[0], bbox[1])
    page.insert_text(point, str(idx + 1), fontsize=8, color=(0, 1, 0))

output_green_pdf_path = "0759470的位置标注结果/annotated_with_green_boxes_0759470.pdf"
doc.save(output_green_pdf_path)
doc.close()

# 处理并保存带有蓝色框（代表images_bbox_no_text_overlap）的PDF
doc = fitz.open(local_pdf_path)
page = doc.load_page(0)

# 绘制无文本重叠图像边界框（蓝色）
for idx, bbox_percent in enumerate(images_bbox_no_text_overlap_percentage):
    bbox = percent_to_pixel(bbox_percent, page_width, page_height)
    annot = page.add_rect_annot(bbox)
    annot.set_colors(stroke=[0, 0, 1])  # 蓝色
    annot.update()

    point = fitz.Point(bbox[0], bbox[1])
    page.insert_text(point, str(idx + 1), fontsize=8, color=(0, 0, 1))

output_blue_pdf_path = "0759470的位置标注结果/annotated_with_blue_boxes_0759470.pdf"
doc.save(output_blue_pdf_path)
doc.close()



print(f"Red boxes saved to {output_red_pdf_path}")
print(f"Yellow boxes saved to {output_yellow_pdf_path}")
print(f"Green boxes saved to {output_green_pdf_path}")
print(f"Blue boxes saved to {output_blue_pdf_path}")

