#!/usr/bin/env python3
import asyncio
import subprocess


HOST = '0.0.0.0'
PORT = 54321


def run_command(command):
    p = subprocess.Popen(command,
                         shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    return True


class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        run_command('{}'.format(message))
        self.transport.close()


loop = asyncio.get_event_loop()
coro = loop.create_server(EchoServerClientProtocol, HOST, PORT)
server = loop.run_until_complete(coro)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
