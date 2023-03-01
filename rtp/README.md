# Reliable Transport Protocol
## Name: Taylor LaMantia

This program is a reliable transport protocol. It uses file transfer over a UDP proxy server. It delivers a file from the sender to receiver over a lossy medium that has varying rate limit, drops, duplicates, reorders, and modifies packets.

# Receiver End:

Begin by running rrecv.py - the receiving server. Run the command with --alg ra to specify that the reliable transport alg with be used.

# UDP Box

Once the receiving server is running, run UDP box. This will corrupt packets, cause data loss, and send duplicates. It enforces a data rate limit of 50 KBytes/sec, but packet loss rate can be specified with --loss_rate

# Sending End:

When running the UDP_Box, the sender has to be modified to send to port 8880 (using the --port 8880 when running the rsend.py). Also enter the command with --alg ra to specify that the reliable transport algorithm will be used. 


# Reliable Transport Algorithm Usage and Evaluation

To test the reliable transport algorithm, the UDP_box is run at different conditions, sending the lorem.txt file. The following table shows the result of the transfer rates at four conditions (always limiting bandwidth to 50 KBps).


| Condition | Parameters | Transfer Rate |
| ---- | ---- | ---- |
| Ideal         | Loss rate = 0, dupe rate = 0, ooo rate = 0, ber = 0             | 0.383 seconds = 7881 bps |
|  Good         | Loss rate = 0.01, dupe rate = 0.01, ooo rate = 0.01, ber = 1e-8 | 0.426 seconds = 7095 bps |
| Medium        | Loss rate = 0.02, dupe rate = 0.02, ooo rate = 0.02, ber = 1e-6 | 3.57 seconds = 846 bps |
|  Terrible     | Loss rate = 0.1, dupe rate = 0.03, ooo rate = 0.05, ber = 1e-4  | 5.38 seconds = 562 bps |
