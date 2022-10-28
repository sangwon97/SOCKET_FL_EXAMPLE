import socket
import pickle
import time
import uuid
import datetime
import matplotlib.pyplot as plt
from _thread import *
from train_module import *

# Variable Set
HOST = '168.131.154.188'
PORT = 8080

current_round = 1

# client socket create
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_dataset = torch.load('./data_tensor/client_dataset_01')
client = Client('client_01', client_dataset)  

def encodeParams(parameter) :
    return pickle.dumps(parameter)

def decodeParamse(parameter) :
    return pickle.loads(parameter)

def roundLearning(data) :
    global current_round

    # global_params = pickle.loads(data)
    msg = str(uuid.uuid4())

    print("[{}] << Recive init parameters : {}".format(datetime.datetime.now(), data.decode()))
    print("[{}] || Round {} train start".format(datetime.datetime.now(), current_round))

    time.sleep(1)

    print("[{}] || Train done ".format(datetime.datetime.now()))
    client_socket.send(msg.encode())
    print("[{}] >> Send trained parameters : {}".format(datetime.datetime.now(), msg))
    current_round += 1

while True:
    data = client_socket.recv(4024)

    if(data):
        roundLearning(data)

    if(current_round > 3):
        print(">> 최종 라운드 학습 완료, 탈출하겠습니다.")
        break

client_socket.close()

'''
# FIXME : Make loop depends on round.
# TODO : socket) global_parameters recv() from GLOBAL.
recv_data = client_socket.recv(1024)
curr_parameters = json.loads(recv_data.decode())
new_parameters = dict([(layer_name, {'weight': 0, 'bias': 0}) for layer_name in curr_parameters])

client_parameters = client.train(curr_parameters)
fraction = client.get_dataset_size() / total_train_size
for layer_name in client_parameters:
    new_parameters[layer_name]['weight'] += fraction * client_parameters[layer_name]['weight']
    new_parameters[layer_name]['bias'] += fraction * client_parameters[layer_name]['bias']

send_parameters = json.dumps(new_parameters)
client_socket.send(send_parameters.encode())
# TODO : socket) new_parameters send() to GLOBAL.

'''