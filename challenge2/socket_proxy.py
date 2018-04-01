'''
SocketProxy is a service that reads data from arbitary socket and proxies it
to a predefined socket.
Socket type: SOCK_STREAM
'''

import asyncio

class ProxyClient(object):
    '''
    ProxyClient talks to a remote server in stream socket
    @param target: a (ip_str, port_int) tuple
    '''

    def __init__(self, target):
        self.transport = None
        self.target = target

    def connect(self):
        '''set up connection to server'''
        loop = asyncio.get_event_loop()
        conn = loop.create_connection(
            asyncio.Protocol, host=self.target[0], port=self.target[1])
        self.transport, _ = loop.run_until_complete(conn)

    def send(self, msg):
        '''
        send message to server
        @param msg: data bytes
        '''
        self.transport.write(msg)

class ProxyProtocol(asyncio.Protocol):
    '''
    A streaming protocol
    @param proxy_client: an instance of ProxyClient
    '''

    def __init__(self, proxy_client):
        self.proxy_client = proxy_client

    def connection_made(self, transport):
        print("[STATUS] connection made.")

    def data_received(self, data):
        '''reads data from listening port and proxies it to self.proxy_client'''
        self.proxy_client.send(data)

class SocketProxy(object):
    '''
    A proxy server re-directs stream data to a specified server
    @param destination: a (ip_str, port_int) tuple
    '''

    def __init__(self, destination):
        self.destination = destination
        self.server = None
        self.client = ProxyClient(destination)

    def listen(self, port):
        '''
        binds and listens to the port, meanwhile connects the client
        @param port: the local port number to listen to
        '''
        loop = asyncio.get_event_loop()
        listen = loop.create_server(lambda: ProxyProtocol(self.client),
                                    host='127.0.0.1', port=port)
        self.server = loop.run_until_complete(listen)
        self.client.connect()

    def halt(self):
        '''stops all remaining tasks and perform gracefully shutdown'''
        if self.server is not None:
            print('[STATUS] Performing graceful shutdown...')
            self.server.close()
