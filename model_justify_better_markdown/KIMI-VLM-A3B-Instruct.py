import os
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
import fitz  # PyMuPDF
import io
import argparse

# 定义本地缓存路径
local_cache_dir = "./moonshot_local_cache"

# 确保本地缓存目录存在
os.makedirs(local_cache_dir, exist_ok=True)

# 模型的远程路径
model_path = "moonshotai/Kimi-VL-A3B-Instruct"

# 加载模型和处理器到本地缓存路径
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype="auto",
    device_map="auto",
    trust_remote_code=True,
    cache_dir=local_cache_dir  # 下载到本地缓存
)
processor = AutoProcessor.from_pretrained(
    model_path,
    trust_remote_code=True,
    cache_dir=local_cache_dir  # 下载到本地缓存
)


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


def test_moonshot(model, processor, text_with_markdown, image_path):
    """使用 moonshotai/Kimi-VL-A3B-Instruct 模型进行推理"""
    try:
        # 加载图片
        image = Image.open(image_path)

        # 构造输入消息
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {"type": "text", "text": text_with_markdown},  # 提示词部分，包含 Markdown 内容
                ],
            }
        ]

        # 准备推理所需的数据
        text = processor.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
        inputs = processor(images=image, text=text, return_tensors="pt", padding=True, truncation=True).to(model.device)

        # 推理生成输出
        generated_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        response = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]

        # 打印模型响应
        print("模型响应：")
        print(response)

    except Exception as e:
        print(f"调用模型失败：{e}")


if __name__ == '__main__':
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="PDF 和 Markdown 对比工具")
    parser.add_argument("--pdf_path", required=True, help="输入的 PDF 文件路径")
    parser.add_argument("--markdown_path", required=True, help="输入的 Markdown 文件路径")
    parser.add_argument("--output_image_path", default="converted_from_pdf.png", help="pdf转换的图片路径")

    args = parser.parse_args()

    # 将 PDF 转换为图片
    pdf_to_image(args.pdf_path, args.output_image_path)

    # 提取 Markdown 文档内容
    markdown_content = read_markdown_content(args.markdown_path)
    if not markdown_content:
        print("无法继续，Markdown 文档内容提取失败。")
    else:
        print(f"Markdown 文档内容：\n{markdown_content}")

        # 构造提示词，包含 Markdown 内容
        text_with_markdown = f"""
        请根据由PDF转换成的图片内容检查以下Markdown文档内容与图片内容是否一致，并用中文列出所有错误，忽略Markdown语言本身的错误。
        以下是常见的OCR结果错误的定义，请在Markdown文档中寻找这些错误：
               1.数学公式错误：公式没有被识别或者公式内容识别有误。
               2.表格错误：表格结构丢失或者表格内容识别错误。
               3.代码错误：代码没有被识别或者代码内容识别错误
               4.排版错误：存在内容出现的顺序不正确。
               5.图片错误：图片没有识别或者图片内容识别错误
               6.段落分割错误：OCR结果可能会错误地将段落分割成多个部分，或者将不同段落合并在一起。
               7.纯文本错误： 纯文本没有被识别或者纯文本内容错误


        输出格式要求：使用数字标号，每一个数字标号的内容为所有具体的错误以及错误的原因（不要举例子我需要全部的错误），除了数字标号内容之外的内容不需要输出

        Markdown 文档内容如下：
        ```
        {markdown_content}
        ```

        请您仔细比对图片和Markdown文档内容，找出并列出所有的差异和错误，以便进行修正，如果有其他常见的OCR结果错误也需要列出来。
        """

        # 使用转换后的图片测试 moonshotai/Kimi-VL-A3B-Instruct 模型
        test_moonshot(
            model=model,
            processor=processor,
            text_with_markdown=text_with_markdown,
            image_path=args.output_image_path,
        )


#python KIMI-VLM-A3B-Instruct.py --pdf_path ./papers/double_column/table_code.pdf --markdown_path ./Kimi-VL-A3B-Instruct_paper/double_column/table_code.md --output_image_path converted_from_pdf.png