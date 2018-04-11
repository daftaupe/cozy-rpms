%define debug_package %{nil}

Name:           cozy-couchdb
Version:        2.1.1
Release:        0%{?dist}
Summary:        CouchDB for cozy

Group:          Applications/System
License:        Apache-2.0
URL:            https://couchdb.apache.org/
Source0:        https://apache.mediamirrors.org/couchdb/source/%{version}/apache-couchdb-%{version}.tar.gz

AutoReq:        no 
AutoReqProv:    no 

BuildRequires:  autoconf autoconf-archive automake  curl-devel erlang-asn1 erlang-erts erlang-eunit gcc-c++ erlang-os_mon erlang-reltool erlang-xmerl erlang-erl_interface help2man js-devel libicu-devel libtool perl-Test-Harness

Requires:       libicu js

%description

%prep
%autosetup -n apache-couchdb-%{version}

%build
./configure
make release

%install
mkdir -p %{buildroot}/home
mkdir -p %{buildroot}/etc/systemd/system
mv rel/couchdb %{buildroot}/home/couchdb
cat << EOF > %{buildroot}/etc/systemd/system/couchdb.service
[Unit]
Description=CouchDB service
After=network.target

[Service]
Type=simple
User=couchdb
ExecStart=/home/couchdb/bin/couchdb -o /dev/stdout -e /dev/stderr
Restart=always

[Install]
WantedBy=multi-user.target
EOF

%pre
useradd couchdb

%post
chown -R couchdb: /home/couchdb
find /home/couchdb -type d -exec chmod 0770 {} \;
chmod -R 0644 /home/couchdb/etc/*
systemctl daemon-reload

%preun
if [ "$1" = 0 ] ; then 
    systemctl stop couchdb
    systemctl disable couchdb
fi

%postun
if [ "$1" = 0 ] ; then 
    mv /home/couchdb /home/couchdb-bkp
    userdel -f couchdb
fi

%files
/home/couchdb/bin/
/home/couchdb/erts-*
/home/couchdb/etc/default.d
/home/couchdb/etc/local.d
/home/couchdb/lib/
/home/couchdb/releases/
/home/couchdb/share/
/home/couchdb/var/
/etc/systemd/system/couchdb.service
%license /home/couchdb/LICENSE
%config /home/couchdb/etc/default.ini
%config /home/couchdb/etc/local.ini
%config /home/couchdb/etc/vm.args

%changelog
* Mon Mar 26 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 2.1.1-0
- Inital rpm for release 2.1.1
