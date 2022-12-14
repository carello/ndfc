# NDFC Automation with Python


### *main_v7b.py* is the most recent script

---
---


The purpose of this script is to automate the configuration of NDFC for creating and attaching VRFs, networks and related switchports.

For setup, you'll need to do a few things.

Create environmental variables for your APIC username and password. In a terminal window:
	
	export USER="your username"
	export PASSWORD="your password"

To configure ethernet switchports you'll need to enter those in the file located in ./data/content.py. In this script, there's a section at line 11 called "master_list". Enter in your serial numbers and desired ethernet switchports you'd like to configure. For example:

	master_list = [
	["leaf1", "FDO210518NL", "Ethernet1/21"],
	["leaf2", "FDO20352B5P", ""]
	]
	
You can enter in a switch names too. However, at this time, the name isn't being used.

As far as Python3 is concerned, you'll need the `requests library` and I suggest you run in a `virtualenv`.

Logging is disabled. If you'd like to turn logging on, in the main_v7b.py file change:

	LOGGING_STATUS=True
	

That should be about it. To run:

	python3 main_v7b.py

There are other branches under development. Eventually, those may be merged into the main branch.




