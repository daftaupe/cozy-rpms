%define debug_package %{nil}
%define repo github.com/cozy/cozy-stack

Name:           cozy-stack
Version:        2018M2S1
Release:        1%{?dist}
Summary:        Cozy: Simple, Versatile, Yours

Group:          Applications/System
License:        AGPLv3
URL:            https://%{repo}
Source0:        https://apt.cozy.io/debian/pool/testing/c/%{name}/%{name}_%{version}.orig.tar.xz
Source1:        https://raw.githubusercontent.com/cozy/%{name}/master/cozy.example.yaml

AutoReq:        no
AutoReqProv:    no

BuildRequires:  git golang systemd

%description
Cozy: Simple, Versatile, Yours
Cozy (https://cozy.io) is a platform that brings all your web services
in the same private space.
This package installs the cozy stack.

%prep
%autosetup -n %{name}

%build
export GOPATH="$(pwd)"
export PATH=$PATH:"$(pwd)"/bin
cd src/%{repo}
COZY_ENV=production GOOS=linux GOARCH=amd64 VERSION_STRING=prod ./scripts/build.sh install

%install
mkdir -p %{buildroot}%{_bindir}
cp bin/%{name} %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datarootdir}/cozy
cp src/%{repo}/scripts/konnector-node-run.sh %{buildroot}%{_datarootdir}/cozy
cp src/%{repo}/scripts/konnector-nsjail-run.sh %{buildroot}%{_datarootdir}/cozy
cp src/%{repo}/scripts/konnector-rkt-run.sh %{buildroot}%{_datarootdir}/cozy
mkdir -p %{buildroot}%{_unitdir}
cat << EOF > %{buildroot}%{_unitdir}/%{name}.service
[Unit]
Description=Cozy service
Wants=couchdb.service
After=network.target couchdb.service

[Service]
User=cozy
Group=cozy
PermissionsStartOnly=true
ExecStart=/usr/bin/cozy-stack serve
Restart=always

[Install]
WantedBy=multi-user.target
EOF
mkdir -p %{buildroot}%{_sysconfdir}/cozy
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/cozy/cozy.yaml
sed -i 's@# url: file://localhost/var/lib/cozy@url: file://localhost/var/lib/cozy@;s@/path/to/key.enc@/var/lib/cozy/keys/key.enc@;s@/path/to/key.dec@/var/lib/cozy/keys/key.dec@;s@cmd: ./scripts@cmd: %{_datarootdir}/cozy@g' %{buildroot}%{_sysconfdir}/cozy/cozy.yaml

%pre

%post
if [ "$1" = 1 ]; then
	groupadd --system cozy
	useradd --system --gid cozy -d /var/lib/cozy -s /sbin/nologin cozy
	chown cozy: -R /etc/cozy
	mkdir -p /var/lib/cozy/keys && chown cozy: -R /var/lib/cozy
	chmod 700 /var/lib/cozy/keys
	mkdir -p /var/log/cozy && chown cozy: /var/log/cozy
	su - cozy -s /bin/bash -c "cozy-stack config gen-keys /var/lib/cozy/keys/key &> /dev/null"
fi

if [ "$1" = 2 ]; then
    systemctl daemon-reload
    if systemctl is-enabled cozy-stack &>/dev/null || systemctl is-active cozy-stack &>/dev/null ; then
        systemctl restart cozy-stack
    fi
fi

%preun
if [ "$1" = 0 ]; then 
    if systemctl is-enabled cozy-stack &>/dev/null || systemctl is-active cozy-stack &>/dev/null ; then
    	systemctl stop cozy-stack
    	systemctl disable cozy-stack
	fi
fi

%postun
if [ "$1" = 0 ]; then
    mv /var/lib/cozy /var/lib/cozy.bkp
    userdel -f cozy
    systemctl daemon-reload
fi

%files
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/cozy/cozy.yaml
%{_datarootdir}/cozy/konnector-node-run.sh
%{_datarootdir}/cozy/konnector-nsjail-run.sh
%{_datarootdir}/cozy/konnector-rkt-run.sh
%license src/%{repo}/LICENSE

%changelog
* Tue Apr 17 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 2018M2S1-1
- New release 2018M2S1

* Sun Mar 25 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 2018M1S6-1
- Improve scriptlets
- Move things to more standard paths

* Sun Mar 25 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 2018M1S6-0
- Inital rpm for release 2018M1S6
