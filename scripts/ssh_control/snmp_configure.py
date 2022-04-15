#!/usr/bin/env python3

import os

def install_mibs():
    """
    Install snmp-mibs-downloader package
    """
    os.system("sudo apt update")
    os.system("sudo apt install ./snmp-mibs-downloader_1.2_all.deb")
    return os.system("sudo apt install -f")

def configure_snmpd_conf():
    """
    Add view rocommunity agentAddress and extend command to snmpd.conf
    """
    #os.system("sudo cp /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.orig") - saving original snmpd.conf file
    
    f = open('/etc/snmp/snmpd.conf', 'r')

    new_conf = ''

    for line in f.readlines():
        if 'access control' in line.lower():
            new_conf += line
            new_conf += 'view all included .1\nrocommunity ssh_enable default\n'
        elif 'agentAddress  udp:127.0.0.1:161' in line.lower():
            new_line += '#agentAddress  udp:127.0.0.1:161\n'
            new_conf += 'agentAddress udp:161,udp6:[::1]:161\n'
        else:
            new_conf += line
    
    new_conf += 'extend ssh_enable /usr/local/bin/ssh_enable.sh\n'
    
    f.close()
    f = open('/etc/snmp/snmpd.conf', 'w')
    f.write(new_conf)
    f.close()

def configure_sudoers():
    """
    Add Debian-snmp to sudoers to run systemctl start ssh without password
    """
    #os.system("sudo cp /etc/sudoers /etc/sudoers.orig") - saving original sudoers file 
    
    f = open('/etc/sudoers', 'a')
    f.write('\nDebian-snmp ALL=(ALL) NOPASSWD: /bin/systemctl start ssh\n')
    f.close()

def add_script():
    """
    add activating to usr/local/bin (probably it should be at /home/aadmin/setup/scripts)
    """
    f = open('/usr/local/bin/ssh_enable.sh', 'w')
    
    script = "#!/bin/bash\n\
echo activating ssh\n\
sudo systemctl start ssh\n"
    
    f.write(script)
    
    f.close()
    
    os.system("sudo chmod +x /usr/local/bin/ssh_enable.sh")
    
def main():
    add_script()
    configure_snmpd_conf()
    configure_sudoers()
    if install_mibs() != 0:
        print(
            "Try install snmp_mibs_downloader, \
            package snmp_mibs_downloader wasn't installed"
        )

if __name__ == "__main__":
    main()
    
