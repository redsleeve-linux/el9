# SystemTap support is disabled by default
%{!?sdt:%global sdt 0}

#http://lists.fedoraproject.org/pipermail/devel/2011-August/155358.html
%global _hardened_build 1

# Where dhcp configuration files are stored
%global dhcpconfdir %{_sysconfdir}/dhcp


%global prever b1
#global patchver P1
%global DHCPVERSION %{version}%{?prever}%{?patchver:-%{patchver}}

Summary:  Dynamic host configuration protocol software
Name:     dhcp
Version:  4.4.2
Release:  18.b1%{?dist}

# NEVER CHANGE THE EPOCH on this package.  The previous maintainer (prior to
# dcantrell maintaining the package) made incorrect use of the epoch and
# that's why it is at 12 now.  It should have never been used, but it was.
# So we are stuck with it.
Epoch:    12
License:  ISC
Url:      https://www.isc.org/dhcp/
Source0:  ftp://ftp.isc.org/isc/dhcp/%{DHCPVERSION}/dhcp-%{DHCPVERSION}.tar.gz
Source1:  dhclient-script
Source2:  README.dhclient.d
Source3:  11-dhclient
Source5:  56dhclient
Source6:  dhcpd.service
Source7:  dhcpd6.service
Source8:  dhcrelay.service
Source9:  dhcp.sysusers

Patch1: 0001-change-bug-url.patch
Patch2: 0002-additional-dhclient-options.patch
Patch3: 0003-Handle-releasing-interfaces-requested-by-sbin-ifup.patch
Patch4: 0004-Support-unicast-BOOTP-for-IBM-pSeries-systems-and-ma.patch
Patch5: 0005-Change-default-requested-options.patch
Patch6: 0006-Various-man-page-only-fixes.patch
Patch7: 0007-Change-paths-to-conform-to-our-standards.patch
Patch8: 0008-Make-sure-all-open-file-descriptors-are-closed-on-ex.patch
Patch9: 0009-Fix-garbage-in-format-string-error.patch
Patch10: 0010-Handle-null-timeout.patch
Patch11: 0011-Drop-unnecessary-capabilities.patch
Patch12: 0012-RFC-3442-Classless-Static-Route-Option-for-DHCPv4-51.patch
Patch13: 0013-DHCPv6-over-PPP-support-626514.patch
Patch14: 0014-IPoIB-support-660681.patch
Patch15: 0015-Add-GUID-DUID-to-dhcpd-logs-1064416.patch
Patch16: 0016-Turn-on-creating-sending-of-DUID.patch
Patch17: 0017-Send-unicast-request-release-via-correct-interface.patch
Patch18: 0018-No-subnet-declaration-for-iface-should-be-info-not-e.patch
Patch19: 0019-dhclient-write-DUID_LLT-even-in-stateless-mode-11563.patch
Patch20: 0020-Discover-all-hwaddress-for-xid-uniqueness.patch
Patch21: 0021-Load-leases-DB-in-non-replay-mode-only.patch
Patch22: 0022-dhclient-make-sure-link-local-address-is-ready-in-st.patch
Patch23: 0023-option-97-pxe-client-id.patch
Patch24: 0024-Detect-system-time-changes.patch
Patch25: 0025-bind-Detect-system-time-changes.patch
Patch26: 0026-Add-dhclient-5-B-option-description.patch
Patch27: 0027-Add-missed-sd-notify-patch-to-manage-dhcpd-with-syst.patch
Patch28: 0028-Fix-for-CVE-2021-25217.patch
Patch29: 0029-Use-system-getaddrinfo-for-dhcp.patch
Patch30: CVE-2021-25220.patch
Patch31: omshell-hmac-sha512-support.patch
Patch32: CVE-2022-2928.patch
Patch33: CVE-2022-2929.patch


BuildRequires: autoconf
BuildRequires: automake
BuildRequires: make
BuildRequires: libtool
BuildRequires: openldap-devel
# --with-ldap-gssapi
BuildRequires: krb5-devel
BuildRequires: libcap-ng-devel
# https://fedorahosted.org/fpc/ticket/502#comment:3
BuildRequires: systemd systemd-devel
# dhcp-sd_notify.patch
BuildRequires: pkgconfig(libsystemd)
%if ! 0%{?_module_build}
BuildRequires: doxygen
%endif
%if %{sdt}
BuildRequires: systemtap-sdt-devel
%global tapsetdir    /usr/share/systemtap/tapset
%endif
BuildRequires: systemd-rpm-macros

# In _docdir we ship some perl scripts and module from contrib subdirectory.
# Because nothing under _docdir is allowed to "require" anything,
# prevent _docdir from being scanned. (#674058)
%filter_requires_in %{_docdir}
%{filter_setup}

%description
DHCP (Dynamic Host Configuration Protocol)

%package server
Summary: Provides the ISC DHCP server
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires(post): coreutils grep sed
%{?sysusers_requires_compat}
%{?systemd_requires}

%description server
DHCP (Dynamic Host Configuration Protocol) is a protocol which allows
individual devices on an IP network to get their own network
configuration information (IP address, subnetmask, broadcast address,
etc.) from a DHCP server. The overall purpose of DHCP is to make it
easier to administer a large network.

This package provides the ISC DHCP server.

%package relay
Summary: Provides the ISC DHCP relay agent
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires(post): grep sed
%{?systemd_requires}

%description relay
DHCP (Dynamic Host Configuration Protocol) is a protocol which allows
individual devices on an IP network to get their own network
configuration information (IP address, subnetmask, broadcast address,
etc.) from a DHCP server. The overall purpose of DHCP is to make it
easier to administer a large network.

This package provides the ISC DHCP relay agent.


%package client
Summary: Provides the ISC DHCP client daemon and dhclient-script
Provides: dhclient = %{epoch}:%{version}-%{release}
Obsoletes: dhclient < %{epoch}:%{version}-%{release}
# dhclient-script requires:
Requires: coreutils gawk grep ipcalc iproute iputils sed systemd
Requires: %{name}-common = %{epoch}:%{version}-%{release}
# Old NetworkManager expects the dispatcher scripts in a different place
Conflicts: NetworkManager < 1.20

%description client
DHCP (Dynamic Host Configuration Protocol) is a protocol which allows
individual devices on an IP network to get their own network
configuration information (IP address, subnetmask, broadcast address,
etc.) from a DHCP server. The overall purpose of DHCP is to make it
easier to administer a large network.

This package provides the ISC DHCP client.

%package common
Summary: Common files used by ISC dhcp client, server and relay agent
BuildArch: noarch
Obsoletes: dhcp-libs < %{epoch}:%{version}



%description common
DHCP (Dynamic Host Configuration Protocol) is a protocol which allows
individual devices on an IP network to get their own network
configuration information (IP address, subnetmask, broadcast address,
etc.) from a DHCP server. The overall purpose of DHCP is to make it
easier to administer a large network.

This package provides common files used by dhcp and dhclient package.

%package libs-static
Summary: Shared libraries used by ISC dhcp client and server
Provides: %{name}-libs%{?_isa} =  %{epoch}:%{version}-%{release}
Provides: %{name}-libs =  %{epoch}:%{version}-%{release}
Provides: bundled(bind-export-libs)
Provides: bundled(bind)

%description libs-static
This package contains shared libraries used by ISC dhcp client and server


%package devel
Summary: Development headers and libraries for interfacing to the DHCP server
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}

%description devel
Header files and API documentation for using the ISC DHCP libraries.  The
libdhcpctl and libomapi static libraries are also included in this package.

%if ! 0%{?_module_build}
%package devel-doc
Summary: Developer's Guide for ISC DHCP
Requires: %{name}-libs = %{epoch}:%{version}-%{release}
BuildArch: noarch

%description devel-doc
This documentation is intended for developers, contributors and other
programmers that are interested in internal operation of the code.
This package contains doxygen-generated documentation.
%endif

%prep
%setup -n dhcp-%{DHCPVERSION}
pushd bind
tar -xf bind.tar.gz
ln -s bind-9* bind
popd
%autopatch -p1 

# Update paths in all man pages
for page in client/dhclient.conf.5 client/dhclient.leases.5 \
            client/dhclient-script.8 client/dhclient.8 ; do
    sed -i -e 's|CLIENTBINDIR|%{_sbindir}|g' \
                -e 's|RUNDIR|%{_localstatedir}/run|g' \
                -e 's|DBDIR|%{_localstatedir}/lib/dhclient|g' \
                -e 's|ETCDIR|%{dhcpconfdir}|g' $page
done

for page in server/dhcpd.conf.5 server/dhcpd.leases.5 server/dhcpd.8 ; do
    sed -i -e 's|CLIENTBINDIR|%{_sbindir}|g' \
                -e 's|RUNDIR|%{_localstatedir}/run|g' \
                -e 's|DBDIR|%{_localstatedir}/lib/dhcpd|g' \
                -e 's|ETCDIR|%{dhcpconfdir}|g' $page
done

sed -i -e 's|/var/db/|%{_localstatedir}/lib/dhcpd/|g' contrib/dhcp-lease-list.pl

## FIXME drop unused bind components 

%build
#libtoolize --copy --force
autoreconf --verbose --force --install

CFLAGS="%{optflags} -fno-strict-aliasing -fcommon" \
%configure \
    --with-srv-lease-file=%{_localstatedir}/lib/dhcpd/dhcpd.leases \
    --with-srv6-lease-file=%{_localstatedir}/lib/dhcpd/dhcpd6.leases \
    --with-cli-lease-file=%{_localstatedir}/lib/dhclient/dhclient.leases \
    --with-cli6-lease-file=%{_localstatedir}/lib/dhclient/dhclient6.leases \
    --with-srv-pid-file=%{_localstatedir}/run/dhcpd.pid \
    --with-srv6-pid-file=%{_localstatedir}/run/dhcpd6.pid \
    --with-cli-pid-file=%{_localstatedir}/run/dhclient.pid \
    --with-cli6-pid-file=%{_localstatedir}/run/dhclient6.pid \
    --with-relay-pid-file=%{_localstatedir}/run/dhcrelay.pid \
    --with-ldap \
    --with-ldapcrypto \
    --with-ldap-gssapi \
    --enable-log-pid \
%if %{sdt}
    --enable-systemtap \
    --with-tapset-install-dir=%{tapsetdir} \
%endif
    --enable-paranoia --enable-early-chroot \
    --enable-binary-leases \
    --with-systemd
make -j1

%if ! 0%{?_module_build}
pushd doc
make %{?_smp_mflags} devel
popd
%endif

%install
make DESTDIR=%{buildroot} install %{?_smp_mflags}

# We don't want example conf files in /etc
rm -f %{buildroot}%{_sysconfdir}/dhclient.conf.example
rm -f %{buildroot}%{_sysconfdir}/dhcpd.conf.example

# dhclient-script
install -D -p -m 0755 %{SOURCE1} %{buildroot}%{_sbindir}/dhclient-script

# README.dhclient.d
install -p -m 0644 %{SOURCE2} .

# Empty directory for dhclient.d scripts
mkdir -p %{buildroot}%{dhcpconfdir}/dhclient.d

# NetworkManager dispatcher script
mkdir -p %{buildroot}%{_prefix}/lib/NetworkManager/dispatcher.d
install -p -m 0755 %{SOURCE3} %{buildroot}%{_prefix}/lib/NetworkManager/dispatcher.d

# pm-utils script to handle suspend/resume and dhclient leases
install -D -p -m 0755 %{SOURCE5} %{buildroot}%{_libdir}/pm-utils/sleep.d/56dhclient

# systemd unit files
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE6} %{buildroot}%{_unitdir}
install -m 644 %{SOURCE7} %{buildroot}%{_unitdir}
install -m 644 %{SOURCE8} %{buildroot}%{_unitdir}

# systemd-sysusers
install -p -D -m 0644 %{SOURCE9} %{buildroot}%{_sysusersdir}/dhcp.conf

# Start empty lease databases
mkdir -p %{buildroot}%{_localstatedir}/lib/dhcpd/
touch %{buildroot}%{_localstatedir}/lib/dhcpd/dhcpd.leases
touch %{buildroot}%{_localstatedir}/lib/dhcpd/dhcpd6.leases
mkdir -p %{buildroot}%{_localstatedir}/lib/dhclient/

# default sysconfig file for dhcpd
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cat <<EOF > %{buildroot}%{_sysconfdir}/sysconfig/dhcpd
# WARNING: This file is NOT used anymore.

# If you are here to restrict what interfaces should dhcpd listen on,
# be aware that dhcpd listens *only* on interfaces for which it finds subnet
# declaration in dhcpd.conf. It means that explicitly enumerating interfaces
# also on command line should not be required in most cases.

# If you still insist on adding some command line options,
# copy dhcpd.service from /lib/systemd/system to /etc/systemd/system and modify
# it there.
# https://fedoraproject.org/wiki/Systemd#How_do_I_customize_a_unit_file.2F_add_a_custom_unit_file.3F

# example:
# $ cp /usr/lib/systemd/system/dhcpd.service /etc/systemd/system/
# $ vi /etc/systemd/system/dhcpd.service
# $ ExecStart=/usr/sbin/dhcpd -f -cf /etc/dhcp/dhcpd.conf -user dhcpd -group dhcpd --no-pid <your_interface_name(s)>
# $ systemctl --system daemon-reload
# $ systemctl restart dhcpd.service
EOF

# Copy sample conf files into position (called by doc macro)
cp -p doc/examples/dhclient-dhcpv6.conf client/dhclient6.conf.example
cp -p doc/examples/dhcpd-dhcpv6.conf server/dhcpd6.conf.example

cat << EOF > client/dhclient-enter-hooks
#!/bin/bash

# For dhclient/dhclient-script debugging.
# Copy this into /etc/dhcp/ and make it executable.
# Run 'dhclient -d <interface>' to see info passed from dhclient to dhclient-script.
# See also HOOKS section in dhclient-script(8) man page.

echo "interface: ${interface}"
echo "reason: ${reason}"

( set -o posix ; set ) | grep "old_"
( set -o posix ; set ) | grep "new_"
( set -o posix ; set ) | grep "alias_"
( set -o posix ; set ) | grep "requested_"
EOF

# Install default (empty) dhcpd.conf:
mkdir -p %{buildroot}%{dhcpconfdir}
cat << EOF > %{buildroot}%{dhcpconfdir}/dhcpd.conf
#
# DHCP Server Configuration file.
#   see /usr/share/doc/dhcp-server/dhcpd.conf.example
#   see dhcpd.conf(5) man page
#
EOF

# Install default (empty) dhcpd6.conf:
cat << EOF > %{buildroot}%{dhcpconfdir}/dhcpd6.conf
#
# DHCPv6 Server Configuration file.
#   see /usr/share/doc/dhcp-server/dhcpd6.conf.example
#   see dhcpd.conf(5) man page
#
EOF

# Install dhcp.schema for LDAP configuration
install -D -p -m 0644 contrib/ldap/dhcp.schema %{buildroot}%{_sysconfdir}/openldap/schema/dhcp.schema

# Don't package libtool *.la files
find %{buildroot} -type f -name "*.la" -delete -print

%pre server
%sysusers_create_compat %{SOURCE9}

%post server
# Initial installation
%systemd_post dhcpd.service dhcpd6.service


for servicename in dhcpd dhcpd6; do
  etcservicefile=%{_sysconfdir}/systemd/system/${servicename}.service
  if [ -f ${etcservicefile} ]; then
    grep -q Type= ${etcservicefile} || sed -i '/\[Service\]/a Type=notify' ${etcservicefile}
    sed -i 's/After=network.target/Wants=network-online.target\nAfter=network-online.target/' ${etcservicefile}
  fi
done
exit 0

%post relay
# Initial installation
%systemd_post dhcrelay.service

for servicename in dhcrelay; do
  etcservicefile=%{_sysconfdir}/systemd/system/${servicename}.service
  if [ -f ${etcservicefile} ]; then
    grep -q Type= ${etcservicefile} || sed -i '/\[Service\]/a Type=notify' ${etcservicefile}
    sed -i 's/After=network.target/Wants=network-online.target\nAfter=network-online.target/' ${etcservicefile}
  fi
done
exit 0

%preun server
# Package removal, not upgrade
%systemd_preun dhcpd.service dhcpd6.service

%preun relay
# Package removal, not upgrade
%systemd_preun dhcrelay.service


%postun server
# Package upgrade, not uninstall
%systemd_postun_with_restart dhcpd.service dhcpd6.service

%postun relay
# Package upgrade, not uninstall
%systemd_postun_with_restart dhcrelay.service


%triggerun -- dhcp
# convert DHC*ARGS from /etc/sysconfig/dhc* to /etc/systemd/system/dhc*.service
for servicename in dhcpd dhcpd6 dhcrelay; do
  if [ -f %{_sysconfdir}/sysconfig/${servicename} ]; then
    # get DHCPDARGS/DHCRELAYARGS value from /etc/sysconfig/${servicename}
    source %{_sysconfdir}/sysconfig/${servicename}
    if [ "${servicename}" == "dhcrelay" ]; then
        args=$DHCRELAYARGS
    else
        args=$DHCPDARGS
    fi
    # value is non-empty (i.e. user modified) and there isn't a service unit yet
    if [ -n "${args}" -a ! -f %{_sysconfdir}/systemd/system/${servicename}.service ]; then
      # in $args replace / with \/ otherwise the next sed won't take it
      args=$(echo $args | sed 's/\//\\\//'g)
      # add $args to the end of ExecStart line
      sed -r -e "/ExecStart=/ s/$/ ${args}/" \
                < %{_unitdir}/${servicename}.service \
                > %{_sysconfdir}/systemd/system/${servicename}.service
    fi
  fi
done

%files server
%doc server/dhcpd.conf.example server/dhcpd6.conf.example
%doc contrib/ldap/ contrib/dhcp-lease-list.pl
%attr(0750,root,root) %dir %{dhcpconfdir}
%attr(0755,dhcpd,dhcpd) %dir %{_localstatedir}/lib/dhcpd
%attr(0644,dhcpd,dhcpd) %verify(mode) %config(noreplace) %{_localstatedir}/lib/dhcpd/dhcpd.leases
%attr(0644,dhcpd,dhcpd) %verify(mode) %config(noreplace) %{_localstatedir}/lib/dhcpd/dhcpd6.leases
%config(noreplace) %{_sysconfdir}/sysconfig/dhcpd
%config(noreplace) %{dhcpconfdir}/dhcpd.conf
%config(noreplace) %{dhcpconfdir}/dhcpd6.conf
%dir %{_sysconfdir}/openldap/schema
%config(noreplace) %{_sysconfdir}/openldap/schema/dhcp.schema
%attr(0644,root,root)   %{_unitdir}/dhcpd.service
%attr(0644,root,root)   %{_unitdir}/dhcpd6.service
%{_sysusersdir}/dhcp.conf
%{_sbindir}/dhcpd
%{_bindir}/omshell
%attr(0644,root,root) %{_mandir}/man1/omshell.1.gz
%attr(0644,root,root) %{_mandir}/man5/dhcpd.conf.5.gz
%attr(0644,root,root) %{_mandir}/man5/dhcpd.leases.5.gz
%attr(0644,root,root) %{_mandir}/man8/dhcpd.8.gz
%if %{sdt}
%{tapsetdir}/*.stp
%endif

%files relay
%{_sbindir}/dhcrelay
%attr(0644,root,root) %{_unitdir}/dhcrelay.service
%attr(0644,root,root) %{_mandir}/man8/dhcrelay.8.gz

%files client
%doc README.dhclient.d
%doc client/dhclient.conf.example client/dhclient6.conf.example client/dhclient-enter-hooks
%attr(0750,root,root) %dir %{dhcpconfdir}
%dir %{dhcpconfdir}/dhclient.d
%dir %{_localstatedir}/lib/dhclient
%dir %{_prefix}/lib/NetworkManager
%dir %{_prefix}/lib/NetworkManager/dispatcher.d
%{_prefix}/lib/NetworkManager/dispatcher.d/11-dhclient
%{_sbindir}/dhclient
%{_sbindir}/dhclient-script
%attr(0755,root,root) %{_libdir}/pm-utils/sleep.d/56dhclient
%attr(0644,root,root) %{_mandir}/man5/dhclient.conf.5.gz
%attr(0644,root,root) %{_mandir}/man5/dhclient.leases.5.gz
%attr(0644,root,root) %{_mandir}/man8/dhclient.8.gz
%attr(0644,root,root) %{_mandir}/man8/dhclient-script.8.gz

%files common
%{!?_licensedir:%global license %%doc}
%{license} LICENSE
%doc README RELNOTES doc/References.txt
%attr(0644,root,root) %{_mandir}/man5/dhcp-options.5.gz
%attr(0644,root,root) %{_mandir}/man5/dhcp-eval.5.gz

%files libs-static
%{_libdir}/libdhcp*.a
%{_libdir}/libomapi.a

%files devel
%doc doc/IANA-arp-parameters doc/api+protocol
%{_includedir}/dhcpctl
%{_includedir}/omapip
%attr(0644,root,root) %{_mandir}/man3/dhcpctl.3.gz
%attr(0644,root,root) %{_mandir}/man3/omapi.3.gz

%if ! 0%{?_module_build}
%files devel-doc
%doc doc/html/
%endif

%changelog
* Tue May 09 2023 CentOS Sources <bugs@centos.org> - 4.4.2-18.b1.el9.centos
- Apply debranding changes

* Mon Oct 10 2022 Martin Osvald <mosvald@redhat.com> - 12:4.4.2-18.b1
- Fix for CVE-2022-2928
- Fix for CVE-2022-2929
- Use systemd-sysusers for dhcp user and group (#2095396)

* Tue May 10 2022 Martin Osvald <mosvald@redhat.com> - 12:4.4.2-17.b1
- omshell: add support for hmac-sha512 algorithm (#2083553)

* Thu Apr 14 2022 Martin Osvald <mosvald@redhat.com> - 12:4.4.2-16.b1
- Fix for CVE-2021-25220

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 12:4.4.2-15.b1
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Jul  8 2021 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.2-14.b1
- Fix for CVE-2021-25217

* Mon Jun 14 2021 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.2-13.b1
- Do not export getaddrinfo from irs libs (#1969858)

* Fri Jun 11 2021 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.2-11.b1
- Drop compat package finally

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 12:4.4.2-10.b1
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.4.2-9.b1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jul 29 2020 Pavel Zhukov <pavel@pzhukov-pc.home.redhat.com> - 12:4.4.2-8.b1
- Fix IB patch (#1860689)

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.4.2-7.b1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Apr 22 2020 Pavel Zhukov <pavel@desktop.zhukoff.net> - 12:4.4.2-6.b1
- Change upstream URL

* Fri Feb 21 2020 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.2-5.b1
- Workarounnd for gcc10

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.4.2-4.b1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan  6 2020 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.2-3.b1
- Drop NetworkManager 12-dhcpd script. It's deprecated by wait-online (#1780861) 

* Mon Jan  6 2020 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.2-1.b1
- Dropped all (pre 4.0.0) changelog
- New version (4.4.2b1)

* Wed Nov 27 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-20
- Fix leak of file descriptors

* Mon Nov 11 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-19
- Reword -B option description

* Thu Nov  7 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-18
- Readd sd-notify patch

* Thu Aug 22 2019 Lubomir Rintel <lkundrak@v3.sk> - 12:4.4.1-17
- Move the NetworkManager dispatcher script out of /etc

* Thu Jul 25 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-16
- Split timers patch to bind and dhcp parts

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.4.1-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jul 11 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-14
- Detect time change and request lease renewal

* Mon May 20 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-13
- Unpack bind prior to patching
- Provide noarch libs

* Sat May 04 2019 Björn Esser <besser82@fedoraproject.org> - 12:4.4.1-12
- rebuilt (bind)

* Tue Apr  2 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-11
- Specify epoch for obsolete

* Tue Apr  2 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-10
- Cherry-pick 00b7f9a Specify architecture for provides -

* Tue Apr  2 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-9
- Move obsolete to common section

* Wed Mar 27 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-8
- Add sd_notify patch to support systemd notify (1687040)

* Mon Mar 18 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-7
- Provides specific version of libs

* Mon Mar 18 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-6
- Obsolete dhcp-libs

* Wed Mar 13 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-5
- Do not require static libs for non devel installations

* Thu Feb 28 2019 Pavel Zhukov <pzhukov@redhat.com> - 12:4.4.1-3
- New version 4.4.1

* Mon Sep 24 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-29
- Resolves: 1632246 - Do not fail if iface has no hwaddr

* Thu Aug 30 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-28
- Do not try to map leases file in memory if not in replay mode

* Fri Jul 13 2018 Petr Menšík <pemensik@redhat.com> - 12:4.3.6-27
- Update to bind 9.11.4

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.3.6-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jun 18 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-25
- Resolves: 1592239 - Handle dhcp4-change event properly

* Mon May 21 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-24
- Fix few more shellcheck warnings

* Fri May 18 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-23
- Get rid of eval in 11-dhclient
- Credits to legolegs user of linux.org.ru

* Tue May 15 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-21
- Fix for CVE-2018-1111

* Fri Apr  6 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-20
- Discover hwaddr for all interfaces for xid uniqueness

* Wed Mar 21 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-19
- Don't use run-parts for hooks discovery (#1558612)

* Fri Mar 09 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-18
- Own ldap schema directory (#1553432)

* Thu Mar  1 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-17
- Fix CVE-2018-5732 CVE-2018-5733 (#1550246)

* Thu Feb 22 2018 Petr Menšík <pemensik@redhat.com> - 12:4.3.6-16
- Compile with recent bind includes, that does not include isc/util.h

* Thu Feb 22 2018 Petr Menšík <pemensik@redhat.com> - 12:4.3.6-15
- Do not rely on ignoring case sensitivity of VERSION variable

* Thu Feb 22 2018 Petr Menšík <pemensik@redhat.com> - 12:4.3.6-14
- Use bind-export-libs package instead of bind99
- Use isc-config.sh to configure bind libs
- Change requirement to bind-export-devel

* Thu Feb 22 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-13
- Do not parse sysconfig/network-scripts if initscripts not installed (#1098172)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.3.6-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 12:4.3.6-11
- Switch to %%ldconfig_scriptlets

* Wed Jan 10 2018 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-10
- Use released version

* Wed Dec 20 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.5-9
- Change duid_uuid patch to not use std99 feature

* Fri Dec  8 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-8
- Fix omapi SD leak (#1523547)

* Thu Nov  9 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-7
- Add patch for proper signal handling with shared context (#1457871)

* Wed Sep 20 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-6
- Do now override hostname variable in script

* Sun Sep 10 2017 Peter Robinson <pbrobinson@fedoraproject.org> 12:4.3.6-5
- Rebuild for bind 9.9.11

* Tue Aug  1 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-4
- Fix typos in dhclient-script

* Thu Jul 27 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-3
- Recreate /etc/resolv.conf if NetworkManager screwed it up (#1475279)

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.3.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild


* Fri Jul 14 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.6-1
- New version 4.3.6

* Fri Jul 07 2017 Igor Gnatenko <ignatenko@redhat.com> - 12:4.3.5-10
- Rebuild due to bug in RPM (RHBZ #1468476)

* Mon Jul 03 2017 Petr Menšík <pemensik@redhat.com> - 12:4.3.5-9
- Rebuild for bind 9.9.10

* Wed May 31 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.5-8
- Drop chown from the post section

* Tue May 23 2017 Pavel Zhukov <pzhukov@redhat.com> - 12:4.3.5-7
- Don't open ddns port until it's needed. Credits to Petr Menšík for the original idea

* Wed Apr 19 2017 Dominika Hodovska <dhodovsk@redhat.com> - 12:4.3.5-5
- don't build doxygen documentation during modular build

* Tue Apr 04 2017 Pavel Zhukov <landgraf@fedoraproject.org> - 12:4.3.5-4
- Add EnvironmentFile parameter for backward compatibility

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.3.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Nov 30 2016 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.5-2
- get BUG_REPORT_URL from /etc/os-release (#1399351)

* Wed Oct 05 2016 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.5-1
- 4.3.5

* Mon Sep 12 2016 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.5-0.1b1
- 4.3.5b1

* Wed Aug 03 2016 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.4-3
- [dhclient] rename -R option to --request-options (#1357947)
- [dhclient] rename -timeout option to --timeout

* Thu May 26 2016 Tomas Hozza <thozza@redhat.com> - 12:4.3.4-2
- Rebuild against bind99-9.9.9-P1

* Fri Apr 29 2016 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.4-1
- 4.3.4
- disable systemtap (I don't think anybody ever used it)

* Wed Mar 23 2016 Zdenek Dohnal zdohnal@redhat.com - 12:4.3.3-13.P1
- Mentioning the bash script is needed in README.dhclient.d

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 12:4.3.3-12.P1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 13 2016 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-11.P1
- 4.3.3-P1 - fix for CVE-2015-8605 (#1298077)

* Wed Dec 16 2015 Tomas Hozza <thozza@redhat.com> - 12:4.3.3-10
- Rebuild against bind-9.9.8-P2

* Mon Dec 14 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-9
- implement DUID-UUID (RFC 6355) and make it default DUID type (#560361#60)

* Tue Nov 24 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-8
- dispatcher.d/12-dhcpd: use reset-failed command

* Mon Nov 23 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-7
- dhclient-script: hostname -> hostnamectl --transient

* Tue Nov 03 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-6
- dhclient-script: source ifcfg-* because of PEERDNS (#1277253)

* Tue Oct 13 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-5
- dhclient-script: fix for gateway not in the end of rfc3442 routes list (#1251644)

* Tue Oct 13 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-4
- dhclient-script: make_resolv_conf(): keep old nameservers
  if server sends domain-name/search, but no nameservers (#1269595)

* Tue Sep 22 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-3
- dhclient: make sure link-local address is ready in stateless mode (#1263466)

* Mon Sep 07 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-2
- VLAN ID is only bottom 12-bits of TCI (#1259552)

* Fri Sep 04 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-1
- 4.3.3

* Tue Aug 11 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-0.2b1
- dhclient-script: respect DEFROUTE/GATEWAYDEV if Classless Static Routes are offered (#1251644)

* Mon Aug 10 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.3-0.1b1
- 4.3.3b1
- enable krb5/gssapi authentication for OpenLDAP
- enable support for binary insertion of leases

* Wed Jul 15 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-12
- fix ipcalc requires

* Tue Jul 14 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-11
- remove dependency on initscripts (#1098172)
- make path to resolv.conf configurable (#1086425)

* Thu Jul 09 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-10
- spec cleanup

* Thu Jul 02 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-9
- test upstream fix for #866714 (paranoia.patch)

* Wed Jun 24 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-8
- add more randomness into xid generation (#1195693)

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.3.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 26 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-6
- dhclient-script: run also scripts in dhclient-[enter/exit]-hooks.d dir

* Tue Apr 21 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-5
- dhclient-script: add a minute to address lifetimes (#1188423)

* Mon Apr 13 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-4
- dhclient-script: amend previous change (#1210984)

* Wed Mar 25 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-3
- dhclient-script: fix shellcheck.net suggestions

* Fri Mar 13 2015 Tomas Hozza <thozza@redhat.com> - 12:4.3.2-2
- rebuild against bind99 9.9.7 package

* Thu Mar 05 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-1
- 4.3.2

* Wed Feb 25 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-0.6b1
- correctly set IB's hw->hlen (#1185075)

* Wed Feb 25 2015 Tomas Hozza <thozza@redhat.com> - 12:4.3.2-0.5b1
- Rebuild against bind-9.10.2rc2

* Tue Feb 17 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-0.4b1
- dhclient-script: use 'ip addr replace' for both BOUND & RENEW

* Tue Feb 17 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-0.3b1
- doc/dhclient/dhclient-enter-hooks for dhclient-script debugging

* Fri Feb 13 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-0.2b1
- dhclient-script: s/addr add/addr replace/

* Sun Feb 08 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.2-0.1b1
- 4.3.2b1

* Tue Feb 03 2015 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-21
- send unicast request/release via correct interface (#800561, #1177351)

* Mon Feb 02 2015 Tomas Hozza <thozza@redhat.com> - 12:4.3.1-20
- rebuild against bind-9.10.2rc1

* Wed Jan 14 2015 Tomas Hozza <thozza@redhat.com> - 12:4.3.1-19
- rebuild against bind 9.10.1-P1

* Thu Dec 18 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-18
- dhclient: write DUID_LLT even in stateless mode (#1156356)

* Wed Dec 17 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-17
- option 97 - pxe-client-id (#1058674)

* Wed Nov 19 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-16
- amend post scriptlets for #1120656

* Mon Nov 10 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-15
- dhclient-script: restorecon calls shouldn't be needed
                   as we have SELinux transition rules (#1161500)

* Tue Nov 04 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-14
- GSSAPI support for ldap authentication (#1150542)

* Fri Oct 31 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-13
- redefine DHCLIENT_DEFAULT_PREFIX_LEN  64 -> 128

* Fri Oct 10 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-12
- Relay-forward Message's Hop Limit should be 32 (#1147240)

* Wed Oct 08 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-11
- dhcpd generates spurious responses when seeing requests
  from vlans on plain interface (#1150587)

* Fri Oct 03 2014 Tomas Hozza <thozza@redhat.com> - 12:4.3.1-10
- rebuild against bind-9.9.6

* Thu Sep 04 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-9
- [dhclient -6] infinite preferred/valid lifetime represented as -1 (#1133839)

* Mon Sep 01 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-8
- better obsoletes for server & client

* Sat Aug 30 2014 Kalev Lember <kalevlember@gmail.com> - 12:4.3.1-7
- Fix dhclient obsoletes version

* Tue Aug 26 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-6
- dhclient-script: another improvement of add_ipv6_addr_with_DAD()

* Mon Aug 25 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-5
- spec: use -D with 'install'
- dhclient-script: IPv6 address which fails DAD is auto-removed when it was
  added with valid_lft/preferred_lft other then 'forever' (#1133465)

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Aug 14 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-3
- dhclient-script: one more fix for #1129500

* Thu Aug 14 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-2
- dhclient-script: PREINIT6: make sure link-local address is available (#1129500)

* Tue Aug 12 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-1
- 4.3.1

* Tue Aug 05 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-0.4.b1
- dhclient-script: it's OK if the arping reply comes from our system (#1116004)

* Tue Jul 22 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-0.3.b1
- Use network-online.target instead of network.target (#1120656)

* Fri Jul 11 2014 Tom Callaway <spot@fedoraproject.org> 12:4.3.1-0.2.b1
- fix license handling

* Thu Jul 10 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.1-0.1.b1
- 4.3.1b1

* Thu Jun 12 2014 Filipe Brandenburger <filbranden@google.com> - 12:4.3.0-15
- dhclient-script: fix issue with classless static routes that breaks Fedora 20 on GCE cloud (#1102830)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.3.0-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 30 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-13
- systemtap: fixed dtrace input file (#1102797)

* Thu May 29 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-12
- dhcp-sd_notify.patch BuildRequires: pkgconfig(libsystemd)

* Wed May 28 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-11
- dhclient-script: fix stateless DHCPv6 mode (#1101149)

* Wed May 07 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-10
- use StandardError=null instead of log_perror.patch

* Tue Mar 18 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-9
- support for sending startup notifications to systemd (#1077666)

* Fri Mar 07 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-8
- rename doc subpackage do devel-doc

* Mon Mar 03 2014 Jaromír Končický <jkoncick@redhat.com> - 12:4.3.0-7
- added 'doc' package containing doxygen-generated documentation

* Wed Feb 19 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-6
- dhclient: rename our -I option to -C as upstream now uses -I

* Wed Feb 19 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-5
- dhclient-script: don't flush all addresses, just the used one

* Tue Feb 18 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-4
- IPoIB: add GUID/DUID to dhcpd logs (#1064416)

* Mon Feb 17 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-3
- don't try to run tests because there's no atf package since F21

* Mon Feb 17 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-2
- turn on using of DUID with DHCPv4 clients (#560361,c#40)
- remove default /etc/dhcp/dhclient.conf

* Tue Feb 04 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-1
- 4.3.0

* Wed Jan 29 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-0.7.rc1
- 4.3.0rc1

* Tue Jan 28 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-0.6.b1
- don't apply retransmission.patch for now (RHBZ#1026565)

* Sun Jan 26 2014 Kevin Fenzi <kevin@scrye.com> 12:4.3.0-0.5.b1
- Rebuild for new bind

* Tue Jan 21 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-0.4.b1
- 4.3.0b1
- ship dhcp-lease-list.pl
- dhclient-script: don't ping router (#1055181)

* Mon Jan 13 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-0.3.a1
- update address lifetimes on RENEW/RENEW6 (#1032809)

* Tue Jan 07 2014 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-0.2.a1
- make it actually build

* Thu Dec 19 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.3.0-0.1.a1
- 4.3.0a1: requires bind-9.9.5

* Thu Nov 21 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-28
- dhclient-script: set address lifetimes (#1032809)

* Thu Nov 14 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-27
- dhclient-script(RENEW6|REBIND6): delete old ip6_address if it changed (#1015729)

* Thu Oct 31 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-26
- Provide default /etc/dhcp/dhclient.conf
- Client always sends dhcp-client-identifier (#560361)

* Thu Oct 24 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-25
- use upstream patch for #1001742 ([ISC-Bugs #34784])

* Mon Oct 07 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-24
- dhcpd rejects the udp packet with checksum=0xffff (#1015997)

* Fri Sep 27 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-23
- 'No subnet declaration for <iface>' should be info, not error
- decrease the sleep in 12-dhcpd due to timeout (#1003695#8)

* Wed Sep 18 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-22
- fix segfault introduced with previous commit

* Tue Sep 17 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-21
- 12-dhcpd: wait a few seconds before restarting services (#1003695)
- another solution for #1001742 (#1005814#c10)

* Thu Sep 12 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-20
- bind DHCPv6 client to link-local address instead of 0 address (#1001742)

* Mon Aug 26 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-19
- don't crash on aliased infiniband interface (#996518)

* Sun Aug 04 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-18
- BuildRequires: systemd due to  %%{_unitdir}

* Mon Jul 29 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-17
- 12-dhcpd previously exited with error status 1 (#989207)

* Mon Jul 15 2013 Tomas Hozza <thozza@redhat.com> - 12:4.2.5-16
- rebuild against new bind

* Tue Jul 02 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-15
- fix several memory leaks in omapi (#978420)
- remove send_release.patch (#979510)

* Tue Jun 18 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-14
- rebuilt against bind once more

* Fri Jun 14 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-13
- return /etc/sysconfig/dhcpd back, but do NOT use it (#909733)

* Tue May 14 2013 Adam Williamson <awilliam@redhat.com> - 12:4.2.5-12
- rebuild against new bind

* Tue Apr 30 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-11
- add missing conversion specifier in log_fatal() call (#957371)

* Tue Apr 16 2013 Adam Tkac <atkac redhat com> - 12:4.2.5-10
- rebuild against new bind

* Wed Apr 03 2013 Tomas Hozza <thozza@redhat.com> - 12:4.2.5-9
- Expose next-server DHCPv4 option to dhclient script

* Tue Mar 26 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-8
- describe -user/-group/-chroot in dhcpd.8

* Fri Feb 22 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-7
- remove triggerun condition (#895475)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.2.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jan 24 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-5
- remove missing-ipv6-not-fatal.patch because the concerning code is later
  removed with getifaddrs.patch

* Wed Jan 23 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-4
- Make sure range6 is correct for subnet6 where it's declared (#902966)

* Fri Jan 18 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-3
- simplify the previously added triggerun scriptlet

* Thu Jan 17 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-2
- during update convert DHC*ARGS from /etc/sysconfig/dhc*
  to /etc/systemd/system/dhc*.service (#895475)
- 12-dhcpd NM dispatcher script now restarts also dhcpd6 service

* Thu Jan 10 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-1
- 4.2.5

* Wed Jan 02 2013 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-0.3.rc1
- run %%check in Fedora only, there's no atf package in RHEL

* Thu Dec 20 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-0.2.rc1
- don't package ancient contrib/* files

* Thu Dec 20 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.5-0.1.rc1
- 4.2.5rc1
  - added %%check - upstream unit tests (Automated Test Framework - ATF)

* Fri Nov 30 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-23.P2
- fix two resource leaks in lpf-ib.patch

* Mon Nov 26 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-22.P2
- add After=time-sync.target to dhcpd[6].service (#878293)
- remove groff from BuildRequires (no idea why it's been there)

* Fri Nov 16 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-21.P2
- multiple key statements in zone definition causes inappropriate error (#873794)

* Fri Oct 26 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-20.P2
- fix path to dhcpd6.leases in dhcpd6.conf.sample (#870458)

* Wed Oct 17 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-19.P2
- dhcpd needs to chown leases file created before de-rooting itself (#866714)

* Thu Oct 11 2012 Adam Tkac <atkac redhat com> - 12:4.2.4-18.P2
- rebuild against new bind-libs-lite

* Tue Oct 09 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-17.P2
- do-forward-updates statement wasn't recognized (#863646)

* Wed Sep 26 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-16.P2
- dhclient-usage.patch+part of manpages.patch merged with dhclient-options.patch

* Thu Sep 13 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-15.P2
- 4.2.4-P2: fix for CVE-2012-3955 (#856770)

* Fri Aug 24 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-14.P1
- SystemD unit files don't use Environment files any more (#850558)
- NetworkManager dispatcher script doesn't use DHCPDARGS any more

* Wed Aug 22 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-13.P1
- fixed SPEC file so it comply with new systemd-rpm macros guidelines (#850089)

* Mon Aug 20 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-12.P1
- dhclient-script: fixed CONFIG variable value passed to need_config (#848858)
- dhclient-script: calling dhclient-up-hooks after setting up route, gateways
                   & interface alias (#848869)

* Fri Aug 17 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-11.P1
- don't build libdst, it hasn't been used since 4.2.0 (#849166)

* Fri Jul 27 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-10.P1
- isc_time_nowplusinterval() is not safe with 64-bit time_t (#662254, #789601)

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.2.4-9.P1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 25 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-8.P1
- Dhclient does not correctly parse zero-length options in
  dhclient6.leases (#633318)

* Wed Jul 25 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-7.P1
- 4.2.4-P1: fix for CVE-2012-3570 CVE-2012-3571 and CVE-2012-3954 (#842892)

* Mon Jul 23 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-6
- ib.patch: added fall-back method (using ioctl(SIOCGIFHWADDR)) when getting
            of HW address with getifaddrs() fails (#626514-c#63, #840601).

* Mon Jul 23 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-5
- Dhcpd does not correctly follow DhcpFailOverPeerDN (#838400)

* Wed Jul 18 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-4
- allow dhcpd to listen on alias interfaces (#840601)

* Mon Jul 09 2012 Tomas Hozza <thozza@redhat.com> - 12:4.2.4-3
- changed list of %%verify on the leases files (#837474)

* Mon Jun 18 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-2
- define $SAVEDIR in dhclient-script (#833054)

* Wed Jun 06 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-1
- 4.2.4

* Tue Jun 05 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.8.rc2
- return prematurely removed 12-dhcpd (NM dispatcher script) (#828522)

* Fri May 25 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.7.rc2
- getifaddrs.patch: use HAVE_SA_LEN macro

* Wed May 23 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.6.rc2
- 4.2.4rc2

* Mon May 07 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.5.rc1
- dhcpd.service: explicitly add -cf to indicate what conf file we use (#819325)
- no need to copy /etc/*.conf to /etc/dhcp/*.conf in %%prep anymore

* Tue May 01 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.4.rc1
- 4.2.4rc1

* Thu Apr 26 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.3.b1
- remove inherit-leases.patch - it's probably not needed anymore (#815355)

* Wed Apr 18 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.2.b1
- update paths.patch and source URL

* Mon Apr 16 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.4-0.1.b1
- 4.2.4b1: noprefixavail.patch merged upstream

* Fri Mar 30 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-25.P2
- move dhclient & dhclient-script from /sbin to /usr/sbin

* Fri Mar 23 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-24.P2
- one more fix (#806342)

* Fri Mar 23 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-23.P2
- improve #449946 fix (#806342)

* Wed Mar 21 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-22.P2
- RFC5970 - DHCPv6 Options for Network Boot (#798735)

* Wed Mar 21 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-21.P2
- don't use fallback_interface when releasing lease (#800561)

* Wed Mar 21 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-20.P2
- use getifaddrs() to scan for interfaces on Linux (#449946)

* Wed Feb 22 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-19.P2
- don't send log messages to the standard error descriptor by default (#790387)

* Mon Feb 13 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-18.P2
- -timeout option (command line) with value 3 or less was driving dhclient mad (#789719)

* Tue Feb 07 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-17.P2
- dhclient-script: install link-local static routes with correct scope (#787318)

* Wed Feb  1 2012 Adam Williamson <awilliam@redhat.com> - 12:4.2.3-16.P2
- rebuild for new bind-libs-lite

* Tue Jan 31 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-15.P2
- revert previous change (#782499)
- remove the rest of the sysvinit scriptlets

* Tue Jan 17 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-14.P2
- use PrivateTmp=true in service files (#782499)

* Fri Jan 13 2012 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-13.P2
- 4.2.3-P2: fix for CVE-2011-4868 (#781246)
- clean up old Provides and Obsoletes

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.2.3-12.P1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 21 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-11.P1
- revert change made in 4.2.3-3 because of failing failover inicialization (#765967)
  the procedure is now:
  init lease file, init failover, init PID file, change effective user/group ID
- don't need to fix lease files ownership before starting service
- dhclient-script: allow static route with a 0.0.0.0 next-hop address (#769463)

* Tue Dec 20 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-10.P1
- hopefully we don't need 12-dhcpd anymore as 'After=network.target'
  in dhcpd[6].service should take care of the original problem (#565921)

* Mon Dec 19 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-9.P1
- don't ship legacy SysV initscripts
- dhcpd6: move '-cf /etc/dhcp/dhcpd6.conf' from sysconfig/dhcpd6 to dhcpd6.service
- run 'chown -R dhcpd:dhcpd /var/lib/dhcpd/' before starting dhcpd/dhcpd6 service
  for the case where leases file is owned by root:root as a
  consequence of running dhcpd without '-user dhcpd -group dhcpd' (#744292)

* Fri Dec 09 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-8.P1
- 4.2.3-P1: fix for CVE-2011-4539 (#765681)

* Thu Nov 24 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-7
- Send DHCPDECLINE and exit(2) when duplicate address was detected and
  dhclient had been started with '-1' (#756759).
- Don't build with -D_GNU_SOURCE, configure.ac uses AC_USE_SYSTEM_EXTENSIONS

* Mon Nov 14 2011 Adam Tkac <atkac redhat com> - 12:4.2.3-6
- rebuild against new bind

* Fri Nov 11 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-5
- dhclient-script: arping address in BOUND|RENEW|REBIND|REBOOT (#752116)

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.2.3-4
- Rebuilt for glibc bug#747377

* Wed Oct 26 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-3
- Write lease file AFTER changing of the effective user/group ID.
- Move omshell from dhcp-common to main package (where it originally was).

* Thu Oct 20 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-2
- Write PID file BEFORE changing of the effective user/group ID.
- Really define _hardened_build this time

* Thu Oct 20 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-1
- 4.2.3

* Tue Oct 18 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.3-0.1.rc1
- 4.2.3rc1

* Sun Oct 09 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-12
- change ownership of /var/lib/dhcpd/ to dhcpd:dhcpd (#744292)
- no need to drop capabilies in dhcpd since it's been running as regular user

* Fri Sep 30 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-11
- 56dhclient: ifcfg file was not sourced (#742482)

* Thu Sep 29 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-10
- dhclient-script: address alias handling fixes from Scott Shambarger (#741786)

* Thu Sep 22 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-9
- dhclient-script: do not backup&restore /etc/resolv.conf and /etc/localtime.

* Wed Sep 21 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-8
- SystemTap support: spec file change, some dummy probes, tapset, simple script

* Mon Sep 19 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-7
- Support for IPoIB (IP over InfiniBand) interfaces (#660681)
- Hopefully last tweak of adding of user and group (#699713)

* Fri Sep 09 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-6
- PIE-RELRO.patch is not needed anymore, defining _hardened_build does the same
- One more tweak of adding of user and group (#699713)

* Fri Sep 09 2011 Adam Tkac <atkac redhat com> - 12:4.2.2-5
- rebuild against new bind

* Fri Aug 26 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-4
- Fix adding of user and group (#699713)

* Fri Aug 19 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-3
- Tighten explicit libs sub-package requirement so that it includes
  the correct architecture as well.

* Fri Aug 12 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-2
- #699713:
  - Use '--enable-paranoia --enable-early-chroot' configure flags
  - Create/delete dhcpd user in %%post/%%postun
  - Run dhcpd/dhcpd6 services with '-user dhcpd -group dhcpd'

* Thu Aug 11 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-1
- 4.2.2: fix for CVE-2011-2748, CVE-2011-2749 (#729850)

* Wed Aug 10 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-0.4.rc1
- Do not ship default /etc/dhcp/dhclient.conf (#560361,c#9)

* Mon Jul 25 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-0.3.rc1
- Improve capabilities patch to be able to run with PARANOIA & EARLY_CHROOT (#699713)

* Mon Jul 18 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-0.2.rc1
- 4.2.2rc1

* Fri Jul 01 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.2-0.1.b1
- 4.2.2b1: upstream merged initialization-delay.patch
- Drop all capabilities in dhcpd/dhcrelay (#699713)

* Fri Jun 17 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-12.P1
- Removed upstream-merged IFNAMSIZ.patch
- Polished patches according to results from static analysis of code.

* Thu Jun 16 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-11.P1
- Add triggerpostun scriptlet tied to dhcp-sysvinit
- Make it possible to build without downstream patches (Kamil Dudka)

* Tue May 17 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-10.P1
- Fix typo in triggerun scriptlet (#705417)

* Mon May 16 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-9.P1
- Packages dhcp/dhclient/dhcp-common explicitly require the libs sub-package
  with the same version and release (bug #705037).
- Fix triggerun scriptlet

* Mon May 09 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-8.P1
- Fix 11-dhclient to export variables (#702735)

* Fri Apr 29 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-7.P1
- Comply with guidelines for systemd services

* Wed Apr 27 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-6.P1
- Fix NetworkManager dispatcher script for dhcpd to support arbitrary interface names

* Wed Apr 06 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-5.P1
- Better fix for CVE-2011-0997: making domain-name check more lenient (#694005)

* Wed Apr 06 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-4.P1
- 4.2.1-P1: fix for CVE-2011-0997 (#694005)

* Fri Mar 25 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-3
- Polished patches according to results from static analysis of code.

* Mon Mar 07 2011 Rex Dieter <rdieter@fedoraproject.org> - 12:4.2.1-2
- rebuild (bind)

* Wed Mar 02 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-1
- 4.2.1

* Wed Feb 23 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-0.6.rc1
- 4.2.1rc1
- Fixed typo in dhclient.leases(5) (#676284)

* Mon Feb 21 2011 Adam Tkac <atkac redhat com> - 12:4.2.1-0.5.b1
- rebuild against new bind-libs-lite

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.2.1-0.4.b1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-0.3.b1
- Prevent anything under _docdir from being scanned. (#674058)

* Fri Jan 28 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-0.2.b1
- dhclient-script improvements, thanks to Ville Skyttä (#672279)

* Thu Jan 27 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.1-0.1.b1
- 4.2.1b1: fix for CVE-2011-0413 (#672996)
- No longer need invalid-dhclient-conf, parse_date and release6-elapsed patches

* Thu Jan 13 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-26.P2
- Fix loading of configuration when LDAP is used (#668276)

* Mon Jan 03 2011 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-25.P2
- Fix OMAPI (#666441)

* Tue Dec 21 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-24.P2
- Provide default /etc/dhcp/dhclient.conf
- Client always sends dhcp-client-identifier (#560361)

* Wed Dec 15 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-23.P2
- Add dhcp-common subpackage (#634673)

* Mon Dec 13 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-22.P2
- 4.2.0-P2: fix for CVE-2010-3616 (#662326)
- Use upstream fix for #628258
- Provide versioned symbols for rpmlint

* Tue Dec 07 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-21.P1
- Porting dhcpd/dhcpd6/dhcrelay services from SysV to Systemd

* Tue Nov 23 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-20.P1
- Remove explicit Obsoletes (#656310)

* Fri Nov 19 2010 Dan Horák <dan[at]danny.cz> - 12:4.2.0-19.P1
- fix build on sparc and s390

* Tue Nov 09 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-18.P1
- Applied Patrik Lahti's patch for DHCPv6 over PPP support (#626514)

* Fri Nov 05 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-17.P1
- fix broken dependencies

* Thu Nov 04 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-16.P1
- 4.2.0-P1: fix for CVE-2010-3611 (#649880)
- dhclient-script: when updating 'search' statement in resolv.conf,
  add domain part of hostname if it's not already there (#637763)

* Wed Oct 20 2010 Adam Tkac <atkac redhat com> - 12:4.2.0-15
- build dhcp's libraries as shared libs instead of static libs

* Wed Oct 20 2010 Adam Tkac <atkac redhat com> - 12:4.2.0-14
- fire away bundled BIND source

* Wed Oct 20 2010 Adam Tkac <atkac redhat com> - 12:4.2.0-13
- improve PIE patch (build libraries with -fpic, not with -fpie)

* Wed Oct 13 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-12
- Server was ignoring client's
  Solicit (where client included address/prefix as a preference) (#634842)

* Thu Oct 07 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-11
- Use ping instead of arping in dhclient-script to handle
  not-on-local-net gateway in ARP-less device (#524298)

* Thu Oct 07 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-10
- Check whether there is any unexpired address in previous lease
  prior to confirming (INIT-REBOOT) the lease (#585418)

* Mon Oct 04 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-9
- RFC 3442 - ignore Router option only if
  Classless Static Routes option contains default router

* Thu Sep 30 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-8
- Explicitly clear the ARP cache and flush all addresses & routes
  instead of bringing the interface down (#574568)

* Tue Sep 07 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-7
- Hardening dhcpd/dhcrelay/dhclient by making them PIE & RELRO

* Thu Sep 02 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-6
- Another fix for handling time values on 64-bit platforms (#628258)

* Wed Sep 01 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-5
- Fix parsing of lease file dates & times on 64-bit platforms (#628258)

* Tue Aug 31 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-4
- RFC 3442 - Classless Static Route Option for DHCPv4 (#516325)

* Fri Aug 20 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-3
- Add DHCRELAYARGS variable to /etc/sysconfig/dhcrelay

* Fri Jul 30 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-2
- Add 12-dhcpd NM dispatcher script (#565921)
- Rename 10-dhclient to 11-dhclient (10-sendmail already exists)

* Wed Jul 21 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.2.0-1
- 4.2.0: includes ldap-for-dhcp

* Mon Jul 12 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-26.P1
- Add LICENSE file to dhclient subpackage.

* Thu Jul 01 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-25.P1
- Adhere to Static Library Packaging Guidelines (#609605)

* Tue Jun 29 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-24.P1
- Fix parsing of date (#514828)

* Thu Jun 03 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-23.P1
- 4.1.1-P1: pair of bug fixes including one for CVE-2010-2156 (#601405)
- Compile with -fno-strict-aliasing

* Mon May 03 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-22
- Fix the initialization-delay.patch (#587070)

* Thu Apr 29 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-21
- Cut down the 0-4 second delay before sending first DHCPDISCOVER (#587070)

* Wed Apr 28 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-20
- Move /etc/NetworkManager/dispatcher.d/10-dhclient script
  from dhcp to dhclient subpackage (#586999)

* Wed Apr 28 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-19
- Add domain-search to the list of default requested DHCP options (#586906)

* Wed Apr 21 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-18
- If the Reply was received in response to Renew or Rebind message,
  client adds any new addresses in the IA option to the IA (#578097)

* Mon Apr 19 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-17
- Fill in Elapsed Time Option in Release/Decline messages (#582939)

* Thu Mar 25 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-16
- In client initiated message exchanges stop retransmission
  upon reaching the MRD rather than at some point after it (#559153)

* Wed Mar 24 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-15
- In dhclient-script check whether bound address
  passed duplicate address detection (DAD) (#559147)
- If the bound address failed DAD (is found to be in use on the link),
  the dhcpv6 client sends a Decline message to the server
  as described in section 18.1.7 of RFC-3315 (#559147)

* Fri Mar 19 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-14
- Fix UseMulticast.patch to not repeatedly parse dhcpd.conf for unicast option
- Fix dhclient-script to set interface MTU only when it's greater than 576 (#574629)

* Fri Mar 12 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-13
- Discard unicast Request/Renew/Release/Decline message
  (unless we set unicast option) and respond with Reply
  with UseMulticast Status Code option (#573090)
- Remove DHCPV6 OPERATION section from dhclient.conf.5
  describing deprecated 'send dhcp6.oro' syntax

* Thu Feb 25 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-12
- Fix paths in man pages (#568031)
- Remove odd tests in %%preun

* Mon Feb 22 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-11
- Add interface-mtu to the list of default requested DHCP options (#566873)

* Fri Feb 19 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-10
- Fix pm-utils/sleep.d/ directory ownership conflict

* Fri Feb 19 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-9
- In dhclient-script:
  - use ip command options '-4' or '-6' as shortcuts for '-f[amily] inet' resp. '-f[amily] inet6'
  - do not use IP protocol family identifier with 'ip link'

* Thu Feb 18 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-8
- Fix installation of pm-utils script (#479639, c#16)

* Tue Feb 16 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-7
- ldap-for-dhcp-4.1.1-2 (#564810)

* Tue Feb 16 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-6
- Fix ldap patch to explicitly link with liblber (#564810)

* Mon Feb 08 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-5
- Fix dhclient-decline-backoff.patch (#562854)

* Fri Feb 05 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-4
- Fix dhclient-script to delete address which the client is going to release
  as soon as it begins the Release message exchange process (#559142)

* Wed Feb 03 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-3
- move /etc/dhcp.conf to /etc/dhcp.conf.rpmsave in %%post (#561094)
- document -nc option in dhclient(8) man page

* Tue Feb 02 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-2
- Fix capability patch (#546765)

* Wed Jan 20 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.1-1
- Upgraded to ISC dhcp-4.1.1

* Mon Jan 18 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-18
- Hide startup info when starting dhcpd6 service.
- Remove -TERM from calling killproc when stopping dhcrelay (#555672)

* Fri Jan 15 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-17
- Added init script to also start dhcpd for IPv6 (#552453)
- Added dhcpd6.conf.sample

* Thu Jan 07 2010 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-16
- Use %%global instead of %%define.

* Mon Dec 14 2009 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-15
- dhclient logs its pid to make troubleshooting NM managed systems
  with multiple dhclients running easier (#546792)

* Mon Nov 23 2009 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-14
- Honor DEFROUTE=yes|no for all connection types (#530209)

* Fri Oct 30 2009 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-13
- Make dhclient-script add IPv6 address to interface (#531997)

* Tue Oct 13 2009 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-12
- Fix 56dhclient so network comes back after suspend/hibernate (#527641)

* Thu Sep 24 2009 Jiri Popelka <jpopelka@redhat.com> - 12:4.1.0p1-11
- Make dhcpd and dhcrelay init scripts LSB compliant (#522134, #522146)

* Mon Sep 21 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-10
- Obsolete the dhcpv6 and dhcpv6-client packages

* Fri Sep 18 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-9
- Update dhclient-script with handlers for DHCPv6 states

* Wed Aug 26 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-8
- Conditionalize restorecon calls in post scriptlets (#519479)

* Wed Aug 26 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-7
- Do not require policycoreutils for post scriptlet (#519479)

* Fri Aug 21 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-6
- BR libcap-ng-devel (#517649)

* Tue Aug 18 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-5
- Drop unnecessary capabilities in dhclient (#517649)

* Fri Aug 14 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-4
- Upgrade to latest ldap-for-dhcp patch which makes sure that only
  dhcpd links with OpenLDAP (#517474)

* Wed Aug 12 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-3
- Update NetworkManager dispatcher script to remove case conversion
  and source /etc/sysconfig/network

* Thu Aug 06 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-2
- Add /usr/lib[64]/pm-utils/sleep.d/56dhclient to handle suspend and
  resume with active dhclient leases (#479639)

* Wed Aug 05 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0p1-1
- Upgrade to dhcp-4.1.0p1, which is the official upstream release to fix
  CVE-2009-0692

* Wed Aug 05 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-27
- Fix for CVE-2009-0692
- Fix for CVE-2009-1892 (#511834)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.1.0-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 23 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-25
- Include NetworkManager dispatcher script to run dhclient.d scripts (#459276)

* Thu Jul 09 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-24
- Ensure 64-bit platforms parse lease file dates & times correctly (#448615)

* Thu Jul 09 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-23
- Upgrade to ldap-for-dhcp-4.1.0-4

* Wed Jul 01 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-22
- Set permissions on /etc/dhcp to 0750 (#508247)
- Update to new ldap-for-dhcp patch set
- Correct problems when upgrading from a previous release and your
  dhcpd.conf file not being placed in /etc/dhcp (#506600)

* Fri Jun 26 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-21
- Handle cases in add_timeout() where the function is called with a NULL
  value for the 'when' parameter (#506626)
- Fix SELinux denials in dhclient-script when the script makes backup
  configuration files and restores them later (#483747)

* Wed May 06 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-20
- Obsolete libdhcp4client <= 12:4.0.0-34.fc10 (#499290)

* Mon Apr 20 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-19
- Restrict interface names given on the dhcpd command line to length
  IFNAMSIZ or shorter (#441524)
- Change to /etc/sysconfig/network-scripts in dhclient-script before
  calling need_config or source_config (#496233)

* Mon Apr 20 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-18
- Make dhclient-script work with pre-configured wireless interfaces (#491157)

* Thu Apr 16 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-17
- Fix setting default route when client IP address changes (#486512, #473658)
- 'reload' and 'try-restart' on dhcpd and dhcrelay init scripts
  will display usage information and return code 3

* Mon Apr 13 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-16
- Correct %%post problems in dhclient package (#495361)
- Read hooks scripts from /etc/dhcp (#495361)
- Update to latest ldap-for-dhcp

* Fri Apr 03 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-15
- Obsolete libdhcp and libdhcp-devel (#493547)

* Thu Apr 02 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-14
- Obsolete libdhcp and libdhcp-devel (#493547)

* Tue Mar 31 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-13
- dhclient obsoletes libdhcp4client (#493213)
- dhcp-devel obsolets libdhcp4client-devel (#493213)

* Wed Mar 11 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-12
- Fix problems with dhclient.d script execution (#488864)

* Mon Mar 09 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-11
- Use LDAP configuration patch from upstream tarball

* Thu Mar 05 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-10
- restorecon fixes for /etc/localtime and /etc/resolv.conf (#488470)

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12:4.1.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-8
- Correct subsystem execution in dhclient-script (#486251)

* Wed Feb 18 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-7
- Do not segfault if the ipv6 kernel module is not loaded (#486097)

* Mon Feb 16 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-6
- Enable dhcpv6 support (#480798)
- Fix config file migration in scriptlets (#480543)
- Allow dhclient-script expansion with /etc/dhcp/dhclient.d/*.sh scripts

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> - 12:4.1.0-5
- rebuild with new openssl

* Tue Jan 13 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-4
- Updated LSB init script header to reference /etc/dhcp/dhcpd.conf (#479012)

* Sun Jan 11 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-3
- Correct syntax errors in %%post script (#479012)

* Sat Jan 10 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-2
- Make sure all /etc/dhcp config files are marked in the manifest
- Include new config file directies in the dhcp and dhclient packages
- Do not overwrite new config files if they already exist

* Tue Jan 06 2009 David Cantrell <dcantrell@redhat.com> - 12:4.1.0-1
- Upgraded to ISC dhcp-4.1.0
- Had to rename the -T option to -timeout as ISC is now using -T
- Allow package rebuilders to easily enable DHCPv6 support with:
      rpmbuild --with DHCPv6 dhcp.spec
  Note that Fedora is still using the 'dhcpv6' package, but some
  users may want to experiment with the ISC DHCPv6 implementation
  locally.

* Thu Dec 18 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-34
- Move /etc/dhclient.conf to /etc/dhcp/dhclient.conf
- Move /etc/dhcpd.conf to /etc/dhcp/dhcpd.conf

* Thu Dec 18 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-33
- Remove unnecessary success/failure lines in init scripts (#476846)

* Wed Dec 03 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-32
- Enable LDAP/SSL support in dhcpd (#467740)
- Do not calculate a prefix for an address we did not receive (#473885)
- Removed libdhcp4client because libdhcp has been removed from Fedora

* Wed Oct 29 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-31
- Use O_CLOEXEC in open(2) calls and "e" mode in fopen(3) calls, build
  with -D_GNU_SOURCE so we pick up O_CLOEXEC (#468984)
- Add missing prototype for validate_port() in common/inet.c

* Thu Oct 23 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-30
- Fix dhclient.conf man page and sample config file to say 'supersede
  domain-search', which is what was actually demonstrated (#467955)

* Wed Oct 01 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-29
- Make sure /etc/resolv.conf has restorecon run on it (#451560)

* Tue Sep 30 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-28
- Forgot to actually include <errno.h> (#438149)

* Tue Sep 30 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-27
- Fix patch fuzziness and include errno.h in includes/dhcpd.h (#438149)

* Tue Sep 30 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-26
- Validate port numbers for dhclient, dhcpd, and dhcrelay to ensure
  that are within the correct range (#438149)

* Mon Sep 29 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-25
- Fix dhcpd so it can find configuration data via LDAP (#452985)

* Tue Sep 16 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-24
- 'server' -> 'service' in dhclient-script (#462343)

* Fri Aug 29 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-23
- Prevent $metric from being set to '' (#460640)
- Remove unnecessary warning messages
- Do not source config file (ifcfg-DEVICE) unless it exists

* Sun Aug 24 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-22
- Add missing '[' to dhclient-script (#459860)
- Correct test statement in add_default_gateway() in dhclient-script (#459860)

* Sat Aug 23 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-21
- Fix syntax error in dhclient-script (#459860)

* Fri Aug 22 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-20
- Rewrite of /sbin/dhclient-script (make the script a little more readable,
  discontinue use of ifconfig in favor of ip, store backup copies of orig
  files in /var rather than in /etc)

* Wed Aug 06 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-19
- Remove 'c' from the domain-search format string in common/tables.c
- Prevent \032 from appearing in resolv.conf search line (#450042)
- Restore SELinux context on saved /etc files (#451560)

* Sun Aug 03 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 12:4.0.0-18
- filter out false positive perl requires

* Fri Aug 01 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-17
- Carry over RES_OPTIONS from ifcfg-ethX files to /etc/resolv.conf (#202923)
- Clean up Requires tags for devel packages
- Allow SEARCH variable in ifcfg files to override search path (#454152)
- Do not down interface if there is an active lease (#453982)
- Clean up how dhclient-script restarts ypbind
- Set close-on-exec on dhclient.leases for SELinux (#446632)

* Sat Jun 21 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-16
- Remove instaces of \032 in domain search option (#450042)
- Make 'service dhcpd configtest' display text indicating the status

* Fri May 16 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-15
- Set close-on-exec on dhclient.leases for SELinux (#446632)

* Tue Apr 01 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-14
- Avoid dhclient crash when run via NetworkManager (#439796)

* Tue Mar 25 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-13
- Update dhclient-script to handle domain-search correctly (#437840)

* Tue Mar 25 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-12
- Remove Requires on openldap-server (#432180)
- Replace CLIENTBINDIR, ETCDIR, DBDIR, and RUNDIR in the man pages with the
  correct paths

* Wed Feb 13 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-11
- Add missing newline to usage() screen in dhclient

* Thu Feb 07 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-10
- Save conf files adding '.predhclient.$interface' to the name (#306381)
- Only restore conf files on EXPIRE/FAIL/RELEASE/STOP if there are no other
  dhclient processes running (#306381)

* Wed Feb 06 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-9
- Match LDAP server option values in stables.c and dhcpd.h (#431003)
- Fix invalid sprintf() statement in server/ldap.c (#431003)

* Wed Feb 06 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-8
- Remove invalid fclose() patch

* Tue Feb 05 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-7
- Don't leak /var/lib/dhclient/dhclient.leases file descriptors (#429890)

* Tue Jan 22 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-6
- read_function() comes from the LDAP patch, so fix it there
- Init new struct universe structs in libdhcp4client so we don't crash on
  multiple DHCP attempts (#428203)

* Thu Jan 17 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-5
- Patch read_function() to handle size_t from read() correctly (#429207)

* Wed Jan 16 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-4
- Fix dhclient.lease file parsing problems (#428785)
- Disable IPv6 support for now as we already ship dhcpv6 (#428987)

* Tue Jan 15 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-3
- Fix segfault in next_iface4() and next_iface6() (#428870)

* Mon Jan 14 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-2
- -fvisibility fails me again

* Mon Jan 14 2008 David Cantrell <dcantrell@redhat.com> - 12:4.0.0-1
- Upgrade to ISC dhcp-4.0.0 (#426634)
     - first ISC release to incorporate DHCPv6 protocol support
     - source tree now uses GNU autoconf/automake
- Removed the libdhcp4client-static package

