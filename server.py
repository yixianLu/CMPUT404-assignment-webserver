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
            #print(methods)
            #print("after handling")
            if methods[1].endswith("/"):
                dir_part = methods[1]
                total_url = os.path.join(os.getcwd(), "www") + dir_part
                self.handle_directory(total_url)
            else:
                #print("file here!!!!")
                file_part = os.path.normpath(methods[1])
                #print(file_part)
                total_url = os.path.join(os.getcwd(), "www") + file_part
                if(os.path.isfile(total_url)):
                    self.handle_files(total_url)
                elif(os.path.isdir(total_url)):
                    correct_path = total_url+ "/"
                    self.handle_move_exception(correct_path)
                else:
                    self.handle_not_found()

    
    def handle_files(self, path):
        status = "200 OK"
        header = "Content-Type: text/"
        file_type = path.split('.')[-1]
        header+= file_type+"\r\n"
        content = open(path,"r").read()
        self.respond_request(status, header, content)
    
    def handle_directory(self, path):
        status = "200 OK"
        header= "Content-Type: text/html\r\n"
        path += "index.html"
        content = open(path,"r").read()
        self.respond_request(status, header, content)
    
    def handle_not_found(self):
        status = "404 Not Found"
        content = '''
        <!DOCTYPE html>
        <html lang="en">
        <meta charset="UTF-8">
        <h1>405 NOT FOUND</h1>
        <body>

        </body>
        </html>
        '''
        self.respond_request(status,"",content)
        
    def handle_method_exception(self):
        status = "405 Method Not Allowed"
        content = '''
        <!DOCTYPE html>
        <html lang="en">
        <meta charset="UTF-8">
        <h1>405 Method not allowed</h1>
        <body>

        </body>
        </html>
        '''
        self.respond_request(status, '',content)
    
    def handle_move_exception(self, correct_path):
        status = "301 MOVED PERMANENTLY"
        header = " Location:  "+correct_path
        content = '''
        <!DOCTYPE html>
        <html lang="en">
        <meta charset="UTF-8">
        <h1>301 MOVED PERMANENTLY</h1>
        <body>

        </body>
        </html>
        '''
        self.respond_request(status, header,content)

    def respond_request(self, status, header, content):
        # print("Got a request of: %s\n" % self.data)
        response = "HTTP/1.1 {}\r\n{}\r\n".format(status, header)
        response += content
        self.request.sendall(bytearray(response, 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
