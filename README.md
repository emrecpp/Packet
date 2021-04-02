# Python Packet Handler
Store data as packet. Send, Recv, Encrypt it.

For C#: https://github.com/emrecpp/DataPacket-CSharp

For C++: https://github.com/emrecpp/DataPacket-CPP

Test.py 

# Example Usage

```
from Packet import Packet, ref
import sys, socket, select, time

class opcodes:
    LOGIN=100
    LOGOUT=101

HOST, PORT = "127.0.0.1", 2000
```
# CLIENT
```
Paket = Packet(opcodes.LOGIN, Encrypt=True, Compress=True)
Username = "Emre"
Paket << Username << "123" << True << bytearray(b'\x07\x10BYTES\xFF') << ["Apple", "Banana", "Orange"]
Paket.Send(socket)
```
# SERVER
```
# Listener Thread
PaketListen = Packet()
while True:
    if PaketListen.Recv(socketServer):
        PaketListen.Print("RECEIVED PACKET (YOUR TITLE)!")
        if PacketListen.GetOpcode() == opcodes.LOGIN:
            UserName, Password, RememberMe, Data, Fruits = ref(str), ref(str), ref(bool), ref(bytearray), ref(list)
            PacketListen >> UserName >> Password >> RememberMe >> Data >> Fruits
            UserName, Password, RememberMe, Data, Fruits = str(UserName), str(Password), RememberMe.obj, bytearray(Data.obj), ", ".join(Fruits.obj)  # We have to cast ref object to (int, str, bool, bytearray ...)
            # Note: Can't use bool(RememberMe), this returns True everytime!!!

            print(f"Username: {UserName}\nPassword: {Password}\nRememberMe: {'Yes' if RememberMe else 'No'}\nData: {str(Data)}\nFruits: {Fruits}")
    else:
        return # Connection Lost

```

# OUTPUT

```
Username: Emre
Password: 123
RememberMe: Yes
Data: bytearray(b'\x07\x10BYTES\xff')
Fruits: Apple, Banana, Orange


*** RECEIVED PACKET (YOUR TITLE)! *** (67)
00000000: 00 64 04 06 00 00 00 00 00 04 45 6D 72 65 00 00   .d........Emre..
00000010: 00 03 31 32 33 01 00 00 00 08 07 10 42 59 54 45   ..123.......BYTE
00000020: 53 FF 00 00 00 1D 5B 22 41 70 70 6C 65 22 2C 20   S.ÿ.........[.".A.p.p.l.e.".,..
00000030: 22 42 61 6E 61 6E 61 22 2C 20 22 4F 72 61 6E 67   "Banana",."Orang
00000040: 65 22 5D                                           e"]

```


