# -*-mic2-options-*- -f raw --save-kernel --arch=armv7l -*-mic2-options-*-

lang en_US.UTF-8
keyboard us
timezone --utc America/Los_Angeles
part / --size=1750  --ondisk mmcblk0p --fstype=ext3

# This is not used currently. It is here because the /boot partition
# needs to be the partition number 3 for the u-boot usage.
part swap --size=8 --ondisk mmcblk0p --fstype=swap

# This partition is made so that u-boot can find the kernel
part /boot --size=32 --ondisk mmcblk0p --fstype=vfat

rootpw meego 
xconfig --startxonboot
desktop --autologinuser=meego  --defaultdesktop=DUI --session="/usr/bin/mcompositor"
user --name meego  --groups audio,video --password meego 

repo --name=core     --baseurl=http://repo.meego.com/MeeGo/builds/trunk/latest/repos/oss/armv7l/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego
repo --name=non-oss  --baseurl=http://repo.meego.com/MeeGo/builds/trunk/latest/repos/non-oss/armv7l/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego

repo --name=devel-quality --baseurl=http://download.meego.com/live/devel:/quality/testing/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego
repo --name=devel-quality-tests --baseurl=http://download.meego.com/live/devel:/quality:/tests/Trunk/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego
repo --name=extra-trunk --baseurl=http://download.meego.com/live/Trunk:/Extra/Trunk/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego


%packages

@MeeGo Compliance
@MeeGo Core
@X for Handsets
@MeeGo Handset Desktop
@MeeGo Handset Applications
@MeeGo Base Development
@Minimal MeeGo X Window System
@Nokia N900 Support
@Nokia N900 Proprietary Support

kernel-adaptation-n900

xorg-x11-utils-xev

# Test automations enablers
eat-device
eat-syslog-device

test-definition-tests
testrunner-lite-regression-tests

%end

%post

# save a little bit of space at least...
rm -f /boot/initrd*

# make sure there aren't core files lying around
rm -f /core*


# Remove cursor from showing during startup BMC#14991
echo "xopts=-nocursor" >> /etc/sysconfig/uxlaunch


# open serial line console for embedded system
echo "s0:235:respawn:/sbin/agetty -L 115200 ttyO2 vt100" >> /etc/inittab


# work around for poor key import UI in PackageKit
rm -f /var/lib/rpm/__db*
rpm --rebuilddb


# Set up proper target for libmeegotouch
Config_Src=`gconftool-2 --get-default-source`
gconftool-2 --direct --config-source $Config_Src \
  -s -t string /meegotouch/target/name N900


# Normal bootchart is only 30 long so we use this to get longer bootchart during startup when needed.
cat > /sbin/bootchartd-long << EOF
#!/bin/sh
exec /sbin/bootchartd -n 4000
EOF
chmod +x /sbin/bootchartd-long


# Use eMMC swap partition as MeeGo swap as well.
# Because of the 2nd partition is swap for the partition numbering
# we can just change the current fstab entry to match the eMMC partition.
sed -i 's/mmcblk0p2/mmcblk1p3/g' /etc/fstab



%end

%post --nochroot
if [ -n "$IMG_NAME" ]; then
    echo "BUILD: $IMG_NAME" >> $INSTALL_ROOT/etc/meego-release
fi



%end
