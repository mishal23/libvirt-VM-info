# libvirt-VM-info

Listens for libvirt events and displays the relevant information of the VM.

The information displayed is:
- VM name
- the VM state
- allocated CPU number
- allocated and max memory
- disks and their source
- the list of network interfaces with their IP addresses

## Implementation

- The code is written in Python using the `libvirt-python` library.
- The **VIR_DOMAIN_EVENT_MAPPING** and **VIR_DOMAIN_STATE_MAPPING** in `constants.py` file is based on the enum defined in libvirt codebase in ```include/libvirt/libvirt-domain.h``` files. (Source [L51](https://github.com/libvirt/libvirt/blob/master/include/libvirt/libvirt-domain.h#L51), [L3014](https://github.com/libvirt/libvirt/blob/master/include/libvirt/libvirt-domain.h#L3014))
- A default event is registered and ```virEventRunDefaultImpl()``` is invoked in a loop to process events. [source](https://libvirt.org/html/libvirt-libvirt-event.html#virEventRegisterDefaultImpl)
- A callback ```domainEventRegisterAny``` is added to receive notification on any event, upon which the relevant information is displayed.
- The information is displayed following the documentation of the library.

## Installation Instructions

Make sure your system supports Virtualization

```bash
- sudo apt install qemu qemu-kvm libvirt-bin bridge-utils virt-manager
- sudo service libvirtd start
- sudo update-rc.d libvirtd enable
- sudo nano /etc/netplan/01-netcfg.yaml
```
Add the following:
```
network:
    ethernets:
        ens33:
            addresses: [192.168.0.51/24]
            gateway4: 192.168.0.1
            nameservers:
              addresses: [192.168.0.1]
            dhcp4: no
            optional: true
    version: 2
```
```
- sudo netplan apply
- sudo pip install libvirt-python
```

Detailed instructions on installation: [here](https://www.linuxtechi.com/install-configure-kvm-ubuntu-18-04-server/) 

## Steps to Run

- Spin a VM to test the code, I installed Ubuntu18.04 without graphics, feel free to use any.

```bash
sudo virt-install \
--name falcon \
--description "Test VM with Ubuntu" \
--os-type Linux \
--os-variant ubuntu18.04 \
--ram 1024 \
--vcpus 1 \
--disk path=/var/lib/libvirt/images/falcon1.img,size=8 \
--graphics none \
--location 'http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/' \
--extra-args "console=ttyS0,115200n8"
```
- Follow the steps on the terminal to complete the installation of the OS on the VM
- Check if it's correctly setup using: ```sudo virsh list --all```

```bash
- git clone https://github.com/mishal23/libvirt-VM-info
- sudo python main.py
```
- On another terminal invoke any event for the VM and it'll display the information.
