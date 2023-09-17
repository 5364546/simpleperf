# Import necessary libraries
import argparse
import socket
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Description:
# Checks if a given value is positive, raises an error if not, and returns the value as an integer.
# Arguments:
# value (str): A string representation of a number.
# Returns:
# int: The integer representation of the input value if it is positive.
def check_positive(value):
   
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive value" % value)
    return ivalue


# Description:
# Converts a string representation of data size (B, KB, MB) to the number of bytes.
# Arguments:
# size (str): A string representation of data size, e.g., '1KB', '2MB'.
# Returns:
# int: The number of bytes equivalent to the input data size.
def num_bytes(value):
   
    if value[-2:] == "KB":
        return int(value[:-2]) * 1000
    elif value[-2:] == "MB":
        return int(value[:-2]) * 1000000
    elif value[-1:] == "B":
        return int(value[:-1])
    else:
        raise argparse.ArgumentTypeError("Invalid format for --num. Use B, KB, or MB.")

    # Description:
# Parses command-line arguments and starts either the server or client depending on the specified arguments.
def main():
    
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Simpleperf client and server mode.')
    parser.add_argument('-s', '--server', action='store_true', help='Enable server mode')
    parser.add_argument('-b', '--bind', type=str, default='', help='IP address to bind the server')
    parser.add_argument('-p', '--port', type=int, default=8088, help='Port number for the server to listen on')
    parser.add_argument('-f', '--format', type=str, default='MB', help='Summary format (B, KB, MB)')
    parser.add_argument('-n', '--num', type=num_bytes, default=None, help='Number of bytes to transfer (B, KB, MB)')
    parser.add_argument('-c', '--client', action='store_true', help='Enable client mode')
    parser.add_argument('-I', '--serverip', type=str, default='127.0.0.1', help='IP address of the server')
    parser.add_argument('-t', '--time', type=check_positive, default=None, help='Duration for sending data in seconds (time > 0)')
    parser.add_argument('-i', '--interval', type=check_positive, default=None, help='Print statistics per z seconds (z > 0)')
    parser.add_argument('-P', '--connections', type=check_positive, default=1, help='Number of parallel connections')

    # Parse command line arguments
    args = parser.parse_args()

    # Check if server or client mode is specified
    if not args.server and not args.client:
        print('Error: you must run either in server or client mode.')
        return

     # Start server or client based on command line arguments
    if args.server:
        server(args.bind, args.port, args.format)
    elif args.client:
        # Check if both num_bytes and duration are specified
        if args.num is None and args.time is None:
            args.time = 25  # Default time
        elif args.num is not None and args.time is not None:
            print('Error: you cannot use both --num and --time at the same time.')
            return

        # Start multiple client connections if specified
        with ThreadPoolExecutor(max_workers=args.connections) as executor:
            futures = [executor.submit(client, args.serverip, args.port, args.num, args.time, args.format, args.interval, i + 1) for i in range(args.connections)]

            # Wait for all client connections to finish
            for future in futures:
                future.result()


# Description:
# Starts the server, binds to the given IP and port, and listens for incoming client connections.
# Starts a new thread for each connection to handle data transfer.
# Arguments:
# ip (str): The IP address to bind the server.
# port (int): The port number to bind the server.
def server(bind_ip, port, format):
    # Description:
    # Handles data transfer for a single client connection.
    # Receives data from the client, measures the transfer rate, and prints the transfer statistics.
    # Arguments:
    # conn (socket): The client socket object.
    # addr (tuple): The client IP and port tuple.
    # format The summary format (B, KB, MB)
    def handle_client(conn, addr, format):
       
        server_ip, server_port = conn.getsockname()
        with conn:
            print(f'A simpleperf client with {addr[0]}:{addr[1]} is connected with {server_ip}:{server_port}')

            start_time = time.time()
            total_received = 0

            # Receive data from the client and update total_received
            while True:
                data = conn.recv(1000)
                total_received += len(data)
                if data == b'BYE':
                    conn.sendall(b'ACK: BYE')
                    break

            end_time = time.time()
            elapsed_time = end_time - start_time
            bandwidth = total_received / elapsed_time

            # Convert total_received and bandwidth to the specified format
            if format == 'KB':
                total_received /= 1000
                bandwidth /= 1000
            elif format == 'MB':
                total_received /= 1000000
                bandwidth /= 1000000

            # Print the transfer statistics
            print(f'ID\t\tInterval\t\tReceived\tRate')
            print(f'{addr}\t0.0 - {elapsed_time:.1f}\t{total_received:.1f} {format}\t{bandwidth:.1f} Mbps')

    # Create a TCP socket and bind to the specified IP and port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((bind_ip, port))
        s.listen()
        print(f'A simpleperf server is listening on port {port}')

        # Accept incoming client connections and start a new thread to handle each connection
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, format))
            client_thread.start()

"""
    Print interval statistics for the client data transfer.
    :param connection_id: The unique identifier for the client connection
    :param client_ip: The client IP address
    :param client_port: The client port number
    :param start_time: The start time of the data transfer
    :param prev_total_sent: The total number of bytes sent at the previous interval
    :param format: The summary format (B, KB, MB)
    :param interval: The interval duration in seconds
    :param total_sent: The total number of bytes sent so far
    """
def print_interval_stats(connection_id, client_ip, client_port, start_time, prev_total_sent, format, interval, total_sent):
    
    current_time = time.time()
    elapsed_time = current_time - start_time
    interval_elapsed_time = elapsed_time - interval

    interval_transfer = (total_sent - prev_total_sent)
    interval_bandwidth = (interval_transfer / (1024 * 1024)) / interval  # MBps

    # Convert interval_transfer and interval_bandwidth to the specified format
    if format == 'KB':
        interval_transfer /= 1024
        interval_bandwidth *= 1024
    elif format == 'MB':
        interval_transfer /= (1024 * 1024)

    # Print the interval statistics
    print(f'({connection_id}) {client_ip}:{client_port}\t{interval_elapsed_time:.1f} - {elapsed_time:.1f}s\t{interval_transfer:.1f} {format}\t{interval_bandwidth:.1f} MBps')




print_interval_stats.prev_total_sent = 0


"""
    # Description:
    # Starts a client connection to the server and performs data transfer.
    # Sends data to the server based on the specified number of bytes or duration.
    # Prints interval statistics if specified.
    # Sends a 'BYE' message to the server indicating the end of the transfer.
    # Waits for an 'ACK: BYE' message from the server.
    # Prints the final summary of the client connection.
    :param server_ip: The IP address of the server
    :param port: The port number of the server
    :param num_bytes: The number of bytes to transfer (None if duration is specified)
    :param duration: The duration of the data transfer in seconds (None if num_bytes is specified)
    :param format: The summary format (B, KB, MB)
    :param interval: The interval duration in seconds for printing statistics (None if not specified)
    :param connection_id: The unique identifier for the client connection
    """
def client(server_ip, port, num_bytes, duration, format, interval, connection_id):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        print(f'A simpleperf client ({connection_id}) connecting to server {server_ip}, port {port}')
        s.connect((server_ip, port))
        client_ip, client_port = s.getsockname()
        print(f'Client ({connection_id}) connected with {server_ip} port {port}')

        start_time = time.time()
        if interval is not None:
            last_print_time = start_time

        total_sent = 0
        prev_total_sent = 0

        # Send initial message to server indicating the start of transfer
        start_msg = f'START {start_time}\n'
        s.sendall(start_msg.encode())

        # Send data to the server based on num_bytes or duration
        if num_bytes is not None:
            while total_sent < num_bytes:
                to_send = min(1000, num_bytes - total_sent)
                s.sendall(b'0' * to_send)
                total_sent += to_send
                if interval is not None and time.time() - last_print_time >= interval:
                    print_interval_stats(connection_id, client_ip, client_port, start_time, prev_total_sent, format, interval, total_sent)
                    last_print_time = time.time()
                    prev_total_sent = total_sent

        elif duration is not None:
            end_time = start_time + duration
            while time.time() < end_time:
                s.sendall(b'0' * 1000)
                total_sent += 1000
                if interval is not None and time.time() - last_print_time >= interval:
                    print_interval_stats(connection_id, client_ip, client_port, start_time, prev_total_sent, format, interval, total_sent)
                    last_print_time = time.time()
                    prev_total_sent = total_sent

        # Send a message to the server indicating the end of transfer
        time.sleep(6)
        s.sendall(b'BYE')
        data = s.recv(1000)
        if data == b'ACK: BYE':
            elapsed_time = time.time() - start_time
            bandwidth = total_sent / elapsed_time

            # Convert total_sent and bandwidth to the specified format
            if format == 'KB':
                total_sent /= 1000
                bandwidth /= 1000
            elif format == 'MB':
                total_sent /= 1000000
                bandwidth /= 1000000
            
            # Print the final summary of the client connection
            print('----------------------------------------------------------')
            print(f'ID\t\tInterval\tTransfer\tBandwidth')
            print(f'{client_ip}:{client_port}\t0.0 - {elapsed_time:.1f}s\t{total_sent:.1f} {format}\t{bandwidth:.1f} MBps')

# Entry point of the script
if __name__ == '__main__':
    main()


