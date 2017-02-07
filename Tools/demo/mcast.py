#!/usr/bin/env python3

"""
Send/receive UDP multicast packets.
Requires that your OS kernel supports IP multicast.

Usage:
  mcast -s (sender, IPv4)
  mcast -s -6 (sender, IPv6)
  mcast    (receivers, IPv4)
  mcast  -6  (receivers, IPv6)
"""

MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
MYTTL = 1 # Increase to reach other networks

zaimportuj time
zaimportuj struct
zaimportuj socket
zaimportuj sys

def main():
    group = MYGROUP_6 jeżeli "-6" w sys.argv[1:] inaczej MYGROUP_4

    jeżeli "-s" w sys.argv[1:]:
        sender(group)
    inaczej:
        receiver(group)


def sender(group):
    addrinfo = socket.getaddrinfo(group, Nic)[0]

    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Set Time-to-live (optional)
    ttl_bin = struct.pack('@i', MYTTL)
    jeżeli addrinfo[0] == socket.AF_INET: # IPv4
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    inaczej:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)

    dopóki Prawda:
        data = repr(time.time()).encode('utf-8') + b'\0'
        s.sendto(data, (addrinfo[4][0], MYPORT))
        time.sleep(1)


def receiver(group):
    # Look up multicast group address w name server oraz find out IP version
    addrinfo = socket.getaddrinfo(group, Nic)[0]

    # Create a socket
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (nie strictly needed)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind it to the port
    s.bind(('', MYPORT))

    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    # Join group
    jeżeli addrinfo[0] == socket.AF_INET: # IPv4
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    inaczej:
        mreq = group_bin + struct.pack('@I', 0)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    # Loop, printing any data we receive
    dopóki Prawda:
        data, sender = s.recvfrom(1500)
        dopóki data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
        print(str(sender) + '  ' + repr(data))


jeżeli __name__ == '__main__':
    main()
