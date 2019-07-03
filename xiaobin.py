# -*-encoding:utf-8 -*-
# 微软小冰链接：http://kan.msxiaobing.com/V3/Portal?task=yanzhi
import requests
import time
import base64
import json
from bs4 import BeautifulSoup

session = requests.Session()


# 获取参数tid
def getTid():
    url = 'http://kan.msxiaobing.com/V3/Portal?task=yanzhi'
    req = session.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup.select('#xb_log_info input')[0]['value']


# # 图片转为Base64
# def toBase64(imgUrl):
# 	req = session.get(imgUrl)
# 	return base64.b64encode(req.content)
def toBase64(path):
    with open(path, "rb") as f:
        base64_data = base64.b64encode(f.read())
        return base64_data


# 上传Base64加密图片获取图片url
def upload(imgBase64):
    url = 'http://kan.msxiaobing.com/Api/Image/UploadBase64'
    headers = {
        'Host': 'kan.msxiaobing.com',
        'Origin': 'http://kan.msxiaobing.com',
        'Referer': 'http://kan.msxiaobing.com/V3/Portal?task=yanzhi',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    req = session.post(url=url, headers=headers, data=imgBase64)
    json_data = json.loads(req.text)
    return json_data['Host'] + json_data['Url']


#### 小冰功能 ####

# 颜值测试
def yanzhi(imgUrl):
    tid = getTid()
    url = 'http://kan.msxiaobing.com/Api/ImageAnalyze/Process?service=yanzhi&tid=' + tid
    headers = {
        'Host': 'kan.msxiaobing.com',
        'Origin': 'http://kan.msxiaobing.com',
        'Referer': 'http://kan.msxiaobing.com/V3/Portal?task=yanzhi',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    imgInfo = upload(toBase64(imgUrl))
    CreateTime = str(int(time.time()))
    data = {
        'MsgId': CreateTime + '222',
        'CreateTime': CreateTime,
        'Content[imageUrl]': imgInfo
    }
    req = session.post(url=url, headers=headers, data=data)
    myjson = json.loads(req.text, strict=False)
    text = myjson['content']['text']
    return text


# 诗人小冰
def poem(imgUrl):
    tid = getTid()
    url = 'https://kan.msxiaobing.com/Api/ImageAnalyze/Process?service=poem&tid=' + tid
    headers = {
        'Host': 'kan.msxiaobing.com',
        'Origin': 'http://kan.msxiaobing.com',
        'Referer': 'http://kan.msxiaobing.com/V3/Portal?task=poem',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    imgInfo = upload(toBase64(imgUrl))
    CreateTime = str(int(time.time()))
    data = {
        'MsgId': CreateTime + '039',
        'CreateTime': CreateTime,
        'Content[imageUrl]': imgInfo
    }
    req = session.post(url=url, headers=headers, data=data)
    myjson = json.loads(req.text, strict=False)
    text = myjson['content']['text']
    return text
