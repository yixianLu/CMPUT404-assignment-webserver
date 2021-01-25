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

        # extract information
        method = self.data[0].split()[0]
        path = self.data[0].split()[1]
        target_path = os.path.abspath(os.getcwd()) + '/www'

        # get the server address
        address = self.server.server_address
        host = "http://" + address[0]+":"+str(address[1])

        if method != "GET":
            # invalid method
            self.method_not_allowed()
        elif os.path.isdir(target_path+os.path.abspath(path)):
            target_path += path
            # location moved
            if target_path[-1] != "/":
                self.location_moved(host+path+"/")
            else:
                is_dir = True
                self.process_file(target_path, is_dir)
        elif os.path.isfile(target_path+os.path.abspath(path)):
            # the path is a file
            self.process_file(target_path+path)
        else:
            # invalid path
            self.invalid_path()

    # compose and send response
    def send_response(self, status, header, content):
        response = "HTTP/1.1 {}\r\n{}\r\n".format(status, header)
        response += content
        self.request.sendall(bytearray(response,'utf-8'))

    # handles invalid method
    def method_not_allowed(self):
        status = "405 Method Not Allowed"
        header = ""
        content = ""
        self.send_response(status, header, content)

    # handles incorrect path
    def location_moved(self, address):
        status = "301 Moved Permanently"
        header = "Content-Type: text/html \r\nLocation: " + address + "\r\n"
        content = """
                <html>
                <body>
                <h1> 301 Moved Permanently </h1>
                </body>
                </html>"""
        self.send_response(status, header, content)

    # handles invalid path
    def invalid_path(self):
        status = "404 Not Found"
        header = "Content-Type: text/html\r\n"
        content = """
                <html>
                <body>
                <h1> 404 Not Found </h1>
                </body>
                </html>"""
        self.send_response(status, header, content)

    # read from file
    def process_file(self, target_path, is_dir=False):
        status = "200 OK"
        if is_dir:
            header = "Content-Type: text/html\r\n"
            content = open(target_path+"index.html").read()
            self.send_response(status, header, content)
        else:
            # get the extension of the file
            ext = target_path.split(".")[-1]
            if (ext == "css" or ext == "html"):
                header = "Content-Type: text/" + ext + "\r\n"
                content = open(target_path).read()
                self.send_response(status, header, content)
            else:
                # mime type not supported
                self.invalid_path()


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()