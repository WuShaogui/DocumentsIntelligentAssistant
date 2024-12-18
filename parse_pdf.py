# -*- coding: utf-8 -*-
import io
import os
from PIL import Image
import pymupdf
import shutil
import tqdm

def parse_pdf(pdf_path, save_dir):
    """
    This function parses a PDF file and extracts text from each page.

    :param pdf_path: Path to the PDF file.
    :param save_dir: Directory where extracted text will be saved as Markdown files.
    :return: None
    """

    # Open the PDF document
    pages = pymupdf.open(pdf_path)

    img_idx = 0
    doc_idx = 0
    save_flag = False
    lines_text = ''
    save_page_idx = ''
    save_page_type = ''

    for page in tqdm.tqdm(pages):
        page_text = page.get_text("dict")
        blocks = page_text["blocks"]  # the list of block dictionaries
        
        if len(blocks)<=2:
            continue
        # print(blocks)
        page_type=blocks[0]['lines'][0]['spans'][0]['text']
        page_idx=str(blocks[1]['lines'][0]['spans'][0]['text'])

        for idx in range(2,len(blocks)):
            block=blocks[idx]
            # print(block)
            if block["type"] == 0:
                lines=block['lines']
                for line in lines:
                    spans=line['spans']
                    spans_text=''
                    for span in spans:
                        if span['size']>9.9 and span['font']=='FZLTZCHK--GBK1-0':
                            if save_flag==True and len(lines_text)>0:
                                with open(f'{save_dir}/doc{save_page_idx}-{save_page_type}-{doc_idx}.md',encoding='utf-8', mode='w') as fw:
                                    fw.write(lines_text)
                                lines_text=''
                                if spans_text.startswith('#'):
                                    spans_text+=span['text']
                                else:
                                    spans_text="# "+span['text']
                                doc_idx+=1
                                save_flag=False
                            else:
                                if spans_text.startswith('#'):
                                    spans_text+=span['text']
                                else:
                                    spans_text="# "+span['text']
                        else:
                            if span['size']>9.9 and span['font']=='FZLTHJW--GB1-0':
                                if spans_text.startswith('##'):
                                    spans_text+=span['text']
                                else:
                                    spans_text="## "+span['text']
                            else:
                                save_flag=True
                                save_page_idx=page_idx
                                save_page_type=page_type
                                spans_text+=span['text']

                    lines_text+=spans_text+'\n'
            if block["type"] == 1:
                img_bytes=block['image']
                width=block['width']
                height=block['height']
                colorspace=block['colorspace']
                image_data=io.BytesIO(img_bytes)
                img=Image.open(image_data)
                
                if width >500 and height>500:
                    image_name=f'img{page_idx}-{img_idx}'+'.png'
                    img.save(os.path.join(save_dir,image_name),format='png')
                    lines_text+='|'+image_name+'|'
                    img_idx+=1

    with open(f'{save_dir}/doc{save_page_idx}-{doc_idx}.md',encoding='utf-8', mode='w') as fw:
        fw.write(lines_text)

if __name__ == "__main__":
    pdf_path = "data\data.pdf"
    save_dir = "preprocess"
    
    if os.path.exists(save_dir) and os.path.isdir(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir)
    # os.makedirs(os.path.join(save_dir,'images'))

    parse_pdf(pdf_path, save_dir)