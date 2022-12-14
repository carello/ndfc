""" Module to extract dictionaries for 'device:serial' and 'serial:swithports' """

# Create a nested list for device, serial and ethernet ports. This can be manual as done here
# or via sources (ie, spreadsheets) and scripting to extract the data in this format.

master_list = [
["leaf1", "AAAAAAAA", "Ethernet1/1"],
["leaf2", "BBBBDDDD", "Ethernet1/2,Ethernet1/16"],
["leaf3", "CCCCEEEE", "Ethernet1/1"],
["leaf4", "DDDDFFFD", ""],
["leaf5", "EEEEABAB", "Ethernet1/25,Ethernet1/26,Ethernet1/27"]
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
