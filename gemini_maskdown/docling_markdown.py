import argparse
from docling.document_converter import DocumentConverter

def convert_pdf_to_markdown(source, output_file):
    """
    将 PDF 转换为 Markdown 并保存到指定文件
    """
    try:
        # 初始化 DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(source)

        # 导出为 Markdown 格式
        markdown_content = result.document.export_to_markdown()

        # 将 Markdown 内容写入文件
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(markdown_content)

        print(f"Markdown 输出已保存到 {output_file}")
    except Exception as e:
        print(f"转换失败：{e}")

if __name__ == '__main__':
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="将 PDF 转换为 Markdown 文件")

    # 添加命令行参数
    parser.add_argument("--pdf", required=True, help="输入的 PDF 文件路径")
    parser.add_argument("--output", required=True, help="输出的 Markdown 文件路径")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用转换函数
    convert_pdf_to_markdown(args.pdf, args.output)