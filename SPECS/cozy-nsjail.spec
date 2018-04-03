%define debug_package %{nil}

Name:           cozy-nsjail
Version:        1.8
Release:        0%{?dist}
Summary:        nsjail for cozy

Group:          Applications/System
License:        Apache-2.0
URL:            https://nsjail.com/
Source0:        https://github.com/google/nsjail/archive/%{version}.tar.gz

AutoReq:        no
AutoReqProv:    no 

BuildRequires:  git pkgconfig bison flex libcap-devel protobuf-compiler protobuf-devel glibc-devel imake gcc-c++ protobuf-c-compiler

Requires:       protobuf

%description

%prep
%autosetup -n nsjail-%{version}
rmdir kafel && git clone https://github.com/google/kafel.git
cd kafel && git reset --hard 2ae8e11 && cd ..

%build
make 

%install
mkdir -p %{buildroot}/usr/local/bin
mkdir -p %{buildroot}/usr/share/licenses/nsjail/
mv nsjail %{buildroot}/usr/local/bin
mv LICENSE %{buildroot}/usr/share/licenses/nsjail


%files
/usr/local/bin/
%license /usr/share/licenses/nsjail/LICENSE

%changelog
* Mon Mar 26 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 1.8-0
- Inital rpm for release 1.8 
