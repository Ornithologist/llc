'''
A running example of SocketProxy.
To test, run:
    "python3.6 run.py -p <local_port> -i <remote_ip> -t <remote_port>"
'''

import argparse
import asyncio
from socket_proxy import SocketProxy

def start_proxy(local_port, port, host):
    loop = asyncio.get_event_loop()
    proxy = SocketProxy((host, port))
    proxy.listen(local_port)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        proxy.halt()
        loop.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Socket Proxy')
    parser.add_argument('-p', '--port', type=int,
                        required=True, help='Local port number to bind')
    parser.add_argument('-i', '--write_ip', type=str,
                        required=True, help='Remote server IP address')
    parser.add_argument('-t', '--write_port', type=int,
                        required=True, help='Remote server port number')
    args = parser.parse_args()
    start_proxy(local_port=args.port, port=args.write_port, host=args.write_ip)
