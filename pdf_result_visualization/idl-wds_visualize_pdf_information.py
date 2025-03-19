import fitz  # PyMuPDF
import json




local_pdf_path = "raw_data/ffkn0016.pdf"
local_json_path = "raw_data/ffkn0016.json"
with open(local_json_path, 'r') as file:
    data = json.load(file)


def percent_to_pixel(bbox_percentage, page_width, page_height):
    left = bbox_percentage[0] * page_width
    top = bbox_percentage[1] * page_height
    right = left + (bbox_percentage[2] * page_width)
    bottom = top + (bbox_percentage[3] * page_height)
    return [left, top, right, bottom]



doc = fitz.open(local_pdf_path)

for page_num, content in enumerate(data['pages']):
    page = doc.load_page(page_num)
    page_width = page.rect.width
    page_height = page.rect.height

    text_bbox_percentage = content['bbox']


    for idx, bbox_percent in enumerate(text_bbox_percentage):
        bbox = percent_to_pixel(bbox_percent, page_width, page_height)
        annot = page.add_rect_annot(bbox)
        annot.set_colors(stroke=[1, 0, 0])  # 红色
        annot.update()

        point = fitz.Point(bbox[0], bbox[1])
        page.insert_text(point, str(idx + 1), fontsize=8, color=(1, 0, 0))


output_red_pdf_path = "result/annotated_with_red_boxes_ffkn0016.pdf"
doc.save(output_red_pdf_path)
doc.close()