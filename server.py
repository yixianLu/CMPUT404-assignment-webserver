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
        self.data = self.data.decode().splitlines()
        method_path = self.data[0].split()
        method = method_path[0]
        path = method_path[1]

        half_path = os.path.abspath(os.getcwd()) + '/www'
        temp = half_path+ os.path.abspath(path)
        if method != "GET":
            self.handle_method_exception()       
        elif os.path.isdir(half_path+ os.path.abspath(path)):
            total_path = half_path+path
            if total_path[-1] != "/":
                self.handle_move_exception(total_path+"/")
            else:
                self.handle_directory(total_path)
        elif os.path.isfile(half_path+ os.path.abspath(path)):
            total_path = half_path+path
            self.handle_files(total_path)

        else:
            self.handle_not_found()
    
    def handle_files(self, path):
        status = "200 OK"
        header = "Content-Type: text/"
        file_type = path.split('.')[-1]
        header+= file_type
        content = open(path,"r").read()
        self.respond_request(status, header, content)
    
    def handle_directory(self, path):
        status = "200 OK"
        header= "Content-Type: text/html"
        path += "index.html"
        content = open(path,"r").read()
        self.respond_request(status, header, content)
    
    def handle_not_found(self):
        status = "404 NOT FOUND"
        self.respond_request(status,"","")
        
    def handle_method_exception(self):
        status = "405 METHOD NOT ALLOWED"
        self.respond_request(status, '','')
    
    def handle_move_exception(self, correct_path):
        status = "301 MOVED PERMANENTLY"
        self.respond_request(status, correct_path,'')

    def respond_request(self, status, header, content):
        #print ("Got a request of: %s\n" % self.data)
        response = "HTTP/1.1 {}\r\n{}\r\n".format(status, header)
        response += content
        self.request.sendall(bytearray(response,'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
