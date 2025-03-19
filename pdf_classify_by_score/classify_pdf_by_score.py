"""
需要修改这个代码实现：
寻找一个阈值，如果出现有一个score低于这个阈值，整个样本划分成低质量数据集中；
如果所有score大于这个阈值，则样本划分成正常质量的数据集
"""
# 通过json文件进行划分（根据阈值），最后把json,pdf,ocr,tif文件都放入不同的文件中：
import json
import os
import shutil


def process_json_files(input_folder, low_simple_folder, common_simple_folder):
    # 遍历输入文件夹下的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            base_name = filename[:-5]  # 去掉.json后缀
            input_file_path = os.path.join(input_folder, filename)

            with open(input_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            pages = data['pages']

            # 设置阈值
            threshold = 0.7

            # 检查是否有任意一个 score 小于阈值
            has_low_score = any(
                any(score < threshold for score in item['score'])
                for item in pages
            )

            if has_low_score:
                target_folder = low_simple_folder
            else:
                target_folder = common_simple_folder

            # 确保目标文件夹存在
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            # 定义需要同时处理的文件扩展名
            extensions = ['.ocr', '.pdf', '.tif', '.json']
            for ext in extensions:
                src_file_path = os.path.join(input_folder, base_name + ext)
                if os.path.exists(src_file_path):
                    shutil.copy(src_file_path, os.path.join(target_folder, base_name + ext))
                    print(f"File {base_name + ext} has been copied to {target_folder}.")

if __name__ == "__main__":
    input_folder = 'idl-train-00002'
    low_simple_folder = 'low_quality_samples'
    common_simple_folder = 'common_quality_samples'
    process_json_files(input_folder, low_simple_folder, common_simple_folder)