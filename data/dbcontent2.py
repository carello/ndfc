""" Module to extract dictionaries for 'device:serial' and 'serial:swithports' """

__version__ = "0.2"

# dbcontent2.py
#
# this version changes the master_list to use a dictionary with a list:
#  {SERIAL: ["name", "switchports, switchport, switchports etc..."]}
# This would simplify the code in main-X.py
# For reference:
#     "ev-leaf1": "FDO210518NL"
#     "ev-leaf2": "FDO20352B5P"

master_list = {
    "FDO210518NL": ["ev-leaf1", "Ethernet1/31,Ethernet1/3"],
    "FDO20352B5P": ["ev-leaf2", "Ethernet1/22"]
}


# Extract serial number and switch ports and place into a dictionary
def serial_switchports(mlist):
    """ Extract serial number and swithports and place into a dictionary """

    serial_swports = {}
    for ser, ports in mlist.items():
        serial_swports[ser] = ports[1]

    return serial_swports


# Using dictionary comprehension alternative.
def serial_switchports_comp(mlist):
    """Extract serial number and swithports and place into a dictionary \
        using dictionary comprehension"""

    serial_swports2 = {ser:ports[1] for ser, ports in mlist.items()}
    return serial_swports2


# Extract serial number and Device name and place into a dictionary
def serial_device_name(mlist):
    """ Extract serial number and swithports and place into a dictionary """

    serial_name = {}
    for ser, name in mlist.items():
        serial_name[ser] = name[0]

    return serial_name


# Display Serial and Switchport infomration
def display_serial_switchports(display):
    """Display Serial nums and Ethernet switch ports."""

    for serial, ports in display.items():
        print(f"Serial: {serial} \t Ports: {ports}")


# Display Serial and Switchport infomration using dictionary comprehension
def display_serial_switchports_comp(display):
    """Display Serial and Switchport information using dictionary comprehension"""

    print({serial:ports for serial, ports in display.items()})


# Display Serial and Device name
def display_serial_name(display):
    """Display Serial nums and Device name"""

    for serial, name in display.items():
        print(f"Serial: {serial} \t Name: {name}")


# Display Master List
def display_master_list(display):
    """ Display master list """

    for serial, device_items in display.items():
        print(serial, device_items)

# TEST: Display serial only
def display_serial_switchports2(display):
    """Display Serial nums and Ethernet switch ports."""

    for serial in display:
        print(f"Serial: {serial}")

# TEST: Display switchports only
def display_serial_switchports3(display):
    """Display Serial nums and Ethernet switch ports."""

    for serial in display.items():
        print(f"Switchports: {serial[1]}")



if __name__ == '__main__':
    # Extract and Display
    #ser_swports = serial_switchports(master_list)
    #ser_name = serial_device_name(master_list)
    #print()
    #display_serial_switchports(ser_swports)
    #print()
    #display_serial_name(ser_name)
    #print()
    #display_serial_switchports2(ser_swports)
    #print()
    #display_serial_switchports3(ser_swports)
    #print()
    #display_master_list(master_list)
    #print()
    ser_swports_comp = serial_switchports_comp(master_list)
    display_serial_switchports_comp(ser_swports_comp)



############################################
############################################
# below is the code from version 0.1

'''
master_list = [
["ev-leaf1", "FDO210518NL", "Ethernet1/31"],
["ev-leaf2", "FDO20352B5P", "Ethernet1/31"]
]

# Iterate over 'serial_switchports', extract Serial number and ports into a dictionary
def serial_switchports(mlist):
    """ Extract serial number and swithports and place into a dictionary """

    serial_swports = {}
    for item in mlist:
        serial_swports[item[1]] = item[2]

    return serial_swports


# Display Serial and Switchport infomration
def display_serial_switchports(display):
    """ Display Serial nums and Ethernet switch ports """

    for serial,ports in display.items():
        print(f"Serial: {serial} \t Ports: {ports}")


# Iterate over 'device_serial', extract Device and Serial number dictionary
def dev_serial(mlist):
    """ Extract device name and serial number and place into a dictionary """

    device_ser = {}
    for item in mlist:
        device_ser[item[0]] = item[1]

    return device_ser


# Display Device and Serial information
def display_dev_ser(display):
    """ Display Serial nums and Ethernet switch ports """

    for serial,ports in display.items():
        print(f"Device: {serial} \t Serial: {ports}")


# Display Master List
def display_master_list(display):
    """ Display master list """

    for item in display:
        print(item)


def hello():
    """ Testing function """
    print("Hello ")


if __name__ == '__main__':
    print()
    dev_ser = dev_serial(master_list)
    display_dev_ser(dev_ser)
    print()
    ser_swports = serial_switchports(master_list)
    display_serial_switchports(ser_swports)
    print()
    display_master_list(master_list)
'''
