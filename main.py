"""
    This script utilizes the python library of libvirt to display relevant information from the VMs.
    The data displayed are:
    - VM name
    - the VM state
    - allocated CPU number
    - allocated and max memory
    - disks and their source
    - the list of network interfaces with their IP addresses
"""
import sys
from xml.dom import minidom
import libvirt
from constants import VIR_DOMAIN_EVENT_MAPPING, VIR_DOMAIN_STATE_MAPPING, KB_to_MB_FACTOR


# registers default event implmenentation
libvirt.virEventRegisterDefaultImpl()


def diplay_info(_conn, dom, event, _detail, _opaque):
    """
    displays the required information using the libvirt library
    :param dom: domain object currently in use
    :param event: the event triggered
    :return: prints the information
    """
    if event in (libvirt.VIR_DOMAIN_EVENT_STARTED, libvirt.VIR_DOMAIN_EVENT_STOPPED):
        print("")
        print("=-" * 25)
        state, maxmem, mem, cpus, _cput = dom.info()
        print("name: " + dom.name())
        print("event: " + VIR_DOMAIN_EVENT_MAPPING.get(event, "?"))
        print("state: " + VIR_DOMAIN_STATE_MAPPING.get(state, "?"))
        print("cpus: " + str(cpus))
        print("memory: " + str(mem * KB_to_MB_FACTOR))
        print("max memory: " + str(maxmem * KB_to_MB_FACTOR))

        raw_xml = dom.XMLDesc(0)
        xml = minidom.parseString(raw_xml)
        disk_types = xml.getElementsByTagName('disk')
        for disk_type in disk_types:
            print('disk: type='+disk_type.getAttribute('type') +
                  ' device='+disk_type.getAttribute('device'))
            disk_nodes = disk_type.childNodes
            for disk_node in disk_nodes:
                if disk_node.nodeName[0:1] != '#' and disk_node.nodeName == "source":
                    for attr in disk_node.attributes.keys():
                        print(
                            'disk: ' + disk_node.attributes[attr].name
                            + disk_node.attributes[attr].value)

        ifaces = dom.interfaceAddresses(
            libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        print("IP Address: ")
        for (_, val) in ifaces.items():
            if val['addrs']:
                for ipaddr in val['addrs']:
                    if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                        print(ipaddr['addr'] + " VIR_IP_ADDR_TYPE_IPV4")
                    elif ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV6:
                        print(ipaddr['addr'] + " VIR_IP_ADDR_TYPE_IPV6")

        print("=-" * 25)


def register_events(conn):
    """
    add callback to receive notifications of arbitary domain events occuring on a domain
    """
    conn.domainEventRegisterAny(
        None,
        libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
        diplay_info,
        conn)


# setup connection
CONN = libvirt.open("qemu:///system")

if CONN is None:
    print('Failed to open connection to the hypervisor')
    sys.exit(1)

# register events
register_events(CONN)

# event loop
while True:
    # process events
    libvirt.virEventRunDefaultImpl()

sys.exit(0)
