""" Module to extract dictionaries for 'device:serial' and 'serial:swithports' """

# Create a nested list for device, serial and ethernet ports. This can be manual as done here
# or via sources (ie, spreadsheets) and scripting to extract the data in this format.

# For reference
# "ev-leaf1": "FDO210518NL"
# "ev-leaf2": "FDO20352B5P"
#    

# Enter your switch serial numbers and ethernet ports. The name is optional at this time
master_list = [
["leaf1", "FDO210518NL", "Ethernet1/21,Ethernet1/30"],
["leaf2", "FDO20352B5P", ""]
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





# *** Misc stuff for testing, delete eventually ***
###################################################
#mylist2 = ["leaf1", "AAAAAAAA", "Ethernet1/1"]
##print(mylist2[1])
#for i in mylist2:
#    #print(mylist2[0])
#    mydict[mylist2[1]] = mylist2[2]

# Print out just switchports
#for ports in serial_switchports.values():
#    print("\n", ports)
