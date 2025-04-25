# pdf-type
store different types of PDF files to facilitate subsequent document content identification and analysis.

- **01-Academic_papers**: 
  - Double column text and simple column text
  - Scanning academic papers
- **02-Docx**:
  - PDF converted from Docx.
  - Text, tables and pictures mixed
  - Both plain Chinese and plain English texts are included
- **03-PPT**:
  - PDF converted from PPT.
- **04-Table**:
  - PDF only include Table
- **05-Report**:
  - Reports from formal document
- **06-Poster**:
  - Posters from everyday life
- **07-Printing_plate**:
  - pdf made by printing
- **pdf_result_visualization**:
  - download pdfa-eng-train-xxxx.tar from https://huggingface.co/datasets/pixparse/pdfa-eng-wds and decompress
  - download idl-train-xxxxx.tar from https://huggingface.co/datasets/pixparse/idl-wds and decompress
  - use idl-wds_visualize_pdf_information.py and pdfa-eng-wds_visualize_pdf_information.py to visulize the result


- **gemini_maskdown/docling_markdown.py command use**:
  - python docling_markdown.py --pdf input_pdf_path --output output_markdown_path
- **gemini_maskdown/gemini_mardkown.py command use**:
  - python gemini-markdown.py --pdf input_pdf-path --markdown input_markdown_path --output_image pdf_converted_image_path
- **model_improve_markdown/gemini_modify.py command use**:
  - python gemini_modify.py --pdf input_pdf-path --markdown input_markdown_path --output_image pdf_converted_image_path --output_markdown output_markdown_path
- **model_improve_markdown/KIMI-VLM-modify.py command use**:
  - python KIMI-VLM-modify.py --pdf input_pdf-path --markdown input_markdown_path --output_image pdf_converted_image_path --output_markdown output_markdown_path
- **model_improve_markdown/Qwen2.5-VLM-api.py command use**:
  - python Qwen2.5-VLM-api.py --pdf input_pdf-path --markdown input_markdown_path --output_image pdf_converted_image_path --output_markdown output_markdown_path --model_id  Qwen/Qwen2.5-VL-32B-Instruct or Qwen/Qwen2.5-VL-7B-Instruct

- **model_justify_better_markdown/gemini_2.0_flask.py command use**:
  - python gemini_2.0_flask.py --pdf_path /path/to/your/pdf/file.pdf --markdown_path /path/to/your/markdown/file.md --output_image_path /path/to/output/image.png
- **model_justify_better_markdown/Qwen-vlm.py command use**:
  - python Qwen-vlm.py --pdf_path /path/to/your/pdf/file.pdf --markdown_path /path/to/your/markdown/file.md --output_image_path /path/to/output/image.png --model_id  Qwen/Qwen2.5-VL-7B-Instruct or Qwen/Qwen2.5-VL-32B-Instruct
- **model_justify_better_markdown/KIMI-VLM-A3B-Instruct.py command use**:
  - python KIMI-VLM-A3B-Instruct.py --pdf_path ./papers/double_column/table_code.pdf --markdown_path ./Kimi-VL-A3B-Instruct_paper/double_column/table_code.md --output_image_path converted_from_pdf.png






