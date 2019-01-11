#!/home/administrator/cats_server/pserver/bin/python3
import threading
import io
from skimage import transform, color
from skimage.data import imread
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import socket
img_x =  240
img_y =  180
n_connections=10
class HandlingConnectionThread(threading.Thread):
    def __init__(self,socket_obj,model):
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
            self.image.write(tmp_recv)
            tmp_recv=self.__socket.recv(1024)
    def __checkImage(self):
        self.__result=self.model.predict_proba([np.array(color.rgb2gray(transform.resize(imread(self.__image),(img_x,img_y)))).reshape(img_x*img_y)])
    def __sendResponse(self):
        if self.__result[0]>0.5:
            self.__socket.sendall("To jest kot na {}%".format(self.__result[0]*100))
        else:
            self.__socket.sendall("To nie jest kot na {}%".format((1-self.__result[0])*100))

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
