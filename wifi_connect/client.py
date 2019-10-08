import socket

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  #等同于服务端

server_address = '127.0.0.1'

s.connect(('127.0.0.1',8080))     #拨通电话 注意此处是一个元组的形式

s.send('hello'.encode('utf-8'))  #转为二进制发出去
print('ready to recv message')

back_msg=s.recv(1024)        #接收消息
print(back_msg)

s.close()