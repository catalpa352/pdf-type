from openai import OpenAI
import base64
import argparse



# 初始化 OpenAI 客户端
client = OpenAI(api_key="123", base_url="http://localhost:8000/v1")

model = "reducto/RolmOCR"


# 编码图像为 Base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# 使用 RolmOCR模型进行 OCR
def ocr_page_with_rolm(img_base64):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_base64}"},
                    },
                    {
                        "type": "text",
                        "text": "Please return all the content in this picture in markdown format.If images are detected to exist in this picture,replace them with the <image> symbol ",
                    },
                ],
            }
        ],
        temperature=0.2,
        max_tokens=11000
    )
    return response.choices[0].message.content


# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description="Perform OCR on an image using RolmOCR_deploy-use.")
    parser.add_argument(
        "--image_path",
        type=str,
        required=True,
        help="Path to the image file you want to process."
    )
    parser.add_argument(
        "--output_md",
        type=str,
        required=True,
        help="Path to save the OCR result as a Markdown file."
    )
    return parser.parse_args()


if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()

    # 读取图片并编码为 Base64
    img_base64 = encode_image(args.image_path)

    # 调用 OCR 函数
    result = ocr_page_with_rolm(img_base64)
    print(result)

    # 将结果保存到指定的 Markdown 文件
    with open(args.output_md, "w", encoding="utf-8") as md_file:
        md_file.write(result)

    print(f"OCR result saved to {args.output_md}")