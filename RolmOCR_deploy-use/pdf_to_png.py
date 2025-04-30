import os
from pdf2image import convert_from_path
import argparse


def convert_pdfs_to_images(pdf_folder, output_folder):
    """
    将指定文件夹中的所有 PDF 文件转换为 PNG 图片。

    :param pdf_folder: 包含 PDF 文件的文件夹路径
    :param output_folder: 输出 PNG 图片的文件夹路径
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 遍历 PDF 文件夹中的所有文件
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):  # 只处理 PDF 文件
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"Processing: {pdf_path}")

            # 将 PDF 转换为图像
            images = convert_from_path(pdf_path, dpi=300)  # dpi 控制图像分辨率

            # 保存每一页为 PNG 图片
            for i, image in enumerate(images):
                image_filename = f"{os.path.splitext(filename)[0]}_page_{i + 1}.png"
                image_path = os.path.join(output_folder, image_filename)
                image.save(image_path, "PNG")
                print(f"Saved: {image_path}")


if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Convert PDFs in a folder to images.")
    parser.add_argument("pdf_folder", type=str, help="Path to the folder containing PDF files.")
    parser.add_argument("output_folder", type=str, help="Path to the folder where images will be saved.")

    # 解析命令行参数
    args = parser.parse_args()

    # 使用从命令行获取的参数进行转换
    convert_pdfs_to_images(args.pdf_folder, args.output_folder)