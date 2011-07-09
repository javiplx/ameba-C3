%{!?dist:%define dist %nil}

Summary: AmebaC3 server
Name: amebaC3
Version: 1.0.99
Release: 1%{dist}
Source: %{name}-%{version}.tar.gz
License: GPLv2
Group: System/Management

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-root

Requires: mod_python , nagios , nagios-plugins

%description


%define python_site %( %{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()" )

%prep

%setup -q -n %{name}-1.1

%build

python setup.py build

%install

python setup.py install --root %{buildroot}

mkdir -p %{buildroot}/etc/httpd/conf.d
cp amebaC3_httpd_sample.conf %{buildroot}/etc/httpd/conf.d/amebaC3.conf

mkdir -p %{buildroot}/etc/nagios/amebaC3
cp callbacks/amebaC3_templates.cfg %{buildroot}/etc/nagios/amebaC3

mkdir -p %{buildroot}/usr/lib/nagios/plugins
cp callbacks/ameba_freshness_exceeded.sh %{buildroot}/usr/lib/nagios/plugins

mkdir -p %{buildroot}/var/lib/amebaC3

%clean
rm -rf %{buildroot}


%files
%defattr(0644,root,root,0755)
%doc INSTALL license.txt
%doc deployment.txt

%config /etc/httpd/conf.d/amebaC3.conf

%dir /etc/nagios/amebaC3
%config /etc/nagios/amebaC3/amebaC3_templates.cfg

%{python_site}/%{name}

%attr(0755,root,root) /usr/lib/nagios/plugins/ameba_freshness_exceeded.sh

%dir %attr(0755,apache,apache) /var/lib/amebaC3
