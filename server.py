#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        decode_message = self.data.decode("utf-8").split('\r\n')
        methods = decode_message[0].split()
        if methods[0] != "GET":
            self.handle_method_exception()
        else:
            #check whether it is a directory
            if methods[1].endswith("/"):
                dir_part = methods[1]
                # if len < 1, it means it is a root, no need to strip
                if len(dir_part) > 1:
                    #clean extra symbols in the path
                    dir_part = os.path.normpath(dir_part)
                    #because it is directory, so the last "/" is also cleaned, so need to
                    # add it back
                    dir_part+="/"
                total_url = os.path.join(os.getcwd(), "www") + dir_part
                #check whether the directory exists
                if os.path.isdir(total_url):
                    #exist, handle the directory
                    self.handle_directory(total_url)
                else:
                    #not exist, raise 404
                    self.handle_not_found()
            else:
                #strip the extra symbol in path
                file_part = os.path.normpath(methods[1])
                total_url = os.path.join(os.getcwd(), "www") + file_part
                #check whether the file exist
                if(os.path.isfile(total_url)):
                    self.handle_files(total_url)
                # if not exist, check whether it is actually an directory whithout last "/"
                elif(os.path.isdir(total_url)):
                    # if yes raise 301 error and find the correct path
                    correct_path = total_url+ "/"
                    self.handle_move_exception(correct_path)
                else:
                    #if not raise 404 error
                    self.handle_not_found()

    
    def handle_files(self, path):
        header = "HTTP/1.1 200 OK\r\n"
        header += "Content-Type: text/"
        file_type = path.split('.')[-1]
        header+= file_type+"\r\n"
        content = open(path,"r").read()
        header += "Content-length: "+ str(len(content))+ "\r\n"
        header+= "\r\n"+ content
        self.request.sendall(bytearray(header, 'utf-8'))
    
    def handle_directory(self, path):
        header = "HTTP/1.1 200 OK\r\n"
        header += "Content-Type: text/html\r\n"
        path += "index.html"
        content = open(path,"r").read()
        header += "Content-length: "+ str(len(content))+ "\r\n"
        header+= "\r\n"+ content
        self.request.sendall(bytearray(header, 'utf-8'))
    
    def handle_not_found(self):
        header = "HTTP/1.1 404 Not Found\r\n"
        header += "Content-Type: text/html\r\n"
        header += "<h1>404 Not found</h1>"
        self.request.sendall(bytearray(header, 'utf-8'))
        
    def handle_method_exception(self):
        header = "HTTP/1.1 405 Method Not Allowed\r\n"
        header += "Content-Type: text/html\r\n"
        header += "Allow: GET\r\n\r\n"+ "<h1>405 Only GET Allowed!</h1>"
        self.request.sendall(bytearray(header, 'utf-8'))
    
    def handle_move_exception(self, correct_path):
        header = "HTTP/1.1 301 Moved Permanently\r\n"
        header += "Server: local host/8080\r\n"
        header += " Location:  "+correct_path+"\r\n"
        self.request.sendall(bytearray(header, 'utf-8'))



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
