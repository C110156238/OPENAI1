from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import * 

#======呼叫檔案內容=====
from mongodb_function import *
#======python的函數庫==========
import  os,json,requests #======python的函數庫==========

from flask import Flask, request

# 載入 LINE Message API 相關函式庫


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi('ix+FBt4qAcThr9OfcHGJndzIg3JrwWF1IpNrcFs/lTt+wq97kUuCe+RcG8sfkizlfrgaUORkIq7OGBZJ5GiMXQZv2TA8y12UmfTkWapMplA0IYL5tVS5owaruUANUufeRAQlt2zjLmrTcp2gjK/2ugdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('85919715906634b7a5064bc0c3b9b8f5')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    write_one_data(eval(body.replace('false','False')))#寫入資料庫
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

headers = {'Authorization':'ix+FBt4qAcThr9OfcHGJndzIg3JrwWF1IpNrcFs/lTt+wq97kUuCe+RcG8sfkizlfrgaUORkIq7OGBZJ5GiMXQZv2TA8y12UmfTkWapMplA0IYL5tVS5owaruUANUufeRAQlt2zjLmrTcp2gjK/2ugdB04t89/1O/w1cDnyilFU='}

req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/你的圖文選單 ID', headers=headers)

print(req.text)

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    #======MongoDB======

    if '@u' in msg:
        params = (msg.split(' '))
        if len(params) != 3:
            text = '請輸入格式 "@u <id> <修改的文字內容>"\n'
            
            all_messages = read_all_message()
            for message in all_messages:
                _id = message['_id']
                message_content = message['events'][0]['message']['text']
                text += f'id:{_id} 原始訊息:{message_content}\n'
            message = TextSendMessage(text=text)
            return line_bot_api.reply_message(event.reply_token, message)
        _id = params[1]
        new_message = params[2]
        data = get_message(_id)
        if data == None:
            text = '此 ID 不存在，修改失敗'
        else:
            data['events'][0]['message']['text'] = new_message
            print(data)
            update_message(_id, data)
            text = '修改成功'
        message = TextSendMessage(text=text)
        return line_bot_api.reply_message(event.reply_token, message)

    elif '@rec' in msg:
        datas = read_chat_records()
        print(type(datas))
        n = 0
        text_list = []
        for data in datas:
            if '@' in data:
                text_list.append(data)
            else:
                text_list.append(data)
            n+=1
        text_list.append(f'一共{n}則訊息')
        data_text = '\n'.join(text_list)
        message = TextSendMessage(text=data_text[:5000])
        line_bot_api.reply_message(event.reply_token, message)

    elif '@r' in msg:
        datas = read_many_datas()
        datas_len = len(datas)
        message = TextSendMessage(text=f'資料數量，一共{datas_len}條')
        line_bot_api.reply_message(event.reply_token, message)

    elif '@c' in msg:
        datas = col_find('events')
        message = TextSendMessage(text=str(datas))
        line_bot_api.reply_message(event.reply_token, message)

    elif '@d' in msg:
        text = delete_all_data()
        message = TextSendMessage(text=text)
        line_bot_api.reply_message(event.reply_token, message)

    else:
        message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
