import libvirt
import sys
from constants import VIR_DOMAIN_EVENT_MAPPING, VIR_DOMAIN_STATE_MAPPING
from xml.dom import minidom

# registers default event implmenentation
libvirt.virEventRegisterDefaultImpl()


def diplay_info(conn, dom, event, detail, opaque):
    dom_conn = conn.lookupByName(dom.name())
    print("")
    print("=-" * 25)
    state, maxmem, mem, cpus, cput = dom.info()

    print("name: " + dom.name())
    print("event: " + VIR_DOMAIN_EVENT_MAPPING.get(event, "?"), event)
    print("state: " + VIR_DOMAIN_STATE_MAPPING.get(state, "?"))
    print("cpus: " + str(cpus))
    print("memory: " + str(mem*0.001))
    print("max memory: " + str(maxmem*0.001))

    raw_xml = dom.XMLDesc(0)
    xml = minidom.parseString(raw_xml)
    diskTypes = xml.getElementsByTagName('disk')
    for diskType in diskTypes:
        print('disk: type='+diskType.getAttribute('type')+' device='+diskType.getAttribute('device'))
        diskNodes = diskType.childNodes
        for diskNode in diskNodes:
            if diskNode.nodeName[0:1] != '#':
                print(' '+diskNode.nodeName)
                for attr in diskNode.attributes.keys():
                    print(' '+diskNode.attributes[attr].name+' = '+diskNode.attributes[attr].value)

    interfaceTypes = xml.getElementsByTagName('interface')
    for interfaceType in interfaceTypes:
        print('interface: type='+interfaceType.getAttribute('type'))
        interfaceNodes = interfaceType.childNodes
        for interfaceNode in interfaceNodes:
            if interfaceNode.nodeName[0:1] != '#':
                print(' '+interfaceNode.nodeName)
                for attr in interfaceNode.attributes.keys():
                    print(' '+interfaceNode.attributes[attr].name+' = '+interfaceNode.attributes[attr].value)

    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
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
conn=libvirt.open("qemu:///system")

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