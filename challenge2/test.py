import asyncio
import time
import unittest
from multiprocessing import Process, Queue
from socket_proxy import ProxyClient, SocketProxy

TestClient = ProxyClient  # use ProxyClient for testing

class TestProtocol(asyncio.Protocol):
    '''
    A streaming protocol that dumps received data to a list
    @param messages: a queue
    '''

    def __init__(self, messages):
        self.messages = messages

    def data_received(self, data):
        '''reads data from listening port and proxies it to self.proxy_client'''
        self.messages.put(data)

class TestServer(object):
    '''
    TestServer listens on a port and dumps the received data to a list
    @param messages: a queue object
    '''

    def __init__(self, messages):
        self.messages = messages

    def listen(self, port):
        '''
        binds and listens to the port, meanwhile connects the client
        @param port: the local port number to listen to
        '''
        loop = asyncio.get_event_loop()
        listen = loop.create_server(lambda: TestProtocol(self.messages),
                                    host='127.0.0.1', port=port)
        self.server = loop.run_until_complete(listen)

    def halt(self):
        '''perform gracefully shutdown'''
        if self.server is not None:
            self.server.close()

def run_proxy_server(local_port, port):
    loop = asyncio.get_event_loop()
    proxy = SocketProxy(('127.0.0.1', port))
    proxy.listen(local_port)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        proxy.halt()
        loop.close()

def run_test_server(port, messages):
    loop = asyncio.get_event_loop()
    test = TestServer(messages)
    test.listen(port)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        test.halt()
        loop.close()

class ProxyTest(unittest.TestCase):

    def test_hello(self):
        hello = Queue()
        server_p = Process(target=run_test_server, args=(1234, hello))
        server_p.start()

        time.sleep(1)  # sleep for a second

        proxy_p = Process(target=run_proxy_server, args=(12345, 1234))
        proxy_p.start()

        time.sleep(1)  # sleep for a second

        client = TestClient(('127.0.0.1', 12345))
        client.connect()
        client.send('hello'.encode('utf-8'))

        time.sleep(1)  # sleep for a second

        server_p.terminate()
        proxy_p.terminate()

        self.assertEqual(hello.get().decode("utf-8"), 'hello')


if __name__ == '__main__':
    unittest.main()
