from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
import os

# 指定本地存储路径
local_model_path = "./models/Qwen2-VL-7B-Instruct"

# 下载模型到本地（如果尚未下载）
if not os.path.exists(local_model_path):
    print("Downloading model to local path...")
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct",
        torch_dtype="auto",
        device_map="auto",
        cache_dir=local_model_path  # 指定缓存目录
    )
    processor = AutoProcessor.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct",
        cache_dir=local_model_path  # 指定缓存目录
    )
    print(f"Model downloaded and cached at: {local_model_path}")
else:
    print("Model already exists locally.")