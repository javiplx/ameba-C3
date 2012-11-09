%{!?dist:%define dist %nil}

Summary: AmebaC3 update agent
Name: amebaC3_client
Version: 1.4
Release: 1%{dist}
Source: %{name}-%{version}.tar.gz
License: GPLv2
Group: System/Management

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-root

%description


%define python_site %( %{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()" )

%prep

%setup -q -n %{name}-1.4

%build

python setup.py build

%install

python setup.py install --root %{buildroot}

mkdir -p %{buildroot}/etc
cat <<EOF > %{buildroot}/etc/aupd.conf
[yum-pull]
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


%files
%defattr(0644,root,root,0755)
%doc README INSTALL license.txt 

%config(noreplace) /etc/aupd.conf

%attr(0755,root,root) /usr/bin/aupd
%attr(0755,root,root) /etc/init.d/ameba-updater

%{python_site}/%{name}

%{_defaultdocdir}/%{name}/externals
%{_defaultdocdir}/%{name}/samples

