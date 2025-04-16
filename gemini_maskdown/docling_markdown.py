from docling.document_converter import DocumentConverter

source = "/Users/xiaoyangtao/PycharmProjects/pdf_process/data/07-Printing_plate/image.pdf"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)

# 将输出保存到文件
output_file = "data/07-Printing_plate/docling_result/image.md"  # 指定保存的文件名
with open(output_file, "w", encoding="utf-8") as file:
    markdown_content = result.document.export_to_markdown()
    file.write(markdown_content)

print(f"Markdown 输出已保存到 {output_file}")