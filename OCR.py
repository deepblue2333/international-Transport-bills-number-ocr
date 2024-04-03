import os

import requests
import re
import base64
import json
from urllib.parse import quote

from PyQt5.QtWidgets import QMessageBox


def code_img(image_path):
    with open(image_path, 'rb') as image_file:
        # 将图片内容进行 base64 编码
        image_data_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # 进行 URL 编码
    url_encoded_image = quote(image_data_base64)

    return url_encoded_image


# API_KEY = "D0qFZqOqpnRNOGrBq0G2Wj2j"
# SECRET_KEY = "Fhli240Lwzqdt9oVr7SNaG21d9GwoXfQ"


def request_ocr(url_encoded_image, api_key, secret_key):
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=" + get_access_token(api_key,
                                                                                                     secret_key)

    payload = f'image={url_encoded_image}&detect_direction=false&paragraph=false&probability=false'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


def get_access_token(api_key, secret_key):
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    return str(requests.post(url, params=params).json().get("access_token"))


def extract_words_from_json(json_text):
    # 移除字符串中的双引号
    json_text = json_text.strip('"')

    # 将 JSON 字符串解析为 Python 对象
    data = json.loads(json_text)

    # 提取所有 "words" 的值并存储在列表中
    words_list = [entry['words'] for entry in data['words_result']]

    return words_list


def find_matching_strings(string_list):
    # 定义正则表达式
    pattern = re.compile(r'\b[A-Za-z]{4}\d{7}\b.*')

    # 存储匹配结果的列表
    matching_strings = []

    # 遍历字符串列表并进行匹配
    for text in string_list:
        match = pattern.match(text)
        if match:
            matching_strings.append(match.group())

    return matching_strings


def get_files_in_directory(directory_path):
    file_list = []

    # 遍历目录下的所有文件
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_list.append(os.path.join(root, file))

    return file_list


def pdf_ocr(file_path, api_key, secret_key):  # 源文件为pdf格式
    # API_KEY = "D0qFZqOqpnRNOGrBq0G2Wj2j"
    # SECRET_KEY = "Fhli240Lwzqdt9oVr7SNaG21d9GwoXfQ"

    from pdf2img import PDFTransformer

    transformer = PDFTransformer()
    transformer.pdf2img(file_path)

    imgs = get_files_in_directory(transformer.output_folder)

    for img in imgs:
        base64img = code_img(img)
        json_file = request_ocr(base64img, api_key, secret_key)
        result_list = extract_words_from_json(json_file)
        print(result_list)
        odd_num = find_matching_strings(result_list)
        img_name = os.path.splitext(os.path.basename(img))[0]
        print(img_name, "匹配到的箱号列表:", odd_num)



def img_ocr(file_path, api_key, secret_key):  # 源文件为img格式
    # API_KEY = "D0qFZqOqpnRNOGrBq0G2Wj2j"
    # SECRET_KEY = "Fhli240Lwzqdt9oVr7SNaG21d9GwoXfQ"

    base64img = code_img(file_path)
    json_file = request_ocr(base64img, api_key, secret_key)
    result_list = extract_words_from_json(json_file)
    print(result_list)
    odd_num = find_matching_strings(result_list)
    print("匹配到的字符串列表:", odd_num)


def get_file_extension(file_path):
    # 使用os.path.splitext获取文件路径的扩展名
    _, extension = os.path.splitext(file_path)
    # 将扩展名转换为小写（例如，".PDF" -> ".pdf"）
    return extension.lower()


def is_pdf(file_path):
    # 判断是否为PDF文件
    return get_file_extension(file_path) == ".pdf"


def is_img(file_path):
    # 判断是否为img文件
    return get_file_extension(file_path) == ".png" or get_file_extension(file_path) == ".jpg"


def ocr(file_path, api_key, secret_key):
    if is_img(file_path):
        img_ocr(file_path, api_key, secret_key)
    elif is_pdf(file_path):
        pdf_ocr(file_path, api_key, secret_key)
