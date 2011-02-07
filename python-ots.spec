Summary: Open Test System 
Name: python-ots
Version: 0.8.2
Release: 1
Source0: %{name}-%{version}.tar.gz
License: LGPL 2.1
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Prefix: %{_prefix}
BuildArch: noarch
BuildRequires: python-setuptools, python

%description
Open Test System for automatic testing.

%package                common
Summary:                Common libraries for OTS
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python
%description            common
Common libraries for OTS.

%package                results
Summary:                Result libraries for OTS
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python, python-ots-common
%description            results
Result libraries for OTS.

%package                server
Summary:                OTS server
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-amqplib, Django, python-configobj, python-ots-results, test-definition
%description            server
OTS server which handles incoming test requests and
results processing.

%package                worker
Summary:                OTS worker
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-amqplib, python-ots-common, testrunner-lite
%description            worker
OTS worker handles test device control and
test execution.

%package                tools
Summary:                Helping tools for controlling OTS
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-ots-common
%description            tools
Helping tools for controlling OTS.

%package                plugin-logger
Summary:                Logger plugin to OTS server
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-ots-server, httpd, mod_wsgi
%description            plugin-logger
Logger plugin to OTS server.

%package                plugin-qareports
Summary:                MeeGo QA reports plugin to OTS server
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-ots-server
%description            plugin-qareports
MeeGo QA reports plugin to OTS server.

%package                plugin-email
Summary:                Email plugin to OTS server
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-ots-server
%description            plugin-email
Email plugin to OTS server.

%prep
%setup -n %{name}-%{version}

%build
echo "Nothing to be built"

%install
packages=`find . -maxdepth 2 -name setup.py`
for package in $packages; do
    cd `dirname $package`
    python setup.py install --root=$RPM_BUILD_ROOT
    cd -
done

%clean
rm -rf $RPM_BUILD_ROOT

%files common
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.common-*
/usr/lib/python*/site-packages/ots/common/*

%files results
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.results-*
/usr/lib/python*/site-packages/ots/results/*

%files server
%defattr(-,root,root)
%config /etc/ots_server.ini
/usr/bin/ots_server
/usr/lib/python*/site-packages/ots.server-*
/usr/lib/python*/site-packages/ots/server/*

%post server
easy_install minixsv
DIR="/var/log/ots"

if [ ! -d $DIR ]; then
  mkdir $DIR
fi

%files worker
%defattr(-,root,root)
%config /etc/ots.ini
%config /etc/conductor.conf
/etc/conductor/
/usr/bin/ots_worker
/usr/bin/conductor
/usr/lib/python*/site-packages/ots.worker-*
/usr/lib/python*/site-packages/ots/worker/*

%files tools
%defattr(-,root,root)
/usr/bin/ots_delete_queue
/usr/bin/ots_empty_queue
/usr/bin/ots_trigger
/usr/lib/python*/site-packages/ots.tools-*
/usr/lib/python*/site-packages/ots/tools/*

%files plugin-logger
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.plugin.logger-*
/usr/lib/python*/site-packages/ots/plugin/logger/*
/usr/share/ots/plugin/logger/*

%post plugin-logger
DIR="/opt/ots/"

if [ ! -d $DIR ]; then
  mkdir $DIR
fi

#SELinux settings
chcon -R -t httpd_user_content_t /opt/ots
setsebool httpd_unified 1


%files plugin-qareports
%defattr(-,root,root)
%config /etc/ots_plugin_qareports.conf
/usr/lib/python*/site-packages/ots.plugin.qareports-*
/usr/lib/python*/site-packages/ots/plugin/qareports/*

%files plugin-email
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.plugin.email*
/usr/lib/python*/site-packages/ots/plugin/email/*

