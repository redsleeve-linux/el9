Name:		librdkafka
Version:	1.6.1
Release:	102%{?dist}
Summary:	The Apache Kafka C library

License:	BSD
URL:		https://github.com/edenhill/librdkafka
Source0:	%{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	make
BuildRequires:	python3
BuildRequires:	libzstd-devel
BuildRequires:	lz4-devel
BuildRequires:	openssl-devel
BuildRequires:	cyrus-sasl-devel
BuildRequires:	zlib-devel
BuildRequires:	rapidjson-devel

Patch0: rsyslog-1.6.1-rhbz2032923-crypto-compliance.patch

%description
Librdkafka is a C/C++ library implementation of the Apache Kafka protocol,
containing both Producer and Consumer support.
It was designed with message delivery reliability and high performance in mind,
current figures exceed 800000 messages/second for the producer and 3 million
messages/second for the consumer.

%package	devel
Summary:	The Apache Kafka C library (Development Environment)
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description	devel
librdkafka is a C/C++ library implementation of the Apache Kafka protocol,
containing both Producer and Consumer support.
This package contains headers and libraries required to build applications
using librdkafka.

%prep
%autosetup -p1

%build
# This package has a configure test which uses ASMs, but does not link the
# resultant .o files.  As such the ASM test is always successful, even on
# architectures were the ASM is not valid when compiling with LTO.
#
# -ffat-lto-objects is sufficient to address this issue.  It is the default
# for F33, but is expected to only be enabled for packages that need it in
# F34, so we use it here explicitly
%define _lto_cflags -flto=auto -ffat-lto-objects

%configure \
    --enable-zlib \
    --enable-zstd \
    --enable-lz4 \
    --enable-lz4-ext \
    --enable-ssl \
    --enable-gssapi \
    --enable-sasl

%make_build

%check
make check

%install
%make_install
find %{buildroot} -name '*.a' -delete -print
find %{buildroot} -name '*-static.pc' -delete -print

%ldconfig_scriptlets

%files
%{_libdir}/librdkafka.so.*
%{_libdir}/librdkafka++.so.*
%doc README.md CONFIGURATION.md INTRODUCTION.md LICENSE LICENSES.txt STATISTICS.md CHANGELOG.md
%license LICENSE LICENSE.pycrc LICENSE.snappy

%files devel
%dir %{_includedir}/librdkafka
%attr(0644,root,root) %{_includedir}/librdkafka/*
%attr(0755,root,root) %{_libdir}/librdkafka.so
%attr(0755,root,root) %{_libdir}/librdkafka++.so
%{_libdir}/pkgconfig/rdkafka.pc
%{_libdir}/pkgconfig/rdkafka++.pc


%changelog
* Tue Feb 08 2022 Sergio Arroutbi <sarroutb@redhat.com> - 1.6.1-102
- Changes for tests to compile and run appropriately
  Related: rhbz#2032923

* Mon Feb 07 2022 Sergio Arroutbi <sarroutb@redhat.com> - 1.6.1-101
- Add missing tests
  Related: rhbz#2032923

* Fri Feb 04 2022 Sergio Arroutbi <sarroutb@redhat.com> - 1.6.1-100
- Fix for rpmlint reporting crypto-policy-non-compliance-openssl
  resolves: rhbz#2032923

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.6.1-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Jun 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.6.1-3
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.6.1-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Mon Mar 08 2021 Attila Lakatos <alakatos@redhat.com> - 1.6.1-1
- Update to upstream 1.6.1
  resolves: rhbz#1932286

* Wed Feb 03 2021 Neal Gompa <ngompa@datto.com> - 1.6.0-1
- Update to upstream 1.6.0
  resolves: rhbz#1883910
- Enable all missing features
- Fix linking to external lz4 library
- Minor spec cleanups

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Sep 09 2020 Zoltan Fridrich <zfridric@redhat.com> - 1.5.0-1
- Update to upstream 1.5.0
  resolves: rhbz#1818082

* Wed Sep 09 2020 Zoltan Fridrich <zfridric@redhat.com> - 1.3.0-6
- Switch BuildRequires from python2 to python3
  resolves: rhbz#1808329

* Fri Aug 21 2020 Jeff Law <law@redhat.com> - 1.3.0-5
- Re-enable LTO

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jun 30 2020 Jeff Law <law@redhat.com> - 1.3.0-3
- Disable LTO

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Dec 30 2019 Michal Luscon <mluscon@gmail.com> - 1.3.0-1
- Update to upstream 1.3.0

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Dec 12 2018 Javier Peña <jpena@redhat.com> - 0.11.6-1
- Update to upstream 0.11.6

* Mon Sep 17 2018 Michal Luscon <mluscon@gmail.com> - 0.11.5-1
- Update to upstream 0.11.5

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Apr 20 2018 Michal Luscon <mluscon@gmail.com> - 0.11.4-1
- Update to upstream 0.11.4

* Thu Mar 15 2018 Iryna Shcherbina <ishcherb@redhat.com> - 0.11.3-3
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 09 2018 Michal Luscon <mluscon@gmail.com> - 0.11.3-1
- Update to upstream 0.11.3

* Thu Nov 02 2017 Michal Luscon <mluscon@gmail.com> - 0.11.1-1
- Update to upstream 0.11.1

* Thu Aug 31 2017 Michal Luscon <mluscon@gmail.com> - 0.11.0-1
- Update to 0.11.0

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon May 22 2017 Radovan Sroka <rsroka@redhat.com> - 0.9.5-1
- Update to 0.9.4

* Sat Mar 11 2017 Michal Luscon <mluscon@gmail.com> - 0.9.4-1
- Update to 0.9.4
- enable lz4, ssl, sasl

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild


* Fri Nov 11 2016 Radovan Sroka <rsroka@redhat.com> 0.9.2-1
- 0.9.2 release
- package created
