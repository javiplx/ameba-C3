%{!?dist:%define dist %nil}

Summary: AmebaC3 server
Name: amebaC3
Version: 1.0.99
Release: 1%{dist}
Source: %{name}-%{version}.tar.gz
Patch: rhel62.patch
License: GPLv2
Group: System/Management

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-root

Requires: mod_python
Requires: nagios , nagios-plugins
Requires: rrdUtils >= 5.5

%description


%define python_site %( %{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()" )

%prep

%setup -q -n %{name}-1.1
%if "%{dist}" == ".el6"
%patch -p1
%endif


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

%attr(0755,apache,apache) %dir /etc/nagios/amebaC3
%attr(0644,apache,apache) %config /etc/nagios/amebaC3/amebaC3_templates.cfg

%{python_site}/%{name}
%if "%{dist}" == ".el6"
%{python_site}/%{name}-%{version}-py%{python_version}.egg-info
%endif

%attr(0755,root,root) /usr/lib/nagios/plugins/ameba_freshness_exceeded.sh

%dir %attr(0755,apache,apache) /var/lib/amebaC3
