import os
import fitz  # PyMuPDF
from paddlex import create_model
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader


#注册本地字体：
def register_custom_font(ttf_file_path):
    """
    注册自定义字体，使用 TTF 文件名（不含扩展名）作为字体名称
    :param ttf_file_path: TTF 文件路径
    :return: 字体名称
    """
    try:
        # 提取文件名（不含扩展名）作为字体名称
        font_name = os.path.splitext(os.path.basename(ttf_file_path))[0]

        # 注册字体
        pdfmetrics.registerFont(TTFont(font_name, ttf_file_path))
        print(f"Font '{font_name}' registered successfully.")
        return font_name
    except Exception as e:
        print(f"Error registering font: {e}")
        return None

#获取pdf大小：
def get_pdf_page_size(pdf_path):
    """
    获取 PDF 页面尺寸（宽度和高度）
    :param pdf_path: 原始 PDF 文件路径
    :return: 页面尺寸 (width, height)
    """
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]  # 获取第一页作为参考
        width = float(page.mediabox.upper_right[0])  # 宽度
        height = float(page.mediabox.upper_right[1])  # 高度
        print(f"Original PDF page size: {width} x {height}")
        return width, height
    except Exception as e:
        print(f"Error reading PDF dimensions: {e}")
        return letter  # 如果无法获取尺寸，回退到默认 Letter 尺寸

#绘制pdf文本：
def create_pdf(json_data, output_path, original_pdf_path, font_name="Helvetica", font_size=12,
               font_color=(0, 0, 0), align="left", line_spacing_multiplier=1.5):
    """
    创建 PDF 文件
    :param json_data: JSON 数据
    :param output_path: 输出 PDF 文件路径
    :param original_pdf_path: 原始 PDF 文件路径
    :param font_name: 字体名称
    :param font_size: 字体大小
    :param font_color: 字体颜色 (R, G, B)，范围为 0-1
    :param align: 对齐方式 ("left", "center", "right")
    :param line_spacing_multiplier: 行间距倍数，默认为 1.5
    """
    # 获取原始 PDF 页面尺寸
    width, height = get_pdf_page_size(original_pdf_path)

    c = canvas.Canvas(output_path, pagesize=(width, height))

    # 计算行间距
    line_spacing = font_size * line_spacing_multiplier

    for page in json_data['pages']:
        texts = page['text']
        polys = page.get('poly', [])

        if polys:
            current_y = None  # 用于跟踪当前行的 y 坐标
            for text, poly_points in zip(texts, polys):
                # 提取 X 和 Y 坐标
                x_coords = [point["X"] * width for point in poly_points]  # 映射到实际宽度
                y_coords = [point["Y"] * height for point in poly_points]  # 映射到实际高度

                # 确定矩形框的边界
                min_x = min(x_coords)  # 左边界的 x 坐标
                max_x = max(x_coords)  # 右边界的 x 坐标
                min_y = min(y_coords)  # 下边界的 y 坐标
                max_y = max(y_coords)  # 上边界的 y 坐标

                # 转换 Y 坐标（ReportLab 使用左下角为原点）
                y_top = height - min_y  # 矩形框顶部的 y 坐标

                # 如果是新段落，更新当前行的 y 坐标
                if current_y is None:
                    current_y = y_top
                else:
                    current_y -= line_spacing  # 应用行间距

                # 设置字体和大小
                c.setFont(font_name, font_size)

                # 设置字体颜色
                c.setFillColorRGB(*font_color)  # 使用 RGB 颜色

                # 根据对齐方式绘制文本
                if align == "center":
                    # 居中对齐
                    text_width = c.stringWidth(text, font_name, font_size)
                    text_x = min_x + (max_x - min_x - text_width) / 2
                    c.drawCentredString(text_x, current_y, text)
                elif align == "right":
                    # 右对齐
                    text_width = c.stringWidth(text, font_name, font_size)
                    text_x = max_x - text_width
                    c.drawRightString(text_x, current_y, text)
                else:
                    # 默认左对齐
                    c.drawString(min_x, current_y, text)

        c.showPage()  # 完成当前页

    c.save()  # 保存 PDF 文件


# 读取json文件
def read_json_file(json_path):
    """
    读取并解析JSON文件。
    :param json_path: JSON文件路径
    :return: 解析后的JSON数据（字典或列表）
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"文件未找到: {json_path}")

    with open(json_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件解析失败: {e}")


# 根据表格预测结果的score值进行过滤：
def filter_by_score(data, threshold):
    result = []
    for item in data:
        if item['score'] > threshold:
            result.append(item)
    return result


# 在PDF页面上绘制表格框的预测结果
def draw_predictions_on_pdf(pdf_path, output_pdf_path, predictions):
    """
    在PDF文件上绘制预测结果。
    :param pdf_path: 输入的PDF文件路径
    :param output_pdf_path: 输出带注释的PDF文件路径
    :param predictions: 每页的预测结果 (list of lists)
    """
    doc = fitz.open(pdf_path)

    if len(predictions) != len(doc):
        raise ValueError("预测结果的数量与PDF页面数量不匹配")

    for page_num, page_preds in enumerate(predictions):
        page = doc[page_num]

        for pred in page_preds:
            bbox = pred["coordinate"]
            xmin, ymin, xmax, ymax = bbox

            rect = fitz.Rect(xmin, ymin, xmax, ymax)
            page.draw_rect(rect, color=(0, 0, 0), width=1.5)  # 绘制矩形框
            # # 添加标签文本
            # label = pred["label"]
            # score = pred["score"]
            # text = f"{label} ({score:.2f})"
            # page.insert_text((xmin, ymin - 10), text, fontsize=8, color=(1, 0, 0))

    doc.save(output_pdf_path)
    doc.close()


#  处理多个页面的 JSON 数据并在 PDF 上绘制预测结果
def process_multiple_pages(pdf_path, output_pdf_path, json_folder, threshold):
    """
    处理多个页面的 JSON 数据并在 PDF 上绘制预测结果。
    :param pdf_path: 输入的PDF文件路径
    :param output_pdf_path: 输出带注释的PDF文件路径
    :param json_folder: 包含 JSON 文件的文件夹路径
    :param threshold: 过滤阈值
    """
    json_files = sorted(
        [f for f in os.listdir(json_folder) if f.startswith("res_page_") and f.endswith(".json")],
        key=lambda x: int(x.split("_")[2].split(".")[0])
    )

    doc = fitz.open(pdf_path)
    if len(json_files) != len(doc):
        raise ValueError("JSON 文件数量与 PDF 页面数量不匹配")
    doc.close()

    all_predictions = []

    for json_file in json_files:
        json_path = os.path.join(json_folder, json_file)
        json_data = read_json_file(json_path)

        filtered_data = filter_by_score(json_data['boxes'], threshold)
        all_predictions.append(filtered_data)

    draw_predictions_on_pdf(pdf_path, output_pdf_path, all_predictions)
    print(f"带注释的 PDF 已保存到: {output_pdf_path}")

def main():
    original_pdf_path = "fjny0110.pdf"  # 替换为你的原始 PDF 文件路径
    json_file_path = "fjny0110.json"  # 替换为你的 JSON 文件路径
    output_pdf_path = "output_text.pdf"
    ttf_file_path = "/System/Library/Fonts/Supplemental/AppleMyungjo.ttf"  # 替换为你的 TTF 文件路径（可选）
    font_size = 12  # 字体大小
    font_color = (0, 0, 0)  # 字体颜色，红色 (R, G, B)，范围为 0-1
    align = "left"  # 对齐方式 ("left", "center", "right")
    line_spacing_multiplier = 1  # 行间距倍数
    # 加载 JSON 数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON data from '{json_file_path}'.")
        return

    # 如果提供了 TTF 文件路径，则注册自定义字体
    if ttf_file_path:
        font_name = register_custom_font(ttf_file_path)
        if not font_name:
            print("Failed to register custom font. Using default font.")
            font_name = "Helvetica"  # 回退到默认字体
    else:
        font_name = "Helvetica"  # 默认字体

    # 创建 PDF 文件与绘制纯文本
    create_pdf(
        json_data,
        output_pdf_path,
        original_pdf_path,
        font_name=font_name,
        font_size=font_size,
        font_color=font_color,
        align=align,
        line_spacing_multiplier=line_spacing_multiplier
    )



    #绘制表格：
    pdf_path_draw=output_pdf_path
    output_dir = "./output/"#保存表格识别结果地址
    output_pdf_path2 = "output_text&table.pdf"  # 输出PDF路径
    threshold = 0.8  # 过滤阈值
    # 创建模型
    model = create_model(model_name="RT-DETR-L_wired_table_cell_det")
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 打开 PDF 文件
    doc = fitz.open(original_pdf_path)

    # 遍历每一页，提取图像并进行预测
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # 加载页面
        pix = page.get_pixmap()  # 将页面转换为图像
        image_path = f"{output_dir}page_{page_num + 1}.jpg"
        pix.save(image_path)  # 保存图像到文件

        # 对图像进行预测
        output = model.predict(image_path, threshold=0.3, batch_size=1)

        # 处理预测结果
        for res in output:
            res.print(json_format=False)  # 打印结果
            res.save_to_img(output_dir)  # 保存可视化结果
            res.save_to_json(f"{output_dir}res_page_{page_num + 1}.json")  # 保存 JSON 结果

    print("PDF页面处理完成！")
    json_folder = output_dir
    process_multiple_pages(pdf_path_draw, output_pdf_path2, json_folder, threshold)


if __name__ == "__main__":
    main()