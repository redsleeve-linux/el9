
%{?scl_package:%global scl gcc-toolset-14}
%global scl_prefix gcc-toolset-14-
BuildRequires: scl-utils-build

%global __python /usr/bin/python3
%{?scl:%scl_package binutils}

Summary: A GNU collection of binary utilities
Name: %{?scl_prefix}binutils
Version: 2.41
Release: 4%{?dist}.1
License: GPL-3.0-or-later AND (GPL-3.0-or-later WITH Bison-exception-2.2) AND (LGPL-2.0-or-later WITH GCC-exception-2.0) AND BSD-3-Clause AND GFDL-1.3-or-later AND GPL-2.0-or-later AND LGPL-2.1-or-later AND LGPL-2.0-or-later
URL: https://sourceware.org/binutils

#---Start of Configure Options-----------------------------------------------

# The binutils can be built with the following parameters to change
#  the default behaviour:

# --with    bootstrap    Build with minimal dependencies.
# --with    clang        Force building with CLANG instead of GCC.
# --with    crossbuilds  Build cross targeted versions of the binutils as well as natives.
# --with    debug        Build without optimizations and without splitting the debuginfo into a separate file.
# --without debuginfod   Disable support for debuginfod.
# --without docs         Skip building documentation.  Default is with docs, except when building a cross binutils.
# --without gold         Disable building of the GOLD linker.
# --without gprofng      Do not build the GprofNG profiler.
# --without systemzlib   Use the binutils version of zlib.
# --without testsuite    Do not run the testsuite.  Default is to run it.

# Other configuration options can be set by modifying the following defines.

# Create shared libraries.
%define enable_shared 1

# Create deterministic archives (ie ones without timestamps).
# Default is off because of BZ 1195883.
%define enable_deterministic_archives 0

# Generate a warning when linking creates an executable stack
%define warn_for_executable_stacks 1

# Generate a warning when linking creates a segment with read, write and execute permissions
%define warn_for_rwx_segments 1

# Turn the above warnings into errors.  Only effective if the warnings are enabled.
%define error_for_executable_stacks 0
%define error_for_rwx_segments 0

# Enable support for GCC LTO compilation.
# Disable if it is necessary to work around bugs in LTO.
%define enable_lto 1

# Enable support for generating new dtags in the linker
# Disable if it is necessary to use RPATH instead.
# Currently enabled for Fedora, disabled for RHEL.
%define enable_new_dtags 1

# Enable the compression of debug sections as default behaviour of the
# assembler and linker.  This option is disabled for now.  The assembler and
# linker have command line options to override the default behaviour.
%define default_compress_debug 0

# Default to read-only-relocations (relro) in shared binaries.
# This is enabled as a security feature.
%define default_relro 1

# Enable the default generation of GNU Build notes by the assembler.
# This option is disabled as it has turned out to be problematic for the i686
# architecture, although the exact reason has not been determined.  (See
# BZ 1572485).  It also breaks building EFI binaries on AArch64, as these
# cannot have relocations against absolute symbols.
%define default_generate_notes 0

# Enable thread support in the GOLD linker (if it is being built).  This is
# particularly important if plugins to the linker intend to use threads
# themselves.  See BZ 1636479 for more details.  This option is made
# configurable in case there is ever a need to disable thread support.
%define enable_threading 1

# Enable the use of separate code and data segments for all architectures,
# not just x86/x86_64.
%define enable_separate_code 1

#----End of Configure Options------------------------------------------------

# Note - in the future the gold linker may become deprecated.
%ifnarch riscv64
%bcond_without gold
%else
# RISC-V does not have ld.gold thus disable by default.
%bcond_with gold
%endif

# Default: Not bootstrapping.
%bcond_with bootstrap
# Default: Not debug
%bcond_with debug
# Default: Always build documentation.
%bcond_without docs
# Default: Always run the testsuite.
%bcond_without testsuite
# Default: support debuginfod.
%bcond_without debuginfod
# Default: build binutils-gprofng package.
%bcond_without gprofng
# Default: Use the system supplied version of the zlib compression library.
%bcond_without systemzlib

# Allow the user to override the compiler used to build the binutils.
# The default build compiler is gcc if %%toolchain is not clang.
%if "%toolchain" == "clang"
%bcond_without clang
%else
%bcond_with clang
%endif

%if %{with clang}
%global toolchain clang
%else
%global toolchain gcc
%endif

# Do not create cross targeted versions of the binutils.
%undefine with_crossbuilds

%if %{with bootstrap}
%undefine with_docs
%undefine with_testsuite
%undefine with_gprofng
%endif

%if %{with debug}
%undefine with_testsuite
%define enable_shared 0
%endif

# GprofNG currenly onlly supports the x86 and AArch64 architectures.
%ifnarch x86_64 aarch64
%undefine with_gprofng
%endif

# The opcodes library needs a few functions defined in the bfd
# library, but these symbols are not defined in the stub bfd .so
# that is available at link time.  (They are present in the real
# .so that is used at run time).
%undefine _strict_symbol_defs_build

# BZ 1924068.  Since applications that use the BFD library are
# required to link against the static version, ensure that it retains
# its debug informnation.
%undefine __brp_strip_static_archive

#----------------------------------------------------------------------------

# Bootstrapping: Set this to 1 to build annobin with the system gcc.
# Then once GTS-gcc is built and in the buildroot, reset this variable
# to 0, bump the NVR and rebuild GTS-binutils.
%define bootstrapping 0

#----------------------------------------------------------------------------

# Note - the Linux Kernel binutils releases are too unstable and contain
# too many controversial patches so we stick with the official FSF version
# instead.

Source: https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
Source2: binutils-2.19.50.0.1-output-format.sed

#----------------------------------------------------------------------------

# Purpose:  Use /lib64 and /usr/lib64 instead of /lib and /usr/lib in the
#           default library search path of 64-bit targets.
# Lifetime: Permanent, but it should not be.  This is a bug in the libtool
#           sources used in both binutils and gcc, (specifically the
#           libtool.m4 file).  These are based on a version released in 2009
#           (2.2.6?) rather than the latest version.  (Definitely fixed in
#           libtool version 2.4.6).
Patch01: binutils-libtool-lib64.patch

# Purpose:  Appends a RHEL or Fedora release string to the generic binutils
#           version string.
# Lifetime: Permanent.  This is a RHEL/Fedora specific patch.
Patch02: binutils-version.patch

# Purpose:  Exports the demangle.h header file (associated with the libiberty
#           sources) with the binutils-devel rpm.
# Lifetime: Permanent.  This is a RHEL/Fedora specific patch.
Patch03: binutils-export-demangle.h.patch

# Purpose:  Disables the check in the BFD library's bfd.h header file that
#           config.h has been included before the bfd.h header.  See BZ
#           #845084 for more details.
# Lifetime: Permanent - but it should not be.  The bfd.h header defines
#           various types that are dependent upon configuration options, so
#           the order of inclusion is important.
# FIXME:    It would be better if the packages using the bfd.h header were
#           fixed so that they do include the header files in the correct
#           order.
Patch04: binutils-no-config-h-check.patch

# Purpose:  Disable an x86/x86_64 optimization that moves functions from the
#           PLT into the GOTPLT for faster access.  This optimization is
#           problematic for tools that want to intercept PLT entries, such
#           as ltrace and LD_AUDIT.  See BZs 1452111 and 1333481.
# Lifetime: Permanent.  But it should not be.
# FIXME:    Replace with a configure time option.
Patch05: binutils-revert-PLT-elision.patch

# Purpose:  Do not create PLT entries for AARCH64 IFUNC symbols referenced in
#           debug sections.
# Lifetime: Permanent.
# FIXME:    Find related bug.  Decide on permanency.
Patch06: binutils-2.27-aarch64-ifunc.patch

# Purpose:  Stop the binutils from statically linking with libstdc++.
# Lifetime: Permanent.
Patch07: binutils-do-not-link-with-static-libstdc++.patch

# Purpose:  Allow OS specific sections in section groups.
# Lifetime: Fixed in 2.42 (maybe)
Patch08: binutils-special-sections-in-groups.patch

# Purpose:  Stop gold from aborting when input sections with the same name
#            have different flags.
# Lifetime: Fixed in 2.42 (maybe)
Patch09: binutils-gold-mismatched-section-flags.patch

# Purpose:  Change the gold configuration script to only warn about
#            unsupported targets.  This allows the binutils to be built with
#            BPF support enabled.
# Lifetime: Permanent.
Patch10: binutils-gold-warn-unsupported.patch

# Purpose:  Enable the creation of .note.gnu.property sections by the GOLD
#            linker for x86 binaries.
# Lifetime: Permanent.
Patch11: binutils-gold-i386-gnu-property-notes.patch

# Purpose:  Allow the binutils to be configured with any (recent) version of
#            autoconf.
# Lifetime: Fixed in 2.42 (maybe ?)
Patch12: binutils-autoconf-version.patch

# Purpose:  Stop libtool from inserting useless runpaths into binaries.
# Lifetime: Who knows.
Patch13: binutils-libtool-no-rpath.patch

%if %{enable_new_dtags}
# Purpose:  Change ld man page so that it says that --enable-new-dtags is the default.
# Lifetime: Permanent
Patch14: binutils-update-linker-manual.patch
%endif

# Purpose:  Stop an abort when using dwp to process a file with no dwo links.
# Lifetime: Fixed in 2.42 (maybe)
Patch15: binutils-gold-empty-dwp.patch

# Purpose:  Fix binutils testsuite failures.
# Lifetime: Permanent, but varies with each rebase.
Patch16: binutils-testsuite-fixes.patch

# Purpose:  Fix binutils testsuite failures for the RISCV-64 target.
# Lifetime: Permanent, but varies with each rebase.
Patch17: binutils-riscv-testsuite-fixes.patch

# Purpose:  Fix the GOLD linker's handling of 32-bit PowerPC binaries.
# Lifetime: Fixed in 2.42
Patch18: binutils-gold-powerpc.patch

# Purpose:  Fix a potential NULL pointer dereference when parsing corrupt
#            ELF symbol version information.
# Lifetime: Fixed in 2.42
Patch19: binutils-handle-corrupt-version-info.patch

# Purpose:  Add options to turn the bfd linker's warnings about executable
#            stacks and rwx segments into errors.
# Lifetime: Fixed in 2.42
Patch20: binutils-execstack-error.patch

# Purpose:  Accept and ignore R_BPF_64_NODYLD32 relocations.
# Lifetime: Fixed in 2.42
Patch21: binutils-BPF-reloc-4.patch

# Purpose:  Allow for x86_64 build environments that use a base ISA of x86-64-v3.
# Lifetime: Fixed in 2.42
Patch22: binutils-x86-64-v3.patch

# Purpose:  Fix mergeing strings in really big programs.
# Lifetime: Fixed in 2.42
Patch23: binutils-big-merge.patch

# Purpose:  Fix linker generated call veneers for large AArch64 programs with BTI enabled.
# Lifetime: Fixed in 2.42
Patch24: binutils-aarch64-big-bti-programs.patch

# Purpose:  Make the GOLD linker ignore the "-z pack-relative-relocs" command line option.
# Lifetime: Fixed in 2.42 (maybe)
Patch25: binutils-gold-pack-relative-relocs.patch

# Purpose:  Add support for Intel's AVX10.1 architecture extension to gas.
# Lifetime: Fixed in 2.42
Patch26: i686-AVX10.1-part-1.patch
Patch27: i686-AVX10.1-part-2.patch
Patch28: i686-AVX10.1-part-3.patch
Patch29: i686-AVX10.1-part-4.patch
Patch30: i686-AVX10.1-part-5.patch
Patch31: i686-AVX10.1-part-6.patch

# Purpose: Fix: PR31179, The SET/ADD/SUB fix breaks ABI compatibility with 2.41 objects
# Lifetime: Fixed in 2.42
Patch32: binutils-riscv-SUB_ULEB128.patch

# Purpose:  Let the gold lihnker ignore --error-execstack and --error-rwx-segments.
# Lifetime: Fixed in 2.42 (maybe)
Patch33: binutils-gold-ignore-execstack-error.patch

# Purpose:  Fix the allocation of space for DT_RELR relocations on PPC64.
# Lifetime: Fixed in 2.42 (maybe)
Patch34: binutils-ppc-dt_relr-relocs.patch

# Purpose:  Add support for mangling used by gcc v14.
# Lifetime: Fixed in 2.42
Patch35: binutils-demangler-updates.patch

# Purpose:  Add support for Intel's APX extensions (part 1)
# Lifetime: Fixed in 2.42
Patch36: binutils-Intel-APX-part-1.patch

# Purpose:  Add support for IBM's Power11 architecture extensions
# Lifetime: Fixed in 2.43
Patch37: binutils-power-11.patch

# Purpose:  Fix support for Intel's APX extensions (part 1)
# Lifetime: Fixed in 2.43
Patch38: binutils-Intel-APX-part-1-fixes.patch

# Purpose:  Import top-level multlib.am file.
# Lifetime: Fixed in 2.42
Patch39: binutils-multilib.am.patch

# Purpose:  Fix APX support for R_X86_64_CODE_6_GOTTPOFF
# Lifetime: Fixed in 2.42
Patch40: binutils-Intel-APX-CODE_6_GOTTPOFF.patch

Patch41: binutils-LTO-plugin-common-symbols.patch

# Purpose:  Workaround for an unresolved bug in ppc gcc
#           which generates bad code in the linker.  cf RHEL-49348
# Lifetime: TEMPORARY
Patch98: binutils-PPC64-LD-ASSERT.patch

# Purpose:  Suppress the x86 linker's p_align-1 tests due to kernel bug on CentOS-10
# Lifetime: TEMPORARY
Patch99: binutils-suppress-ld-align-tests.patch

#----------------------------------------------------------------------------

Provides: bundled(libiberty)

%if %{with debug}
# Define this if you want to skip the strip step and preserve debug info.
# Useful for testing.
%define __debug_install_post : > %{_builddir}/%{?buildsubdir}/debugfiles.list
%define debug_package %{nil}
%endif

# Perl, sed and touch are all used in the %%prep section of this spec file.
BuildRequires: autoconf, automake, perl, sed, coreutils, make

%if %{with clang}
BuildRequires: clang compiler-rt
%else

%if %{bootstrapping}
# Note - during GTS bootstrap these have to use the system compiler.

# Note - during GTS bootstrap it may be necessary to build the binutils without
# annobin annotations.
# %%undefine _annotated_build

%define gcc_package gcc
%define gxx_package gcc-c++

%define gcc_for_binutils /usr/bin/gcc
%define gxx_for_binutils /usr/bin/g++

%else

# Use the GTS version of gcc to build the binutils so that the built static libraries
# (libfd.a, libopcodes.a libiberty.a libsframe.a) use the same LTO version as the one
# that will be used by consumers of GTS binutils.

%define gcc_package %{?scl_prefix}gcc
%define gxx_package %{?scl_prefix}gcc-c++

BuildRequires: %{?scl_prefix}annobin-plugin-gcc

%define gcc_for_binutils %{_scl_root}/usr/bin/gcc
%define gxx_for_binutils %{_scl_root}/usr/bin/g++

%endif

BuildRequires: %{gcc_package}
BuildRequires: %{gxx_package}

%endif

#----------------------------------------------------------------------------

%if %{with gold}
# Gold needs bison in order to build gold/yyscript.c.  The GOLD testsuite needs a static libc++
BuildRequires: bison, m4, libstdc++-static

%if ! %{with clang}

%if %{bootstrapping}
BuildRequires: gcc-c++
%else
BuildRequires: %{?scl_prefix}gcc-c++
%endif

%endif
%endif

#----------------------------------------------------------------------------

%if %{without bootstrap}

BuildRequires: gettext, flex, jansson-devel

%if %{with systemzlib}
BuildRequires: zlib-devel
%endif

%endif

#----------------------------------------------------------------------------

%if %{with docs}

BuildRequires: texinfo >= 4.0
# BZ 920545: We need pod2man in order to build the manual pages.
BuildRequires: /usr/bin/pod2man

%else

BuildRequires: findutils

%endif

#----------------------------------------------------------------------------

%if %{with testsuite}

# Required for: ld-bootstrap/bootstrap.exp bootstrap with --static
# It should not be required for: ld-elf/elf.exp static {preinit,init,fini} array
# relro_test.sh uses dc which is part of the bc rpm, hence its inclusion here.
# sharutils is needed so that we can uuencode the testsuite results.
BuildRequires: dejagnu, glibc-static, sharutils, bc, libstdc++

%if %{with systemzlib}
BuildRequires: zlib-devel
%endif

%endif

#----------------------------------------------------------------------------

%if %{with debuginfod}
BuildRequires: elfutils-debuginfod-client-devel
%endif

#----------------------------------------------------------------------------

%{?scl:Requires:%scl_runtime}

%if %{bootstrapping}
%define alternatives_cmd     %{_sbindir}/alternatives
%define alternatives_cmdline %{alternatives_cmd}
%else
%define alternatives_cmd     %{!?scl:%{_sbindir}}%{?scl:%{_root_sbindir}}/alternatives
%define alternatives_cmdline %{alternatives_cmd}%{?scl: --altdir %{_sysconfdir}/alternatives --admindir %{_scl_root}/var/lib/alternatives}
%endif

Requires(post):  %{alternatives_cmd}
Requires(preun): %{alternatives_cmd}

# We also need rm.
Requires(post): coreutils

# On ARM EABI systems, we do want -gnueabi to be part of the
# target triple.
%ifnarch %{arm}
%define _gnu %{nil}
%endif

#----------------------------------------------------------------------------

%description
Binutils is a collection of binary utilities, including ar (for
creating, modifying and extracting from archives), as (a family of GNU
assemblers), gprof (for displaying call graph profile data), ld (the
GNU linker), nm (for listing symbols from object files), objcopy (for
copying and translating object files), objdump (for displaying
information from object files), ranlib (for generating an index for
the contents of an archive), readelf (for displaying detailed
information about binary files), size (for listing the section sizes
of an object or archive file), strings (for listing printable strings
from files), strip (for discarding symbols), and addr2line (for
converting addresses to file and line).

#----------------------------------------------------------------------------

%package devel
Summary: BFD and opcodes static and dynamic libraries and header files
Provides: %{?scl_prefix}binutils-static = %{version}-%{release}
%if %{with systemzlib}
Requires: zlib-devel
%endif
Requires: %{?scl_prefix}binutils = %{version}-%{release}
# BZ 1215242: We need touch...
Requires: coreutils

%description devel
This package contains BFD and opcodes static and dynamic libraries.

The dynamic libraries are in this package, rather than a separate
base package because they are actually linker scripts that force
the use of the static libraries.  This is because the API of the
BFD library is too unstable to be used dynamically.

The static libraries are here because they are now needed by the
dynamic libraries.

Developers starting new projects are strongly encouraged to consider
using libelf instead of BFD.

# BZ 1924068.  Since applications that use the BFD library are
# required to link against the static version, ensure that it retains
# its debug informnation.
# FIXME: Yes - this is being done twice.  I have no idea why this
# second invocation is necessary but if both are not present the
# static archives will be stripped.
%undefine __brp_strip_static_archive

#----------------------------------------------------------------------------

%if %{with gold}

%package gold
Summary: The GOLD linker, a faster alternative to the BFD linker
Provides: %{?scl_prefix}binutils-gold = %{version}-%{release}
Requires: %{?scl_prefix}binutils >= %{version}

%description gold
This package provides the GOLD linker, which can be used as an alternative to
the default binutils linker (ld.bfd).  The GOLD is generally faster than the
BFD linker, and it supports features such as Identical Code Folding and
Incremental linking.  Unfortunately it is not as well maintained as the BFD
linker, and it may become deprecated in the future.

# The higher of these two numbers determines the default linker.
%{!?ld_gold_priority:%global ld_gold_priority   30}

%endif

%{!?ld_bfd_priority: %global ld_bfd_priority    50}

#----------------------------------------------------------------------------

%if %{with gprofng}

%package gprofng
Summary: Next Generating code profiling tool
Provides: %{?scl_prefix}binutils-gprofng = %{version}-%{release}
Requires: %{?scl_prefix}binutils = %{version}-%{release}

BuildRequires: bison

%description gprofng
GprofNG is the GNU Next Generation Profiler for analyzing the performance 
of Linux applications.

%endif

#----------------------------------------------------------------------------

%if %{with crossbuilds}

# Uncomment this when testing changes to the spec file, especially the cross building support.
# Remember to comment it out again once the testing is complete.
# %%undefine with_testsuite

# The list of cross targets to build.
%global system         redhat-linux
%global cross_targets  aarch64-%{system} ppc64le-%{system} s390x-%{system} x86_64-%{system}

%package -n cross-binutils-aarch64
Summary: Cross targeted AArch64 binutils for developer use.  Not intended for production.
Provides: cross-binutils-aarch64 = %{version}-%{release}
Requires: coreutils
%if %{with systemzlib}
Requires: zlib-devel
%endif

BuildRequires: autoconf automake perl sed coreutils make findutils
BuildRequires: %{gcc_package}
BuildRequires: %{gxx_package}

ExcludeArch: aarch64-linux-gnu aarch64-redhat-linux

%description -n cross-binutils-aarch64
This package contains an AArch64 cross targeted version of the binutils for
use by developers.  It is NOT INTENDED FOR PRODUCTION use.


%package -n cross-binutils-ppc64le
Summary: Cross targeted PPC64LE binutils for developer use.  Not intended for production.
Provides: cross-binutils-ppc64le = %{version}-%{release}
Requires: coreutils
%if %{with systemzlib}
Requires: zlib-devel
%endif

BuildRequires: autoconf automake perl sed coreutils make findutils
BuildRequires: %{gcc_package}
BuildRequires: %{gxx_package}

ExcludeArch: ppc64le-linux-gnu ppc64le-redhat-linux

%description -n cross-binutils-ppc64le
This package contains a PPC64LE cross targeted version of the binutils for
use by developers.  It is NOT INTENDED FOR PRODUCTION use.


%package -n cross-binutils-s390x
Summary: Cross targeted S390X binutils for developer use.  Not intended for production.
Provides: cross-binutils-s390x = %{version}-%{release}
Requires: coreutils
%if %{with systemzlib}
Requires: zlib-devel
%endif

BuildRequires: autoconf automake perl sed coreutils make findutils
BuildRequires: %{gcc_package}
BuildRequires: %{gxx_package}

ExcludeArch: s390x-linux-gnu s390x-redhat-linux

%description -n cross-binutils-s390x
This package contains a S390X cross targeted version of the binutils for
use by developers.  It is NOT INTENDED FOR PRODUCTION use.


%package -n cross-binutils-x86_64
Summary: Cross targeted X86_64 binutils for developer use.  Not intended for production.
Provides: cross-binutils-x86_64 = %{version}-%{release}
Requires: coreutils
%if %{with systemzlib}
Requires: zlib-devel
%endif

BuildRequires: autoconf automake perl sed coreutils make findutils
BuildRequires: %{gcc_package}
BuildRequires: %{gxx_package}

ExcludeArch: x86_64-linux-gnu x86_64-redhat-linux i686-linux-gnu i686-redhat-linux

%description -n cross-binutils-x86_64
This package contains a X86_64 cross targeted version of the binutils for
use by developers.  It is NOT INTENDED FOR PRODUCTION use.

%endif

#----------------------------------------------------------------------------

%prep
# NB/ Do not add {?scl_prefix} to the -n option below.  The binutils sources
# uppack into a directory called binutils-VERSION not gcc-toolset-14-binutils-VERSION.
%autosetup -p1 -n binutils-%{version}

# On ppc64 and aarch64, we might use 64KiB pages
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*ppc.c
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*aarch64.c
sed -i -e '/common_pagesize/s/4 /64 /' gold/powerpc.cc
sed -i -e '/pagesize/s/0x1000,/0x10000,/' gold/aarch64.cc

# LTP sucks
perl -pi -e 's/i\[3-7\]86/i[34567]86/g' */conf*
sed -i -e 's/%''{release}/%{release}/g' bfd/Makefile{.am,.in}
sed -i -e '/^libopcodes_la_\(DEPENDENCIES\|LIBADD\)/s,$, ../bfd/libbfd.la,' opcodes/Makefile.{am,in}

# Build libbfd.so and libopcodes.so with -Bsymbolic-functions if possible.
if gcc %{optflags} -v --help 2>&1 | grep -q -- -Bsymbolic-functions; then
sed -i -e 's/^libbfd_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' bfd/Makefile.{am,in}
sed -i -e 's/^libopcodes_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' opcodes/Makefile.{am,in}
fi

# $PACKAGE is used for the gettext catalog name.
sed -i -e 's/^ PACKAGE=/ PACKAGE=%{?cross}/' */configure

# Undo the name change to run the testsuite.
for tool in binutils gas ld
do
  sed -i -e "2aDEJATOOL = $tool" $tool/Makefile.am
  sed -i -e "s/^DEJATOOL = .*/DEJATOOL = $tool/" $tool/Makefile.in
done

# Touch the .info files so that they are newer then the .texi files and
# hence do not need to be rebuilt.  This eliminates the need for makeinfo.
# The -print is there just to confirm that the command is working.
%if %{without docs}
  find . -name *.info -print -exec touch {} \;
%else
# If we are creating the docs, touch the texi files so that the info and
# man pages will be rebuilt.
  find . -name *.texi -print -exec touch {} \;
%endif

%ifarch %{power64}
%define _target_platform %{_arch}-%{_vendor}-%{_host_os}
%endif

#----------------------------------------------------------------------------

%build

# Building is now handled by functions which allow for both native and cross
# builds.  Builds are created in their own sub-directory of the sources, which
# allows for both native and cross builds to be created at the same time.

# compute_global_configuration()
#   Build the CARGS variable which contains the global configuration arguments.
compute_global_configuration()
{
    CARGS="--quiet \
	--build=%{_target_platform} \
	--host=%{_target_platform} \
	--enable-ld \
	--enable-plugins \
	--enable-64-bit-bfd \
	--with-bugurl=%{dist_bug_report_url}"

%if %{without bootstrap}
    CARGS="$CARGS --enable-jansson=yes"
%endif

%if %{with debuginfod}
    CARGS="$CARGS --with-debuginfod"
%endif

%if %{with gprofng}
    CARGS="$CARGS --enable-gprofng=yes"
%else
    CARGS="$CARGS --enable-gprofng=no"
%endif

%if %{with systemzlib}
    CARGS="$CARGS --with-system-zlib"
%endif

%if %{default_compress_debug}
    CARGS="$CARGS --enable-compressed-debug-sections=all"
%else
    CARGS="$CARGS --enable-compressed-debug-sections=none"
%endif

%if %{default_generate_notes}
    CARGS="$CARGS --enable-generate-build-notes=yes"
%else
    CARGS="$CARGS --enable-generate-build-notes=no"
%endif

%if %{default_relro}
    CARGS="$CARGS --enable-relro=yes"
%else
    CARGS="$CARGS --enable-relro=no"
%endif

%if %{enable_deterministic_archives}
    CARGS="$CARGS --enable-deterministic-archives"
%else
    CARGS="$CARGS --enable-deterministic-archives=no"
%endif

%if %{warn_for_executable_stacks}
    CARGS="$CARGS --enable-warn-execstack=yes"
    CARGS="$CARGS --enable-default-execstack=no"
%if %{error_for_executable_stacks}
    CARGS="$CARGS --enable-error-execstack=yes"
%endif
%else
    CARGS="$CARGS --enable-warn-execstack=no"
%endif

%if %{warn_for_rwx_segments}
    CARGS="$CARGS --enable-warn-rwx-segments=yes"
%if %{error_for_rwx_segments}
    CARGS="$CARGS --enable-error-rwx-segments=yes"
%endif
%else
    CARGS="$CARGS --enable-warn-rwx-segments=no"
%endif

%if %{enable_lto}
    CARGS="$CARGS --enable-lto"
%endif

%if %{enable_new_dtags}
    CARGS="$CARGS --enable-new-dtags --disable-rpath"
%endif

%if %{enable_separate_code}
  CARGS="$CARGS --enable-separate-code=yes"
%endif

%if %{enable_threading}
    CARGS="$CARGS --enable-threads=yes"
%else
    CARGS="$CARGS --enable-threads=no"
%endif
}

# run_target_configuration()
#    Create and configure the build tree.
#        $1 is the target architecture
#        $2 is 1 if this is a native build
#        $3 is 1 if shared libraries should be built
#
run_target_configuration()
{
    local target="$1"
    local native="$2"
    local shared="$3"
    local builddir=build-$target

    # Create a build directory
    rm -rf $builddir
    mkdir $builddir
    pushd $builddir

    echo "BUILDING the Binutils for TARGET $target (native ? $native) (shared ? $shared)"

    %set_build_flags

%ifarch %{power64}
    export CFLAGS="$RPM_OPT_FLAGS -Wno-error"
%else
    export CFLAGS="$RPM_OPT_FLAGS"
%endif

%if %{with debug}
    %undefine _fortify_level
    export CFLAGS="$CFLAGS -O0 -ggdb2 -Wno-error"
%endif

    export CXXFLAGS="$CXXFLAGS $CFLAGS"

    # BZ 1541027 - include the linker flags from redhat-rpm-config as well.
    export LDFLAGS=$RPM_LD_FLAGS

%if %{enable_new_dtags}
    # Build the tools with new dtags, as well as supporting their generation by the linker.
    export LDFLAGS="$LDFLAGS -Wl,--enable-new-dtags"
%endif

    if test x$native == x1 ; then
        # Extra targets to build along with the native one.
        #
        # BZ 1920373: Enable PEP support for all targets as the PERF package's
        # testsuite expects to be able to read PE format files ragrdless of
        # the host's architecture.
        #
        # Also enable the BPF target so that strip will work on BPF files.
        case $target in
    	s390*)
    	    # Note - The s390-linux target is there so that the GOLD linker will
    	    # build.  By default, if configured for just s390x-linux, the GOLD
    	    # configure system will only include support for 64-bit targets, but
    	    # the s390x gold backend uses both 32-bit and 64-bit templates.
    	    TARGS="--enable-targets=s390-linux,s390x-linux,x86_64-pep,bpf-unknown-none"
    	    ;;
    	ia64*)
    	    TARGS="--enable-targets=ia64-linux,x86_64-pep,bpf-unknown-none"
    	    ;;
    	ppc64-*)
    	    TARGS="--enable-targets=powerpc64le-linux,spu,x86_64-pep,bpf-unknown-none"
    	    ;;
    	ppc64le*)
    	    TARGS="--enable-targets=powerpc-linux,spu,x86_64-pep,bpf-unknown-none"
    	    ;;
    	*)
    	    TARGS="--enable-targets=x86_64-pep,bpf-unknown-none"
    	    ;;
        esac

	# Set up the sysroot and paths.
	SARGS="--with-sysroot=/ \
               --prefix=%{_prefix} \
               --libdir=%{_libdir} \
               --sysconfdir=%{_sysconfdir}"
%if %{with gold}
        SARGS="$SARGS --enable-gold=default"
%else
        SARGS="$SARGS --disable-gold"
%endif

    else # Cross builds

	# No extra targets are supported.
	TARGS=""

        # Disable the GOLD linker for cross builds because although it does
        # support sysroots specified on the command line, it does not support
        # them in linker scripts via the =/$SYSROOT prefix.
	SARGS="--with-sysroot=yes \
               --program-prefix=$target- \
               --prefix=%{_prefix}/$target \
               --libdir=%{_libdir} \
               --exec-prefix=%{_usr} \
               --sysconfdir=%{_sysconfdir} \
	       --disable-gold"
    fi

    if test x$shared == x1 ; then
	RARGS="--enable-shared"
    else
	RARGS="--disable-shared"
    fi

    CC=%gcc_for_binutils CXX=%gxx_for_binutils ../configure --target=$target $CARGS $SARGS $RARGS $TARGS  || cat config.log

    popd
}

# build_target ()
#   Builds a configured set of sources.
#        $1 is the target architecture
build_target()
{
    local target="$1"
    local builddir=build-$target

    pushd $builddir

%if %{with docs}
    # Because of parallel building, info has to be made after all.

    # FIXME: Setting CXXFLAGS is a workaround for the PPC64 compiler bug (cf RHEL-49348).
    # It allows the binutils to build using a version of gcc-toolset-14-ld that is already affected by the bug.
    # Once built and installed into the buildroot, this fix will no longer be needed.
    # Although whilst the bug in the PPC64 compiler remains Patch98 will still be needed.
    %make_build %{_smp_mflags} tooldir=%{_prefix} CC=%gcc_for_binutils CXX=%gxx_for_binutils all CXXFLAGS="$RPM_OPT_FLAGS -fno-lto"
    %make_build %{_smp_mflags} tooldir=%{_prefix} CC=%gcc_for_binutils CXX=%gxx_for_binutils info
%else
    %make_build %{_smp_mflags} tooldir=%{_prefix} CC=%gcc_for_binutils CXX=%gxx_for_binutils MAKEINFO=true all
%endif
    
    popd
}

# run_tests()
#	Test a built (but not installed) binutils.
#        $1 is the target architecture
#        $2 is 1 if this is a native build
#
run_tests()
{
    local target="$1"
    local native="$2"

    echo "TESTING the binutils FOR TARGET $target (native ? $native)"

    # Do not use %%check as it is run after %%install where libbfd.so is rebuilt
    # with -fvisibility=hidden no longer being usable in its shared form.
%if %{without testsuite}
    echo ================ $target == TESTSUITE DISABLED ====================
    return
%endif

    pushd build-$target

    # FIXME:  I have not been able to find a way to capture a "failed" return
    # value from "make check" without having it also stop the build.  So in
    # order to obtain the logs from the test runs if a check fails I have to
    # run the tests twice.  Once to generate the logs and then a second time
    # to generate the correct exit code.
    
    echo ================ $target == TEST RUN 1 =============================

    # Run the tests and accumulate the logs - but ignore failures...
    
    if test x$native == x1 ; then
	make -k CC=%gcc_for_binutils CXX=%gxx_for_binutils check-gas check-binutils check-ld < /dev/null || :
%if %{with gold}
	# The GOLD testsuite always returns an error code, even if no tests fail.
	make -k CC=%gcc_for_binutils CXX=%gxx_for_binutils check-gold < /dev/null || :
%endif
    else
	# Do not try running linking tests for the cross-binutils.
	make -k CC=%gcc_for_binutils CXX=%gxx_for_binutils check-gas check-binutils < /dev/null || :
    fi
    
    for f in {gas/testsuite/gas,ld/ld,binutils/binutils}.sum
    do
	if [ -f $f ]; then
	    cat $f
	fi
    done

%if %{with gold}
    if [ -f gold/test-suite.log ]; then
	cat gold/test-suite.log
    fi
    if [ -f gold/testsuite/test-suite.log ]; then
	cat gold/testsuite/*.log
    fi
%endif

    for file in {gas/testsuite/gas,ld/ld,binutils/binutils}.{sum,log}
    do
	if [ -f $file ]; then
	    ln $file binutils-$target-$(basename $file) || :
	fi
    done

    tar cjf binutils-$target.tar.xz  binutils-$target-*.{sum,log}
    uuencode binutils-$target.tar.xz binutils-$target.tar.xz
    rm -f binutils-$target.tar.xz    binutils-$target-*.{sum,log}

%if %{with gold}
    if [ -f gold/testsuite/test-suite.log ]; then
	tar cjf  binutils-$target-gold.log.tar.xz gold/testsuite/*.log
	uuencode binutils-$target-gold.log.tar.xz binutils-$target-gold.log.tar.xz
	rm -f    binutils-$target-gold.log.tar.xz
    fi
%endif

    echo ================ $target == TEST RUN 2 =============================

    # Run the tests and this time fail if there are any errors.

    if test x$native == x1 ; then
	make -k CC=%gcc_for_binutils CXX=%gxx_for_binutils check-gas check-binutils check-ld < /dev/null
	# Ignore the gold tests - they always fail
    else
	# Do not try running linking tests for the cross-binutils.
	make -k CC=%gcc_for_binutils CXX=%gxx_for_binutils check-gas check-binutils < /dev/null
    fi

    popd
}

#----------------------------------------------------------------------------

# There is a problem with the clang+libtool+lto combination.
# The LDFLAGS containing -flto are not being passed when linking the
# libbfd.so, so the build fails.  Solution: disable LTO.
%if %{with clang}
%define enable_lto 0
%endif

%if %{with clang}
%define _with_cc_clang 1
%endif

# Disable LTO on Arm due to:
# https://bugzilla.redhat.com/show_bug.cgi?id=1918924
%ifarch %{arm}
%define enable_lto 0
%endif

%if !0%{?enable_lto}
%global _lto_cflags %{nil}
%endif

compute_global_configuration

# Build the native configuration.
run_target_configuration  %{_target_platform} 1 %{enable_shared}
build_target              %{_target_platform}
run_tests                 %{_target_platform} 1 

%if %{with crossbuilds}

# Build the cross configurations.
for f in %{cross_targets}; do

    # Skip the native build.
    if test x$f != x%{_target_platform}; then
	# We could improve the cross build's size by enabling shared libraries but
	# the produced binaries may be less convenient in the embedded environment.
        run_target_configuration  $f 0 0
	build_target              $f 
	run_tests                 $f 0
    fi
done

%endif

#----------------------------------------------------------------------------

%install

# install_binutils()
#	Install the binutils.
#        $1 is the target architecture
#        $2 is 1 if this is a native build
#        $3 is 1 if shared libraries should be built
#
install_binutils()
{
    local target="$1"
    local native="$2"
    local shared="$3"

    local local_root=%{buildroot}/%{_prefix}
    local local_bindir=$local_root/bin
    local local_libdir=%{buildroot}%{_libdir}
    local local_mandir=$local_root/share/man/man1
    local local_incdir=$local_root/include
    local local_infodir=$local_root/share/info
    local local_libdir
    
    mkdir -p $local_libdir
    mkdir -p $local_incdir
    mkdir -p $local_mandir
    mkdir -p $local_infodir

    echo "INSTALLING the binutils FOR TARGET $target (native ? $native) (shared ? $shared)"

    pushd build-$target
    
    if test x$native == x1 ; then

%if %{with docs}
	%make_install CC=%gcc_for_binutils CXX=%gxx_for_binutils DESTDIR=%{buildroot}
	make CC=%gcc_for_binutils CXX=%gxx_for_binutils prefix=%{buildroot}%{_prefix} infodir=$local_infodir install-info
%else
	%make_install CC=%gcc_for_binutils CXX=%gxx_for_binutils DESTDIR=%{buildroot} MAKEINFO=true
%endif
        # Rebuild the static libiaries with -fPIC.
	# It would be nice to build the static libraries with -fno-lto so that
	# they can be used by programs that are built with a different version
	# of GCC from the one used to build the libraries, but this will trigger
	# warnings from annocheck.

        # Future: Remove libiberty together with its header file, projects should bundle it.
	%make_build -s -C libiberty CC=%gcc_for_binutils CXX=%gxx_for_binutils clean
	%set_build_flags
	%make_build -s CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C libiberty CC=%gcc_for_binutils CXX=%gxx_for_binutils 

	# Without the hidden visibility the 3rd party shared libraries would export
	# the bfd non-stable ABI.
	%make_build -s -C bfd CC=%gcc_for_binutils CXX=%gxx_for_binutils clean
	%set_build_flags
	%make_build -s CFLAGS="-g -fPIC $RPM_OPT_FLAGS -fvisibility=hidden" -C bfd CC=%gcc_for_binutils CXX=%gxx_for_binutils 

	%make_build -s -C opcodes clean CC=%gcc_for_binutils CXX=%gxx_for_binutils
	%set_build_flags
	%make_build -s CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C opcodes CC=%gcc_for_binutils CXX=%gxx_for_binutils

	%make_build -s -C libsframe clean CC=%gcc_for_binutils CXX=%gxx_for_binutils
	%set_build_flags
	%make_build -s CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C libsframe CC=%gcc_for_binutils CXX=%gxx_for_binutils

	install -m 644 bfd/.libs/libbfd.a           $local_libdir
	install -m 644 libiberty/libiberty.a        $local_libdir
	install -m 644 ../include/libiberty.h       $local_incdir
	install -m 644 opcodes/.libs/libopcodes.a   $local_libdir
	install -m 644 libsframe/.libs/libsframe.a  $local_libdir

	# Remove Windows/Novell only man pages
	rm -f $local_mandir/{dlltool,nlmconv,windres,windmc}*
%if %{without docs}
	rm -f $local_mandir/{addr2line,ar,as,c++filt,elfedit,gprof,ld,nm,objcopy,objdump,ranlib,readelf,size,strings,strip}*
	rm -f $local_infodir/{as,bfd,binutils,gprof,ld}*
%endif

%if %{enable_shared}
	chmod +x $local_libdir/lib*.so*
%endif

	# Prevent programs from linking against libbfd and libopcodes
	# dynamically, as they are changed far too often.
	rm -f $local_libdir/lib{bfd,opcodes}.so

	# Remove libtool files, which reference the .so libs
	rm -f %local_libdir/lib{bfd,opcodes}.la

	# Sanity check --enable-64-bit-bfd really works.
	grep '^#define BFD_ARCH_SIZE 64$' $local_incdir/bfd.h
	# Fix multilib conflicts of generated values by __WORDSIZE-based expressions.
%ifarch %{ix86} x86_64 ppc %{power64} s390 s390x sh3 sh4 sparc sparc64 arm
	sed -i -e '/^#include "ansidecl.h"/{p;s~^.*$~#include <bits/wordsize.h>~;}' \
	    -e 's/^#define BFD_DEFAULT_TARGET_SIZE \(32\|64\) *$/#define BFD_DEFAULT_TARGET_SIZE __WORDSIZE/' \
	    -e 's/^#define BFD_HOST_64BIT_LONG [01] *$/#define BFD_HOST_64BIT_LONG (__WORDSIZE == 64)/' \
	    -e 's/^#define BFD_HOST_64_BIT \(long \)\?long *$/#if __WORDSIZE == 32\
#define BFD_HOST_64_BIT long long\
#else\
#define BFD_HOST_64_BIT long\
#endif/' \
	    -e 's/^#define BFD_HOST_U_64_BIT unsigned \(long \)\?long *$/#define BFD_HOST_U_64_BIT unsigned BFD_HOST_64_BIT/' \
	    $local_incdir/bfd.h
%endif

	touch -r ../bfd/bfd-in2.h $local_incdir/bfd.h

	# Generate .so linker scripts for dependencies; imported from glibc/Makerules:

	# This fragment of linker script gives the OUTPUT_FORMAT statement
	# for the configuration we are building.
	OUTPUT_FORMAT="\
/* Ensure this .so library will not be used by a link for a different format
   on a multi-architecture system.  */
$(gcc $CFLAGS $LDFLAGS -shared -x c /dev/null -o /dev/null -Wl,--verbose -v 2>&1 | sed -n -f "%{SOURCE2}")"

	tee $local_libdir/libbfd.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

/* The libz & libsframe dependencies are unexpected by legacy build scripts.  */
/* The libdl dependency is for plugin support.  (BZ 889134)  */
INPUT ( %{_libdir}/libbfd.a %{_libdir}/libsframe.a -liberty -lz -ldl )
EOH

	tee $local_libdir/libopcodes.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

INPUT ( %{_libdir}/libopcodes.a -lbfd )
EOH

	rm -fr $local_root/$target

    else # CROSS BUILDS

	local target_root=$local_root/$target
	
	%make_install DESTDIR=%{buildroot} MAKEINFO=true CC=%gcc_for_binutils CXX=%gxx_for_binutils
    fi

    # This one comes from gcc
    rm -f $local_infodir/dir

    %find_lang binutils
    %find_lang opcodes
    %find_lang bfd
    %find_lang gas
    %find_lang gprof
    cat opcodes.lang >> binutils.lang
    cat bfd.lang     >> binutils.lang
    cat gas.lang     >> binutils.lang
    cat gprof.lang   >> binutils.lang

    if [ -x ld/ld-new ]; then
	%find_lang ld
	cat ld.lang >> binutils.lang
    fi

    if [ -x gold/ld-new ]; then
	%find_lang gold
	cat gold.lang >> binutils.lang
    fi

    popd
}

#----------------------------------------------------------------------------

install_binutils %{_target_platform} 1 %{enable_shared}

%if %{with crossbuilds}

for f in %{cross_targets}; do
    if test x$f != x%{_target_platform}; then
	install_binutils $f 0 0
    fi
done

%endif

# Stop check-rpaths from complaining about standard runpaths.
export QA_RPATHS=0x0003

#----------------------------------------------------------------------------

%post

# Remove the /usr/bin/ld file so that the alternatives program
# can replace it with a symbolic link.
%__rm -f %{_bindir}/ld

%{alternatives_cmdline} --install %{_bindir}/ld ld \
  %{_bindir}/ld.bfd %{ld_bfd_priority}

# Do not run "alternatives --auto ld" here.  Leave the setting to
# however the user previously had it set.  See BZ 1592069 for more details.

%ldconfig_post

# BZ 2232410: We cannot be sure that the GTS runtime rpm has restored the SE context.
restorecon -R %{_scl_root}/usr/share/locale

# RHEL-22818: Restore the SELinux context of the bfd-plugins.
restorecon -R %{_libdir}

exit 0

#------------------

%post devel
# RHEL-22818: Restore the SELinux context of the libraries.
restorecon -R %{_libdir}
exit 0

#------------------

%if %{with gprofng}
%post gprofng
# RHEL-22818: Restire the SELinux context of the gprofng libraries.
restorecon -R %{_libdir}
# And the rc file.
restorecon %{_scl_root}/etc/gprofng.rc
exit 0
%endif

#------------------

%if %{with gold}
%post gold

%{alternatives_cmdline} --install %{_bindir}/ld ld \
  %{_bindir}/ld.gold %{ld_gold_priority}

exit 0
%endif

#----------------------------------------------------------------------------

# Note: $1 == 0 means that there is an uninstall in progress.
# $1 == 1 means that there is an upgrade in progress.

%if %{with gold}
%preun gold

if [ $1 = 0 ]; then
  %{alternatives_cmdline} --remove ld %{_bindir}/ld.gold
fi
exit 0
%endif

%preun
if [ $1 = 0 ]; then
  %{alternatives_cmdline} --remove ld %{_bindir}/ld.bfd
fi

# Restore the /usr/bin/ld file so that the automatic file
# removal part of the uninstall process will work.
touch %{_bindir}/ld

exit 0

#----------------------------------------------------------------------------

%postun
%ldconfig_postun

#----------------------------------------------------------------------------

%files -f build-%{_target_platform}/binutils.lang

%if %{with crossbuilds}
%if "%{_target_platform}" != "aarch64-%{system}"
%exclude /usr/aarch64-%{system}/*
%exclude /usr/bin/aarch64-%{system}-*
%endif

%if "%{_target_platform}" != "ppc64le-%{system}"
%exclude /usr/ppc64le-%{system}/*
%exclude /usr/bin/ppc64le-%{system}-*
%endif

%if "%{_target_platform}" != "s390x-%{system}"
%exclude /usr/s390x-%{system}/*
%exclude /usr/bin/s390x-%{system}-*
%endif

%if "%{_target_platform}" != "x86_64-%{system}"
%exclude /usr/x86_64-%{system}/*
%exclude /usr/bin/x86_64-%{system}-*
%endif
%endif

%license COPYING COPYING3 COPYING3.LIB COPYING.LIB
%doc README
%{_bindir}/[!l]*
# %%verify(symlink) does not work for some reason, so using "owner" instead.
%verify(owner) %{_bindir}/ld
# The mtime check fails for ld.bfd because of the alternatives mechanism, so ignore it.
%verify(owner) %{_bindir}/ld.bfd

%if %{with gprofng}
%exclude %{_bindir}/gp-*
%exclude %{_bindir}/gprofng
%endif

%exclude %dir %{_exec_prefix}/lib/debug

%if %{with docs}
%{_mandir}/man1/
%exclude %{_mandir}/man1/gp-*
%exclude %{_mandir}/man1/gprofng*
%{_infodir}/as.info.*
%{_infodir}/binutils.info.*
%{_infodir}/ld.info.*
%{_infodir}/ldint.info.*
%{_infodir}/bfd.info.*
%{_infodir}/ctf-spec.info.*
%{_infodir}/gprof.info.*
%{_infodir}/sframe-spec.info.*

%if %{with gprofng}
%exclude %{_infodir}/gprofng*
%endif
%endif

%if %{enable_shared}
%{_libdir}/lib*.so
%{_libdir}/lib*.so.*
%exclude %{_libdir}/libbfd.so
%exclude %{_libdir}/libopcodes.so
%exclude %{_libdir}/libctf.a
%exclude %{_libdir}/libctf-nobfd.a

%dir %{_libdir}/bfd-plugins
%{_libdir}/bfd-plugins/libdep.so
%endif

%if %{with debug}
%dir %{_libdir}/bfd-plugins
%{_libdir}/bfd-plugins/libdep.a
%endif

%files devel
%{_prefix}/include/*
%{_libdir}/lib*.a
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.so
%if %{enable_shared}
%exclude %{_libdir}/lib*.la
%endif

%if %{with gold}
%files gold
%{_bindir}/%{?cross}ld.gold
%endif

%if %{with gprofng}
%files gprofng
%{_bindir}/gp-*
%{_bindir}/gprofng
%{_mandir}/man1/gp-*
%{_mandir}/man1/gprofng*
%{_infodir}/gprofng.info.*
%dir %{_libdir}/gprofng
%{_libdir}/gprofng/*
# FIXME: Work out the correct way to specify this file:
%{_scl_root}/etc/gprofng.rc
%endif

%if %{with crossbuilds}

%if "%{_target_platform}" != "aarch64-%{system}"
%files -n cross-binutils-aarch64 
/usr/aarch64-%{system}/
/usr/bin/aarch64-%{system}-*
%endif

%if "%{_target_platform}" != "ppc64le-%{system}"
%files -n cross-binutils-ppc64le
/usr/ppc64le-%{system}/
/usr/bin/ppc64le-%{system}-*
%endif

%if "%{_target_platform}" != "s390x-%{system}"
%files -n cross-binutils-s390x
/usr/s390x-%{system}/
/usr/bin/s390x-%{system}-*
%endif

%if "%{_target_platform}" != "x86_64-%{system}"
%files -n cross-binutils-x86_64
/usr/x86_64-%{system}/
/usr/bin/x86_64-%{system}-*
%endif

%endif

#----------------------------------------------------------------------------
%changelog
* Mon Feb 24 2025 Nick Clifton  <nickc@redhat.com> - 2.41-4.1
- Fix assertion failure in ppc64 ld due to compiler miscompilation.  (RHEL-83791)

* Thu Feb 20 2025 Nick Clifton  <nickc@redhat.com> - 2.41-4
- Backport fixes for PR 32082 and PR 32153 in order to fix the PR 20267 linker tests.  (RHEL-80372)

* Fri Aug 16 2024 Nick Clifton  <nickc@redhat.com> - 2.41-3
- Fix restoring contect to gprofng.rc file.  (RHEL-54563)

* Fri Aug 16 2024 Nick Clifton  <nickc@redhat.com> - 2.41-2
- NVR Bump to allow rebuilding with GTS-14 gcc.  (RHEL-53516)

* Fri Apr 26 2024 Nick Clifton  <nickc@redhat.com> - 2.41-1
- Initial import of upstream 2.41 release with patches from Fedora 40.
