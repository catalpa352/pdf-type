# markdown文件提交gemini
import google.generativeai as genai
from PIL import Image
import base64
import fitz  # PyMuPDF
import io


def pdf_to_image(pdf_path, output_image_path):
    """将单页 PDF 文件转换为图片"""
    try:
        # 打开 PDF 文件
        pdf_document = fitz.open(pdf_path)
        # 确保 PDF 只有一页
        if pdf_document.page_count != 1:
            print("警告：PDF 含有多页，只有第一页会被处理")
        # 获取第一页
        page = pdf_document.load_page(0)
        # 将页面转换为图像
        pix = page.get_pixmap()
        # 将图像保存到内存中
        img_byte_arr = io.BytesIO()
        img_byte_arr.write(pix.tobytes("png"))
        img_byte_arr.seek(0)
        # 使用 PIL 打开图像以便于保存为文件
        img = Image.open(img_byte_arr)
        img.save(output_image_path, format='PNG')
        print(f"PDF 已成功转换为图片：{output_image_path}")
    except Exception as e:
        print(f"PDF 转换失败：{e}")


def image_to_base64(image_path):
    """将图片转换为 Base64 编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def read_markdown_content(markdown_path):
    """直接读取 Markdown 文件的原始内容"""
    try:
        # 打开并读取 Markdown 文件
        with open(markdown_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()
        return markdown_content
    except Exception as e:
        print(f"Markdown 文档读取失败：{e}")
        return ""


def test_gemini(apikey, text, image_path, markdown_content):
    # 配置 API 密钥
    genai.configure(api_key=apikey, transport='rest')
    model = genai.GenerativeModel('gemini-2.0-flash')

    # 加载图片并转换为 Base64 编码
    try:
        img_base64 = image_to_base64(image_path)
        print(f"图片加载成功并已转换为 Base64 编码")
    except Exception as e:
        print(f"图片加载或转换失败：{e}")
        return

    # 构造输入内容
    contents = [
        {"text": text},  # 文本部分
        {
            "inline_data": {
                "mime_type": "image/png",  # 根据图片格式设置 MIME 类型
                "data": img_base64  # 图片的 Base64 编码数据
            }
        },  # 图片部分
        {"text": f"\n下面是 Markdown 文档的内容：\n{markdown_content}"}  # 添加 Markdown 内容
    ]

    # 调用模型
    try:
        response = model.generate_content(contents, stream=False)  # 禁用流式传输
        print("模型响应：")
        print(response.text)

    except Exception as e:
        print(f"调用模型失败：{e}")


if __name__ == '__main__':
    apikey = "AIzaSyA_U5nVGQcQetZ1pz4BMzvH9wYpdaNh_K8"

    # 输入路径
    pdf_path = '/Users/xiaoyangtao/PycharmProjects/pdf_process/data/07-Printing_plate/image.pdf'  # 输入你的 PDF 路径
    markdown_path = '/Users/xiaoyangtao/PycharmProjects/pdf_process/data/07-Printing_plate/docling_result/image.md'  # 输入你的 Markdown 文件路径
    output_image_path = 'converted_from_pdf.png'  # 输出图片路径

    # 将 PDF 转换为图片
    pdf_to_image(pdf_path, output_image_path)

    # 提取 Markdown 文档内容
    markdown_content = read_markdown_content(markdown_path)
    if not markdown_content:
        print("无法继续，Markdown 文档内容提取失败。")
    else:
        print(f"Markdown 文档内容：\n{markdown_content}")

        # 使用转换后的图片测试 Gemini Pro Vision 模型
        test_gemini(
            apikey,
            text="""
            请根据由PDF转换成的图片内容检查以下由OCR结果生成的Markdown文档内容与排版是否一致，并用中文列出所有错误，忽略Markdown语言本身的错误。
            以下是常见的OCR结果错误示例，请在Markdown文档中寻找类似问题：
               1.数学公式错误：公式没有被识别或者公式内容识别有误。
               2.表格错误：表格结构丢失或者表格内容识别错误。
               3.代码错误：代码没有被识别或者代码内容识别错误
               4.排版错误：存在内容出现的顺序不正确。
               5.图片错误：图片没有识别或者图片内容识别错误
               6.段落分割错误：OCR结果可能会错误地将段落分割成多个部分，或者将不同段落合并在一起。
               7.纯文本错误： 纯文本没有被识别或者纯文本内容错误


            输出格式要求：使用数字标号一个个错误，不要举例子所有错误都要输出，其他内容不需要

            输出例子：
            1.数学公式错误：公式不完整
            2.表格错误： 表格缺失内容
            3.代码错误：  import data代码没有被识别
            4.排版错误： data出现在image前面
            5.段落分割错误：一段被分成了三段

            请您仔细比对图片和Markdown文档内容，找出并列出所有的差异和错误，以便进行修正，如果有其他常见的OCR结果错误也需要列出来。
            """
            ,
            image_path=output_image_path,
            markdown_content=markdown_content
        )