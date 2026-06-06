# To rebuild this RPM, you must first rebuild the portable
# RPM using the java-21-openjdk-portable.specfile, install
# it and then adjust portablerelease and portablesuffix
# to match the new portable.

# RPM conditionals so as to be able to dynamically produce
# slowdebug/release builds. See:
# http://rpm.org/user_doc/conditional_builds.html
#
# Examples:
#
# Produce release, fastdebug *and* slowdebug builds on x86_64 (default):
# $ rpmbuild -ba java-25-openjdk.spec
#
# Produce only release builds (no debug builds) on x86_64:
# $ rpmbuild -ba java-25-openjdk.spec --without slowdebug --without fastdebug
#
# Only produce a release build on x86_64:
# $ fedpkg mockbuild --without slowdebug --without fastdebug

# Enable fastdebug builds by default on relevant arches.
%bcond_without fastdebug
# Enable slowdebug builds by default on relevant arches.
%bcond_without slowdebug
# Enable release builds by default on relevant arches.
%bcond_without release
# Enable static library builds by default.
%bcond_without staticlibs
# Build with system libraries
%bcond_with system_libs

# Workaround for stripping of debug symbols from static libraries
%if %{with staticlibs}
%define __brp_strip_static_archive %{nil}
%global include_staticlibs 1
%else
%global include_staticlibs 0
%endif

%if %{with system_libs}
%global system_libs 1
%global link_type system
%global freetype_lib %{nil}
%else
%global system_libs 0
%global link_type bundled
%global freetype_lib |libfreetype[.]so.*
%endif

# The -g flag says to use strip -g instead of full strip on DSOs or EXEs.
# This fixes detailed NMT and other tools which need minimal debug info.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1520879
%global _find_debuginfo_opts -g

# With LTO flags enabled, debuginfo checks fail for some reason. Disable
# LTO for a passing build. This really needs to be looked at.
%define _lto_cflags %{nil}

# note: parametrized macros are order-sensitive (unlike not-parametrized) even with normal macros
# also necessary when passing it as parameter to other macros. If not macro, then it is considered a switch
# see the difference between global and define:
# See https://github.com/rpm-software-management/rpm/issues/127 to comments at  "pmatilai commented on Aug 18, 2017"
# (initiated in https://bugzilla.redhat.com/show_bug.cgi?id=1482192)
%global debug_suffix_unquoted -slowdebug
%global fastdebug_suffix_unquoted -fastdebug
# quoted one for shell operations
%global debug_suffix "%{debug_suffix_unquoted}"
%global fastdebug_suffix "%{fastdebug_suffix_unquoted}"
%global normal_suffix ""

%global debug_warning This package is unoptimised with full debugging. Install only as needed and remove ASAP.
%global fastdebug_warning This package is optimised with full debugging. Install only as needed and remove ASAP.
%global debug_on unoptimised with full debugging on
%global fastdebug_on optimised with full debugging on
%global for_fastdebug for packages with debugging on and optimisation
%global for_debug for packages with debugging on and no optimisation

%if %{with release}
%global include_normal_build 1
%else
%global include_normal_build 0
%endif

%if %{include_normal_build}
%global normal_build %{normal_suffix}
%else
%global normal_build %{nil}
%endif

# We have hardcoded list of files, which  is appearing in alternatives, and in files
# in alternatives those are slaves and master, very often triplicated by man pages
# in files all masters and slaves are ghosted
# the ghosts are here to allow installation via query like `dnf install /usr/bin/java`
# you can list those files, with appropriate sections: cat *.spec | grep -e --install -e --slave -e post_ -e alternatives
# TODO - fix those hardcoded lists via single list
# Those files must *NOT* be ghosted for *slowdebug* packages
# FIXME - if you are moving jshell or jlink or similar, always modify all three sections
# you can check via headless and devels:
#    rpm -ql --noghost java-11-openjdk-headless-11.0.1.13-8.fc29.x86_64.rpm  | grep bin
# == rpm -ql           java-11-openjdk-headless-slowdebug-11.0.1.13-8.fc29.x86_64.rpm  | grep bin
# != rpm -ql           java-11-openjdk-headless-11.0.1.13-8.fc29.x86_64.rpm  | grep bin
# similarly for other %%{_jvmdir}/{jre,java} and %%{_javadocdir}/{java,java-zip}
%define is_release_build() %( if [ "%{?1}" == "%{debug_suffix_unquoted}" -o "%{?1}" == "%{fastdebug_suffix_unquoted}" ]; then echo "0" ; else echo "1"; fi )

# Indicates whether this is the default JDK on this version of RHEL
# Only the default/system JDK provides unversioned Provides like 'java', 'jre' and 'java-devel'
%global is_system_jdk 0

%global aarch64         aarch64 arm64 armv8
# we need to distinguish between big and little endian PPC64
%global ppc64le         ppc64le
%global ppc64be         ppc64 ppc64p7
# Set of architectures which support multiple ABIs
%global multilib_arches %{power64} sparc64 x86_64
# Set of architectures for which we build slowdebug builds
%global debug_arches    %{ix86} x86_64 sparcv9 sparc64 %{aarch64} %{power64} s390x
# Set of architectures for which we build fastdebug builds
%global fastdebug_arches x86_64 ppc64le aarch64
# Set of architectures with a Just-In-Time (JIT) compiler
%global jit_arches      %{arm} %{aarch64} %{ix86} %{power64} s390x sparcv9 sparc64 x86_64 riscv64
# Set of architectures which use the Zero assembler port (!jit_arches)
%global zero_arches ppc s390
# Set of architectures which run a full bootstrap cycle
%global bootstrap_arches %{jit_arches}
# Set of architectures which support SystemTap tapsets
%global systemtap_arches %{jit_arches}
# Set of architectures with a Ahead-Of-Time (AOT) compiler
%global aot_arches      x86_64 %{aarch64}
# Set of architectures which support the serviceability agent
%global sa_arches       %{ix86} x86_64 sparcv9 sparc64 %{aarch64} %{power64} %{arm} riscv64
# Set of architectures which support class data sharing
# As of JDK-8005165 in OpenJDK 10, class sharing is not arch-specific
# However, it does segfault on the Zero assembler port, so currently JIT only
%global share_arches    %{jit_arches}
# Set of architectures for which we build the Shenandoah garbage collector
%global shenandoah_arches x86_64 %{aarch64} riscv64
# Set of architectures for which we build the Z garbage collector
%global zgc_arches x86_64 riscv64
# Set of architectures for which alt-java has SSB mitigation
%global ssbd_arches x86_64
# Set of architectures for which java has short vector math library (libjsvml.so)
%global svml_arches x86_64
# Set of architectures for which java has intrinsics for Arrays.sort (libsimdsort.so)
%global simdsort_arches x86_64
# Set of architectures for which SLEEF is used for vector math operations
%global sleef_arches %{aarch64} riscv64
# Set of architectures where we verify backtraces with gdb
%global gdb_arches %{jit_arches} %{zero_arches}
# Architecture on which we run Java only tests
%global jdk_test_arch x86_64

# By default, we build a debug build during main build on JIT architectures
%if %{with slowdebug}
%ifarch %{debug_arches}
%global include_debug_build 1
%else
%global include_debug_build 0
%endif
%else
%global include_debug_build 0
%endif

# On certain architectures, we compile the Shenandoah GC
%ifarch %{shenandoah_arches}
%global use_shenandoah_hotspot 1
%else
%global use_shenandoah_hotspot 0
%endif

# By default, we build a fastdebug build during main build only on fastdebug architectures
%if %{with fastdebug}
%ifarch %{fastdebug_arches}
%global include_fastdebug_build 1
%else
%global include_fastdebug_build 0
%endif
%else
%global include_fastdebug_build 0
%endif

%if %{include_debug_build}
%global slowdebug_build %{debug_suffix}
%else
%global slowdebug_build %{nil}
%endif

%if %{include_fastdebug_build}
%global fastdebug_build %{fastdebug_suffix}
%else
%global fastdebug_build %{nil}
%endif

# If you disable all builds, then the build fails
# Build and test slowdebug first as it provides the best diagnostics
%global build_loop %{slowdebug_build} %{fastdebug_build} %{normal_build}

%if 0%{?flatpak}
%global bootstrap_build false
%else
%ifarch %{bootstrap_arches}
%global bootstrap_build true
%else
%global bootstrap_build false
%endif
%endif

# debugedit tool for rewriting ELF file paths
%if 0%{?rhel} >= 10
# From RHEL 10, the tool is in its own package installed in the usual location
%global debugedit %{_bindir}/debugedit
%else
# On earlier versions of RHEL, it is part of the rpm package
%global debugedit %{_rpmconfigdir}/debugedit
%endif

# In some cases, the arch used by the JDK does
# not match _arch.
# Also, in some cases, the machine name used by SystemTap
# does not match that given by _target_cpu
%ifarch x86_64
%global archinstall amd64
%global stapinstall x86_64
%endif
%ifarch ppc
%global archinstall ppc
%global stapinstall powerpc
%endif
%ifarch %{ppc64be}
%global archinstall ppc64
%global stapinstall powerpc
%endif
%ifarch %{ppc64le}
%global archinstall ppc64le
%global stapinstall powerpc
%endif
%ifarch %{ix86}
%global archinstall i686
%global stapinstall i386
%endif
%ifarch ia64
%global archinstall ia64
%global stapinstall ia64
%endif
%ifarch s390
%global archinstall s390
%global stapinstall s390
%endif
%ifarch s390x
%global archinstall s390x
%global stapinstall s390
%endif
%ifarch %{arm}
%global archinstall arm
%global stapinstall arm
%endif
%ifarch %{aarch64}
%global archinstall aarch64
%global stapinstall arm64
%endif
%ifarch riscv64
%global archinstall riscv64
%global stapinstall riscv64
%endif
# 32 bit sparc, optimized for v9
%ifarch sparcv9
%global archinstall sparc
%global stapinstall %{_target_cpu}
%endif
# 64 bit sparc
%ifarch sparc64
%global archinstall sparcv9
%global stapinstall %{_target_cpu}
%endif
# Need to support noarch for srpm build
%ifarch noarch
%global archinstall %{nil}
%global stapinstall %{nil}
%endif

%ifarch %{systemtap_arches}
%global with_systemtap 1
%else
%global with_systemtap 0
%endif

# New Version-String scheme-style defines
%global featurever 25
%global interimver 0
%global updatever 3
%global patchver 0
# We don't add any LTS designator for STS packages (Fedora and EPEL).
# We need to explicitly exclude EPEL as it would have the %%{rhel} macro defined.
%if 0%{?rhel} && !0%{?epel}
  %global lts_designator "LTS"
  %global lts_designator_zip -%{lts_designator}
%else
  %global lts_designator ""
  %global lts_designator_zip ""
%endif

# Define vendor information used by OpenJDK
%global oj_vendor Red Hat, Inc.
%global oj_vendor_url https://www.redhat.com/
# Define what url should JVM offer in case of a crash report
# order may be important, epel may have rhel declared
%if 0%{?epel}
%global oj_vendor_bug_url  https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora%20EPEL&component=%{name}&version=epel%{epel}
%else
%if 0%{?fedora}
# Does not work for rawhide, keeps the version field empty
%global oj_vendor_bug_url  https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora&component=%{name}&version=%{fedora}
%else
%if 0%{?rhel}
%global oj_vendor_bug_url https://access.redhat.com/support/cases/
%else
%global oj_vendor_bug_url  https://bugzilla.redhat.com/enter_bug.cgi
%endif
%endif
%endif
%global oj_vendor_version (Red_Hat-%{version}-%{portablerelease})

# Define IcedTea version used for SystemTap tapsets and desktop file
%global icedteaver      6.0.0pre00-c848b93a8598
# Define current Git revision for the FIPS support patches
%global fipsver 57722aab802
# Define nssadapter variables
%global nssadapter_version 0.1.1
%global nssadapter_name nssadapter-%{nssadapter_version}
# Define whether the crypto policy is expected to be active when testing
%global crypto_policy_active true
# Define JDK versions
%global newjavaver %{featurever}.%{interimver}.%{updatever}.%{patchver}
%global javaver         %{featurever}
# Strip up to 6 trailing zeros in newjavaver, as the JDK does, to get the correct version used in filenames
%global filever %(svn=%{newjavaver}; for i in 1 2 3 4 5 6 ; do svn=${svn%%.0} ; done; echo ${svn})
# The tag used to create the OpenJDK tarball
%global vcstag jdk-%{filever}+%{buildver}%{?tagsuffix:-%{tagsuffix}}

# Define the OS the portable JDK is built on
# This is undefined for CentOS & openjdk-portable-rhel-8 builds and
# equals 'rhel7' for openjdk-portable-rhel-7 builds
%if 0
%undefine pkgos
%endif

# Standard JPackage naming and versioning defines
%global origin          openjdk
%global origin_nice     OpenJDK
%global top_level_dir_name   %{vcstag}
%global top_level_dir_name_backup %{top_level_dir_name}-backup
%global buildver        9
%global rpmrelease      1
# Settings used by the portable build
%global portablerelease 1
# Portable suffix differs between RHEL and CentOS
%if 0%{?centos} == 0
%global portablerhel %{?pkgos:7_9}%{!?pkgos:8}
%else
%global portablerhel 9
%endif
%global portablebuilddir /builddir/build/BUILD
%global portablesuffix el%{rhel}
# Check if pandoc was available to generate docs (including man pages)
%if 0%{?portablerhel} == 8
%global pandoc_available 1
%else
%global pandoc_available 0
%endif

%ifarch armv6hl
%global pandoc_available 0
%endif

# Priority must be 8 digits in total; up to openjdk 1.8, we were using 18..... so when we moved to 11, we had to add another digit
%if %is_system_jdk
# Using 10 digits may overflow the int used for priority, so we combine the patch and build versions
# It is very unlikely we will ever have a patch version > 4 or a build version > 20, so we combine as (patch * 20) + build.
# This means 11.0.9.0+11 would have had a priority of 11000911 as before
# A 11.0.9.1+1 would have had a priority of 11000921 (20 * 1 + 1), thus ensuring it is bigger than 11.0.9.0+11
%global combiver $( expr 20 '*' %{patchver} + %{buildver} )
%global priority %( printf '%02d%02d%02d%02d' %{featurever} %{interimver} %{updatever} %{combiver} )
%else
# for techpreview, using 1, so slowdebugs can have 0
%global priority %( printf '%08d' 1 )
%endif

# Define milestone (EA for pre-releases, GA for releases)
# Release will be (where N is usually a number starting at 1):
# - 0.N%%{?extraver}%%{?dist} for EA releases,
# - N%%{?extraver}{?dist} for GA releases
%global is_ga           1
%if %{is_ga}
%global build_type GA
%global ea_designator ""
%global ea_designator_zip %{nil}
%global extraver %{nil}
%global eaprefix %{nil}
%else
%global build_type EA
%global ea_designator ea
%global ea_designator_zip -%{ea_designator}
%global extraver .%{ea_designator}
%global eaprefix 0.
%endif

# parametrized macros are order-sensitive
%global compatiblename  java-%{featurever}-%{origin}
%global fullversion     %{compatiblename}-%{version}-%{release}
# output dir stub
%define installoutputdir() %{expand:install/jdk%{featurever}.install%{?1}}
# we can copy the javadoc to not arched dir, or make it not noarch
%define uniquejavadocdir() %{expand:%{compatiblename}%{?1}}
# main id and dir of this jdk
%define uniquesuffix() %{expand:%{compatiblename}%{?1}}

#################################################################
# fix for https://bugzilla.redhat.com/show_bug.cgi?id=1111349
#         https://bugzilla.redhat.com/show_bug.cgi?id=1590796#c14
#         https://bugzilla.redhat.com/show_bug.cgi?id=1655938
%global _privatelibs libsplashscreen[.]so.*|libawt_xawt[.]so.*|libjli[.]so.*|libattach[.]so.*|libawt[.]so.*|libextnet[.]so.*|libawt_headless[.]so.*|libdt_socket[.]so.*|libfontmanager[.]so.*|libinstrument[.]so.*|libj2gss[.]so.*|libj2pcsc[.]so.*|libj2pkcs11[.]so.*|libjaas[.]so.*|libjavajpeg[.]so.*|libjdwp[.]so.*|libjimage[.]so.*|libjsound[.]so.*|libjsvml[.]so.*|liblcms[.]so.*|libmanagement[.]so.*|libmanagement_agent[.]so.*|libmanagement_ext[.]so.*|libmlib_image[.]so.*|libnet[.]so.*|libnio[.]so.*|libprefs[.]so.*|librmi[.]so.*|libsaproc[.]so.*|libsctp[.]so.*|libsimdsort[.]so.*|libsleef[.]so.*|libsyslookup[.]so.*|libzip[.]so.*%{freetype_lib}
%global _publiclibs libjawt[.]so.*|libjava[.]so.*|libjvm[.]so.*|libverify[.]so.*|libjsig[.]so.*
%if %is_system_jdk
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$
# Never generate lib-style provides/requires for any debug packages
%global exclude_from_regexp ^.*/%{uniquesuffix -- %{debug_suffix_unquoted}}/.*$|^.*/%{uniquesuffix -- %{fastdebug_suffix_unquoted}}/.*$
%global __provides_exclude_from %{exclude_from_regexp}
%global __requires_exclude_from %{exclude_from_regexp}
%else
# Don't generate provides/requires for JDK provided shared libraries at all.
%global __provides_exclude ^(%{_privatelibs}|%{_publiclibs})$
%global __requires_exclude ^(%{_privatelibs}|%{_publiclibs})$
%endif

# VM variant being built
%ifarch %{zero_arches}
%global vm_variant zero
%else
%global vm_variant server
%endif

%global etcjavasubdir     %{_sysconfdir}/java/java-%{javaver}-%{origin}
%define etcjavadir()      %{expand:%{etcjavasubdir}/%{uniquesuffix -- %{?1}}}
# Standard JPackage directories and symbolic links.
%define sdkdir()        %{expand:%{uniquesuffix -- %{?1}}}

%define sdkbindir()     %{expand:%{_jvmdir}/%{sdkdir -- %{?1}}/bin}
%define jrebindir()     %{expand:%{_jvmdir}/%{sdkdir -- %{?1}}/bin}

%global alt_java_name     alt-java

%global rpm_state_dir %{_localstatedir}/lib/rpm-state/

# For flatpack builds hard-code /usr/sbin/alternatives,
# otherwise use %%{_sbindir} relative path.
%if 0%{?flatpak}
%global alternatives_requires /usr/sbin/alternatives
%else
%global alternatives_requires %{_sbindir}/alternatives
%endif

%if %{with_systemtap}
# Where to install systemtap tapset (links)
# We would like these to be in a package specific sub-dir,
# but currently systemtap doesn't support that, so we have to
# use the root tapset dir for now. To distinguish between 64
# and 32 bit architectures we place the tapsets under the arch
# specific dir (note that systemtap will only pickup the tapset
# for the primary arch for now). Systemtap uses the machine name
# aka target_cpu as architecture specific directory name.
%global tapsetroot /usr/share/systemtap
%global tapsetdirttapset %{tapsetroot}/tapset/
%global tapsetdir %{tapsetdirttapset}/%{stapinstall}
%endif

# not-duplicated scriptlets for normal/debug packages
%global update_desktop_icons /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%define post_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
}

# We want fastdebug and slowdebug alternatives to have a lower
# priority than the normal alternatives, so the normal alternatives
# are the default.
# If the argument to this macro is non-nil, that is either -fastdebug
# or -slowdebug, then priority_for will expand to a value one less
# than the priority global.  If the argument to this macro is nil,
# that is represents the non-debug or normal package, then the result
# is the normal priority macro value.
# This computation is done at RPM macro expansion time, rather than at
# runtime, to keep scriptlets as simple as possible.
%define priority_for() %{expand:%[%{?1:1}%{!?1:0} ? %{priority} - 1 : %{priority}]}

%global man_comp .gz

%define alternatives_java_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
alternatives --install %{_bindir}/java java %{jrebindir -- %{?1}}/java %{priority_for -- %{?1}} \\
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{sdkdir -- %{?1}} \\
  --slave %{_bindir}/%{alt_java_name} %{alt_java_name} %{jrebindir -- %{?1}}/%{alt_java_name} \\
  --slave %{_bindir}/jcmd jcmd %{sdkbindir -- %{?1}}/jcmd \\
  --slave %{_bindir}/keytool keytool %{jrebindir -- %{?1}}/keytool \\
  --slave %{_bindir}/rmiregistry rmiregistry %{jrebindir -- %{?1}}/rmiregistry
%if %{pandoc_available}
alternatives --add-slave java %{jrebindir -- %{?1}}/java \\
  %{_mandir}/man1/java.1%{man_comp} java.1%{man_comp} %{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave java %{jrebindir -- %{?1}}/java \\
  %{_mandir}/man1/%{alt_java_name}.1%{man_comp} %{alt_java_name}.1%{man_comp} %{_mandir}/man1/%{alt_java_name}-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave java %{jrebindir -- %{?1}}/java \\
  %{_mandir}/man1/jcmd.1%{man_comp} jcmd.1%{man_comp} %{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave java %{jrebindir -- %{?1}}/java \\
  %{_mandir}/man1/keytool.1%{man_comp} keytool.1%{man_comp} %{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave java %{jrebindir -- %{?1}}/java \\
  %{_mandir}/man1/rmiregistry.1%{man_comp} rmiregistry.1%{man_comp} %{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1%{man_comp}
%endif
  
alternatives --install %{_jvmdir}/jre-%{origin} jre_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} %{priority_for -- %{?1}}
alternatives --install %{_jvmdir}/jre-%{javaver} jre_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}} %{priority_for -- %{?1}}
alternatives --install %{_jvmdir}/jre-%{javaver}-%{origin} jre_%{javaver}_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} %{priority_for -- %{?1}}
}

%define post_headless() %{expand:
%{alternatives_java_install -- %{?1}}
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
}

%define postun_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
}

# Perform alternatives removals in preun instead of postun so that we
# are removing live symbolic links instead of dangling symbolic links,
# even though the alternatives command does not seem to care.  The
# documentation uses preun or postun without providing a rationale for
# using one over the other:
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Alternatives/
#
# The [ $1 -eq 0 ] is an RPM scriptlet idiom meaning "only do the
# following if this scriptlet is being run during a straight package
# removal; in other words, do NOT do the following if this scriptlet
# is being run as part of an upgrade transaction".
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/#_syntax
%define preun_headless() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
if [ $1 -eq 0 ]
then
  alternatives --remove java %{jrebindir -- %{?1}}/java
  alternatives --remove jre_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}}
  alternatives --remove jre_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}}
  alternatives --remove jre_%{javaver}_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}}
fi
}

# Invoke gtk-update-icon-cache in posttrans instead of post as an
# optimization.  If other packages in the transaction install icons
# and use this optimization, then invocations of gtk-update-icon-cache
# will all happen in succession, and invocations after the first one
# will notice that the cache is fresh and immediately succeed.  If
# this were instead done in each package's post, then the icon cache
# would be regenerated every time, rendering the whole transaction
# slower.
# See:
# https://lists.fedoraproject.org/archives/list/packaging\
# @lists.fedoraproject.org/thread/HXIIKIHBMT3HELPKWH2BAXRNIF7BPPJD/
# and:
# https://fedoraproject.org/wiki/Archive:PackagingDrafts/Icon_Cache
%define posttrans_script() %{expand:
%{update_desktop_icons}
}

%define alternatives_javac_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
alternatives --install %{_bindir}/javac javac %{sdkbindir -- %{?1}}/javac %{priority_for -- %{?1}} \\
  --slave %{_jvmdir}/java java_sdk %{_jvmdir}/%{sdkdir -- %{?1}} \\
  --slave %{_bindir}/jar jar %{sdkbindir -- %{?1}}/jar \\
  --slave %{_bindir}/jarsigner jarsigner %{sdkbindir -- %{?1}}/jarsigner \\
  --slave %{_bindir}/javadoc javadoc %{sdkbindir -- %{?1}}/javadoc \\
  --slave %{_bindir}/javap javap %{sdkbindir -- %{?1}}/javap \\
  --slave %{_bindir}/jconsole jconsole %{sdkbindir -- %{?1}}/jconsole \\
  --slave %{_bindir}/jdb jdb %{sdkbindir -- %{?1}}/jdb \\
  --slave %{_bindir}/jdeps jdeps %{sdkbindir -- %{?1}}/jdeps \\
  --slave %{_bindir}/jdeprscan jdeprscan %{sdkbindir -- %{?1}}/jdeprscan \\
  --slave %{_bindir}/jfr jfr %{sdkbindir -- %{?1}}/jfr \\
%ifarch %{sa_arches}
%ifnarch %{zero_arches}
  --slave %{_bindir}/jhsdb jhsdb %{sdkbindir -- %{?1}}/jhsdb \\
%endif
%endif
  --slave %{_bindir}/jimage jimage %{sdkbindir -- %{?1}}/jimage \\
  --slave %{_bindir}/jinfo jinfo %{sdkbindir -- %{?1}}/jinfo \\
  --slave %{_bindir}/jlink jlink %{sdkbindir -- %{?1}}/jlink \\
  --slave %{_bindir}/jmap jmap %{sdkbindir -- %{?1}}/jmap \\
  --slave %{_bindir}/jmod jmod %{sdkbindir -- %{?1}}/jmod \\
  --slave %{_bindir}/jnativescan jnativescan %{sdkbindir -- %{?1}}/jnativescan \\
  --slave %{_bindir}/jps jps %{sdkbindir -- %{?1}}/jps \\
  --slave %{_bindir}/jpackage jpackage %{sdkbindir -- %{?1}}/jpackage \\
  --slave %{_bindir}/jrunscript jrunscript %{sdkbindir -- %{?1}}/jrunscript \\
  --slave %{_bindir}/jshell jshell %{sdkbindir -- %{?1}}/jshell \\
  --slave %{_bindir}/jstack jstack %{sdkbindir -- %{?1}}/jstack \\
  --slave %{_bindir}/jstat jstat %{sdkbindir -- %{?1}}/jstat \\
  --slave %{_bindir}/jstatd jstatd %{sdkbindir -- %{?1}}/jstatd \\
  --slave %{_bindir}/jwebserver jwebserver %{sdkbindir -- %{?1}}/jwebserver \\
  --slave %{_bindir}/serialver serialver %{sdkbindir -- %{?1}}/serialver
%if %{pandoc_available}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jar.1%{man_comp} jar.1%{man_comp} %{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jarsigner.1%{man_comp} jarsigner.1%{man_comp} %{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/javac.1%{man_comp} javac.1%{man_comp} %{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/javadoc.1%{man_comp} javadoc.1%{man_comp} %{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/javap.1%{man_comp} javap.1%{man_comp} %{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jconsole.1%{man_comp} jconsole.1%{man_comp} %{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jdb.1%{man_comp} jdb.1%{man_comp} %{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jdeps.1%{man_comp} jdeps.1%{man_comp} %{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jdeprscan.1%{man_comp} jdeprscan.1%{man_comp} %{_mandir}/man1/jdeprscan-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jfr.1%{man_comp} jfr.1%{man_comp} %{_mandir}/man1/jfr-%{uniquesuffix -- %{?1}}.1%{man_comp}
%ifarch %{sa_arches}
%ifnarch %{zero_arches}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jhsdb.1%{man_comp} jhsdb.1%{man_comp} %{_mandir}/man1/jhsdb-%{uniquesuffix -- %{?1}}.1%{man_comp}
%endif
%endif
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jimage.1%{man_comp} jimage.1%{man_comp} %{_mandir}/man1/jimage-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jinfo.1%{man_comp} jinfo.1%{man_comp} %{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jlink.1%{man_comp} jlink.1%{man_comp} %{_mandir}/man1/jlink-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jmap.1%{man_comp} jmap.1%{man_comp} %{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jmod.1%{man_comp} jmod.1%{man_comp} %{_mandir}/man1/jmod-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jnativescan.1%{man_comp} jnativescan.1%{man_comp} %{_mandir}/man1/jnativescan-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jps.1%{man_comp} jps.1%{man_comp} %{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jpackage.1%{man_comp} jpackage.1%{man_comp} %{_mandir}/man1/jpackage-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jrunscript.1%{man_comp} jrunscript.1%{man_comp} %{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jstack.1%{man_comp} jstack.1%{man_comp} %{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jstat.1%{man_comp} jstat.1%{man_comp} %{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jstatd.1%{man_comp} jstatd.1%{man_comp} %{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/jwebserver.1%{man_comp} jwebserver.1%{man_comp} %{_mandir}/man1/jwebserver-%{uniquesuffix -- %{?1}}.1%{man_comp}
alternatives --add-slave javac %{sdkbindir -- %{?1}}/javac \\
  %{_mandir}/man1/serialver.1%{man_comp} serialver.1%{man_comp} %{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1%{man_comp}
%endif
alternatives --install %{_jvmdir}/java-%{origin} java_sdk_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} %{priority_for -- %{?1}}
alternatives --install %{_jvmdir}/java-%{javaver} java_sdk_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}} %{priority_for -- %{?1}}
}

%define post_devel() %{expand:
%{alternatives_javac_install -- %{?1}}
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
}

%define preun_devel() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
if [ $1 -eq 0 ]
then
  alternatives --remove javac %{sdkbindir -- %{?1}}/javac
  alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}}
  alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}}
fi
}

%define postun_devel() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
update-desktop-database %{_datadir}/applications &> /dev/null || :

if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
}

%define posttrans_devel() %{expand:
%{update_desktop_icons}
}

%define alternatives_javadoc_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
alternatives --install %{_javadocdir}/java-%{origin} javadocdir_%{origin} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api %{priority_for -- %{?1}}
alternatives --install %{_javadocdir}/java-%{javaver} javadocdir_%{javaver} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api %{priority_for -- %{?1}}
alternatives --install %{_javadocdir}/java javadocdir %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api %{priority_for -- %{?1}}
}

%define preun_javadoc() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
if [ $1 -eq 0 ]
then
  alternatives --remove javadocdir %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api
  alternatives --remove javadocdir_%{origin} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api
  alternatives --remove javadocdir_%{javaver} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api
fi
}

%define alternatives_javadoczip_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
alternatives --install %{_javadocdir}/java-%{origin}.zip javadoczip_%{origin} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip %{priority_for -- %{?1}}
alternatives --install %{_javadocdir}/java-%{javaver}.zip javadoczip_%{javaver} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip %{priority_for -- %{?1}}
# Weird legacy filename for backwards-compatibility
alternatives --install %{_javadocdir}/java-zip javadoczip %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip %{priority_for -- %{?1}}
}

%define preun_javadoc_zip() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
if [ $1 -eq 0 ]
then
  alternatives --remove javadoczip %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
  alternatives --remove javadoczip_%{origin} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
  alternatives --remove javadoczip_%{javaver} %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
fi
}

%define files_jre() %{expand:
%{_datadir}/icons/hicolor/*x*/apps/java-%{javaver}-%{origin}.png
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsplashscreen.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libawt_xawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjawt.so
}

%define files_jre_headless() %{expand:
%license %{_jvmdir}/%{sdkdir -- %{?1}}/legal
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/NEWS
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/README.md
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/java-%{featurever}-openjdk-portable.specfile
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/openjdk-devkit.specfile
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/0*.patch
%dir %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}
%dir %{_sysconfdir}/.java/.systemPrefs
%dir %{_sysconfdir}/.java
%dir %{_jvmdir}/%{sdkdir -- %{?1}}
%{_jvmdir}/%{sdkdir -- %{?1}}/release
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/bin
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/java
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/%{alt_java_name}
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jcmd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/keytool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmiregistry
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib
%ifarch %{jit_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/classlist
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jexec
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jspawnhelper
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jrt-fs.jar
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/modules
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/psfont.properties.ja
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/psfontj2d.properties
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/tzdb.dat
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjli.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jvm.cfg
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libattach.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libextnet.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjsig.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libawt_headless.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libdt_socket.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libfontmanager.so
%if ! %{system_libs}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libfreetype.so
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libinstrument.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libj2gss.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libj2pcsc.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libj2pkcs11.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjaas.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjava.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjavajpeg.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjdwp.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjimage.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjsound.so
%ifarch %{svml_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjsvml.so
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/liblcms.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmanagement.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmanagement_agent.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmanagement_ext.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmlib_image.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libnet.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libnio.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libprefs.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/librmi.so
# Some architectures don't have the serviceability agent
%ifarch %{sa_arches}
%ifnarch %{zero_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsaproc.so
%endif
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsctp.so
%ifarch %{simdsort_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsimdsort.so
%endif
%ifarch %{sleef_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsleef.so
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsyslookup.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libverify.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libzip.so
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/jfr
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jfr/default.jfc
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jfr/profile.jfc
%if %{pandoc_available}
%{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/%{alt_java_name}-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1*
%endif
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/*.so
%ifarch %{share_arches}
%attr(444, root, root) %{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/classes.jsa
#attr(444, root, root) %{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/classes_coh.jsa
%ifnarch %{ix86} %{arm32}
%attr(444, root, root) %{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/classes_nocoops.jsa
%attr(444, root, root) %{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/classes_nocoops_coh.jsa
%endif
%endif
%dir %{etcjavasubdir}
%dir %{etcjavadir -- %{?1}}
%dir %{etcjavadir -- %{?1}}/lib
%dir %{etcjavadir -- %{?1}}/lib/security
%{etcjavadir -- %{?1}}/lib/security/cacerts
%dir %{etcjavadir -- %{?1}}/conf
%dir %{etcjavadir -- %{?1}}/conf/sdp
%dir %{etcjavadir -- %{?1}}/conf/management
%dir %{etcjavadir -- %{?1}}/conf/security
%dir %{etcjavadir -- %{?1}}/conf/security/policy
%dir %{etcjavadir -- %{?1}}/conf/security/policy/limited
%dir %{etcjavadir -- %{?1}}/conf/security/policy/unlimited
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/blocked.certs
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/public_suffix_list.dat
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/limited/exempt_local.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/limited/default_local.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/limited/default_US_export.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/unlimited/default_local.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/unlimited/default_US_export.policy
 %{etcjavadir -- %{?1}}/conf/security/policy/README.txt
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/java.security
%dir %{etcjavadir -- %{?1}}/conf/security/redhat
%dir %{etcjavadir -- %{?1}}/conf/security/redhat/false
%dir %{etcjavadir -- %{?1}}/conf/security/redhat/true
# config-noreplace in case the system administrator wants to adjust
# the FIPS configuration
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/redhat/SunPKCS11-FIPS.cfg
# config-noreplace in case the system administrator wants to change
# the default for crypto-policies usage
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/redhat/crypto-policies.properties
# The system administrator is never expected to change these files -- they
# are implementation details -- so leave them as not config-noreplace
%config %{etcjavadir -- %{?1}}/conf/security/redhat/false/crypto-policies.properties
%config %{etcjavadir -- %{?1}}/conf/security/redhat/true/crypto-policies.properties
%config %{etcjavadir -- %{?1}}/conf/security/redhat/false/fips.properties
%config %{etcjavadir -- %{?1}}/conf/security/redhat/true/fips.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/management/jmxremote.access
# This is a config template, thus not config-noreplace
%config  %{etcjavadir -- %{?1}}/conf/management/jmxremote.password.template
%config  %{etcjavadir -- %{?1}}/conf/sdp/sdp.conf.template
%config(noreplace) %{etcjavadir -- %{?1}}/conf/management/management.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/jaxp.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/jaxp-strict.properties.template
%config(noreplace) %{etcjavadir -- %{?1}}/conf/logging.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/net.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/sound.properties
%{_jvmdir}/%{sdkdir -- %{?1}}/conf
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/security
%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_bindir}/java
%ghost %{_jvmdir}/jre
%ghost %{_bindir}/%{alt_java_name}
%ghost %{_bindir}/jcmd
%ghost %{_bindir}/keytool
%ghost %{_bindir}/rmiregistry
%ghost %{_jvmdir}/jre-%{origin}
%ghost %{_jvmdir}/jre-%{javaver}
%ghost %{_jvmdir}/jre-%{javaver}-%{origin}
%endif
%endif
# https://bugzilla.redhat.com/show_bug.cgi?id=1820172
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Directory_Replacement/
%ghost %{_jvmdir}/%{sdkdir -- %{?1}}/conf.rpmmoved
%ghost %{_jvmdir}/%{sdkdir -- %{?1}}/lib/security.rpmmoved
}

%define files_devel() %{expand:
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/bin
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jar
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jarsigner
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javac
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javadoc
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jconsole
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdb
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdeps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdeprscan
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jfr
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jimage
# Some architectures don't have the serviceability agent
%ifarch %{sa_arches}
%ifnarch %{zero_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jhsdb
%if %{pandoc_available}
%{_mandir}/man1/jhsdb-%{uniquesuffix -- %{?1}}.1*
%endif
%endif
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jinfo
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jlink
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jmap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jmod
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jnativescan
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jpackage
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jrunscript
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jshell
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstack
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstat
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstatd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jwebserver
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/serialver
%{_jvmdir}/%{sdkdir -- %{?1}}/include
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/ct.sym

%if %{with_systemtap}
%{_jvmdir}/%{sdkdir -- %{?1}}/tapset
%endif

%{_datadir}/applications/*jconsole%{?1}.desktop

%if %{pandoc_available}
%{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdeprscan-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jfr-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jlink-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jmod-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jnativescan-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jpackage-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jshell-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jwebserver-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1*
%endif

%if %{with_systemtap}
%dir %{tapsetroot}
%dir %{tapsetdirttapset}
%dir %{tapsetdir}
%{tapsetdir}/*%{_arch}%{?1}.stp
%endif

%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_bindir}/javac
%ghost %{_jvmdir}/java
%ghost %{_bindir}/jhsdb
%ghost %{_bindir}/jar
%ghost %{_bindir}/jarsigner
%ghost %{_bindir}/javadoc
%ghost %{_bindir}/javap
%ghost %{_bindir}/jconsole
%ghost %{_bindir}/jdb
%ghost %{_bindir}/jdeps
%ghost %{_bindir}/jdeprscan
%ghost %{_bindir}/jfr
%ghost %{_bindir}/jimage
%ghost %{_bindir}/jinfo
%ghost %{_bindir}/jlink
%ghost %{_bindir}/jmap
%ghost %{_bindir}/jmod
%ghost %{_bindir}/jnativescan
%ghost %{_bindir}/jps
%ghost %{_bindir}/jpackage
%ghost %{_bindir}/jrunscript
%ghost %{_bindir}/jshell
%ghost %{_bindir}/jstack
%ghost %{_bindir}/jstat
%ghost %{_bindir}/jstatd
%ghost %{_bindir}/jwebserver
%ghost %{_bindir}/serialver
%ghost %{_jvmdir}/java-%{origin}
%ghost %{_jvmdir}/java-%{javaver}
%endif
%endif
}

%define files_jmods() %{expand:
%{_jvmdir}/%{sdkdir -- %{?1}}/jmods
}

%define files_demo() %{expand:
%{_jvmdir}/%{sdkdir -- %{?1}}/demo
}

%define files_src() %{expand:
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/src.zip
}

%define files_static_libs() %{expand:
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/static
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/static/linux-%{archinstall}
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/static/linux-%{archinstall}/glibc
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/static/linux-%{archinstall}/glibc/lib*.a
}

%define files_javadoc() %{expand:
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}
%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_javadocdir}/java
%ghost %{_javadocdir}/java-%{origin}
%ghost %{_javadocdir}/java-%{javaver}
%endif
%endif
}

%define files_javadoc_zip() %{expand:
%dir %{_javadocdir}/%{uniquejavadocdir -- %{?1}}
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_javadocdir}/java-zip
%ghost %{_javadocdir}/java-%{origin}.zip
%ghost %{_javadocdir}/java-%{javaver}.zip
%endif
%endif
}

%define files_crypto_adapter() %{expand:
%dir %{_libdir}/%{sdkdir -- %{?1}}
%{_libdir}/%{sdkdir -- %{?1}}/libnssadapter.so
}

# not-duplicated requires/provides/obsoletes for normal/debug packages
%define java_rpo() %{expand:
Requires: fontconfig%{?_isa}
Requires: xorg-x11-fonts-Type1
# Require libXcomposite explicitly since it's only dynamically loaded
# at runtime. Fixes screenshot issues. See JDK-8150954.
Requires: libXcomposite%{?_isa}
# Requires rest of java
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# for java-X-openjdk package's desktop binding
# Where recommendations are available, recommend Gtk+ for the Swing look and feel
%if 0%{?rhel} >= 8 || 0%{?fedora} > 0
Recommends: gtk3%{?_isa}
%endif
# Recommend PipeWire for screenshots under Wayland.
%if 0%{?rhel} >= 9 || 0%{?fedora} > 0
Recommends: pipewire%{?_isa}
%endif

Provides: java-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}

# Standard JPackage base provides
Provides: jre-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java%{?1} = %{epoch}:%{version}-%{release}
Provides: jre%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_headless_rpo() %{expand:
# Require /etc/pki/java/cacerts
Requires: ca-certificates
# Require javapackages-filesystem for ownership of /usr/lib/jvm/ and macros
Requires: javapackages-filesystem
# Require zone-info data provided by tzdata-java sub-package
# 2025a required as of JDK-8347965
Requires: tzdata-java >= 2025a
# for support of kernel stream control
# libsctp.so.1 is being `dlopen`ed on demand
Requires: lksctp-tools%{?_isa}
# for printing support
Requires: cups-libs
# for system security properties
Requires: crypto-policies
# Post requires alternatives to install tool alternatives
Requires(post):   %{alternatives_requires}
# Postun requires alternatives to uninstall tool alternatives
Requires(postun): %{alternatives_requires}
# Where suggestions are available, recommend the sctp and pcsc libraries
# for optional support of kernel stream control and card reader
%if 0%{?rhel} >= 8 || 0%{?fedora} > 0
Suggests: lksctp-tools%{?_isa}, pcsc-lite-libs%{?_isa}
%endif
# for libnssadapter.so
Requires: %{name}-crypto-adapter%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

# Standard JPackage base provides
Provides: jre-%{javaver}-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-headless%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_devel_rpo() %{expand:
# Requires base package
Requires:         %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives
Requires(post):   %{alternatives_requires}
# Postun requires alternatives to uninstall tool alternatives
Requires(postun): %{alternatives_requires}

# Standard JPackage devel provides
Provides: java-sdk-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-sdk-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-devel%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-devel%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-devel-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-sdk-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-devel%{?1} = %{epoch}:%{version}-%{release}
Provides: java-sdk%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_static_libs_rpo() %{expand:
Requires:         %{name}-devel%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
}

# Requires the devel package which contains jmod and jlink
%define java_jmods_rpo() %{expand:
# As most jmods are bytecode, they should be OK without any _isa
# (java.base mod does contain native libraries)
Requires:         %{name}-devel%{?1} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1} = %{epoch}:%{version}-%{release}

Provides: java-%{javaver}-jmods%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-jmods%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-jmods%{?1} = %{epoch}:%{version}-%{release}
%endif
}

# The demo package depends on the full graphical JRE which is needed to
# run the demos.
%define java_demo_rpo() %{expand:
Requires: %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

Provides: java-%{javaver}-demo%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-demo%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-demo%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{origin}-demo%{?1} = %{epoch}:%{version}-%{release}
%endif
}

# The javadoc packages depend on the headless package for the legal documentation.
# Potentially, the legal documentation could be split into a small package
# which the javadoc and headless packages then depend on, but it does not
# seem worth the additional disruption just to have docs installed and no JDK.
# Arguments:
# - 1 = package name suffix (called twice for javadoc-zip with nil & -zip)
%define java_javadoc_rpo() %{expand:
# Standard JPackage javadoc provides
Provides: java-%{javaver}-javadoc%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-javadoc%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-javadoc%{?1} = %{epoch}:%{version}-%{release}
%endif
}

# The src package depends on the headless package for the legal documentation.
# Potentially, the legal documentation could be split into a small package
# which the src and headless package then depend on, but it does not
# seem worth the additional disruption just to have sources installed and no JDK.
%define java_src_rpo() %{expand:
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

# Standard JPackage sources provides
Provides: java-%{javaver}-src%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-src%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-src%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{origin}-src%{?1} = %{epoch}:%{version}-%{release}
%endif
}

# Prevent brp-java-repack-jars from being run
%global __jar_repack 0
# Define the root name of the portable packages
%global pkgnameroot java-%{featurever}-%{origin}-portable%{?pkgos:-%{pkgos}}

# Define the architectures on which we build
ExclusiveArch: %{aarch64} %{ppc64le} s390x x86_64 riscv64 %{arm}

Name:    java-%{javaver}-%{origin}
Version: %{newjavaver}.%{buildver}
Release: %{?eaprefix}%{rpmrelease}%{?extraver}%{?dist}.redsleeve
# Equivalent for the portable build
%global prelease %{?eaprefix}%{portablerelease}%{?extraver}
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons
# and this change was brought into RHEL-4. java-1.5.0-ibm packages
# also included the epoch in their virtual provides. This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0". In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0. So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages. Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".

Epoch:   1
Summary: %{origin_nice} %{featurever} Runtime Environment
# Groups are only used up to RHEL 8 and on Fedora versions prior to F30
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

# HotSpot code is licensed under GPLv2
# JDK library code is licensed under GPLv2 with the Classpath exception
# The Apache license is used in code taken from Apache projects (primarily xalan & xerces)
# DOM levels 2 & 3 and the XML digital signature schemas are licensed under the W3C Software License
# The JSR166 concurrency code is in the public domain
# The BSD and MIT licenses are used for a number of third-party libraries (see ADDITIONAL_LICENSE_INFO)
# The OpenJDK source tree includes:
# - JPEG library (IJG), zlib & libpng (zlib), giflib (MIT), harfbuzz (ISC),
# - freetype (FTL), jline (BSD) and LCMS (MIT)
# - jquery (MIT), jdk.crypto.cryptoki PKCS 11 wrapper (RSA)
# - public_suffix_list.dat from publicsuffix.org (MPLv2.0)
# The test code includes copies of NSS under the Mozilla Public License v2.0
# The PCSClite headers are under a BSD with advertising license
# The elliptic curve cryptography (ECC) source code is licensed under the LGPLv2.1 or any later version
License:  ASL 1.1 and ASL 2.0 and BSD and BSD with advertising and GPL+ and GPLv2 and GPLv2 with exceptions and IJG and LGPLv2+ and MIT and MPLv2.0 and Public Domain and W3C and zlib and ISC and FTL and RSA
URL:      http://openjdk.java.net/

# The source tarball, generated using generate_source_tarball.sh
Source0: https://openjdk-sources.osci.io/openjdk%{featurever}/open%{vcstag}%{ea_designator_zip}.tar.xz

# Use 'icedtea_sync.sh' to update the following
# They are based on code contained in the IcedTea project (6.x).
# Systemtap tapsets. Zipped up to keep it small.
Source8: tapsets-icedtea-%{icedteaver}.tar.xz

# Desktop files. Adapted from IcedTea
Source9: jconsole.desktop.in

# Source code for alt-java
Source11: alt-java.c

# Removed libraries that we link instead
Source12: remove-intree-libraries.sh

# Ensure we aren't using the limited crypto policy
Source13: TestCryptoLevel.java

# Ensure ECDSA is working
Source14: TestECDSA.java

# Verify system crypto (policy) can be disabled via a property
Source15: TestSecurityProperties.java

# Ensure vendor settings are correct
Source16: CheckVendor.java

# Ensure translations are available for new timezones
Source18: TestTranslations.java

# Include portable spec and instructions on how to rebuild
Source19: README.md
Source20: java-%{featurever}-openjdk-portable.specfile
Source21: NEWS
Source22: openjdk-devkit.specfile
# Devkit patches; see https://github.com/rh-openjdk/jdk/tree/devkit
# To regenerate, use git format-patch -N jdk21u/master
# Add RHEL RPM URLs and turn off robots
Source23: 0001-Allow-devkit-to-work-with-RHEL.patch
# Turn off multilib on x86_64
Source24: 0002-Disable-multilib-on-x86_64.patch
# Improve build logging (OPENJDK-3071)
Source25: 0003-Log-devkit-build-to-stdout.patch
# Remove .comment sections from sysroot objects
Source26: 0004-devkit-Remove-.comment-sections-from-sysroot-objects.patch
# Configure binutils with --enable-deterministic-archives
Source27: 0005-Tools.gmk-Configure-binutils-with-enable-determinist.patch
# Configure gcc with --enable-linker-build-id (OPENJDK-3068)
Source28: 0006-Tools.gmk-Add-enable-linker-build-id-to-gcc-build.patch
# Exclude systemtap-sdt-devel on s390x & ppc64* (OPENJDK-3070)
Source29: 0007-Tools.gmk-Exclude-systemtap-sdt-devel-on-s390x-ppc64.patch
# Use update repository on RHEL rather than GA (OPENJDK-3589)
Source30: 0008-Tools.gmk-Use-update-repository-on-RHEL-rather-than-.patch

# FIPS support sources.
# For libnssadapter.so (RHEL-128413)
Source31: https://github.com/rh-openjdk/nss-native-fips-key-import-export-adapter/releases/download/%{nssadapter_version}/%{nssadapter_name}.tar.xz
# Create OpenJDK's crypto-policies hierarchy (RHEL-128409)
Source32: create-redhat-properties-files.bash

# Setup variables to reference correct sources
%global releasezip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.unstripped.jdk.%{_arch}.tar.xz
%global staticlibzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.static-libs.%{_arch}.tar.xz
%global docszip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.docs.%{_arch}.tar.xz
%global misczip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.misc.%{_arch}.tar.xz
%global slowdebugzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.slowdebug.jdk.%{_arch}.tar.xz
%global slowdebugstaticlibzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.slowdebug.static-libs.%{_arch}.tar.xz
%global fastdebugzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.fastdebug.jdk.%{_arch}.tar.xz
%global fastdebugstaticlibzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.fastdebug.static-libs.%{_arch}.tar.xz

############################################
#
# RPM/distribution specific patches
#
############################################

# Crypto policy and FIPS support patches
# Patch is generated from the fips-25u tree at https://github.com/rh-openjdk/jdk/tree/fips-25u
# as follows: git diff %%{vcstag} src make test > fips-25u-$(git show -s --format=%h HEAD).patch
# Diff is limited to src and make subdirectories to exclude .github changes
# Fixes currently included:
# OPENJDK-2108: Internal __redhat_fips__ property
# OPENJDK-2123: Algorithms lockdown
# OPENJDK-4559: Red Hat Build of OpenJDK 25 should not restrict all the providers in FIPS
Patch1001: fips-%{featurever}u-%{fipsver}.patch

#############################################
#
# OpenJDK patches in need of upstreaming
#
#############################################

# Currently empty

#############################################
#
# OpenJDK patches which missed last update
#
#############################################

# JDK-8375294: (fs) Files.copy can fail with EOPNOTSUPP when copy_file_range not supported
Patch2001: jdk8375294-handle-EOPNOTSUPP-in-copying.patch

#############################################
#
# Portable build specific patches
#
#############################################

# Currently empty

#############################################
#
# NSS adapter patches
#
#############################################

# Currently empty

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: alsa-lib-devel
BuildRequires: binutils
BuildRequires: cups-devel
# From RHEL 10, debugedit is in its own package
%if 0%{?rhel} >= 10
BuildRequires: debugedit
%endif
BuildRequires: desktop-file-utils
# elfutils only are OK for build without AOT
BuildRequires: elfutils-devel
BuildRequires: fontconfig-devel
BuildRequires: gcc-c++
BuildRequires: gdb
BuildRequires: libxslt
BuildRequires: libX11-devel
BuildRequires: libXi-devel
BuildRequires: libXinerama-devel
BuildRequires: libXrandr-devel
BuildRequires: libXrender-devel
BuildRequires: libXt-devel
BuildRequires: libXtst-devel
# Requirement for system security property test
BuildRequires: crypto-policies
BuildRequires: pkgconfig
BuildRequires: xorg-x11-proto-devel
BuildRequires: zip
BuildRequires: javapackages-filesystem
%if %{include_normal_build}
BuildRequires: %{pkgnameroot}-unstripped = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: %{pkgnameroot}-static-libs = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
%endif
%if %{include_fastdebug_build}
BuildRequires: %{pkgnameroot}-devel-fastdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: %{pkgnameroot}-static-libs-fastdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
%endif
%if %{include_debug_build}
BuildRequires: %{pkgnameroot}-devel-slowdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: %{pkgnameroot}-static-libs-slowdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
%endif
BuildRequires: %{pkgnameroot}-docs = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: %{pkgnameroot}-misc = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
# Zero-assembler build requirement
%ifarch %{zero_arches}
BuildRequires: libffi-devel
%endif
# 2025a required as of JDK-8347965
BuildRequires: tzdata-java >= 2025a
# Earlier versions have a bug in tree vectorization on PPC
BuildRequires: gcc >= 4.8.3-8

%if %{with_systemtap}
BuildRequires: systemtap-sdt-devel
%endif
BuildRequires: make

# libnssadapter.so build requirements
BuildRequires: nss-devel
BuildRequires: nss-softokn-devel

%if %{system_libs}
BuildRequires: freetype-devel
BuildRequires: giflib-devel
BuildRequires: harfbuzz-devel
BuildRequires: lcms2-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: zlib-devel
%else
# Version in src/java.desktop/share/legal/freetype.md
Provides: bundled(freetype) = 2.14.2
# Version in src/java.desktop/share/native/libsplashscreen/giflib/gif_lib.h
Provides: bundled(giflib) = 6.1.2
# Version in src/java.desktop/share/native/libharfbuzz/hb-version.h
Provides: bundled(harfbuzz) = 12.3.2
# Version in src/java.desktop/share/native/liblcms/lcms2.h
Provides: bundled(lcms2) = 2.17.0
# Version in src/java.desktop/share/native/libjavajpeg/jpeglib.h
Provides: bundled(libjpeg) = 6b
# Version in src/java.desktop/share/native/libsplashscreen/libpng/png.h
Provides: bundled(libpng) = 1.6.57
# Version in src/java.base/share/native/libzip/zlib/zlib.h
Provides: bundled(zlib) = 1.3.2
%endif
%ifarch %{sleef_arches}
# SLEEF is always bundled
# Version in src/jdk.incubator.vector/linux/native/libsleef/generated/sleefinline_advsimd.h
Provides: bundled(sleef) = 3.6.1
%endif

# this is always built, also during debug-only build
# when it is built in debug-only this package is just placeholder
%{java_rpo %{nil}}

%description
The %{origin_nice} %{featurever} runtime environment.

%if %{include_debug_build}
%package slowdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_rpo -- %{debug_suffix_unquoted}}
%description slowdebug
The %{origin_nice} %{featurever} runtime environment.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package fastdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_rpo -- %{fastdebug_suffix_unquoted}}
%description fastdebug
The %{origin_nice} %{featurever} runtime environment.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package headless
Summary: %{origin_nice} %{featurever} Headless Runtime Environment
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_headless_rpo %{nil}}

%description headless
The %{origin_nice} %{featurever} runtime environment without audio and video support.
%endif

%if %{include_debug_build}
%package headless-slowdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_headless_rpo -- %{debug_suffix_unquoted}}

%description headless-slowdebug
The %{origin_nice} %{featurever} runtime environment without audio and video support.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package headless-fastdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_headless_rpo -- %{fastdebug_suffix_unquoted}}

%description headless-fastdebug
The %{origin_nice} %{featurever} runtime environment without audio and video support.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package devel
Summary: %{origin_nice} %{featurever} Development Environment
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_devel_rpo %{nil}}

%description devel
The %{origin_nice} %{featurever} development tools.
%endif

%if %{include_debug_build}
%package devel-slowdebug
Summary: %{origin_nice} %{featurever} Development Environment %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_devel_rpo -- %{debug_suffix_unquoted}}

%description devel-slowdebug
The %{origin_nice} %{featurever} development tools.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package devel-fastdebug
Summary: %{origin_nice} %{featurever} Development Environment %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Tools
%endif

%{java_devel_rpo -- %{fastdebug_suffix_unquoted}}

%description devel-fastdebug
The %{origin_nice} %{featurever} development tools              .
%{fastdebug_warning}
%endif

%if %{include_staticlibs}

%if %{include_normal_build}
%package static-libs
Summary: %{origin_nice} %{featurever} libraries for static linking

%{java_static_libs_rpo %{nil}}

%description static-libs
The %{origin_nice} %{featurever} libraries for static linking.
%endif

%if %{include_debug_build}
%package static-libs-slowdebug
Summary: %{origin_nice} %{featurever} libraries for static linking %{debug_on}

%{java_static_libs_rpo -- %{debug_suffix_unquoted}}

%description static-libs-slowdebug
The %{origin_nice} %{featurever} libraries for static linking.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package static-libs-fastdebug
Summary: %{origin_nice} %{featurever} libraries for static linking %{fastdebug_on}

%{java_static_libs_rpo -- %{fastdebug_suffix_unquoted}}

%description static-libs-fastdebug
The %{origin_nice} %{featurever} libraries for static linking.
%{fastdebug_warning}
%endif

# staticlibs
%endif

%if %{include_normal_build}
%package jmods
Summary: JMods for %{origin_nice} %{featurever}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_jmods_rpo %{nil}}

%description jmods
The JMods for %{origin_nice} %{featurever}.
%endif

%if %{include_debug_build}
%package jmods-slowdebug
Summary: JMods for %{origin_nice} %{featurever} %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_jmods_rpo -- %{debug_suffix_unquoted}}

%description jmods-slowdebug
The JMods for %{origin_nice} %{featurever}.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package jmods-fastdebug
Summary: JMods for %{origin_nice} %{featurever} %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Tools
%endif

%{java_jmods_rpo -- %{fastdebug_suffix_unquoted}}

%description jmods-fastdebug
The JMods for %{origin_nice} %{featurever}.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package demo
Summary: %{origin_nice} %{featurever} Demos
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_demo_rpo %{nil}}

%description demo
The %{origin_nice} %{featurever} demos.
%endif

%if %{include_debug_build}
%package demo-slowdebug
Summary: %{origin_nice} %{featurever} Demos %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_demo_rpo -- %{debug_suffix_unquoted}}

%description demo-slowdebug
The %{origin_nice} %{featurever} demos.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package demo-fastdebug
Summary: %{origin_nice} %{featurever} Demos %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_demo_rpo -- %{fastdebug_suffix_unquoted}}

%description demo-fastdebug
The %{origin_nice} %{featurever} demos.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package src
Summary: %{origin_nice} %{featurever} Source Bundle
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_src_rpo %{nil}}

%description src
The %{compatiblename}-src sub-package contains the complete %{origin_nice} %{featurever}
class library source code for use by IDE indexers and debuggers.
%endif

%if %{include_debug_build}
%package src-slowdebug
Summary: %{origin_nice} %{featurever} Source Bundle %{for_debug}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_src_rpo -- %{debug_suffix_unquoted}}

%description src-slowdebug
The %{compatiblename}-src-slowdebug sub-package contains the complete %{origin_nice} %{featurever}
 class library source code for use by IDE indexers and debuggers, %{for_debug}.
%endif

%if %{include_fastdebug_build}
%package src-fastdebug
Summary: %{origin_nice} %{featurever} Source Bundle %{for_fastdebug}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_src_rpo -- %{fastdebug_suffix_unquoted}}

%description src-fastdebug
The %{compatiblename}-src-fastdebug sub-package contains the complete %{origin_nice} %{featurever}
 class library source code for use by IDE indexers and debuggers, %{for_fastdebug}.
%endif

%if %{include_normal_build}
%package javadoc
Summary: %{origin_nice} %{featurever} API documentation
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Documentation
%endif
Requires: javapackages-filesystem
Requires: %{name}-headless%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: javadoc-slowdebug < 1:13.0.0.33-1.rolling
# Post requires alternatives to install javadoc alternative
Requires(post):   %{alternatives_requires}
# Postun requires alternatives to uninstall javadoc alternative
Requires(postun): %{alternatives_requires}

%{java_javadoc_rpo -- %{nil}}

%description javadoc
The %{origin_nice} %{featurever} API documentation.
%package javadoc-zip
Summary: %{origin_nice} %{featurever} API documentation compressed in a single archive
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Documentation
%endif
Requires: javapackages-filesystem
Requires: %{name}-headless%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: javadoc-zip-slowdebug < 1:13.0.0.33-1.rolling
# Post requires alternatives to install javadoc alternative
Requires(post):   %{alternatives_requires}
# Postun requires alternatives to uninstall javadoc alternative
Requires(postun): %{alternatives_requires}

%{java_javadoc_rpo -- -zip}
%{java_javadoc_rpo -- %{nil}}

%description javadoc-zip
The %{origin_nice} %{featurever} API documentation compressed in a single archive.
%endif

# java-25-openjdk-crypto-adapter
%if %{include_normal_build}
%package crypto-adapter
Summary: %{origin_nice} %{featurever} Cryptography Adapter Library
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

# java-25-openjdk-crypto-adapter does not need an "rpo" function since
# its specific nss and nss-softokn library requirements are
# automatically generated by RPM.

%description crypto-adapter
The %{origin_nice} %{featurever} cryptography adapter library.
%endif

%if %{include_debug_build}
%package crypto-adapter-slowdebug
Summary: %{origin_nice} %{featurever} Cryptography Adapter Library %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%description crypto-adapter-slowdebug
The %{origin_nice} %{featurever} cryptography adapter library.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package crypto-adapter-fastdebug
Summary: %{origin_nice} %{featurever} Cryptography Adapter Library %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%description crypto-adapter-fastdebug
The %{origin_nice} %{featurever} cryptography adapter library.
%{fastdebug_warning}
%endif

%prep

echo "Preparing %{oj_vendor_version}"
echo "System is RHEL=%{?rhel}%{!?rhel:0}, CentOS=%{?centos}%{!?centos:0}, EPEL=%{?epel}%{!?epel:0}, Fedora=%{?fedora}%{!?fedora:0}"

# Using the echo macro breaks rpmdev-bumpspec, as it parses the first line of stdout :-(
%if 0%{?stapinstall:1}
  echo "CPU: %{_target_cpu}, arch install directory: %{archinstall}, SystemTap install directory: %{stapinstall}"
%else
  %{error:Unrecognised architecture %{_target_cpu}}
%endif

if [ %{include_normal_build} -eq 0 -o  %{include_normal_build} -eq 1 ] ; then
  echo "include_normal_build is %{include_normal_build}"
else
  echo "include_normal_build is %{include_normal_build}, that is invalid. Use 1 for yes or 0 for no"
  exit 11
fi
if [ %{include_debug_build} -eq 0 -o  %{include_debug_build} -eq 1 ] ; then
  echo "include_debug_build is %{include_debug_build}"
else
  echo "include_debug_build is %{include_debug_build}, that is invalid. Use 1 for yes or 0 for no"
  exit 12
fi
if [ %{include_fastdebug_build} -eq 0 -o  %{include_fastdebug_build} -eq 1 ] ; then
  echo "include_fastdebug_build is %{include_fastdebug_build}"
else
  echo "include_fastdebug_build is %{include_fastdebug_build}, that is invalid. Use 1 for yes or 0 for no"
  exit 13
fi
if [ %{include_debug_build} -eq 0 -a  %{include_normal_build} -eq 0 -a  %{include_fastdebug_build} -eq 0 ] ; then
  echo "You have disabled all builds (normal,fastdebug,slowdebug). That is a no go."
  exit 14
fi

export XZ_OPT="-T0"
%setup -q -c -n %{uniquesuffix ""} -T -a 0
# Prepare libnssadapter.so source code
tar -xJf %{SOURCE31}
# https://bugzilla.redhat.com/show_bug.cgi?id=1189084
prioritylength=`expr length %{priority}`
if [ $prioritylength -ne 8 ] ; then
 echo "priority must be 8 digits in total, violated"
 exit 14
fi

# OpenJDK patches

%if %{system_libs}
# Remove libraries that are linked by both static and dynamic builds
sh %{SOURCE12} %{top_level_dir_name}
%endif

# Patch the JDK
# This syntax is deprecated:
#    %patchN [...]
# and should be replaced with:
#    %patch -PN [...]
# For example:
#    %patch1001 -p1
# becomes:
#    %patch -P1001 -p1
# The replacement format suggested by recent (circa Fedora 38) RPM
# deprecation messages:
#    %patch N [...]
# is not backward-compatible with prior (circa RHEL-8) versions of
# rpmbuild.
pushd %{top_level_dir_name}
# Add crypto policy and FIPS support
%patch -P1001 -p1
# Add EOPNOTSUPP patch
%patch -P2001 -p1
popd # openjdk

# Patch NSS adapter
pushd %{nssadapter_name}
# Nothing to do
popd # nssadapter

# The OpenJDK version file includes the current
# upstream version information. For some reason,
# configure does not automatically use the
# default pre-version supplied there (despite
# what the file claims), so we pass it manually
# to configure
VERSION_FILE=$(pwd)/%{top_level_dir_name}/make/conf/version-numbers.conf
if [ -f ${VERSION_FILE} ] ; then
    UPSTREAM_EA_DESIGNATOR=$(grep '^DEFAULT_PROMOTED_VERSION_PRE' ${VERSION_FILE} | cut -d '=' -f 2)
else
    echo "Could not find OpenJDK version file.";
    exit 16
fi
if [ "x${UPSTREAM_EA_DESIGNATOR}" != "x%{ea_designator}" ] ; then
    echo "WARNING: Designator mismatch";
    echo "Spec file is configured for a %{build_type} build with designator '%{ea_designator}'"
    echo "Upstream version-pre setting is '${UPSTREAM_EA_DESIGNATOR}'";
    exit 17
fi

# Prepare desktop files
# The _X_ syntax indicates variables that are replaced by make upstream
# The @X@ syntax indicates variables that are replaced by configure upstream
for suffix in %{build_loop} ; do
for file in %{SOURCE9}; do
    FILE=`basename $file | sed -e s:\.in$::g`
    EXT="${FILE##*.}"
    NAME="${FILE%.*}"
    OUTPUT_FILE=$NAME$suffix.$EXT
    sed    -e  "s:_SDKBINDIR_:%{sdkbindir -- $suffix}:g" $file > $OUTPUT_FILE
    sed -i -e  "s:@target_cpu@:%{_arch}:g" $OUTPUT_FILE
    sed -i -e  "s:@OPENJDK_VER@:%{version}-%{release}.%{_arch}$suffix:g" $OUTPUT_FILE
    sed -i -e  "s:@JAVA_VER@:%{javaver}:g" $OUTPUT_FILE
    sed -i -e  "s:@JAVA_VENDOR@:%{origin}:g" $OUTPUT_FILE
done
done

%build

function customisejdk() {
    local imagepath=${1}
    local suffix=${2}

    if [ -d ${imagepath} ] ; then
        # Install crypto-policies FIPS configuration files and append
        # include line to java.security
        bash -ex %{SOURCE32} ${imagepath}/conf/security %{_libdir}/%{sdkdir -- ${suffix}}/libnssadapter.so

        # Use system-wide tzdata
        rm ${imagepath}/lib/tzdb.dat
        ln -s %{_datadir}/javazi-1.8/tzdb.dat ${imagepath}/lib/tzdb.dat
    fi
}

export XZ_OPT="-T0"

mkdir -p $(dirname %{installoutputdir})

docdir=%{installoutputdir -- "-docs"}
tar -xJf %{docszip}
mv java-%{featurever}-openjdk*.docs.* ${docdir}

miscdir=%{installoutputdir -- "-misc"}
tar -xJf %{misczip}
mv java-%{featurever}-openjdk*.misc.* ${miscdir}

for suffix in %{build_loop} ; do

  if [ "x$suffix" = "x" ] ; then
      jdkzip=%{releasezip}
      staticlibzip=%{staticlibzip}
      make -C %{nssadapter_name} CFLAGS="%{build_cflags}" LDFLAGS="%{build_ldflags}"
  elif [ "x$suffix" = "x%{fastdebug_suffix_unquoted}" ] ; then
      jdkzip=%{fastdebugzip}
      staticlibzip=%{fastdebugstaticlibzip}
      make -C %{nssadapter_name} CFLAGS="%{build_cflags}" LDFLAGS="%{build_ldflags}"
  else # slowdebug
      jdkzip=%{slowdebugzip}
      staticlibzip=%{slowdebugstaticlibzip}
      # Disable _FORTIFY_SOURCE to allow for no optimization
      make -C %{nssadapter_name} CFLAGS="%{build_cflags} -O0 -Wp,-U_FORTIFY_SOURCE" LDFLAGS="%{build_ldflags}"
  fi

  installdir=%{installoutputdir -- ${suffix}}

  # TODO: should verify checksums when using packages from buildroot
  tar -xJf ${jdkzip}
  tar -xJf ${staticlibzip}
  mv java-%{featurever}-openjdk* ${installdir}

  # Install and clean libnssadapter.so
  install -m 755 %{nssadapter_name}/bin/libnssadapter.so ${installdir}/lib
  make -C %{nssadapter_name} clean

  # Fix build paths in ELF files so it looks like we built them
  portablenvr="%{name}-%{VERSION}-%{prelease}.%{portablesuffix}.%{_arch}"
  for file in $(find ${installdir} -type f) ; do
      if file ${file} | grep -q 'ELF'; then
          %{debugedit} -b %{portablebuilddir}/${portablenvr} -d $(pwd) -n ${file}
      fi
  done

  # Set tapset variables to match this build
%if %{with_systemtap}
  for file in ${miscdir}/tapset${suffix}/*.in; do
    OUTPUT_FILE=`echo $file | sed -e "s:\.stp\.in$:-%{version}-%{release}.%{_arch}.stp:g"`
    sed -e "s:@ABS_SERVER_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/lib/%{vm_variant}/libjvm.so:g" $file > ${OUTPUT_FILE}
# TODO find out which architectures other than i686 have a client vm
%ifarch %{ix86}
    sed -i -e "s:@ABS_CLIENT_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/lib/client/libjvm.so:g" ${OUTPUT_FILE}
%else
    sed -i -e "/@ABS_CLIENT_LIBJVM_SO@/d" ${OUTPUT_FILE}
%endif
    sed -i -e "s:@ABS_JAVA_HOME_DIR@:%{_jvmdir}/%{sdkdir -- $suffix}:g" $OUTPUT_FILE
    sed -i -e "s:@prefix@:%{_jvmdir}/%{sdkdir -- $suffix}/:g" $OUTPUT_FILE
  done
%endif

  # Final setup on the main image
  customisejdk ${installdir} ${suffix}

  # Print release information
  cat ${installdir}/release

# build cycles
done # end of release / debug cycle loop

%check

# We test debug first as it will give better diagnostics on a crash
for suffix in %{build_loop} ; do

export JAVA_HOME=$(pwd)/%{installoutputdir -- ${suffix}}

# Pre-test setup

# Check Shenandoah is enabled
%if %{use_shenandoah_hotspot}
$JAVA_HOME/bin/java -XX:+UnlockExperimentalVMOptions -XX:+UseShenandoahGC -version
%endif

# Only test on one architecture (the fastest) for Java only tests
%ifarch %{jdk_test_arch}

  # Check unlimited policy has been used
  $JAVA_HOME/bin/javac -d . %{SOURCE13}
  $JAVA_HOME/bin/java --add-opens java.base/javax.crypto=ALL-UNNAMED TestCryptoLevel

  # Check ECC is working
  $JAVA_HOME/bin/javac -d . %{SOURCE14}
  $JAVA_HOME/bin/java $(echo $(basename %{SOURCE14})|sed "s|\.java||")

  # Check system crypto (policy) is active and can be disabled
  # Test takes a single argument - true or false - to state whether system
  # security properties are enabled or not.
  $JAVA_HOME/bin/javac -d . %{SOURCE15}
  export PROG=$(echo $(basename %{SOURCE15})|sed "s|\.java||")
  export SEC_DEBUG="-Djava.security.debug=properties"
  $JAVA_HOME/bin/java ${SEC_DEBUG} ${PROG} %{crypto_policy_active}
  $JAVA_HOME/bin/java ${SEC_DEBUG} -Dredhat.crypto-policies=false ${PROG} false

  # Check correct vendor values have been set
  $JAVA_HOME/bin/javac -d . %{SOURCE16}
  $JAVA_HOME/bin/java $(echo $(basename %{SOURCE16})|sed "s|\.java||") "%{oj_vendor}" "%{oj_vendor_url}" "%{oj_vendor_bug_url}" "%{oj_vendor_version}"

%if ! 0%{?flatpak}
  # Check translations are available for new timezones (during flatpak builds, the
  # tzdb.dat used by this test is not where the test expects it, so this is
  # disabled for flatpak builds)
  # Disable test until we are on the latest JDK
  $JAVA_HOME/bin/javac -d . %{SOURCE18}
  $JAVA_HOME/bin/java $(echo $(basename %{SOURCE18})|sed "s|\.java||") JRE
  $JAVA_HOME/bin/java -Djava.locale.providers=CLDR $(echo $(basename %{SOURCE18})|sed "s|\.java||") CLDR
%endif

  # Check src.zip has all sources. See RHBZ#1130490
  unzip -l $JAVA_HOME/lib/src.zip | grep 'sun.misc.Unsafe'

  # Check class files include useful debugging information
  $JAVA_HOME/bin/javap -c -l java.lang.Object | grep "Compiled from"
  $JAVA_HOME/bin/javap -c -l java.lang.Object | grep LineNumberTable
  $JAVA_HOME/bin/javap -c -l java.lang.Object | grep LocalVariableTable

  # Check generated class files include useful debugging information
  $JAVA_HOME/bin/javap -c -l java.nio.ByteBuffer | grep "Compiled from"
  $JAVA_HOME/bin/javap -c -l java.nio.ByteBuffer | grep LineNumberTable
  $JAVA_HOME/bin/javap -c -l java.nio.ByteBuffer | grep LocalVariableTable

%else

  # Just run a basic java -version test on other architectures
  $JAVA_HOME/bin/java -version

%endif

# Check java launcher has no SSB mitigation
if ! nm $JAVA_HOME/bin/java | grep set_speculation ; then true ; else false; fi

# Check alt-java launcher has SSB mitigation on supported architectures
# set_speculation function exists in both cases, so check for prctl call
alt_java_binary=$RPM_BUILD_ROOT%{jrebindir -- $suffix}/%{alt_java_name}
%ifarch %{ssbd_arches}
nm ${alt_java_binary} | grep prctl
%else
if ! nm ${alt_java_binary} | grep prctl ; then true ; else false; fi
%endif

%if %{include_staticlibs}
# Check debug symbols in static libraries (smoke test)
# Temporary workaround for debuginfo failure on x86_64 with devkit build
%ifnarch x86_64
export STATIC_LIBS_HOME=${JAVA_HOME}/lib/static/linux-%{archinstall}/glibc
readelf --debug-dump $STATIC_LIBS_HOME/libnet.a | grep Inet4AddressImpl.c
readelf --debug-dump $STATIC_LIBS_HOME/libnet.a | grep Inet6AddressImpl.c
%endif
%endif

so_suffix="so"
# Check debug symbols are present and can identify code
find "$JAVA_HOME" -iname "*.$so_suffix" -print0 | while read -d $'\0' lib
do
  if [ -f "$lib" ] ; then
    echo "Testing $lib for debug symbols"
    # All these tests rely on RPM failing the build if the exit code of any set
    # of piped commands is non-zero.

    # Test for .debug_* sections in the shared object. This is the main test
    # Stripped objects will not contain these
    eu-readelf -S "$lib" | grep "] .debug_"
    test $(eu-readelf -S "$lib" | grep -E "\]\ .debug_(info|abbrev)" | wc --lines) == 2

    # Test FILE symbols. These will most likely be removed by anything that
    # manipulates symbol tables because it's generally useless. So a nice test
    # that nothing has messed with symbols
    old_IFS="$IFS"
    IFS=$'\n'
    for line in $(eu-readelf -s "$lib" | grep "00000000      0 FILE    LOCAL  DEFAULT")
    do
     # We expect to see .cpp files, except for architectures like aarch64 and
     # s390 where we expect .o and .oS files
      echo "$line" | grep -E "ABS ((.*/)?[-_a-zA-Z0-9]+\.(c|cc|cpp|cxx|o|S|oS))?$"
    done
    IFS="$old_IFS"

    # If this is the JVM, look for javaCalls.(cpp|o) in FILEs, for extra sanity checking
    if [ "`basename $lib`" = "libjvm.so" ]; then
      eu-readelf -s "$lib" | \
        grep -E "00000000      0 FILE    LOCAL  DEFAULT      ABS javaCalls.(cpp|o)$"
    fi

    # Test that there are no .gnu_debuglink sections pointing to another
    # debuginfo file. There shouldn't be any debuginfo files, so the link makes
    # no sense either
    eu-readelf -S "$lib" | grep 'gnu'
    if eu-readelf -S "$lib" | grep '] .gnu_debuglink' | grep PROGBITS; then
      echo "bad .gnu_debuglink section."
      eu-readelf -x .gnu_debuglink "$lib"
      false
    fi
  fi
done

# Make sure gdb can do a backtrace based on line numbers on libjvm.so
# javaCalls.cpp:58 should map to:
# http://hg.openjdk.java.net/jdk8u/jdk8u/hotspot/file/ff3b27e6bcc2/src/share/vm/runtime/javaCalls.cpp#l58
# Using line number 1 might cause build problems. See:
# https://bugzilla.redhat.com/show_bug.cgi?id=1539664
# https://bugzilla.redhat.com/show_bug.cgi?id=1538767
gdb -q "$JAVA_HOME/bin/java" <<EOF | tee gdb.out
handle SIGSEGV pass nostop noprint
handle SIGILL pass nostop noprint
set breakpoint pending on
break javaCalls.cpp:58
commands 1
backtrace
quit
end
run -version
EOF

%ifarch %{gdb_arches}
grep 'JavaCallWrapper::JavaCallWrapper' gdb.out
%endif

# build cycles check
done

%install
STRIP_KEEP_SYMTAB=libjvm*

for suffix in %{build_loop} ; do

jdk_image=$(pwd)/%{installoutputdir -- ${suffix}}
# Should match same definitions in build section
docdir=$(pwd)/%{installoutputdir -- "-docs"}
miscdir=$(pwd)/%{installoutputdir -- "-misc"}

# Install release notes and rebuild instructions
commondocdir=${RPM_BUILD_ROOT}%{_defaultdocdir}/%{uniquejavadocdir -- $suffix}
install -d -m 755 ${commondocdir}
mv ${jdk_image}/NEWS ${commondocdir}
# Copy portable and devkit specfiles and README.md
cp -a %{SOURCE19} %{SOURCE20} %{SOURCE22} ${commondocdir}
# Copy devkit patches
cp -a  %{SOURCE23} %{SOURCE24} %{SOURCE25} %{SOURCE26} \
       %{SOURCE27} %{SOURCE28} %{SOURCE29} %{SOURCE30} ${commondocdir}

# Install the jdk
mkdir -p $RPM_BUILD_ROOT%{_jvmdir}
cp -a ${jdk_image} $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}
# Install %{alt_java_name} binary
install -D -p -m 755 ${miscdir}/%{alt_java_name} $RPM_BUILD_ROOT%{jrebindir -- $suffix}

%if %{with_systemtap}
  # Install systemtap support files
  install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset
  cp -a ${miscdir}/tapset$suffix/*.stp $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
  pushd  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
   tapsetFiles=`ls *.stp`
  popd
  install -d -m 755 $RPM_BUILD_ROOT%{tapsetdir}
  for name in $tapsetFiles ; do
    targetName=`echo $name | sed "s/.stp/$suffix.stp/"`
    ln -sf %{_jvmdir}/%{sdkdir -- $suffix}/tapset/$name $RPM_BUILD_ROOT%{tapsetdir}/$targetName
  done
%endif

  install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{sdkdir -- ${suffix}}
  mv $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/libnssadapter.so $RPM_BUILD_ROOT%{_libdir}/%{sdkdir -- ${suffix}}

  # Remove empty cacerts database
  rm -f $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/security/cacerts
  # Install cacerts symlink needed by some apps which hard-code the path
  pushd $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/security
      ln -sf /etc/pki/java/cacerts .
  popd

%if %{pandoc_available}
  # Install man pages
  install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
  pushd ${jdk_image}
  for manpage in man/man1/*
  do
    # Convert man pages to UTF8 encoding
    iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
    mv -f $manpage.tmp $manpage
    install -m 644 -p $manpage $RPM_BUILD_ROOT%{_mandir}/man1/$(basename \
      $manpage .1)-%{uniquesuffix -- $suffix}.1
  done
  # Remove man pages from jdk image
  rm -rf $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/man
  popd
%endif

if ! echo $suffix | grep -q "debug" ; then
    # Install Javadoc documentation
    install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}
    cp -a ${docdir}/docs $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}
    built_doc_archive=jdk-%{filever}%{ea_designator_zip}+%{buildver}%{lts_designator_zip}-docs.zip
    cp -a ${docdir}/${built_doc_archive} \
        $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}.zip || ls -l ${top_dir_abs_main_build_path}/bundles/
    touch $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}.zip
fi

# Install icons and menu entries
for s in 16 24 32 48 ; do
  install -D -p -m 644 \
    ${miscdir}/java-icon${s}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps/java-%{javaver}-%{origin}.png
done

# Install desktop files
# TODO: provide desktop files via portable
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
for e in jconsole$suffix ; do
    desktop-file-install --vendor=%{uniquesuffix -- $suffix} --mode=644 \
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications $e.desktop
done

# Install /etc/.java/.systemPrefs/ directory
# See https://bugzilla.redhat.com/show_bug.cgi?id=741821
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/.java/.systemPrefs

# moving config files to /etc
mkdir -p $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}
mkdir -p $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}/lib
mv $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/conf/  $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}
mv $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/lib/security  $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}/lib
pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}
  ln -s %{etcjavadir -- $suffix}/conf  ./conf
popd
pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/lib
  ln -s %{etcjavadir -- $suffix}/lib/security  ./security
popd
# end moving files to /etc

# stabilize permissions
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -name "*.so" -exec chmod 755 {} \; ;
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -type d -exec chmod 755 {} \; ;
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/legal -type f -exec chmod 644 {} \; ;

# end, dual install
done

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/
# recommends an explicit "exit 0" at the end of each scriptlet.  Keep
# them in this section instead of in the parameterized macro
# definitions, so that multiple macros can be called without worrying
# about which one ends with "exit 0".
%if %{include_normal_build}
%post
%{post_script %{nil}}
exit 0

# Allow upgrades from packages that have /usr/lib/jvm/java-21-openjdk
# as an alternatives symlink, without running into the known RPM
# limitation when changing to a directory a symlink to a directory.
# See also javadoc and javadoc-zip subpackages for
# /usr/share/javadoc/java-21-openjdk, which was a symlink before.
# /etc/java/java-21-openjdk is OK because it was always a directory.
# Reference:
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Directory_Replacement/
%define lua_delete_old_link() %{expand:
path = "%{1}"
st = posix.stat(path)
if st and st.type == "link" then
  os.remove(path)
end
}

%pretrans headless -p <lua>
%{lua_delete_old_link -- %{_jvmdir}/%{sdkdir -- %{?1}}}

%post headless
%{post_headless %{nil}}
exit 0

%postun
%{postun_script %{nil}}
exit 0

%preun headless
%{preun_headless %{nil}}
exit 0

%posttrans
%{posttrans_script %{nil}}
exit 0

%post devel
%{post_devel %{nil}}
exit 0

%preun devel
%{preun_devel %{nil}}
exit 0

%postun devel
%{postun_devel %{nil}}
exit 0

%posttrans devel
%{posttrans_devel %{nil}}
exit 0

%pretrans javadoc -p <lua>
%{lua_delete_old_link -- %{_jvmdir}/%{sdkdir -- %{?1}}}
%{lua_delete_old_link -- %{_javadocdir}/%{uniquejavadocdir -- %{?1}}}

%post javadoc
%{alternatives_javadoc_install %{nil}}
exit 0

%preun javadoc
%{preun_javadoc %{nil}}
exit 0

%pretrans javadoc-zip -p <lua>
%{lua_delete_old_link -- %{_jvmdir}/%{sdkdir -- %{?1}}}
%{lua_delete_old_link -- %{_javadocdir}/%{uniquejavadocdir -- %{?1}}}

%post javadoc-zip
%{alternatives_javadoczip_install %{nil}}
exit 0

%preun javadoc-zip
%{preun_javadoc_zip %{nil}}
exit 0
%endif

%if %{include_debug_build}
%post slowdebug
%{post_script -- %{debug_suffix_unquoted}}
exit 0

%post headless-slowdebug
%{post_headless -- %{debug_suffix_unquoted}}
exit 0

%postun slowdebug
%{postun_script -- %{debug_suffix_unquoted}}
exit 0

%preun headless-slowdebug
%{preun_headless -- %{debug_suffix_unquoted}}
exit 0

%posttrans slowdebug
%{posttrans_script -- %{debug_suffix_unquoted}}
exit 0

%post devel-slowdebug
%{post_devel -- %{debug_suffix_unquoted}}
exit 0

%preun devel-slowdebug
%{preun_devel -- %{debug_suffix_unquoted}}
exit 0

%postun devel-slowdebug
%{postun_devel -- %{debug_suffix_unquoted}}
exit 0

%posttrans devel-slowdebug
%{posttrans_devel -- %{debug_suffix_unquoted}}
exit 0
%endif

%if %{include_fastdebug_build}
%post fastdebug
%{post_script -- %{fastdebug_suffix_unquoted}}
exit 0

%post headless-fastdebug
%{post_headless -- %{fastdebug_suffix_unquoted}}
exit 0

%postun fastdebug
%{postun_script -- %{fastdebug_suffix_unquoted}}
exit 0

%preun headless-fastdebug
%{preun_headless -- %{fastdebug_suffix_unquoted}}
exit 0

%posttrans fastdebug
%{posttrans_script -- %{fastdebug_suffix_unquoted}}
exit 0

%post devel-fastdebug
%{post_devel -- %{fastdebug_suffix_unquoted}}
exit 0

%preun devel-fastdebug
%{preun_devel -- %{fastdebug_suffix_unquoted}}
exit 0

%postun devel-fastdebug
%{postun_devel -- %{fastdebug_suffix_unquoted}}
exit 0

%posttrans devel-fastdebug
%{posttrans_devel -- %{fastdebug_suffix_unquoted}}
exit 0
%endif

%if %{include_normal_build}
%files
# main package builds always
%{files_jre %{nil}}
%else
%files
# placeholder
%endif

%if %{include_normal_build}
%files crypto-adapter
%{files_crypto_adapter %{nil}}

%files headless
%{files_jre_headless %{nil}}

%files devel
%{files_devel %{nil}}

%if %{include_staticlibs}
%files static-libs
%{files_static_libs %{nil}}
%endif

%files jmods
%{files_jmods %{nil}}

%files demo
%{files_demo %{nil}}

%files src
%{files_src %{nil}}

%files javadoc
%{files_javadoc %{nil}}

# This puts a huge documentation file in /usr/share
# It is now architecture-dependent, as eg. AOT and Graal are now x86_64 only
# same for debug variant
%files javadoc-zip
%{files_javadoc_zip %{nil}}
%endif

%if %{include_debug_build}
%files crypto-adapter-slowdebug
%{files_crypto_adapter -- %{debug_suffix_unquoted}}

%files slowdebug
%{files_jre -- %{debug_suffix_unquoted}}

%files headless-slowdebug
%{files_jre_headless -- %{debug_suffix_unquoted}}

%files devel-slowdebug
%{files_devel -- %{debug_suffix_unquoted}}

%if %{include_staticlibs}
%files static-libs-slowdebug
%{files_static_libs -- %{debug_suffix_unquoted}}
%endif

%files jmods-slowdebug
%{files_jmods -- %{debug_suffix_unquoted}}

%files demo-slowdebug
%{files_demo -- %{debug_suffix_unquoted}}

%files src-slowdebug
%{files_src -- %{debug_suffix_unquoted}}
%endif

%if %{include_fastdebug_build}
%files crypto-adapter-fastdebug
%{files_crypto_adapter --  %{fastdebug_suffix_unquoted}}

%files fastdebug
%{files_jre -- %{fastdebug_suffix_unquoted}}

%files headless-fastdebug
%{files_jre_headless -- %{fastdebug_suffix_unquoted}}

%files devel-fastdebug
%{files_devel -- %{fastdebug_suffix_unquoted}}

%if %{include_staticlibs}
%files static-libs-fastdebug
%{files_static_libs -- %{fastdebug_suffix_unquoted}}
%endif

%files jmods-fastdebug
%{files_jmods -- %{fastdebug_suffix_unquoted}}

%files demo-fastdebug
%{files_demo -- %{fastdebug_suffix_unquoted}}

%files src-fastdebug
%{files_src -- %{fastdebug_suffix_unquoted}}

%endif

%changelog
* Sat May 16 2026 Jacco Ligthart <jacco@redsleeve.org> - 25.0.3.0.9-1.redsleeve
- add %{arm} to ExclusiveArch

* Sat Apr 25 2026 Release Engineering <releng@rockylinux.org> - 1:25.0.3.0.9-1
- Build for Rocky Linux %{rocky} using our own portable

* Sat Apr 18 2026 Andrew Hughes <gnu.andrew@redhat.com> - 1:25.0.3.0.9-1
- Update to jdk-25.0.3+9 (GA)
- Update release notes to 25.0.3+9
- Update FIPS patch to 57722aab802 version synced with 25.0.3+8
- Drop local libpng patches now JDK-8372534, JDK-8375063 & JDK-8377526 are included upstream
- Drop local HarfBuzz patch now JDK-8375057 is included upstream
- Bump freetype version to 2.14.2 following JDK-8373290 & JDK-8379158
- Bump giflib version to 6.1.2 following JDK-8379256 & JDK-8380078
- Bump libpng version to 1.6.57 following JDK-8380959 & JDK-8382047
- Bump zlib version to 1.3.2 following JDK-8378631
- Add JDK-8375294 EOPNOTSUPP patch ahead of 25.0.4
- Sync the copy of the portable specfile with the latest update
- ** This tarball is embargoed until 2026-04-21 @ 1pm PT. **
- Resolves: RHEL-169619
- Resolves: RHEL-157142
- Resolves: RHEL-157154
- Resolves: RHEL-161306
- Resolves: RHEL-161455
- Resolves: RHEL-169615

* Wed Mar 11 2026 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:25.0.2.0.10-3
- Disable abidiff inspection in rpminspect.yaml to avoid an out-of-memory error on the CentOS test farm
- See: https://docs.testing-farm.io/Testing%20Farm/0.1/errors.html#TFE-1
- Resolves: RHEL-149786

* Tue Mar 03 2026 Andrew Hughes <gnu.andrew@redhat.com> - 1:25.0.2.0.10-3
- Update FIPS patch to e55ada9353e to include the fix for the too restrictive provider lockdown
- Fix FIPS issue list to represent the new 25u version
- Add JDK-8375063 libpng 1.6.54 ahead of 25.0.3
- Add JDK-8375057 harfbuzz 12.3.2 ahead of 25.0.3
- Add JDK-8377526 libpng 1.6.55 ahead of 25.0.3
- Bump libpng version to 1.6.55 following JDK-8375063 & JDK-8377526
- Bump harfbuzz version to 12.3.2 following JDK-8375057
- Bump nssadapter version to bring in shared PKCS11 session fix
- Drop LDFLAGS nssadapter patch which is now upstream in 0.1.1
- Add tagging scripts with signature checks and gating handling
- Update tagged versions to include 9.8.0-z, 9.9.0, 10.2-z & 10.3.
- Add gating scripts to simplify obtaining results and waiving issues
- Sync the copy of the portable specfile with the latest update
- Resolves: RHEL-155001
- Resolves: RHEL-147354
- Resolves: RHEL-148410
- Resolves: RHEL-148997
- Resolves: RHEL-155047
- Resolves: RHEL-155330
- Resolves: RHEL-156036
- Resolves: RHEL-156040

* Wed Jan 28 2026 Andrew Hughes <gnu.andrew@redhat.com> - 1:25.0.2.0.10-2
- Bump rpmrelease for CentOS build
- Related: RHEL-139577
- Related: RHEL-142856
- Related: RHEL-142808

* Wed Jan 21 2026 Jiri Vanek <jvanek@redhat.com> - 1:25.0.2.0.10-1
- Execute create-redhat-properties-files.bash with '-e' to exit on failure
- Related: RHEL-142856

* Mon Jan 12 2026 Andrew Hughes <gnu.andrew@redhat.com> - 1:25.0.2.0.10-1
- Update to jdk-25.0.2+10 (GA)
- Update release notes to 25.0.2+10
- Add JDK-8372534 libpng 1.6.51 ahead of 25.0.3
- Bump libpng version to 1.6.51 following JDK-8372534
- Bump ID of NSS adapter patch so we can stay in sync with portable on the libpng patch
- Test for java.security's existence in create-redhat-properties-files.bash
- Handle 'upgrade' as an alternative to 'update' in openjdk_news.sh
- Sync the copy of the portable specfile with the latest update
- ** This tarball is embargoed until 2026-01-20 @ 1pm PT. **
- Resolves: RHEL-139577
- Resolves: RHEL-143373
- Resolves: RHEL-143368
- Resolves: RHEL-142856
- Resolves: RHEL-142808

* Mon Dec 08 2025 Andrew Hughes <gnu.andrew@redhat.com> - 1:25.0.1.0.8-2
- Incorporate new FIPS patch for 25u
- Drop static libjvm.a following adjusted build target for portable build
- Remove redundant (and now outdated) build targets, jdkimage and static_libs_image
- Remove OpenJDK compiler flag filters and use build_{c,ld}flags directly
- Sync the copy of the portable specfile with the latest update
- Resolves: RHEL-133743
- Resolves: RHEL-133737
- Related: RHEL-131898

* Mon Dec 08 2025 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:25.0.1.0.8-2
- Add java-25-openjdk-crypto-adapter subpackage
- Update library setting in create-redhat-properties-files.bash
- Remove /usr/lib/jvm/java-25-openjdk/conf/security/redhat/fips.properties
- Resolves: RHEL-132520
- Resolves: RHEL-132523

* Fri Nov 28 2025 Andrew Hughes <gnu.andrew@redhat.com> - 1:25.0.1.0.8-1
- Pass ourflags and ourldflags into the nssadapter build using CFLAGS & LDFLAGS
- Patch the nssadapter build to recognise LDFLAGS
- Resolves: RHEL-131898

* Mon Nov 24 2025 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:25.0.1.0.8-1
- Add libnssadapter.so
- Add FIPS crypto-policies configuration
- Remove obsolete security.useSystemPropertiesFile setup
- Update TestSecurityProperties.java test and calling convention
- Resolves: RHEL-128414
- Resolves: RHEL-128412

* Wed Nov 12 2025 Andrew Hughes <gnu.andrew@redhat.com> - 1:25.0.1.0.8-1
- Create java-25-openjdk package based on java-21-openjdk
- Update to jdk-25.0.1+8 (GA)
- Update release notes with features of JDK 22, 23, 24 & 25
- Mention finalisation JEP for features finalised in JDK 22, 23 & 24
- Update release notes to 25.0.1+8
- Update README file for java-25-openjdk
- Make sure this is not the default/system JDK providing 'java', 'jre', 'java-devel' ,etc.
- Remove 21u FIPS patch and disable use until we are ready for the 25 version
- Adjust CLDR expectations in TestTranslations.java after JDK-8317979 started using tzdata values
- Adjust TestTranslations.java to expect the same short name throughout for fr_FR and de_DE (bug?)
- Remove references to libsystemconf.so and nss.fips.cfg from the 21u FIPS patch
- Include static libraries in the vm_variant subdirectory after JDK-8307858 (libjvm.a)
- Flip equals test in TestSecurityProperties.java to handle null values from Security.getProperty
- Introduce crypto_policy_active to designate whether we should expect policy adherence in testing
- Flip crypto_policy_active to false while the crypto policy & FIPS patch is not present
- Handle new libsimdsort.so introduced on x86_64 only by JDK-8309130
- Remove lible.so handling following its removal in JDK-8327476: "Upgrade JLine to 3.26.1"
- Install jaxp-strict.properties.template added by JDK-8330542: "Template for Creating Strict JAXP Configuration File"
- alt-java man page installation is now handled by the OpenJDK build
- Adjust TestTranslations.java with updated German translations from CLDR 46 (JDK-8333582) (Mountain->Mountains)
- Run javap with the disassembled code (-c) option now required for -l by JDK-8345145
- Remove default.policy and java.policy following JDK-8338411: "Permanently Disable the Security Manager"
- Make man page handling dependent on pandoc being available during the portable build
- Handle new CDS archive variants (*_coh*) added by Compact Object Headers (JDK-8305895)
- Add missing man page alternatives for jdeprscan, jfr, jhsdb, jimage, jlink & jmod and fix alphabetical ordering
- Support jnativescan added by JDK-8317611: "Add a tool like jdeprscan to find usage of restricted methods"
- Add recent native libraries to _privatelibs (libjsvml.so, libsimdsort.so, libsyslookup.so)
- Support libsleef on AArch64 & RISC-V added by JDK-8329816, JDK-8320500 (RISC-V) & JDK-8312425 (AArch64)
- Remove superfluous backslashes that cause two alternative commands to be combined
- Sync the copy of the portable specfile with the latest update
- Resolves: RHEL-126022
