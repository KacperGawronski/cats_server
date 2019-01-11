#!/home/administrator/cats_server/pserver/bin/python3
'''
This file is part of cats_server.

cats_server is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cats_server is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cats_server.  If not, see <https://www.gnu.org/licenses/>.
'''
import threading
import io
from skimage import transform, color
from skimage.data import imread
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import socket
import numpy as np
img_x =  240
img_y =  180
n_connections=10
class HandlingConnectionThread(threading.Thread):
    def __init__(self,socket_obj,model):
        threading.Thread.__init__(self)
        self.__socket=socket_obj
        self.__model=model
    def run(self):
        self.__receiveImage()
        self.__checkImage()
        self.__sendResponse()
    def __receiveImage(self):
        self.__image=io.BytesIO()
        tmp_recv=self.__socket.recv(1024)
        while(tmp_recv):
            self.__image.write(tmp_recv)
            tmp_recv=self.__socket.recv(1024)
    def __checkImage(self):
        self.__result=self.__model.predict_proba([np.array(color.rgb2gray(transform.resize(imread(self.__image),(img_x,img_y)))).reshape(img_x*img_y)])
    def __sendResponse(self):
        print(self.__result)
        print("{:.2%}".format(self.__result[0][0]))
        if self.__result[0][0]>0.6:
            '''
            self.__socket.sendall("To jest kot".encode('ascii'))
        else:
            self.__socket.sendall("To nie jest kot".encode('ascii'))
            '''
            self.__socket.sendall("To jest kot na {:.2%}".format(self.__result[0][0]).encode('ascii'))
        else:
            self.__socket.sendall("To nie jest kot na {:.2%}".format((self.__result[0][1])).encode('ascii'))
            
        self.__socket.close() 
class Server:
    def __init__(self):
        self.__port=9500
        self.__address=''
        self.__model=joblib.load('cats.pkl')
        self.__threads=[]
        self.__socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.__socket.bind((self.__address,self.__port))
    def run(self):
        self.__socket.listen(n_connections)
        while(True):
            conn,addr=self.__socket.accept()
            tmp_thread=HandlingConnectionThread(conn,self.__model)
            tmp_thread.start()
    def __del__(self):
        self.__socket.close()

server=Server()
server.run()
