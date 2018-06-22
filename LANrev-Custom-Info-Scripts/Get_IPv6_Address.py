#!/usr/bin/python

import os, subprocess

def bashCommand(script):
    try:
        return subprocess.check_output(script)
    except (subprocess.CalledProcessError, OSError), err:
        return "[* Error] **%s** [%s]" % (err, str(script))

network_output = bashCommand(["/usr/sbin/system_profiler", "SPNetworkDataType"])

network_list = network_output.splitlines()
interface_list = []
for item in network_list:
    if "BSD Device Name: " in item:
        interface = item.replace("      BSD Device Name: ", "")
        interface_list.append(interface)

for interface in interface_list:
    try:
        interface_output = subprocess.check_output(["/sbin/ifconfig", interface], stderr=subprocess.STDOUT)
        if "inet6" in interface_output:
            interface_output = interface_output.splitlines()
            for line in interface_output:
                if "inet6" in line:
                    line = line.replace("   inet6 ", "")
                    line = line.split(" ")[0]
                    if not "fe80" in line:
                        IPv6_address = line
                        print IPv6_address
    except:
        pass