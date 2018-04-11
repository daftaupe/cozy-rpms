%define debug_package %{nil}
%define repo github.com/cozy/cozy-stack

Name:           cozy-stack
Version:        2018M1S6
Release:        0%{?dist}
Summary:        Cozy: Simple, Versatile, Yours

Group:          Applications/System
License:        AGPLv3
URL:            https://%{repo}
Source0:        https://%{repo}/releases/download/2018M1S6/%{name}_%{version}.orig.tar.xz
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
%autosetup -n cozy-stack

%build
export GOPATH="$(pwd)"
export PATH=$PATH:"$(pwd)"/bin
cd src/%{repo}
COZY_ENV=production GOOS=linux GOARCH=amd64 VERSION_STRING=prod ./scripts/build.sh install

%install
mkdir -p %{buildroot}/usr/local/bin
cp bin/cozy-stack %{buildroot}/usr/local/bin/cozy-stack
mkdir -p %{buildroot}%{_datarootdir}/cozy
cp src/%{repo}/scripts/konnector-node-run.sh %{buildroot}%{_datarootdir}/cozy
cp src/%{repo}/scripts/konnector-nsjail-run.sh %{buildroot}%{_datarootdir}/cozy
cp src/%{repo}/scripts/konnector-rkt-run.sh %{buildroot}%{_datarootdir}/cozy
mkdir -p %{buildroot}%{_unitdir}
cat << EOF > %{buildroot}%{_unitdir}/cozy-stack.service
[Unit]
Description=Cozy service
Wants=couchdb.service
After=network.target couchdb.service

[Service]
User=cozy
Group=cozy
PermissionsStartOnly=true
ExecStart=/usr/local/bin/cozy-stack serve
Restart=always

[Install]
WantedBy=multi-user.target
EOF
mkdir -p %{buildroot}%{_sysconfdir}/cozy
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/cozy/cozy.yaml
sed -i 's@# url: file://localhost/var/lib/cozy@url: file://localhost/var/lib/cozy@;s@/path/to/key.enc@/home/cozy/keys/key.enc@;s@/path/to/key.dec@/home/cozy/keys/key.dec@;s@cmd: ./scripts@cmd: %{_datarootdir}/cozy@g' %{buildroot}%{_sysconfdir}/cozy/cozy.yaml

%pre

%post
useradd cozy
chown cozy: -R /etc/cozy
mkdir -p /var/lib/cozy && chown cozy: /var/lib/cozy
mkdir -p /var/log/cozy && chown cozy: /var/log/cozy
mkdir -p /home/cozy/keys && chown cozy: /home/cozy/keys
su - cozy -c "cozy-stack config gen-keys ~/keys/key &> /dev/null"


%preun
if [ "$1" = 0 ]; then 
    systemctl stop cozy-stack
    systemctl disable cozy-stack
fi

%postun
if [ "$1" = 0 ]; then
    mv /home/cozy /home/cozy.bkp
    mv /var/lib/cozy /var/lib/cozy.bkp
    mv /var/log/cozy /var/log/cozy.bkp
    userdel cozy
fi

%files
/usr/local/bin/cozy-stack
%{_unitdir}/cozy-stack.service
%config %{_sysconfdir}/cozy/cozy.yaml
%{_datarootdir}/cozy/konnector-node-run.sh
%{_datarootdir}/cozy/konnector-nsjail-run.sh
%{_datarootdir}/cozy/konnector-rkt-run.sh
%license src/%{repo}/LICENSE

%changelog
* Sun Mar 25 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 2018M1S6-0
- Inital rpm for release 2018M1S6
