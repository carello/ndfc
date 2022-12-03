
# This is working without __init__.py
# Let's try __init__.py

# Can do this either way. The second option has more control 'from data.data import hello'
# The first one 'from data import data' imports the whole file, then I'd use data.hello()

# OPTION A (very flexible)
'''
from data import data

data.hello()
print()
data.display_master_list(data.master_list)
print()

dev_ser = data.dev_serial(data.master_list)
data.display_dev_ser(dev_ser)

print()
ser_swports = data.serial_switchports(data.master_list)
data.display_serial_switchports(ser_swports)
'''

#OPTION B (very restrictive but probably safer)
from data.data import hello, display_master_list, master_list, \
    serial_switchports, display_serial_switchports

hello()
display_master_list(master_list)

print()
ser_swports = serial_switchports(master_list)
display_serial_switchports(ser_swports)
