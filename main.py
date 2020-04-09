import libvirt
import sys
from constants import VIR_DOMAIN_EVENT_MAPPING, VIR_DOMAIN_STATE_MAPPING
from xml.dom import minidom
from prettytable import PrettyTable
import logging

# registers default event implmenentation
libvirt.virEventRegisterDefaultImpl()


def diplay_info(conn, dom, event, detail, opaque):
    if event == 2 or event == 5:
        print("")
        print("=-" * 25)
        t = PrettyTable(['Name', 'Value'])
        state, maxmem, mem, cpus, cput = dom.info()
        t.add_row(['name', dom.name()])
        t.add_row(['event', VIR_DOMAIN_EVENT_MAPPING.get(event, "?")])
        t.add_row(['state', VIR_DOMAIN_STATE_MAPPING.get(state, "?")])
        t.add_row(['cpus', str(cpus)])
        t.add_row(['memory', str(mem*0.001)])
        t.add_row(['max memory', str(maxmem*0.001)])

        raw_xml = dom.XMLDesc(0)
        xml = minidom.parseString(raw_xml)
        diskTypes = xml.getElementsByTagName('disk')
        for diskType in diskTypes:
            print('disk: type='+diskType.getAttribute('type')+' device='+diskType.getAttribute('device'))
            diskNodes = diskType.childNodes
            for diskNode in diskNodes:
                if diskNode.nodeName[0:1] != '#' and diskNode.nodeName == "source":
                    for attr in diskNode.attributes.keys():
                        t.add_row(['disk: ' + diskNode.attributes[attr].name, diskNode.attributes[attr].value])

        print(t)
        # interfaceTypes = xml.getElementsByTagName('interface')
        # for interfaceType in interfaceTypes:
        #     print('interface: type='+interfaceType.getAttribute('type'))
        #     interfaceNodes = interfaceType.childNodes
        #     for interfaceNode in interfaceNodes:
        #         if interfaceNode.nodeName[0:1] != '#':
        #             print(' '+interfaceNode.nodeName)
        #             for attr in interfaceNode.attributes.keys():
        #                 print(' '+interfaceNode.attributes[attr].name+' = '+interfaceNode.attributes[attr].value)

        ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        print(ifaces)
        print("IP Address: ")
        for (name, val) in ifaces.iteritems():
            if val['addrs']:
                for ipaddr in val['addrs']:
                    if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                        print(ipaddr['addr'] + " VIR_IP_ADDR_TYPE_IPV4")
                    elif ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV6:
                        print(ipaddr['addr'] + " VIR_IP_ADDR_TYPE_IPV6")
        
        print("=-" * 25)


def register_events(conn):
    # add callback to receive notifications of arbitary domain events occuring on a domain
    conn.domainEventRegisterAny(
        None,
        libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
        diplay_info,
        conn)


# setup connection
conn = libvirt.open("qemu:///system")

if conn == None:
    print('Failed to open connection to the hypervisor')
    sys.exit(1)

# register events
register_events(conn)

# event loop
while True:
    # process events
    libvirt.virEventRunDefaultImpl()

sys.exit(0)