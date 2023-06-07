# launch shell, parse commands

import os
import threading
from socket import *
from filelock import FileLock
from Crypto.Cipher import AES
from filename_mapping import *
import json
import datetime

AES_KEY = b'\xc1\xce\x9d\x7f\xbfy\n\xa0\x1f\xe4]\x9b\x0c\xe8D\x04'
AES_NONCE = AES_KEY

def send_response_to_client(data, server_socket):
    server_socket.send(data.encode('utf-8'))

def create(plaintext_filename,Grant_AccessW,Grant_AccessR,user,current_dir):
    filename = filename_mapping(plaintext_filename)
    file_dictionaryW[filename] = Grant_AccessW,user
    file_dictionaryR[filename] = Grant_AccessR
    with open(writeperm_encrypted, 'w') as convert_file:
        convert_file.write(json.dumps(file_dictionaryW))
    with open(readperm_encrypted, 'w') as convert_file:
        convert_file.write(json.dumps(file_dictionaryR))
    with open(filename, "w"):
        logging("CREATE", "File created with name: " + plaintext_filename, user,current_dir)
        pass

def delete(plaintext_filename,current_dir,user):
    filename = filename_mapping(plaintext_filename)
    if os.path.exists(filename):
        if(user in file_dictionaryW[filename]):
            os.remove(filename)
            
            del file_dictionaryR[filename]
            with open(readperm_encrypted, 'w') as convert_file:
                convert_file.write(json.dumps(file_dictionaryR))
                
            del file_dictionaryW[filename]
            with open(writeperm_encrypted, 'w') as convert_file:
                convert_file.write(json.dumps(file_dictionaryW))
                
            logging("DELETE", "File deleted with name: " + plaintext_filename, user,current_dir)
            response = f"{plaintext_filename} successfully deleted."
        else:
            logging("DELETE", "Access Denied :File not deleted with name: " + plaintext_filename, user,current_dir)
            response = f"Access Denied"
    else:
        logging("DELETE", "ERROR: No File Exists with name: " + plaintext_filename, user,current_dir)
        response = f"ERROR: {plaintext_filename} does not exist."
    return response

#def write(plaintext_filename, text):
#    filename = filename_mapping(plaintext_filename)
#    with FileLock(filename):
#        with open(filename, "wb") as f:
#            f.write(text.encode('utf-8'))
            
def write(plaintext_filename,text,user,current_dir):
    filename = filename_mapping(plaintext_filename)
    
    with FileLock(filename):
        if user in file_dictionaryW[filename]:
            with open(filename, "wb") as f:
                # send response to ask for input
                logging("WRITE", "File written with name: " + plaintext_filename, user,current_dir)
                f.write(text.encode('utf-8'))
        else:
            text = "Access denied"
            logging("WRITE", "ACCESS DENIED to write to file with name: " + plaintext_filename, user,current_dir)
            print(text)
            #send_response_to_client(text, conn)
        
    #return text.decode('utf-8')


#def read(plaintext_filename):
#    filename = filename_mapping(plaintext_filename)
#    if os.path.exists(filename):
#        with open(filename, "rb") as f:
#            response = f.read()
#    else:
#        response = f"ERROR: {filename1} not found."
#    if type(response) == str:
#        return response
#    else:
#        return response.decode('utf-8')
def read(plaintext_filename,user,current_dir):
    filename = filename_mapping(plaintext_filename)
    if os.path.exists(filename):
        if (user in file_dictionaryR[filename]) or (user in file_dictionaryW[filename]):
            with open(filename, "rb") as f:
                response = f.read()
                logging("READ", "File read with name: " + plaintext_filename, user,current_dir)
            if not response:
                response = f"Empty file"
        else:
            logging("READ", "ACCESS DENIED to read the file with name: " + plaintext_filename, user,current_dir)
            response = f"Access denied rep"
    else:
        logging("READ", "ERROR: File not found with name: " + plaintext_filename, user,current_dir)
        response = f"ERROR: {filename1} not found."

    if type(response) == str:
        return response
    else:
        return response.decode('utf-8')

def rename(plaintext_filename1, plaintext_filename2,current_dir,user):
    filename1 = filename_mapping(plaintext_filename1)
    filename2 = filename_mapping(plaintext_filename2)
    if user in file_dictionaryW[filename1]:
        file_dictionaryW[filename2] = file_dictionaryW[filename1]
        if filename1 in file_dictionaryR:
            file_dictionaryR[filename2] = file_dictionaryR[filename1]
            del file_dictionaryR[filename1]
            with open(readperm_encrypted, 'w') as convert_file:
                convert_file.write(json.dumps(file_dictionaryR))
        del file_dictionaryW[filename1]
        print(file_dictionaryW)
        os.rename(filename1, filename2)
        response = "File renamed successfully"
        with open(writeperm_encrypted, 'w') as convert_file:
            convert_file.write(json.dumps(file_dictionaryW))
    else:
        response = "Access denied"
    
    return response

def mkdir(plaintext_filename,current_dir):
    filename = filename_mapping(plaintext_filename)
    
    if not os.path.exists(filename):
        os.mkdir(filename)
        logging("MKDIR", "Directory created with name: " + plaintext_filename, user,current_dir)
        response = "directory successfully created."
    else:
        logging("MKDIR", "ERROR: Directory already exists with name: " + plaintext_filename, user,current_dir)
        response = "directory already exists."
    return response

def cd(plaintext_filename,current_dir):
    filename = filename_mapping(plaintext_filename)
    if plaintext_filename == "..":
        filename = ".."
    
    if os.path.exists(filename):
        os.chdir(filename)
        logging("CD", "Current working Direcotry changed to: " + os.getcwd(), user,current_dir)
        rest1 = os.getcwd().split('replica1')[1]
        rest2 = ""
        for i,s in enumerate(rest1.split("\\")):
            if i == 0:
                continue # skip empty string
            rest2 += "\\" + filename_unmapping(s)
        
        response = '\\replica1' + rest2
    else:
        logging("CD", "ERROR: directory does not exist with name: " + plaintext_filename, user,current_dir)
        response = "ERROR: directory does not exist."
    
    return response

def ls(plaintext_filename,current_dir):
    filename = filename_mapping(plaintext_filename)
    if plaintext_filename == ".":
        filename = plaintext_filename
    
    files = [f for f in os.listdir(filename) if os.path.isfile(f) or os.path.isdir(f)]
    data = ""
    for f in files:
        if f == "server_logs":
            pass
        else:
            data += filename_unmapping(f) + "\n"
    logging("LS", "Read the list of all the files in current directory: " + os.getcwd(), user,current_dir)    
    return data

def logging(command_name, message, user_name,current_dir):
    ct = str(datetime.datetime.now())
    with open( current_dir + "/server_logs", "a") as f:
        f.write(ct + " | " + "Command : "+ command_name + " | "  + message + "| Username: " + user_name + "\n")

    
if __name__ == "__main__":

    os.chdir('replica1')

    current_dir = os.getcwd()

    server_addr = '127.0.0.1'
    server_port = 12002
    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.bind((server_addr, server_port))
    server_socket.listen(10)
    writeperm_encrypted=filename_mapping("WritePermissions.txt")
    with open(writeperm_encrypted,'a+') as f:
        data = f.read()
        print(data)
        if data :
          file_dictionaryW=json.loads(data)
        else:
          file_dictionaryW = {}
          
#file_dictionaryW=json.loads(data)
    readperm_encrypted=filename_mapping("ReadPermissions.txt")

    with open(readperm_encrypted,'a+') as f:
    #with open('ReadPermissions.txt') as f:
        data1 = f.read()
        print(data1)
        if data1 :
          file_dictionaryR=json.loads(data1)
        else:
          file_dictionaryR = {}
    
    while True:
        # valid commands are "create", "delete", "write", "read", "rename"

        print("waiting for command...")
        conn, addr = server_socket.accept()
        command = conn.recv(4096)
        command = command.decode('utf-8')
        print("RECEIVED: ", command)
        #print(command)
        if 'create' in command:
            command,user,Grant_AccessW, Grant_AccessR=command.split('|')
         #   print(command)
         #   print(user)
         #   print(Grant_AccessW)
         #   print(Grant_AccessR)
        elif 'write' in command:
            command,user,text=command.split('|')
        else:
            command,user= command.split('|')

          

        # check for all whitespace, return to beginning of loop
        if len(command.strip()) == 0:
            continue
        
        first_word_command = command.split()[0]
        if len(command.split()) > 1:
            filename1 = command.split()[1]

        # create [filename]
        if first_word_command == "create":
            #thread = threading.Thread(target=create, args=(filename1,))
            #thread.start()
            create(filename1,Grant_AccessW,Grant_AccessR,user,current_dir)

        if first_word_command == "delete":
            #thread = threading.Thread(target=delete, args=(filename1,))
            #thread.start()
            data = delete(filename1,current_dir,user)
            send_response_to_client(data, conn)

        if first_word_command == "write":
            # write test "example text"
            #text = user.split('"')[1]
            #thread = threading.Thread(target=write, args=(filename1,text))
            #thread.start()
            write(filename1,text,user,current_dir)

        if first_word_command == "read":
            #thread = threading.Thread(target=read, args=(filename1,))
            #thread.start()
            data = read(filename1,user,current_dir)
            send_response_to_client(data, conn)

        if first_word_command == "rename":
            filename2 = command.split()[2]
            #thread = threading.Thread(target=rename, args=(filename1,filename2))
            #thread.start()
            rename(filename1, filename2,current_dir,user)

        if first_word_command == "mkdir":
            #thread = threading.Thread(target=mkdir, args=(filename1,))
            #thread.start()
            data = mkdir(filename1,current_dir)
            send_response_to_client(data, conn)
            
        if first_word_command == "cd":
            #thread = threading.Thread(target=cd, args=(filename1,))
            #thread.start()
            data = cd(filename1,current_dir)
            send_response_to_client(data, conn)

        if first_word_command == "ls":
            if len(command.split()) == 1:
                dirname = '.'
            else:
                dirname = filename1
                
            #thread = threading.Thread(target=ls, args=(dirname,))
            #thread.start()
            data = ls(dirname,current_dir)
            if data == "":
                data = "No files in the current directory."
            send_response_to_client(data, conn)
            

        
    
