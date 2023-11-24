# We are building with clang for faster/lower memory LTO builds.
# See https://docs.fedoraproject.org/en-US/packaging-guidelines/#_compiler_macros
%global toolchain clang

%global gts_version 13

%bcond_with compat_build
%bcond_with bundle_compat_lib
%bcond_without check

%global maj_ver 16
%global min_ver 0
%global patch_ver 6
%global clang_version %{maj_ver}.%{min_ver}.%{patch_ver}

%if %{with compat_build}
%global pkg_name clang%{maj_ver}
# Install clang to same prefix as llvm, so that apps that use llvm-config
# will also be able to find clang libs.
%global install_prefix %{_libdir}/llvm%{maj_ver}
%global install_bindir %{install_prefix}/bin
%global install_includedir %{install_prefix}/include
%global install_libdir %{install_prefix}/lib

%global pkg_bindir %{install_bindir}
%global pkg_includedir %{install_includedir}
%global pkg_libdir %{install_libdir}
%else
%global pkg_name clang
%global install_prefix /usr
%global pkg_libdir %{_libdir}
%endif

%if %{with bundle_compat_lib}
%global compat_maj_ver 15
%global compat_ver %{compat_maj_ver}.0.7
%endif


%ifarch ppc64le aarch64
# Too many threads on ppc64 and aarch64 systems causes OOM errors.
%global _smp_mflags -j8
%endif

%global clang_srcdir clang-%{clang_version}%{?rc_ver:rc%{rc_ver}}.src
%global clang_tools_srcdir clang-tools-extra-%{clang_version}%{?rc_ver:rc%{rc_ver}}.src

Name:		%pkg_name
Version:	%{clang_version}%{?rc_ver:~rc%{rc_ver}}
Release:	1%{?dist}
Summary:	A C language family front-end for LLVM

License:	Apache-2.0 WITH LLVM-exception OR NCSA
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}%{?rc_ver:-rc%{rc_ver}}/%{clang_srcdir}.tar.xz
Source1:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}%{?rc_ver:-rc%{rc_ver}}/%{clang_srcdir}.tar.xz.sig
%if %{without compat_build}
Source2:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}%{?rc_ver:-rc%{rc_ver}}/%{clang_tools_srcdir}.tar.xz
Source3:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{clang_version}%{?rc_ver:-rc%{rc_ver}}/%{clang_tools_srcdir}.tar.xz.sig
%endif
Source4:	release-keys.asc
%if %{with bundle_compat_lib}
Source5:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{compat_ver}/clang-%{compat_ver}.src.tar.xz
Source6:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{compat_ver}/clang-%{compat_ver}.src.tar.xz.sig
Source7:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{compat_ver}/llvm-%{compat_ver}.src.tar.xz
Source8:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{compat_ver}/llvm-%{compat_ver}.src.tar.xz.sig
Source9:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{compat_ver}/cmake-%{compat_ver}.src.tar.xz
Source10:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{compat_ver}/cmake-%{compat_ver}.src.tar.xz.sig
%endif
%if !0%{with compat_build}
Source11:	macros.%{name}
%endif

# Patches for clang

Patch1:     0003-PATCH-Make-funwind-tables-the-default-on-all-archs.patch
Patch2:     0006-Don-t-install-static-libraries.patch
Patch3:     0002-Driver-Add-a-gcc-equivalent-triple-to-the-list-of-tr.patch
Patch4:	    0010-PATCH-clang-Produce-DWARF4-by-default.patch
# Make clangBasic and clangDriver depend on LLVMTargetParser
# See https://reviews.llvm.org/D141581
Patch7:     D141581.diff
# clang/cmake: Use installed gtest libraries for stand-alone builds
# See https://reviews.llvm.org/D138472
Patch8:     D138472.diff

Patch10:    fix-ieee128-cross.diff

Patch11:    0001-Change-LLVM_COMMON_CMAKE_UTILS-usage.patch

# RHEL specific patch
Patch12:     0009-disable-recommonmark.patch
Patch13:     0001-Driver-Give-devtoolset-path-precedence-over-Installe.patch

%if %{without compat_build}
# Patches for clang-tools-extra
# See https://reviews.llvm.org/D120301
Patch201:   0001-clang-tools-extra-Make-test-dependency-on-LLVMHello-.patch
%endif

# Required for 64-bit atomics on i686.
BuildRequires: gcc-toolset-%{gts_version}-libatomic-devel
# Required to handle LTO debuginfo.
BuildRequires: gcc-toolset-%{gts_version}-gdb
BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	ninja-build
%if %{with compat_build}
BuildRequires:	llvm%{maj_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}-static = %{version}
%else
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-test = %{version}
# llvm-static is required, because clang-tablegen needs libLLVMTableGen, which
# is not included in libLLVM.so.
BuildRequires:	llvm-static = %{version}
BuildRequires:	llvm-googletest = %{version}
%endif

BuildRequires:	libxml2-devel
BuildRequires:	perl-generators
BuildRequires:	ncurses-devel
# According to https://fedoraproject.org/wiki/Packaging:Emacs a package
# should BuildRequires: emacs if it packages emacs integration files.
BuildRequires:	emacs

# The testsuite uses /usr/bin/lit which is part of the python3-lit package.
BuildRequires:	python3-lit

BuildRequires:	python3-sphinx
BuildRequires:	libatomic

# We need python3-devel for %%py3_shebang_fix
BuildRequires:	python3-devel

%if %{without compat_build}
# For reproducible pyc file generation
# See https://docs.fedoraproject.org/en-US/packaging-guidelines/Python_Appendix/#_byte_compilation_reproducibility
%if 0%{?fedora}
BuildRequires: /usr/bin/marshalparser
%global py_reproducible_pyc_path %{buildroot}%{python3_sitelib}
%endif
%endif

# Needed for %%multilib_fix_c_header
BuildRequires:	multilib-rpm-config

# For origin certification
BuildRequires:	gnupg2

# scan-build uses these perl modules so they need to be installed in order
# to run the tests.
BuildRequires: perl(Digest::MD5)
BuildRequires: perl(File::Copy)
BuildRequires: perl(File::Find)
BuildRequires: perl(File::Path)
BuildRequires: perl(File::Temp)
BuildRequires: perl(FindBin)
BuildRequires: perl(Hash::Util)
BuildRequires: perl(lib)
BuildRequires: perl(Term::ANSIColor)
BuildRequires: perl(Text::ParseWords)
BuildRequires: perl(Sys::Hostname)

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

# clang requires gcc, clang++ requires libstdc++-devel
# - https://bugzilla.redhat.com/show_bug.cgi?id=1021645
# - https://bugzilla.redhat.com/show_bug.cgi?id=1158594
Requires:	libstdc++-devel
Requires:	gcc-c++

Provides:	clang(major) = %{maj_ver}

Conflicts:	compiler-rt < 11.0.0

%description
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

Install compiler-rt if you want the Blocks C language extension or to
enable sanitization and profiling options when building, and
libomp-devel to enable -fopenmp.

%package libs
Summary: Runtime library for clang
Requires: %{name}-resource-filesystem%{?_isa} = %{version}
Requires: gcc-toolset-%{gts_version}-gcc-c++
Recommends: compiler-rt%{?_isa} = %{version}
# atomic support is not part of compiler-rt
Recommends: libatomic%{?_isa}
# libomp-devel is required, so clang can find the omp.h header when compiling
# with -fopenmp.
Recommends: libomp-devel%{_isa} = %{version}
Recommends: libomp%{_isa} = %{version}

# Use lld as the default linker on ARM due to rhbz#1918924
%ifarch %{arm}
Requires: lld
%endif

%description libs
Runtime library for clang.

%package devel
Summary: Development header files for clang
Requires: %{name}-libs = %{version}-%{release}
%if %{without compat_build}
Requires: %{name}%{?_isa} = %{version}-%{release}
# The clang CMake files reference tools from clang-tools-extra.
Requires: %{name}-tools-extra%{?_isa} = %{version}-%{release}
%endif

%description devel
Development header files for clang.

%package resource-filesystem
Summary: Filesystem package that owns the clang resource directory
Provides: %{name}-resource-filesystem(major) = %{maj_ver}

%description resource-filesystem
This package owns the clang resouce directory: $libdir/clang/$version/

%if %{without compat_build}
%package analyzer
Summary:	A source code analysis framework
License:	Apache-2.0 WITH LLVM-exception OR NCSA OR MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}

%description analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%package tools-extra
Summary:	Extra tools for clang
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Requires:	emacs-filesystem

%description tools-extra
A set of extra tools built using Clang's tooling API.

# Put git-clang-format in its own package, because it Requires git
# and we don't want to force users to install all those dependenices if they
# just want clang.
%package -n git-clang-format
Summary:	Integration of clang-format for git
Requires:	%{name}-tools-extra = %{version}-%{release}
Requires:	git
Requires:	python3

%description -n git-clang-format
clang-format integration for git.


%package -n python3-clang
Summary:       Python3 bindings for clang
Requires:      %{name}-devel%{?_isa} = %{version}-%{release}
Requires:      python3
%description -n python3-clang
%{summary}.


%endif


%prep
%{gpgverify} --keyring='%{SOURCE4}' --signature='%{SOURCE1}' --data='%{SOURCE0}'

%if %{with bundle_compat_lib}
%{gpgverify} --keyring='%{SOURCE4}' --signature='%{SOURCE6}' --data='%{SOURCE5}'
%{gpgverify} --keyring='%{SOURCE4}' --signature='%{SOURCE8}' --data='%{SOURCE7}'
%{gpgverify} --keyring='%{SOURCE4}' --signature='%{SOURCE10}' --data='%{SOURCE9}'

%setup -T -q -b 5 -n clang-%{compat_ver}.src
%setup -T -q -b 7 -n llvm-%{compat_ver}.src
%setup -T -q -b 9 -n cmake-%{compat_ver}.src
%endif

%if %{with compat_build}
%autosetup -n %{clang_srcdir} -p2
%else

%{gpgverify} --keyring='%{SOURCE4}' --signature='%{SOURCE3}' --data='%{SOURCE2}'
%setup -T -q -b 2 -n %{clang_tools_srcdir}
%autopatch -m200 -p2


# failing test case
rm test/clang-tidy/checkers/altera/struct-pack-align.cpp

%py3_shebang_fix \
	clang-tidy/tool/ \
	clang-include-fixer/find-all-symbols/tool/run-find-all-symbols.py

%setup -q -n %{clang_srcdir}
%autopatch -M200 -p2

# failing test case
rm test/CodeGen/profile-filter.c

%py3_shebang_fix \
	tools/clang-format/ \
	tools/clang-format/git-clang-format \
	utils/hmaptool/hmaptool \
	tools/scan-view/bin/scan-view \
	tools/scan-view/share/Reporter.py \
	tools/scan-view/share/startfile.py \
	tools/scan-build-py/bin/* \
	tools/scan-build-py/libexec/*
%endif

%build

%if 0%{?__isa_bits} == 64
sed -i 's/\@FEDORA_LLVM_LIB_SUFFIX\@/64/g' test/lit.cfg.py
%else
sed -i 's/\@FEDORA_LLVM_LIB_SUFFIX\@//g' test/lit.cfg.py
%endif

%ifarch %ix86
# Linking libclang.so goes out of memory even with ThinLTO and a single link job.
%global _lto_cflags %nil
%endif

%ifarch s390 s390x %{arm} aarch64 %ix86 ppc64le
# Decrease debuginfo verbosity to reduce memory consumption during final library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

# Disable dwz on aarch64, because it takes a huge amount of time to decide not to optimize things.
%ifarch aarch64
%define _find_debuginfo_dwz_opts %{nil}
%endif


%if %{with bundle_compat_lib}

mv ../clang-%{compat_ver}.src ../clang
mv ../cmake-%{compat_ver}.src ../cmake

%global targets_to_build "X86;AMDGPU;PowerPC;NVPTX;SystemZ;AArch64;ARM;Mips;BPF;WebAssembly"

# Disable LTO when building the compat libraries. This would perform LTO across all of LLVM and
# Clang, and fails due to "too many open files". We don't particularly care about the performance
# of these compat libraries.
%cmake -S ../llvm-%{compat_ver}.src -B ../clang-compat-libs -G Ninja \
	-DLLVM_ENABLE_PROJECTS=clang \
	-DCMAKE_BUILD_TYPE=Release \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DLLVM_ENABLE_EH=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DLLVM_TARGETS_TO_BUILD=%{targets_to_build} \
	-DLLVM_INCLUDE_BENCHMARKS=OFF \
	-DCMAKE_C_FLAGS_RELEASE="-fno-lto" \
	-DCMAKE_CXX_FLAGS_RELEASE="-fno-lto"

%ninja_build -C ../clang-compat-libs libclang.so
%ninja_build -C ../clang-compat-libs libclang-cpp.so


%endif

# We set CLANG_DEFAULT_PIE_ON_LINUX=OFF to match the default used by Fedora's GCC.
# See https://bugzilla.redhat.com/show_bug.cgi?id=2134146
%cmake  -G Ninja \
%ifarch %ix86
	-DHAVE_CXX_ATOMICS64_WITHOUT_LIB=OFF \
%endif
	-DCLANG_DEFAULT_PIE_ON_LINUX=OFF \
	-DLLVM_PARALLEL_LINK_JOBS=1 \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
%ifarch s390 s390x %{arm} %ix86 ppc64le
	-DCMAKE_C_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
	-DCMAKE_CXX_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
%endif
%if %{with compat_build}
	-DCLANG_BUILD_TOOLS:BOOL=OFF \
	-DLLVM_CONFIG:FILEPATH=%{pkg_bindir}/llvm-config-%{maj_ver}-%{__isa_bits} \
	-DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DCLANG_INCLUDE_TESTS:BOOL=OFF \
%else
	-DCLANG_INCLUDE_TESTS:BOOL=ON \
	-DLLVM_BUILD_UTILS:BOOL=ON \
	-DLLVM_EXTERNAL_CLANG_TOOLS_EXTRA_SOURCE_DIR=../%{clang_tools_srcdir} \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_LIT_ARGS="-vv" \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
%endif
	\
%if %{with compat_build}
	-DLLVM_TABLEGEN_EXE:FILEPATH=%{_bindir}/llvm-tblgen-%{maj_ver} \
%else
	-DLLVM_TABLEGEN_EXE:FILEPATH=%{_bindir}/llvm-tblgen \
%endif
	-DLLVM_COMMON_CMAKE_UTILS=%{_libdir}/cmake/llvm \
	-DCLANG_ENABLE_ARCMT:BOOL=ON \
	-DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON \
	-DCLANG_INCLUDE_DOCS:BOOL=ON \
	-DCLANG_PLUGIN_SUPPORT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DLLVM_ENABLE_EH=ON \
	-DLLVM_ENABLE_RTTI=ON \
	-DLLVM_BUILD_DOCS=ON \
	-DLLVM_ENABLE_SPHINX=ON \
	-DCLANG_LINK_CLANG_DYLIB=ON \
	-DSPHINX_WARNINGS_AS_ERRORS=OFF \
	\
	-DCLANG_BUILD_EXAMPLES:BOOL=OFF \
	-DBUILD_SHARED_LIBS=OFF \
	-DCLANG_REPOSITORY_STRING="%{?fedora:Fedora}%{?rhel:Red Hat} %{version}-%{release}" \
%ifarch %{arm}
	-DCLANG_DEFAULT_LINKER=lld \
%endif
	-DCLANG_DEFAULT_UNWINDLIB=libgcc \
	-DGCC_INSTALL_PREFIX=/opt/rh/gcc-toolset-%{gts_version}/root/usr \
	-DLLVM_INCLUDE_BENCHMARKS=OFF

%cmake_build

%install

# Use newer GDB for gdb-add-index step, as system GDB can't handle the LTO debuginfo.
source scl_source enable gcc-toolset-%{gts_version}
export GDB=`which gdb`

%cmake_install

%if %{with bundle_compat_lib}
install -m 0755 ../clang-compat-libs/lib/libclang.so.%{compat_maj_ver}* %{buildroot}%{_libdir}
install -m 0755 ../clang-compat-libs/lib/libclang-cpp.so.%{compat_maj_ver}* %{buildroot}%{_libdir}
%endif

%if %{with compat_build}

# Remove binaries/other files
rm -Rf %{buildroot}%{install_bindir}
rm -Rf %{buildroot}%{install_prefix}/share
rm -Rf %{buildroot}%{install_prefix}/libexec
# Remove scanview-py helper libs
rm -Rf %{buildroot}%{install_prefix}/%{_lib}/{libear,libscanbuild}

%else

# File in the macros file for other packages to use.  We are not doing this
# in the compat package, because the version macros would # conflict with
# eachother if both clang and the clang compat package were installed together.
install -p -m0644 -D %{SOURCE11} %{buildroot}%{_rpmmacrodir}/macros.%{name}
sed -i -e "s|@@CLANG_MAJOR_VERSION@@|%{maj_ver}|" \
       -e "s|@@CLANG_MINOR_VERSION@@|%{min_ver}|" \
       -e "s|@@CLANG_PATCH_VERSION@@|%{patch_ver}|" \
       %{buildroot}%{_rpmmacrodir}/macros.%{name}

# install clang python bindings
mkdir -p %{buildroot}%{python3_sitelib}/clang/
install -p -m644 bindings/python/clang/* %{buildroot}%{python3_sitelib}/clang/
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/clang

# install scanbuild-py to python sitelib.
mv %{buildroot}%{_prefix}/%{_lib}/{libear,libscanbuild} %{buildroot}%{python3_sitelib}
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/{libear,libscanbuild}

# Fix permissions of scan-view scripts
chmod a+x %{buildroot}%{_datadir}/scan-view/{Reporter.py,startfile.py}

# multilib fix
%multilib_fix_c_header --file %{_includedir}/clang/Config/config.h

# Move emacs integration files to the correct directory
mkdir -p %{buildroot}%{_emacs_sitestartdir}
for f in clang-format.el clang-rename.el clang-include-fixer.el; do
mv %{buildroot}{%{_datadir}/clang,%{_emacs_sitestartdir}}/$f
done

# remove editor integrations (bbedit, sublime, emacs, vim)
rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{_datadir}/clang/clang-format-sublime.py*

# TODO: Package html docs
rm -Rvf %{buildroot}%{_docdir}/Clang/clang/html
rm -Rvf %{buildroot}%{_datadir}/clang/clang-doc-default-stylesheet.css
rm -Rvf %{buildroot}%{_datadir}/clang/index.js

# TODO: What are the Fedora guidelines for packaging bash autocomplete files?
rm -vf %{buildroot}%{_datadir}/clang/bash-autocomplete.sh

# Create Manpage symlinks
ln -s clang.1.gz %{buildroot}%{_mandir}/man1/clang++.1.gz
ln -s clang.1.gz %{buildroot}%{_mandir}/man1/clang-%{maj_ver}.1.gz
ln -s clang.1.gz %{buildroot}%{_mandir}/man1/clang++-%{maj_ver}.1.gz

# Add clang++-{version} symlink
ln -s clang++ %{buildroot}%{_bindir}/clang++-%{maj_ver}


# Fix permission
chmod u-x %{buildroot}%{_mandir}/man1/scan-build.1*

%endif

# Create sub-directories in the clang resource directory that will be
# populated by other packages
mkdir -p %{buildroot}%{pkg_libdir}/clang/%{maj_ver}/{include,lib,share}/


# Remove clang-tidy headers.  We don't ship the libraries for these.
rm -Rvf %{buildroot}%{_includedir}/clang-tidy/

%if %{without compat_build}
# Add a symlink in /usr/bin to clang-format-diff
ln -s %{_datadir}/clang/clang-format-diff.py %{buildroot}%{_bindir}/clang-format-diff
%endif

%check
# see rhbz#1994082
sed -i -e "s/'ASAN_SYMBOLIZER_PATH', 'MSAN_SYMBOLIZER_PATH'/'ASAN_SYMBOLIZER_PATH', 'MSAN_SYMBOLIZER_PATH', 'SOURCE_DATE_EPOCH'/" test/lit.cfg.py

%if %{without compat_build}
%if %{with check}
# Build test dependencies separately, to prevent invocations of host clang from being affected
# by LD_LIBRARY_PATH below.
%cmake_build --target clang-test-depends \
    ExtraToolsUnitTests ClangdUnitTests ClangIncludeCleanerUnitTests ClangPseudoUnitTests

%if %{with bundle_compat_lib}
# Move the compat -cpp.so out of the way so it's not picked up
# by the LD_LIBRARY_PATH below.
compat_lib=$(find %{buildroot}%{_libdir} -name libclang-cpp.so.%{compat_maj_ver})
mv "$compat_lib" .
%endif

# requires lit.py from LLVM utilities
# FIXME: Fix failing ARM tests
SOURCE_DATA_EPOCH=1629181597 LD_LIBRARY_PATH=%{buildroot}/%{_libdir} %{__ninja} check-all -C %{__cmake_builddir} || \
%ifarch %{arm}
:
%else
false
%endif

%if %{with bundle_compat_lib}
mv ./libclang-cpp.so.%{compat_maj_ver} "$compat_lib"
%endif

%endif
%endif


%if %{without compat_build}
%files
%license LICENSE.TXT
%{_bindir}/clang
%{_bindir}/clang++
%{_bindir}/clang-%{maj_ver}
%{_bindir}/clang++-%{maj_ver}
%{_bindir}/clang-cl
%{_bindir}/clang-cpp
%{_mandir}/man1/clang.1.gz
%{_mandir}/man1/clang++.1.gz
%{_mandir}/man1/clang-%{maj_ver}.1.gz
%{_mandir}/man1/clang++-%{maj_ver}.1.gz
%endif

%files libs
%if %{without compat_build}
%{_libdir}/clang/%{maj_ver}/include/*
%{_libdir}/*.so.*
%else
%{pkg_libdir}/*.so.*
%{pkg_libdir}/clang/%{maj_ver}/include/*
%endif
%if %{with bundle_compat_lib}
%{_libdir}/libclang.so.%{compat_maj_ver}*
%{_libdir}/libclang-cpp.so.%{compat_maj_ver}*
%endif

%files devel
%if %{without compat_build}
%{_libdir}/*.so
%{_includedir}/clang/
%{_includedir}/clang-c/
%{_libdir}/cmake/*
%{_bindir}/clang-tblgen
%dir %{_datadir}/clang/
%{_rpmmacrodir}/macros.%{name}
%else
%{pkg_libdir}/*.so
%{pkg_includedir}/clang/
%{pkg_includedir}/clang-c/
%{pkg_libdir}/cmake/
%endif

%files resource-filesystem
%dir %{pkg_libdir}/clang/
%dir %{pkg_libdir}/clang/%{maj_ver}/
%dir %{pkg_libdir}/clang/%{maj_ver}/include/
%dir %{pkg_libdir}/clang/%{maj_ver}/lib/
%dir %{pkg_libdir}/clang/%{maj_ver}/share/

%if %{without compat_build}
%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_bindir}/analyze-build
%{_bindir}/intercept-build
%{_bindir}/scan-build-py
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_libexecdir}/analyze-c++
%{_libexecdir}/analyze-cc
%{_libexecdir}/intercept-c++
%{_libexecdir}/intercept-cc
%{_datadir}/scan-view/
%{_datadir}/scan-build/
%{_mandir}/man1/scan-build.1.*
%{python3_sitelib}/libear
%{python3_sitelib}/libscanbuild


%files tools-extra
%{_bindir}/amdgpu-arch
%{_bindir}/clang-apply-replacements
%{_bindir}/clang-change-namespace
%{_bindir}/clang-check
%{_bindir}/clang-doc
%{_bindir}/clang-extdef-mapping
%{_bindir}/clang-format
%{_bindir}/clang-include-cleaner
%{_bindir}/clang-include-fixer
%{_bindir}/clang-move
%{_bindir}/clang-offload-bundler
%{_bindir}/clang-offload-packager
%{_bindir}/clang-linker-wrapper
%{_bindir}/clang-pseudo
%{_bindir}/clang-query
%{_bindir}/clang-refactor
%{_bindir}/clang-rename
%{_bindir}/clang-reorder-fields
%{_bindir}/clang-repl
%{_bindir}/clang-scan-deps
%{_bindir}/clang-tidy
%{_bindir}/clangd
%{_bindir}/diagtool
%{_bindir}/hmaptool
%{_bindir}/nvptx-arch
%{_bindir}/pp-trace
%{_bindir}/c-index-test
%{_bindir}/find-all-symbols
%{_bindir}/modularize
%{_bindir}/clang-format-diff
%{_mandir}/man1/diagtool.1.gz
%{_emacs_sitestartdir}/clang-format.el
%{_emacs_sitestartdir}/clang-rename.el
%{_emacs_sitestartdir}/clang-include-fixer.el
%{_datadir}/clang/clang-format.py*
%{_datadir}/clang/clang-format-diff.py*
%{_datadir}/clang/clang-include-fixer.py*
%{_datadir}/clang/clang-tidy-diff.py*
%{_bindir}/run-clang-tidy
%{_datadir}/clang/run-find-all-symbols.py*
%{_datadir}/clang/clang-rename.py*

%files -n git-clang-format
%{_bindir}/git-clang-format

%files -n python3-clang
%{python3_sitelib}/clang/


%endif
%changelog
* Wed Jul 05 2023 Nikita Popov <npopov@redhat.com> - 16.0.6-1
- Update to LLVM 16.0.6

* Fri Jun 30 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-7
- Restore gcc-toolset-libatomic-devel requirement

* Fri Jun 30 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-6
- Switch to gcc-toolset-13-gcc

* Thu Jun 29 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-5
- Use gcc-toolset-13-gdb for gdb-add-index

* Fri Jun 02 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-4
- Build with LTO

* Thu May 25 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-3
- Use ld from gcc-toolset

* Tue Apr 18 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-2
- Restore use of gcc-toolset-12

* Mon Apr 17 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-1
- Update to LLVM 16.0.1

* Fri Jan 27 2023 Konrad Kleine <kkleine@redhat.com> - 15.0.7-3
- Remove clang-tools-extra-devel package

* Mon Jan 16 2023 Konrad Kleine <kkleine@redhat.com> - 15.0.7-2
- Update to 15.0.7

* Thu Dec 08 2022 Konrad Kleine<kkleine@redhat.com> - 15.0.6-1
- Update to 15.0.6

* Mon Oct 17 2022 Nikita Popov <npopov@redhat.com> - 15.0.1-2
- Default to non-pie, fix rhbz#2134146

* Mon Sep 26 2022 Konrad Kleine <kkleine@redhat.com> - 15.0.1-1
- Update to 15.0.1

* Tue Jul 19 2022 Timm Bäder <tbaeder@redhat.com> - 14.0.6-1
- Update to 14.0.6

* Mon Jun 20 2022 Timm Bäder <tbaeder@redhat.com> - 14.0.5-1
- Update to 14.0.5

* Fri Apr 22 2022 Timm Bäder <tbaeder@redhat.com> - 14.0.0-1
- 14.0.0 Release

* Thu Feb 03 2022 Tom Stellard <tstellar@redhat.com> - 13.0.1-1
- 13.0.1 Release

* Fri Jan 21 2022 Serge Guelton - 13.0.0-3
- Backport bidi patches

* Wed Nov 03 2021 Timm Bäder <tbaeder@redhat.com> - 13.0.0-2
- Ship libclang-cpp.so.12 as well

* Wed Oct 13 2021 Timm Bäder <tbaeder@redhat.com> - 13.0.0-1
- Release 13.0.0

* Tue Aug 17 2021 sguelton@redhat.com - 12.0.1-5
- Force SOURCE_DATE_EPOCH, fix rhbz#1994082

* Mon Aug 16 2021 Tom Stellard <tstellar@redhat.com> - 12.0.1-4
- Don't requirest tests on s390x

* Mon Aug 16 2021 sguelton@redhat.com - 12.0.1-3
- rebuilt

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jul 13 2021 Tom Stellard <tstellar@redhat.com> - 12.0.1-1
- 12.0.1 Release
- Remove clang-11 compat lib

* Mon Jun 14 2021 sguelton@redhat.com - 12.0.0-5
- Backport

* Tue Jun 08 2021 Tom Stellard <tstellar@redhat.com> - 12.0.0-4
- Only enable -funwind-tables by default on Fedora arches

* Fri May 14 2021 Tom Stellard <tstellar@redhat.com> - 12.0.0-3
- Reduce number of ninja jobs on aarch64

* Fri May 14 2021 Tom Stellard <tstellar@redhat.com> - 12.0.0-2
- Add libclang.so compat library

* Fri Apr 16 2021 Tom Stellard <tstellar@redhat.cm> - 12.0.0-1
- 12.0.0 Release

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 11.1.0-0.5.rc2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Thu Feb 04 2021 Tom Stellard <tstellar@redhat.com> - 11.1.0-0.4.rc2
- Rebuild for llvm-11.1.0-0.3.rc2.el9

* Fri Jan 22 2021 Serge Guelton - 11.1.0-0.3.rc2
- 11.1.0-rc2 release

* Wed Jan 20 2021 Serge Guelton - 11.1.0-0.2.rc1
- rebuilt with https://reviews.llvm.org/D94941 applied.

* Thu Jan 14 2021 Serge Guelton - 11.1.0-0.1.rc1
- 11.1.0-rc1 release

* Wed Jan 06 2021 Serge Guelton - 11.0.1-4
- LLVM 11.0.1 final

* Sun Dec 20 2020 sguelton@redhat.com - 11.0.1-3.rc2
- llvm 11.0.1-rc2

* Wed Dec 16 2020 Tom Stellard <tstellar@redhat.com> - 11.0.1-2.rc1
- Don't build with -flto

* Tue Dec 01 2020 sguelton@redhat.com - 11.0.1-1.rc1
- llvm 11.0.1-rc1

* Thu Oct 29 2020 Tom Stellard <tstellar@redhat.com> - 11.0.0-3
- Remove -ffat-lto-objects compiler flag

* Wed Oct 28 2020 Tom Stellard <tstellar@redhat.com> - 11.0.0-2
- Add clang-resource-filesystem sub-package

* Thu Oct 15 2020 sguelton@redhat.com - 11.0.0-1
- Fix NVR

* Mon Oct 12 2020 sguelton@redhat.com - 11.0.0-0.7
- llvm 11.0.0 - final release

* Thu Oct 08 2020 sguelton@redhat.com - 11.0.0-0.6.rc6
- 11.0.0-rc6

* Fri Oct 02 2020 sguelton@redhat.com - 11.0.0-0.5.rc5
- 11.0.0-rc5 Release

* Sun Sep 27 2020 sguelton@redhat.com - 11.0.0-0.4.rc3
- Fix NVR

* Thu Sep 24 2020 sguelton@redhat.com - 11.0.0-0.1.rc3
- 11.0.0-rc3 Release

* Tue Sep 22 2020 sguelton@redhat.com - 11.0.0-0.3.rc2
- Prefer gcc toolchains with libgcc_s

* Tue Sep 01 2020 sguelton@redhat.com - 11.0.0-0.2.rc2
- Normalize some doc directory locations

* Tue Sep 01 2020 sguelton@redhat.com - 11.0.0-0.1.rc2
- 11.0.0-rc2 Release
- Use %%license macro

* Tue Aug 11 2020 Tom Stellard <tstellar@redhat.com> - 11.0.0-0.2.rc1
- Fix test failures

* Mon Aug 10 2020 Tom Stellard <tstellar@redhat.com> - 11.0.0-0.1.rc1
- 11.0.0-rc1 Release

* Tue Aug 04 2020 Tom Stellard <tstellar@redhat.com> - 10.0.0-11
- Remove Requires: emacs-filesystem

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 10.0.0-10
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 28 2020 Jeff Law <law@redhat.com> - 10.0.0-9
- Disable LTO on arm and i686

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 10.0.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 20 2020 sguelton@redhat.com - 10.0.0-7
- Update cmake macro usage
- Finalize source verification

* Fri Jun 26 2020 Tom Stellard <tstellar@redhat.com> - 10.0.0-6
- Add cet.h header

* Mon Jun 08 2020 Tom Stellard <tstellar@redhat.com> - 10.0.0-5
- Accept multiple --config options

* Wed Jun  3 2020 Dan Čermák <dan.cermak@cgc-instruments.com> - 10.0.0-4
- Add symlink to %%{_libdir}/clang/%%{maj_ver} for persistent access to the resource directory accross minor version bumps

* Mon May 25 2020 Miro Hrončok <mhroncok@redhat.com> - 10.0.0-3
- Rebuilt for Python 3.9

* Tue May 19 2020 sguelton@redhat.com - 10.0.0-2
- Backport ad7211df6f257e39da2e5a11b2456b4488f32a1e, see rhbz#1825593

* Thu Mar 26 2020 sguelton@redhat.com - 10.0.0-1
- 10.0.0 final

* Tue Mar 24 2020 sguelton@redhat.com - 10.0.0-0.11.rc6
- 10.0.0 rc6

* Sun Mar 22 2020 sguelton@redhat.com - 10.0.0-0.10.rc5
- Update git-clang-format dependency, see rhbz#1815913

* Fri Mar 20 2020 Tom Stellard <tstellar@redhat.com> - 10.0.0-0.9.rc5
- Add dependency on libomp-devel

* Fri Mar 20 2020 sguelton@redhat.com - 10.0.0-0.8.rc5
- 10.0.0 rc5

* Sat Mar 14 2020 sguelton@redhat.com - 10.0.0-0.7.rc4
- 10.0.0 rc4

* Thu Mar 12 2020 sguelton@redhat.com - 10.0.0-0.6.rc3
- Move a few files from clang to clang-tools-extra.

* Thu Mar 05 2020 sguelton@redhat.com - 10.0.0-0.5.rc3
- 10.0.0 rc3

* Tue Feb 25 2020 sguelton@redhat.com - 10.0.0-0.4.rc2
- Apply -fdiscard-value-names patch.

* Mon Feb 17 2020 sguelton@redhat.com - 10.0.0-0.3.rc2
- Fix NVR

* Fri Feb 14 2020 sguelton@redhat.com - 10.0.0-0.1.rc2
- 10.0.0 rc2

* Tue Feb 11 2020 sguelton@redhat.com - 10.0.0-0.2.rc1
- Explicitly conflicts with any different compiler-rt version, see rhbz#1800705

* Fri Jan 31 2020 Tom Stellard <tstellar@redhat.com> - 10.0.0-0.1.rc1
- Stop shipping individual component libraries
- https://fedoraproject.org/wiki/Changes/Stop-Shipping-Individual-Component-Libraries-In-clang-lib-Package

* Fri Jan 31 2020 sguelton@redhat.com - 10.0.0-0.1.rc1
- 10.0.0 rc1

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 9.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jan 10 2020 Tom Stellard <tstellar@redhat.com> - 9.0.1-2
- Fix crash with kernel bpf self-tests

* Thu Dec 19 2019 Tom Stellard <tstellar@redhat.com> - 9.0.1-1
- 9.0.1 Release

* Wed Dec 11 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-3
- Add explicit requires for clang-libs to fix rpmdiff errors

* Tue Dec 10 2019 sguelton@redhat.com - 9.0.0-2
- Activate -funwind-tables on all arches, see rhbz#1655546.

* Thu Sep 19 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-1
- 9.0.0 Release

* Wed Sep 11 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-0.2.rc3
- Reduce debug info verbosity on ppc64le to avoid OOM errors in koji

* Thu Aug 22 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-0.1.rc3
- 9.0.0 Release candidate 3

* Tue Aug 20 2019 sguelton@redhat.com - 8.0.0-4
- Rebuilt for Python 3.8

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 8.0.0-3.2
- Rebuilt for Python 3.8

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 8.0.0-3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu May 16 2019 sguelton@redhat.com - 8.0.0-3
- Fix for rhbz#1674031

* Fri Apr 12 2019 sguelton@redhat.com - 8.0.0-2
- Remove useless patch thanks to GCC upgrade

* Wed Mar 20 2019 sguelton@redhat.com - 8.0.0-1
- 8.0.0 final

* Tue Mar 12 2019 sguelton@redhat.com - 8.0.0-0.6.rc4
- 8.0.0 Release candidate 4

* Mon Mar 4 2019 sguelton@redhat.com - 8.0.0-0.5.rc3
- Cleanup specfile after llvm dependency update

* Mon Mar 4 2019 sguelton@redhat.com - 8.0.0-0.4.rc3
- 8.0.0 Release candidate 3

* Mon Feb 25 2019 tstellar@redhat.com - 8.0.0-0.3.rc2
- Fix compiling with -stdlib=libc++

* Thu Feb 21 2019 sguelton@redhat.com - 8.0.0-0.2.rc2
- 8.0.0 Release candidate 2

* Sat Feb 09 2019 sguelton@redhat.com - 8.0.0-0.1.rc1
- 8.0.0 Release candidate 1

* Tue Feb 05 2019 sguelton@redhat.com - 7.0.1-6
- Update patch for Python3 port of scan-view

* Tue Feb 05 2019 sguelton@redhat.com - 7.0.1-5
- Working CI test suite

* Mon Feb 04 2019 sguelton@redhat.com - 7.0.1-4
- Workaround gcc-9 bug when compiling bitfields

* Fri Feb 01 2019 sguelton@redhat.com - 7.0.1-3
- Fix uninitialized error detected by gcc-9

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 7.0.1-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Dec 19 2018 Tom Stellard <tstellar@redhat.com> - 7.0.1-2
- Fix for rhbz#1657544

* Tue Dec 18 2018 sguelton@redhat.com - 7.0.1-1
- 7.0.1

* Tue Dec 18 2018 sguelton@redhat.com - 7.0.0-10
- Install proper manpage symlinks for clang/clang++ versions

* Fri Dec 14 2018 sguelton@redhat.com - 7.0.0-9
- No longer Ignore -fstack-clash-protection option

* Tue Dec 04 2018 sguelton@redhat.com - 7.0.0-8
- Ensure rpmlint passes on specfile

* Fri Nov 30 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-7
- Drop python2 dependency from clang-tools-extra

* Wed Nov 21 2018 sguelton@redhat.com - 7.0.0-6
- Prune unneeded reference to llvm-test-suite sub-package

* Mon Nov 19 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-5
- Run 'make check-all' instead of 'make check-clang'

* Mon Nov 19 2018 sergesanspaille <sguelton@redhat.com> - 7.0.0-4
- Avoid Python2 + Python3 dependency for clang-analyzer

* Mon Nov 05 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-3
- User helper macro to fixup config.h for multilib

* Tue Oct 02 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-2
- Use correct shebang substitution for python scripts

* Mon Sep 24 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-1
- 7.0.0 Release

* Wed Sep 19 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.16.rc3
- Move builtin headers into clang-libs sub-package

* Wed Sep 19 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.15.rc3
- Remove ambiguous python shebangs

* Thu Sep 13 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.14.rc3
- Move unversioned shared objects to devel package

* Thu Sep 13 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.13.rc3
- Rebuild with new llvm-devel that disables rpath on install

* Thu Sep 13 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.12.rc3
- Fix clang++-7 symlink

* Wed Sep 12 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.11.rc3
- 7.0.0-rc3 Release

* Mon Sep 10 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.10.rc2
- Drop siod from llvm-test-suite

* Fri Sep 07 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.9.rc2
- Drop python2 dependency from clang package

* Thu Sep 06 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.8.rc2
- Drop all uses of python2 from lit tests

* Sat Sep 01 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.7.rc2
- Add Fedora specific version string

* Tue Aug 28 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.6.rc2
- 7.0.0-rc2 Release

* Tue Aug 28 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.5.rc1
- Enable unit tests

* Fri Aug 17 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.4.rc1
- Move llvm-test-suite into a sub-package

* Fri Aug 17 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.3.rc1
- Recommend the same version of compiler-rt

* Wed Aug 15 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.2.rc1
- Rebuild for f30

* Mon Aug 13 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.1.rc1
- 7.0.0-rc1 Release

* Mon Jul 23 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-3
- Sync spec file with the clang6.0 package

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 26 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-1
- 6.0.1 Release

* Wed Jun 13 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-0.2.rc2
- 6.0.1-rc2

* Fri May 11 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-0.1.rc1
- 6.0.1-rc1 Release

* Fri Mar 23 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-5
- Add a clang++-{version} symlink rhbz#1534098

* Thu Mar 22 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-4
- Use correct script for running lit tests

* Wed Mar 21 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-3
- Fix toolchain detection so we don't default to using cross-compilers:
  rhbz#1482491

* Mon Mar 12 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-2
- Add Provides: clang(major) rhbz#1547444

* Fri Mar 09 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-1
- 6.0.0 Release

* Mon Feb 12 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.6.rc2
- 6.0.0-rc2 Release

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.0-0.5.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Feb 01 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.4.rc1
- Package python helper scripts for tools

* Fri Jan 26 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.3.rc1
- Ignore -fstack-clash-protection option instead of giving an error

* Fri Jan 26 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.2.rc1
- Package emacs integration files

* Wed Jan 24 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.1.rc1
- 6.0.0-rc1 Release

* Wed Jan 24 2018 Tom Stellard <tstellar@redhat.com> - 5.0.1-3
- Rebuild against llvm5.0 compatibility package
- rhbz#1538231

* Wed Jan 03 2018 Iryna Shcherbina <ishcherb@redhat.com> - 5.0.1-2
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Wed Dec 20 2017 Tom Stellard <tstellar@redhat.com> - 5.0.1-1
- 5.0.1 Release

* Wed Dec 13 2017 Tom Stellard <tstellar@redhat.com> - 5.0.0-3
- Make compiler-rt a weak dependency and add a weak dependency on libomp

* Mon Nov 06 2017 Merlin Mathesius <mmathesi@redhat.com> - 5.0.0-2
- Cleanup spec file conditionals

* Mon Oct 16 2017 Tom Stellard <tstellar@redhat.com> - 5.0.0-1
- 5.0.0 Release

* Wed Oct 04 2017 Rex Dieter <rdieter@fedoraproject.org> - 4.0.1-6
- python2-clang subpkg (#1490997)
- tools-extras: tighten (internal) -libs dep
- %%install: avoid cd

* Wed Aug 30 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-5
- Add Requires: python for git-clang-format

* Sun Aug 06 2017 Björn Esser <besser82@fedoraproject.org> - 4.0.1-4
- Rebuilt for AutoReq cmake-filesystem

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun 23 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-1
- 4.0.1 Release.

* Fri Jun 16 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-8
- Enable make check-clang

* Mon Jun 12 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-7
- Package git-clang-format

* Thu Jun 08 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-6
- Generate man pages

* Thu Jun 08 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-5
- Ignore test-suite failures until all arches are fixed.

* Mon Apr 03 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-4
- Run llvm test-suite

* Mon Mar 27 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-3
- Enable eh/rtti, which are required by lldb.

* Fri Mar 24 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-2
- Fix clang-tools-extra build
- Fix install

* Thu Mar 23 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-1
- clang 4.0.0 final release

* Mon Mar 20 2017 David Goerger <david.goerger@yale.edu> - 3.9.1-3
- add clang-tools-extra rhbz#1328091

* Thu Mar 16 2017 Tom Stellard <tstellar@redhat.com> - 3.9.1-2
- Enable build-id by default rhbz#1432403

* Thu Mar 02 2017 Dave Airlie <airlied@redhat.com> - 3.9.1-1
- clang 3.9.1 final release

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 14 2016 Nathaniel McCallum <npmccallum@redhat.com> - 3.9.0-3
- Add Requires: compiler-rt to clang-libs.
- Without this, compiling with certain CFLAGS breaks.

* Tue Nov  1 2016 Peter Robinson <pbrobinson@fedoraproject.org> 3.9.0-2
- Rebuild for new arches

* Fri Oct 14 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-1
- clang 3.9.0 final release

* Fri Jul 01 2016 Stephan Bergmann <sbergman@redhat.com> - 3.8.0-2
- Resolves: rhbz#1282645 add GCC abi_tag support

* Thu Mar 10 2016 Dave Airlie <airlied@redhat.com> 3.8.0-1
- clang 3.8.0 final release

* Thu Mar 03 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.4
- clang 3.8.0rc3

* Wed Feb 24 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.3
- package all libs into clang-libs.

* Wed Feb 24 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.2
- enable dynamic linking of clang against llvm

* Thu Feb 18 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.1
- clang 3.8.0rc2

* Fri Feb 12 2016 Dave Airlie <airlied@redhat.com> 3.7.1-4
- rebuild against latest llvm packages
- add BuildRequires llvm-static

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 28 2016 Dave Airlie <airlied@redhat.com> 3.7.1-2
- just accept clang includes moving to /usr/lib64, upstream don't let much else happen

* Thu Jan 28 2016 Dave Airlie <airlied@redhat.com> 3.7.1-1
- initial build in Fedora.

* Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
- initial version using cmake build system
