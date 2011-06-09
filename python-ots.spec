Summary: Open Test System 
Name: python-ots
Version: 0.8.6
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
Requires:               python, python-setuptools
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

%package                django
Summary:                OTS django project
Prefix:                 /usr
Group:                  Development/Tools
Requires:               Django, httpd, mod_wsgi
%description            django
OTS django project and applications.

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
Requires:               python-ots-server, python-ots-django
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

%package                plugin-history
Summary:                History plugin to OTS server
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-ots-server, python-ots-django
%description            plugin-history
Test package distribution model based on last execution time.

%package                plugin-monitor
Summary:                Monitor plugin to OTS server
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-ots-server, python-ots-django
%description            plugin-monitor
Statistical information from the OTS system.

%package                plugin-conductor-richcore
Summary:                Rich core processing plugin to OTS worker
Prefix:                 /usr
Group:                  Development/Tools
Requires:               python-ots-worker, python-configobj
%description            plugin-conductor-richcore
Plugin for sending rich-core dumps saved from test runs to post-processing.

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
%config /etc/init.d/ots-worker
/etc/conductor/
/usr/bin/ots_worker
/usr/bin/conductor
/usr/lib/python*/site-packages/ots.worker-*
/usr/lib/python*/site-packages/ots/worker/*

%files django
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.django-*
/usr/lib/python*/site-packages/ots/django/*
/usr/share/ots/django/*

%post django
DIR="/opt/ots/"

if [ ! -d $DIR ]; then
  mkdir $DIR
fi

#SELinux settings
chcon -R -t httpd_user_content_t /opt/ots
setsebool httpd_unified 1

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

%files plugin-qareports
%defattr(-,root,root)
%config /etc/ots_plugin_qareports.conf
/usr/lib/python*/site-packages/ots.plugin.qareports-*
/usr/lib/python*/site-packages/ots/plugin/qareports/*

%files plugin-email
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.plugin.email*
/usr/lib/python*/site-packages/ots/plugin/email/*

%files plugin-history
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.plugin.history-*
/usr/lib/python*/site-packages/ots/plugin/history/*

%files plugin-monitor
%defattr(-,root,root)
/usr/lib/python*/site-packages/ots.plugin.monitor-*
/usr/lib/python*/site-packages/ots/plugin/monitor/*
/usr/share/ots/plugin/monitor/*

%files plugin-conductor-richcore
%defattr(-,root,root)
%config /etc/ots_plugin_conductor_richcore.conf
/usr/lib/python*/site-packages/ots.plugin.conductor.richcore-*
/usr/lib/python*/site-packages/ots/plugin/conductor/richcore/*


