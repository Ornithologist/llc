import asyncio
import time
import unittest
from multiprocessing import Process, Queue
from socket_proxy import ProxyClient, SocketProxy
from struct import pack, unpack

TestClient = ProxyClient    # use ProxyClient for testing
TEST_QUEUE = Queue()        # a testing queue
INT_FMT = '>i'


class TestProtocol(asyncio.Protocol):
    '''
    A streaming protocol that dumps received data to a list
    @param messages: a queue
    '''

    def __init__(self, messages):
        self.messages = messages

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        '''reads data from listening port and proxies it to self.proxy_client'''
        self.messages.put(data)

    def connection_lost(self, exc):
        self.transport.close()

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

def unpack_b2i(buffer_bytes):
    return unpack(INT_FMT, buffer_bytes)[0]

def pack_i2b(number):
    return pack(INT_FMT, number)

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
    server = TestServer(messages)
    server.listen(port)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.halt()
        loop.close()

class ProxyTest(unittest.TestCase):

    def test_integrity(self):
        self.assertTrue(TEST_QUEUE.empty())

        client = TestClient(('127.0.0.1', 12345))
        client.connect()
        client.send('hello'.encode('utf-8'))
        client.close()

        time.sleep(1)  # sleep for a second

        self.assertEqual(TEST_QUEUE.get().decode("utf-8"), 'hello')

    def test_order(self):
        self.assertTrue(TEST_QUEUE.empty())

        for i in range(10):
            client = TestClient(('127.0.0.1', 12345))
            client.connect()
            client.send(pack_i2b(i))
            client.close()

        time.sleep(1)  # sleep for a second

        for i in range(10):
            output = TEST_QUEUE.get()
            self.assertEqual(unpack_b2i(output), i)


if __name__ == '__main__':
    server_p = Process(target=run_test_server, args=(1234, TEST_QUEUE))
    server_p.start()

    time.sleep(1)               # sleep for a second

    proxy_p = Process(target=run_proxy_server, args=(12345, 1234))
    proxy_p.start()

    time.sleep(1)               # sleep for a second
    unittest.main(exit=False)   # don't exit yet, we have to clean up

    server_p.terminate()        # just terminate them =)
    proxy_p.terminate()
