%global DATE 20220421
%global gitrev 1d3172725999deb0dca93ac70393ed9a0ad0da3f
%global gcc_version 11.3.1
%global gcc_major 11
# Note, gcc_release must be integer, if you want to add suffixes to
# %%{release}, append them after %%{gcc_release} on Release: line.
%global gcc_release 2
%global nvptx_tools_gitrev 5f6f343a302d620b0868edab376c00b15741e39e
%global newlib_cygwin_gitrev 50e2a63b04bdd018484605fbb954fd1bd5147fa0
%global _unpackaged_files_terminate_build 0
%if 0%{?fedora} > 27 || 0%{?rhel} > 7
# Until annobin is fixed (#1519165).
%undefine _annotated_build
%endif
# Strip will fail on nvptx-none *.a archives and the brp-* scripts will
# fail randomly depending on what is stripped last.
%if 0%{?__brp_strip_static_archive:1}
%global __brp_strip_static_archive %{__brp_strip_static_archive} || :
%endif
%if 0%{?__brp_strip_lto:1}
%global __brp_strip_lto %{__brp_strip_lto} || :
%endif
%if 0%{?fedora} < 32 && 0%{?rhel} < 8
%global multilib_64_archs sparc64 ppc64 ppc64p7 s390x x86_64
%else
%global multilib_64_archs sparc64 ppc64 ppc64p7 x86_64
%endif
%if 0%{?rhel} > 7
%global build_ada 0
%global build_objc 0
%global build_go 0
%global build_d 0
%else
%ifarch %{ix86} x86_64 ia64 ppc %{power64} alpha s390x %{arm} aarch64 riscv64
%global build_ada 1
%else
%global build_ada 0
%endif
%global build_objc 1
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64 %{mips} riscv64
%global build_go 1
%else
%global build_go 0
%endif
%ifarch %{ix86} x86_64 %{arm} %{mips} s390 s390x riscv64
%global build_d 1
%else
%global build_d 0
%endif
%endif
%ifarch %{ix86} x86_64 ia64 ppc64le
%global build_libquadmath 1
%else
%global build_libquadmath 0
%endif
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64
%global build_libasan 1
%else
%global build_libasan 0
%endif
%ifarch x86_64 ppc64 ppc64le aarch64
%global build_libtsan 1
%else
%global build_libtsan 0
%endif
%ifarch x86_64 ppc64 ppc64le aarch64
%global build_liblsan 1
%else
%global build_liblsan 0
%endif
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64
%global build_libubsan 1
%else
%global build_libubsan 0
%endif
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64 %{mips} riscv64
%global build_libatomic 1
%else
%global build_libatomic 0
%endif
%ifarch %{ix86} x86_64 %{arm} alpha ppc ppc64 ppc64le ppc64p7 s390 s390x aarch64
%global build_libitm 1
%else
%global build_libitm 0
%endif
%if 0%{?rhel} > 8
%global build_isl 0
%else
%global build_isl 1
%endif
%global build_libstdcxx_docs 1
%ifarch %{ix86} x86_64 ppc ppc64 ppc64le ppc64p7 s390 s390x %{arm} aarch64 %{mips}
%global attr_ifunc 1
%else
%global attr_ifunc 0
%endif
%ifarch x86_64 ppc64le
%global build_offload_nvptx 1
%else
%global build_offload_nvptx 0
%endif
%if 0%{?fedora} < 32 && 0%{?rhel} < 8
%ifarch s390x
%global multilib_32_arch s390
%endif
%endif
%ifarch sparc64
%global multilib_32_arch sparcv9
%endif
%ifarch ppc64 ppc64p7
%global multilib_32_arch ppc
%endif
%ifarch x86_64
%global multilib_32_arch i686
%endif
Summary: Various compilers (C, C++, Objective-C, ...)
Name: gcc
Version: %{gcc_version}
Release: %{gcc_release}.1%{?dist}
# libgcc, libgfortran, libgomp, libstdc++ and crtstuff have
# GCC Runtime Exception.
License: GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions and LGPLv2+ and BSD
# The source for this package was pulled from upstream's vcs.
# %%{gitrev} is some commit from the
# https://gcc.gnu.org/git/?p=gcc.git;h=refs/vendors/redhat/heads/gcc-%%{gcc_major}-branch
# branch.  Use the following commands to generate the tarball:
# git clone --depth 1 git://gcc.gnu.org/git/gcc.git gcc-dir.tmp
# git --git-dir=gcc-dir.tmp/.git fetch --depth 1 origin %%{gitrev}
# git --git-dir=gcc-dir.tmp/.git archive --prefix=%%{name}-%%{version}-%%{DATE}/ %%{gitrev} | xz -9e > %%{name}-%%{version}-%%{DATE}.tar.xz
# rm -rf gcc-dir.tmp
Source0: gcc-%{version}-%{DATE}.tar.xz
# The source for nvptx-tools package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
# git clone --depth 1 git://github.com/MentorEmbedded/nvptx-tools.git nvptx-tools-dir.tmp
# git --git-dir=nvptx-tools-dir.tmp/.git fetch --depth 1 origin %%{nvptx_tools_gitrev}
# git --git-dir=nvptx-tools-dir.tmp/.git archive --prefix=nvptx-tools-%%{nvptx_tools_gitrev}/ %%{nvptx_tools_gitrev} | xz -9e > nvptx-tools-%%{nvptx_tools_gitrev}.tar.xz
# rm -rf nvptx-tools-dir.tmp
Source1: nvptx-tools-%{nvptx_tools_gitrev}.tar.xz
# The source for nvptx-newlib package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
# git clone git://sourceware.org/git/newlib-cygwin.git newlib-cygwin-dir.tmp
# git --git-dir=newlib-cygwin-dir.tmp/.git archive --prefix=newlib-cygwin-%%{newlib_cygwin_gitrev}/ %%{newlib_cygwin_gitrev} ":(exclude)newlib/libc/sys/linux/include/rpc/*.[hx]" | xz -9e > newlib-cygwin-%%{newlib_cygwin_gitrev}.tar.xz
# rm -rf newlib-cygwin-dir.tmp
Source2: newlib-cygwin-%{newlib_cygwin_gitrev}.tar.xz
%global isl_version 0.18
Source3: https://gcc.gnu.org/pub/gcc/infrastructure/isl-%{isl_version}.tar.bz2
URL: http://gcc.gnu.org
# Need binutils with -pie support >= 2.14.90.0.4-4
# Need binutils which can omit dot symbols and overlap .opd on ppc64 >= 2.15.91.0.2-4
# Need binutils which handle -msecure-plt on ppc >= 2.16.91.0.2-2
# Need binutils which support .weakref >= 2.16.91.0.3-1
# Need binutils which support --hash-style=gnu >= 2.17.50.0.2-7
# Need binutils which support mffgpr and mftgpr >= 2.17.50.0.2-8
# Need binutils which support --build-id >= 2.17.50.0.17-3
# Need binutils which support %%gnu_unique_object >= 2.19.51.0.14
# Need binutils which support .cfi_sections >= 2.19.51.0.14-33
# Need binutils which support --no-add-needed >= 2.20.51.0.2-12
# Need binutils which support -plugin
# Need binutils which support .loc view >= 2.30
# Need binutils which support --generate-missing-build-notes=yes >= 2.31
%if 0%{?fedora} >= 29 || 0%{?rhel} > 7
BuildRequires: binutils >= 2.31
%else
BuildRequires: binutils >= 2.24
%endif
# While gcc doesn't include statically linked binaries, during testing
# -static is used several times.
BuildRequires: glibc-static
BuildRequires: zlib-devel, gettext, dejagnu, bison, flex, sharutils
BuildRequires: texinfo, texinfo-tex, /usr/bin/pod2man
BuildRequires: systemtap-sdt-devel >= 1.3
BuildRequires: gmp-devel >= 4.1.2-8, mpfr-devel >= 3.1.0, libmpc-devel >= 0.8.1
BuildRequires: python3-devel, /usr/bin/python
BuildRequires: gcc, gcc-c++, make
%if %{build_go}
BuildRequires: hostname, procps
%endif
# For VTA guality testing
BuildRequires: gdb
# Make sure pthread.h doesn't contain __thread tokens
# Make sure glibc supports stack protector
# Make sure glibc supports DT_GNU_HASH
BuildRequires: glibc-devel >= 2.4.90-13
BuildRequires: elfutils-devel >= 0.147
BuildRequires: elfutils-libelf-devel >= 0.147
BuildRequires: libzstd-devel
%ifarch ppc ppc64 ppc64le ppc64p7 s390 s390x sparc sparcv9 alpha
# Make sure glibc supports TFmode long double
BuildRequires: glibc >= 2.3.90-35
%endif
%ifarch %{multilib_64_archs} sparcv9 ppc
# Ensure glibc{,-devel} is installed for both multilib arches
BuildRequires: /lib/libc.so.6 /usr/lib/libc.so /lib64/libc.so.6 /usr/lib64/libc.so
%endif
%if %{build_ada}
# Ada requires Ada to build
BuildRequires: gcc-gnat >= 3.1, libgnat >= 3.1
%endif
%ifarch ia64
BuildRequires: libunwind >= 0.98
%endif
%if %{build_libstdcxx_docs}
BuildRequires: doxygen >= 1.7.1
BuildRequires: graphviz, dblatex, texlive-collection-latex, docbook5-style-xsl
%endif
Requires: cpp = %{version}-%{release}
# Need .eh_frame ld optimizations
# Need proper visibility support
# Need -pie support
# Need --as-needed/--no-as-needed support
# On ppc64, need omit dot symbols support and --non-overlapping-opd
# Need binutils that owns /usr/bin/c++filt
# Need binutils that support .weakref
# Need binutils that supports --hash-style=gnu
# Need binutils that support mffgpr/mftgpr
# Need binutils that support --build-id
# Need binutils that support %%gnu_unique_object
# Need binutils that support .cfi_sections
# Need binutils that support --no-add-needed
# Need binutils that support -plugin
# Need binutils that support .loc view >= 2.30
# Need binutils which support --generate-missing-build-notes=yes >= 2.31
%if 0%{?fedora} >= 29 || 0%{?rhel} > 7
Requires: binutils >= 2.31
%else
Requires: binutils >= 2.24
%endif
# Make sure gdb will understand DW_FORM_strp
Conflicts: gdb < 5.1-2
Requires: glibc-devel >= 2.2.90-12
%ifarch ppc ppc64 ppc64le ppc64p7 s390 s390x sparc sparcv9 alpha
# Make sure glibc supports TFmode long double
Requires: glibc >= 2.3.90-35
%endif
%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
%ifarch %{arm}
Requires: glibc >= 2.16
%endif
%endif
Requires: libgcc >= %{version}-%{release}
Requires: libgomp = %{version}-%{release}
# lto-wrapper invokes make
Requires: make
%if !%{build_ada}
Obsoletes: gcc-gnat < %{version}-%{release}
%endif
Obsoletes: gcc-java < %{version}-%{release}
AutoReq: true
Provides: bundled(libiberty)
Provides: bundled(libbacktrace)
Provides: bundled(libffi)
Provides: gcc(major) = %{gcc_major}

Patch0: gcc11-hack.patch
Patch2: gcc11-sparc-config-detection.patch
Patch3: gcc11-libgomp-omp_h-multilib.patch
Patch4: gcc11-libtool-no-rpath.patch
Patch5: gcc11-isl-dl.patch
Patch6: gcc11-isl-dl2.patch
Patch7: gcc11-libstdc++-docs.patch
Patch8: gcc11-no-add-needed.patch
Patch9: gcc11-foffload-default.patch
Patch10: gcc11-Wno-format-security.patch
Patch11: gcc11-rh1574936.patch
Patch12: gcc11-d-shared-libphobos.patch
Patch14: gcc11-libgcc-link.patch
Patch15: gcc11-pr101786.patch
Patch16: gcc11-stringify-__VA_OPT__.patch
Patch17: gcc11-stringify-__VA_OPT__-2.patch
Patch18: gcc11-Wbidi-chars.patch
Patch19: gcc11-dg-ice-fixes.patch
Patch20: gcc11-relocatable-pch.patch
Patch21: gcc11-dejagnu-multiline.patch
Patch23: gcc11-pie.patch
Patch24: gcc11-bind-now.patch
Patch25: gcc11-pr105331.patch
# This can go once we rebase from GCC 11.
Patch26: gcc11-rh2106262.patch

Patch100: gcc11-fortran-fdec-duplicates.patch
Patch101: gcc11-fortran-flogical-as-integer.patch
Patch102: gcc11-fortran-fdec-ichar.patch
Patch103: gcc11-fortran-fdec-non-integer-index.patch
Patch104: gcc11-fortran-fdec-old-init.patch
Patch105: gcc11-fortran-fdec-override-kind.patch
Patch106: gcc11-fortran-fdec-non-logical-if.patch
Patch107: gcc11-fortran-fdec-promotion.patch
Patch108: gcc11-fortran-fdec-sequence.patch
Patch109: gcc11-fortran-fdec-add-missing-indexes.patch

# On ARM EABI systems, we do want -gnueabi to be part of the
# target triple.
%ifnarch %{arm}
%global _gnu %{nil}
%else
%global _gnu -gnueabi
%endif
%ifarch sparcv9
%global gcc_target_platform sparc64-%{_vendor}-%{_target_os}
%endif
%ifarch ppc ppc64p7
%global gcc_target_platform ppc64-%{_vendor}-%{_target_os}
%endif
%ifnarch sparcv9 ppc ppc64p7
%global gcc_target_platform %{_target_platform}
%endif

%if %{build_go}
# Avoid stripping these libraries and binaries.
%global __os_install_post \
chmod 644 %{buildroot}%{_prefix}/%{_lib}/libgo.so.19.* \
chmod 644 %{buildroot}%{_prefix}/bin/go.gcc \
chmod 644 %{buildroot}%{_prefix}/bin/gofmt.gcc \
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cgo \
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/buildid \
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/test2json \
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/vet \
%__os_install_post \
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgo.so.19.* \
chmod 755 %{buildroot}%{_prefix}/bin/go.gcc \
chmod 755 %{buildroot}%{_prefix}/bin/gofmt.gcc \
chmod 755 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cgo \
chmod 755 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/buildid \
chmod 755 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/test2json \
chmod 755 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/vet \
%{nil}
%endif

%description
The gcc package contains the GNU Compiler Collection version 11.
You'll need this package in order to compile C code.

%package -n libgcc
Summary: GCC version 11 shared support library
Autoreq: false
%if !%{build_ada}
Obsoletes: libgnat < %{version}-%{release}
%endif
Obsoletes: libmudflap
Obsoletes: libmudflap-devel
Obsoletes: libmudflap-static
Obsoletes: libgcj < %{version}-%{release}
Obsoletes: libgcj-devel < %{version}-%{release}
Obsoletes: libgcj-src < %{version}-%{release}
%ifarch %{ix86} x86_64
Obsoletes: libcilkrts
Obsoletes: libcilkrts-static
Obsoletes: libmpx
Obsoletes: libmpx-static
%endif

%description -n libgcc
This package contains GCC shared support library which is needed
e.g. for exception handling support.

%package c++
Summary: C++ support for GCC
Requires: gcc = %{version}-%{release}
Requires: libstdc++ = %{version}-%{release}
Requires: libstdc++-devel = %{version}-%{release}
Provides: gcc-g++ = %{version}-%{release}
Provides: g++ = %{version}-%{release}
Autoreq: true

%description c++
This package adds C++ support to the GNU Compiler Collection.
It includes support for most of the current C++ specification,
including templates and exception handling.

%package -n libstdc++
Summary: GNU Standard C++ Library
Autoreq: true
Requires: glibc >= 2.10.90-7

%description -n libstdc++
The libstdc++ package contains a rewritten standard compliant GCC Standard
C++ Library.

%package -n libstdc++-devel
Summary: Header files and libraries for C++ development
Requires: libstdc++%{?_isa} = %{version}-%{release}
Autoreq: true

%description -n libstdc++-devel
This is the GNU implementation of the standard C++ libraries.  This
package includes the header files and libraries needed for C++
development. This includes rewritten implementation of STL.

%package -n libstdc++-static
Summary: Static libraries for the GNU standard C++ library
Requires: libstdc++-devel = %{version}-%{release}
Autoreq: true

%description -n libstdc++-static
Static libraries for the GNU standard C++ library.

%package -n libstdc++-docs
Summary: Documentation for the GNU standard C++ library
Autoreq: true

%description -n libstdc++-docs
Manual, doxygen generated API information and Frequently Asked Questions
for the GNU standard C++ library.

%package objc
Summary: Objective-C support for GCC
Requires: gcc = %{version}-%{release}
Requires: libobjc = %{version}-%{release}
Autoreq: true

%description objc
gcc-objc provides Objective-C support for the GCC.
Mainly used on systems running NeXTSTEP, Objective-C is an
object-oriented derivative of the C language.

%package objc++
Summary: Objective-C++ support for GCC
Requires: gcc-c++ = %{version}-%{release}, gcc-objc = %{version}-%{release}
Autoreq: true

%description objc++
gcc-objc++ package provides Objective-C++ support for the GCC.

%package -n libobjc
Summary: Objective-C runtime
Autoreq: true

%description -n libobjc
This package contains Objective-C shared library which is needed to run
Objective-C dynamically linked programs.

%package gfortran
Summary: Fortran support
Requires: gcc = %{version}-%{release}
Requires: libgfortran = %{version}-%{release}
%if %{build_libquadmath}
Requires: libquadmath = %{version}-%{release}
Requires: libquadmath-devel = %{version}-%{release}
%endif
Provides: gcc-fortran = %{version}-%{release}
Provides: gfortran = %{version}-%{release}
Autoreq: true

%description gfortran
The gcc-gfortran package provides support for compiling Fortran
programs with the GNU Compiler Collection.

%package -n libgfortran
Summary: Fortran runtime
Autoreq: true
%if %{build_libquadmath}
Requires: libquadmath = %{version}-%{release}
%endif

%description -n libgfortran
This package contains Fortran shared library which is needed to run
Fortran dynamically linked programs.

%package -n libgfortran-static
Summary: Static Fortran libraries
Requires: libgfortran = %{version}-%{release}
Requires: gcc = %{version}-%{release}
%if %{build_libquadmath}
Requires: libquadmath-static = %{version}-%{release}
%endif

%description -n libgfortran-static
This package contains static Fortran libraries.

%package gdc
Summary: D support
Requires: gcc = %{version}-%{release}
Requires: libgphobos = %{version}-%{release}
Provides: gcc-d = %{version}-%{release}
Provides: gdc = %{version}-%{release}
Autoreq: true

%description gdc
The gcc-gdc package provides support for compiling D
programs with the GNU Compiler Collection.

%package -n libgphobos
Summary: D runtime
Autoreq: true

%description -n libgphobos
This package contains D shared library which is needed to run
D dynamically linked programs.

%package -n libgphobos-static
Summary: Static D libraries
Requires: libgphobos = %{version}-%{release}
Requires: gcc-gdc = %{version}-%{release}

%description -n libgphobos-static
This package contains static D libraries.

%package -n libgomp
Summary: GCC OpenMP v4.5 shared support library

%description -n libgomp
This package contains GCC shared support library which is needed
for OpenMP v4.5 support.

%package -n libgomp-offload-nvptx
Summary: GCC OpenMP v4.5 plugin for offloading to NVPTX
Requires: libgomp = %{version}-%{release}

%description -n libgomp-offload-nvptx
This package contains libgomp plugin for offloading to NVidia
PTX.  The plugin needs libcuda.so.1 shared library that has to be
installed separately.

%package gdb-plugin
Summary: GCC plugin for GDB
Requires: gcc = %{version}-%{release}

%description gdb-plugin
This package contains GCC plugin for GDB C expression evaluation.

%package -n libgccjit
Summary: Library for embedding GCC inside programs and libraries
Requires: gcc = %{version}-%{release}

%description -n libgccjit
This package contains shared library with GCC JIT front-end.

%package -n libgccjit-devel
Summary: Support for embedding GCC inside programs and libraries
%if 0%{?fedora} > 27 || 0%{?rhel} > 7
BuildRequires: python3-sphinx
%else
BuildRequires: python-sphinx
%endif
Requires: libgccjit = %{version}-%{release}

%description -n libgccjit-devel
This package contains header files and documentation for GCC JIT front-end.

%package -n libquadmath
Summary: GCC __float128 shared support library

%description -n libquadmath
This package contains GCC shared support library which is needed
for __float128 math support and for Fortran REAL*16 support.

%package -n libquadmath-devel
Summary: GCC __float128 support
Requires: libquadmath = %{version}-%{release}
Requires: gcc = %{version}-%{release}

%description -n libquadmath-devel
This package contains headers for building Fortran programs using
REAL*16 and programs using __float128 math.

%package -n libquadmath-static
Summary: Static libraries for __float128 support
Requires: libquadmath-devel = %{version}-%{release}

%description -n libquadmath-static
This package contains static libraries for building Fortran programs
using REAL*16 and programs using __float128 math.

%package -n libitm
Summary: The GNU Transactional Memory library

%description -n libitm
This package contains the GNU Transactional Memory library
which is a GCC transactional memory support runtime library.

%package -n libitm-devel
Summary: The GNU Transactional Memory support
Requires: libitm = %{version}-%{release}
Requires: gcc = %{version}-%{release}

%description -n libitm-devel
This package contains headers and support files for the
GNU Transactional Memory library.

%package -n libitm-static
Summary: The GNU Transactional Memory static library
Requires: libitm-devel = %{version}-%{release}

%description -n libitm-static
This package contains GNU Transactional Memory static libraries.

%package -n libatomic
Summary: The GNU Atomic library

%description -n libatomic
This package contains the GNU Atomic library
which is a GCC support runtime library for atomic operations not supported
by hardware.

%package -n libatomic-static
Summary: The GNU Atomic static library
Requires: libatomic = %{version}-%{release}

%description -n libatomic-static
This package contains GNU Atomic static libraries.

%package -n libasan
Summary: The Address Sanitizer runtime library

%description -n libasan
This package contains the Address Sanitizer library
which is used for -fsanitize=address instrumented programs.

%package -n libasan-static
Summary: The Address Sanitizer static library
Requires: libasan = %{version}-%{release}

%description -n libasan-static
This package contains Address Sanitizer static runtime library.

%package -n libtsan
Summary: The Thread Sanitizer runtime library

%description -n libtsan
This package contains the Thread Sanitizer library
which is used for -fsanitize=thread instrumented programs.

%package -n libtsan-static
Summary: The Thread Sanitizer static library
Requires: libtsan = %{version}-%{release}

%description -n libtsan-static
This package contains Thread Sanitizer static runtime library.

%package -n libubsan
Summary: The Undefined Behavior Sanitizer runtime library

%description -n libubsan
This package contains the Undefined Behavior Sanitizer library
which is used for -fsanitize=undefined instrumented programs.

%package -n libubsan-static
Summary: The Undefined Behavior Sanitizer static library
Requires: libubsan = %{version}-%{release}

%description -n libubsan-static
This package contains Undefined Behavior Sanitizer static runtime library.

%package -n liblsan
Summary: The Leak Sanitizer runtime library

%description -n liblsan
This package contains the Leak Sanitizer library
which is used for -fsanitize=leak instrumented programs.

%package -n liblsan-static
Summary: The Leak Sanitizer static library
Requires: liblsan = %{version}-%{release}

%description -n liblsan-static
This package contains Leak Sanitizer static runtime library.

%package -n cpp
Summary: The C Preprocessor
Requires: filesystem >= 3
Provides: /lib/cpp
Autoreq: true

%description -n cpp
Cpp is the GNU C-Compatible Compiler Preprocessor.
Cpp is a macro processor which is used automatically
by the C compiler to transform your program before actual
compilation. It is called a macro processor because it allows
you to define macros, abbreviations for longer
constructs.

The C preprocessor provides four separate functionalities: the
inclusion of header files (files of declarations that can be
substituted into your program); macro expansion (you can define macros,
and the C preprocessor will replace the macros with their definitions
throughout the program); conditional compilation (using special
preprocessing directives, you can include or exclude parts of the
program according to various conditions); and line control (if you use
a program to combine or rearrange source files into an intermediate
file which is then compiled, you can use line control to inform the
compiler about where each source line originated).

You should install this package if you are a C programmer and you use
macros.

%package gnat
Summary: Ada 83, 95, 2005 and 2012 support for GCC
Requires: gcc = %{version}-%{release}
Requires: libgnat = %{version}-%{release}, libgnat-devel = %{version}-%{release}
Autoreq: true

%description gnat
GNAT is a GNU Ada 83, 95, 2005 and 2012 front-end to GCC. This package includes
development tools, the documents and Ada compiler.

%package -n libgnat
Summary: GNU Ada 83, 95, 2005 and 2012 runtime shared libraries
Autoreq: true

%description -n libgnat
GNAT is a GNU Ada 83, 95, 2005 and 2012 front-end to GCC. This package includes
shared libraries, which are required to run programs compiled with the GNAT.

%package -n libgnat-devel
Summary: GNU Ada 83, 95, 2005 and 2012 libraries
Autoreq: true

%description -n libgnat-devel
GNAT is a GNU Ada 83, 95, 2005 and 2012 front-end to GCC. This package includes
libraries, which are required to compile with the GNAT.

%package -n libgnat-static
Summary: GNU Ada 83, 95, 2005 and 2012 static libraries
Requires: libgnat-devel = %{version}-%{release}
Autoreq: true

%description -n libgnat-static
GNAT is a GNU Ada 83, 95, 2005 and 2012 front-end to GCC. This package includes
static libraries.

%package go
Summary: Go support
Requires: gcc = %{version}-%{release}
Requires: libgo = %{version}-%{release}
Requires: libgo-devel = %{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
Provides: gccgo = %{version}-%{release}
Autoreq: true

%description go
The gcc-go package provides support for compiling Go programs
with the GNU Compiler Collection.

%package -n libgo
Summary: Go runtime
Autoreq: true

%description -n libgo
This package contains Go shared library which is needed to run
Go dynamically linked programs.

%package -n libgo-devel
Summary: Go development libraries
Requires: libgo = %{version}-%{release}
Autoreq: true

%description -n libgo-devel
This package includes libraries and support files for compiling
Go programs.

%package -n libgo-static
Summary: Static Go libraries
Requires: libgo = %{version}-%{release}
Requires: gcc = %{version}-%{release}

%description -n libgo-static
This package contains static Go libraries.

%package plugin-devel
Summary: Support for compiling GCC plugins
Requires: gcc = %{version}-%{release}
Requires: gmp-devel >= 4.1.2-8, mpfr-devel >= 3.1.0, libmpc-devel >= 0.8.1

%description plugin-devel
This package contains header files and other support files
for compiling GCC plugins.  The GCC plugin ABI is currently
not stable, so plugins must be rebuilt any time GCC is updated.

%package offload-nvptx
Summary: Offloading compiler to NVPTX
Requires: gcc = %{version}-%{release}
Requires: libgomp-offload-nvptx = %{version}-%{release}

%description offload-nvptx
The gcc-offload-nvptx package provides offloading support for
NVidia PTX.  OpenMP and OpenACC programs linked with -fopenmp will
by default add PTX code into the binaries, which can be offloaded
to NVidia PTX capable devices if available.

%package plugin-annobin
Summary: The annobin plugin for gcc, built by the installed version of gcc
Requires: gcc = %{version}-%{release}
# Starting with release 10.01 annobin fixed a bug in its configure scripts
# which prevented them from working with a built but not installed compiler
BuildRequires: annobin >= 10.01
# Starting with release  9.93 annobin-plugin-gcc puts a copy of the sources
# in /usr/src/annobin
# FIXME: Currently the annobin-plugin-gcc subpackage only exists in Fedora.
# For RHEL-9 the annobin package does everything.
# BuildRequires: annobin-plugin-gcc
# Needed in order to be able to decompress the annobin source tarball.
BuildRequires: xz

%description plugin-annobin
This package adds a version of the annobin plugin for gcc.  This version
of the plugin is explicitly built by the same version of gcc that is installed
so that there cannot be any synchronization problems.

%prep
%setup -q -n gcc-%{version}-%{DATE} -a 1 -a 2 -a 3
%patch0 -p0 -b .hack~
%patch2 -p0 -b .sparc-config-detection~
%patch3 -p0 -b .libgomp-omp_h-multilib~
%patch4 -p0 -b .libtool-no-rpath~
%if %{build_isl}
%patch5 -p0 -b .isl-dl~
%patch6 -p0 -b .isl-dl2~
%endif
%if %{build_libstdcxx_docs}
%patch7 -p0 -b .libstdc++-docs~
%endif
%patch8 -p0 -b .no-add-needed~
%patch9 -p0 -b .foffload-default~
%patch10 -p0 -b .Wno-format-security~
%if 0%{?fedora} >= 29 || 0%{?rhel} > 7
%patch11 -p0 -b .rh1574936~
%endif
%patch12 -p0 -b .d-shared-libphobos~
%patch14 -p0 -b .libgcc-link~
%patch15 -p0 -b .pr101786~
%patch16 -p0 -b .stringify-__VA_OPT__~
%patch17 -p0 -b .stringify-__VA_OPT__-2~
%patch18 -p1 -b .bidi~
%patch19 -p1 -b .ice~
%patch20 -p1 -b .pch~
%patch21 -p1 -b .dejagnu-multiline~
%patch23 -p1 -b .pie~
%patch24 -p1 -b .now~
%patch25 -p0 -b .pr105331~
%patch26 -p1 -b .rh2106262~

%if 0%{?rhel} >= 9
%patch100 -p1 -b .fortran-fdec-duplicates~
%patch101 -p1 -b .fortran-flogical-as-integer~
%patch102 -p1 -b .fortran-fdec-ichar~
%patch103 -p1 -b .fortran-fdec-non-integer-index~
%patch104 -p1 -b .fortran-fdec-old-init~
%patch105 -p1 -b .fortran-fdec-override-kind~
%patch106 -p1 -b .fortran-fdec-non-logical-if~
%patch107 -p1 -b .fortran-fdec-promotion~
%patch108 -p1 -b .fortran-fdec-sequence~
%patch109 -p1 -b .fortran-fdec-add-missing-indexes~
%endif

%ifarch %{arm}
rm -f gcc/testsuite/go.test/test/fixedbugs/issue19182.go
%endif

echo 'Red Hat %{version}-%{gcc_release}' > gcc/DEV-PHASE

cp -a libstdc++-v3/config/cpu/i{4,3}86/atomicity.h

./contrib/gcc_update --touch

LC_ALL=C sed -i -e 's/\xa0/ /' gcc/doc/options.texi

sed -i -e 's/Common Driver Var(flag_report_bug)/& Init(1)/' gcc/common.opt

%ifarch ppc
if [ -d libstdc++-v3/config/abi/post/powerpc64-linux-gnu ]; then
  mkdir -p libstdc++-v3/config/abi/post/powerpc64-linux-gnu/64
  mv libstdc++-v3/config/abi/post/powerpc64-linux-gnu/{,64/}baseline_symbols.txt
  mv libstdc++-v3/config/abi/post/powerpc64-linux-gnu/{32/,}baseline_symbols.txt
  rm -rf libstdc++-v3/config/abi/post/powerpc64-linux-gnu/32
fi
%endif
%ifarch sparc
if [ -d libstdc++-v3/config/abi/post/sparc64-linux-gnu ]; then
  mkdir -p libstdc++-v3/config/abi/post/sparc64-linux-gnu/64
  mv libstdc++-v3/config/abi/post/sparc64-linux-gnu/{,64/}baseline_symbols.txt
  mv libstdc++-v3/config/abi/post/sparc64-linux-gnu/{32/,}baseline_symbols.txt
  rm -rf libstdc++-v3/config/abi/post/sparc64-linux-gnu/32
fi
%endif

# This test causes fork failures, because it spawns way too many threads
rm -f gcc/testsuite/go.test/test/chan/goroutines.go

# This test fails randomly.
%ifarch ppc64le
rm -f libstdc++-v3/testsuite/30_threads/future/members/poll.cc
%endif

%build

# Undo the broken autoconf change in recent Fedora versions
export CONFIG_SITE=NONE

CC=gcc
CXX=g++
OPT_FLAGS=`echo %{optflags}|sed -e 's/\(-Wp,\)\?-D_FORTIFY_SOURCE=[12]//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-flto=auto//g;s/-flto//g;s/-ffat-lto-objects//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-m64//g;s/-m32//g;s/-m31//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-mfpmath=sse/-mfpmath=sse -msse2/g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/ -pipe / /g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-Werror=format-security/-Wformat-security/g'`
%ifarch sparc
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-mcpu=ultrasparc/-mtune=ultrasparc/g;s/-mcpu=v[78]//g'`
%endif
%ifarch %{ix86}
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-march=i.86//g'`
%endif
OPT_FLAGS=`echo "$OPT_FLAGS" | sed -e 's/[[:blank:]]\+/ /g'`
case "$OPT_FLAGS" in
  *-fasynchronous-unwind-tables*)
    sed -i -e 's/-fno-exceptions /-fno-exceptions -fno-asynchronous-unwind-tables /' \
      libgcc/Makefile.in
    ;;
esac

%if %{build_offload_nvptx}
mkdir obji
IROOT=`pwd`/obji
cd nvptx-tools-%{nvptx_tools_gitrev}
rm -rf obj-%{gcc_target_platform}
mkdir obj-%{gcc_target_platform}
cd obj-%{gcc_target_platform}
CC="$CC" CXX="$CXX" CFLAGS="%{optflags} -fPIE" CXXFLAGS="%{optflags} -fPIE" LDFLAGS="-pie -Wl,-z,now" \
../configure --prefix=%{_prefix}
make %{?_smp_mflags}
make install prefix=${IROOT}%{_prefix}
cd ../..

ln -sf newlib-cygwin-%{newlib_cygwin_gitrev}/newlib newlib
rm -rf obj-offload-nvptx-none
mkdir obj-offload-nvptx-none

cd obj-offload-nvptx-none
CC="$CC" CXX="$CXX" CFLAGS="$OPT_FLAGS" \
	CXXFLAGS="`echo " $OPT_FLAGS " | sed 's/ -Wall / /g;s/ -fexceptions / /g' \
		  | sed 's/ -Wformat-security / -Wformat -Wformat-security /'`" \
	XCFLAGS="$OPT_FLAGS" TCFLAGS="$OPT_FLAGS" \
	../configure --disable-bootstrap --disable-sjlj-exceptions \
	--enable-newlib-io-long-long --with-build-time-tools=${IROOT}%{_prefix}/nvptx-none/bin \
	--target nvptx-none --enable-as-accelerator-for=%{gcc_target_platform} \
	--enable-languages=c,c++,fortran,lto \
	--prefix=%{_prefix} --mandir=%{_mandir} --infodir=%{_infodir} \
	--with-bugurl=http://bugzilla.redhat.com/bugzilla \
	--enable-checking=release --with-system-zlib \
	--with-gcc-major-version-only --without-isl --enable-host-pie --enable-host-bind-now
make %{?_smp_mflags}
cd ..
rm -f newlib
%endif

rm -rf obj-%{gcc_target_platform}
mkdir obj-%{gcc_target_platform}
cd obj-%{gcc_target_platform}

%if %{build_isl}
mkdir isl-build isl-install
%ifarch s390 s390x
ISL_FLAG_PIC=-fPIC
%else
ISL_FLAG_PIC=-fpic
%endif
cd isl-build
sed -i 's|libisl|libgcc11privateisl|g' \
  ../../isl-%{isl_version}/Makefile.{am,in}
../../isl-%{isl_version}/configure \
  CC=/usr/bin/gcc CXX=/usr/bin/g++ \
  CFLAGS="${CFLAGS:-%optflags} $ISL_FLAG_PIC" --prefix=`cd ..; pwd`/isl-install
make %{?_smp_mflags}
make install
cd ../isl-install/lib
rm libgcc11privateisl.so{,.15}
mv libgcc11privateisl.so.15.3.0 libisl.so.15
ln -sf libisl.so.15 libisl.so
cd ../..
%endif

enablelgo=
enablelada=
enablelobjc=
enableld=
%if %{build_objc}
enablelobjc=,objc,obj-c++
%endif
%if %{build_ada}
enablelada=,ada
%endif
%if %{build_go}
enablelgo=,go
%endif
%if %{build_d}
enableld=,d
%endif
CONFIGURE_OPTS="\
	--prefix=%{_prefix} --mandir=%{_mandir} --infodir=%{_infodir} \
	--with-bugurl=http://bugzilla.redhat.com/bugzilla \
	--enable-shared --enable-threads=posix --enable-checking=release \
%ifarch ppc64le
	--enable-targets=powerpcle-linux \
%endif
%ifarch ppc64le %{mips} s390x
%ifarch s390x
%if 0%{?fedora} < 32 && 0%{?rhel} < 8
	--enable-multilib \
%else
	--disable-multilib \
%endif
%else
	--disable-multilib \
%endif
%else
	--enable-multilib \
%endif
	--with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions \
	--enable-gnu-unique-object --enable-linker-build-id --with-gcc-major-version-only \
%ifnarch %{mips}
	--with-linker-hash-style=gnu \
%endif
	--enable-plugin --enable-initfini-array \
%if %{build_isl}
	--with-isl=`pwd`/isl-install \
%else
	--without-isl \
%endif
%if %{build_offload_nvptx}
	--enable-offload-targets=nvptx-none \
	--without-cuda-driver \
%endif
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7
%if %{attr_ifunc}
	--enable-gnu-indirect-function \
%endif
%endif
%ifarch %{arm}
	--disable-sjlj-exceptions \
%endif
%ifarch ppc ppc64 ppc64le ppc64p7
	--enable-secureplt \
%endif
%ifarch sparc sparcv9 sparc64 ppc ppc64 ppc64le ppc64p7 s390 s390x alpha
	--with-long-double-128 \
%endif
%ifarch sparc
	--disable-linux-futex \
%endif
%ifarch sparc64
	--with-cpu=ultrasparc \
%endif
%ifarch sparc sparcv9
	--host=%{gcc_target_platform} --build=%{gcc_target_platform} --target=%{gcc_target_platform} --with-cpu=v7
%endif
%ifarch ppc ppc64 ppc64p7
%if 0%{?rhel} >= 7
	--with-cpu-32=power7 --with-tune-32=power7 --with-cpu-64=power7 --with-tune-64=power7 \
%endif
%if 0%{?rhel} == 6
	--with-cpu-32=power4 --with-tune-32=power6 --with-cpu-64=power4 --with-tune-64=power6 \
%endif
%endif
%ifarch ppc64le
%if 0%{?rhel} == 9
	--with-cpu-32=power9 --with-tune-32=power9 --with-cpu-64=power9 --with-tune-64=power9 \
%else
	--with-cpu-32=power8 --with-tune-32=power8 --with-cpu-64=power8 --with-tune-64=power8 \
%endif
%endif
%ifarch ppc
	--build=%{gcc_target_platform} --target=%{gcc_target_platform} --with-cpu=default32
%endif
%ifarch %{ix86} x86_64
	--enable-cet \
	--with-tune=generic \
%endif
%if 0%{?rhel} >= 7
%ifarch %{ix86}
	--with-arch=x86-64 \
%endif
%ifarch x86_64
%if 0%{?rhel} > 8
	--with-arch_64=x86-64-v2 \
%endif
	--with-arch_32=x86-64 \
%endif
%else
%ifarch %{ix86}
	--with-arch=i686 \
%endif
%ifarch x86_64
	--with-arch_32=i686 \
%endif
%endif
%ifarch s390 s390x
%if 0%{?rhel} >= 7
%if 0%{?rhel} > 7
%if 0%{?rhel} > 8
%if 0%{?rhel} == 9
	--with-arch=z14 --with-tune=z15 \
%else
	--with-arch=z13 --with-tune=arch13 \
%endif
%else
	--with-arch=z13 --with-tune=z14 \
%endif
%else
	--with-arch=z196 --with-tune=zEC12 \
%endif
%else
%if 0%{?fedora} >= 26
	--with-arch=zEC12 --with-tune=z13 \
%else
	--with-arch=z9-109 --with-tune=z10 \
%endif
%endif
	--enable-decimal-float \
%endif
%ifarch armv7hl
	--with-tune=generic-armv7-a --with-arch=armv7-a \
	--with-float=hard --with-fpu=vfpv3-d16 --with-abi=aapcs-linux \
%endif
%ifarch mips mipsel
	--with-arch=mips32r2 --with-fp-32=xx \
%endif
%ifarch mips64 mips64el
	--with-arch=mips64r2 --with-abi=64 \
%endif
%ifarch riscv64
	--with-arch=rv64gc --with-abi=lp64d --with-multilib-list=lp64d \
%endif
%ifnarch sparc sparcv9 ppc
	--build=%{gcc_target_platform} \
%endif
%if 0%{?fedora} >= 35 || 0%{?rhel} >= 9
%ifnarch %{arm}
	--with-build-config=bootstrap-lto --enable-link-serialization=1 \
%endif
%endif
	"

CC="$CC" CXX="$CXX" CFLAGS="$OPT_FLAGS" \
	CXXFLAGS="`echo " $OPT_FLAGS " | sed 's/ -Wall / /g;s/ -fexceptions / /g' \
		  | sed 's/ -Wformat-security / -Wformat -Wformat-security /'`" \
	XCFLAGS="$OPT_FLAGS" TCFLAGS="$OPT_FLAGS" \
	../configure --enable-bootstrap --enable-host-pie --enable-host-bind-now \
	--enable-languages=c,c++,fortran${enablelobjc}${enablelada}${enablelgo}${enableld},lto \
	$CONFIGURE_OPTS

%ifarch sparc sparcv9 sparc64
make %{?_smp_mflags} BOOT_CFLAGS="$OPT_FLAGS" LDFLAGS_FOR_TARGET=-Wl,-z,relro,-z,now bootstrap
%else
make %{?_smp_mflags} BOOT_CFLAGS="$OPT_FLAGS" LDFLAGS_FOR_TARGET=-Wl,-z,relro,-z,now profiledbootstrap
%endif

CC="`%{gcc_target_platform}/libstdc++-v3/scripts/testsuite_flags --build-cc`"
CXX="`%{gcc_target_platform}/libstdc++-v3/scripts/testsuite_flags --build-cxx` `%{gcc_target_platform}/libstdc++-v3/scripts/testsuite_flags --build-includes`"

# Build libgccjit separately, so that normal compiler binaries aren't -fpic
# unnecessarily.
mkdir objlibgccjit
cd objlibgccjit
CC="$CC" CXX="$CXX" CFLAGS="$OPT_FLAGS" \
	CXXFLAGS="`echo " $OPT_FLAGS " | sed 's/ -Wall / /g;s/ -fexceptions / /g' \
		  | sed 's/ -Wformat-security / -Wformat -Wformat-security /'`" \
	XCFLAGS="$OPT_FLAGS" TCFLAGS="$OPT_FLAGS" \
	../../configure --disable-bootstrap --enable-host-shared  --enable-host-bind-now \
	--enable-languages=jit $CONFIGURE_OPTS
make %{?_smp_mflags} BOOT_CFLAGS="$OPT_FLAGS" all-gcc
cp -a gcc/libgccjit.so* ../gcc/
cd ../gcc/
ln -sf xgcc %{gcc_target_platform}-gcc-%{gcc_major}
cp -a Makefile{,.orig}
sed -i -e '/^CHECK_TARGETS/s/$/ check-jit/' Makefile
touch -r Makefile.orig Makefile
rm Makefile.orig
make jit.sphinx.html
make jit.sphinx.install-html jit_htmldir=`pwd`/../../rpm.doc/libgccjit-devel/html
cd ..

%if %{build_isl}
cp -a isl-install/lib/libisl.so.15 gcc/
%endif

# Make generated man pages even if Pod::Man is not new enough
perl -pi -e 's/head3/head2/' ../contrib/texi2pod.pl
for i in ../gcc/doc/*.texi; do
  cp -a $i $i.orig; sed 's/ftable/table/' $i.orig > $i
done
make -C gcc generated-manpages
for i in ../gcc/doc/*.texi; do mv -f $i.orig $i; done

# Make generated doxygen pages.
%if %{build_libstdcxx_docs}
cd %{gcc_target_platform}/libstdc++-v3
make doc-html-doxygen
make doc-man-doxygen
cd ../..
%endif

# Copy various doc files here and there
cd ..
mkdir -p rpm.doc/gfortran rpm.doc/objc rpm.doc/gdc rpm.doc/libphobos
mkdir -p rpm.doc/go rpm.doc/libgo rpm.doc/libquadmath rpm.doc/libitm
mkdir -p rpm.doc/changelogs/{gcc/cp,gcc/ada,gcc/jit,libstdc++-v3,libobjc,libgomp,libcc1,libatomic,libsanitizer}

for i in {gcc,gcc/cp,gcc/ada,gcc/jit,libstdc++-v3,libobjc,libgomp,libcc1,libatomic,libsanitizer}/ChangeLog*; do
	cp -p $i rpm.doc/changelogs/$i
done

(cd gcc/fortran; for i in ChangeLog*; do
	cp -p $i ../../rpm.doc/gfortran/$i
done)
(cd libgfortran; for i in ChangeLog*; do
	cp -p $i ../rpm.doc/gfortran/$i.libgfortran
done)
%if %{build_objc}
(cd libobjc; for i in README*; do
	cp -p $i ../rpm.doc/objc/$i.libobjc
done)
%endif
%if %{build_d}
(cd gcc/d; for i in ChangeLog*; do
	cp -p $i ../../rpm.doc/gdc/$i.gdc
done)
(cd libphobos; for i in ChangeLog*; do
	cp -p $i ../rpm.doc/libphobos/$i.libphobos
done
cp -a src/LICENSE*.txt libdruntime/LICENSE ../rpm.doc/libphobos/)
%endif
%if %{build_libquadmath}
(cd libquadmath; for i in ChangeLog* COPYING.LIB; do
	cp -p $i ../rpm.doc/libquadmath/$i.libquadmath
done)
%endif
%if %{build_libitm}
(cd libitm; for i in ChangeLog*; do
	cp -p $i ../rpm.doc/libitm/$i.libitm
done)
%endif
%if %{build_go}
(cd gcc/go; for i in README* ChangeLog*; do
	cp -p $i ../../rpm.doc/go/$i
done)
(cd libgo; for i in LICENSE* PATENTS* README; do
	cp -p $i ../rpm.doc/libgo/$i.libgo
done)
%endif

rm -f rpm.doc/changelogs/gcc/ChangeLog.[1-9]
find rpm.doc -name \*ChangeLog\* | xargs bzip2 -9

# Get the annobin sources.  Note these are not added to the rpm as SOURCE4
# because if they were the build phase would try to include them as part of
# gcc itself, and this causes problems.  Instead we locate the sources in
# the buildroot.  They should have been put there when annobin was installed.

pushd %{_builddir}

%global annobin_source_dir %{_usrsrc}/annobin

if [ -d %{annobin_source_dir} ]
then
    # Unpack the sources.
    echo "Unpacking annobin sources"
    rm -fr annobin-*
    tar xvf %{annobin_source_dir}/latest-annobin.tar.xz

    # Setting this as a local symbol because using %%global does not appear to work.
    annobin_dir=$(find . -maxdepth 1 -type d -name "annobin*")

    # Now build the annobin plugin using the just built compiler.
    echo "annobin directory = ${annobin_dir}"
    cd ${annobin_dir}

    # Work out where this version of gcc stores its plugins.
%global ANNOBIN_GCC_PLUGIN_DIR  %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin

    CONFIG_ARGS="--quiet"
    CONFIG_ARGS="$CONFIG_ARGS --with-gcc-plugin-dir=%{ANNOBIN_GCC_PLUGIN_DIR}"
    CONFIG_ARGS="$CONFIG_ARGS --without-annocheck"
    CONFIG_ARGS="$CONFIG_ARGS --without-tests"
    CONFIG_ARGS="$CONFIG_ARGS --disable-rpath"

    comp_dir="%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/gcc/"
    ccompiler="%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/gcc/xgcc -B $comp_dir"
    cxxcompiler="%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/gcc/xg++ -B $comp_dir"

    comp_flags="%build_cflags"
    comp_flags="$comp_flags -I %{_builddir}/gcc-%{version}-%{DATE}/gcc"
    comp_flags="$comp_flags -I %{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/gcc/"
    comp_flags="$comp_flags -I %{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/%{gcc_target_platform}/libstdc++-v3/include"
    comp_flags="$comp_flags -I %{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/%{gcc_target_platform}/libstdc++-v3/include/%{gcc_target_platform}"
    comp_flags="$comp_flags -I %{_builddir}/gcc-%{version}-%{DATE}/libstdc++-v3/libsupc++"
    comp_flags="$comp_flags -I %{_builddir}/gcc-%{version}-%{DATE}/include"
    comp_flags="$comp_flags -I %{_builddir}/gcc-%{version}-%{DATE}/libcpp/include"

    ld_flags="%build_ldflags"
    ld_flags="$ld_flags -L%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/libstdc++-v3/.libs"
    ld_flags="$ld_flags -L%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/%{gcc_target_platform}/libstdc++-v3/.libs"
    ld_flags="$ld_flags -L%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/%{gcc_target_platform}/libstdc++-v3/src/.libs"
    ld_flags="$ld_flags -L%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/libstdc++-v3/libsupc++/.libs"
    ld_flags="$ld_flags -L%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/%{gcc_target_platform}/libstdc++-v3/libsupc++/.libs"
    ld_flags="$ld_flags -L%{_builddir}/gcc-%{version}-%{DATE}/obj-%{gcc_target_platform}/%{gcc_target_platform}/libgcc/.libs"

    # libtool works with CFLAGS but ignores LDFLAGS, so we have to combine them.
    comp_flags="$comp_flags $ld_flags"

    echo "Configuring the annobin plugin"
    CC="${ccompiler}" CFLAGS="${comp_flags}" \
      CXX="${cxxcompiler}" CXXFLAGS="${comp_flags}" \
      LDFLAGS="${ld_flags}" \
      ./configure ${CONFIG_ARGS}  || cat config.log

    echo "Building the annobin plugin"
    make

    echo "Annobin plugin build complete"
else
    echo "Unable to locate annobin sources (expected to find: %{annobin_source_dir}/latest-annobin.tar.xz)"
    echo "These should be provided by installing the annobin package"
    exit 1
fi
popd

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# RISC-V ABI wants to install everything in /lib64/lp64d or /usr/lib64/lp64d.
# Make these be symlinks to /lib64 or /usr/lib64 respectively. See:
# https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/thread/DRHT5YTPK4WWVGL3GIN5BF2IKX2ODHZ3/
%ifarch riscv64
for d in %{buildroot}%{_libdir} %{buildroot}/%{_lib} \
	  %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib} \
	  %{buildroot}%{_prefix}/include/c++/%{gcc_major}/%{gcc_target_platform}/%{_lib}; do
  mkdir -p $d
  (cd $d && ln -sf . lp64d)
done
%endif

%if %{build_offload_nvptx}
cd nvptx-tools-%{nvptx_tools_gitrev}
cd obj-%{gcc_target_platform}
make install prefix=%{buildroot}%{_prefix}
cd ../..

ln -sf newlib-cygwin-%{newlib_cygwin_gitrev}/newlib newlib
cd obj-offload-nvptx-none
make prefix=%{buildroot}%{_prefix} mandir=%{buildroot}%{_mandir} \
  infodir=%{buildroot}%{_infodir} install
rm -rf %{buildroot}%{_prefix}/libexec/gcc/nvptx-none/%{gcc_major}/install-tools
rm -rf %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none/{install-tools,plugin,cc1,cc1plus,f951}
rm -rf %{buildroot}%{_infodir} %{buildroot}%{_mandir}/man7 %{buildroot}%{_prefix}/share/locale
rm -rf %{buildroot}%{_prefix}/lib/gcc/nvptx-none/%{gcc_major}/{install-tools,plugin}
rm -rf %{buildroot}%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none/{install-tools,plugin,include-fixed}
rm -rf %{buildroot}%{_prefix}/%{_lib}/libc[cp]1*
mv -f %{buildroot}%{_prefix}/nvptx-none/lib/*.{a,spec} %{buildroot}%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none/
mv -f %{buildroot}%{_prefix}/nvptx-none/lib/mgomp/*.{a,spec} %{buildroot}%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none/mgomp/
mv -f %{buildroot}%{_prefix}/lib/gcc/nvptx-none/%{gcc_major}/*.a %{buildroot}%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none/
mv -f %{buildroot}%{_prefix}/lib/gcc/nvptx-none/%{gcc_major}/mgomp/*.a %{buildroot}%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none/mgomp/
find %{buildroot}%{_prefix}/lib/gcc/nvptx-none %{buildroot}%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none \
     %{buildroot}%{_prefix}/nvptx-none/lib -name \*.la | xargs rm
cd ..
rm -f newlib
%endif

cd obj-%{gcc_target_platform}

TARGET_PLATFORM=%{gcc_target_platform}

# There are some MP bugs in libstdc++ Makefiles
make -C %{gcc_target_platform}/libstdc++-v3

make prefix=%{buildroot}%{_prefix} mandir=%{buildroot}%{_mandir} \
  infodir=%{buildroot}%{_infodir} install
%if %{build_ada}
chmod 644 %{buildroot}%{_infodir}/gnat*
%endif

FULLPATH=%{buildroot}%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
FULLEPATH=%{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}

%if %{build_isl}
cp -a isl-install/lib/libisl.so.15 $FULLPATH/
%endif

# fix some things
ln -sf gcc %{buildroot}%{_prefix}/bin/cc
rm -f %{buildroot}%{_prefix}/lib/cpp
ln -sf ../bin/cpp %{buildroot}/%{_prefix}/lib/cpp
ln -sf gfortran %{buildroot}%{_prefix}/bin/f95
rm -f %{buildroot}%{_infodir}/dir
gzip -9 %{buildroot}%{_infodir}/*.info*
ln -sf gcc %{buildroot}%{_prefix}/bin/gnatgcc
mkdir -p %{buildroot}%{_fmoddir}

%if %{build_go}
mv %{buildroot}%{_prefix}/bin/go{,.gcc}
mv %{buildroot}%{_prefix}/bin/gofmt{,.gcc}
ln -sf /etc/alternatives/go %{buildroot}%{_prefix}/bin/go
ln -sf /etc/alternatives/gofmt %{buildroot}%{_prefix}/bin/gofmt
%endif

cxxconfig="`find %{gcc_target_platform}/libstdc++-v3/include -name c++config.h`"
for i in `find %{gcc_target_platform}/[36]*/libstdc++-v3/include -name c++config.h 2>/dev/null`; do
  if ! diff -up $cxxconfig $i; then
    cat > %{buildroot}%{_prefix}/include/c++/%{gcc_major}/%{gcc_target_platform}/bits/c++config.h <<EOF
#ifndef _CPP_CPPCONFIG_WRAPPER
#define _CPP_CPPCONFIG_WRAPPER 1
#include <bits/wordsize.h>
#if __WORDSIZE == 32
%ifarch %{multilib_64_archs}
`cat $(find %{gcc_target_platform}/32/libstdc++-v3/include -name c++config.h)`
%else
`cat $(find %{gcc_target_platform}/libstdc++-v3/include -name c++config.h)`
%endif
#else
%ifarch %{multilib_64_archs}
`cat $(find %{gcc_target_platform}/libstdc++-v3/include -name c++config.h)`
%else
`cat $(find %{gcc_target_platform}/64/libstdc++-v3/include -name c++config.h)`
%endif
#endif
#endif
EOF
    break
  fi
done

for f in `find %{buildroot}%{_prefix}/include/c++/%{gcc_major}/%{gcc_target_platform}/ -name c++config.h`; do
  for i in 1 2 4 8; do
    sed -i -e 's/#define _GLIBCXX_ATOMIC_BUILTINS_'$i' 1/#ifdef __GCC_HAVE_SYNC_COMPARE_AND_SWAP_'$i'\
&\
#endif/' $f
  done
done

# Nuke bits/*.h.gch dirs
# 1) there is no bits/*.h header installed, so when gch file can't be
#    used, compilation fails
# 2) sometimes it is hard to match the exact options used for building
#    libstdc++-v3 or they aren't desirable
# 3) there are multilib issues, conflicts etc. with this
# 4) it is huge
# People can always precompile on their own whatever they want, but
# shipping this for everybody is unnecessary.
rm -rf %{buildroot}%{_prefix}/include/c++/%{gcc_major}/%{gcc_target_platform}/bits/*.h.gch

%if %{build_libstdcxx_docs}
libstdcxx_doc_builddir=%{gcc_target_platform}/libstdc++-v3/doc/doxygen
mkdir -p ../rpm.doc/libstdc++-v3
cp -r -p ../libstdc++-v3/doc/html ../rpm.doc/libstdc++-v3/html
cp -r -p $libstdcxx_doc_builddir/html ../rpm.doc/libstdc++-v3/html/api
mkdir -p %{buildroot}%{_mandir}/man3
cp -r -p $libstdcxx_doc_builddir/man/man3/* %{buildroot}%{_mandir}/man3/
find ../rpm.doc/libstdc++-v3 -name \*~ | xargs rm
%endif

%ifarch sparcv9 sparc64
ln -f %{buildroot}%{_prefix}/bin/%{gcc_target_platform}-gcc \
  %{buildroot}%{_prefix}/bin/sparc-%{_vendor}-%{_target_os}-gcc
%endif
%ifarch ppc ppc64 ppc64p7
ln -f %{buildroot}%{_prefix}/bin/%{gcc_target_platform}-gcc \
  %{buildroot}%{_prefix}/bin/ppc-%{_vendor}-%{_target_os}-gcc
%endif

FULLLSUBDIR=
%ifarch sparcv9 ppc
FULLLSUBDIR=lib32
%endif
%ifarch sparc64 ppc64 ppc64p7
FULLLSUBDIR=lib64
%endif
if [ -n "$FULLLSUBDIR" ]; then
  FULLLPATH=$FULLPATH/$FULLLSUBDIR
  mkdir -p $FULLLPATH
else
  FULLLPATH=$FULLPATH
fi

find %{buildroot} -name \*.la | xargs rm -f

mv %{buildroot}%{_prefix}/%{_lib}/libgfortran.spec $FULLPATH/
%if %{build_d}
mv %{buildroot}%{_prefix}/%{_lib}/libgphobos.spec $FULLPATH/
%endif
%if %{build_libitm}
mv %{buildroot}%{_prefix}/%{_lib}/libitm.spec $FULLPATH/
%endif
%if %{build_libasan}
mv %{buildroot}%{_prefix}/%{_lib}/libsanitizer.spec $FULLPATH/
%endif

mkdir -p %{buildroot}/%{_lib}
mv -f %{buildroot}%{_prefix}/%{_lib}/libgcc_s.so.1 %{buildroot}/%{_lib}/libgcc_s-%{gcc_major}-%{DATE}.so.1
chmod 755 %{buildroot}/%{_lib}/libgcc_s-%{gcc_major}-%{DATE}.so.1
ln -sf libgcc_s-%{gcc_major}-%{DATE}.so.1 %{buildroot}/%{_lib}/libgcc_s.so.1
%ifarch %{ix86} x86_64 ppc ppc64 ppc64p7 ppc64le %{arm} aarch64 riscv64
rm -f $FULLPATH/libgcc_s.so
echo '/* GNU ld script
   Use the shared library, but some functions are only in
   the static library, so try that secondarily.  */
OUTPUT_FORMAT('`gcc -Wl,--print-output-format -nostdlib -r -o /dev/null`')
GROUP ( /%{_lib}/libgcc_s.so.1 libgcc.a )' > $FULLPATH/libgcc_s.so
%else
ln -sf /%{_lib}/libgcc_s.so.1 $FULLPATH/libgcc_s.so
%endif
%ifarch sparcv9 ppc
%ifarch ppc
rm -f $FULLPATH/64/libgcc_s.so
echo '/* GNU ld script
   Use the shared library, but some functions are only in
   the static library, so try that secondarily.  */
OUTPUT_FORMAT('`gcc -m64 -Wl,--print-output-format -nostdlib -r -o /dev/null`')
GROUP ( /lib64/libgcc_s.so.1 libgcc.a )' > $FULLPATH/64/libgcc_s.so
%else
ln -sf /lib64/libgcc_s.so.1 $FULLPATH/64/libgcc_s.so
%endif
%endif
%ifarch %{multilib_64_archs}
%ifarch x86_64 ppc64 ppc64p7
rm -f $FULLPATH/64/libgcc_s.so
echo '/* GNU ld script
   Use the shared library, but some functions are only in
   the static library, so try that secondarily.  */
OUTPUT_FORMAT('`gcc -m32 -Wl,--print-output-format -nostdlib -r -o /dev/null`')
GROUP ( /lib/libgcc_s.so.1 libgcc.a )' > $FULLPATH/32/libgcc_s.so
%else
ln -sf /lib/libgcc_s.so.1 $FULLPATH/32/libgcc_s.so
%endif
%endif

mv -f %{buildroot}%{_prefix}/%{_lib}/libgomp.spec $FULLPATH/

%if %{build_ada}
mv -f $FULLPATH/adalib/libgnarl-*.so %{buildroot}%{_prefix}/%{_lib}/
mv -f $FULLPATH/adalib/libgnat-*.so %{buildroot}%{_prefix}/%{_lib}/
rm -f $FULLPATH/adalib/libgnarl.so* $FULLPATH/adalib/libgnat.so*
%endif

mkdir -p %{buildroot}%{_prefix}/libexec/getconf
if gcc/xgcc -B gcc/ -E -P -dD -xc /dev/null | grep '__LONG_MAX__.*\(2147483647\|0x7fffffff\($\|[LU]\)\)'; then
  ln -sf POSIX_V6_ILP32_OFF32 %{buildroot}%{_prefix}/libexec/getconf/default
else
  ln -sf POSIX_V6_LP64_OFF64 %{buildroot}%{_prefix}/libexec/getconf/default
fi

mkdir -p %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++*gdb.py* \
      %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/
pushd ../libstdc++-v3/python
for i in `find . -name \*.py`; do
  touch -r $i %{buildroot}%{_prefix}/share/gcc-%{gcc_major}/python/$i
done
touch -r hook.in %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/libstdc++*gdb.py
popd
for f in `find %{buildroot}%{_prefix}/share/gcc-%{gcc_major}/python/ \
	       %{buildroot}%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/ -name \*.py`; do
  r=${f/$RPM_BUILD_ROOT/}
  %{__python3} -c 'import py_compile; py_compile.compile("'$f'", dfile="'$r'")'
  %{__python3} -O -c 'import py_compile; py_compile.compile("'$f'", dfile="'$r'")'
done

rm -f $FULLEPATH/libgccjit.so
cp -a objlibgccjit/gcc/libgccjit.so* %{buildroot}%{_prefix}/%{_lib}/
cp -a ../gcc/jit/libgccjit*.h %{buildroot}%{_prefix}/include/
/usr/bin/install -c -m 644 objlibgccjit/gcc/doc/libgccjit.info %{buildroot}/%{_infodir}/
gzip -9 %{buildroot}/%{_infodir}/libgccjit.info

pushd $FULLPATH
if [ "%{_lib}" = "lib" ]; then
%if %{build_objc}
ln -sf ../../../libobjc.so.4 libobjc.so
%endif
ln -sf ../../../libstdc++.so.6.*[0-9] libstdc++.so
ln -sf ../../../libgfortran.so.5.* libgfortran.so
ln -sf ../../../libgomp.so.1.* libgomp.so
%if %{build_go}
ln -sf ../../../libgo.so.19.* libgo.so
%endif
%if %{build_libquadmath}
ln -sf ../../../libquadmath.so.0.* libquadmath.so
%endif
%if %{build_d}
ln -sf ../../../libgdruntime.so.2.* libgdruntime.so
ln -sf ../../../libgphobos.so.2.* libgphobos.so
%endif
%if %{build_libitm}
ln -sf ../../../libitm.so.1.* libitm.so
%endif
%if %{build_libatomic}
ln -sf ../../../libatomic.so.1.* libatomic.so
%endif
%if %{build_libasan}
ln -sf ../../../libasan.so.6.* libasan.so
mv ../../../libasan_preinit.o libasan_preinit.o
%endif
%if %{build_libubsan}
ln -sf ../../../libubsan.so.1.* libubsan.so
%endif
else
%if %{build_objc}
ln -sf ../../../../%{_lib}/libobjc.so.4 libobjc.so
%endif
ln -sf ../../../../%{_lib}/libstdc++.so.6.*[0-9] libstdc++.so
ln -sf ../../../../%{_lib}/libgfortran.so.5.* libgfortran.so
ln -sf ../../../../%{_lib}/libgomp.so.1.* libgomp.so
%if %{build_go}
ln -sf ../../../../%{_lib}/libgo.so.19.* libgo.so
%endif
%if %{build_libquadmath}
ln -sf ../../../../%{_lib}/libquadmath.so.0.* libquadmath.so
%endif
%if %{build_d}
ln -sf ../../../../%{_lib}/libgdruntime.so.2.* libgdruntime.so
ln -sf ../../../../%{_lib}/libgphobos.so.2.* libgphobos.so
%endif
%if %{build_libitm}
ln -sf ../../../../%{_lib}/libitm.so.1.* libitm.so
%endif
%if %{build_libatomic}
ln -sf ../../../../%{_lib}/libatomic.so.1.* libatomic.so
%endif
%if %{build_libasan}
ln -sf ../../../../%{_lib}/libasan.so.6.* libasan.so
mv ../../../../%{_lib}/libasan_preinit.o libasan_preinit.o
%endif
%if %{build_libubsan}
ln -sf ../../../../%{_lib}/libubsan.so.1.* libubsan.so
%endif
%if %{build_libtsan}
rm -f libtsan.so
echo 'INPUT ( %{_prefix}/%{_lib}/'`echo ../../../../%{_lib}/libtsan.so.0.* | sed 's,^.*libt,libt,'`' )' > libtsan.so
mv ../../../../%{_lib}/libtsan_preinit.o libtsan_preinit.o
%endif
%if %{build_liblsan}
rm -f liblsan.so
echo 'INPUT ( %{_prefix}/%{_lib}/'`echo ../../../../%{_lib}/liblsan.so.0.* | sed 's,^.*libl,libl,'`' )' > liblsan.so
mv ../../../../%{_lib}/liblsan_preinit.o liblsan_preinit.o
%endif
fi
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libstdc++fs.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libsupc++.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libgfortran.*a $FULLLPATH/
%if %{build_objc}
mv -f %{buildroot}%{_prefix}/%{_lib}/libobjc.*a .
%endif
mv -f %{buildroot}%{_prefix}/%{_lib}/libgomp.*a .
%if %{build_libquadmath}
mv -f %{buildroot}%{_prefix}/%{_lib}/libquadmath.*a $FULLLPATH/
%endif
%if %{build_d}
mv -f %{buildroot}%{_prefix}/%{_lib}/libgdruntime.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libgphobos.*a $FULLLPATH/
%endif
%if %{build_libitm}
mv -f %{buildroot}%{_prefix}/%{_lib}/libitm.*a $FULLLPATH/
%endif
%if %{build_libatomic}
mv -f %{buildroot}%{_prefix}/%{_lib}/libatomic.*a $FULLLPATH/
%endif
%if %{build_libasan}
mv -f %{buildroot}%{_prefix}/%{_lib}/libasan.*a $FULLLPATH/
%endif
%if %{build_libubsan}
mv -f %{buildroot}%{_prefix}/%{_lib}/libubsan.*a $FULLLPATH/
%endif
%if %{build_libtsan}
mv -f %{buildroot}%{_prefix}/%{_lib}/libtsan.*a $FULLPATH/
%endif
%if %{build_liblsan}
mv -f %{buildroot}%{_prefix}/%{_lib}/liblsan.*a $FULLPATH/
%endif
%if %{build_go}
mv -f %{buildroot}%{_prefix}/%{_lib}/libgo.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libgobegin.*a $FULLLPATH/
mv -f %{buildroot}%{_prefix}/%{_lib}/libgolibbegin.*a $FULLLPATH/
%endif

%if %{build_ada}
%ifarch sparcv9 ppc
rm -rf $FULLPATH/64/ada{include,lib}
%endif
%ifarch %{multilib_64_archs}
rm -rf $FULLPATH/32/ada{include,lib}
%endif
if [ "$FULLPATH" != "$FULLLPATH" ]; then
mv -f $FULLPATH/ada{include,lib} $FULLLPATH/
pushd $FULLLPATH/adalib
if [ "%{_lib}" = "lib" ]; then
ln -sf ../../../../../libgnarl-*.so libgnarl.so
ln -sf ../../../../../libgnarl-*.so libgnarl-11.so
ln -sf ../../../../../libgnat-*.so libgnat.so
ln -sf ../../../../../libgnat-*.so libgnat-11.so
else
ln -sf ../../../../../../%{_lib}/libgnarl-*.so libgnarl.so
ln -sf ../../../../../../%{_lib}/libgnarl-*.so libgnarl-11.so
ln -sf ../../../../../../%{_lib}/libgnat-*.so libgnat.so
ln -sf ../../../../../../%{_lib}/libgnat-*.so libgnat-11.so
fi
popd
else
pushd $FULLPATH/adalib
if [ "%{_lib}" = "lib" ]; then
ln -sf ../../../../libgnarl-*.so libgnarl.so
ln -sf ../../../../libgnarl-*.so libgnarl-11.so
ln -sf ../../../../libgnat-*.so libgnat.so
ln -sf ../../../../libgnat-*.so libgnat-11.so
else
ln -sf ../../../../../%{_lib}/libgnarl-*.so libgnarl.so
ln -sf ../../../../../%{_lib}/libgnarl-*.so libgnarl-11.so
ln -sf ../../../../../%{_lib}/libgnat-*.so libgnat.so
ln -sf ../../../../../%{_lib}/libgnat-*.so libgnat-11.so
fi
popd
fi
%endif

%ifarch sparcv9 ppc
%if %{build_objc}
ln -sf ../../../../../lib64/libobjc.so.4 64/libobjc.so
%endif
ln -sf ../`echo ../../../../lib/libstdc++.so.6.*[0-9] | sed s~/lib/~/lib64/~` 64/libstdc++.so
ln -sf ../`echo ../../../../lib/libgfortran.so.5.* | sed s~/lib/~/lib64/~` 64/libgfortran.so
ln -sf ../`echo ../../../../lib/libgomp.so.1.* | sed s~/lib/~/lib64/~` 64/libgomp.so
%if %{build_go}
rm -f libgo.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libgo.so.19.* | sed 's,^.*libg,libg,'`' )' > libgo.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libgo.so.19.* | sed 's,^.*libg,libg,'`' )' > 64/libgo.so
%endif
%if %{build_libquadmath}
rm -f libquadmath.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libquadmath.so.0.* | sed 's,^.*libq,libq,'`' )' > libquadmath.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libquadmath.so.0.* | sed 's,^.*libq,libq,'`' )' > 64/libquadmath.so
%endif
%if %{build_d}
rm -f libgdruntime.so libgphobos.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libgdruntime.so.2.* | sed 's,^.*libg,libg,'`' )' > libgdruntime.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libgdruntime.so.2.* | sed 's,^.*libg,libg,'`' )' > 64/libgdruntime.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libgphobos.so.2.* | sed 's,^.*libg,libg,'`' )' > libgphobos.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libgphobos.so.2.* | sed 's,^.*libg,libg,'`' )' > 64/libgphobos.so
%endif
%if %{build_libitm}
rm -f libitm.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libitm.so.1.* | sed 's,^.*libi,libi,'`' )' > libitm.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libitm.so.1.* | sed 's,^.*libi,libi,'`' )' > 64/libitm.so
%endif
%if %{build_libatomic}
rm -f libatomic.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libatomic.so.1.* | sed 's,^.*liba,liba,'`' )' > libatomic.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libatomic.so.1.* | sed 's,^.*liba,liba,'`' )' > 64/libatomic.so
%endif
%if %{build_libasan}
rm -f libasan.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libasan.so.6.* | sed 's,^.*liba,liba,'`' )' > libasan.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libasan.so.6.* | sed 's,^.*liba,liba,'`' )' > 64/libasan.so
mv ../../../../lib64/libasan_preinit.o 64/libasan_preinit.o
%endif
%if %{build_libubsan}
rm -f libubsan.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib/libubsan.so.1.* | sed 's,^.*libu,libu,'`' )' > libubsan.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib/libubsan.so.1.* | sed 's,^.*libu,libu,'`' )' > 64/libubsan.so
%endif
ln -sf lib32/libgfortran.a libgfortran.a
ln -sf ../lib64/libgfortran.a 64/libgfortran.a
%if %{build_objc}
mv -f %{buildroot}%{_prefix}/lib64/libobjc.*a 64/
%endif
mv -f %{buildroot}%{_prefix}/lib64/libgomp.*a 64/
ln -sf lib32/libstdc++.a libstdc++.a
ln -sf ../lib64/libstdc++.a 64/libstdc++.a
ln -sf lib32/libstdc++fs.a libstdc++fs.a
ln -sf ../lib64/libstdc++fs.a 64/libstdc++fs.a
ln -sf lib32/libsupc++.a libsupc++.a
ln -sf ../lib64/libsupc++.a 64/libsupc++.a
%if %{build_libquadmath}
ln -sf lib32/libquadmath.a libquadmath.a
ln -sf ../lib64/libquadmath.a 64/libquadmath.a
%endif
%if %{build_d}
ln -sf lib32/libgdruntime.a libgdruntime.a
ln -sf ../lib64/libgdruntime.a 64/libgdruntime.a
ln -sf lib32/libgphobos.a libgphobos.a
ln -sf ../lib64/libgphobos.a 64/libgphobos.a
%endif
%if %{build_libitm}
ln -sf lib32/libitm.a libitm.a
ln -sf ../lib64/libitm.a 64/libitm.a
%endif
%if %{build_libatomic}
ln -sf lib32/libatomic.a libatomic.a
ln -sf ../lib64/libatomic.a 64/libatomic.a
%endif
%if %{build_libasan}
ln -sf lib32/libasan.a libasan.a
ln -sf ../lib64/libasan.a 64/libasan.a
%endif
%if %{build_libubsan}
ln -sf lib32/libubsan.a libubsan.a
ln -sf ../lib64/libubsan.a 64/libubsan.a
%endif
%if %{build_go}
ln -sf lib32/libgo.a libgo.a
ln -sf ../lib64/libgo.a 64/libgo.a
ln -sf lib32/libgobegin.a libgobegin.a
ln -sf ../lib64/libgobegin.a 64/libgobegin.a
ln -sf lib32/libgolibbegin.a libgolibbegin.a
ln -sf ../lib64/libgolibbegin.a 64/libgolibbegin.a
%endif
%if %{build_ada}
ln -sf lib32/adainclude adainclude
ln -sf ../lib64/adainclude 64/adainclude
ln -sf lib32/adalib adalib
ln -sf ../lib64/adalib 64/adalib
%endif
%endif
%ifarch %{multilib_64_archs}
mkdir -p 32
%if %{build_objc}
ln -sf ../../../../libobjc.so.4 32/libobjc.so
%endif
ln -sf ../`echo ../../../../lib64/libstdc++.so.6.*[0-9] | sed s~/../lib64/~/~` 32/libstdc++.so
ln -sf ../`echo ../../../../lib64/libgfortran.so.5.* | sed s~/../lib64/~/~` 32/libgfortran.so
ln -sf ../`echo ../../../../lib64/libgomp.so.1.* | sed s~/../lib64/~/~` 32/libgomp.so
%if %{build_go}
rm -f libgo.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libgo.so.19.* | sed 's,^.*libg,libg,'`' )' > libgo.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libgo.so.19.* | sed 's,^.*libg,libg,'`' )' > 32/libgo.so
%endif
%if %{build_libquadmath}
rm -f libquadmath.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libquadmath.so.0.* | sed 's,^.*libq,libq,'`' )' > libquadmath.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libquadmath.so.0.* | sed 's,^.*libq,libq,'`' )' > 32/libquadmath.so
%endif
%if %{build_d}
rm -f libgdruntime.so libgphobos.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libgdruntime.so.2.* | sed 's,^.*libg,libg,'`' )' > libgdruntime.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libgdruntime.so.2.* | sed 's,^.*libg,libg,'`' )' > 32/libgdruntime.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libgphobos.so.2.* | sed 's,^.*libg,libg,'`' )' > libgphobos.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libgphobos.so.2.* | sed 's,^.*libg,libg,'`' )' > 32/libgphobos.so
%endif
%if %{build_libitm}
rm -f libitm.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libitm.so.1.* | sed 's,^.*libi,libi,'`' )' > libitm.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libitm.so.1.* | sed 's,^.*libi,libi,'`' )' > 32/libitm.so
%endif
%if %{build_libatomic}
rm -f libatomic.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libatomic.so.1.* | sed 's,^.*liba,liba,'`' )' > libatomic.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libatomic.so.1.* | sed 's,^.*liba,liba,'`' )' > 32/libatomic.so
%endif
%if %{build_libasan}
rm -f libasan.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libasan.so.6.* | sed 's,^.*liba,liba,'`' )' > libasan.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libasan.so.6.* | sed 's,^.*liba,liba,'`' )' > 32/libasan.so
mv ../../../../lib/libasan_preinit.o 32/libasan_preinit.o
%endif
%if %{build_libubsan}
rm -f libubsan.so
echo 'INPUT ( %{_prefix}/lib64/'`echo ../../../../lib64/libubsan.so.1.* | sed 's,^.*libu,libu,'`' )' > libubsan.so
echo 'INPUT ( %{_prefix}/lib/'`echo ../../../../lib64/libubsan.so.1.* | sed 's,^.*libu,libu,'`' )' > 32/libubsan.so
%endif
%if %{build_objc}
mv -f %{buildroot}%{_prefix}/lib/libobjc.*a 32/
%endif
mv -f %{buildroot}%{_prefix}/lib/libgomp.*a 32/
%endif
%ifarch sparc64 ppc64 ppc64p7
ln -sf ../lib32/libgfortran.a 32/libgfortran.a
ln -sf lib64/libgfortran.a libgfortran.a
ln -sf ../lib32/libstdc++.a 32/libstdc++.a
ln -sf lib64/libstdc++.a libstdc++.a
ln -sf ../lib32/libstdc++fs.a 32/libstdc++fs.a
ln -sf lib64/libstdc++fs.a libstdc++fs.a
ln -sf ../lib32/libsupc++.a 32/libsupc++.a
ln -sf lib64/libsupc++.a libsupc++.a
%if %{build_libquadmath}
ln -sf ../lib32/libquadmath.a 32/libquadmath.a
ln -sf lib64/libquadmath.a libquadmath.a
%endif
%if %{build_d}
ln -sf ../lib32/libgdruntime.a 32/libgdruntime.a
ln -sf lib64/libgdruntime.a libgdruntime.a
ln -sf ../lib32/libgphobos.a 32/libgphobos.a
ln -sf lib64/libgphobos.a libgphobos.a
%endif
%if %{build_libitm}
ln -sf ../lib32/libitm.a 32/libitm.a
ln -sf lib64/libitm.a libitm.a
%endif
%if %{build_libatomic}
ln -sf ../lib32/libatomic.a 32/libatomic.a
ln -sf lib64/libatomic.a libatomic.a
%endif
%if %{build_libasan}
ln -sf ../lib32/libasan.a 32/libasan.a
ln -sf lib64/libasan.a libasan.a
%endif
%if %{build_libubsan}
ln -sf ../lib32/libubsan.a 32/libubsan.a
ln -sf lib64/libubsan.a libubsan.a
%endif
%if %{build_go}
ln -sf ../lib32/libgo.a 32/libgo.a
ln -sf lib64/libgo.a libgo.a
ln -sf ../lib32/libgobegin.a 32/libgobegin.a
ln -sf lib64/libgobegin.a libgobegin.a
ln -sf ../lib32/libgolibbegin.a 32/libgolibbegin.a
ln -sf lib64/libgolibbegin.a libgolibbegin.a
%endif
%if %{build_ada}
ln -sf ../lib32/adainclude 32/adainclude
ln -sf lib64/adainclude adainclude
ln -sf ../lib32/adalib 32/adalib
ln -sf lib64/adalib adalib
%endif
%else
%ifarch %{multilib_64_archs}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libgfortran.a 32/libgfortran.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libstdc++.a 32/libstdc++.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libstdc++fs.a 32/libstdc++fs.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libsupc++.a 32/libsupc++.a
%if %{build_libquadmath}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libquadmath.a 32/libquadmath.a
%endif
%if %{build_d}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libgdruntime.a 32/libgdruntime.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libgphobos.a 32/libgphobos.a
%endif
%if %{build_libitm}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libitm.a 32/libitm.a
%endif
%if %{build_libatomic}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libatomic.a 32/libatomic.a
%endif
%if %{build_libasan}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libasan.a 32/libasan.a
%endif
%if %{build_libubsan}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libubsan.a 32/libubsan.a
%endif
%if %{build_go}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libgo.a 32/libgo.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libgobegin.a 32/libgobegin.a
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/libgolibbegin.a 32/libgolibbegin.a
%endif
%if %{build_ada}
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/adainclude 32/adainclude
ln -sf ../../../%{multilib_32_arch}-%{_vendor}-%{_target_os}/%{gcc_major}/adalib 32/adalib
%endif
%endif
%endif

# If we are building a debug package then copy all of the static archives
# into the debug directory to keep them as unstripped copies.
%if 0%{?_enable_debug_packages}
for d in . $FULLLSUBDIR; do
  mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/debug%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/$d
  for f in `find $d -maxdepth 1 -a \
		\( -name libasan.a -o -name libatomic.a \
		-o -name libcaf_single.a \
		-o -name libgcc.a -o -name libgcc_eh.a \
		-o -name libgcov.a -o -name libgfortran.a \
		-o -name libgo.a -o -name libgobegin.a \
		-o -name libgolibbegin.a -o -name libgomp.a \
		-o -name libitm.a -o -name liblsan.a \
		-o -name libobjc.a -o -name libgdruntime.a -o -name libgphobos.a \
		-o -name libquadmath.a -o -name libstdc++.a \
		-o -name libstdc++fs.a -o -name libsupc++.a \
		-o -name libtsan.a -o -name libubsan.a \) -a -type f`; do
    cp -a $f $RPM_BUILD_ROOT%{_prefix}/lib/debug%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/$d/
  done
done
%endif

# Strip debug info from Fortran/ObjC/Java static libraries
strip -g `find . \( -name libgfortran.a -o -name libobjc.a -o -name libgomp.a \
		    -o -name libgcc.a -o -name libgcov.a -o -name libquadmath.a \
		    -o -name libgdruntime.a -o -name libgphobos.a \
		    -o -name libitm.a -o -name libgo.a -o -name libcaf\*.a \
		    -o -name libatomic.a -o -name libasan.a -o -name libtsan.a \
		    -o -name libubsan.a -o -name liblsan.a -o -name libcc1.a \) \
		 -a -type f`
popd
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgfortran.so.5.*
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgomp.so.1.*
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libcc1.so.0.*
%if %{build_libquadmath}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libquadmath.so.0.*
%endif
%if %{build_d}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgdruntime.so.2.*
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgphobos.so.2.*
%endif
%if %{build_libitm}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libitm.so.1.*
%endif
%if %{build_libatomic}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libatomic.so.1.*
%endif
%if %{build_libasan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libasan.so.6.*
%endif
%if %{build_libubsan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libubsan.so.1.*
%endif
%if %{build_libtsan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libtsan.so.0.*
%endif
%if %{build_liblsan}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/liblsan.so.0.*
%endif
%if %{build_go}
# Avoid stripping these libraries and binaries.
chmod 644 %{buildroot}%{_prefix}/%{_lib}/libgo.so.19.*
chmod 644 %{buildroot}%{_prefix}/bin/go.gcc
chmod 644 %{buildroot}%{_prefix}/bin/gofmt.gcc
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cgo
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/buildid
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/test2json
chmod 644 %{buildroot}%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/vet
%endif
%if %{build_objc}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libobjc.so.4.*
%endif

%if %{build_ada}
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgnarl*so*
chmod 755 %{buildroot}%{_prefix}/%{_lib}/libgnat*so*
%endif

mv $FULLPATH/include-fixed/syslimits.h $FULLPATH/include/syslimits.h
mv $FULLPATH/include-fixed/limits.h $FULLPATH/include/limits.h
for h in `find $FULLPATH/include -name \*.h`; do
  if grep -q 'It has been auto-edited by fixincludes from' $h; then
    rh=`grep -A2 'It has been auto-edited by fixincludes from' $h | tail -1 | sed 's|^.*"\(.*\)".*$|\1|'`
    diff -up $rh $h || :
    rm -f $h
  fi
done

cat > %{buildroot}%{_prefix}/bin/c89 <<"EOF"
#!/bin/sh
fl="-std=c89"
for opt; do
  case "$opt" in
    -ansi|-std=c89|-std=iso9899:1990) fl="";;
    -std=*) echo "`basename $0` called with non ANSI/ISO C option $opt" >&2
	    exit 1;;
  esac
done
exec gcc $fl ${1+"$@"}
EOF
cat > %{buildroot}%{_prefix}/bin/c99 <<"EOF"
#!/bin/sh
fl="-std=c99"
for opt; do
  case "$opt" in
    -std=c99|-std=iso9899:1999) fl="";;
    -std=*) echo "`basename $0` called with non ISO C99 option $opt" >&2
	    exit 1;;
  esac
done
exec gcc $fl ${1+"$@"}
EOF
chmod 755 %{buildroot}%{_prefix}/bin/c?9

cd ..
%find_lang %{name}
%find_lang cpplib

# Remove binaries we will not be including, so that they don't end up in
# gcc-debuginfo
rm -f %{buildroot}%{_prefix}/%{_lib}/{libffi*,libiberty.a} || :
rm -f $FULLEPATH/install-tools/{mkheaders,fixincl}
rm -f %{buildroot}%{_prefix}/lib/{32,64}/libiberty.a
rm -f %{buildroot}%{_prefix}/%{_lib}/libssp*
rm -f %{buildroot}%{_prefix}/%{_lib}/libvtv* || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gfortran || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gccgo || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcj || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcc-ar || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcc-nm || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gcc-ranlib || :
rm -f %{buildroot}%{_prefix}/bin/%{_target_platform}-gdc || :

%ifarch %{multilib_64_archs}
# Remove libraries for the other arch on multilib arches
rm -f %{buildroot}%{_prefix}/lib/lib*.so*
rm -f %{buildroot}%{_prefix}/lib/lib*.a
rm -f %{buildroot}/lib/libgcc_s*.so*
%if %{build_go}
rm -rf %{buildroot}%{_prefix}/lib/go/%{gcc_major}/%{gcc_target_platform}
%ifnarch sparc64 ppc64 ppc64p7
ln -sf %{multilib_32_arch}-%{_vendor}-%{_target_os} %{buildroot}%{_prefix}/lib/go/%{gcc_major}/%{gcc_target_platform}
%endif
%endif
%else
%ifarch sparcv9 ppc
rm -f %{buildroot}%{_prefix}/lib64/lib*.so*
rm -f %{buildroot}%{_prefix}/lib64/lib*.a
rm -f %{buildroot}/lib64/libgcc_s*.so*
%if %{build_go}
rm -rf %{buildroot}%{_prefix}/lib64/go/%{gcc_major}/%{gcc_target_platform}
%endif
%endif
%endif

rm -f %{buildroot}%{mandir}/man3/ffi*

# Help plugins find out nvra.
echo gcc-%{version}-%{release}.%{_arch} > $FULLPATH/rpmver

# Add symlink to lto plugin in the binutils plugin directory.
%{__mkdir_p} %{buildroot}%{_libdir}/bfd-plugins/
ln -s ../../libexec/gcc/%{gcc_target_platform}/%{gcc_major}/liblto_plugin.so \
  %{buildroot}%{_libdir}/bfd-plugins/

# Rename the annobin plugin to gcc-annobin.
mkdir -p %{buildroot}%{ANNOBIN_GCC_PLUGIN_DIR}
pushd    %{buildroot}%{ANNOBIN_GCC_PLUGIN_DIR}

annobin_dir=$(find %{_builddir} -maxdepth 1 -type d -name "annobin*")
echo "annobin directory = ${annobin_dir}"

cp ${annobin_dir}/gcc-plugin/.libs/annobin.so.0.0.0 gcc-annobin.so.0.0.0

rm -f gcc-annobin.so.0 gcc-annobin.so
ln -s gcc-annobin.so.0.0.0 gcc-annobin.so.0
ln -s gcc-annobin.so.0.0.0 gcc-annobin.so
popd

%check
cd obj-%{gcc_target_platform}

# run the tests.
LC_ALL=C make %{?_smp_mflags} -k check ALT_CC_UNDER_TEST=gcc ALT_CXX_UNDER_TEST=g++ \
%if 0%{?fedora} >= 20 || 0%{?rhel} > 7
     RUNTESTFLAGS="--target_board=unix/'{,-fstack-protector-strong}'" || :
%else
     RUNTESTFLAGS="--target_board=unix/'{,-fstack-protector}'" || :
%endif
if [ -f %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin/annobin.so ]; then
  # Test whether current annobin plugin won't fail miserably with the newly built gcc.
  echo -e '#include <stdio.h>\nint main () { printf ("Hello, world!\\n"); return 0; }' > annobin-test.c
  echo -e '#include <iostream>\nint main () { std::cout << "Hello, world!" << std::endl; return 0; }' > annobin-test.C
  `%{gcc_target_platform}/libstdc++-v3/scripts/testsuite_flags --build-cc` \
  -O2 -g -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS \
  -fexceptions -fstack-protector-strong -grecord-gcc-switches -o annobin-test{c,.c} \
  -Wl,-rpath,%{gcc_target_platform}/libgcc/ \
  -fplugin=%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin/annobin.so \
  2> ANNOBINOUT1 || echo Annobin test 1 FAIL > ANNOBINOUT2;
  `%{gcc_target_platform}/libstdc++-v3/scripts/testsuite_flags --build-cxx` \
  `%{gcc_target_platform}/libstdc++-v3/scripts/testsuite_flags --build-includes` \
  -O2 -g -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS \
  -fexceptions -fstack-protector-strong -grecord-gcc-switches -o annobin-test{C,.C} \
  -Wl,-rpath,%{gcc_target_platform}/libgcc/:%{gcc_target_platform}/libstdc++-v3/src/.libs/ \
  -fplugin=%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin/annobin.so \
  -B %{gcc_target_platform}/libstdc++-v3/src/.libs/ \
  2> ANNOBINOUT3 || echo Annobin test 2 FAIL > ANNOBINOUT4;
  [ -f ./annobin-testc ] || echo Annobin test 1 MISSING > ANNOBINOUT5;
  [ -f ./annobin-testc ] && \
  ( ./annobin-testc > ANNOBINRES1 2>&1 || echo Annobin test 1 RUNFAIL > ANNOBINOUT6 );
  [ -f ./annobin-testC ] || echo Annobin test 2 MISSING > ANNOBINOUT7;
  [ -f ./annobin-testC ] && \
  ( ./annobin-testC > ANNOBINRES2 2>&1 || echo Annobin test 2 RUNFAIL > ANNOBINOUT8 );
  cat ANNOBINOUT[1-8] > ANNOBINOUT
  touch ANNOBINRES1 ANNOBINRES2
  [ -s ANNOBINOUT ] && echo Annobin testing FAILed > ANNOBINRES
  cat ANNOBINOUT ANNOBINRES[12] >> ANNOBINRES
  rm -f ANNOBINOUT* ANNOBINRES[12] annobin-test{c,C}
fi
echo ====================TESTING=========================
( LC_ALL=C ../contrib/test_summary || : ) 2>&1 | sed -n '/^cat.*EOF/,/^EOF/{/^cat.*EOF/d;/^EOF/d;/^LAST_UPDATED:/d;p;}'
[ -f ANNOBINRES ] && cat ANNOBINRES
echo ====================TESTING END=====================
mkdir testlogs-%{_target_platform}-%{version}-%{release}
for i in `find . -name \*.log | grep -F testsuite/ | grep -v 'config.log\|acats.*/tests/'`; do
  ln $i testlogs-%{_target_platform}-%{version}-%{release}/ || :
done
tar cf - testlogs-%{_target_platform}-%{version}-%{release} | xz -9e \
  | uuencode testlogs-%{_target_platform}.tar.xz || :
rm -rf testlogs-%{_target_platform}-%{version}-%{release}

%post go
%{_sbindir}/update-alternatives --install \
  %{_prefix}/bin/go go %{_prefix}/bin/go.gcc 92 \
  --slave %{_prefix}/bin/gofmt gofmt %{_prefix}/bin/gofmt.gcc

%preun go
if [ $1 = 0 ]; then
  %{_sbindir}/update-alternatives --remove go %{_prefix}/bin/go.gcc
fi

# Because glibc Prereq's libgcc and /sbin/ldconfig
# comes from glibc, it might not exist yet when
# libgcc is installed
%post -n libgcc -p <lua>
if posix.access ("/sbin/ldconfig", "x") then
  local pid = posix.fork ()
  if pid == 0 then
    posix.exec ("/sbin/ldconfig")
  elseif pid ~= -1 then
    posix.wait (pid)
  end
end

%postun -n libgcc -p <lua>
if posix.access ("/sbin/ldconfig", "x") then
  local pid = posix.fork ()
  if pid == 0 then
    posix.exec ("/sbin/ldconfig")
  elseif pid ~= -1 then
    posix.wait (pid)
  end
end

%ldconfig_scriptlets -n libstdc++

%ldconfig_scriptlets -n libobjc

%ldconfig_scriptlets -n libgfortran

%ldconfig_scriptlets -n libgphobos

%ldconfig_scriptlets -n libgnat

%ldconfig_scriptlets -n libgomp

%ldconfig_scriptlets gdb-plugin

%ldconfig_scriptlets -n libgccjit

%ldconfig_scriptlets -n libquadmath

%ldconfig_scriptlets -n libitm

%ldconfig_scriptlets -n libatomic

%ldconfig_scriptlets -n libasan

%ldconfig_scriptlets -n libubsan

%ldconfig_scriptlets -n libtsan

%ldconfig_scriptlets -n liblsan

%ldconfig_scriptlets -n libgo

%files -f %{name}.lang
%{_prefix}/bin/cc
%{_prefix}/bin/c89
%{_prefix}/bin/c99
%{_prefix}/bin/gcc
%{_prefix}/bin/gcov
%{_prefix}/bin/gcov-tool
%{_prefix}/bin/gcov-dump
%{_prefix}/bin/gcc-ar
%{_prefix}/bin/gcc-nm
%{_prefix}/bin/gcc-ranlib
%{_prefix}/bin/lto-dump
%ifarch ppc
%{_prefix}/bin/%{_target_platform}-gcc
%endif
%ifarch sparc64 sparcv9
%{_prefix}/bin/sparc-%{_vendor}-%{_target_os}-gcc
%endif
%ifarch ppc64 ppc64p7
%{_prefix}/bin/ppc-%{_vendor}-%{_target_os}-gcc
%endif
%{_prefix}/bin/%{gcc_target_platform}-gcc
%{_prefix}/bin/%{gcc_target_platform}-gcc-%{gcc_major}
%{_mandir}/man1/gcc.1*
%{_mandir}/man1/gcov.1*
%{_mandir}/man1/gcov-tool.1*
%{_mandir}/man1/gcov-dump.1*
%{_mandir}/man1/lto-dump.1*
%{_infodir}/gcc*
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/lto1
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/lto-wrapper
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/liblto_plugin.so*
%{_libdir}/bfd-plugins/liblto_plugin.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/rpmver
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stddef.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdarg.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdfix.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/varargs.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/float.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/limits.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdbool.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/iso646.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/syslimits.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/unwind.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/omp.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/openacc.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/acc_prof.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdint.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdint-gcc.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdalign.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdnoreturn.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/stdatomic.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/gcov.h
%ifarch %{ix86} x86_64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/emmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/pmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/tmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/ammintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/smmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/nmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/bmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/wmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/immintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avxintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/x86intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/fma4intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xopintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/lwpintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/popcntintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/bmiintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/tbmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/ia32intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx2intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/bmi2intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/f16cintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/fmaintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/lzcntintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/rtmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xtestintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/adxintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/prfchwintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/rdseedintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/fxsrintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xsaveintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xsaveoptintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512cdintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512erintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512fintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512pfintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/shaintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mm_malloc.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mm3dnow.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/cpuid.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/cross-stdarg.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512bwintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512dqintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512ifmaintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512ifmavlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vbmiintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vbmivlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vlbwintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vldqintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/clflushoptintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/clwbintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mwaitxintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xsavecintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xsavesintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/clzerointrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/pkuintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx5124fmapsintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx5124vnniwintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vpopcntdqintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/sgxintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/gfniintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/cetintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/cet.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vbmi2intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vbmi2vlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vnniintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vnnivlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/vaesintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/vpclmulqdqintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vpopcntdqvlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512bitalgintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/pconfigintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/wbnoinvdintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/movdirintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/waitpkgintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/cldemoteintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512bf16vlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512bf16intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/enqcmdintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vp2intersectintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avx512vp2intersectvlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/serializeintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/tsxldtrkintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/amxtileintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/amxint8intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/amxbf16intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/x86gprintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/uintrintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/hresetintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/keylockerintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/avxvnniintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mwaitintrin.h
%endif
%ifarch ia64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/ia64intrin.h
%endif
%ifarch ppc ppc64 ppc64le ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/ppc-asm.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/altivec.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/ppu_intrinsics.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/si2vmx.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/spu2vmx.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/vec_types.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/htmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/htmxlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/bmi2intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/bmiintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/xmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mm_malloc.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/emmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/x86intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/pmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/tmmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/smmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/amo.h
%endif
%ifarch %{arm}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/unwind-arm-common.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/mmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_neon.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_acle.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_cmse.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_fp16.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_bf16.h
%endif
%ifarch aarch64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_neon.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_acle.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_fp16.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_bf16.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/arm_sve.h
%endif
%ifarch sparc sparcv9 sparc64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/visintrin.h
%endif
%ifarch s390 s390x
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/s390intrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/htmintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/htmxlintrin.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/vecintrin.h
%endif
%if %{build_libasan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/sanitizer
%endif
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/collect2
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/crt*.o
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgcc.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgcov.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgcc_eh.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgcc_s.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgomp.spec
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgomp.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgomp.so
%if %{build_libitm}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libitm.spec
%endif
%if %{build_libasan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libsanitizer.spec
%endif
%if %{build_isl}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libisl.so.*
%endif
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/crt*.o
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgcc.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgcov.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgcc_eh.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgcc_s.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgomp.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgomp.so
%if %{build_libquadmath}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libquadmath.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libquadmath.so
%endif
%if %{build_libitm}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libitm.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libitm.so
%endif
%if %{build_libatomic}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libatomic.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libatomic.so
%endif
%if %{build_libasan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libasan.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libasan.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libasan_preinit.o
%endif
%if %{build_libubsan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libubsan.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libubsan.so
%endif
%endif
%ifarch %{multilib_64_archs}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/crt*.o
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgcc.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgcov.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgcc_eh.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgcc_s.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgomp.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgomp.so
%if %{build_libquadmath}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libquadmath.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libquadmath.so
%endif
%if %{build_libitm}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libitm.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libitm.so
%endif
%if %{build_libatomic}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libatomic.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libatomic.so
%endif
%if %{build_libasan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libasan.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libasan.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libasan_preinit.o
%endif
%if %{build_libubsan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libubsan.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libubsan.so
%endif
%endif
%ifarch sparcv9 sparc64 ppc ppc64 ppc64p7
%if %{build_libquadmath}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libquadmath.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libquadmath.so
%endif
%if %{build_libitm}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libitm.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libitm.so
%endif
%if %{build_libatomic}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libatomic.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libatomic.so
%endif
%if %{build_libasan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libasan.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libasan.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libasan_preinit.o
%endif
%if %{build_libubsan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libubsan.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libubsan.so
%endif
%else
%if %{build_libatomic}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libatomic.so
%endif
%if %{build_libasan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libasan.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libasan_preinit.o
%endif
%if %{build_libubsan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libubsan.so
%endif
%endif
%if %{build_libtsan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libtsan.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libtsan_preinit.o
%endif
%if %{build_liblsan}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/liblsan.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/liblsan_preinit.o
%endif
%{_prefix}/libexec/getconf/default
%doc gcc/README* rpm.doc/changelogs/gcc/ChangeLog* 
%{!?_licensedir:%global license %%doc}
%license gcc/COPYING* COPYING.RUNTIME

%files -n cpp -f cpplib.lang
%{_prefix}/lib/cpp
%{_prefix}/bin/cpp
%{_mandir}/man1/cpp.1*
%{_infodir}/cpp*
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cc1

%files -n libgcc
/%{_lib}/libgcc_s-%{gcc_major}-%{DATE}.so.1
/%{_lib}/libgcc_s.so.1
%{!?_licensedir:%global license %%doc}
%license gcc/COPYING* COPYING.RUNTIME

%files c++
%{_prefix}/bin/%{gcc_target_platform}-*++
%{_prefix}/bin/g++
%{_prefix}/bin/c++
%{_mandir}/man1/g++.1*
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cc1plus
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/g++-mapper-server
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libstdc++.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libstdc++.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libstdc++fs.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libsupc++.a
%endif
%ifarch %{multilib_64_archs}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libstdc++.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libstdc++.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libstdc++fs.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libsupc++.a
%endif
%ifarch sparcv9 ppc %{multilib_64_archs}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libstdc++.so
%endif
%ifarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libstdc++.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libstdc++fs.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libsupc++.a
%endif
%doc rpm.doc/changelogs/gcc/cp/ChangeLog*

%files -n libstdc++
%{_prefix}/%{_lib}/libstdc++.so.6*
%dir %{_datadir}/gdb
%dir %{_datadir}/gdb/auto-load
%dir %{_datadir}/gdb/auto-load/%{_prefix}
%dir %{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/
# Package symlink to keep compatibility
%ifarch riscv64
%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/lp64d
%endif
%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/libstdc*gdb.py*
%{_datadir}/gdb/auto-load/%{_prefix}/%{_lib}/__pycache__
%dir %{_prefix}/share/gcc-%{gcc_major}
%dir %{_prefix}/share/gcc-%{gcc_major}/python
%{_prefix}/share/gcc-%{gcc_major}/python/libstdcxx

%files -n libstdc++-devel
%dir %{_prefix}/include/c++
%{_prefix}/include/c++/%{gcc_major}
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifnarch sparcv9 ppc %{multilib_64_archs}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libstdc++.so
%endif
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libstdc++fs.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libstdc++fs.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libstdc++fs.a
%endif
%doc rpm.doc/changelogs/libstdc++-v3/ChangeLog* libstdc++-v3/README*

%files -n libstdc++-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libstdc++.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libsupc++.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libstdc++.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libsupc++.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libstdc++.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libsupc++.a
%endif

%if %{build_libstdcxx_docs}
%files -n libstdc++-docs
%{_mandir}/man3/*
%doc rpm.doc/libstdc++-v3/html
%endif

%if %{build_objc}
%files objc
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/objc
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cc1obj
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libobjc.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libobjc.so
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libobjc.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libobjc.so
%endif
%ifarch %{multilib_64_archs}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libobjc.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libobjc.so
%endif
%doc rpm.doc/objc/*
%doc libobjc/THREADS* rpm.doc/changelogs/libobjc/ChangeLog*

%files objc++
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cc1objplus

%files -n libobjc
%{_prefix}/%{_lib}/libobjc.so.4*
%endif

%files gfortran
%{_prefix}/bin/gfortran
%{_prefix}/bin/f95
%{_mandir}/man1/gfortran.1*
%{_infodir}/gfortran*
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/ISO_Fortran_binding.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/omp_lib.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/omp_lib.f90
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/omp_lib.mod
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/omp_lib_kinds.mod
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/openacc.f90
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/openacc.mod
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/openacc_kinds.mod
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/openacc_lib.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/ieee_arithmetic.mod
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/ieee_exceptions.mod
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/finclude/ieee_features.mod
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/f951
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgfortran.spec
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libcaf_single.a
%ifarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgfortran.a
%endif
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgfortran.so
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libcaf_single.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgfortran.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgfortran.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/finclude
%endif
%ifarch %{multilib_64_archs}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libcaf_single.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgfortran.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgfortran.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/finclude
%endif
%dir %{_fmoddir}
%doc rpm.doc/gfortran/*

%files -n libgfortran
%{_prefix}/%{_lib}/libgfortran.so.5*

%files -n libgfortran-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libgfortran.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libgfortran.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgfortran.a
%endif

%if %{build_d}
%files gdc
%{_prefix}/bin/gdc
%{_mandir}/man1/gdc.1*
%{_infodir}/gdc*
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/d
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/d21
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgphobos.spec
%ifarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgdruntime.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgphobos.a
%endif
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgdruntime.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgphobos.so
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgdruntime.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgphobos.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgdruntime.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgphobos.so
%endif
%ifarch %{multilib_64_archs}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgdruntime.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgphobos.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgdruntime.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgphobos.so
%endif
%doc rpm.doc/gdc/*

%files -n libgphobos
%{_prefix}/%{_lib}/libgdruntime.so.2*
%{_prefix}/%{_lib}/libgphobos.so.2*
%doc rpm.doc/libphobos/*

%files -n libgphobos-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libgdruntime.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libgphobos.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libgdruntime.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libgphobos.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgdruntime.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgphobos.a
%endif
%endif

%if %{build_ada}
%files gnat
%{_prefix}/bin/gnat
%{_prefix}/bin/gnat[^i]*
%{_infodir}/gnat*
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/adainclude
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/adalib
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/ada_target_properties
%endif
%ifarch %{multilib_64_archs}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/adainclude
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/adalib
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/ada_target_properties
%endif
%ifarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adainclude
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adalib
%endif
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/ada_target_properties
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/gnat1
%doc rpm.doc/changelogs/gcc/ada/ChangeLog*

%files -n libgnat
%{_prefix}/%{_lib}/libgnat-*.so
%{_prefix}/%{_lib}/libgnarl-*.so

%files -n libgnat-devel
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/adainclude
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/adalib
%exclude %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/adalib/libgnat.a
%exclude %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/adalib/libgnarl.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/adainclude
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/adalib
%exclude %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/adalib/libgnat.a
%exclude %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/adalib/libgnarl.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adainclude
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adalib
%exclude %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adalib/libgnat.a
%exclude %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adalib/libgnarl.a
%endif

%files -n libgnat-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/adalib
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/adalib/libgnat.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/adalib/libgnarl.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/adalib
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/adalib/libgnat.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/adalib/libgnarl.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adalib
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adalib/libgnat.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/adalib/libgnarl.a
%endif
%endif

%files -n libgomp
%{_prefix}/%{_lib}/libgomp.so.1*
%{_infodir}/libgomp.info*
%doc rpm.doc/changelogs/libgomp/ChangeLog*

%if %{build_libquadmath}
%files -n libquadmath
%{_prefix}/%{_lib}/libquadmath.so.0*
%{_infodir}/libquadmath.info*
%{!?_licensedir:%global license %%doc}
%license rpm.doc/libquadmath/COPYING*

%files -n libquadmath-devel
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/quadmath.h
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include/quadmath_weak.h
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libquadmath.so
%endif
%doc rpm.doc/libquadmath/ChangeLog*

%files -n libquadmath-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libquadmath.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libquadmath.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libquadmath.a
%endif
%endif

%if %{build_libitm}
%files -n libitm
%{_prefix}/%{_lib}/libitm.so.1*
%{_infodir}/libitm.info*

%files -n libitm-devel
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/include
#%%{_prefix}/lib/gcc/%%{gcc_target_platform}/%%{gcc_major}/include/itm.h
#%%{_prefix}/lib/gcc/%%{gcc_target_platform}/%%{gcc_major}/include/itm_weak.h
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libitm.so
%endif
%doc rpm.doc/libitm/ChangeLog*

%files -n libitm-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libitm.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libitm.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libitm.a
%endif
%endif

%if %{build_libatomic}
%files -n libatomic
%{_prefix}/%{_lib}/libatomic.so.1*

%files -n libatomic-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libatomic.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libatomic.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libatomic.a
%endif
%doc rpm.doc/changelogs/libatomic/ChangeLog*
%endif

%if %{build_libasan}
%files -n libasan
%{_prefix}/%{_lib}/libasan.so.6*

%files -n libasan-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libasan.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libasan.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libasan.a
%endif
%doc rpm.doc/changelogs/libsanitizer/ChangeLog*
%{!?_licensedir:%global license %%doc}
%license libsanitizer/LICENSE.TXT
%endif

%if %{build_libubsan}
%files -n libubsan
%{_prefix}/%{_lib}/libubsan.so.1*

%files -n libubsan-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libubsan.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libubsan.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libubsan.a
%endif
%doc rpm.doc/changelogs/libsanitizer/ChangeLog*
%{!?_licensedir:%global license %%doc}
%license libsanitizer/LICENSE.TXT
%endif

%if %{build_libtsan}
%files -n libtsan
%{_prefix}/%{_lib}/libtsan.so.0*

%files -n libtsan-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libtsan.a
%doc rpm.doc/changelogs/libsanitizer/ChangeLog*
%{!?_licensedir:%global license %%doc}
%license libsanitizer/LICENSE.TXT
%endif

%if %{build_liblsan}
%files -n liblsan
%{_prefix}/%{_lib}/liblsan.so.0*

%files -n liblsan-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/liblsan.a
%doc rpm.doc/changelogs/libsanitizer/ChangeLog*
%{!?_licensedir:%global license %%doc}
%license libsanitizer/LICENSE.TXT
%endif

%if %{build_go}
%files go
%ghost %{_prefix}/bin/go
%attr(755,root,root) %{_prefix}/bin/go.gcc
%{_prefix}/bin/gccgo
%ghost %{_prefix}/bin/gofmt
%attr(755,root,root) %{_prefix}/bin/gofmt.gcc
%{_mandir}/man1/gccgo.1*
%{_mandir}/man1/go.1*
%{_mandir}/man1/gofmt.1*
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/go1
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/cgo
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/buildid
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/test2json
%attr(755,root,root) %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/vet
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgo.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgo.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgobegin.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/64/libgolibbegin.a
%endif
%ifarch %{multilib_64_archs}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgo.so
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgo.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgobegin.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/32/libgolibbegin.a
%endif
%ifarch sparcv9 ppc %{multilib_64_archs}
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgo.so
%endif
%ifarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgo.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgobegin.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgolibbegin.a
%endif
%doc rpm.doc/go/*

%files -n libgo
%attr(755,root,root) %{_prefix}/%{_lib}/libgo.so.19*
%doc rpm.doc/libgo/*

%files -n libgo-devel
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/%{_lib}/go
%dir %{_prefix}/%{_lib}/go/%{gcc_major}
%{_prefix}/%{_lib}/go/%{gcc_major}/%{gcc_target_platform}
%ifarch %{multilib_64_archs}
%ifnarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/go
%dir %{_prefix}/lib/go/%{gcc_major}
%{_prefix}/lib/go/%{gcc_major}/%{gcc_target_platform}
%endif
%endif
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libgobegin.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libgolibbegin.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libgobegin.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libgolibbegin.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgobegin.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgolibbegin.a
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgo.so
%endif

%files -n libgo-static
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%ifarch sparcv9 ppc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib32/libgo.a
%endif
%ifarch sparc64 ppc64 ppc64p7
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/lib64/libgo.a
%endif
%ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/libgo.a
%endif
%endif

%files -n libgccjit
%{_prefix}/%{_lib}/libgccjit.so.*
%doc rpm.doc/changelogs/gcc/jit/ChangeLog*

%files -n libgccjit-devel
%{_prefix}/%{_lib}/libgccjit.so
%{_prefix}/include/libgccjit*.h
%{_infodir}/libgccjit.info*
%doc rpm.doc/libgccjit-devel/*
%doc gcc/jit/docs/examples

%files plugin-devel
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin/gtype.state
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin/include
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/plugin

%files gdb-plugin
%{_prefix}/%{_lib}/libcc1.so*
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin/libcc1plugin.so*
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/plugin/libcp1plugin.so*
%doc rpm.doc/changelogs/libcc1/ChangeLog*

%if %{build_offload_nvptx}
%files offload-nvptx
%{_prefix}/bin/nvptx-none-*
%{_prefix}/bin/%{gcc_target_platform}-accel-nvptx-none-gcc
%{_prefix}/bin/%{gcc_target_platform}-accel-nvptx-none-lto-dump
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}
%dir %{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/accel
%{_prefix}/lib/gcc/nvptx-none
%{_prefix}/lib/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none
%{_prefix}/libexec/gcc/%{gcc_target_platform}/%{gcc_major}/accel/nvptx-none
%dir %{_prefix}/nvptx-none
%{_prefix}/nvptx-none/bin
%{_prefix}/nvptx-none/include

%files -n libgomp-offload-nvptx
%{_prefix}/%{_lib}/libgomp-plugin-nvptx.so.*
%endif

%files plugin-annobin
%{ANNOBIN_GCC_PLUGIN_DIR}/gcc-annobin.so
%{ANNOBIN_GCC_PLUGIN_DIR}/gcc-annobin.so.0
%{ANNOBIN_GCC_PLUGIN_DIR}/gcc-annobin.so.0.0.0

%changelog
* Tue Jul 12 2022 Marek Polacek <polacek@redhat.com> 11.3.1-2.1
- fix handling of invalid ranges in std::regex (#2106262)

* Thu Apr 21 2022 Jakub Jelinek <jakub@redhat.com> 11.3.1-2
- update from releases/gcc-11-branch (#2077536)
  - GCC 11.3 release
  - PRs c++/98249, c++/99893, c++/100608, c++/101051, c++/101532, c++/101677,
	c++/101717, c++/101894, c++/102869, c++/103105, c++/103328,
	c++/103341, c++/103455, c++/103706, c++/103885, c++/103943,
	c++/104008, c++/104079, c++/104225, c++/104507, c++/104565,
	c++/105003, c++/105064, c++/105143, c++/105186, c++/105256, c/101585,
	debug/105203, fortran/102992, fortran/104210, fortran/104228,
	fortran/104570, fortran/105138, gcov-profile/105282, ipa/103083,
	ipa/103432, jit/100613, libstdc++/90943, libstdc++/100516,
	libstdc++/103630, libstdc++/103638, libstdc++/103650,
	libstdc++/103955, libstdc++/104098, libstdc++/104301,
	libstdc++/104542, libstdc++/104859, libstdc++/105021,
	libstdc++/105027, middle-end/104497, middle-end/105165,
	rtl-optimization/104985, rtl-optimization/105028,
	rtl-optimization/105211, target/80556, target/100106, target/104117,
	target/104474, target/104853, target/104894, target/105214,
	target/105257, tree-optimization/99121, tree-optimization/104880,
	tree-optimization/105053, tree-optimization/105070,
	tree-optimization/105189, tree-optimization/105198,
	tree-optimization/105226, tree-optimization/105232,
	tree-optimization/105235
- fix bogus -Wuninitialized warning on va_arg with complex types on x86_64
  (PR target/105331)
- remove bogus assertion in std::from_chars (PR libstdc++/105324)

* Mon Apr  4 2022 David Malcolm <dmalcolm@redhat.com> - 11.2.1-10
- update from releases/gcc-11-branch (#2063255)
  - PRs ada/98724, ada/104258, ada/104767, ada/104861, c++/58646, c++/59950,
	c++/61611, c++/95036, c++/100468, c++/101030, c++/101095, c++/101371,
	c++/101515, c++/101767, c++/102045, c++/102123, c++/102538,
	c++/102740, c++/102990, c++/103057, c++/103186, c++/103291,
	c++/103299, c++/103337, c++/103711, c++/103769, c++/103968,
	c++/104107, c++/104108, c++/104284, c++/104410, c++/104472,
	c++/104513, c++/104568, c++/104667, c++/104806, c++/104847,
	c++/104944, c++/104994, c++/105035, c++/105061, c/82283, c/84685,
	c/104510, c/104711, d/104659, d/105004, debug/104337, debug/104517,
	debug/104557, fortran/66193, fortran/99585, fortran/100337,
	fortran/103790, fortran/104211, fortran/104311, fortran/104331,
	fortran/104430, fortran/104619, fortran/104811, go/100537,
	libgomp/104385, libstdc++/101231, libstdc++/102358, libstdc++/103904,
	libstdc++/104442, lto/104237, lto/104333, lto/104617,
	middle-end/95115, middle-end/99578, middle-end/100464,
	middle-end/100680, middle-end/100775, middle-end/100786,
	middle-end/104307, middle-end/104402, middle-end/104446,
	middle-end/104786, middle-end/104971, middle-end/105032,
	preprocessor/104147, rtl-optimization/104544, rtl-optimization/104589,
	rtl-optimization/104777, rtl-optimization/104814, sanitizer/102656,
	sanitizer/104449, sanitizer/105093, target/79754, target/87496,
	target/99708, target/99754, target/100784, target/101324,
	target/102140, target/102952, target/102957, target/103307,
	target/103627, target/103925, target/104090, target/104208,
	target/104219, target/104253, target/104362, target/104448,
	target/104451, target/104453, target/104458, target/104462,
	target/104469, target/104502, target/104674, target/104681,
	target/104688, target/104775, target/104890, target/104910,
	target/104923, target/104963, target/104998, target/105000,
	target/105052, target/105058, target/105068, testsuite/103556,
	testsuite/103586, testsuite/104730, testsuite/104759,
	testsuite/105055, tree-optimization/45178, tree-optimization/100834,
	tree-optimization/101636, tree-optimization/102819,
	tree-optimization/102893, tree-optimization/103169,
	tree-optimization/103361, tree-optimization/103489,
	tree-optimization/103544, tree-optimization/103596,
	tree-optimization/103641, tree-optimization/103864,
	tree-optimization/104263, tree-optimization/104288,
	tree-optimization/104511, tree-optimization/104601,
	tree-optimization/104675, tree-optimization/104782,
	tree-optimization/104931, tree-optimization/105094
- fix x86 vector initialization expansion fallback (PR target/105123)
- drop patch 22 (gcc11-libsanitizer-pthread.patch;
  upstreamed as r11-9607-ga8dd74bfb921ed)

* Thu Feb 10 2022 Marek Polacek <polacek@redhat.com> 11.2.1-9.4
- add --enable-host-bind-now, use it (#2044917)

* Tue Feb  8 2022 Marek Polacek <polacek@redhat.com> 11.2.1-9.3
- use _thread_db_sizeof_pthread to obtain struct pthread size (#2034494)
- add --enable-host-pie, build the compilers as PIE (#2044917)

* Mon Feb  7 2022 Marek Polacek <polacek@redhat.com> 11.2.1-9.2
- add support for relocation of the PCH data (pch/71934, #2044917)
- remove 30_threads/future/members/poll.cc (#2050090)
- avoid overly-greedy match in dejagnu regexp (#2050089)

* Mon Jan 31 2022 Marek Polacek <polacek@redhat.com> 11.2.1-9.1
- don't set -Wl,-rpath when building annobin (#2047356)

* Fri Jan 28 2022 Marek Polacek <polacek@redhat.com> 11.2.1-9
- update from releases/gcc-11-branch (#2047296)
  - PRs fortran/104127, fortran/104212, fortran/104227, target/101529
- fix up va-opt-6.c testcase

* Fri Jan 28 2022 Marek Polacek <polacek@redhat.com> 11.2.1-8
- update from releases/gcc-11-branch (#2047296)
  - PRs ada/103538, analyzer/101962, bootstrap/103688, c++/85846, c++/95009,
	c++/98394, c++/99911, c++/100493, c++/101715, c++/102229, c++/102933,
	c++/103012, c++/103198, c++/103480, c++/103703, c++/103714,
	c++/103758, c++/103783, c++/103831, c++/103912, c++/104055, c/97548,
	c/101289, c/101537, c/103587, c/103881, d/103604, debug/103838,
	debug/103874, fortran/67804, fortran/83079, fortran/101329,
	fortran/101762, fortran/102332, fortran/102717, fortran/102787,
	fortran/103411, fortran/103412, fortran/103418, fortran/103473,
	fortran/103505, fortran/103588, fortran/103591, fortran/103606,
	fortran/103607, fortran/103609, fortran/103610, fortran/103692,
	fortran/103717, fortran/103718, fortran/103719, fortran/103776,
	fortran/103777, fortran/103778, fortran/103782, fortran/103789,
	ipa/101354, jit/103562, libfortran/103634, libstdc++/100017,
	libstdc++/102994, libstdc++/103453, libstdc++/103501,
	libstdc++/103549, libstdc++/103877, libstdc++/103919,
	middle-end/101751, middle-end/102860, middle-end/103813, objc/103639,
	preprocessor/89971, preprocessor/102432, rtl-optimization/102478,
	rtl-optimization/103837, rtl-optimization/103860,
	rtl-optimization/103908, sanitizer/102911, target/102347,
	target/103465, target/103661, target/104172, target/104188,
	tree-optimization/101615, tree-optimization/103523,
	tree-optimization/103603, tree-optimization/103995

* Tue Jan 25 2022 Marek Polacek <polacek@redhat.com> 11.2.1-7.7
- do not undefine _hardened_build (#2044917)

* Mon Jan 24 2022 Marek Polacek <polacek@redhat.com> 11.2.1-7.6
- update annobin plugin patch (#2030667)

* Thu Jan 13 2022 Marek Polacek <polacek@redhat.com> 11.2.1-7.5
- update annobin plugin patch (#2030667)

* Fri Jan  7 2022 Marek Polacek <polacek@redhat.com> 11.2.1-7.4
- update annobin plugin patch (#2030667)

* Tue Jan  4 2022 Marek Polacek <polacek@redhat.com> 11.2.1-7.3
- fix dg-ice tests (#1996047)

* Tue Jan  4 2022 Marek Polacek <polacek@redhat.com> 11.2.1-7.2
- update annobin plugin patch (#2030667)

* Thu Dec 16 2021 Marek Polacek <polacek@redhat.com> 11.2.1-7.1
- build annobin plugin (patch by Nick Clifton) (#2030667)

* Tue Dec  7 2021 Marek Polacek <polacek@redhat.com> 11.2.1-7
- update from releases/gcc-11-branch (#1996858)
  - PRs ada/100486, c++/70796, c++/92746, c++/93286, c++/94490, c++/102642,
	c++/102786, debug/101378, debug/103046, debug/103315, fortran/87711,
	fortran/87851, fortran/97896, fortran/99061, fortran/99348,
	fortran/102521, fortran/102685, fortran/102715, fortran/102745,
	fortran/102816, fortran/102817, fortran/102917, fortran/103137,
	fortran/103138, fortran/103392, gcov-profile/100520, ipa/102714,
	ipa/102762, ipa/103052, ipa/103246, ipa/103267, libstdc++/96416,
	libstdc++/98421, libstdc++/100117, libstdc++/100153, libstdc++/100748,
	libstdc++/101571, libstdc++/101608, libstdc++/102894,
	libstdc++/103022, libstdc++/103086, libstdc++/103133,
	libstdc++/103240, libstdc++/103381, middle-end/64888,
	middle-end/101480, middle-end/102431, middle-end/102518,
	middle-end/103059, middle-end/103181, middle-end/103248,
	middle-end/103384, preprocessor/103130, rtl-optimization/102356,
	rtl-optimization/102842, target/101985, target/102976, target/102991,
	target/103205, target/103274, target/103275, testsuite/102690,
	tree-optimization/100393, tree-optimization/102139,
	tree-optimization/102505, tree-optimization/102572,
	tree-optimization/102788, tree-optimization/102789,
	tree-optimization/102798, tree-optimization/102970,
	tree-optimization/103192, tree-optimization/103204,
	tree-optimization/103237, tree-optimization/103255,
	tree-optimization/103435
- fix up #__VA_OPT__ handling (PR preprocessor/103415)

* Mon Nov 29 2021 Marek Polacek <polacek@redhat.com> 11.2.1-6.1
- add -Wbidi-chars patch (#2008393)

* Wed Oct 27 2021 Marek Polacek <polacek@redhat.com> 11.2.1-6
- update from releases/gcc-11-branch (#1996858)
- build target shared libraries with -Wl,-z,relro,-z,now
- add mwaitintrin.h on x86 (#2013860)
- improve generated code with extern thread_local constinit vars
  with trivial dtors
- add support for C++20 #__VA_OPT__
- add bundled(libbacktrace) and bundled(libffi) provides (#1993932)

* Thu Aug 12 2021 Marek Polacek <polacek@redhat.com> 11.2.1-2.2
- bootstrap with -Wl,-z,relro,-z,now, apply libgcc hardening patch (#1988450)
- fix libsanitizer with non-constant SIGSTKSZ (#1992727)

* Fri Jul 30 2021 Marek Polacek <polacek@redhat.com> 11.2.1-2.1
- enable LTO profiledbootstrap on all arches (#1986141)

* Thu Jul 29 2021 Florian Weimer <fweimer@redhat.com> 11.2.1-2
- Rebuild with changed aarch64 build flags (#1984652)

* Wed Jul 28 2021 Marek Polacek <polacek@redhat.com> 11.2.1-1
- update from releases/gcc-11-branch (#1986836)
  - GCC 11.2 release
  - PRs middle-end/101586, rtl-optimization/101562
- enable LTO profiledbootstrap on x86_64, i?86, ppc64le and s390x for rhel9
  (#1986141)

* Wed Jun 23 2021 David Malcolm <dmalcolm@redhat.com> 11.1.1-6.1
- drop patch that retained broken std::call_once symbols
  (#1937700, PR libstdc++/99341)

* Wed Jun 23 2021 Jakub Jelinek <jakub@redhat.com> 11.1.1-6
- update from releases/gcc-11-branch
  - PRs c++/100876, c++/100879, c++/101106, c/100619, c/100783, fortran/95501,
	fortran/95502, fortran/100283, fortran/101123, inline-asm/100785,
	libstdc++/91488, libstdc++/95833, libstdc++/100806, libstdc++/100940,
	middle-end/100250, middle-end/100307, middle-end/100574,
	middle-end/100684, middle-end/100732, middle-end/100876,
	middle-end/101062, middle-end/101167, target/99842, target/99939,
	target/100310, target/100777, target/100856, target/100871,
	target/101016

* Thu Jun 17 2021 Jakub Jelinek <jakub@redhat.com> 11.1.1-5
- update from releases/gcc-11-branch
  - PRs bootstrap/100731, c++/91706, c++/91859, c++/95719, c++/100065,
	c++/100102, c++/100580, c++/100666, c++/100796, c++/100797,
	c++/100862, c++/100946, c++/100963, c++/101029, c++/101078, c/100902,
	c/100920, d/100882, d/100935, d/100964, d/100967, d/100999,
	debug/100852, fortran/82376, fortran/98301, fortran/99839,
	fortran/100965, ipa/100791, libstdc++/98842, libstdc++/100475,
	libstdc++/100577, libstdc++/100631, libstdc++/100639,
	libstdc++/100676, libstdc++/100690, libstdc++/100768,
	libstdc++/100770, libstdc++/100824, libstdc++/100833,
	libstdc++/100889, libstdc++/100894, libstdc++/100900,
	libstdc++/100982, libstdc++/101034, libstdc++/101055,
	middle-end/100576, middle-end/100898, middle-end/101009,
	preprocessor/100646, rtl-optimization/100342, rtl-optimization/100590,
	rtl-optimization/101008, target/100333, target/100885, target/100887,
	target/101046, testsuite/100750, tree-optimization/100934,
	tree-optimization/100981

* Mon Jun 14 2021 Florian Weimer <fweimer@redhat.com> 11.1.1-4
- NVR bump to enable rebuild in side tag

* Mon May 31 2021 Jakub Jelinek <jakub@redhat.com> 11.1.1-3
- update from releases/gcc-11-branch
  - PRs bootstrap/100552, c++/100205, c++/100261, c++/100281, c++/100367,
	c++/100372, c++/100489, c++/100502, c++/100634, c++/100644,
	c++/100659, c/100550, fortran/98411, fortran/100551, fortran/100602,
	fortran/100633, fortran/100656, ipa/100513, libstdc++/100361,
	libstdc++/100479, libstdc++/100630, middle-end/100471,
	middle-end/100508, middle-end/100509, preprocessor/100392,
	target/94177, target/99725, target/99960, target/99977, target/100419,
	target/100563, target/100626, target/100767, testsuite/96488,
	tree-optimization/100492, tree-optimization/100519

* Wed May 12 2021 Jakub Jelinek <jakub@redhat.com> 11.1.1-2
- update from releases/gcc-11-branch
  - PRs c++/98032, c++/100319, c++/100362, c/100450, fortran/100274,
	ipa/100308, libgomp/100352, libstdc++/99006, libstdc++/99453,
	libstdc++/100259, libstdc++/100298, libstdc++/100384,
	rtl-optimization/84878, rtl-optimization/100225,
	rtl-optimization/100230, rtl-optimization/100263,
	rtl-optimization/100411, target/99988, target/100217, target/100232,
	target/100236, target/100270, target/100305, target/100311,
	target/100375, target/100402, tree-optimization/96513,
	tree-optimization/100253, tree-optimization/100278,
	tree-optimization/100329, tree-optimization/100414
- fix build with removed linux/cyclades.h header (PR sanitizer/100379)
- fix up mausezahn miscompilation (#1958887, PR tree-optimization/100566)

* Wed Apr 28 2021 Jakub Jelinek <jakub@redhat.com> 11.1.1-1
- update from releases/gcc-11-branch
  - GCC 11.1 release
  - PRs c++/93383, c++/95291, c++/96380, c++/99200, c++/99683, c++/100161,
	debug/100255, fortran/100154, fortran/100218, libstdc++/100290,
	rtl-optimization/100254, target/98952, target/100200,
	tree-optimization/100239
- fix ICE in aarch64_add_offset_1_temporaries (PR target/100302)

* Fri Apr 23 2021 Jakub Jelinek <jakub@redhat.com> 11.0.1-0.7
- update from trunk and releases/gcc-11 branch
  - GCC 11.1-rc2
  - PRs libstdc++/100179, target/100182

* Thu Apr 22 2021 Jakub Jelinek <jakub@redhat.com> 11.0.1-0.6
- update from trunk and releases/gcc-11 branch
  - GCC 11.1-rc1
  - PRs ada/99360, c++/97536, c/100143, d/98058, d/98457, d/98494, d/98584,
	d/99794, demangler/100177, fortran/100110, libstdc++/95983,
	libstdc++/100146, libstdc++/100164, preprocessor/100142,
	rtl-optimization/99927, target/100108, testsuite/100176,
	tree-optimization/100081
- fix a cprop -fcompare-debug bug (PR rtl-optimization/100148)

* Sun Apr 18 2021 Jakub Jelinek <jakub@redhat.com> 11.0.1-0.5
- update from trunk
  - PRs analyzer/98599, analyzer/99042, analyzer/99212, analyzer/99774,
	analyzer/99886, analyzer/99906, analyzer/100011, c++/41723, c++/49951,
	c++/52202, c++/52625, c++/58123, c++/80456, c++/83476, c++/88742,
	c++/90215, c++/90479, c++/90674, c++/91241, c++/91849, c++/91933,
	c++/92918, c++/93085, c++/93295, c++/93314, c++/93867, c++/94529,
	c++/95317, c++/95486, c++/95870, c++/96311, c++/96673, c++/96873,
	c++/97121, c++/97134, c++/97679, c++/97974, c++/98440, c++/98800,
	c++/98852, c++/99008, c++/99066, c++/99118, c++/99180, c++/99201,
	c++/99380, c++/99478, c++/99700, c++/99803, c++/99806, c++/99833,
	c++/99844, c++/99850, c++/99859, c++/99874, c++/99885, c++/99899,
	c++/99901, c++/99961, c++/99994, c++/100006, c++/100032, c++/100054,
	c++/100078, c++/100079, c++/100091, c++/100101, c++/100111, c/98852,
	c/99420, c/99972, c/99990, d/99812, d/99914, d/99917, debug/99830,
	fortran/63797, fortran/99307, fortran/99817, fortran/100018,
	fortran/100094, jit/100096, libfortran/78314, libgomp/99984,
	libstdc++/96657, libstdc++/99402, libstdc++/99433, libstdc++/99805,
	libstdc++/99985, libstdc++/99995, libstdc++/100044, libstdc++/100060,
	lto/98599, lto/99849, lto/99857, middle-end/55288, middle-end/84877,
	middle-end/84991, middle-end/84992, middle-end/86058,
	middle-end/90779, middle-end/98088, middle-end/99883,
	middle-end/99989, preprocessor/99446, rtl-optimization/98601,
	rtl-optimization/98689, rtl-optimization/99596,
	rtl-optimization/99905, rtl-optimization/99929,
	rtl-optimization/100066, sanitizer/99877, sanitizer/100114,
	target/87763, target/99246, target/99647, target/99648, target/99748,
	target/99767, target/99781, target/99872, target/100028,
	target/100048, target/100056, target/100067, target/100075,
	testsuite/99955, testsuite/100071, testsuite/100073,
	tree-optimization/82800, tree-optimization/97513,
	tree-optimization/98736, tree-optimization/99873,
	tree-optimization/99880, tree-optimization/99924,
	tree-optimization/99947, tree-optimization/99954,
	tree-optimization/100053
- for %%{rhel} == 9, default to -march=z14 -mtune=z15 on s390x and
  to -mcpu=power9 -mtune=power9 on ppc64le

* Fri Apr  9 2021 Marek Polacek <polacek@redhat.com> 11.0.1-0.3.1
- for %%{rhel} == 9, default to -march=z14 -mtune=z15 on s390x and
  to -mcpu=power9 -mtune=power9 on ppc64le

* Mon Apr  5 2021 Jakub Jelinek <jakub@redhat.com> 11.0.1-0.4
- update from trunk
  - PRs ada/99802, analyzer/93695, analyzer/99044, analyzer/99716,
	analyzer/99771, bootstrap/98860, c++/90664, c++/91217, c++/91416,
	c++/94751, c++/97900, c++/97938, c++/98352, c++/99331, c++/99445,
	c++/99565, c++/99583, c++/99584, c++/99586, c++/99643, c++/99672,
	c++/99705, c++/99745, c++/99790, c++/99815, c++/99831, c++/99869,
	d/91595, d/99691, debug/99334, fortran/99369, fortran/99602,
	fortran/99651, fortran/99818, fortran/99840, ipa/98265, ipa/99122,
	ipa/99466, ipa/99751, libstdc++/99533, lto/99447, middle-end/65182,
	rtl-optimization/97141, rtl-optimization/98726,
	rtl-optimization/99863, target/96974, target/97653, target/98119,
	target/98136, target/98209, target/99037, target/99133, target/99216,
	target/99555, target/99718, target/99724, target/99727, target/99744,
	target/99753, target/99766, target/99773, target/99786, target/99808,
	target/99813, target/99820, target/99822, testsuite/98125,
	tree-optimization/48483, tree-optimization/55060,
	tree-optimization/59970, tree-optimization/61112,
	tree-optimization/61677, tree-optimization/61869,
	tree-optimization/96573, tree-optimization/96974,
	tree-optimization/97009, tree-optimization/98268,
	tree-optimization/99726, tree-optimization/99746,
	tree-optimization/99777, tree-optimization/99807,
	tree-optimization/99824, tree-optimization/99825,
	tree-optimization/99856, tree-optimization/99863,
	tree-optimization/99882

* Wed Mar 24 2021 Jakub Jelinek <jakub@redhat.com> 11.0.1-0.3
- update from trunk
  - PRs analyzer/99614, c++/99239, c++/99283, c++/99318, c++/99425, c++/99456,
	c++/99480, c++/99687, c/99588, fortran/93660, fortran/99688,
	rtl-optimization/99680, target/97252, target/97926, target/98914,
	target/99540, target/99581, target/99652, target/99660, target/99661,
	target/99663, target/99679, target/99702, target/99704, target/99733,
	tree-optimization/99296, tree-optimization/99656,
	tree-optimization/99694, tree-optimization/99721

* Fri Mar 19 2021 Jakub Jelinek <jakub@redhat.com> 11.0.1-0.2
- update from trunk
  - PRs c++/90448, c++/96268, c++/96749, c++/97973, c++/98480, c++/98704,
	c++/99047, c++/99108, c++/99238, c++/99248, c++/99285, c++/99423,
	c++/99436, c++/99459, c++/99472, c++/99496, c++/99500, c++/99507,
	c++/99508, c++/99509, c++/99528, c++/99601, c++/99613, c++/99617,
	fortran/49278, fortran/96983, fortran/97927, fortran/98858,
	fortran/99125, fortran/99205, fortran/99345, fortran/99514,
	fortran/99545, ipa/99517, libstdc++/99172, libstdc++/99341,
	libstdc++/99413, libstdc++/99536, libstdc++/99537, middle-end/97631,
	middle-end/98266, middle-end/99502, middle-end/99641, objc++/49070,
	sanitizer/98920, target/98092, target/98959, target/99070,
	target/99094, target/99102, target/99422, target/99437, target/99454,
	target/99463, target/99464, target/99492, target/99504, target/99542,
	target/99563, target/99592, target/99600, testsuite/97680,
	testsuite/98245, testsuite/99292, testsuite/99498, testsuite/99626,
	testsuite/99636, tree-optimization/98834, tree-optimization/99305,
	tree-optimization/99489, tree-optimization/99510,
	tree-optimization/99523, tree-optimization/99544
  - fix ARM ICE in neon_output_shift_immediate (#1922599, PR target/99593)
- avoid false positive aarch64 -Wpsabi notes in some cases (PR target/91710)
- fix a -fcompare-debug failure caused by C FE bug (PR debug/99230)
- fix up -gdwarf-5 -gsplit-dwarf ranges handling (PR debug/99490)
- fix up handling of > 64 bit constants in dwarf2out (PR debug/99562,
  PR debug/66728)
- reject invalid C++ structured bindings that need reference to void
  (PR c++/99650)
- include private isl 0.18 in the package instead of relying on old
  distro version

* Sun Mar  7 2021 Jakub Jelinek <jakub@redhat.com> 11.0.1-0.1
- update from trunk
  - PRs ada/98996, ada/99020, ada/99095, ada/99264, analyzer/96374,
	analyzer/99193, bootstrap/92002, bootstrap/98590, c++/82959,
	c++/88146, c++/90333, c++/94521, c++/95451, c++/95615, c++/95616,
	c++/95675, c++/95822, c++/96078, c++/96330, c++/96443, c++/96474,
	c++/96960, c++/97034, c++/97587, c++/98118, c++/98318, c++/98810,
	c++/98990, c++/99009, c++/99103, c++/99120, c++/99166, c++/99170,
	c++/99176, c++/99213, c++/99245, c++/99251, c++/99287, c++/99294,
	c++/99344, c++/99362, c++/99365, c++/99374, c++/99377, c++/99389,
	c/99137, c/99275, c/99304, c/99323, c/99324, c/99325, c/99363,
	d/99337, debug/66668, debug/99090, debug/99319, fortran/57871,
	fortran/99300, fortran/99303, fortran/99355, gcov-profile/97461,
	gcov-profile/99105, gcov-profile/99385, gcov-profile/99406, ipa/98078,
	ipa/98338, libbacktrace/98818, libfortran/81986, libfortran/99218,
	libgomp/98738, libstdc++/99265, libstdc++/99270, libstdc++/99301,
	libstdc++/99382, libstdc++/99396, middle-end/93235, middle-end/94655,
	middle-end/95757, middle-end/96963, middle-end/97172,
	middle-end/97855, middle-end/99276, middle-end/99281,
	middle-end/99295, middle-end/99322, other/99288,
	rtl-optimization/99376, target/44107, target/48097, target/95798,
	target/98996, target/99085, target/99234, target/99271, target/99279,
	target/99313, target/99321, target/99381, testsuite/99233,
	tree-optimization/80635, tree-optimization/99253
- fix debug info for __fp16 constants (PR debug/99388)

* Thu Feb 25 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.20
- update from trunk
  - PRs analyzer/94596, analyzer/98969, analyzer/99196, c++/94034, c++/94546,
	c++/95468, c++/95888, c++/96251, c++/96926, c++/97246, c++/97582,
	c++/97742, c++/98718, c++/98741, c++/98988, c++/99023, c++/99030,
	c++/99031, c++/99033, c++/99035, c++/99039, c++/99040, c++/99062,
	c++/99063, c++/99071, c++/99072, c++/99074, c++/99116, c++/99132,
	c++/99150, c++/99153, c++/99174, c++/99208, c/97172, c/99055, c/99136,
	c/99224, debug/96997, debug/98755, fortran/98342, fortran/98686,
	fortran/98897, fortran/98979, fortran/99010, fortran/99027,
	fortran/99043, fortran/99060, fortran/99111, fortran/99124,
	fortran/99146, fortran/99171, fortran/99206, fortran/99226,
	inline-asm/98096, inline-asm/99123, ipa/97346, ipa/99003, ipa/99029,
	ipa/99034, jit/99126, libfortran/95647, libfortran/98825,
	libgcc/99236, libstdc++/88881, libstdc++/97549, libstdc++/98389,
	libstdc++/99058, libstdc++/99077, libstdc++/99096, libstdc++/99181,
	libstdc++/99261, middle-end/38474, middle-end/99007, middle-end/99109,
	middle-end/99122, preprocessor/96391, rtl-optimization/96264,
	rtl-optimization/98439, rtl-optimization/98791,
	rtl-optimization/98872, rtl-optimization/99054, sanitizer/99106,
	sanitizer/99168, target/85074, target/96166, target/97417,
	target/98491, target/98657, target/98931, target/98998, target/99025,
	target/99041, target/99100, target/99104, target/99113, target/99134,
	target/99157, testsuite/99173, translation/99167,
	tree-optimization/38474, tree-optimization/92879,
	tree-optimization/98772, tree-optimization/99002,
	tree-optimization/99024, tree-optimization/99026,
	tree-optimization/99079, tree-optimization/99142,
	tree-optimization/99149, tree-optimization/99165,
	tree-optimization/99204, tree-optimization/99220,
	tree-optimization/99225

* Wed Feb 10 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.19
- update from trunk
  - PRs analyzer/93355, analyzer/96374, analyzer/98575, analyzer/98918,
	c++/20408, c++/84494, c++/90926, c++/95192, c++/96199, c++/96462,
	c++/96905, c++/97804, c++/97878, c++/98295, c++/98326, c++/98355,
	c++/98531, c++/98570, c++/98717, c++/98802, c++/98835, c++/98899,
	c++/98926, c++/98929, c++/98944, c++/98947, c++/98951, c++/98994,
	c/97882, c/97932, d/98910, d/98921, debug/98656, driver/98943,
	fortran/91862, fortran/98913, libstdc++/70303, libstdc++/99021,
	lto/96591, lto/98912, lto/98971, middle-end/97172, middle-end/97487,
	middle-end/97971, middle-end/98465, middle-end/98974,
	middle-end/99004, preprocessor/98882, rtl-optimization/96015,
	target/97510, target/98172, target/98537, target/98743, target/98957,
	testsuite/98243, testsuite/98325, tree-optimization/97960,
	tree-optimization/98287, tree-optimization/98499,
	tree-optimization/98848, tree-optimization/98855,
	tree-optimization/98863, tree-optimization/98928,
	tree-optimization/98937, tree-optimization/99017

* Sat Jan 30 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.18
- update from trunk
  - PRs ada/98228, bootstrap/98839, c++/33661, c++/88548, c++/94775,
	c++/96137, c++/97474, c++/97566, c++/97874, c++/98463, c++/98646,
	c++/98770, c++/98841, c++/98843, c++/98847, d/98806, debug/98331,
	debug/98811, fortran/67539, fortran/70070, fortran/86470,
	fortran/93924, fortran/93925, fortran/96843, fortran/98472,
	fortran/98517, libstdc++/66414, lto/85574, middle-end/98726,
	middle-end/98807, rtl-optimization/80960, rtl-optimization/97684,
	rtl-optimization/98144, rtl-optimization/98863, sanitizer/98828,
	target/97701, target/98730, target/98799, target/98827, target/98833,
	target/98849, target/98853, testsuite/98771, testsuite/98870,
	tree-optimization/97260, tree-optimization/97627,
	tree-optimization/98854, tree-optimization/98866

* Sat Jan 23 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.17
- update from trunk
  - PRs ada/98740, c++/41437, c++/58993, c++/71879, c++/82613, c++/95434,
	c++/96623, c++/97399, c++/97966, c++/98333, c++/98530, c++/98545,
	c++/98624, c++/98659, c++/98744, fortran/96320, fortran/98476,
	fortran/98565, fortran/98757, fortran/98763, gcov-profile/98739,
	ipa/97673, ipa/98330, ipa/98690, middle-end/98664, middle-end/98773,
	middle-end/98793, rtl-optimization/92294, rtl-optimization/98694,
	rtl-optimization/98722, rtl-optimization/98777, sanitizer/95693,
	target/79251, target/96372, target/96891, target/98065, target/98093,
	target/98348, target/98636, testsuite/97301, testsuite/98241,
	testsuite/98795, tree-optimization/47059, tree-optimization/90248,
	tree-optimization/96674, tree-optimization/98255,
	tree-optimization/98535, tree-optimization/98758,
	tree-optimization/98766, tree-optimization/98786
  - ensure for empty CUs -gdwarf-5 emits at least the required 0th directory
    and filename entry in the .debug_line section (#1919243, PR debug/98796)
- fix aarch64 bug where emitted ubfix insn can't be assembled
  (PR target/98681)

* Wed Jan 20 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.16
- fix DWARF5 -g -flto -ffat-lto-objects, so that LTO sections can be stripped
  off later (PR debug/98765)
- fix GOMP_task caller stack corruption on s390x
- libgccjit DWARF5 fixes (PR debug/98751)

* Tue Jan 19 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.15
- update from trunk
  - PRs debug/98708, debug/98716, ipa/98222, libstdc++/98725, target/97847,
	testsuite/97299, testsuite/97494, testsuite/97987,
	tree-optimization/96271
  - fix miscompilation of portable signed multiplication overflow check
    (#1916576, PR tree-optimization/98727)
  - switch to DWARF 5 by default
- fix PRs c++/98672, c++/98687, c++/98742, middle-end/98638,
	  tree-optimization/98721

* Sat Jan 16 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.14
- update from trunk
  - PRs ada/98595, analyzer/98679, bootstrap/98696, c++/63707, c++/98231,
	c++/98372, c++/98538, c++/98591, c++/98626, c++/98642, fortran/98661,
	ipa/98652, jit/98586, libgomp/65099, libstdc++/98466, libstdc++/98471,
	preprocessor/95253, target/70454, target/71233, target/88836,
	target/95905, target/96938, target/98667, target/98671, target/98676,
	testsuite/96098, testsuite/96147, tree-optimization/92645,
	tree-optimization/96376, tree-optimization/96669,
	tree-optimization/96681, tree-optimization/96688,
	tree-optimization/96691, tree-optimization/98455,
	tree-optimization/98597, tree-optimization/98640,
	tree-optimization/98674, tree-optimization/98685
  - fix up pmovzx permutation SSE4.1 patterns (#1916240, PR target/98670)

* Wed Jan 13 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.13
- update from trunk
  - PRs analyzer/98628, c++/97284, c++/98481, c++/98556, c++/98611, c++/98620,
	c/98592, debug/97714, jit/98615, libstdc++/98613,
	rtl-optimization/98603, target/97875, target/97969, target/98612,
	testsuite/98225, testsuite/98602, tree-optimization/91403,
	tree-optimization/95731, tree-optimization/95852,
	tree-optimization/95867, tree-optimization/98526,
	tree-optimization/98550, tree-optimization/98629
  - fix ICEs in print_mem_ref (#1915400, #1915437, #1915781, PR c/98597)

* Sat Jan  9 2021 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.12
- update from trunk
  - PRs analyzer/97072, analyzer/97074, analyzer/98073, analyzer/98223,
	analyzer/98293, analyzer/98564, analyzer/98580, bootstrap/98324,
	bootstrap/98506, c++/82099, c++/95768, c++/96045, c++/96504,
	c++/97597, c++/98206, c++/98305, c++/98316, c++/98329, c++/98332,
	c++/98353, c++/98413, c++/98441, c++/98469, c++/98515, c++/98551,
	c/98029, d/98427, fortran/83118, fortran/93701, fortran/93794,
	fortran/93833, fortran/97612, fortran/97694, fortran/97723,
	fortran/98022, fortran/98458, libstdc++/98384, middle-end/98160,
	middle-end/98578, other/98437, rtl-optimization/97144,
	rtl-optimization/97978, rtl-optimization/98214,
	rtl-optimization/98334, rtl-optimization/98403, target/89057,
	target/96793, target/97269, target/98461, target/98482, target/98495,
	target/98521, target/98522, target/98567, target/98585,
	testsuite/98489, testsuite/98566, tree-optimization/56719,
	tree-optimization/94785, tree-optimization/94802,
	tree-optimization/94994, tree-optimization/95401,
	tree-optimization/95582, tree-optimization/95771,
	tree-optimization/96239, tree-optimization/96782,
	tree-optimization/96928, tree-optimization/96930,
	tree-optimization/98282, tree-optimization/98291,
	tree-optimization/98302, tree-optimization/98308,
	tree-optimization/98371, tree-optimization/98381,
	tree-optimization/98393, tree-optimization/98428,
	tree-optimization/98464, tree-optimization/98474,
	tree-optimization/98513, tree-optimization/98514,
	tree-optimization/98516, tree-optimization/98544,
	tree-optimization/98560, tree-optimization/98568

* Wed Dec 23 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.11
- update from trunk
  - PRs bootstrap/98300, bootstrap/98380, bootstrap/98412, c++/67343,
	c++/93480, c++/96840, c++/98340, c++/98343, c++/98353, c++/98383,
	c/98047, c/98260, d/98067, fortran/83118, fortran/92587,
	fortran/96012, fortran/98284, fortran/98307, go/98402,
	libstdc++/46447, libstdc++/93151, libstdc++/96083, libstdc++/98319,
	libstdc++/98344, libstdc++/98370, libstdc++/98374, libstdc++/98377,
	middle-end/98366, other/98400, other/98409, rtl-optimization/98271,
	rtl-optimization/98276, rtl-optimization/98289,
	rtl-optimization/98347, sanitizer/97868, target/96793, target/98146,
	target/98177, target/98280, tree-optimization/96239,
	tree-optimization/97750, tree-optimization/98272,
	tree-optimization/98279, tree-optimization/98378,
	tree-optimization/98407

* Thu Dec 17 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.10
- apply workaround for profiledbootstrap x86_64 failure
- put g++-mapper-server into the right directory

* Wed Dec 16 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.8
- update from trunk
  - PRs ada/98230, bootstrap/98188, c++/57111, c++/59238, c++/68451,
	c++/78173, c++/91506, c++/93083, c++/96299, c++/97093, c++/97517,
	c++/98043, c++/98103, c++/98122, c++/98126, c++/98130, c++/98187,
	c++/98193, c/97981, c/98200, d/98277, fortran/90207, fortran/98016,
	fortran/98022, gcov-profile/98273, libstdc++/98108, libstdc++/98226,
	lto/98275, middle-end/94600, middle-end/98160, middle-end/98166,
	middle-end/98183, middle-end/98190, middle-end/98205,
	middle-end/98264, rtl-optimization/97092, rtl-optimization/97421,
	rtl-optimization/98212, rtl-optimization/98229, sanitizer/98204,
	target/58901, target/66791, target/92469, target/94440, target/95294,
	target/96226, target/96470, target/97865, target/97872, target/98100,
	target/98147, target/98152, target/98161, target/98162, target/98219,
	target/98274, testsuite/95900, testsuite/98123, testsuite/98156,
	testsuite/98239, testsuite/98240, testsuite/98242, testsuite/98244,
	tree-optimization/95582, tree-optimization/96094,
	tree-optimization/96232, tree-optimization/96272,
	tree-optimization/96344, tree-optimization/96685,
	tree-optimization/97559, tree-optimization/97929,
	tree-optimization/98069, tree-optimization/98113,
	tree-optimization/98117, tree-optimization/98137,
	tree-optimization/98169, tree-optimization/98174,
	tree-optimization/98180, tree-optimization/98182,
	tree-optimization/98191, tree-optimization/98192,
	tree-optimization/98199, tree-optimization/98211,
	tree-optimization/98213, tree-optimization/98235,
	tree-optimization/98256
  - C++20 modules support
  - fix up __patchable_function_entries handling when gcc is configured
    against recent binutils (#1907945)
- fix up handling of non-memory VIEW_CONVERT_EXPRs in PRE
  (PR tree-optimization/98282)

* Fri Dec  4 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.7
- update from trunk
  - PRs bootstrap/97983, c++/80780, c++/90629, c++/93093, c++/97187,
	c++/97947, c++/97975, c++/97993, c++/98019, c++/98054, c++/98072,
	c++/98104, c++/98107, c++/98115, c++/98116, c/65455, c/92935, c/97880,
	c/98087, d/87788, d/87818, d/98025, debug/97989, fortran/95342,
	fortran/98010, fortran/98011, fortran/98013, ipa/88702, ipa/98057,
	ipa/98075, jit/97867, libgcc/97543, libgcc/97643, libstdc++/65480,
	libstdc++/68735, libstdc++/93121, libstdc++/98001, libstdc++/98003,
	middle-end/89428, middle-end/92936, middle-end/92940,
	middle-end/93195, middle-end/93197, middle-end/94527,
	middle-end/97373, middle-end/97595, middle-end/98070,
	middle-end/98082, middle-end/98099, other/98027, plugins/98059,
	preprocessor/97602, rtl-optimization/97459, rtl-optimization/97777,
	rtl-optimization/97954, rtl-optimization/98037, target/96607,
	target/96906, target/97642, target/97770, target/97939, target/98063,
	target/98079, target/98086, testsuite/98002, testsuite/98036,
	testsuite/98085, tree-optimization/14799, tree-optimization/88702,
	tree-optimization/96679, tree-optimization/96708,
	tree-optimization/97630, tree-optimization/97953,
	tree-optimization/97979, tree-optimization/97997,
	tree-optimization/98024, tree-optimization/98048,
	tree-optimization/98064, tree-optimization/98066,
	tree-optimization/98084

* Thu Nov 26 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.6
- update from trunk
  - PRs bootstrap/94982, bootstrap/97622, bootstrap/97933, c++/97899, c/97958,
	fortran/85796, libstdc++/67791, libstdc++/97935, libstdc++/97936,
	libstdc++/97944, middle-end/97943, middle-end/97956,
	rtl-optimization/95862, target/91816, target/97534, target/97950,
	tree-optimization/96929, tree-optimization/97849,
	tree-optimization/97964

* Tue Nov 24 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.5
- update from trunk
  - PRs c++/94695, c++/97427, c++/97839, c++/97846, c++/97881, c++/97904,
	c/95630, d/97889, libstdc++/97948, tree-optimization/95853

* Sat Nov 21 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.4
- update from trunk
  - PRs ada/97805, ada/97859, analyzer/97668, analyzer/97893, bootstrap/57076,
	bootstrap/97666, bootstrap/97857, c++/25814, c++/52830, c++/63287,
	c++/67453, c++/78209, c++/81660, c++/87765, c++/88115, c++/88982,
	c++/89565, c++/90799, c++/91318, c++/93107, c++/93907, c++/95808,
	c++/97388, c++/97412, c++/97453, c++/97479, c++/97518, c++/97523,
	c++/97632, c++/97663, c++/97670, c++/97675, c++/97762, c++/97790,
	c++/97871, c++/97877, c++/97895, c++/97905, c++/97918, c/90628,
	c/97748, c/97860, d/97644, d/97842, d/97843, debug/97060, debug/97599,
	debug/97718, driver/97574, fortran/90111, fortran/92793,
	fortran/94358, fortran/95847, fortran/97652, fortran/97655,
	fortran/97768, fortran/97782, ipa/97578, ipa/97660, ipa/97695,
	ipa/97698, ipa/97816, jit/87291, libstdc++/55394, libstdc++/66146,
	libstdc++/83938, libstdc++/84323, libstdc++/88101, libstdc++/92285,
	libstdc++/92546, libstdc++/93421, libstdc++/93456, libstdc++/94971,
	libstdc++/95989, libstdc++/96269, libstdc++/96958, libstdc++/97415,
	libstdc++/97600, libstdc++/97613, libstdc++/97719, libstdc++/97729,
	libstdc++/97731, libstdc++/97758, libstdc++/97798, libstdc++/97828,
	libstdc++/97869, lto/97290, lto/97508, middle-end/85811,
	middle-end/95673, middle-end/97267, middle-end/97556,
	middle-end/97579, middle-end/97840, middle-end/97862,
	middle-end/97879, objc/77404, objc/90707, objc/97854, other/97911,
	pch/86674, pch/97593, preprocessor/97858, rtl-optimization/92180,
	rtl-optimization/97705, sanitizer/95634, target/31799, target/85486,
	target/91489, target/93449, target/96307, target/96770, target/96791,
	target/96933, target/96967, target/96998, target/97140, target/97194,
	target/97205, target/97326, target/97528, target/97532, target/97540,
	target/97638, target/97682, target/97685, target/97715, target/97726,
	target/97727, target/97730, target/97870, target/97873,
	testsuite/80219, testsuite/85303, testsuite/97117, testsuite/97688,
	testsuite/97788, testsuite/97797, testsuite/97803,
	tree-optimization/80928, tree-optimization/83072,
	tree-optimization/91029, tree-optimization/93781,
	tree-optimization/94406, tree-optimization/96671,
	tree-optimization/96789, tree-optimization/97223,
	tree-optimization/97424, tree-optimization/97558,
	tree-optimization/97609, tree-optimization/97623,
	tree-optimization/97626, tree-optimization/97633,
	tree-optimization/97650, tree-optimization/97678,
	tree-optimization/97690, tree-optimization/97693,
	tree-optimization/97706, tree-optimization/97709,
	tree-optimization/97721, tree-optimization/97725,
	tree-optimization/97732, tree-optimization/97733,
	tree-optimization/97736, tree-optimization/97737,
	tree-optimization/97741, tree-optimization/97746,
	tree-optimization/97753, tree-optimization/97760,
	tree-optimization/97761, tree-optimization/97764,
	tree-optimization/97765, tree-optimization/97767,
	tree-optimization/97769, tree-optimization/97780,
	tree-optimization/97806, tree-optimization/97812,
	tree-optimization/97830, tree-optimization/97835,
	tree-optimization/97838, tree-optimization/97886,
	tree-optimization/97888, tree-optimization/97897,
	tree-optimization/97901
- add BuildRequires: make and Requires: make, the latter for -flto reasons

* Thu Oct 29 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.3
- update from trunk
  - PRs ada/97504, analyzer/96608, analyzer/97489, analyzer/97514,
	analyzer/97568, analyzer/97608, bootstrap/97451, c++/82239, c++/86773,
	c++/91741, c++/94799, c++/95132, c++/96241, c++/96575, c++/96675,
	c++/96742, c++/97328, c++/97438, c++/97511, c++/97573, c/94722,
	c/97463, fortran/45516, fortran/97454, gcov-profile/97461, ipa/97445,
	ipa/97576, ipa/97586, libstdc++/94268, libstdc++/95592,
	libstdc++/95609, libstdc++/95917, libstdc++/96713, libstdc++/97512,
	libstdc++/97570, lto/96680, lto/97524, middle-end/92942,
	middle-end/97521, middle-end/97552, rtl-optimization/97249,
	rtl-optimization/97439, rtl-optimization/97497, sanitizer/97414,
	target/87767, target/95151, target/95458, target/97360, target/97502,
	target/97506, target/97535, testsuite/81690, testsuite/97590,
	tree-optimization/66552, tree-optimization/97164,
	tree-optimization/97360, tree-optimization/97456,
	tree-optimization/97457, tree-optimization/97466,
	tree-optimization/97467, tree-optimization/97486,
	tree-optimization/97488, tree-optimization/97496,
	tree-optimization/97500, tree-optimization/97501,
	tree-optimization/97503, tree-optimization/97505,
	tree-optimization/97515, tree-optimization/97520,
	tree-optimization/97538, tree-optimization/97539,
	tree-optimization/97546, tree-optimization/97555,
	tree-optimization/97560, tree-optimization/97567,
	tree-optimization/97615
- for ELN default to -march=x86-64-v2 for x86 64-bit compilation and
  for s390x to -march=z13 -mtune=arch13

* Mon Oct 19 2020 Jakub Jelinek <jakub@redhat.com> 11.0.0-0.2
- new package
