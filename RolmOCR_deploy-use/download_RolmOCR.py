from huggingface_hub import snapshot_download
import os

# 模型名称
model_name = "reducto/RolmOCR"

# 下载路径（可选）
output_dir = "./RolmOCR_model"

# 下载模型
try:
    print(f"正在下载模型 {model_name}...")
    # 使用 snapshot_download 下载整个模型仓库
    download_path = snapshot_download(repo_id=model_name, cache_dir=output_dir)
    print(f"模型已成功下载到: {download_path}")
except Exception as e:
    print(f"下载失败: {e}")

