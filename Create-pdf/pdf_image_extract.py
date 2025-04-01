import json
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
import os

class PDFImageAnalyzer:
    def __init__(self, model_path="models/Qwen2-VL-7B-Instruct/models--Qwen--Qwen2-VL-7B-Instruct/snapshots/eed13092ef92e448dd6875b2a00151bd3f7db0ac"):
        """
        初始化模型和处理器
        :param model_path: 本地模型路径
        """
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
              model_path,
              torch_dtype=torch.bfloat16,
              attn_implementation="flash_attention_2",
              device_map="auto",
        )
        self.processor = AutoProcessor.from_pretrained(model_path)
    #将PDF页面渲染为高分辨率图片
    def render_page_as_image(self, page, zoom=2):
        """
        将PDF页面渲染为高分辨率图片
        :param page: PyMuPDF页面对象
        :param zoom: 缩放因子，提高分辨率
        :return: PIL Image对象
        """
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("ppm")
        return Image.open(BytesIO(img_bytes)).convert("RGB")

    #使用大模型分析页面内容并提取图片信息
    def analyze_page(self, page_image, page_number):
        """
        使用大模型分析页面内容并提取图片信息
        :param page_image: PIL Image对象（整个页面）
        :param page_number: 页码
        :return: 包含图片信息的字典
        """
        try:
            # 准备页面图片
            buffered = BytesIO()
            page_image.save(buffered, format="PNG")
            img_str = buffered.getvalue()
            if not isinstance(img_str, bytes):
                raise ValueError("Image data is not in bytes format")
            # 构建提示词
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": img_str},
                        {"type": "text", "text": (
                            "Analyze this PDF page and extract all images with their details. "
                            "For each image, provide:\n"
                            "1. Its exact position on the page (coordinates and size)\n"
                            "2. Raw binary content\n"
                            "Format the response as a JSON object with 'images' array."
                        )},
                    ],
                }
            ]

            # 处理输入
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            # 确保 image_inputs 是字节类型
            for img_input in image_inputs:
                if not isinstance(img_input, bytes):
                    raise ValueError("Image input is not in bytes format")

            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to("cuda")

            # 生成响应
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )

            output_text = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]

            # 尝试解析JSON响应
            try:
                return {
                    "page_number": page_number,
                    "analysis": json.loads(output_text),
                    "raw_response": output_text
                }
            except json.JSONDecodeError:
                return {
                    "page_number": page_number,
                    "error": "Model did not return valid JSON",
                    "raw_response": output_text
                }

        except Exception as e:
            return {
                "page_number": page_number,
                "error": str(e)
            }

    def process_pdf(self, pdf_path):
        """
        处理PDF文件，分析每一页的内容
        :param pdf_path: PDF文件路径
        :return: 包含分析结果的JSON
        """
        result = {
            "pdf_file": pdf_path,
            "pages": []
        }

        try:
            doc = fitz.open(pdf_path)
            result["page_count"] = len(doc)

            for page_num, page in enumerate(doc, start=1):
                # 渲染整个页面为图片
                page_image = self.render_page_as_image(page)

                # 使用大模型分析页面
                page_result = self.analyze_page(page_image, page_num)
                result["pages"].append(page_result)

        except Exception as e:
            result["error"] = str(e)

        return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    analyzer = PDFImageAnalyzer()
    pdf_path = "fjny0110.pdf"  # 替换为您的PDF文件路径
    result_json = analyzer.process_pdf(pdf_path)
    print(result_json)
    # 可选：保存到文件
    with open("analysis_result.json", "w", encoding="utf-8") as f:
        f.write(result_json)
