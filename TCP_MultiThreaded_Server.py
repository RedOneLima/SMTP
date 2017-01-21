import threading
import SocketServer

#This is a simple python TCP SMTP server that follows basic SMTP protocols
#   Kyle Hewitt     CS3700 Networks Homework 4      29 Feb 2016


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    #override function called at the creation of the TCP connection
    def setup(self):
        self.request.sendall("220 OKAY\r\n")
        print 'Client {} started on {}'.format(self.client_address,threading.current_thread().name)

    #override function called at the end of the TCP connection
    def finish(self):
        print 'Client connection on {} ended'.format(threading.current_thread().name)

    #Override function to handle the process of the client thread
    def handle(self):
        sent = 1
        msg_body = ''
        while 1:
            try:
                #receive data from client thread
                data = self.request.recv(1024)
                #check for quit
                if data == 'quit\r\n':
                    self.request.sendall('221 {} closing connection'.format(server.server_address))
                    print '221 {} closing connection'.format(self.server)
                    self.finish()
                    break
            except StandardError:
                print('{} on {} connection closed'.format(self.client_address,threading.current_thread().name))
                break

            else:
                try:
                    print 'From {} on {}: {}'.format(self.client_address,threading.current_thread().name,data)
                    #the expected command is controled by a int counter 'sent'
                    if sent == 1:
                        #handle hello
                         data_list = data.split(' ')
                         if data_list[0] == 'HELO':
                            self.request.sendall('250 {} Hello {}\r\n'.format(server_thread.name,data_list[1]))
                            sent +=1
                         else:
                             self.request.sendall('503 5.5.2 Send hello first\r\n')
                    elif sent == 2:
                        #handle 'MAIL FROM'
                        data_list = data.split(':')
                        remove_bracket = str(data_list[1])
                        remove_bracket = remove_bracket[2:-1]
                        data_list[1] = remove_bracket
                        if data_list[0] == 'MAIL FROM':
                            self.request.sendall('250 2.1.0 {} Sender OK\r\n'.format(data_list[1]))
                            sent +=1
                        else:
                            self.request.sendall('503 5.5.2 Need mail command\r\n')
                    elif sent == 3:
                        #Handle 'RCPT TO'
                        data_list = data.split(':')
                        remove_bracket = str(data_list[1])
                        remove_bracket = remove_bracket[2:-1]
                        data_list[1] = remove_bracket
                        if data_list[0] == 'RCPT TO':
                            self.request.sendall('250 2.1.5 {} Recipient ok\r\n'.format(data_list[1]))
                            sent +=1
                        else:
                            self.request.sendall('503 5.5.2 Need rcpt command\r\n')
                    elif sent == 4:
                        #Handle 'DATA'
                        if 'DATA\r\n' ==  data.upper():
                            self.request.sendall('354 Start mail input\r\n')
                            sent +=1
                        else:
                            self.request.sendall('503 5.5.2 Need data command\r\n')
                    elif sent ==5:
                        #Handle body
                        data_list = data.split('\r\n')
                        #checking for termination char
                        for line in data_list:
                            if str(line) == '.':
                                msg_body += '\n{}'.format(str(line))
                                out_file = open('out_file', 'w')
                                out_file.write(msg_body)
                                self.request.sendall('250 Message Accepted For Delivery \r\n')
                                sent = 1
                                out_file.close()
                            else:
                                msg_body += str(line)+'\r\n'
                # gets thrown when case 2 and 3 are in incorrect format
                except IndexError:
                    if sent == 2:
                        self.request.sendall('503 5.5.2 Need mail command\r\n')
                    elif sent == 3:
                        self.request.sendall('503 5.5.2 Need rcpt command\r\n')


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "cs3700.msudenver.edu", 5120
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    try:
        #create/start multithreaded server
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        print "Server loop running in thread:", server_thread.name
    except Exception:
            #if connection fails
            print "Ending server process"
            server.server_close()
