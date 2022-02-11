import socket
import socketserver

class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''
        t = (data[2] >> 3) & 15
        if t == 0:
            i = 12
            l = data[i]
            while l != 0:
                self.domain += data[i + 1:i + l + 1].decode('utf-8') + '.'
                i += l + 1
                l = data[i]

    def response(self):
        if self.domain:
            name = self.domain
            namemap = DNSServer.namemap
            if namemap.__contains__(name):
                ip = namemap[name]
            else:
                ip = socket.gethostbyname_ex(name)[2][0]
            packet = b''
            packet += self.data[:2] + b'\x81\x80'
            packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'
            packet += self.data[12:]
            packet += b'\xc0\x0c'
            packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'
            packet += bytearray.fromhex('{:02X}{:02X}{:02X}{:02X}'.format(*map(int, ip.split('.'))))
            return packet

class DNSUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        query = DNSQuery(data)
        socket.sendto(query.response(), self.client_address)

class DNSServer:
    def __init__(self, port=53):
        DNSServer.namemap = {}
        self.port = port
    def addname(self, name, ip):
        DNSServer.namemap[name] = ip
    def start(self):
        HOST, PORT = "0.0.0.0", self.port
        server = socketserver.UDPServer((HOST, PORT), DNSUDPHandler)
        server.serve_forever()

def fake_dns(server_ip):
    dns = DNSServer()
    dns.addname('secure.zwift.com.', server_ip)
    dns.addname('us-or-rly101.zwift.com.', server_ip)
    dns.start()
