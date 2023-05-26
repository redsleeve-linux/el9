# Only enable if using patches that touches configure.ac,
# Makefile.am or other build system related files
#
%define enable_autoreconf 1

%global bundled_mozjs 1

%if 0%{?bundled_mozjs}
%global mozjs_major 78
%global mozjs_version 78.10.0

# Big endian platforms
%ifarch ppc ppc64 s390 s390x
%global big_endian 1
%endif

# Make sure we don't add requires/provides for private libraries
%global __provides_exclude_from ^%{_libdir}/polkit-1/
%global __requires_exclude ^libmozjs-%{mozjs_major}\\.so.*
%endif

Summary: An authorization framework
Name: polkit
Version: 0.117
Release: 11%{?dist}
License: LGPLv2+
URL: http://www.freedesktop.org/wiki/Software/polkit
Source0: http://www.freedesktop.org/software/polkit/releases/%{name}-%{version}.tar.gz
Source1: http://www.freedesktop.org/software/polkit/releases/%{name}-%{version}.tar.gz.sign

Patch1001: mozjs78.patch
Patch1002: CVE-2021-3560.patch
Patch1003: CVE-2021-4034.patch
Patch1004: CVE-2021-4115.patch
Patch1005: tty-restore-flags-if-changed.patch

%if 0%{?bundled_mozjs}
Source2: https://ftp.mozilla.org/pub/firefox/releases/%{mozjs_version}esr/source/firefox-%{mozjs_version}esr.source.tar.xz

# Patches from mozjs68, rebased for mozjs78:
Patch02: copy-headers.patch
Patch03: tests-increase-timeout.patch
Patch09: icu_sources_data.py-Decouple-from-Mozilla-build-system.patch
Patch10: icu_sources_data-Write-command-output-to-our-stderr.patch

# Build fixes - https://hg.mozilla.org/mozilla-central/rev/ca36a6c4f8a4a0ddaa033fdbe20836d87bbfb873
Patch12: emitter.patch

# Build fixes
Patch14: init_patch.patch
# TODO: Check with mozilla for cause of these fails and re-enable spidermonkey compile time checks if needed
Patch15: spidermonkey_checks_disable.patch

# armv7 fixes
Patch17: definitions_for_user_vfp.patch

# s390x/ppc64 fixes, TODO: file bug report upstream?
Patch18: spidermonkey_style_check_disable_s390x.patch
Patch19: 0001-Skip-failing-tests-on-ppc64-and-s390x.patch

# Fix for https://bugzilla.mozilla.org/show_bug.cgi?id=1644600 ( SharedArrayRawBufferRefs is not exported )
# https://github.com/0ad/0ad/blob/83e81362d850cc6f2b3b598255b873b6d04d5809/libraries/source/spidermonkey/FixSharedArray.diff
Patch30: FixSharedArray.diff

# Avoid autoconf213 dependency, backported from upstream
# https://bugzilla.mozilla.org/show_bug.cgi?id=1663863
Patch31: 0002-D89554-autoconf1.diff
Patch32: 0003-D94538-autoconf2.diff
%endif

BuildRequires: make
BuildRequires: gcc-c++
BuildRequires: glib2-devel >= 2.30.0
BuildRequires: expat-devel
BuildRequires: pam-devel
BuildRequires: gtk-doc
BuildRequires: intltool
BuildRequires: gobject-introspection-devel
BuildRequires: systemd, systemd-devel
%if 0%{?bundled_mozjs}
BuildRequires: cargo
BuildRequires: clang-devel
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: m4
BuildRequires: make
%if !0%{?rhel}
BuildRequires: nasm
%endif
BuildRequires: llvm
BuildRequires: llvm-devel
BuildRequires: rust
BuildRequires: perl-devel
BuildRequires: pkgconfig(libffi)
BuildRequires: pkgconfig(zlib)
BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: python3-six
BuildRequires: readline-devel
BuildRequires: zip
%if 0%{?big_endian}
BuildRequires: icu
%endif
%else
BuildRequires: pkgconfig(mozjs-78)
%endif

%if 0%{?enable_autoreconf}
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
%endif

Requires: dbus, polkit-pkla-compat
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Obsoletes: PolicyKit <= 0.10
Provides: PolicyKit = 0.11

# polkit saw some API/ABI changes from 0.96 to 0.97 so require a
# sufficiently new polkit-gnome package
Conflicts: polkit-gnome < 0.97

Obsoletes: polkit-desktop-policy < 0.103
Provides: polkit-desktop-policy = 0.103

Obsoletes: polkit-js-engine < 0.110-4
Provides: polkit-js-engine = %{version}-%{release}

# when -libs was split out, handle multilib upgrade path -- rex
Obsoletes: polkit < 0.113-3

%description
polkit is a toolkit for defining and handling authorizations.  It is
used for allowing unprivileged processes to speak to privileged
processes.

%package devel
Summary: Development files for polkit
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: %name-docs = %{version}-%{release}
Requires: glib2-devel
Obsoletes: PolicyKit-devel <= 0.10
Provides: PolicyKit-devel = 0.11

%description devel
Development files for polkit.

%package docs
Summary: Development documentation for polkit
Requires: %name-devel = %{version}-%{release}
Obsoletes: PolicyKit-docs <= 0.10
Provides: PolicyKit-docs = 0.11
BuildArch: noarch

%description docs
Development documentation for polkit.

%package libs
Summary: Libraries for polkit
%if 0%{?bundled_mozjs}
License: MIT and (MPLv1.1 or GPLv2+ or LGPLv2+) and MPLv2.0 and MPLv1.1 and BSD and GPLv2+ and GPLv3+ and LGPLv2+ and AFL and ASL 2.0
Provides: bundled(mozjs) = %{mozjs_version}
%endif

%description libs
Libraries files for polkit.


%prep
%setup -q

# Apply polkit patches
%patch1001 -p1
%patch1002 -p1
%patch1003 -p1
%patch1004 -p1
%patch1005 -p1

%if 0%{?bundled_mozjs}
# Extract mozjs archive
tar -xf %{S:2}

# Apply mozjs patches
pushd firefox-%{mozjs_version}
%patch02 -p1
%patch03 -p1
%patch09 -p1
%patch10 -p1

%patch12 -p1

%patch14 -p1
%patch15 -p1

%ifarch armv7hl
# Include definitions for user vfp on armv7 as it causes the compilation to fail without them
# https://bugzilla.mozilla.org/show_bug.cgi?id=1526653
%patch17 -p1
%endif

%ifarch s390x
%patch18 -p1
%endif

# Fixes for ppc64 and s390x, there is no need to keep it in ifarch here since mozilla tests support ifarch conditions
%patch19 -p1

# Export SharedArrayRawBufferRefs
%patch30 -p1

# Avoid autoconf213 dependency
%patch31 -p1 -b .autoconf213
%patch32 -p1 -b .autoconf213-2

# Remove zlib directory (to be sure using system version)
rm -rf modules/zlib
popd
%endif

%build
%if 0%{?bundled_mozjs}
pushd firefox-%{mozjs_version}/js/src
# Prefer GCC for now
export CC=gcc
export CXX=g++

# Workaround
# error: options `-C embed-bitcode=no` and `-C lto` are incompatible
# error: could not compile `jsrust`.
# https://github.com/japaric/cargo-call-stack/issues/25
export RUSTFLAGS="-C embed-bitcode"

# https://github.com/ptomato/mozjs/commit/36bb7982b41e0ef9a65f7174252ab996cd6777bd
export CARGO_PROFILE_RELEASE_LTO=true

export LINKFLAGS="%{?__global_ldflags}"
export PYTHON="%{__python3}"

%configure \
  --without-system-icu \
  --with-system-zlib \
  --disable-tests \
  --disable-strip \
  --with-intl-api \
  --enable-readline \
  --enable-shared-js \
  --enable-optimize \
  --disable-debug \
  --enable-pie \
  --disable-jemalloc

%if 0%{?big_endian}
echo "Generate big endian version of config/external/icu/data/icud67l.dat"
pushd ../..
  icupkg -tb config/external/icu/data/icudt67l.dat config/external/icu/data/icudt67b.dat
  rm -f config/external/icu/data/icudt*l.dat
popd
%endif

%make_build
popd

cat > mozjs-%{mozjs_major}.pc << EOF
Name: SpiderMonkey %{mozjs_version}
Description: The Mozilla library for JavaScript
Version: %{mozjs_version}

Libs: -L`pwd`/firefox-%{mozjs_version}/js/src/dist/bin -lmozjs-%{mozjs_major}
Cflags: -include `pwd`/firefox-%{mozjs_version}/js/src/dist/include/js/RequiredDefines.h -I`pwd`/firefox-%{mozjs_version}/js/src/dist/include
EOF
%endif

%if 0%{?enable_autoreconf}
autoreconf -i
%endif
# we can't use _hardened_build here, see
# https://bugzilla.redhat.com/show_bug.cgi?id=962005
export CFLAGS='-fPIC %optflags'
export LDFLAGS='-pie -Wl,-z,now -Wl,-z,relro'
%if 0%{?bundled_mozjs}
export PKG_CONFIG_PATH=`pwd`
export LD_LIBRARY_PATH=`pwd`/firefox-%{mozjs_version}/js/src/dist/bin
export LDFLAGS="$LDFLAGS -Wl,-rpath=%{_libdir}/polkit-1"
%endif
%configure --enable-gtk-doc \
        --disable-static \
        --enable-introspection \
        --disable-examples \
        --enable-libsystemd-login=yes
make V=1

%install
%if 0%{?bundled_mozjs}
mkdir -p %{buildroot}%{_libdir}/polkit-1
cp -p firefox-%{mozjs_version}/js/src/dist/bin/libmozjs-%{mozjs_major}.so %{buildroot}%{_libdir}/polkit-1/
%endif

%make_install \
    typelibsdir=%{_libdir}/girepository-1.0 \
    girdir=%{_datadir}/gir-1.0


rm -f $RPM_BUILD_ROOT%{_libdir}/*.la

%find_lang polkit-1

%check
%if 0%{?bundled_mozjs}
export LD_LIBRARY_PATH=`pwd`/firefox-%{mozjs_version}/js/src/dist/bin

pushd firefox-%{mozjs_version}/js/src
# Run SpiderMonkey tests
PYTHONPATH=tests/lib %{__python3} tests/jstests.py -d -s -t 1800 --no-progress --wpt=disabled ../../js/src/dist/bin/js

# Run basic JIT tests
PYTHONPATH=tests/lib %{__python3} jit-test/jit_test.py -s -t 1800 --no-progress ../../js/src/dist/bin/js basic
popd
%endif

%pre
getent group polkitd >/dev/null || groupadd -r polkitd
getent passwd polkitd >/dev/null || useradd -r -g polkitd -d / -s /sbin/nologin -c "User for polkitd" polkitd
exit 0

%post
# The implied (systemctl preset) will fail and complain, but the macro hides
# and ignores the fact.  This is in fact what we want, polkit.service does not
# have an [Install] section and it is always started on demand.
%systemd_post polkit.service

%preun
%systemd_preun polkit.service

%postun
%systemd_postun_with_restart polkit.service

%files -f polkit-1.lang
%doc COPYING NEWS README
%{_datadir}/man/man1/*
%{_datadir}/man/man8/*
%{_datadir}/dbus-1/system-services/*
%{_unitdir}/polkit.service
%dir %{_datadir}/polkit-1/
%dir %{_datadir}/polkit-1/actions
%attr(0700,polkitd,root) %dir %{_datadir}/polkit-1/rules.d
%{_datadir}/polkit-1/actions/org.freedesktop.policykit.policy
%dir %{_sysconfdir}/polkit-1
%{_sysconfdir}/polkit-1/rules.d/50-default.rules
%attr(0700,polkitd,root) %dir %{_sysconfdir}/polkit-1/rules.d
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.PolicyKit1.conf
%{_sysconfdir}/pam.d/polkit-1
%{_bindir}/pkaction
%{_bindir}/pkcheck
%{_bindir}/pkttyagent
%dir %{_prefix}/lib/polkit-1
%{_prefix}/lib/polkit-1/polkitd

# see upstream docs for why these permissions are necessary
%attr(4755,root,root) %{_bindir}/pkexec
%attr(4755,root,root) %{_prefix}/lib/polkit-1/polkit-agent-helper-1

%files devel
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%{_datadir}/gir-1.0/*.gir
%{_includedir}/*
%{_datadir}/gettext/its/polkit.its
%{_datadir}/gettext/its/polkit.loc

%files docs
%{_datadir}/gtk-doc

%ldconfig_scriptlets libs

%files libs
%{_libdir}/lib*.so.*
%{_libdir}/girepository-1.0/*.typelib
%if 0%{?bundled_mozjs}
%dir %{_libdir}/polkit-1
%{_libdir}/polkit-1/libmozjs-%{mozjs_major}.so
%endif

%changelog
* Fri Dec 02 2022 Jan Rybar <jrybar@redhat.com> - 0.117-11
- backport: restore tty only if changed
- Resolves: rhbz#2150310

* Mon Mar 07 2022 Jan Rybar <jrybar@redhat.com> - 0.117-10
- fixed CVE-2021-4115 patch application
- Resolves: rhbz#2062644

* Wed Feb 16 2022 Jan Rybar <jrybar@redhat.com> - 0.117-9
- file descriptor exhaustion (GHSL-2021-077)
- Resolves: CVE-2021-4115

* Thu Jan 27 2022 Jan Rybar <jrybar@redhat.com> - 0.117-8
- pkexec: argv overflow results in local privilege esc.
- Resolves: CVE-2021-4034

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 0.117-7
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Jun 30 2021 Kalev Lember <klember@redhat.com> - 0.117-6
- Bundle mozjs (#1958111)

* Mon Jun 28 2021 Jan Rybar <jrybar@redhat.com> - 0.117-5
- CVE-2021-3560 mitigation
- Resolves: CVE-2021-3560

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 0.117-4
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.117-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Aug 12 2020 Jan Rybar <jrybar@redhat.com> - 0.117-2
- update dependency to mozjs78

* Fri Jul 31 2020 Jan Rybar <jrybar@redhat.com> - 0.117-1
- Rebased to polkit-0.117

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.116-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 22 2020 Tom Stellard <tstellar@redhat.com> - 0.116-8
- Use make macros
- https://fedoraproject.org/wiki/Changes/UseMakeBuildInstallMacro

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.116-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Oct 25 2019 Jan Rybar <jrybar@redhat.com> - 0.116-6
- jsauthority memleak fix

* Fri Sep 27 2019 Jan Rybar <jrybar@redhat.com> - 0.116-5
- pkttyagent: unread input flushed on terminal restore

* Sun Sep 08 2019 Kalev Lember <klember@redhat.com> - 0.116-4
- Rebuilt for mozjs60 s390x fixes

* Fri Aug 02 2019 Jan Rybar <jrybar@redhat.com> - 0.116-3
- pkttyagent: backport patch, get SIGTTOU in background job

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.116-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu May 02 2019 Pete Walter <pwalter@fedoraproject.org> - 0.116-1
- Update to 0.116

* Thu Feb 14 2019 Jan Rybar <jrybar@redhat.com> - 0.115-11
- pkttyagent: PolkitAgentTextListener leaves echo tty disabled if SIGINT/SIGTERM

* Fri Feb 08 2019 Pete Walter <pwalter@fedoraproject.org> - 0.115-10
- Move to mozjs60

* Tue Feb 05 2019 Jan Rybar <jrybar@redhat.com> - 0.115-9
- Allow uid=-1 for PolkitUnixProcess

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.115-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Jan 08 2019 Colin Walters <walters@verbum.org> - 0.115-7
- Add security fix for
  https://bugs.chromium.org/p/project-zero/issues/detail?id=1692

* Fri Dec 07 2018 Jan Rybar <jrybar@redhat.com> - 0.115-6
- Fix of CVE-2018-19788, priv escalation with high UIDs
- Resolves: rhbz#1655926

* Thu Sep 27 2018 Owen Taylor <otaylor@redhat.com> - 0.115-5
- Fix installation with prefix != /usr

* Mon Aug 13 2018 Jan Rybar <jrybar@redhat.com> - 0.115-4
- Leaking zombie processess started by rules

* Fri Jul 20 2018 Jan Rybar <jrybar@redhat.com> - 0.115-3
- Warning raised by polkit when disconnected from ssh
- polkitagentlistener: resource leak - pointer to 'server'
- Error message raised on every 'systemctl start' in emergency.target

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.115-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jul 10 2018 Miloslav Trmač <mitr@redhat.com> - 0.115-1
- Update to 0.115 (CVE-2018-1116)

* Tue Apr 03 2018 Ray Strode <rstrode@redhat.com> - 0.114-1
- Update to 0.114

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.113-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.113-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.113-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Apr 13 2017 Richard Hughes <rhughes@redhat.com> - 0.113-13
- Add the its files from upstream.

* Tue Apr 4 2017 Miloslav Trmač <mitr@redhat.com> - 0.113-12
- Fix a memory leak in PolkitPermission.
  Patch by Rui Matos <tiagomatos@gmail.com>
  Resolves: #1433915

* Tue Apr 4 2017 Miloslav Trmač <mitr@redhat.com> - 0.113-11
- Revert back to the state in 0.113-7, undoing the untested changes.

* Tue Apr  4 2017 Peter Robinson <pbrobinson@fedoraproject.org> 0.113-10
- Move to an upstream snapshot, rebase patches

* Fri Mar 31 2017 Rex Dieter <rdieter@fedoraproject.org> - 0.113-9
- restore Provides: polkit-desktop-policy polkit-js-engine

* Thu Mar 30 2017 Peter Robinson <pbrobinson@fedoraproject.org> 0.113-8
- Use %%license, license needs to be in -libs as it's the only guaranteed installed package
- Move to mozjs38
- Other upstream fixes
- Spec cleanups

* Mon Feb 13 2017 Miloslav Trmač <mitr@redhat.com> - 0.113-7
- Fix memory leaks when calling authentication agents
  Resolves: #1380166

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.113-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.113-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jul 14 2015 Miloslav Trmač <mitr@redhat.com> - 0.113-4
- Bump the Obsoletes: to < 0.113-3 to account for the non-split 0.113-2.fc21
  Resolves: #1243004

* Sun Jul 12 2015 Rex Dieter <rdieter@fedoraproject.org> 0.113-3
- Obsoletes: polkit < 0.112-8 (handle multilib upgrade path)

* Fri Jul 10 2015 Miloslav Trmač <mitr@redhat.com> - 0.113-2
- Add a fully versioned dependency from polkit to polkit-libs
  Resolves: #1241759
- Require polkit-libs, not polkit, in polkit-devel

* Thu Jul 2 2015 Miloslav Trmač <mitr@redhat.com> - 0.113-1
- Update to polkit-0.113 (CVE-2015-3218, CVE-2015-3255, CVE-2015-3256,
  CVE-2015-4625)
  Resolves: #910262, #1175061, #1177930, #1194391, #1228739, #1233810

* Fri Jun 19 2015 Miloslav Trmač <mitr@redhat.com> - 0.112-11
- Add BuildRequires: systemd so that %%{_unitdir} is defined, to fix the build.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.112-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Jan 25 2015 Rex Dieter <rdieter@fedoraproject.org>  - 0.112-9
- polkit doesn't release reference counters of GVariant data (#1180886)
- fix ldconfig scriptlets (move to -libs subpkg)

* Sat Nov 08 2014 Colin Walters <walters@redhat.com> - 0.112-8
- Split separate -libs package, so that NetworkManager can just depend on
  that, without dragging in the daemon (as well as libmozjs17).  This
  allows the creation of more minimal systems that want programs like NM,
  but do not need the configurability of the daemon; it would be ok if only
  root is authorized.

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.112-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jul 22 2014 Kalev Lember <kalevlember@gmail.com> - 0.112-6
- Rebuilt for gobject-introspection 1.41.4

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.112-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jun  5 2014 Kay Sievers <kay@redhat.com> - 0.112-4
- backport upstream D-Bus "user bus" changes

* Mon Feb 10 2014 Miloslav Trmač <mitr@redhat.com> - 0.112-3
- Fix a PolkitAgentSession race condition
  Resolves: #1063193

* Sat Dec  7 2013 Miloslav Trmač <mitr@redhat.com> - 0.112-2
- Workaround pam_systemd setting broken XDG_RUNTIME_DIR
  Resolves: #1033774
- Always use mozjs-17.0 even if js-devel is installed

* Wed Sep 18 2013 Miloslav Trmač <mitr@redhat.com> - 0.112-1
- Update to polkit-0.112
- Resolves: #1009538, CVE-2013-4288

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.111-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed May 29 2013 Tomas Bzatek <tbzatek@redhat.com> - 0.111-2
- Fix a race on PolkitSubject type registration (#866718)

* Wed May 15 2013 Miloslav Trmač <mitr@redhat.com> - 0.111-1
- Update to polkit-0.111
  Resolves: #917888
- Use SpiderMonkey from mozjs17 instead of js
- Ship the signature in the srpm
- Try to preserve timestamps in (make install)

* Fri May 10 2013 Miloslav Trmač <mitr@redhat.com> - 0.110-4
- Shut up rpmlint about Summary:
- Build with V=1
- Use %%{_unitdir} instead of hard-coding the path
- Use the new systemd macros, primarily to run (systemctl daemon-reload)
  Resolves: #857382

* Fri May 10 2013 Miloslav Trmač <mitr@redhat.com> - 0.110-4
- Make the JavaScript engine mandatory.  The polkit-js-engine package has been
  removed, main polkit package Provides:polkit-js-engine for compatibility.
- Add Requires: polkit-pkla-compat
  Resolves: #908808

* Wed Feb 13 2013 Miloslav Trmač <mitr@redhat.com> - 0.110-3
- Don't ship pk-example-frobnicate in the "live" configuration
  Resolves: #878112

* Fri Feb  8 2013 Miloslav Trmač <mitr@redhat.com> - 0.110-2
- Own %%{_docdir}/polkit-js-engine-*
  Resolves: #907668

* Wed Jan  9 2013 David Zeuthen <davidz@redhat.com> - 0.110-1%{?dist}
- Update to upstream release 0.110

* Mon Jan  7 2013 Matthias Clasen <mclasen@redhat.com> - 0.109-2%{?dist}
- Build with pie and stuff

* Wed Dec 19 2012 David Zeuthen <davidz@redhat.com> 0.109-1%{?dist}
- Update to upstream release 0.109
- Drop upstreamed patches

* Thu Nov 15 2012 David Zeuthen <davidz@redhat.com> 0.108-3%{?dist}
- Attempt to open the correct libmozjs185 library, otherwise polkit
  authz rules will not work unless js-devel is installed (fdo #57146)

* Wed Nov 14 2012 David Zeuthen <davidz@redhat.com> 0.108-2%{?dist}
- Include gmodule-2.0 to avoid build error

* Wed Nov 14 2012 David Zeuthen <davidz@redhat.com> 0.108-1%{?dist}
- Update to upstream release 0.108
- Drop upstreamed patches
- This release dynamically loads the JavaScript interpreter and can
  cope with it not being available. In this case, polkit authorization
  rules are not processed and the defaults for an action - as defined
  in its .policy file - are used for authorization decisions.
- Add new meta-package, polkit-js-engine, that pulls in the required
  JavaScript bits to make polkit authorization rules work. The default
  install - not the minimal install - should include this package

* Wed Oct 10 2012 Adam Jackson <ajax@redhat.com> 0.107-4
- Don't crash if initializing the server object fails

* Tue Sep 18 2012 David Zeuthen <davidz@redhat.com> 0.107-3%{?dist}
- Authenticate as root if e.g. the wheel group is empty (#834494)

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.107-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 David Zeuthen <davidz@redhat.com> 0.107-1%{?dist}
- Update to upstream release 0.107

* Fri Jun 29 2012 David Zeuthen <davidz@redhat.com> 0.106-2%{?dist}
- Add forgotten Requires(pre): shadow-utils

* Thu Jun 07 2012 David Zeuthen <davidz@redhat.com> 0.106-1%{?dist}
- Update to upstream release 0.106
- Authorizations are no longer controlled by .pkla files - from now
  on, use the new .rules files described in the polkit(8) man page

* Tue Apr 24 2012 David Zeuthen <davidz@redhat.com> 0.105-1%{?dist}
- Update to upstream release 0.105
- Nuke patches that are now upstream
- Change 'PolicyKit' to 'polkit' in summary and descriptions

* Thu Mar 08 2012 David Zeuthen <davidz@redhat.com> 0.104-6%{?dist}
- Don't leak file descriptors (bgo #671486)

* Mon Feb 13 2012 Matthias Clasen <mclasen@redhat.com> - 0.104-5%{?dist}
- Make the -docs subpackage noarch

* Mon Feb 06 2012 David Zeuthen <davidz@redhat.com> 0.104-4%{?dist}
- Set error if we cannot obtain a PolkitUnixSession for a given PID (#787222)

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.104-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Jan 03 2012 David Zeuthen <davidz@redhat.com> 0.104-2%{?dist}
- Nuke the ConsoleKit run-time requirement

* Tue Jan 03 2012 David Zeuthen <davidz@redhat.com> 0.104-1%{?dist}
- Update to upstream release 0.104
- Force usage of systemd (instead of ConsoleKit) for session tracking

* Tue Dec 06 2011 David Zeuthen <davidz@redhat.com> 0.103-1%{?dist}
- Update to upstream release 0.103
- Drop upstreamed patch
- Drop Fedora-specific policy, it is now upstream (fdo #41008)

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.102-3
- Rebuilt for glibc bug#747377

* Tue Oct 18 2011 David Zeuthen <davidz@redhat.com> 0.102-2%{?dist}
- Add patch to neuter the annoying systemd behavior where stdout/stderr
  is sent to the system logs

* Thu Aug 04 2011 David Zeuthen <davidz@redhat.com> 0.102-1
- Update to 0.102 release

* Fri May 13 2011 Bastien Nocera <bnocera@redhat.com> 0.101-7
- Allow setting the pretty hostname without a password for wheel,
  change matches systemd in git

* Mon May  2 2011 Matthias Clasen <mclasen@redhat.com> - 0.101-6
- Update the action id of the datetime mechanism

* Tue Apr 19 2011 David Zeuthen <davidz@redhat.com> - 0.101-5
- CVE-2011-1485 (#697951)

* Tue Mar 22 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> - 0.101-4
- Also allow org.kde.kcontrol.kcmclock.save without password for wheel

* Thu Mar 17 2011 David Zeuthen <davidz@redhat.com> - 0.101-3
- Fix typo in pkla file (thanks notting)

* Thu Mar 17 2011 David Zeuthen <davidz@redhat.com> - 0.101-2
- Nuke desktop_admin_r and desktop_user_r groups - just use the
  wheel group instead (#688363)
- Update the set of configuration directives that gives users
  in the wheel group extra privileges

* Thu Mar 03 2011 David Zeuthen <davidz@redhat.com> - 0.101-1
- New upstream version

* Mon Feb 21 2011 David Zeuthen <davidz@redhat.com> - 0.100-1
- New upstream version

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.98-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 28 2011 Matthias Clasen <mclasen@redhat.com> - 0.98-6
- Own /usr/libexec/polkit-1

* Fri Nov 12 2010 Matthias Clasen <mclasen@redhat.com> - 0.98-5
- Enable introspection

* Thu Sep 02 2010 David Zeuthen <davidz@redhat.com> - 0.98-4
- Fix #629515 in a way that doesn't require autoreconf

* Thu Sep 02 2010 David Zeuthen <davidz@redhat.com> - 0.98-2
- Include polkitagentenumtypes.h (#629515)

* Mon Aug 23 2010 Matthias Clasen <mclasen@redhat.com> - 0.98-1
- Update to upstream release 0.98
- Co-own /usr/share/gtk-doc (#604410)

* Wed Aug 18 2010 Matthias Clasen <mclasen@redhat.com> - 0.97-5
- Rebuid to work around bodhi limitations

* Wed Aug 18 2010 Matthias Clasen <mclasen@redhat.com> - 0.97-4
- Fix a ConsoleKit interaction bug

* Fri Aug 13 2010 David Zeuthen <davidz@redhat.com> - 0.97-3
- Add a patch to make pkcheck(1) work the way libvirtd uses it (#623257)
- Require GLib >= 2.25.12 instead of 2.25.11
- Ensure polkit-gnome packages earlier than 0.97 are not used with
  these packages

* Mon Aug 09 2010 David Zeuthen <davidz@redhat.com> - 0.97-2
- Rebuild

* Mon Aug 09 2010 David Zeuthen <davidz@redhat.com> - 0.97-1
- Update to 0.97. This release contains a port from EggDBus to the
  GDBus code available in recent GLib releases.

* Fri Jan 15 2010 David Zeuthen <davidz@redhat.com> - 0.96-1
- Update to 0.96
- Disable introspection support for the time being

* Fri Nov 13 2009 David Zeuthen <davidz@redhat.com> - 0.95-2
- Rebuild

* Fri Nov 13 2009 David Zeuthen <davidz@redhat.com> - 0.95-1
- Update to 0.95
- Drop upstreamed patches

* Tue Oct 20 2009 Matthias Clasen <mclasen@redhat.com> - 0.95-0.git20090913.3
- Fix a typo in pklocalauthority(8)

* Mon Sep 14 2009 David Zeuthen <davidz@redhat.com> - 0.95-0.git20090913.2
- Refine how Obsolete: is used and also add Provides: (thanks Jesse
  Keating and nim-nim)

* Mon Sep 14 2009 David Zeuthen <davidz@redhat.com> - 0.95-0.git20090913.1
- Add bugfix for polkit_unix_process_new_full() (thanks Bastien Nocera)
- Obsolete old PolicyKit packages

* Sun Sep 13 2009 David Zeuthen <davidz@redhat.com> - 0.95-0.git20090913
- Update to git snapshot
- Drop upstreamed patches
- Turn on GObject introspection
- Don't delete desktop_admin_r and desktop_user_r groups when
  uninstalling polkit-desktop-policy

* Fri Sep 11 2009 David Zeuthen <davidz@redhat.com> - 0.94-4
- Add some patches from git master
- Sort pkaction(1) output
- Bug 23867 – UnixProcess vs. SystemBusName aliasing

* Thu Aug 13 2009 David Zeuthen <davidz@redhat.com> - 0.94-3
- Add desktop_admin_r and desktop_user_r groups along with a first cut
  of default authorizations for users in these groups.

* Wed Aug 12 2009 David Zeuthen <davidz@redhat.com> - 0.94-2
- Disable GObject Introspection for now as it breaks the build

* Wed Aug 12 2009 David Zeuthen <davidz@redhat.com> - 0.94-1
- Update to upstream release 0.94

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.93-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 20 2009 David Zeuthen <davidz@redhat.com> - 0.93-2
- Rebuild

* Mon Jul 20 2009 David Zeuthen <davidz@redhat.com> - 0.93-1
- Update to 0.93

* Tue Jun 09 2009 David Zeuthen <davidz@redhat.com> - 0.92-3
- Don't make docs noarch (I *heart* multilib)
- Change license to LGPLv2+

* Mon Jun 08 2009 David Zeuthen <davidz@redhat.com> - 0.92-2
- Rebuild

* Mon Jun 08 2009 David Zeuthen <davidz@redhat.com> - 0.92-1
- Update to 0.92 release

* Wed May 27 2009 David Zeuthen <davidz@redhat.com> - 0.92-0.git20090527
- Update to 0.92 snapshot

* Mon Feb  9 2009 David Zeuthen <davidz@redhat.com> - 0.91-1
- Initial spec file.
