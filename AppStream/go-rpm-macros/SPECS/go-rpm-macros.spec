%global forgeurl  https://pagure.io/go-rpm-macros
Version:   3.2.0
%forgemeta

#https://src.fedoraproject.org/rpms/redhat-rpm-config/pull-request/51
%global _spectemplatedir %{_datadir}/rpmdevtools/fedora
%global _docdir_fmt     %{name}

# Master definition that will be written to macro files
%global golang_arches   %{ix86} x86_64 %{arm} aarch64 ppc64le s390x
%global gccgo_arches    %{mips}
%if 0%{?rhel} >= 9
%global golang_arches   x86_64 aarch64 ppc64le s390x
%endif
# Go sources can contain arch-specific files and our macros will package the
# correct files for each architecture. Therefore, move gopath to _libdir and
# make Go devel packages archful
%global gopath          %{_datadir}/gocode

# whether to bundle golist or require it as a dependency
%global bundle_golist 1

%if 0%{?bundle_golist}
# do not create debuginfo packages when we add a build section
%global debug_package %{nil}
%global golist_version 0.10.1
%global golist_builddir %{_builddir}/golist-%{golist_version}/_build
%global golist_goipath pagure.io/golist
# where to bundle the golist executable
%global golist_execdir %{_libexecdir}/go-rpm-macros/
# define gobuild to avoid this package requiring itself to build
%define gobuild(o:) GO111MODULE=off go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '-Wl,-z,relro -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld '" -a -v %{?**};
%endif

ExclusiveArch: %{golang_arches} %{gccgo_arches}

Name:      go-rpm-macros
Release:   1%{?dist}
Summary:   Build-stage rpm automation for Go packages

License:   GPLv3+
URL:       %{forgeurl}
Source0:   %{forgesource}
%if 0%{?bundle_golist}
Source1:   https://pagure.io/golist/archive/v%{golist_version}/golist-%{golist_version}.tar.gz
%endif

Requires:  go-srpm-macros = %{version}-%{release}
Requires:  go-filesystem  = %{version}-%{release}

%if 0%{?bundle_golist}
BuildRequires: golang
%else
Requires:  golist
%endif

%ifarch %{golang_arches}
Requires:  golang
Provides:  compiler(golang)
Provides:  compiler(go-compiler) = 2
Obsoletes: go-compilers-golang-compiler < %{version}-%{release}
%endif

%ifarch %{gccgo_arches}
Requires:  gcc-go
Provides:  compiler(gcc-go)
Provides:  compiler(go-compiler) = 1
Obsoletes: go-compilers-gcc-go-compiler < %{version}-%{release}
%endif

Patch0: update-default-gobuild-args.patch
# Replace golang-github-urfave-cli with a minimal
# command line parser backend to bootstrap golist
# without dependencies.
Patch1: golist-bootstrap-cli-no-vendor.patch

# RHEL 8 only provides the macros.go-srpm file which includes gobuild and gotest.
# C9S also only provides the macros.go-srpm file but it also follows upstream which includes gobuild and gotest in the macros.go-compilers-gcc.
# For a simple fix, this patch ports both RHEL 8 macros to macros.go-srpm.
# Resolves: rhbz#1965292
Patch2: add-gobuild-and-gotest.patch

%description
This package provides build-stage rpm automation to simplify the creation of Go
language (golang) packages.

It does not need to be included in the default build root: go-srpm-macros will
pull it in for Go packages only.

%package -n go-srpm-macros
Summary:   Source-stage rpm automation for Go packages
BuildArch: noarch
Requires:  redhat-rpm-config

%description -n go-srpm-macros
This package provides SRPM-stage rpm automation to simplify the creation of Go
language (golang) packages.

It limits itself to the automation subset required to create Go SRPM packages
and needs to be included in the default build root.

The rest of the automation is provided by the go-rpm-macros package, that
go-srpm-macros will pull in for Go packages only.

%package -n go-filesystem
Summary:   Directories used by Go packages
License:   Public Domain

%description -n go-filesystem
This package contains the basic directory layout used by Go packages.

%package -n go-rpm-templates
Summary:   RPM spec templates for Go packages
License:   MIT
BuildArch: noarch
Requires:  go-rpm-macros = %{version}-%{release}
#https://src.fedoraproject.org/rpms/redhat-rpm-config/pull-request/51
#Requires:  redhat-rpm-templates

%description -n go-rpm-templates
This package contains documented rpm spec templates showcasing how to use the
macros provided by go-rpm-macros to create Go packages.

%prep
%forgesetup

%patch0 -p1

%writevars -f rpm/macros.d/macros.go-srpm golang_arches gccgo_arches gopath
for template in templates/rpm/*\.spec ; do
  target=$(echo "${template}" | sed "s|^\(.*\)\.spec$|\1-bare.spec|g")
  grep -v '^#' "${template}" > "${target}"
  touch -r "${template}" "${target}"
done

# unpack golist and patch
%if 0%{?bundle_golist}
pushd %{_builddir}
tar -xf %{_sourcedir}/golist-%{golist_version}.tar.gz
cd golist-%{golist_version}
%patch1 -p1
cp %{_builddir}/golist-%{golist_version}/LICENSE %{_builddir}/go-rpm-macros-%{version}/LICENSE-golist
popd

# create directory structure for a Go build
if [[ ! -e %{golist_builddir}/bin ]]; then
  install -m 0755 -vd %{golist_builddir}/bin
  export GOPATH=%{golist_builddir}:${GOPATH:+${GOPATH}:}/usr/share/gocode
fi
if [[ ! -e %{golist_builddir}/src/%{golist_goipath} ]]; then
  install -m 0755 -vd %{golist_builddir}/src/pagure.io
  ln -sf $(dirname %{golist_builddir}) %{golist_builddir}/src/%{golist_goipath}

fi
%endif

%patch2 -p1

%build
# build golist
%if 0%{?bundle_golist}
pushd %{golist_builddir}/src/%{golist_goipath}
export GOPATH=%{golist_builddir}:${GOPATH:+${GOPATH}:}/usr/share/gocode
for cmd in cmd/* ; do
  %gobuild -o %{golist_builddir}/bin/$(basename $cmd) %{golist_goipath}/$cmd
done
popd
%endif

%install
# Some of those probably do not work with gcc-go right now
# This is not intentional, but mips is not a primary Fedora architecture
# Patches and PRs are welcome

install -m 0755 -vd   %{buildroot}%{gopath}/src

install -m 0755 -vd   %{buildroot}%{_spectemplatedir}

if ls templates/rpm/*\.spec; then
  install -m 0644 -vp   templates/rpm/*spec \
                        %{buildroot}%{_spectemplatedir}
fi

install -m 0755 -vd   %{buildroot}%{_bindir}
install -m 0755 bin/* %{buildroot}%{_bindir}

install -m 0755 -vd   %{buildroot}%{rpmmacrodir}
install -m 0644 -vp   rpm/macros.d/macros.go-* \
                      %{buildroot}%{rpmmacrodir}
install -m 0755 -vd   %{buildroot}%{_rpmluadir}/fedora/srpm
install -m 0644 -vp   rpm/lua/srpm/*lua \
                      %{buildroot}%{_rpmluadir}/fedora/srpm
install -m 0755 -vd   %{buildroot}%{_rpmluadir}/fedora/rpm
install -m 0644 -vp   rpm/lua/rpm/*lua \
                      %{buildroot}%{_rpmluadir}/fedora/rpm
install -m 0755 -vd   %{buildroot}%{_rpmconfigdir}/fileattrs
install -m 0644 -vp   rpm/fileattrs/*.attr \
                      %{buildroot}%{_rpmconfigdir}/fileattrs/
install -m 0755 -vp   rpm/*\.{prov,deps} \
                      %{buildroot}%{_rpmconfigdir}/

%ifarch %{golang_arches}
install -m 0644 -vp   rpm/macros.d/macros.go-compilers-golang \
                      %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compiler-golang
%endif

%ifarch %{gccgo_arches}
install -m 0644 -vp   rpm/macros.d/macros.go-compilers-gcc \
                      %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compiler-gcc
%endif

# install golist
%if 0%{?bundle_golist}
install -m 0755 -vd                     %{buildroot}%{golist_execdir}
install -m 0755 -vp %{golist_builddir}/bin/* %{buildroot}%{golist_execdir}/
sed -i "s,golist,%{golist_execdir}/golist,g" %{buildroot}%{_bindir}/go-rpm-integration
%endif

%files
%license LICENSE.txt LICENSE-golist
%doc README.md
%{_bindir}/*
%{_rpmconfigdir}/fileattrs/*.attr
%{_rpmconfigdir}/*.prov
%{_rpmconfigdir}/*.deps
%{_rpmconfigdir}/macros.d/macros.go-rpm*
%{_rpmconfigdir}/macros.d/macros.go-compiler*
%{_rpmluadir}/fedora/rpm/*.lua
# package golist
%if 0%{?bundle_golist}
%{golist_execdir}/golist
%endif

%files -n go-srpm-macros
%license LICENSE.txt
%doc README.md
%{_rpmconfigdir}/macros.d/macros.go-srpm
%{_rpmluadir}/fedora/srpm/*.lua

%files -n go-filesystem
%dir %{gopath}
%dir %{gopath}/src

%files -n go-rpm-templates
%license LICENSE-templates.txt
%doc README.md
# https://src.fedoraproject.org/rpms/redhat-rpm-config/pull-request/51
%dir %{dirname:%{_spectemplatedir}}
%dir %{_spectemplatedir}
%{_spectemplatedir}/*.spec

%changelog
* Wed Nov 23 2022 Alejandro Sáez <asm@redhat.com> - 3.2.0-1
- Update to 3.2.0
- Add add-gobuild-and-gotest.patch
- Resolves: rhbz#1965292

* Wed Jan 26 2022 Alejandro Sáez <asm@redhat.com> - 3.0.9-10
- Fix typos in update-default-gobuild-args.patch
- Related: rhbz#2043107

* Tue Jan 18 2022 David Benoit <dbenoit@redhat.com> 3.0.9-9
- Delete remove-fedora-dependency-automation.patch
- Bundle golist in /usr/libexec
- Related: rhbz#2043107

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Aug 03 2021 David Benoit <dbenoit@redhat.com> 3.0.9-7
- Escape quotation marks in gobuildflags
- Resolves: rhbz#1988717

* Tue Jul 27 2021 David Benoit <dbenoit@redhat.com> 3.0.9-6
- Remove arch conditional on gocompilerflags
- Related: rhbz#1982298

* Fri Jul 23 2021 David Benoit <dbenoit@redhat.com> 3.0.9-5
- Remove fedora-specific Go dependency automation macros
- Remove dependency on golist
- Temporarily remove incompatible template spec files
- Update gobuild flags
- Resolves: rhbz#1982298

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Thu Feb 11 2021 Jeff Law  <law@redhat.com> - 3.0.9-3
- Drop 32 bit arches in EL 9 (originally from Petr Sabata)

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Aug 13 2020 Neal Gompa <ngompa13@gmail.com> - 3.0.9-1
- Update to 3.0.9

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.8-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jun 05 2019 Nicolas Mailhot <nim@fedoraproject.org>
- 3.0.8-3
- initial Fedora import, for golist 0.10.0 and redhat-rpm-config 130
