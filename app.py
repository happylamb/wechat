from flask import Flask
from wechat import itchat
from threading import Thread
from flask import jsonify
import base64

app = Flask(__name__)

thread = Thread()

@app.route('/wxlogin')
def wxlogin():
    global thread
    uuid = itchat.get_QRuuid()
    itchat.get_QR(uuid=uuid, qrCallback=QR_to_b64)
    print(thread.is_alive())
    if thread.is_alive():
        return jsonify({'success': 0, 'msg': '已有登陆线程存在'})

    # thread = task(monitor_login,itchat)
    thread = Thread(target=monitor_login, args=(itchat,))
    thread.start()
    #浏览器显示二维码，扫码登陆
    return '<img src="data:image/png;base64,' + qr_b64.decode("utf-8") + '">'

qr_b64 = ""
def QR_to_b64(uuid, status, qrcode):
  global qr_b64
  qr_b64 = base64.b64encode(qrcode)
  return qr_b64


def monitor_login(itchat):
    isLoggedIn = False
    while 1:
        waiting_time = 0
        while not isLoggedIn:
            status = itchat.check_login()
            waiting_time += 1
            print(waiting_time)
            if status == '200':
                print ("status is 200!")
                isLoggedIn = True
            elif status == '201':
                print ("status is 201!")
                if isLoggedIn is not None:
                    print ('Please press confirm on your phone.')
                    isLoggedIn = None
            elif status != '408':
                break
            elif waiting_time == 5:
                print(5)
        if isLoggedIn:
            print ("已经确认登陆了")
            break

    print ("==== here status is ", status)
    itchat.check_login()
    itchat.web_init()
    itchat.show_mobile_login()
    itchat.get_contact(True)
    # you can do your business here
    itchat.start_receiving()
    itchat.run()


if __name__ == '__main__':
    app.run()


