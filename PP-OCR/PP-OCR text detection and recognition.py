from paddleocr import PaddleOCR, draw_ocr
import json
# 设置需要识别的PDF文件路径和页面编号
PAGE_NUM = 0  # 将识别页码前置作为全局，防止后续打开pdf的参数和前文识别参数不一致
pdf_path = 'print_text.pdf'
ocr = PaddleOCR(use_angle_cls=True,page_num=PAGE_NUM)  # 需要运行一次以下载并加载模型到内存中
# 如果需要使用GPU，请取消以下行的注释，并注释上一行
# ocr = PaddleOCR(use_angle_cls=True, lang="ch", page_num=PAGE_NUM, use_gpu=0)
result = ocr.ocr(pdf_path, cls=True)

# 保存识别结果：
result2 = []
for idx, res_per_page in enumerate(result):  # 使用enumerate来获取当前是第几页
    if res_per_page is None:  # 如果该页没有识别出内容，则跳过
        print(f"[DEBUG] Empty page {idx + 1} detected, skip it.")
        continue
    for line in res_per_page:
        # 在此处为每一行添加页码信息
        line_with_page_info = (line[0], line[1], idx + 1)  # 假设line是一个元组，这里我们添加了第三个元素，即页码
        print(line_with_page_info)
        result2.append(line_with_page_info)

idx = 1
pages_dict = {'pages': []}  # 初始化存储每页信息的结构

for item in result2:
    current_idx = item[2]

    # 检查是否已经存在current_idx对应的页面
    if current_idx > len(pages_dict['pages']):
        # 如果没有，则添加一个新的页面字典
        pages_dict['pages'].append({'text': [],'poly': [], 'score': []})

    # 确保current_idx不超过现有范围
    if current_idx <= len(pages_dict['pages']):
        pages_dict['pages'][current_idx - 1]['text'].append(item[1][0])
        pages_dict['pages'][current_idx - 1]['poly'].append(item[0])
        pages_dict['pages'][current_idx - 1]['score'].append(item[1][1])

# 将pages_dict保存为json文件
with open('pages_dict.json', 'w', encoding='utf-8') as f:
    json.dump(pages_dict, f, ensure_ascii=False, indent=4)

print("pages_dict已保存为pages_dict.json")




# 可视化检测结果：
import fitz
from PIL import Image
import cv2
import numpy as np
imgs = []
with fitz.open(pdf_path) as pdf:
    # 使用 pdf.page_count 获取 PDF 总页数
    for pg in range(0, pdf.page_count):
        page = pdf[pg]
        mat = fitz.Matrix(2, 2)
        pm = page.get_pixmap(matrix=mat, alpha=False)
        if pm.width > 2000 or pm.height > 2000:
            pm = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        img = Image.frombytes("RGB", [pm.width, pm.height], pm.samples)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        imgs.append(img)

for idx in range(len(result)):
    res = result[idx]
    if res == None:
        continue
    image = imgs[idx]
    boxes = [line[0] for line in res]
    txts = [line[1][0] for line in res]
    scores = [line[1][1] for line in res]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('result_page_{}.jpg'.format(idx))