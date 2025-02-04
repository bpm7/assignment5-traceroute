from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.
    ID = os.getpid() & 0xFFFF
    myCheckSum=0
    header=struct.pack("bbHHH",ICMP_ECHO_REQUEST,0,myCheckSum,ID,1)
    data=struct.pack("d",time.time())
    myCheckSum=checksum(header+data)
    if sys.platform=='darwin':
        myCheckSum=htons(myCheckSum) & 0xffff
    else:
        myCheckSum= htons(myCheckSum)
    header=struct.pack("bbHHH",ICMP_ECHO_REQUEST,0,myCheckSum,ID,1)

    # Don’t send the packet yet , just return the final packet in this function.
    #Fill in end

    # So the function ending should look like this

    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [] #This is your list to use when iterating through each trace 
    tracelist2 = [] #This is your list to contain all traces
    print("Getting "+hostname+" by Python")

    for ttl in range(1,MAX_HOPS):
        tracelist1.append(str(ttl))
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            #Fill in start
            icmp = getprotobyname("icmp")
            # Make a raw socket named mySocket
            mySocket=socket(AF_INET, SOCK_RAW, icmp)
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    
                    tracelist1.extend(('*',"Request timed out"))
                    #Fill in start
                    tracelist2.append(tracelist1)
                    tracelist1=[]
                    #You should add the list above to your all traces list
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived =str( int((time.time() -startedSelect)*1000))+'ms'
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1.append('*')
                    tracelist1.append("Request timed out")
                    tracelist2.append(tracelist1)
                    tracelist1=[]
                    #Fill in start
                    
                    #Fill in end
            except timeout:
                continue

            else:
                #Fill in start
                icmpHeader=recvPacket[20:28]
                ty, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
                
                types=ty
                #print(addr)
                #print(types)
                #Fetch the icmp type from the IP packet
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    hopHostname = gethostbyaddr(addr[0])[0]
                    #print(hopHostname)
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    # hop#, rtt, hostIP(addr), hostname
                    hopHostname="hostname not returnable"
                    #Fill in end
                
                # Time Exceeded
                if types == 11:
                    #print("Code 11")
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +bytes])[0]
                    #Fill in start
                    tracelist1.append(timeReceived)
                    tracelist1.append(addr[0])
                    tracelist1.append(hopHostname)
                    tracelist2.append(tracelist1)
                    tracelist1=[]
                    #You should add your responses to your lists here
                    #Fill in end
                # Dest unreachable
                elif types == 3: 
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    print("Code 3")
                    tracelist1.append(timeReceived)
                    tracelist1.append(addr[0])
                    tracelist1.append(hopHostname)
                    tracelist2.append(tracelist1)
                    tracelist1=[]
                    #You should add your responses to your lists here 
                    #Fill in end
                # Echo Reply
                elif types == 0:
                    print("Code 0")
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #timeReceived=str(time.time()-timeSent)
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    tracelist1.append(timeReceived)
                    tracelist1.append(addr[0])
                    tracelist1.append(hopHostname)
                    #tracelist1=[]

                    #for item in tracelist1:
                        #print(item)
                    tracelist2.append(tracelist1)
                    #for item in tracelist2:
                        #print(item)
                    if destAddr==addr[0]:
                        #print("FOUND IT")
                        return tracelist2
                    tracelist1=[]
                    #Fill in end
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    tracelist1.append("Error")
                    #Fill in end
                break
            finally:
                #print("Finally")
                #print(tracelist1)
                #print(tracelist2)
                mySocket.close()
                #return tracelist2
    return tracelist2

if __name__ == '__main__':
    pi=get_route("google.co.il")
    print(pi)
    #get_route("portswigger.net")
    pi=get_route("localhost")
    print(pi)
    print(get_route("bing.com"))
    #get_route("no.no.no.e")
