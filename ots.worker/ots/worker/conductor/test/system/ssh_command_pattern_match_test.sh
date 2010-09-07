#!/bin/bash 
sudo /usr/share/autoflash/fbusb-switchbox.sh /dev/ttyUSB0 0 0
sudo /usr/share/autoflash/fbusb-switchbox.sh /dev/ttyUSB0 1 1
python ../../ssh_command_pattern_match.py 
