import redis


#用redis保存消息
#redis服务器IP
IP = 'xx.xx.xx.xx'
# 端口
PORT = 6379
# 密码
PASSWORD = 'password'

r = redis.Redis(host=IP, port=6379, password=PASSWORD)

