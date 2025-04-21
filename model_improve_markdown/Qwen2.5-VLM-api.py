import argparse
from openai import OpenAI
import fitz  # PyMuPDF
import base64
import io
from PIL import Image
from dotenv import load_dotenv
import os

# 定义 ModelScope 的 API 配置
load_dotenv()
apikey = os.getenv("api_key")

client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1/',
    api_key=apikey,  # 替换为你的 ModelScope Token
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


def test_qwen(model_id, text_with_markdown, image_path, output_markdown_path):
    """使用 Qwen/Qwen2.5-VL-32B-Instruct 模型进行推理"""
    try:
        # 加载图片并转换为 Base64 编码
        img_base64 = image_to_base64(image_path)
        print(f"图片加载成功并已转换为 Base64 编码")

        # 构造输入消息
        messages = [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': text_with_markdown},  # 提示词部分，包含 Markdown 内容
                    {'type': 'image_url', 'image_url': {'url': f"data:image/png;base64,{img_base64}"}},  # 图片部分
                ],
            }
        ]

        # 调用模型
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            stream=False
        )

        # 打印模型响应
        print("模型响应：")
        generated_content = response.choices[0].message.content
        print(generated_content)

        # 将生成的内容保存到 Markdown 文件
        with open(output_markdown_path, "w", encoding="utf-8") as file:
            file.write(generated_content)
        print(f"Markdown 内容已成功保存到文件：{output_markdown_path}")

    except Exception as e:
        print(f"调用模型失败：{e}")


if __name__ == '__main__':
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="将 PDF 转换为图片并测试 Qwen 模型")

    # 添加命令行参数
    parser.add_argument("--pdf", required=True, help="输入的 PDF 文件路径")
    parser.add_argument("--markdown", required=True, help="输入的 Markdown 文件路径")
    parser.add_argument("--output_image", default="converted_from_pdf.png", help="输出pdf转换的图片路径")
    parser.add_argument("--output_markdown", required=True, help="改进后的 Markdown 文件路径")
    parser.add_argument("--model_id", help="使用的模型 ID")

    # 解析命令行参数
    args = parser.parse_args()

    # 输入路径
    pdf_path = args.pdf
    markdown_path = args.markdown
    output_image_path = args.output_image
    output_markdown_path = args.output_markdown
    model_id = args.model_id

    # 将 PDF 转换为图片
    pdf_to_image(pdf_path, output_image_path)

    # 提取 Markdown 文档内容
    markdown_content = read_markdown_content(markdown_path)
    if not markdown_content:
        print("无法继续，Markdown 文档内容提取失败。")
    else:
        print(f"Markdown 文档内容：\n{markdown_content}")

        # 构造提示词，包含 Markdown 内容
        text_with_markdown = f"""
        请根据由PDF转换成的图片内容，在OCR结果生成的Markdown文档内容基础上输出一个效果更好的Markdown内容,其他多余的内容不需要输出。
        效果更好markdown内容注意事项：
        1.图片可以使用<image>标签代替，图片的具体内容不需要输出
        2.纯文本，表格，公式，代码参考图片内容在OCR结果生成的Markdown文档内容基础上进行修改
        3.请你自己检查一下输出的markdown内容是否合理，不要比OCR结果生成的Markdown文档内容效果更差
        4.输出内容中不要添加：```markdown```这些内容方便能够直接可视化
        Markdown 文档内容如下：
        ```
        {markdown_content}
        ```

        后面的内容为已转换为 Base64 编码的PDF图片内容：
        """

        # 使用转换后的图片测试 Qwen/Qwen2.5-VL-32B-Instruct 模型
        test_qwen(
            model_id=model_id,
            text_with_markdown=text_with_markdown,
            image_path=output_image_path,
            output_markdown_path=output_markdown_path
        )