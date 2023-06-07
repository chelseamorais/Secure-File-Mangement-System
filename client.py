# launch shell, parse commands

import os
import threading
from socket import *
from Crypto.Cipher import AES

AES_KEY = b'\xa5\xf6\xc3\xa3\x08$%\x0f1\xb6\x8a\xec\x0bj\xd1\xc1'
AES_NONCE = AES_KEY

def send_command_to_server(command):
    # create the socket
    server_addr = '127.0.0.1'
    server_port = 12001
    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.connect((server_addr,server_port)) 

    server_socket.send(command.encode('utf-8'))
    # any command in the below list will get a response from server
    if (command.split('|')[0] in ["ls"]) or (command.split(' ')[0] in ["read", "cd", "delete", "mkdir", "write","rename"]):
        response = server_socket.recv(4096)
        response = response.decode('utf-8')
    else:
        response = None
    
    server_socket.close()

    return response
    
    
if __name__ == "__main__":

    a = input("Please enter your name:")
    print("Please enter your command at the prompt. \n ")
    
    if not os.path.exists("umbc"):
        os.mkdir("umbc")

    cur_dir = "umbc"
    os.chdir(cur_dir)
    
    while True:
        # valid commands are "create", "delete", "write", "read", "rename"

        # change current working directory 
        Grant_Access = ""
        command = input(f"{cur_dir}>>>  ")
        command = command+'|'+a

        if "create" in command:
            Grant_AccessW = input("Enter the users you want to grant permission to for both read and write:")
            command=command+'|'+Grant_AccessW
            Grant_AccessR = input("Enter the users you want to grant permission to for only read:")
            command = command+'|'+Grant_AccessR

        response = send_command_to_server(command)
        # check for all whitespace, return to beginning of loop
        if len(command.strip()) == 0:
            continue
        
        first_word_command = command.split()[0]
        if len(command.split()) > 1:
            filename1 = command.split()[1]

        # check write lock
        if first_word_command == "write" and os.path.exists(filename1 + ".lock"):
            print("error: file is locked")
            continue

        # create [filename]
        #response = send_command_to_server(command)
            #print(".......")
        if first_word_command == "read"and response!="Access denied" :
            if response[:5] != "ERROR":
                # decrypt the file contents client-side
                # ciphertext is in response, so decrypt and overwrite response
                cipher = AES.new(AES_KEY, AES.MODE_EAX, AES_NONCE)
                plaintext_encoded = cipher.decrypt(response.encode('ISO-8859-1'))
                response = plaintext_encoded.decode("ISO-8859-1")
            print(response)
            
        elif first_word_command == "cd":

            if response[:5] != "ERROR":
                cur_dir = response
            else:
                print(response)
        else:
            if response:
                print(response)

        if first_word_command == "write" and response!="Access denied" and response !="ERROR: {filename1} not found.":
            # check if file is locked
            text = input()
            
            # encrypt file contents client-side
            cipher = AES.new(AES_KEY, AES.MODE_EAX, nonce=AES_NONCE)
            encoded_text = text.encode("utf-8")
            ciphertext = cipher.encrypt(encoded_text)
            decoded_ciphertext = ciphertext.decode("ISO-8859-1")
            
            response = send_command_to_server(decoded_ciphertext)
            #response = send_command_to_server(text)
        
        if first_word_command == "exit":
            print("Thank you for using our file system! Goodbye.")
            break

        
    
