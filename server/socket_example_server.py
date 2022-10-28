import socket
import pickle
import time
import uuid
import datetime
from _thread import *
from train_module import *

# Variable Set
client_sockets = []
max_client = 2
client_count = 0
current_round = 1
learn_flag = False

HOST = '168.131.154.188'
PORT = 8080


# server socket create
print(">> Server Start ")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

global_net = to_device(FederatedNet(), device)
history = []
# init_parameter = pickle.dumps(global_net.get_parameters())
init_parameter = str(uuid.uuid4())

# FIXME : Make loop depends on round.
# NOTE : Check the method using thread operate sync or async.
# TODO : Import train_module, Add socket funcs, Concat with client. 

def encodeParams(parameter) :
    return pickle.dumps(parameter)

def decodeParamse(parameter) :
    return pickle.loads(parameter)

def threaded(client_socket, addr) :
    global client_count
    global learn_flag
    global init_parameter
    current_parameter = init_parameter

    print("[{}] || Connected by : <{}|{}>".format(datetime.datetime.now(), addr[0], addr[1]))

    client_socket.send(current_parameter.encode())
    print("[{}] >> Send Init parameters to <{}|{}> : {}".format(datetime.datetime.now(), addr[0],  addr[1], current_parameter))

    while True:
        try:   
            if not learn_flag :
                data = client_socket.recv(524288)

                if data:            
                    print("[{}] << Recive local parameters from <{}|{}> : {}".format(datetime.datetime.now(), addr[0],  addr[1], data.decode()))       
                    client_count += 1

        except ConnectionResetError as e:
            print("[{}] | Disconnected by : <{}|{}>".format(datetime.datetime.now(), addr[0], addr[1]))
            break

    print(">>>>>> Thread 종료!")
    client_socket.close()

def globalLearning() :
    global client_count
    global max_client
    global current_round
    global learn_flag
    global client_sockets

    while True:
        if(client_count >= max_client) :                       
            learn_flag = True
            print("[{}] || Round {} : Local parameters all selected".format(datetime.datetime.now(), current_round))
            time.sleep(2)
            print("[{}] || Global train done.".format(datetime.datetime.now()))
            current_parameter = str(uuid.uuid4()).encode()

            client_count = 0
            current_round += 1
            learn_flag = False

            for client in client_sockets :
                client.send(current_parameter)

        if (current_round > 3) :
            print(">> 최종 라운드 학습 완료, 탈출하겠습니다.")
            break
    
    print(">>>>>> Thread 종료!")

# Wait for connect all clients
try:
    
    start_new_thread(globalLearning,())
    while (client_count < max_client):
        print('>> Wait')

        client_socket, addr = server_socket.accept()
        client_sockets.append(client_socket)
        start_new_thread(threaded, (client_socket, addr))
        
except Exception as e :
    print ('[chobisang] ERROR : ',e)

finally:

    server_socket.close()
