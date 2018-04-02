# socket_proxy

SocketProxy listens on a port, reads arbitary data from a socket, and forwards the data to another socket.

To run the test, do

```bash
python3.6 test.py
```

## Assumptions

* This service would be used for file transfer. Data integrity and intra-data order should be ensured.
* There might be multiple processes trying to connect the service at once. Scalability is desired.

## Design Choices

### Python3.6 (again)

There is no distinctive performance differences of socket implementation between Python2.7 and Python3.6. However, due to the fact that an asynchronous approach typically improves the system's scalability (it may not be true under certain conditions, but it applies here), Python3.6, with its builtin `asyncio` standard library, is desired. Moreover, `asyncio` conveniently provides a streaming protocol base `asyncio.Protocol` and communication facilities such as `asyncio.create_connection()`.

### SocketProxy Design

Three classes are defined in [socket_proxy.py](./socket_proxy.py):

* ProxyClient -- creates a streaming transport connection. It's used by SocketProxy to forward data to a remote service
* ProxyProtocol -- extends the base Protocol by adding the callback to proxy data when reveiving it. It's used by SocketProxy to forward recived data.
* SocketProxy -- the server class that listens on a given port.

Thanks to its scalability and convenient wrappers, all client and server classes are written using `asyncio`. Streaming socket (SOCK_STREAM) is used to prevent data loss and corruption. It takes one extra round trip than datagram socket to initiate a connection, but it provides more stable (and relatively more secure against hijacking/spoofing) connection at a small cost.