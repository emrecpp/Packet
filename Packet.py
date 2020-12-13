# -*- coding: utf-8 -*-
""" With Socket, Send, Recv and Parse data
"""

version = "1.0.4"
__author__ = "Emre Demircan (emrecpp1@gmail.com)"
__date__ = "2020-12-13"

import sys, os, time
import socket
from functools import singledispatch
import struct


class Packet(object):
    storage = bytearray()
    _rpos, _wpos, encryptEnabled = 0, 0, False
    useNtohl = True
    PrintErrorLog=True

    # Maximum a Variable data Size = "\xFF\xFF\xFF\xFF" (4.294.967.295 bytes (4GB))
    # Opcode Range: [0-255]

    def __init__(self, opcode=0, useNtohl=True, encryptEnabled=False, PrintErrorLog=True):
        super(Packet, self).__init__()
        self._rpos = 0
        self._wpos = 0
        self.encryptEnabled=encryptEnabled
        self.PrintErrorLog = PrintErrorLog
        self.overload_append = singledispatch(self.append)
        self.overload_append.register(int, self.append_int)
        self.overload_append.register(str, self.append_str)
        self.overload_append.register(bytearray, self.append_bytearray)
        self.storage = bytearray()
        self.storage.clear()
        self.storage.append(opcode)
        self._rpos = 1 # Skip Opcode
        if opcode != 0:
            self._wpos = 1

        self.useNtohl = useNtohl

    def append(self, buffer):
        return TypeError("append Unknown Data Type")

    def clear(self):
        if len(self.storage) > 0 and self.storage[0] != 0:
            # fmt = '%ds %dx %ds' % (0, 1, len(self.storage)-1)
            # self.storage = bytearray(struct.unpack(fmt, self.storage)[1])
            self.storage = bytearray(self.storage[0:1])
            self._rpos = 1
            self._wpos = 1
        else:
            self.storage.clear()
            self._rpos = 0
            self._wpos = 0
    #00000000: 07 01 00 00 00 00 00 00 0D 45 6D 72 65 20 44 65   .........Emre.De
    #00000010: 6D 69 72 63 61 6E                                  mircan
    # To ->
    #00000000: E3 D9 D4 D0 CC C8 C4 C0 C9 FD 21 22 11 C8 E8 05   ã.Ù.Ô.Ð.Ì.È.Ä.À.É.ý.!."...È.è..
    #00000010: 09 01 06 F3 ED F6                                  ......ó.í.ö
    def Encrypt(self):
        for i in range(self.size()):
            data = self.storage[i]
            encVal = 0x123 + i*4
            encVal ^= 0xFF

            self.storage[i] = (data + encVal) & 0xFF

    def Decrypt(self):
        for i in range(self.size()):
            data = self.storage[i]
            encVal = 0x123 + i*4
            encVal ^= 0xFF

            self.storage[i] = (data-encVal) & 0xFF

    def append_int(self, buffer):
        bf = struct.pack("<I", buffer)

        # Maximum Integer Value = "\xFF\xFF\xFF\xFF" (4.294.967.295)
        '''if self.useNtohl:
            self.storage.extend(struct.pack("<I", socket.htonl(len(bf))))
        else:
            self.storage.extend(struct.pack("<I", len(bf)))'''

        self.storage.extend(bf)
        self._wpos += len(bf)

    def append_str(self, buffer):
        bytesBuffer = bytes(buffer, "utf-8")
        bf = struct.pack("%ds" % (len(bytesBuffer)), bytesBuffer)
        if self.useNtohl:
            self.storage.extend(struct.pack("<I", socket.htonl(len(bf))))
        else:
            self.storage.extend(struct.pack("<I", len(buffer)))
        self.storage.extend(bf)
        self._wpos += len(bf)
    def append_bytearray(self, buffer):
        if self.useNtohl:
            self.storage.extend(struct.pack("<I", socket.htonl(len(buffer))))
        else:
            self.storage.extend(struct.pack("<I", len(buffer)))
        self.storage.extend(buffer)
        self._wpos += len(buffer)

    def __len__(self):
        return self.size()

    def size(self):
        return len(self.storage)

    def GetOpcode(self): # Opcode must be 0-255 because reserve first 1 byte (max=\xFF=255)
        return 0 if len(self.storage) == 0 else self.storage[0]

    def __lshift__(self, value):
        self.overload_append(value)
        return self

    def __rshift__(self, value):
        if self.size() > 0 and self._rpos == 0:  # Skip Opcode
            self._rpos = 1
        if value.obj == int:
            Sonuc = self.read_int()
        elif value.obj == str:
            Sonuc = self.read_str()
        elif value.obj == bytearray:
            Sonuc = self.read_bytearray()
        else:
            return self

        value.obj = Sonuc
        return self

    def readLength(self): # Reserved Data Size, in 4 bytes
        if self._rpos +4 > self.size():
            return None
        ReadLength = struct.unpack("<I", self.storage[self._rpos:self._rpos + 4])[0]
        if self.useNtohl:
            ReadLength = socket.ntohl(ReadLength)

        self._rpos += 4
        return ReadLength

    def read_int(self):  # Maximum Integer Value = \xFF\xFF\xFF\xFF = (4.294.967.295)
        if self._rpos + 4 > self.size():
            return 0

        '''ReadLength = struct.unpack("<I", self.storage[self._rpos:self._rpos+4])[0]
        if self.useNtohl:
            ReadLength = socket.ntohl(ReadLength)

        if self._rpos+ReadLength >= self.size():
            return 0

        self._rpos += ReadLength
        data = struct.unpack("<I", self.storage[self._rpos:self._rpos+ReadLength])[0]
        self._rpos += ReadLength
        '''
        data = struct.unpack("<I", self.storage[self._rpos:self._rpos + 4])[0]
        self._rpos += 4
        return data

    def read_str(self):
        ReadLength = self.readLength()
        if ReadLength == None:
            return ""

        data = self.storage[self._rpos:self._rpos + ReadLength].decode('utf-8')
        self._rpos += ReadLength
        return data

    def read_bytearray(self):
        ReadLength = self.readLength()
        if ReadLength == None:
            return bytearray()
        data = bytearray(self.storage[self._rpos:self._rpos+ReadLength])
        self._rpos += ReadLength
        return data

    class ref():  # We don't have Pointers in Python :(
        obj = None
        def __init__(self, obj): self.obj = obj
        def __get__(self, instance, owner): return self.obj
        def __set__(self, instance, value): self.obj = value
        def __eq__(self, other): return other == self.obj
        def __setattr__(self, key, value): self.__dict__[key] = value
        def __getattr__(self, item): return self.obj
        def __str__(self):  # print("Data: %s" % (data_str))
            return str(self.obj)
        def __int__(self):  # print("Data: %d" % (data_int))
            return self.obj

    # waitRecv = if you have a Recv function in thread, then you sent packet will received from this thread received function. So creating new socket, sending and receiving data from new socket. So Thread Recv function can't access this data.
    def Send(self, s, waitRecv=False):
        try:
            if self.size() == 0:
                return False
            if hasattr(s, "_closed") and s._closed:
                if self.PrintErrorLog: print("Packet Handler | Connection is already closed!")
                return False
            if self.useNtohl:
                msg = struct.pack(">I", socket.ntohl(self.size()))
            else:
                msg = struct.pack(">I", self.size())
            TargetSocket = s

            if waitRecv:
                SocketCreatedNew = False
                if type(waitRecv) == socket.socket: # if Socket created we will not close it and we can use it multiple times.
                    TargetSocket = waitRecv
                else:
                    # self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack("LL", recv_timeout, 0))
                    # self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, struct.pack("LL", send_timeout, 0))

                    SocketCreatedNew = True
                    newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    #newSocket.connect(s.getsockname())
                    newSocket.connect(s.getpeername())  # Be sure; Server can listen more than 1 socket.
                    TargetSocket = newSocket

            TargetSocket.send(msg)
            numberOfBytes = self.size()
            totalBytesSent = 0
            if self.encryptEnabled: self.Encrypt()

            while totalBytesSent < numberOfBytes:
                totalBytesSent += TargetSocket.send(self.storage[totalBytesSent:])

            if waitRecv:
                self.Recv(TargetSocket)
                if SocketCreatedNew:
                    TargetSocket.shutdown(socket.SHUT_RDWR)
                    TargetSocket.close()

                return self

            return True
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
            return False
        except OSError:
            if self.PrintErrorLog: print("Packet Handler | Send Failed probably Connection Closed.")
            return False
        except Exception as ERR:
            if self.PrintErrorLog: self.PrintErr("Packet Send Err: %s    " % str(ERR))
            return False

    def Recv(self, s):
        try:
            packetSize = s.recv(4)
            if not packetSize:  # Connection Closed
                return False

            packetSize = struct.unpack(">I", packetSize)[0]
            if self.useNtohl:
                packetSize = socket.ntohl(packetSize)
            self.storage.clear()
            totalBytesReceived = 0


            while totalBytesReceived < packetSize:
                ReceivedBytes = s.recv(packetSize-totalBytesReceived)

                if not ReceivedBytes:
                    if self.PrintErrorLog: print("Packet Handler | Connection closed while receiving")
                    return False
                self.storage.extend(ReceivedBytes)
                totalBytesReceived+=len(ReceivedBytes)

            if self.encryptEnabled: self.Decrypt()


            self._wpos = self.size()
            if self._rpos == 0 and self.size() > 0:
                self._rpos = 1 # Skip Opcode
            return True
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
            return False
        except Exception as ERR:
            if self.PrintErrorLog: self.PrintErr("Packet Recv Err: %s    " % str(ERR))
            return False
    def PrintErr(self, ERR):
        exc_type, exc_obj, exc_tb = sys.exc_info();
        fname = exc_tb.tb_frame.f_code.co_filename
        print(ERR, exc_type, fname, exc_tb.tb_lineno)


    # >>> Output : Print
    # Flag (Default) = 1 | 2 | 4
    # 00000000: 07 01 00 00 00 00 00 00 0D 45 6D 72 65 20 44 65   .........Emre.De
    # 00000010: 6D 69 72 63 61 6E                                  mircan

    # Flag = 1
    # 00000000:
    # 00000010:

    #Flag = 2
    # 07 01 00 00 00 00 00 00 0D 45 6D 72 65 20 44 65
    # 6D 69 72 63 61 6E

    # Flag = 4
    # .........Emre.De
    # mircan
    def Print(self, maxPerLine=16, utf_8=True, Flag=1|2|4): # 1 Address, 2 Hex Bytes, 4 ASCII
        try:
            Total = ""
            dumpstr=""
            for addr in range(0, self.size(),maxPerLine):
                d = bytes(self.storage[addr:addr+maxPerLine])
                if (Flag & 1) == 1:
                    line = '%08X: ' % (addr)
                else:
                    line = ""
                if (Flag & 2) == 2:
                    dumpstr = ' '.join('%02X'%hstr for hstr in d)

                line += dumpstr[:8 * 3]
                if len(d) > 8:
                    line += dumpstr[8 * 3:]

                pad = 2
                if len(d) < maxPerLine:
                    pad += 3 * (maxPerLine - len(d))
                if len(d) <= 8:
                    pad += 1
                line += ' ' * pad

                if (Flag & 4) == 4:
                    if utf_8:
                        line+=" "
                        try:
                            utf8str = str(bytes(self.storage[addr:addr+maxPerLine]), 'utf-8')
                        except UnicodeDecodeError:
                            utf8str = ' '.join(chr(hstr) for hstr in self.storage[addr:addr+maxPerLine])#str(self.storage[addr:addr+maxPerLine])
                        listutf8str = list(utf8str)
                        for i in range(len(listutf8str)):
                            #if listutf8str[i] == "\x00" or ord(listutf8str[i]) < 0x20:
                            if ord(listutf8str[i]) <= 0x20:
                                listutf8str[i]="."
                            i+=1
                        line+= "".join(listutf8str)
                    else:
                        line += " "
                        for byte in d:
                            if byte > 0x20 and byte <= 0x7E:
                                line += chr(byte)
                            else:
                                line += '.'
                Total+=line+"\n"
            print(Total)
            return Total
        except Exception as err:
            self.PrintErr("Print Error: %s    " % err)
            return ""
