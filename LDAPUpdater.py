import socketserver
import LDAPHelper as helper

# TODO: parse the command line for arguments:
# - Host
# - Port
# - Help
# - Version

# Defines what happens after a connection has been made
class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # Read data from the client (only for debugging)

        # self.rfile is a file-like object created by the handler;
        self.data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

        # Reply to the client to it closes the socket.
        # self.wfile is a file-like object used to write back
        status_message = "Request received and processed"
        self.wfile.write(status_message)

# Start the socket server
if __name__ == "__main__":
    HOST, PORT = "localhost", 4480
    # Host a TCP-server on host at a specified port and handle connections
    # in accordance to the specified handler
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    # Run until the program is forcefully killed
    server.serve_forever()
