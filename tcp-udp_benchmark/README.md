# TCP UDP Benchmarking
## Name: Taylor LaMantia

This program is an echo server (echo-server.py) and traffic generator (traffic-generator.py) that is used to evaluate the performance of TCP vs UDP

# echo-server.py
Run the echo server on the host computer with the following arguments:
--protocol: "tcp" or "udp"
--host: the host number of the computer such as 0.0.0.0 (default)
--port: port number such as 8888 (default)

# traffic-generator.py
Run the traffic generator with the following arguments:
--protocol: either "tcp" or "udp". Must match the protocol of echo server
--size: the size of packets being sent (default=10)
--bandwidth: bandwidth in packets/second to send (default=10)
--dst: destination address of the host running echo server (default=0.0.0.0)
--port: port to run on (default=8888)
--distribution: either "uniform" or "burst"
--duration: time to run in seconds (default=10)