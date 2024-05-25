from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

import json

with open('secret.json') as f:
    secret = json.load(f)

KEY = secret['KEY']
ENDPOINT = secret['ENDPOINT']

computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def get_tags(filepath):
    with open(filepath, "rb") as local_image:
        tags_result = computervision_client.tag_image_in_stream(local_image)
    tags = tags_result.tags
    tags_name = [tag.name for tag in tags]
    return tags_name

def detect_objects(filepath):
    with open(filepath, "rb") as local_image:
        detect_objects_results = computervision_client.detect_objects_in_stream(local_image)
    objects = detect_objects_results.objects
    return objects

import streamlit as st
from PIL import ImageDraw
from PIL import ImageFont

st.title('物体検出アプリ')

uploaded_file = st.file_uploader('Choose an image...', type=['jpg', 'png'])
if uploaded_file is not None:
    img = Image.open(uploaded_file)

    # 一時ファイルとして保存してパスを取得
    img_path = f'temp_{uploaded_file.name}'
    img.save(img_path)

    # 物体検出を行う
    objects = detect_objects(img_path)

    # 描画
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font='./Helvetica 400.ttf', size=20)

    for object in objects:
        x = object.rectangle.x
        y = object.rectangle.y
        w = object.rectangle.w
        h = object.rectangle.h
        caption = object.object_property

        # テキストサイズを取得
        left, top, right, bottom = draw.textbbox((0, 0), caption, font=font)
        text_w = right - left
        text_h = bottom - top

        # バウンディングボックスを描画
        draw.rectangle([(x, y), (x+w, y+h)], fill=None, outline='green', width=5)
        # テキスト背景を描画
        draw.rectangle([(x, y - text_h), (x + text_w, y)], fill='green')
        # テキストを描画
        draw.text((x, y - text_h), caption, fill='white', font=font)

    st.image(img)

    # タグを取得して表示
    tags_name = get_tags(img_path)
    tags_name = ', '.join(tags_name)
    st.markdown('**認識されたコンテンツタグ**')
    st.markdown(f'> {tags_name}')

    # 一時ファイルを削除
    os.remove(img_path)
