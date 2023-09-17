"""
# README for simpleperf

# Overview
`simpleperf.py` is a simple client-server application that measures data transfer performance between clients and a server. The script can be run in both client and server modes. The server listens for incoming connections and measures the received data rate, while the client sends data to the server to evaluate the performance.

# Running simpleperf
"""

# 1. Start the server
# On the server machine, run the following command to start the server in server mode:
 python3 simpleperf.py -s

# By default, the server will bind to all available IP addresses and listen on port 8088. To bind the server to a specific IP address and port, use the `-b` and `-p` options:
 python3 simpleperf.py -s -b 192.168.1.1 -p 9000

# 2. Start the client
# On the client machine, run the following command to start the client in client mode:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000

# The `-I` option specifies the IP address of the server, and the `-p` option specifies the port number. To send a specific amount of data to the server, use the `-n` option:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -n 10MB

# To send data for a specific duration, use the `-t` option:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -t 30

# To print interval statistics, use the `-i` option:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -i 5

# 3. Start multiple clients
# To start multiple client connections simultaneously, use the `-P` option followed by the number of parallel connections:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -P 5

# This command will start 5 parallel client connections to the server.

# 4. Configure the summary format
# You can configure the summary format (B, KB, or MB) using the `-f` option:
 python3 simpleperf.py -s -f MB

# This command will start the server and display the received data in MB. Similarly, for the client:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -f KB

# This command will start the client and display the sent data in KB.

# Testing
# To generate data for testing, run the server and multiple clients with different configurations (data size, duration, intervals, etc.) and analyze the output statistics. Observe the transfer rates, and identify potential bottlenecks or performance issues.

# 5. Set data transfer limits
# You can set limits on the data transfer by specifying either the number of bytes or the duration of the transfer. To set the number of bytes, use the `-n` option followed by the number and unit (B, KB, or MB):
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -n 10MB

# This command will start the client and limit the data transfer to 10 MB.

# To set the duration of the transfer, use the `-t` option followed by the number of seconds:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -t 30

# This command will start the client and limit the data transfer to 30 seconds.

# Note: You cannot use both `-n` and `-t` options at the same time.

# 6. Print interval statistics
# You can print interval statistics during the data transfer by specifying the interval duration in seconds using the `-i` option:
 python3 simpleperf.py -c -I 192.168.1.1 -p 9000 -i 5

# This command will start the client and print interval statistics every 5 seconds.

# Analyzing the results
# After running multiple tests with various configurations, analyze the output statistics to identify the performance characteristics of your network. Pay attention to transfer rates, connection durations, and any performance bottlenecks or issues. This information can help you understand the network's behavior and make necessary adjustments to optimize its performance.

