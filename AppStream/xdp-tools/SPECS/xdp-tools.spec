Name:             xdp-tools
Version:          1.4.2
Release:          1%{?dist}.redsleeve
Summary:          Utilities and example programs for use with XDP
%global _soversion 1.4.0

License:          GPL-2.0-only
URL:              https://github.com/xdp-project/%{name}
Source0:          https://github.com/xdp-project/%{name}/releases/download/v%{version}/xdp-tools-%{version}.tar.gz

BuildRequires:    libbpf-devel
BuildRequires:    elfutils-libelf-devel
BuildRequires:    zlib-devel
BuildRequires:    libpcap-devel
BuildRequires:    clang >= 10.0.0
BuildRequires:    llvm >= 10.0.0
BuildRequires:    make
BuildRequires:    gcc
BuildRequires:    pkgconfig
BuildRequires:    m4
BuildRequires:    emacs-nox
BuildRequires:    wireshark-cli

%ifnarch i686 %{arm}
BuildRequires:    bpftool
%endif

# Always keep xdp-tools and libxdp packages in sync
Requires:         libxdp = %{version}-%{release}

# find-debuginfo produces empty debugsourcefiles.list
# disable the debug package to avoid rpmbuild error'ing out because of this
%global debug_package %{nil}
%global _hardened_build 1

%description
Utilities and example programs for use with XDP

%package -n libxdp
Summary:          XDP helper library
License:          LGPL-2.1-only OR BSD-2-Clause
Requires:         kernel-headers

%package -n libxdp-devel
Summary:          Development files for libxdp
License:          LGPL-2.1-only OR BSD-2-Clause
Requires:         kernel-headers
Requires:         libxdp = %{version}-%{release}

%package -n libxdp-static
Summary:          Static library files for libxdp
License:          LGPL-2.1-only OR BSD-2-Clause
Requires:         kernel-headers
Requires:         libxdp-devel = %{version}-%{release}

%description -n libxdp
The libxdp package contains the libxdp library for managing XDP programs,
used by the %{name} package

%description -n libxdp-devel
The libxdp-devel package contains headers used for building XDP programs using
libxdp.

%description -n libxdp-static
The libxdp-static package contains the static library version of libxdp.

%prep
%autosetup -p1 -n %{name}-%{version}


%build
export CFLAGS='%{build_cflags}'
export LDFLAGS='%{build_ldflags}'
export LIBDIR='%{_libdir}'
export RUNDIR='%{_rundir}'
export CLANG=%{_bindir}/clang
export LLC=%{_bindir}/llc
export PRODUCTION=1
export DYNAMIC_LIBXDP=1
export FORCE_SYSTEM_LIBBPF=1
export FORCE_EMACS=1
./configure
make %{?_smp_mflags} V=1

%install
export DESTDIR='%{buildroot}'
export SBINDIR='%{_sbindir}'
export LIBDIR='%{_libdir}'
export RUNDIR='%{_rundir}'
export MANDIR='%{_mandir}'
export DATADIR='%{_datadir}'
export HDRDIR='%{_includedir}/xdp'
make install V=1

%files
%{_sbindir}/xdp-filter
%{_sbindir}/xdp-loader
%{_sbindir}/xdpdump
%ifnarch i686 %{arm}
%{_sbindir}/xdp-bench
%{_sbindir}/xdp-monitor
%{_sbindir}/xdp-trafficgen
%endif
%{_mandir}/man8/*
%{_libdir}/bpf/xdpfilt_*.o
%{_libdir}/bpf/xdpdump_*.o
%{_datadir}/xdp-tools/
%license LICENSES/*

%files -n libxdp
%{_libdir}/libxdp.so.1
%{_libdir}/libxdp.so.%{_soversion}
%{_libdir}/bpf/xdp-dispatcher.o
%{_libdir}/bpf/xsk_def_xdp_prog*.o
%{_mandir}/man3/*
%license LICENSES/*

%files -n libxdp-static
%{_libdir}/libxdp.a

%files -n libxdp-devel
%{_includedir}/xdp/*.h
%{_libdir}/libxdp.so
%{_libdir}/pkgconfig/libxdp.pc

%changelog
* Fri May 31 2024 Jacco Ligthart <jacco@redsleeve.org> 1.4.2-1.redsleeve
- do not require bpftool for arm

* Tue Feb 6 2024 Toke Høiland-Jørgensen <toke@redhat.com> 1.4.2-1
- Upstream version bump

* Fri Oct 20 2023 Toke Høiland-Jørgensen <toke@redhat.com> 1.4.1-1
- Upstream version bump

* Thu Jul 6 2023 Toke Høiland-Jørgensen <toke@redhat.com> 1.4.0-1
- Upstream version bump

* Thu Feb 23 2023 Toke Høiland-Jørgensen <toke@redhat.com> 1.3.1-1
- Upstream version bump

* Thu Feb 9 2023 Toke Høiland-Jørgensen <toke@redhat.com> 1.3.0-2
- Restore building on i686, by patching the build to exclude the bits that require bpftool

* Tue Feb 7 2023 Toke Høiland-Jørgensen <toke@redhat.com> 1.3.0-1
- Upstream version bump
- Don't build on i686 (because of missing bpftool)

* Thu Feb 2 2023 Toke Høiland-Jørgensen <toke@redhat.com> 1.2.9-1
- Upstream version bump

* Tue Aug 16 2022 Toke Høiland-Jørgensen <toke@redhat.com> 1.2.6-1
- Upstream version bump

* Thu Feb 17 2022 Toke Høiland-Jørgensen <toke@redhat.com> 1.2.3-1
- Upstream version bump

* Mon Jan 31 2022 Toke Høiland-Jørgensen <toke@redhat.com> 1.2.2-1
- Upstream version bump

* Thu Jan 13 2022 Toke Høiland-Jørgensen <toke@redhat.com> 1.2.1-1
- Upstream version bump

* Thu Aug 19 2021 Toke Høiland-Jørgensen <toke@redhat.com> 1.2.0-1
- Upstream version bump

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 1.1.1-3
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.1.1-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Feb 3 2021 Toke Høiland-Jørgensen <toke@redhat.com> 1.1.1-1
- Upstream version bump

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 4 2021 Toke Høiland-Jørgensen <toke@redhat.com> 1.1.0-1
- Upstream version bump

* Thu Aug 20 2020 Toke Høiland-Jørgensen <toke@redhat.com> 1.0.1-1
- Upstream version bump

* Tue Aug 18 2020 Toke Høiland-Jørgensen <toke@redhat.com> 1.0.0-1
- Upstream version bump

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.0~beta3-0.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 15 2020 Eelco Chaudron <echaudro@redhat.com> 1.0.0~beta3-0.1
- Upstream version bump

* Fri Jul 10 2020 Toke Høiland-Jørgensen <toke@redhat.com> 1.0.0~beta2-0.1
- Upstream version bump

* Mon Jun 15 2020 Toke Høiland-Jørgensen <toke@redhat.com> 1.0.0~beta1-0.1
- Upstream version bump

* Mon Apr 6 2020 Toke Høiland-Jørgensen <toke@redhat.com> 0.0.3-1
- Upstream update, add libxdp sub-packages

* Thu Nov 21 2019 Toke Høiland-Jørgensen <toke@redhat.com> 0.0.2-1
- Upstream update

* Fri Nov 8 2019 Toke Høiland-Jørgensen <toke@redhat.com> 0.0.1-1
- Initial release
