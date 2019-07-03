import os
import urllib
import itchat
from itchat.content import *
import re
from AccessToken import VoiceChange
from movie import recommend
from moviename import spider
from mydb import mysql
from rccpoem import Mypoem
import sched
import time
import json
import threading
import xiaobin
import requests
import urllib.parse
import urllib.request

# 全局变量
mypoem = Mypoem()
ispoem = False
istime = False
ismovie = False
ischat = False
ischating = False
isyanzhe = True
ismoviename = False
db = mysql()
mysprider = spider()
schedule = sched.scheduler(time.time, time.sleep)
myvoice = VoiceChange()
dictnum = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100, '千': 13,
           '万': 14, '亿': 18, '两': 2,
           '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10, '佰': 100, '1': 1, '2': 2,
           '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}


def send(id, usrname, message):
    itchat.send_msg("****定时提醒消息****：" + message, usrname)
    db.delet(id)


# def timetask(id, time, usrname, message):
#     schedule.enter(time, 0, send, (id, usrname, message))
#     schedule.run()


# 获取图灵消息。
def gettuling(msg):
    api_url = "http://openapi.tuling123.com/openapi/api/v2"
    req = {
        "perception":
            {
                "inputText":
                    {
                        "text": "%s" % msg
                    },
            },

        "userInfo":
            {
                # 换成自己的
                "apiKey": "c29d471d77d7487eb5cf45c5ce685fde",
                "userId": "hexinjiyi"
            }
    }
    req = json.dumps(req).encode('utf8')
    http_post = urllib.request.Request(api_url, data=req, headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(http_post)
    response_str = response.read().decode('utf8')
    response_dic = json.loads(response_str)
    return response_dic['results'][0]['values']['text']


def bingreplay(message):
    r = requests.get('https://www4.bing.com/socialagent/chat?q=' + message + '&anid=123456')  # 小冰接口
    r1 = r.json()
    return urllib.parse.unquote(r1['InstantMessage']['ReplyText'])


def robotChat(message, usrname):
    mytext = message
    itchat.send_msg('小冰说：%s' % mytext, usrname)
    while ischating:
        mytext = gettuling(mytext)
        itchat.send_msg('图灵机器人说：%s' % mytext, usrname)
        mytext = bingreplay(mytext)
        itchat.send_msg('小冰说：%s' % mytext, usrname)
    itchat.send_msg('---机器对话结束---', usrname)


def chatThread(message, usrname):
    threading.Thread(target=robotChat, args=(message, usrname)).start()


def process(usrname, message):
    global ispoem, text, i
    global istime, ismovie, ischat, ischating, ismoviename
    text = ''
    if ischating:
        ischating = False
    # 发送转化的藏头诗
    if ispoem:
        ispoem = False
        itchat.send_msg('正在生成请稍等大约一分钟...', usrname)
        # 判断当前末尾是否存在标点
        if message[-1] == '。' or message[-1] == '!':
            message = message[0:-1]
        itchat.send_msg(mypoem.gen_head_poetry(message, 5), usrname)
    # 将定时任务插入数据库
    elif istime:
        try:
            istime = False
            # 正则表达式提取信息
            matchObj = re.match(r'(.*)分钟后提醒我(.*)', message)
            now = int(time.time())
            mytime = int(dictnum[matchObj.group(1)]) * 60
            text = matchObj.group(2)
            db.insert(now, usrname, now + mytime, text)
            threading.Timer(mytime, send, (now, usrname, text)).start()
            # timetask(now, mytime, usrname, matchObj.group(2))
            itchat.send_msg('设定成功', usrname)
        except:
            itchat.send_msg('格式不对，生成定时任务失败', usrname)
    elif ismovie:
        ismovie = False
        # 长度小于4且全是数字
        if len(message) < 4 and message.isdigit():
            start = int(message)
            end = start + 10
            if start + 10 > 250:
                end = 250
            mytext = ""
            for row in db.selectMovie(start, end):
                mytext = mytext + '%d，%s \n' % (row[0], row[1])
            itchat.send_msg(mytext, usrname)
        # 通过电影名称找相似电影
        else:
            i = 1
            try:
                movie = mymovie.improved_recommendations(message)
                for title, score, year in zip(movie['title'], movie['vote_average'], movie['year']):
                    text = text + '%d:%s,%s分,%s年\n' % (i, title, score, year)
                    i = i + 1
                itchat.send_msg(text, usrname)
            except:
                itchat.send_msg("电影不存在", usrname)
    elif ischat:
        ischat = False
        ischating = True
        chatThread(message, usrname)
    elif ismoviename:
        ismoviename = False
        try:
            temp = mysprider.search(message)
            itchat.send_msg("电影名称为：\n%s\n豆瓣网址为：%s" % (temp[0], temp[1]), usrname)
        except:
            itchat.send_msg("电影不存在", usrname)
    # 匹配消息
    elif message == '?' or message == "帮助" or message == '？':
        itchat.send_msg('快来与我聊天吧,支持图片和语音，若使用功能则需：\n输入1：观看小冰和图灵机器人对话\n输入2：用臧头诗功能\n输入3：设置定时任务\n输入4：查询所有的定时任务\n输入5'
                        '：电影推荐\n输入6：电影详细信息',
                        usrname)
    # 机器人聊天
    elif message == '1':
        ischat = True
        itchat.send_msg('请说一句让机器人开头的话。', usrname)
    # 臧头诗
    elif message == '2':
        ispoem = True
        itchat.send_msg('请输入您要转化成藏头诗的句子', usrname)
    # 定时任务
    elif message == '3':
        istime = True
        itchat.send_msg('请输入定时任务描述，格式为:n分钟后提醒我xxxxx，比如：2分钟后提醒我演示该结束了', usrname)
    elif message == '4':
        sche = db.select(usrname)
        if len(sche) == 0:
            text = "暂时没有定时任务"
        else:
            i = 1
            for row in sche:
                text = text + '第%d条记录，提醒你：%s \n' % (i, row[3])
                i = i + 1
        itchat.send_msg(text, usrname)
    elif message == '5':
        ismovie = True
        itchat.send_msg('1.输入数字1-250则返回10条排行榜消息\n2.输入您最喜欢的电影名称则返回此电影相似的的电影', usrname)
    elif message == '6':
        ismoviename = True
        itchat.send_msg('请输入要搜索的电影名称', usrname)
    else:
        itchat.send_msg(bingreplay(message), usrname)


# 接受消息
@itchat.msg_register(itchat.content.TEXT)
def reply_msg(msg):
    process(msg['FromUserName'], msg['Text'])


# 接收语音
@itchat.msg_register(RECORDING)
def voice_receive(msg):
    # itchat.send_msg('正在解析文本请稍等', msg['FromUserName'])
    # 下载语音到本地
    msg['Text'](msg['FileName'])
    message = myvoice.change(msg['FileName'])
    itchat.send_msg('您发送的语音消息为：' + message, msg['FromUserName'])
    process(msg['FromUserName'], message)


# 接收图片
@itchat.msg_register(itchat.content.PICTURE)
def img_opera(msg):
    global isyanzhe
    # 下载图片
    msg['Text'](msg['FileName'])
    imgUrl = msg['FileName']
    if isyanzhe:
        isyanzhe = False
        mytext = xiaobin.yanzhi(imgUrl)
        itchat.send("小冰测试颜值:\n" + mytext, toUserName=msg['FromUserName'])  # 发送回复消息
    else:
        isyanzhe = True
        mytext = xiaobin.poem(imgUrl)
        itchat.send("小冰作诗:\n" + mytext, toUserName=msg['FromUserName'])  # 发送回复消息
    os.remove(msg['FileName'])


if __name__ == '__main__':
    global mymovie
    print("正在构建电影模型")
    mymovie = recommend()
    print("电影模型构建成功")
    itchat.auto_login()
    itchat.run()
