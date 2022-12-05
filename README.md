# ndfc

Branch DEV2

Branch DEV1 has been merged into main. Started a new branch (DEV2) from main

main_v6.py is the most recent and robust version of this script. It includes error checking, logging and references a module for the "data". The idea here is that data could end of being very large and having this in a separate module will scale better and provide flexiblity on sourcing the data from external sources. ie: csv files.

main_v5.py doesn't reference external data module. Also it doesn't have much in terms of error checking and no logging. Probably best to not use this version.

DEV2 is merged with main. 12/5/22 @ 4:15pm

