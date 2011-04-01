# -*-mic2-options-*- -f loop --save-kernel  -*-mic2-options-*-

lang en_US.UTF-8
keyboard us
timezone --utc America/Los_Angeles
auth --useshadow --enablemd5
part / --size 1700 --ondisk sda --fstype=ext3
rootpw meego 
xconfig --startxonboot
bootloader --timeout=0 --append="quiet"
desktop --autologinuser=meego  --defaultdesktop=DUI --session="/usr/bin/mcompositor"
user --name meego  --groups audio,video --password meego 

repo --name=oss     --baseurl=http://download.meego.com/snapshots/1.1.99.0.20110329.5/repos/oss/ia32/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego
repo --name=non-oss  --baseurl=http://download.meego.com/snapshots/1.1.99.0.20110329.5/repos/non-oss/ia32/packages/ --save --debuginfo --source --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego
repo --name=devel-quality  --baseurl=http://download.meego.com/live/devel:/quality/testing/ --save --gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego

%packages 
@MeeGo Core
@MeeGo Compliance

kernel
bash
libxml2
zypper

test-definition-tests
testrunner-lite-regression-tests

%end
%post

# save a little bit of space at least...
rm -f /boot/initrd*

# make sure there aren't core files lying around
rm -f /core*

# Prelink can reduce boot time
if [ -x /usr/sbin/prelink ]; then
    /usr/sbin/prelink -aRqm
fi

# work around for poor key import UI in PackageKit
rm -f /var/lib/rpm/__db*
rpm --rebuilddb

%end

%post --nochroot
if [ -n "$IMG_NAME" ]; then
    echo "BUILD: $IMG_NAME" >> $INSTALL_ROOT/etc/meego-release
fi
%end
