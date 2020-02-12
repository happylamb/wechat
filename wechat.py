from threading import Thread
import itchat
from itchat.content import *
import redis
import json
import re
import time
import requests
import base64
from redisUtis import r

firends=[]
EXPIRE_TIME=300


'''
监听撤回消息
'''
@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True)
def handleNoteMsg(msg):
    try:
        # print(msg)
        if '撤回了一条消息' in msg.Text:
            recall_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
            oldMsgStr = r.get('wxmsg:' + str(recall_msg_id))
            if oldMsgStr:
                oldMsg = json.loads(oldMsgStr)
                fromUser = oldMsg['fromUser']
                if oldMsg['isGroup']:
                    fromUser = oldMsg['groupName'] + '=>' + fromUser
                m = fromUser + '\n' + str(oldMsg['time'])+'\n撤回了'
                if oldMsg['msgType'] == 'file':
                    itchat.send_msg(m +'文件消息\n', 'filehelper')
                    itchat.send(oldMsg['content'], 'filehelper')
                elif oldMsg['msgType'] == 'Text':
                    itchat.send_msg( m + '文本消息\n' + oldMsg['content'], 'filehelper')

    except:
        print('error4')


'''
监听文件助手消息
'''
@itchat.msg_register([TEXT], isFriendChat=True)
def handleTextMsg(msg):
    try:
        msg_time_receive = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        user = msg.User
        if (user.UserName == 'filehelper'):
            handleMyMsg(msg)
        else:
            curMsg = {
                'msgId': msg.MsgId,
                'msgType': 'Text',
                'content': msg['Text'],
                'time': msg_time_receive,
                'fromUser': msg['User']['NickName'],
                'isGroup': False
            }
            r.set('wxmsg:' + str(msg.MsgId), json.dumps(curMsg))
            r.expire('wxmsg:' + str(msg.MsgId), EXPIRE_TIME)
        if (msg['Text'] == '毒鸡汤'):
            ms = getDailyWord()
            itchat.send_msg(msg['User']['NickName'] + ":\n" + ms, msg['FromUserName'])
    except:
        print('error3')

@itchat.msg_register([TEXT], isGroupChat=True)
def handleGroupTextMsg(msg):
    try:
        msg_time_receive = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        user = msg.User
        if (user.UserName == 'filehelper'):
            handleMyMsg(msg)
        else:
            groupName = None
            try:
                groupName = msg['User']['NickName']
            except:
                groupName = None
            if groupName is None:
                groupName = '群：'
            else:
                groupName = '群：' + groupName
            curMsg = {
                'msgId': msg.MsgId,
                'msgType': 'Text',
                'content': msg['Text'],
                'groupContent': msg['Content'],
                'time': msg_time_receive,
                'fromUser': msg['ActualNickName'],
                'groupName': groupName,
                'isGroup': True
            }
            r.set('wxmsg:' + str(msg.MsgId), json.dumps(curMsg))
            r.expire('wxmsg:' + str(msg.MsgId), EXPIRE_TIME)
    except:
        print('error2')

'''
处理文件助手消息
'''
def handleMyMsg(msg):
    try:
        print("文件助手：")
        print(msg.Text)
    except:
        print('error1')

'''
监听附件、图片音频等消息
'''
@itchat.msg_register([PICTURE, ATTACHMENT, VIDEO, VOICE], isFriendChat=True)
def handleImgMsg(msg):
    try:
        msg_time_receive = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        user = msg.User
        msg.download(msg.fileName)
        curMsg = {
            'msgId': msg.MsgId,
            'msgType': 'file',
            'content': '@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', msg['FileName']),
            'time': msg_time_receive,
            'fromUser': msg['User']['NickName'],
            'isGroup': False
        }
        r.set('wxmsg:' + str(msg.MsgId), json.dumps(curMsg))
        r.expire('wxmsg:' + str(msg.MsgId), EXPIRE_TIME)
    except:
        print('error0')



'''
监听附件、图片音频等消息
'''
@itchat.msg_register([PICTURE, ATTACHMENT, VIDEO, VOICE], isGroupChat=True)
def handleGroupImgMsg(msg):
    msg_time_receive = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    user = msg.User
    msg.download(msg.fileName)
    groupName = msg['User']['NickName']
    if groupName is None:
        groupName = '群：'
    else:
        groupName = '群：' + groupName
    curMsg = {
        'msgId': msg.MsgId,
        'msgType':'file',
        'content':'@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil',msg['FileName']),
        'time': msg_time_receive,
        'fromUser': msg['ActualNickName'],
        'groupName': groupName,
        'isGroup':True
    }
    r.set('wxmsg:' + str(msg.MsgId), json.dumps(curMsg))
    r.expire('wxmsg:' + str(msg.MsgId), EXPIRE_TIME)

def getDailyWord():
    result = '小羊在睡觉'
    try:
        result = requests.get("https://api.uixsj.cn/hitokoto/en.php").text
    except:
        result = result
    return result



