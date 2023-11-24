# Do this until the feature is fixed in Fedora.
%undefine _package_note_flags

# If we should verify tarball signature with GPGv2.
%global verify_tarball_signature 1

# If there are patches which touch autotools files, set this to 1.
%global patches_touch_autotools %{nil}

# The source directory.
%global source_directory 1.16-stable

Name:           libnbd
Version:        1.16.0
Release:        1%{?dist}
Summary:        NBD client library in userspace

License:        LGPLv2+
URL:            https://gitlab.com/nbdkit/libnbd

Source0:        http://libguestfs.org/download/libnbd/%{source_directory}/%{name}-%{version}.tar.gz
Source1:        http://libguestfs.org/download/libnbd/%{source_directory}/%{name}-%{version}.tar.gz.sig
# Keyring used to verify tarball signature.  This contains the single
# key from here:
# https://pgp.key-server.io/pks/lookup?search=rjones%40redhat.com&fingerprint=on&op=vindex
Source2:       libguestfs.keyring

# Maintainer script which helps with handling patches.
Source3:        copy-patches.sh

# Patches are stored in the upstream repository:
# https://gitlab.com/nbdkit/libnbd/-/commits/rhel-9.3/

# (no patches)

%if 0%{patches_touch_autotools}
BuildRequires: autoconf, automake, libtool
%endif

%if 0%{verify_tarball_signature}
BuildRequires:  gnupg2
%endif

# For the core library.
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  /usr/bin/pod2man
BuildRequires:  gnutls-devel
BuildRequires:  libxml2-devel

# For nbdfuse.
BuildRequires:  fuse3, fuse3-devel

%if !0%{?rhel}
# For nbdublk
BuildRequires:  liburing-devel >= 2.2
BuildRequires:  ubdsrv-devel >= 1.0-3.rc6
%endif

# For the Python 3 bindings.
BuildRequires:  python3-devel

# For the OCaml bindings.
BuildRequires:  ocaml
BuildRequires:  ocaml-findlib-devel
BuildRequires:  ocaml-ocamldoc

# Only for building the examples.
BuildRequires:  glib2-devel

# For bash-completion.
BuildRequires:  bash-completion

# Only for running the test suite.
BuildRequires:  coreutils
BuildRequires:  gcc-c++
BuildRequires:  gnutls-utils
BuildRequires:  iproute
BuildRequires:  jq
%if !0%{?rhel}
BuildRequires:  nbd
%endif
BuildRequires:  util-linux

# On RHEL, maybe even in Fedora in future, we do not build qemu-img or
# nbdkit for i686.  These are only needed for the test suite so make
# them optional.  This reduces our test exposure on 32 bit platforms,
# although there is still Fedora/armv7 and some upstream testing.
%ifnarch %{ix86}
BuildRequires:  qemu-img
BuildRequires:  nbdkit
BuildRequires:  nbdkit-data-plugin
BuildRequires:  nbdkit-eval-plugin
BuildRequires:  nbdkit-memory-plugin
BuildRequires:  nbdkit-null-plugin
BuildRequires:  nbdkit-pattern-plugin
BuildRequires:  nbdkit-sh-plugin
BuildRequires:  nbdkit-sparse-random-plugin
%endif


%description
NBD — Network Block Device — is a protocol for accessing Block Devices
(hard disks and disk-like things) over a Network.

This is the NBD client library in userspace, a simple library for
writing NBD clients.

The key features are:

 * Synchronous and asynchronous APIs, both for ease of use and for
   writing non-blocking, multithreaded clients.

 * High performance.

 * Minimal dependencies for the basic library.

 * Well-documented, stable API.

 * Bindings in several programming languages.


%package devel
Summary:        Development headers for %{name}
License:        LGPLv2+ and BSD
Requires:       %{name}%{?_isa} = %{version}-%{release}


%description devel
This package contains development headers for %{name}.


%package -n ocaml-%{name}
Summary:        OCaml language bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}


%description -n ocaml-%{name}
This package contains OCaml language bindings for %{name}.


%package -n ocaml-%{name}-devel
Summary:        OCaml language development package for %{name}
Requires:       ocaml-%{name}%{?_isa} = %{version}-%{release}


%description -n ocaml-%{name}-devel
This package contains OCaml language development package for
%{name}.  Install this if you want to compile OCaml software which
uses %{name}.


%package -n python3-%{name}
Summary:        Python 3 bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{name}}

# The Python module happens to be called lib*.so.  Don't scan it and
# have a bogus "Provides: libnbdmod.*".
%global __provides_exclude_from ^%{python3_sitearch}/lib.*\\.so


%description -n python3-%{name}
python3-%{name} contains Python 3 bindings for %{name}.


%package -n nbdfuse
Summary:        FUSE support for %{name}
License:        LGPLv2+ and BSD
Requires:       %{name}%{?_isa} = %{version}-%{release}
Recommends:     fuse3


%description -n nbdfuse
This package contains FUSE support for %{name}.


%if !0%{?rhel}
%package -n nbdublk
Summary:        Userspace NBD block device
License:        LGPLv2+
Requires:       %{name}%{?_isa} = %{version}-%{release}
Recommends:     kernel >= 6.0.0
Recommends:     %{_sbindir}/ublk


%description -n nbdublk
This package contains a userspace NBD block device
based on %{name}.
%endif


%package bash-completion
Summary:       Bash tab-completion for %{name}
BuildArch:     noarch
Requires:      bash-completion >= 2.0
# Don't use _isa here because it's a noarch package.  This dependency
# is just to ensure that the subpackage is updated along with libnbd.
Requires:      %{name} = %{version}-%{release}


%description bash-completion
Install this package if you want intelligent bash tab-completion
for %{name}.


%prep
%if 0%{verify_tarball_signature}
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%endif
%autosetup -p1
%if 0%{patches_touch_autotools}
autoreconf -i
%endif


%build
%configure \
    --disable-static \
    --with-tls-priority=@LIBNBD,SYSTEM \
    PYTHON=%{__python3} \
    --enable-python \
    --enable-ocaml \
    --enable-fuse \
    --disable-golang

make %{?_smp_mflags}


%install
%make_install

# Delete libtool crap.
find $RPM_BUILD_ROOT -name '*.la' -delete

# Delete the golang man page since we're not distributing the bindings.
rm $RPM_BUILD_ROOT%{_mandir}/man3/libnbd-golang.3*

%if 0%{?rhel}
# Delete nbdublk on RHEL.
rm $RPM_BUILD_ROOT%{_datadir}/bash-completion/completions/nbdublk
%endif


%check
function skip_test ()
{
    for f in "$@"; do
        rm -f "$f"
        echo 'exit 77' > "$f"
        chmod +x "$f"
    done
}

# interop/structured-read.sh fails with the old qemu-nbd in Fedora 29,
# so disable it there.
%if 0%{?fedora} <= 29
skip_test interop/structured-read.sh
%endif

# interop/interop-qemu-storage-daemon.sh fails in RHEL 9 because of
# this bug in qemu:
# https://lists.nongnu.org/archive/html/qemu-devel/2021-03/threads.html#03544
%if 0%{?rhel}
skip_test interop/interop-qemu-storage-daemon.sh
%endif

# All fuse tests fail in Koji with:
# fusermount: entry for fuse/test-*.d not found in /etc/mtab
# for unknown reasons but probably related to the Koji environment.
skip_test fuse/test-*.sh

# IPv6 loopback connections fail in Koji.
make -C tests connect-tcp6 ||:
skip_test tests/connect-tcp6

make %{?_smp_mflags} check || {
    for f in $(find -name test-suite.log); do
        echo
        echo "==== $f ===="
        cat $f
    done
    exit 1
  }


%files
%doc README.md
%license COPYING.LIB
%{_bindir}/nbdcopy
%{_bindir}/nbddump
%{_bindir}/nbdinfo
%{_libdir}/libnbd.so.*
%{_mandir}/man1/nbdcopy.1*
%{_mandir}/man1/nbddump.1*
%{_mandir}/man1/nbdinfo.1*


%files devel
%doc TODO examples/*.c
%license examples/LICENSE-FOR-EXAMPLES
%{_includedir}/libnbd.h
%{_libdir}/libnbd.so
%{_libdir}/pkgconfig/libnbd.pc
%{_mandir}/man3/libnbd.3*
%{_mandir}/man1/libnbd-release-notes-1.*.1*
%{_mandir}/man3/libnbd-security.3*
%{_mandir}/man3/nbd_*.3*


%files -n ocaml-%{name}
%{_libdir}/ocaml/nbd
%exclude %{_libdir}/ocaml/nbd/*.a
%exclude %{_libdir}/ocaml/nbd/*.cmxa
%exclude %{_libdir}/ocaml/nbd/*.cmx
%exclude %{_libdir}/ocaml/nbd/*.mli
%{_libdir}/ocaml/stublibs/dllmlnbd.so
%{_libdir}/ocaml/stublibs/dllmlnbd.so.owner


%files -n ocaml-%{name}-devel
%doc ocaml/examples/*.ml
%license ocaml/examples/LICENSE-FOR-EXAMPLES
%{_libdir}/ocaml/nbd/*.a
%{_libdir}/ocaml/nbd/*.cmxa
%{_libdir}/ocaml/nbd/*.cmx
%{_libdir}/ocaml/nbd/*.mli
%{_mandir}/man3/libnbd-ocaml.3*
%{_mandir}/man3/NBD.3*
%{_mandir}/man3/NBD.*.3*


%files -n python3-%{name}
%{python3_sitearch}/libnbdmod*.so
%{python3_sitearch}/nbd.py
%{python3_sitearch}/nbdsh.py
%{python3_sitearch}/__pycache__/nbd*.py*
%{_bindir}/nbdsh
%{_mandir}/man1/nbdsh.1*


%files -n nbdfuse
%{_bindir}/nbdfuse
%{_mandir}/man1/nbdfuse.1*


%if !0%{?rhel}
%files -n nbdublk
%{_bindir}/nbdublk
%{_mandir}/man1/nbdublk.1*
%endif


%files bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/nbdcopy
%{_datadir}/bash-completion/completions/nbddump
%{_datadir}/bash-completion/completions/nbdfuse
%{_datadir}/bash-completion/completions/nbdinfo
%{_datadir}/bash-completion/completions/nbdsh
%if !0%{?rhel}
%{_datadir}/bash-completion/completions/nbdublk
%endif


%changelog
* Tue Apr 18 2023 Richard W.M. Jones <rjones@redhat.com> - 1.16.0-1
- Rebase to 1.16.0
  resolves: rhbz#2168628

* Tue Jan 03 2023 Richard W.M. Jones <rjones@redhat.com> - 1.14.2-1
- Rebase to new stable branch version 1.14.2
  resolves: rhbz#2135764

* Thu Jul 28 2022 Richard W.M. Jones <rjones@redhat.com> - 1.12.6-1
- Rebase to new stable branch version 1.12.6
  resolves: rhbz#2059288
- New tool: nbddump
- nbdcopy: Use preferred block size for copying
  related: rhbz#2047660
- Fix remote TLS failures
  resolves: rhbz#2111524
  (and 2111813)

* Thu Feb 10 2022 Richard W.M. Jones <rjones@redhat.com> - 1.10.5-1
- Rebase to new stable branch version 1.10.5
  resolves: rhbz#2011708
- Map uint32_t to OCaml int64 to avoid signedness problems
  resolves: rhbz#2040610
- CVE-2022-0485 nbdcopy destination image corruption
- New upstream API to control initialization of pread buffer
  resolves: rhbz#2046194

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.8.2-3
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Jul 30 2021 Richard W.M. Jones <rjones@redhat.com> - 1.8.2-2
- Fix nbdcopy progress bar.
- Add nbdinfo --map --totals and --can/--is options.
  resolves: rhbz#1950630

* Sat Jul 03 2021 Richard W.M. Jones <rjones@redhat.com> - 1.8.2-1
- New upstream stable version 1.8.2.

* Wed Jun 23 2021 Richard W.M. Jones <rjones@redhat.com> - 1.8.1-2
- Bump and rebuild
  resolves: rhbz#1975316

* Fri Jun 11 2021 Richard W.M. Jones <rjones@redhat.com> - 1.8.1-1
- New upstream stable version 1.8.1.

* Mon Jun 07 2021 Richard W.M. Jones <rjones@redhat.com> - 1.8.0-1
- New upstream version 1.8.0.

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 1.7.12-2
- Rebuilt for Python 3.10

* Sat May 29 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.12-1
- New upstream version 1.7.12.

* Thu May 20 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.11-1
- New upstream version 1.7.11.

* Fri May 14 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.10-1
- New upstream version 1.7.10.

* Thu Apr 29 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.9-1
- New upstream version 1.7.9.
- Switch to fuse3.
- Make nbdfuse package recommend fuse3 (to get fusermount3).

* Sat Apr 24 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.8-1
- New upstream development version 1.7.8.

* Sat Apr 10 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.7-1
- New upstream development version 1.7.7.
- +BR iproute
- Add skip_test helper function.
- Skip connect-tcp6 test which fails under Koji.

* Thu Apr 08 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.6-1
- New upstream development version 1.7.6.

* Sat Apr 03 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.5-1
- New upstream development version 1.7.5.

* Mon Mar 15 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.4-1
- New upstream development version 1.7.4.

* Mon Mar 15 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.3-3
- Update documentation for CVE-2021-20286.
- Workaround broken interop/interop-qemu-storage-daemon.sh test in RHEL 9.

* Thu Mar  4 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.3-2
- Add fix for nbdkit test suite.

* Tue Mar  2 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.3-1
- New upstream version 1.7.3.

* Mon Mar  1 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.2-3
- OCaml 4.12.0 build

* Wed Feb 24 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.2-2
- Disable nbd BR on RHEL.

* Mon Feb 22 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.2-1
- New upstream version 1.7.2.

* Fri Jan 29 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.1-6
- Disable BR qemu-img on i686.

* Thu Jan 28 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.1-3
- Disable BR nbdkit on i686 because it breaks ELN/RHEL 9.

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jan 20 2021 Richard W.M. Jones <rjones@redhat.com> - 1.7.1-1
- New upstream development version 1.7.1.

* Thu Jan 07 2021 Richard W.M. Jones <rjones@redhat.com> - 1.6.0-1
- New upstream stable version 1.6.0.

* Tue Dec 08 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.9-1
- New upstream development version 1.5.9.

* Thu Dec 03 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.8-1
- New upstream development version 1.5.8.
- Unify Fedora and RHEL spec files.

* Wed Nov 25 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.7-1
- New upstream development version 1.5.7.
- Add some more test suite buildrequires lines.
- Fix bogus date in changelog.

* Thu Nov 12 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.6-1
- New upstream development version 1.5.6.

* Mon Nov 02 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.5-1
- New upstream development version 1.5.5.

* Mon Oct 05 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.4-1
- New upstream development version 1.5.4.
- More OCaml man pages.

* Sat Sep 26 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.3-1
- New upstream development version 1.5.3.

* Thu Sep 10 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.2-1
- New upstream development version 1.5.2.

* Tue Sep 08 2020 Richard W.M. Jones <rjones@redhat.com> - 1.5.1-1
- New upstream development version 1.5.1.

* Tue Sep 01 2020 Richard W.M. Jones <rjones@redhat.com> - 1.4.0-2
- OCaml 4.11.1 rebuild

* Tue Aug 25 2020 Richard W.M. Jones <rjones@redhat.com> - 1.4.0-1
- New stable release 1.4.0.

* Fri Aug 21 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.12-3
- Bump release and rebuild.

* Fri Aug 21 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.12-2
- OCaml 4.11.0 rebuild

* Thu Aug 20 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.12-1
- New upstream version 1.3.12.

* Thu Aug  6 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.11-1
- New upstream version 1.3.11.

* Tue Aug  4 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.10-1
- New upstream version 1.3.10.

* Wed Jul 29 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.9-3
- Bump and rebuild.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 21 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.9-1
- New upstream version 1.3.9.
- New tool: nbdinfo.

* Fri Jul 17 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.8-2
- New upstream version 1.3.8.
- New tool: nbdcopy
- Add upstream patch to fix compilation with glibc from Rawhide.

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 1.3.7-3
- Rebuilt for Python 3.9

* Mon May 04 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.7-2
- OCaml 4.11.0+dev2-2020-04-22 rebuild

* Thu Apr 23 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.7-1
- New upstream version 1.3.7.

* Tue Apr 21 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.6-5
- OCaml 4.11.0 pre-release attempt 2

* Fri Apr 17 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.6-4
- OCaml 4.11.0 pre-release
- Add upstream patch to fix one of the tests that fails on slow machines.

* Thu Apr 02 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.6-2
- Update all OCaml dependencies for RPM 4.16.

* Tue Mar 31 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.6-1
- New upstream development version 1.3.6.
- Golang bindings are contained in this release but not distributed.

* Wed Mar 11 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.5-2
- Fix bogus runtime Requires of new bash-completion package.

* Tue Mar 10 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.5-1
- New upstream development version 1.3.5.
- Add new bash-completion subpackage.

* Sat Feb 29 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.4-1
- New upstream development version 1.3.4.

* Wed Feb 26 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.3-2
- OCaml 4.10.0 final.

* Wed Feb 05 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.3-1
- New upstream development version 1.3.3.

* Thu Jan 30 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.2-1
- New upstream development version 1.3.2.

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Jan 19 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.1-4
- Bump release and rebuild.

* Sun Jan 19 2020 Richard W.M. Jones <rjones@redhat.com> - 1.3.1-3
- OCaml 4.10.0+beta1 rebuild.

* Thu Dec 12 2019 Richard W.M. Jones <rjones@redhat.com> - 1.3.1-2
- Rebuild for OCaml 4.09.0.

* Tue Dec 03 2019 Richard W.M. Jones <rjones@redhat.com> - 1.3.1-1
- New upstream development version 1.3.1.

* Wed Nov 27 2019 Richard W.M. Jones <rjones@redhat.com> - 1.2.0-2
- Use gpgverify macro instead of explicit gpgv2 command.

* Thu Nov 14 2019 Richard W.M. Jones <rjones@redhat.com> - 1.2.0-1
- New stable release 1.2.0

* Sat Nov 09 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.9-1
- New upstream version 1.1.9.
- Add new nbdkit-release-notes-1.2(1) man page.

* Wed Nov 06 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.8-1
- New upstream version 1.1.8.

* Thu Oct 24 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.7-1
- New upstream version 1.1.7.

* Sat Oct 19 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.6-1
- New upstream version 1.1.6.

* Sat Oct 12 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.5-1
- New upstream version 1.1.5.
- New tool and subpackage nbdfuse.

* Wed Oct  9 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.4-1
- New upstream version 1.1.4.
- Contains fix for remote code execution vulnerability.
- Add new libnbd-security(3) man page.

* Tue Oct  1 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.3-1
- New upstream version 1.1.3.

* Tue Sep 17 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.2-1
- New upstream version 1.1.2.
- Remove patches which are upstream.
- Contains fix for NBD Protocol Downgrade Attack (CVE-2019-14842).

* Thu Sep 12 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.1-2
- Add upstream patch to fix nbdsh (for nbdkit tests).

* Sun Sep 08 2019 Richard W.M. Jones <rjones@redhat.com> - 1.1.1-1
- New development version 1.1.1.

* Wed Aug 28 2019 Richard W.M. Jones <rjones@redhat.com> - 1.0.0-1
- New upstream version 1.0.0.

* Wed Aug 21 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.9-2
- Rebuilt for Python 3.8

* Wed Aug 21 2019 Richard W.M. Jones <rjones@redhat.com> - 0.9.9-1
- New upstream version 0.9.9.

* Wed Aug 21 2019 Richard W.M. Jones <rjones@redhat.com> - 0.9.8-4
- Fix nbdkit dependencies so we're actually running the tests.
- Add glib2-devel BR so we build the glib main loop example.
- Add upstream patch to fix test error:
  nbd_connect_unix: getlogin: No such device or address
- Fix test failure on 32 bit.

* Tue Aug 20 2019 Richard W.M. Jones <rjones@redhat.com> - 0.9.8-3
- Bump and rebuild to fix releng brokenness.
  https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/2LIDI33G3IEIPYSCCIP6WWKNHY7XZJGQ/

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.8-2
- Rebuilt for Python 3.8

* Thu Aug 15 2019 Richard W.M. Jones <rjones@redhat.com> - 0.9.8-1
- New upstream version 0.9.8.
- Package the new nbd_*(3) man pages.

* Mon Aug  5 2019 Richard W.M. Jones <rjones@redhat.com> - 0.9.7-1
- New upstream version 0.9.7.
- Add libnbd-ocaml(3) man page.

* Sat Aug  3 2019 Richard W.M. Jones <rjones@redhat.com> - 0.9.6-2
- Add all upstream patches since 0.9.6 was released.
- Package the ocaml bindings into a subpackage.

* Tue Jul 30 2019 Richard W.M. Jones <rjones@redhat.com> - 0.9.6-1
- New upstream verison 0.9.6.

* Fri Jul 26 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.9-1
- New upstream version 0.1.9.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 17 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.8-1
- New upstream version 0.1.8.

* Tue Jul 16 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.7-1
- New upstream version 0.1.7.

* Wed Jul  3 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.6-1
- New upstream version 0.1.6.

* Thu Jun 27 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.5-1
- New upstream version 0.1.5.

* Sun Jun 09 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.4-1
- New upstream version 0.1.4.

* Sun Jun  2 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.2-2
- Enable libxml2 for NBD URI support.

* Thu May 30 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.2-1
- New upstream version 0.1.2.

* Tue May 28 2019 Richard W.M. Jones <rjones@redhat.com> - 0.1.1-1
- Fix license in man pages and examples.
- Add nbdsh(1) man page.
- Include the signature and keyring even if validation is disabled.
- Update devel subpackage license.
- Fix old FSF address in Python tests.
- Filter Python provides.
- Remove executable permission on the tar.gz.sig file.
- Initial release.
