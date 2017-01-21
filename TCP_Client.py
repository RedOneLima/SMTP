import socket
import time, datetime

#This is a simple TCP SMTP client that takes in user input and sends it to a SMTP server per protocol.
#           Kyle Hewitt    CS3700 Networks Homework 4      29 Feb 2016

#function to send messages to the server and calc RTT
def to_server(message, yes):
    if yes:#if yes print what client sent
        print 'C: '+message
    t1 = str(datetime.datetime.now()).split(':')
    t1 = float(t1[-1])*1000
    sock.sendall(message)
    server_response = sock.recv(1024)
    t2 = str(datetime.datetime.now()).split(':')
    t2 = float(t2[-1])*1000
    RTT = t2 - t1
    return server_response, RTT

#function that gets all of the information from the user to send to the server
def user_input():
    sender,sender_domain, recpt = '','',''
    while 1:
        sender = raw_input('From: ')
        #check for valid email characters
        if '@' in sender and '.' in sender:
            sender_info = sender.split('@')
            sender_domain = sender_info[1]
            break
        else:
            print 'Enter valid sender email address'
            continue
    while 1:
        recpt = raw_input('To: ')
        #check for valid email characters
        if '@' in recpt and '.' in recpt:
            recpt_info = recpt.split('@')
            break
        else:
             print 'Enter valid recipient email address'
             continue
    subject = raw_input('Subject: ')
    message = ''
    msg_body = []
    #email body input
    print "Start mail input; end with <CRLF>.<CRLF>"
    while message != '.':
        message = raw_input()
        msg_body.append(message)

    return sender, sender_domain, recpt, subject, msg_body



#This function builds the user input to the correct SMTP protocol
def server_process(sender, sender_domain, recpt,subject, msg_body):
        #HELO
        helo = 'HELO '+sender_domain
        server_response, RTT = to_server(helo, True)
        server_response_display = server_response[:-2]
        print 'S: {}  --RTT: {}ms--'.format(server_response_display, RTT)

        #MAIL FROM
        mail_from = 'MAIL FROM: <{}>'.format(sender)
        server_response, RTT = to_server(mail_from, True)
        server_response_display = server_response[:-2]
        print 'S: {}  --RTT: {}ms--'.format(server_response_display, RTT)

        #RCPT TO
        rcpt_to = 'RCPT TO: <{}>'.format(recpt)
        server_response, RTT = to_server(rcpt_to,True)
        server_response_display = server_response[:-2]
        print 'S: {}  --RTT: {}ms--'.format(server_response_display, RTT)

        #DATA
        server_response, RTT = to_server('DATA\r\n', True)
        server_response_display = server_response[:-2]
        print 'S: {}  --RTT: {}ms--'.format(server_response_display, RTT)

        #full message
        msg_server = '\nTo: {}\r\nFrom: {}\r\nSubject: {}\n \r\n{}'.format(recpt, sender, subject, '\r\n'.join(msg_body))
        time_sent = str(datetime.datetime.now()).split(':')
        time_sent = float(time_sent[1])
        server_response, RTT = to_server(msg_server, False)
        if '250' in server_response:
            time_recv = str(datetime.datetime.now()).split(':')
            time_recv = float(time_recv[1])
            RTT = time_recv - time_sent
            server_response_display = server_response[:-3]
            print 'S: {}  --RTT: {}ms--'.format(server_response_display, RTT)


#This attemps to recover from a connection loss
def reconnect():
    sock = None
    print "Lost connection with server"
    time.sleep(.5)
    print 'Attempting to reconnect...'
    time.sleep(.5)
    print ' '
    time.sleep(.5)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        return
    except socket.error:
        print 'Unable to reconnect'
        sock.close()
        print 'Socket closed.'




HOST = raw_input('Enter Host/DNS:\n>>')
PORT =  5120
data, sender_domain = '',''
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
t1 = str(datetime.datetime.now()).split(':')
t1 = float(t1[-1])*1000
#connect to server
try:
    sock.connect((HOST, PORT))
    received = sock.recv(1024)

except socket.error:
    print 'Socket error.\nUnable to connect to SMTP server'
    reconnect()

else:
    t2 = str(datetime.datetime.now()).split(':')
    t2 = float(t2[-1])*1000
    RTT = t2 - t1
    print received
    #220 message
    if received == '220 OKAY\r\n':
        print 'Python SMTP server ready --RTT: {}ms--\n'.format(RTT)
    else:
        print 'Not connected to SMTP server'
        reconnect()

    while 1:
        #get user input and pass it into functions to handle the process
        sender, sender_domain, recpt, subject, msg_body = user_input()
        server_process(sender, sender_domain, recpt, subject, msg_body)

        #sending 'quit' command
        quitting = raw_input('Press any key to send another or type "quit" to exit\n')
        if quitting.lower() == 'quit':
            sock.sendall(quitting+'\r\n')
            print sock.recv(1024)
            sock.close()
            break
