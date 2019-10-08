#!/usr/bin/env Python3
#导入socket sys模块
import socket
import sys
 
#创建socket对象
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
 
#获取本地主机名
host = socket.gethostname()
 
port = 9999
 
#绑定端口
serversocket.bind(('', port))

#设置最大连接数，超过后排队
serversocket.listen(5)

print("server started!")
 
while True:
    #建立客户端连接
    clientsocket, addr = serversocket.accept()
 
    print("连接地址：%s" %str(addr))
 
    msg = 'wlecome' + "\r\n"
 
    clientsocket.send(msg.encode('utf-8'))
    
    client_msg = clientsocket.recv(1024)
    print("client msg: "+ client_msg.decode('utf-8'))
    
    #clientsocket.close()
    


serversocket.close()