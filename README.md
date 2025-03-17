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
