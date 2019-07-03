# 通过 restful 请求 获取token
import base64
import hashlib
import hmac
import requests
import time
import uuid
from urllib import parse
import http.client
import json
import os
from pydub import AudioSegment


class VoiceChange:
    def __init__(self):
        access_key_id = 'LTAIcvQia81jljdW'
        access_key_secret = 'FcfoU3u9PM3rkTF92Rcs7LseNR5A7Y'
        self.token, self.expire_time = VoiceChange.create_token(access_key_id, access_key_secret)

    @staticmethod
    def _encode_text(text):
        encoded_text = parse.quote_plus(text)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')

    @staticmethod
    def _encode_dict(dic):
        keys = dic.keys()
        dic_sorted = [(key, dic[key]) for key in sorted(keys)]
        encoded_text = parse.urlencode(dic_sorted)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')

    @staticmethod
    def create_token(access_key_id, access_key_secret):
        parameters = {'AccessKeyId': access_key_id,
                      'Action': 'CreateToken',
                      'Format': 'JSON',
                      'RegionId': 'cn-shanghai',
                      'SignatureMethod': 'HMAC-SHA1',
                      'SignatureNonce': str(uuid.uuid1()),
                      'SignatureVersion': '1.0',
                      'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      'Version': '2019-02-28'}
        # 构造规范化的请求字符串
        query_string = VoiceChange._encode_dict(parameters)
        #         print('规范化的请求字符串: %s' % query_string)
        # 构造待签名字符串
        string_to_sign = 'GET' + '&' + VoiceChange._encode_text('/') + '&' + VoiceChange._encode_text(query_string)
        #         print('待签名的字符串: %s' % string_to_sign)
        # 计算签名
        secreted_string = hmac.new(bytes(access_key_secret + '&', encoding='utf-8'),
                                   bytes(string_to_sign, encoding='utf-8'),
                                   hashlib.sha1).digest()
        signature = base64.b64encode(secreted_string)
        #         print('签名: %s' % signature)
        # 进行URL编码
        signature = VoiceChange._encode_text(signature)
        #         print('URL编码后的签名: %s' % signature)
        # 调用服务
        full_url = 'http://nls-meta.cn-shanghai.aliyuncs.com/?Signature=%s&%s' % (signature, query_string)
        #         print('url: %s' % full_url)
        # 提交HTTP GET请求
        response = requests.get(full_url)
        if response.ok:
            root_obj = response.json()
            key = 'Token'
            if key in root_obj:
                token = root_obj[key]['Id']
                expire_time = root_obj[key]['ExpireTime']
                return token, expire_time
        #         print(response.text)
        return None, None

    def init_request(self,appKey):
        # 服务请求地址
        url = 'http://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr'
        format = 'pcm'
        sampleRate = 16000
        enablePunctuationPrediction = True
        enableInverseTextNormalization = True
        enableVoiceDetection = False

        # 设置RESTful请求参数
        request = f"{url}?appkey={appKey}&format={format}&sample_rate={sampleRate}"

        # 是否在后处理中添加标点
        if enablePunctuationPrediction:
            request = f"{request}&enable_punctuation_prediction=true"
        # 是否在后处理中执行ITN
        if enableInverseTextNormalization:
            request = f"{request}&enable_inverse_text_normalization=true"
        # 是否启动语音检测
        if enableVoiceDetection:
            request = f"{request}&enable_voice_detection=true"
        #     print('Request: ' + request)
        return request

    def process(self,request, token, audioFile):

        # 读取音频文件
        with open(audioFile, mode='rb') as f:
            audioContent = f.read()
        # 设置HTTP请求头部
        httpHeaders = {
            'X-NLS-Token': token,
            'Content-type': 'application/octet-stream',
            'Content-Length': len(audioContent)
        }

        host = 'nls-gateway.cn-shanghai.aliyuncs.com'
        conn = http.client.HTTPConnection(host)
        conn.request(method='POST', url=request, body=audioContent, headers=httpHeaders)
        response = conn.getresponse()
        body = response.read()
        try:
            body = json.loads(body)
            status = body['status']
            if status == 20000000:
                result = body['result']
                if (len(result) > 0):
                    # 有内容
                    return (result)
                else:
                    # 空内容
                    return "_close"
            else:
                return ("_close")
        except ValueError:
            print('The response is not json format string')
        conn.close()

    # 将语音消息转化为文字输出
    def change(self, path):
        appKey = 'FCREZYfzBqwvMMnN'
        request = self.init_request(appKey)
        song = AudioSegment.from_mp3(path)
        # 转变格式并保存到本地
        song.export("tmp.wav", format="wav")
        # 使用阿里云进行语音识别
        res = self.process(request, self.token, "tmp.wav")
        os.remove('tmp.wav')
        os.remove(path)
        return res


if __name__ == "__main__":
    x=VoiceChange()
    print(x.change("test.mp3"))
