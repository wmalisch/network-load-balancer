import socket
import os
from datetime import datetime
import time
import sys
import argparse
from signal import signal, SIGINT
from urllib.parse import urlparse

BUFFER_SIZE = 1024
PORT = 5040
# Test file that has been placed in all servers
TEST_FILE = "test.jpg"

# Function to set up ctrl C signal handler for closing the server properly
def signal_handler(sig, frame):
    print("\nInterrupt received, shutting down ...")
    sys.exit(0)

# Function that prepares a simple HTTP GET message
def prepare_get_message(host, port, file_name):
    request = f'GET {file_name} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n' 
    return request

# Function for reading the a response received from a socket
def get_line_from_socket(sock):
    done = False
    line = ''
    while (not done):
        char = sock.recv(1).decode()
        if (char == '\r'):
            pass
        elif (char == '\n'):
            done = True
        else:
            line = line + char
    return line

# Function used to retrieve an error file from an HTTP response, after the headers have been read
def print_file_from_socket(sock, bytes_to_read):
    bytes_read = 0
    while (bytes_read < bytes_to_read):
        chunk = sock.recv(BUFFER_SIZE)
        bytes_read += len(chunk)
        print(chunk.decode())

# Function used to retrieve a file or any body data from an HTTP response, after the headers have been read
def save_file_from_socket(sock, bytes_to_read, file_name):
    with open(file_name, 'wb') as file_to_write:
        bytes_read = 0
        while (bytes_read < bytes_to_read):
            chunk = sock.recv(BUFFER_SIZE)
            bytes_read += len(chunk)
            file_to_write.write(chunk)

# Function that creates a list to represent the ratio of server instance to server instance, so that we can effectively distribute the load across servers
def create_balancer_list(server_dict):
    balancer_list = []
    index = len(server_dict)
    for key in list(server_dict):
        counter = 0
        while(counter < index):
            balancer_list.append(key)
            counter+=1
        index-=1
    return balancer_list

# Function create an HTTP response
def prepare_response_message(value):
    date = datetime.datetime.now()
    date_string = 'Date: ' + date.strftime('%a, %d %b %Y %H:%M:%S EDT')
    message = 'HTTP/1.1 '
    if value == '200':
        message = message + value + ' OK\r\n' + date_string + '\r\n'
    elif value == '404':
        message = message + value + ' Not Found\r\n' + date_string + '\r\n'
    elif value == '501':
        message = message + value + ' Method Not Implemented\r\n' + date_string + '\r\n'
    elif value == '505':
        message = message + value + ' Version Not Supported\r\n' + date_string + '\r\n'
    return message

# A function to send the given response and file back to the client.
def send_response_to_client(sock, code, file_name):

    type = 'text/html'
    # Get size of file

    file_size = os.path.getsize(file_name)

    # Construct header and send it

    header = prepare_response_message(code) + 'Content-Type: ' + type + '\r\nContent-Length: ' + str(file_size) + '\r\n\r\n'
    sock.send(header.encode())

    # Open the file, read it, and send it

    with open(file_name, 'rb') as file_to_send:
        while True:
            chunk = file_to_send.read(BUFFER_SIZE)
            if chunk:
                sock.send(chunk)
            else:
                break

# Function to parse the config file, making sure that it is not full of white space
def parse_config_file(file_name):
    # Open config file and assess its contents
    file = open(file_name, 'r')
    server_dict = {}
    text = file.readlines()

    # If there is nothing, raise error
    if(len(text) == 0):
        raise ValueError

    # If there are contents, check if they are of correct format
    else:
        line_count = 0
        space_count = 0
        for i in text:
            if(i == '\n'):
                space_count+=1
            else:
                line_count+=1
    if(space_count == len(text)):
        raise ValueError
    else:
        for i in text:
            if (i == '\n'):
                pass
            else:
                if(i[-1] == '\n'):
                    server_dict[i[:-1]] = 0
                else:
                    server_dict[i] = 0
    file.close()
    return server_dict

# Function for testing the latency of each server upon loading the load-balancer
def test_connection(server_dict): 
    epoch = datetime.utcfromtimestamp(0)
    for i in server_dict:
        server_details = i.partition(':')
        host = server_details[0]
        port = int(server_details[2])
        test_request = prepare_get_message(host, port, TEST_FILE)
        print(f'[CONNECTING] testing server {host}:{port}')
        start = datetime.now()
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((host, port))
        except ConnectionRefusedError:
            print('[ERROR] That host or port is not accepting connections. Server is being removed from list of active servers.')
            server_dict[i] = -1
            continue

        server_socket.send(test_request.encode())

        response_line = get_line_from_socket(server_socket)
        response_list = response_line.split(' ')
        headers_done = False

        # Check if there was an error. Because ever server instance should have the testing file, we will exit if there is an error
        # So that we can place the test file in the server folders before running again
        if response_list[1] != '200':
            print('Error:  An error response was received from the server.  Details:\n')
            print(response_line);
            bytes_to_read = 0
            while (not headers_done):
                header_line = get_line_from_socket(server_socket)
                header_list = header_line.split(' ')
                if (header_line == ''):
                    headers_done = True
                elif (header_list[0] == 'Content-Length:'):
                    bytes_to_read = int(header_list[1])
            print_file_from_socket(server_socket, bytes_to_read)
            sys.exit(1)
        # If it's OK, we retrieve and write the file out.
        else:

            print('[SECURED]  Server is sending file.  Downloading it now.')

            # Go through headers and find the size of the file, then save it.
    
            bytes_to_read = 0
            while (not headers_done):
                header_line = get_line_from_socket(server_socket)
                header_list = header_line.split(' ')
                if (header_line == ''):
                    headers_done = True
                elif (header_list[0] == 'Content-Length:'):
                    bytes_to_read = int(header_list[1])
            save_file_from_socket(server_socket, bytes_to_read, TEST_FILE)
        
        # End timer and add time delay to dictionary
        finish = datetime.now()
        start_since_epoch = (start - epoch).total_seconds()*1000.0
        finish_since_epoch = (finish - epoch).total_seconds()*1000.0
        time_delay = finish_since_epoch - start_since_epoch
        server_dict[i] = time_delay

        print(f"[COMPLETE] {host}:{port} start: {start} end: {finish}\n")

    return server_dict

def main():
    signal(SIGINT, signal_handler)

    # Make sure the user is passing a config file
    try:
        args = len(sys.argv)
        if((args == 2)):
            pass
        else:
            raise ValueError
    except ValueError:
        print('Error:  You must enter exactly 2 arguments. Usage should be: loadbalancer.py config.txt')
        sys.exit(1)

    try:
        config_file = sys.argv[1]
        config_file_type = config_file.rpartition('.')[2]

        # Make sure config file is a .txt

        if(config_file_type != 'txt'):
            raise ValueError
        else:
            # Parse config file, and store the server details in a dictionary
            server_dict = parse_config_file(config_file)

    except ValueError:
        print('Error:  Invalid config file. Config file must be a txt and must only contain lines of the format host:port. Only one host:port combination per line')
        sys.exit(1)

    # Test each server response time. Remove the server if there is erros, otherwise update it's time
    server_dict = test_connection(server_dict)
    
    # Sort the servers in order of performance
    server_dict = dict(sorted(server_dict.items(), key=lambda item: item[1]))

    # Remove any inactive servers, marked by a -1 in the dictionary
    for key in list(server_dict):
        if server_dict[key] == -1:
            del server_dict[key]

    # Create a list of server details, where there are as many server instances as the index of the server in the sorted dictionary
    balancer_list = create_balancer_list(server_dict)
    mod_balancer = len(balancer_list)
    # Now that we have prioritized the servers, we can accept requests

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(('', PORT))
    print('Clients can create connections at port ' + str(client_socket.getsockname()[1]))
    client_socket.listen(1)

    while(1):
        print("[WAITING] Ready to receive connection from client")
        conn, addr = client_socket.accept()
        print('Accepted connection from client address:', addr)
        print('Connection to client established, waiting to receive message...')

    # We obtain our request from the socket.  We look at the request and
    # figure out what to do based on the contents of things.

    request = get_line_from_socket(conn)
    print('Received request:  ' + request)
    request_list = request.split()

    # This server doesn't care about headers, so we just clean them up.

    while (get_line_from_socket(conn) != ''):
        pass

    if request_list[0] != 'GET':
            print('Invalid type of request received ... responding with error!')
            send_response_to_client(conn, '501', '501.html')

    # If we did not get the proper HTTP version respond with a 505.

    elif request_list[2] != 'HTTP/1.1':
        print('Invalid HTTP version received ... responding with error!')
        send_response_to_client(conn, '505', '505.html')
    
    
    
    
    print('done')

if __name__ == '__main__':
    main()