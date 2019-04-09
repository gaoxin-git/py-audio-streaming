import pyaudio
import time
import socket
import threading
import audioop
import numpy

HOST,UDPPORT = "0.0.0.0",1234   #for udp

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST,UDPPORT))


WIDTH = 2
CHANNELS = 1
RATE = 8000
CHUNK = 160

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    s.sendto(in_data, ('127.0.0.1',8080))
    # print(len(in_data))
    return (in_data, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=160,
                stream_callback=None)

stream.start_stream()

def sampleAudio(s):
    while True:
        data = stream.read(CHUNK)
        alaw = audioop.lin2alaw(data,WIDTH)
        print('tx',len(alaw))
        s.sendto(alaw, ('127.0.0.1',UDPPORT))

def processUdpData(s):
    import random
    print('udp data monitoring...')
    while True:
        data, addr = s.recvfrom(8192)
        pcm = audioop.alaw2lin(data,WIDTH)
        stream.write(pcm)
        print('rx',len(pcm))

t2 = threading.Thread(target=processUdpData,args=(s,))
t2.start()

t1 = threading.Thread(target=sampleAudio,args=(s,))
t1.start()

time.sleep(30)
stream.stop_stream()
stream.close()

p.terminate()