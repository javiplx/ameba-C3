%{!?dist:%define dist %nil}

Summary: AmebaC3 update agent
Name: amebaC3_client
Version: 1.4.1
Release: 2%{dist}
Source: %{name}-%{version}.tar.gz
License: GPLv2
Group: System/Management

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-root

%description


%define python_site %( %{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()" )

%prep

%setup -q -n %{name}-%{version}

%build

python setup.py build

%install

python setup.py install --root %{buildroot}

mkdir -p %{buildroot}/etc
cat <<EOF > %{buildroot}/etc/aupd.conf
[pull]
check-only = 1
check_cmds = yum check-update
outdated_retcode = 100
update_cmds = yum -y upgrade

[pulldaemon]
random-wait = 180.0
check-interval = 3600.0
check-only = True
EOF

mkdir -p %{buildroot}/etc/init.d
cp ameba-updater %{buildroot}/etc/init.d

%clean
rm -rf %{buildroot}


%post

if [ "$1" = "1" ] ; then
  chkconfig --add ameba-updater
elif [ "$1" = "2" ] ; then
  /etc/init.d/ameba-updater condrestart
  fi

%preun

if [ "$1" = "0" ] ; then
  /etc/init.d/ameba-updater stop
  chkconfig --del ameba-updater
  fi


%files
%defattr(0644,root,root,0755)
%doc README INSTALL license.txt 

%config(noreplace) /etc/aupd.conf

%attr(0755,root,root) /usr/bin/aupd
%attr(0755,root,root) /etc/init.d/ameba-updater

%{python_site}/%{name}
%if "%{dist}" == ".el6"
%{python_site}/%{name}-%{version}-py%{python_version}.egg-info
%endif

%{_defaultdocdir}/%{name}/externals
%{_defaultdocdir}/%{name}/samples

%changelog
* Sat Nov 17 2012 Javier Palacios <javiplx@gmail.com>
- Fixed some errors in response handling
