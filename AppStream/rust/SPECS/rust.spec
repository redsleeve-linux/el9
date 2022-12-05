# Only x86_64 and i686 are Tier 1 platforms at this time.
# https://doc.rust-lang.org/nightly/rustc/platform-support.html
%global rust_arches x86_64 i686 aarch64 ppc64le s390x

# The channel can be stable, beta, or nightly
%{!?channel: %global channel stable}

# To bootstrap from scratch, set the channel and date from src/stage0.json
# e.g. 1.59.0 wants rustc: 1.58.0-2022-01-13
# or nightly wants some beta-YYYY-MM-DD
%global bootstrap_version 1.61.0
%global bootstrap_channel 1.61.0
%global bootstrap_date 2022-05-19

# Only the specified arches will use bootstrap binaries.
# NOTE: Those binaries used to be uploaded with every new release, but that was
# a waste of lookaside cache space when they're most often unused.
# Run "spectool -g rust.spec" after changing this and then "fedpkg upload" to
# add them to sources. Remember to remove them again after the bootstrap build!
#global bootstrap_arches %%{rust_arches}

# Define a space-separated list of targets to ship rust-std-static-$triple for
# cross-compilation. The packages are noarch, but they're not fully
# reproducible between hosts, so only x86_64 actually builds it.
%ifarch x86_64
%if 0%{?fedora}
%global mingw_targets i686-pc-windows-gnu x86_64-pc-windows-gnu
%endif
%if 0%{?fedora} || 0%{?rhel} >= 8
%global wasm_targets wasm32-unknown-unknown wasm32-wasi
%endif
%endif

# We need CRT files for *-wasi targets, at least as new as the commit in
# src/ci/docker/host-x86_64/dist-various-2/build-wasi-toolchain.sh
# (updated per https://github.com/rust-lang/rust/pull/96907)
%global wasi_libc_url https://github.com/WebAssembly/wasi-libc
%global wasi_libc_commit 9886d3d6200fcc3726329966860fc058707406cd
%global wasi_libc_name wasi-libc-%{wasi_libc_commit}
%global wasi_libc_source %{wasi_libc_url}/archive/%{wasi_libc_commit}/%{wasi_libc_name}.tar.gz
%global wasi_libc_dir %{_builddir}/%{wasi_libc_name}

# Using llvm-static may be helpful as an opt-in, e.g. to aid LLVM rebases.
%bcond_with llvm_static

# We can also choose to just use Rust's bundled LLVM, in case the system LLVM
# is insufficient.  Rust currently requires LLVM 12.0+.
%global min_llvm_version 12.0.0
%global bundled_llvm_version 14.0.4
%bcond_with bundled_llvm

# Requires stable libgit2 1.4, and not the next minor soname change.
# This needs to be consistent with the bindings in vendor/libgit2-sys.
%global min_libgit2_version 1.4.0
%global next_libgit2_version 1.5.0~
%global bundled_libgit2_version 1.4.2
%if 0%{?fedora} >= 99
%bcond_with bundled_libgit2
%else
%bcond_without bundled_libgit2
%endif

# needs libssh2_userauth_publickey_frommemory
%global min_libssh2_version 1.6.0
%if 0%{?rhel}
# Disable cargo->libgit2->libssh2 on RHEL, as it's not approved for FIPS (rhbz1732949)
%bcond_without disabled_libssh2
%else
%bcond_with disabled_libssh2
%endif

%if 0%{?rhel} && 0%{?rhel} < 8
%bcond_with curl_http2
%else
%bcond_without curl_http2
%endif

# LLDB isn't available everywhere...
%if 0%{?rhel} && 0%{?rhel} < 8
%bcond_with lldb
%else
%bcond_without lldb
%endif

Name:           rust
Version:        1.62.1
Release:        1%{?dist}
Summary:        The Rust Programming Language
License:        (ASL 2.0 or MIT) and (BSD and MIT)
# ^ written as: (rust itself) and (bundled libraries)
URL:            https://www.rust-lang.org
ExclusiveArch:  %{rust_arches}

%if "%{channel}" == "stable"
%global rustc_package rustc-%{version}-src
%else
%global rustc_package rustc-%{channel}-src
%endif
Source0:        https://static.rust-lang.org/dist/%{rustc_package}.tar.xz
Source1:        %{wasi_libc_source}
# Sources for bootstrap_arches are inserted by lua below

# By default, rust tries to use "rust-lld" as a linker for WebAssembly.
Patch1:         0001-Use-lld-provided-by-system-for-wasm.patch

# Set a substitute-path in rust-gdb for standard library sources.
Patch2:         rustc-1.61.0-rust-gdb-substitute-path.patch

### RHEL-specific patches below ###

# Simple rpm macros for rust-toolset (as opposed to full rust-packaging)
Source100:      macros.rust-toolset

# Disable cargo->libgit2->libssh2 on RHEL, as it's not approved for FIPS (rhbz1732949)
Patch100:       rustc-1.59.0-disable-libssh2.patch

# libcurl on RHEL7 doesn't have http2, but since cargo requests it, curl-sys
# will try to build it statically -- instead we turn off the feature.
Patch101:       rustc-1.62.0-disable-http2.patch

# kernel rh1410097 causes too-small stacks for PIE.
# (affects RHEL6 kernels when building for RHEL7)
Patch102:       rustc-1.58.0-no-default-pie.patch


# Get the Rust triple for any arch.
%{lua: function rust_triple(arch)
  local abi = "gnu"
  if arch == "armv7hl" then
    arch = "armv7"
    abi = "gnueabihf"
  elseif arch == "ppc64" then
    arch = "powerpc64"
  elseif arch == "ppc64le" then
    arch = "powerpc64le"
  elseif arch == "riscv64" then
    arch = "riscv64gc"
  end
  return arch.."-unknown-linux-"..abi
end}

%global rust_triple %{lua: print(rust_triple(rpm.expand("%{_target_cpu}")))}

%if %defined bootstrap_arches
# For each bootstrap arch, add an additional binary Source.
# Also define bootstrap_source just for the current target.
%{lua: do
  local bootstrap_arches = {}
  for arch in string.gmatch(rpm.expand("%{bootstrap_arches}"), "%S+") do
    table.insert(bootstrap_arches, arch)
  end
  local base = rpm.expand("https://static.rust-lang.org/dist/%{bootstrap_date}")
  local channel = rpm.expand("%{bootstrap_channel}")
  local target_arch = rpm.expand("%{_target_cpu}")
  for i, arch in ipairs(bootstrap_arches) do
    i = 1000 + i * 3
    local suffix = channel.."-"..rust_triple(arch)
    print(string.format("Source%d: %s/cargo-%s.tar.xz\n", i, base, suffix))
    print(string.format("Source%d: %s/rustc-%s.tar.xz\n", i+1, base, suffix))
    print(string.format("Source%d: %s/rust-std-%s.tar.xz\n", i+2, base, suffix))
    if arch == target_arch then
      rpm.define("bootstrap_source_cargo "..i)
      rpm.define("bootstrap_source_rustc "..i+1)
      rpm.define("bootstrap_source_std "..i+2)
      rpm.define("bootstrap_suffix "..suffix)
    end
  end
end}
%endif

%ifarch %{bootstrap_arches}
%global local_rust_root %{_builddir}/rust-%{bootstrap_suffix}
Provides:       bundled(%{name}-bootstrap) = %{bootstrap_version}
%else
BuildRequires:  cargo >= %{bootstrap_version}
%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires:  %{name} >= %{bootstrap_version}
BuildConflicts: %{name} > %{version}
%else
BuildRequires:  (%{name} >= %{bootstrap_version} with %{name} <= %{version})
%endif
%global local_rust_root %{_prefix}
%endif

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  ncurses-devel
# explicit curl-devel to avoid httpd24-curl (rhbz1540167)
BuildRequires:  curl-devel
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(liblzma)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(zlib)

%if %{without bundled_libgit2}
BuildRequires:  (pkgconfig(libgit2) >= %{min_libgit2_version} with pkgconfig(libgit2) < %{next_libgit2_version})
%endif

%if %{without disabled_libssh2}
BuildRequires:  pkgconfig(libssh2) >= %{min_libssh2_version}
%endif

%if 0%{?rhel} == 8
BuildRequires:  platform-python
%else
BuildRequires:  python3
%endif
BuildRequires:  python3-rpm-macros

%if %with bundled_llvm
BuildRequires:  cmake3 >= 3.13.4
BuildRequires:  ninja-build
Provides:       bundled(llvm) = %{bundled_llvm_version}
%else
BuildRequires:  cmake >= 2.8.11
%if 0%{?epel} == 7
%global llvm llvm13
%endif
%if %defined llvm
%global llvm_root %{_libdir}/%{llvm}
%else
%global llvm llvm
%global llvm_root %{_prefix}
%endif
BuildRequires:  %{llvm}-devel >= %{min_llvm_version}
%if %with llvm_static
BuildRequires:  %{llvm}-static
BuildRequires:  libffi-devel
%endif
%endif

# make check needs "ps" for src/test/ui/wait-forked-but-failed-child.rs
BuildRequires:  procps-ng

# debuginfo-gdb tests need gdb
BuildRequires:  gdb

# For src/test/run-make/static-pie
BuildRequires:  glibc-static

# Virtual provides for folks who attempt "dnf install rustc"
Provides:       rustc = %{version}-%{release}
Provides:       rustc%{?_isa} = %{version}-%{release}

# Always require our exact standard library
Requires:       %{name}-std-static%{?_isa} = %{version}-%{release}

# The C compiler is needed at runtime just for linking.  Someday rustc might
# invoke the linker directly, and then we'll only need binutils.
# https://github.com/rust-lang/rust/issues/11937
Requires:       /usr/bin/cc

%if 0%{?epel} == 7
%global devtoolset_name devtoolset-9
BuildRequires:  %{devtoolset_name}-binutils
BuildRequires:  %{devtoolset_name}-gcc
BuildRequires:  %{devtoolset_name}-gcc-c++
%global devtoolset_bindir /opt/rh/%{devtoolset_name}/root/usr/bin
%global __cc     %{devtoolset_bindir}/gcc
%global __cxx    %{devtoolset_bindir}/g++
%global __ar     %{devtoolset_bindir}/ar
%global __ranlib %{devtoolset_bindir}/ranlib
%global __strip  %{devtoolset_bindir}/strip
%else
%global __ranlib %{_bindir}/ranlib
%endif

# ALL Rust libraries are private, because they don't keep an ABI.
%global _privatelibs lib(.*-[[:xdigit:]]{16}*|rustc.*)[.]so.*
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$
%global __provides_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$
%global __requires_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$

# While we don't want to encourage dynamic linking to Rust shared libraries, as
# there's no stable ABI, we still need the unallocated metadata (.rustc) to
# support custom-derive plugins like #[proc_macro_derive(Foo)].
%if 0%{?rhel} && 0%{?rhel} < 8
# eu-strip is very eager by default, so we have to limit it to -g, only debugging symbols.
%global _find_debuginfo_opts -g
%undefine _include_minidebuginfo
%else
# Newer find-debuginfo.sh supports --keep-section, which is preferable. rhbz1465997
%global _find_debuginfo_opts --keep-section .rustc
%endif

%if %{without bundled_llvm}
%if "%{llvm_root}" == "%{_prefix}" || 0%{?scl:1}
%global llvm_has_filecheck 1
%endif
%endif

# We're going to override --libdir when configuring to get rustlib into a
# common path, but we'll fix the shared libraries during install.
%global common_libdir %{_prefix}/lib
%global rustlibdir %{common_libdir}/rustlib

%if %defined mingw_targets
BuildRequires:  mingw32-filesystem >= 95
BuildRequires:  mingw64-filesystem >= 95
BuildRequires:  mingw32-crt
BuildRequires:  mingw64-crt
BuildRequires:  mingw32-gcc
BuildRequires:  mingw64-gcc
BuildRequires:  mingw32-winpthreads-static
BuildRequires:  mingw64-winpthreads-static
%endif

%if %defined wasm_targets
BuildRequires:  clang
BuildRequires:  lld
# brp-strip-static-archive breaks the archive index for wasm
%global __os_install_post \
%__os_install_post \
find '%{buildroot}%{rustlibdir}'/wasm*/lib -type f -regex '.*\\.\\(a\\|rlib\\)' -print -exec '%{llvm_root}/bin/llvm-ranlib' '{}' ';' \
%{nil}
%endif

%description
Rust is a systems programming language that runs blazingly fast, prevents
segfaults, and guarantees thread safety.

This package includes the Rust compiler and documentation generator.


%package std-static
Summary:        Standard library for Rust
Requires:       %{name} = %{version}-%{release}
Requires:       glibc-devel%{?_isa} >= 2.11

%description std-static
This package includes the standard libraries for building applications
written in Rust.

%if %defined mingw_targets
%{lua: do
  for triple in string.gmatch(rpm.expand("%{mingw_targets}"), "%S+") do
    local subs = {
      triple = triple,
      name = rpm.expand("%{name}"),
      verrel = rpm.expand("%{version}-%{release}"),
      mingw = string.sub(triple, 1, 4) == "i686" and "mingw32" or "mingw64",
    }
    local s = string.gsub([[

%package std-static-{{triple}}
Summary:        Standard library for Rust {{triple}}
BuildArch:      noarch
Provides:       {{mingw}}-rust = {{verrel}}
Provides:       {{mingw}}-rustc = {{verrel}}
Requires:       {{mingw}}-crt
Requires:       {{mingw}}-gcc
Requires:       {{mingw}}-winpthreads-static
Requires:       {{name}} = {{verrel}}

%description std-static-{{triple}}
This package includes the standard libraries for building applications
written in Rust for the MinGW target {{triple}}.

]], "{{(%w+)}}", subs)
    print(s)
  end
end}
%endif

%if %defined wasm_targets
%{lua: do
  for triple in string.gmatch(rpm.expand("%{wasm_targets}"), "%S+") do
    local subs = {
      triple = triple,
      name = rpm.expand("%{name}"),
      verrel = rpm.expand("%{version}-%{release}"),
      wasi = string.find(triple, "-wasi") and 1 or 0,
    }
    local s = string.gsub([[

%package std-static-{{triple}}
Summary:        Standard library for Rust {{triple}}
BuildArch:      noarch
Requires:       {{name}} = {{verrel}}
Requires:       lld >= 8.0
%if {{wasi}}
Provides:       bundled(wasi-libc)
%endif

%description std-static-{{triple}}
This package includes the standard libraries for building applications
written in Rust for the WebAssembly target {{triple}}.

]], "{{(%w+)}}", subs)
    print(s)
  end
end}
%endif


%package debugger-common
Summary:        Common debugger pretty printers for Rust
BuildArch:      noarch

%description debugger-common
This package includes the common functionality for %{name}-gdb and %{name}-lldb.


%package gdb
Summary:        GDB pretty printers for Rust
BuildArch:      noarch
Requires:       gdb
Requires:       %{name}-debugger-common = %{version}-%{release}

%description gdb
This package includes the rust-gdb script, which allows easier debugging of Rust
programs.


%if %with lldb

%package lldb
Summary:        LLDB pretty printers for Rust
BuildArch:      noarch
Requires:       lldb
Requires:       python3-lldb
Requires:       %{name}-debugger-common = %{version}-%{release}

%description lldb
This package includes the rust-lldb script, which allows easier debugging of Rust
programs.

%endif


%package doc
Summary:        Documentation for Rust
# NOT BuildArch:      noarch
# Note, while docs are mostly noarch, some things do vary by target_arch.
# Koji will fail the build in rpmdiff if two architectures build a noarch
# subpackage differently, so instead we have to keep its arch.

%description doc
This package includes HTML documentation for the Rust programming language and
its standard library.


%package -n cargo
Summary:        Rust's package manager and build tool
%if %with bundled_libgit2
Provides:       bundled(libgit2) = %{bundled_libgit2_version}
%endif
# For tests:
BuildRequires:  git-core
# Cargo is not much use without Rust
Requires:       %{name}

# "cargo vendor" is a builtin command starting with 1.37.  The Obsoletes and
# Provides are mostly relevant to RHEL, but harmless to have on Fedora/etc. too
Obsoletes:      cargo-vendor <= 0.1.23
Provides:       cargo-vendor = %{version}-%{release}

%description -n cargo
Cargo is a tool that allows Rust projects to declare their various dependencies
and ensure that you'll always get a repeatable build.


%package -n cargo-doc
Summary:        Documentation for Cargo
BuildArch:      noarch
# Cargo no longer builds its own documentation
# https://github.com/rust-lang/cargo/pull/4904
Requires:       %{name}-doc = %{version}-%{release}

%description -n cargo-doc
This package includes HTML documentation for Cargo.


%package -n rustfmt
Summary:        Tool to find and fix Rust formatting issues
Requires:       cargo

# The component/package was rustfmt-preview until Rust 1.31.
Obsoletes:      rustfmt-preview < 1.0.0
Provides:       rustfmt-preview = %{version}-%{release}

%description -n rustfmt
A tool for formatting Rust code according to style guidelines.


%package -n rls
Summary:        Rust Language Server for IDE integration
%if %with bundled_libgit2
Provides:       bundled(libgit2) = %{bundled_libgit2_version}
%endif
Requires:       %{name}-analysis
# /usr/bin/rls is dynamically linked against internal rustc libs
Requires:       %{name}%{?_isa} = %{version}-%{release}

# The component/package was rls-preview until Rust 1.31.
Obsoletes:      rls-preview < 1.31.6
Provides:       rls-preview = %{version}-%{release}

%description -n rls
The Rust Language Server provides a server that runs in the background,
providing IDEs, editors, and other tools with information about Rust programs.
It supports functionality such as 'goto definition', symbol search,
reformatting, and code completion, and enables renaming and refactorings.


%package -n clippy
Summary:        Lints to catch common mistakes and improve your Rust code
Requires:       cargo
# /usr/bin/clippy-driver is dynamically linked against internal rustc libs
Requires:       %{name}%{?_isa} = %{version}-%{release}

# The component/package was clippy-preview until Rust 1.31.
Obsoletes:      clippy-preview <= 0.0.212
Provides:       clippy-preview = %{version}-%{release}

%description -n clippy
A collection of lints to catch common mistakes and improve your Rust code.


%package src
Summary:        Sources for the Rust standard library
BuildArch:      noarch

%description src
This package includes source files for the Rust standard library.  It may be
useful as a reference for code completion tools in various editors.


%package analysis
Summary:        Compiler analysis data for the Rust standard library
Requires:       %{name}-std-static%{?_isa} = %{version}-%{release}

%description analysis
This package contains analysis data files produced with rustc's -Zsave-analysis
feature for the Rust standard library. The RLS (Rust Language Server) uses this
data to provide information about the Rust standard library.


%if 0%{?rhel} && 0%{?rhel} >= 8

%package toolset
Summary:        Rust Toolset
Requires:       rust%{?_isa} = %{version}-%{release}
Requires:       cargo%{?_isa} = %{version}-%{release}

%description toolset
This is the metapackage for Rust Toolset, bringing in the Rust compiler,
the Cargo package manager, and a few convenience macros for rpm builds.

%endif


%prep

%ifarch %{bootstrap_arches}
rm -rf %{local_rust_root}
%setup -q -n cargo-%{bootstrap_suffix} -T -b %{bootstrap_source_cargo}
./install.sh --prefix=%{local_rust_root} --disable-ldconfig
%setup -q -n rustc-%{bootstrap_suffix} -T -b %{bootstrap_source_rustc}
./install.sh --prefix=%{local_rust_root} --disable-ldconfig
%setup -q -n rust-std-%{bootstrap_suffix} -T -b %{bootstrap_source_std}
./install.sh --prefix=%{local_rust_root} --disable-ldconfig
test -f '%{local_rust_root}/bin/cargo'
test -f '%{local_rust_root}/bin/rustc'
%endif

%if %defined wasm_targets
%setup -q -n %{wasi_libc_name} -T -b 1
%endif

%setup -q -n %{rustc_package}

%patch1 -p1
%patch2 -p1

%if %with disabled_libssh2
%patch100 -p1
%endif

%if %without curl_http2
%patch101 -p1
rm -rf vendor/libnghttp2-sys/
%endif

%if 0%{?rhel} && 0%{?rhel} < 8
%patch102 -p1
%endif

# Use our explicit python3 first
sed -i.try-python -e '/^try python3 /i try "%{__python3}" "$@"' ./configure

# Set a substitute-path in rust-gdb for standard library sources.
sed -i.rust-src -e "s#@BUILDDIR@#$PWD#" ./src/etc/rust-gdb

%if %without bundled_llvm
rm -rf src/llvm-project/
mkdir -p src/llvm-project/libunwind/
%endif

# Remove other unused vendored libraries
rm -rf vendor/curl-sys/curl/
rm -rf vendor/*jemalloc-sys*/jemalloc/
rm -rf vendor/libmimalloc-sys/c_src/mimalloc/
rm -rf vendor/libssh2-sys/libssh2/
rm -rf vendor/libz-sys/src/zlib/
rm -rf vendor/libz-sys/src/zlib-ng/
rm -rf vendor/lzma-sys/xz-*/
rm -rf vendor/openssl-src/openssl/

%if %without bundled_libgit2
rm -rf vendor/libgit2-sys/libgit2/
%endif

%if %with disabled_libssh2
rm -rf vendor/libssh2-sys/
%endif

# This only affects the transient rust-installer, but let it use our dynamic xz-libs
sed -i.lzma -e '/LZMA_API_STATIC/d' src/bootstrap/tool.rs

%if %{with bundled_llvm} && 0%{?epel} == 7
mkdir -p cmake-bin
ln -s /usr/bin/cmake3 cmake-bin/cmake
%global cmake_path $PWD/cmake-bin
%endif

%if %{without bundled_llvm} && %{with llvm_static}
# Static linking to distro LLVM needs to add -lffi
# https://github.com/rust-lang/rust/issues/34486
sed -i.ffi -e '$a #[link(name = "ffi")] extern {}' \
  src/librustc_llvm/lib.rs
%endif

# The configure macro will modify some autoconf-related files, which upsets
# cargo when it tries to verify checksums in those files.  If we just truncate
# that file list, cargo won't have anything to complain about.
find vendor -name .cargo-checksum.json \
  -exec sed -i.uncheck -e 's/"files":{[^}]*}/"files":{ }/' '{}' '+'

# Sometimes Rust sources start with #![...] attributes, and "smart" editors think
# it's a shebang and make them executable. Then brp-mangle-shebangs gets upset...
find -name '*.rs' -type f -perm /111 -exec chmod -v -x '{}' '+'

# Set up shared environment variables for build/install/check
%global rust_env %{?rustflags:RUSTFLAGS="%{rustflags}"}
%if 0%{?cmake_path:1}
%global rust_env %{?rust_env} PATH="%{cmake_path}:$PATH"
%endif
%if %without disabled_libssh2
# convince libssh2-sys to use the distro libssh2
%global rust_env %{?rust_env} LIBSSH2_SYS_USE_PKG_CONFIG=1
%endif
%global export_rust_env %{?rust_env:export %{rust_env}}


%build
%{export_rust_env}

%ifarch %{arm} %{ix86} s390x
# full debuginfo is exhausting memory; just do libstd for now
# https://github.com/rust-lang/rust/issues/45854
%if 0%{?rhel} && 0%{?rhel} < 8
# Older rpmbuild didn't work with partial debuginfo coverage.
%global debug_package %{nil}
%define enable_debuginfo --debuginfo-level=0
%else
%define enable_debuginfo --debuginfo-level=0 --debuginfo-level-std=2
%endif
%else
%define enable_debuginfo --debuginfo-level=2
%endif

# Some builders have relatively little memory for their CPU count.
# At least 2GB per CPU is a good rule of thumb for building rustc.
ncpus=$(/usr/bin/getconf _NPROCESSORS_ONLN)
max_cpus=$(( ($(free -g | awk '/^Mem:/{print $2}') + 1) / 2 ))
if [ "$max_cpus" -ge 1 -a "$max_cpus" -lt "$ncpus" ]; then
  ncpus="$max_cpus"
fi

%if %defined mingw_targets
%{lua: do
  local cfg = ""
  for triple in string.gmatch(rpm.expand("%{mingw_targets}"), "%S+") do
    local subs = {
      triple = triple,
      mingw = string.sub(triple, 1, 4) == "i686" and "mingw32" or "mingw64",
    }
    local s = string.gsub([[
      --set target.{{triple}}.linker=%{{{mingw}}_cc}
      --set target.{{triple}}.cc=%{{{mingw}}_cc}
      --set target.{{triple}}.ar=%{{{mingw}}_ar}
      --set target.{{triple}}.ranlib=%{{{mingw}}_ranlib}
    ]], "{{(%w+)}}", subs)
    cfg = cfg .. " " .. s
  end
  cfg = string.gsub(cfg, "%s+", " ")
  rpm.define("mingw_target_config " .. cfg)
end}
%endif

%if %defined wasm_targets
%make_build --quiet -C %{wasi_libc_dir} CC=clang AR=llvm-ar NM=llvm-nm
%{lua: do
  local wasi_root = rpm.expand("%{wasi_libc_dir}") .. "/sysroot"
  local cfg = ""
  for triple in string.gmatch(rpm.expand("%{wasm_targets}"), "%S+") do
    if string.find(triple, "-wasi") then
      cfg = cfg .. " --set target." .. triple .. ".wasi-root=" .. wasi_root
    end
  end
  rpm.define("wasm_target_config "..cfg)
end}
%endif

%configure --disable-option-checking \
  --libdir=%{common_libdir} \
  --build=%{rust_triple} --host=%{rust_triple} --target=%{rust_triple} \
  --set target.%{rust_triple}.linker=%{__cc} \
  --set target.%{rust_triple}.cc=%{__cc} \
  --set target.%{rust_triple}.cxx=%{__cxx} \
  --set target.%{rust_triple}.ar=%{__ar} \
  --set target.%{rust_triple}.ranlib=%{__ranlib} \
  %{?mingw_target_config} \
  %{?wasm_target_config} \
  --python=%{__python3} \
  --local-rust-root=%{local_rust_root} \
  --set build.rustfmt=/bin/true \
  %{!?with_bundled_llvm: --llvm-root=%{llvm_root} \
    %{!?llvm_has_filecheck: --disable-codegen-tests} \
    %{!?with_llvm_static: --enable-llvm-link-shared } } \
  --disable-llvm-static-stdcpp \
  --disable-rpath \
  %{enable_debuginfo} \
  --set rust.codegen-units-std=1 \
  --enable-extended \
  --tools=analysis,cargo,clippy,rls,rustfmt,src \
  --enable-vendor \
  --enable-verbose-tests \
  --dist-compression-formats=gz \
  --release-channel=%{channel} \
  --release-description="%{?fedora:Fedora }%{?rhel:Red Hat }%{version}-%{release}"

%{__python3} ./x.py build -j "$ncpus" --stage 2
%{__python3} ./x.py doc --stage 2

for triple in %{?mingw_targets} %{?wasm_targets}; do
  %{__python3} ./x.py build --stage 2 --target=$triple std
done

%install
%{export_rust_env}

DESTDIR=%{buildroot} %{__python3} ./x.py install

for triple in %{?mingw_targets} %{?wasm_targets}; do
  DESTDIR=%{buildroot} %{__python3} ./x.py install --target=$triple std
done

# These are transient files used by x.py dist and install
rm -rf ./build/dist/ ./build/tmp/

# Make sure the shared libraries are in the proper libdir
%if "%{_libdir}" != "%{common_libdir}"
mkdir -p %{buildroot}%{_libdir}
find %{buildroot}%{common_libdir} -maxdepth 1 -type f -name '*.so' \
  -exec mv -v -t %{buildroot}%{_libdir} '{}' '+'
%endif

# The shared libraries should be executable for debuginfo extraction.
find %{buildroot}%{_libdir} -maxdepth 1 -type f -name '*.so' \
  -exec chmod -v +x '{}' '+'

# The libdir libraries are identical to those under rustlib/.  It's easier on
# library loading if we keep them in libdir, but we do need them in rustlib/
# to support dynamic linking for compiler plugins, so we'll symlink.
(cd "%{buildroot}%{rustlibdir}/%{rust_triple}/lib" &&
 find ../../../../%{_lib} -maxdepth 1 -name '*.so' |
 while read lib; do
   if [ -f "${lib##*/}" ]; then
     # make sure they're actually identical!
     cmp "$lib" "${lib##*/}"
     ln -v -f -s -t . "$lib"
   fi
 done)

# Remove installer artifacts (manifests, uninstall scripts, etc.)
find %{buildroot}%{rustlibdir} -maxdepth 1 -type f -exec rm -v '{}' '+'

# Remove backup files from %%configure munging
find %{buildroot}%{rustlibdir} -type f -name '*.orig' -exec rm -v '{}' '+'

# https://fedoraproject.org/wiki/Changes/Make_ambiguous_python_shebangs_error
# We don't actually need to ship any of those python scripts in rust-src anyway.
find %{buildroot}%{rustlibdir}/src -type f -name '*.py' -exec rm -v '{}' '+'

# FIXME: __os_install_post will strip the rlibs
# -- should we find a way to preserve debuginfo?

# Remove unwanted documentation files (we already package them)
rm -f %{buildroot}%{_docdir}/%{name}/README.md
rm -f %{buildroot}%{_docdir}/%{name}/COPYRIGHT
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE-APACHE
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE-MIT
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE-THIRD-PARTY
rm -f %{buildroot}%{_docdir}/%{name}/*.old

# Sanitize the HTML documentation
find %{buildroot}%{_docdir}/%{name}/html -empty -delete
find %{buildroot}%{_docdir}/%{name}/html -type f -exec chmod -x '{}' '+'

# Create the path for crate-devel packages
mkdir -p %{buildroot}%{_datadir}/cargo/registry

# Cargo no longer builds its own documentation
# https://github.com/rust-lang/cargo/pull/4904
mkdir -p %{buildroot}%{_docdir}/cargo
ln -sT ../rust/html/cargo/ %{buildroot}%{_docdir}/cargo/html

%if %without lldb
rm -f %{buildroot}%{_bindir}/rust-lldb
rm -f %{buildroot}%{rustlibdir}/etc/lldb_*
%endif

# We don't want Rust copies of LLVM tools (rust-lld, rust-llvm-dwp)
rm -f %{buildroot}%{rustlibdir}/%{rust_triple}/bin/rust-ll*

%if 0%{?rhel} && 0%{?rhel} >= 8
# This allows users to build packages using Rust Toolset.
%{__install} -D -m 644 %{S:100} %{buildroot}%{rpmmacrodir}/macros.rust-toolset
%endif


%check
%{export_rust_env}

# Sanity-check the installed binaries, debuginfo-stripped and all.
%{buildroot}%{_bindir}/cargo new build/hello-world
env RUSTC=%{buildroot}%{_bindir}/rustc \
    LD_LIBRARY_PATH="%{buildroot}%{_libdir}:$LD_LIBRARY_PATH" \
    %{buildroot}%{_bindir}/cargo run --manifest-path build/hello-world/Cargo.toml

# Try a build sanity-check for other targets
for triple in %{?mingw_targets} %{?wasm_targets}; do
  env RUSTC=%{buildroot}%{_bindir}/rustc \
      LD_LIBRARY_PATH="%{buildroot}%{_libdir}:$LD_LIBRARY_PATH" \
      %{buildroot}%{_bindir}/cargo build --manifest-path build/hello-world/Cargo.toml --target=$triple
done

# The results are not stable on koji, so mask errors and just log it.
# Some of the larger test artifacts are manually cleaned to save space.
%{__python3} ./x.py test --no-fail-fast --stage 2 || :
rm -rf "./build/%{rust_triple}/test/"

%{__python3} ./x.py test --no-fail-fast --stage 2 cargo || :
rm -rf "./build/%{rust_triple}/stage2-tools/%{rust_triple}/cit/"

%{__python3} ./x.py test --no-fail-fast --stage 2 clippy || :

env RLS_TEST_WAIT_FOR_AGES=1 \
%{__python3} ./x.py test --no-fail-fast --stage 2 rls || :

%{__python3} ./x.py test --no-fail-fast --stage 2 rustfmt || :


%ldconfig_scriptlets


%files
%license COPYRIGHT LICENSE-APACHE LICENSE-MIT
%doc README.md
%{_bindir}/rustc
%{_bindir}/rustdoc
%{_libdir}/*.so
%{_mandir}/man1/rustc.1*
%{_mandir}/man1/rustdoc.1*
%dir %{rustlibdir}
%dir %{rustlibdir}/%{rust_triple}
%dir %{rustlibdir}/%{rust_triple}/lib
%{rustlibdir}/%{rust_triple}/lib/*.so


%files std-static
%dir %{rustlibdir}
%dir %{rustlibdir}/%{rust_triple}
%dir %{rustlibdir}/%{rust_triple}/lib
%{rustlibdir}/%{rust_triple}/lib/*.rlib


%if %defined mingw_targets
%{lua: do
  for triple in string.gmatch(rpm.expand("%{mingw_targets}"), "%S+") do
    local subs = {
      triple = triple,
      rustlibdir = rpm.expand("%{rustlibdir}"),
    }
    local s = string.gsub([[

%files std-static-{{triple}}
%dir {{rustlibdir}}
%dir {{rustlibdir}}/{{triple}}
%dir {{rustlibdir}}/{{triple}}/lib
{{rustlibdir}}/{{triple}}/lib/*.rlib
{{rustlibdir}}/{{triple}}/lib/rs*.o
%exclude {{rustlibdir}}/{{triple}}/lib/*.dll
%exclude {{rustlibdir}}/{{triple}}/lib/*.dll.a
%exclude {{rustlibdir}}/{{triple}}/lib/self-contained

]], "{{(%w+)}}", subs)
    print(s)
  end
end}
%endif


%if %defined wasm_targets
%{lua: do
  for triple in string.gmatch(rpm.expand("%{wasm_targets}"), "%S+") do
    local subs = {
      triple = triple,
      rustlibdir = rpm.expand("%{rustlibdir}"),
      wasi = string.find(triple, "-wasi") and 1 or 0,
    }
    local s = string.gsub([[

%files std-static-{{triple}}
%dir {{rustlibdir}}
%dir {{rustlibdir}}/{{triple}}
%dir {{rustlibdir}}/{{triple}}/lib
{{rustlibdir}}/{{triple}}/lib/*.rlib
%if {{wasi}}
%dir {{rustlibdir}}/{{triple}}/lib/self-contained
{{rustlibdir}}/{{triple}}/lib/self-contained/crt*.o
{{rustlibdir}}/{{triple}}/lib/self-contained/libc.a
%endif

]], "{{(%w+)}}", subs)
    print(s)
  end
end}
%endif


%files debugger-common
%dir %{rustlibdir}
%dir %{rustlibdir}/etc
%{rustlibdir}/etc/rust_*.py*


%files gdb
%{_bindir}/rust-gdb
%{rustlibdir}/etc/gdb_*
%exclude %{_bindir}/rust-gdbgui


%if %with lldb
%files lldb
%{_bindir}/rust-lldb
%{rustlibdir}/etc/lldb_*
%endif


%files doc
%docdir %{_docdir}/%{name}
%dir %{_docdir}/%{name}
%dir %{_docdir}/%{name}/html
%{_docdir}/%{name}/html/*/
%{_docdir}/%{name}/html/*.html
%{_docdir}/%{name}/html/*.css
%{_docdir}/%{name}/html/*.js
%{_docdir}/%{name}/html/*.png
%{_docdir}/%{name}/html/*.svg
%{_docdir}/%{name}/html/*.woff2
%license %{_docdir}/%{name}/html/*.txt
%license %{_docdir}/%{name}/html/*.md


%files -n cargo
%license src/tools/cargo/LICENSE-APACHE src/tools/cargo/LICENSE-MIT src/tools/cargo/LICENSE-THIRD-PARTY
%doc src/tools/cargo/README.md
%{_bindir}/cargo
%{_libexecdir}/cargo*
%{_mandir}/man1/cargo*.1*
%{_sysconfdir}/bash_completion.d/cargo
%{_datadir}/zsh/site-functions/_cargo
%dir %{_datadir}/cargo
%dir %{_datadir}/cargo/registry


%files -n cargo-doc
%docdir %{_docdir}/cargo
%dir %{_docdir}/cargo
%{_docdir}/cargo/html


%files -n rustfmt
%{_bindir}/rustfmt
%{_bindir}/cargo-fmt
%doc src/tools/rustfmt/{README,CHANGELOG,Configurations}.md
%license src/tools/rustfmt/LICENSE-{APACHE,MIT}


%files -n rls
%{_bindir}/rls
%doc src/tools/rls/{README.md,COPYRIGHT,debugging.md}
%license src/tools/rls/LICENSE-{APACHE,MIT}


%files -n clippy
%{_bindir}/cargo-clippy
%{_bindir}/clippy-driver
%doc src/tools/clippy/{README.md,CHANGELOG.md}
%license src/tools/clippy/LICENSE-{APACHE,MIT}


%files src
%dir %{rustlibdir}
%{rustlibdir}/src


%files analysis
%{rustlibdir}/%{rust_triple}/analysis/


%if 0%{?rhel} && 0%{?rhel} >= 8
%files toolset
%{rpmmacrodir}/macros.rust-toolset
%endif


%changelog
* Tue Jul 19 2022 Josh Stone <jistone@redhat.com> - 1.62.1-1
- Update to 1.62.1.

* Wed Jul 13 2022 Josh Stone <jistone@redhat.com> - 1.62.0-2
- Prevent unsound coercions from functions with opaque return types.

* Thu Jun 30 2022 Josh Stone <jistone@redhat.com> - 1.62.0-1
- Update to 1.62.0.

* Fri Jun 03 2022 Josh Stone <jistone@redhat.com> - 1.61.0-1
- Update to 1.61.0.
- Add rust-toolset as a subpackage.

* Wed Apr 20 2022 Josh Stone <jistone@redhat.com> - 1.60.0-1
- Update to 1.60.0.

* Tue Apr 19 2022 Josh Stone <jistone@redhat.com> - 1.59.0-1
- Update to 1.59.0.

* Thu Jan 20 2022 Josh Stone <jistone@redhat.com> - 1.58.1-1
- Update to 1.58.1.

* Thu Jan 13 2022 Josh Stone <jistone@redhat.com> - 1.58.0-1
- Update to 1.58.0.

* Wed Dec 15 2021 Josh Stone <jistone@redhat.com> - 1.57.0-1
- Update to 1.57.0.

* Wed Dec 01 2021 Josh Stone <jistone@redhat.com> - 1.56.1-2
- Add rust-std-static-wasm32-wasi
  Resolves: rhbz#1980082

* Thu Nov 04 2021 Josh Stone <jistone@redhat.com> - 1.56.1-1
- Update to 1.56.1.

* Fri Oct 29 2021 Josh Stone <jistone@redhat.com> - 1.55.0-1
- Update to 1.55.0.

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 1.54.0-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Aug 04 2021 Josh Stone <jistone@redhat.com> - 1.54.0-1
- Update to 1.54.0.

* Tue Jun 22 2021 Josh Stone <jistone@redhat.com> - 1.53.0-1
- Update to 1.53.0.
- Update openssl crates to published versions for 3.0 support.

* Tue Jun 15 2021 Mohan Boddu <mboddu@redhat.com> - 1.52.1-4
- Rebuilt for RHEL 9 BETA for openssl 3.0

* Mon Jun 07 2021 Josh Stone <jistone@redhat.com> - 1.52.1-3
- Set rust.codegen-units-std=1 for all targets again.
- Add rust-std-static-wasm32-unknown-unknown.

* Tue May 18 2021 Josh Stone <jistone@redhat.com> - 1.52.1-2
- Rebuild for OpenSSL 3.0.0-alpha16

* Thu May 13 2021 Josh Stone <jistone@redhat.com> - 1.52.1-1
- Update to 1.52.1. Includes security fixes for CVE-2020-36323,
  CVE-2021-28876, CVE-2021-28878, CVE-2021-28879, and CVE-2021-31162.
- Initial support for OpenSSL 3.0.0-alpha15

* Wed Apr 28 2021 Josh Stone <jistone@redhat.com> - 1.51.0-1
- Update to 1.51.0. Includes security fixes for CVE-2021-28875
  and CVE-2021-28877.

* Tue Apr 27 2021 Josh Stone <jistone@redhat.com> - 1.50.0-1
- Update to 1.50.0.

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.49.0-5
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Fri Feb 12 2021 Josh Stone <jistone@redhat.com> - 1.49.0-4
- Rebuild without bootstrap binaries

* Thu Feb 11 2021 Josh Stone <jistone@redhat.com> - 1.49.0-3
- Re-bootstrap due to removed LLVM targets

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.49.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Jan 05 2021 Josh Stone <jistone@redhat.com> - 1.49.0-1
- Update to 1.49.0.

* Tue Dec 29 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 1.48.0-3
- De-bootstrap

* Mon Dec 28 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 1.48.0-2
- Rebuild for libgit2 1.1.x

* Thu Nov 19 2020 Josh Stone <jistone@redhat.com> - 1.48.0-1
- Update to 1.48.0.

* Sat Oct 10 2020 Jeff Law <law@redhat.com> - 1.47.0-2
- Re-enable LTO

* Thu Oct 08 2020 Josh Stone <jistone@redhat.com> - 1.47.0-1
- Update to 1.47.0.

* Fri Aug 28 2020 Fabio Valentini <decathorpe@gmail.com> - 1.46.0-2
- Fix LTO with doctests (backported cargo PR#8657).

* Thu Aug 27 2020 Josh Stone <jistone@redhat.com> - 1.46.0-1
- Update to 1.46.0.

* Mon Aug 03 2020 Josh Stone <jistone@redhat.com> - 1.45.2-1
- Update to 1.45.2.

* Thu Jul 30 2020 Josh Stone <jistone@redhat.com> - 1.45.1-1
- Update to 1.45.1.

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.45.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu Jul 16 2020 Josh Stone <jistone@redhat.com> - 1.45.0-1
- Update to 1.45.0.

* Wed Jul 01 2020 Jeff Law <law@redhat.com> - 1.44.1-2
- Disable LTO

* Thu Jun 18 2020 Josh Stone <jistone@redhat.com> - 1.44.1-1
- Update to 1.44.1.

* Thu Jun 04 2020 Josh Stone <jistone@redhat.com> - 1.44.0-1
- Update to 1.44.0.

* Thu May 07 2020 Josh Stone <jistone@redhat.com> - 1.43.1-1
- Update to 1.43.1.

* Thu Apr 23 2020 Josh Stone <jistone@redhat.com> - 1.43.0-1
- Update to 1.43.0.

* Thu Mar 12 2020 Josh Stone <jistone@redhat.com> - 1.42.0-1
- Update to 1.42.0.

* Thu Feb 27 2020 Josh Stone <jistone@redhat.com> - 1.41.1-1
- Update to 1.41.1.

* Thu Feb 20 2020 Josh Stone <jistone@redhat.com> - 1.41.0-2
- Rebuild with llvm9.0

* Thu Jan 30 2020 Josh Stone <jistone@redhat.com> - 1.41.0-1
- Update to 1.41.0.

* Thu Jan 16 2020 Josh Stone <jistone@redhat.com> - 1.40.0-3
- Build compiletest with in-tree libtest

* Tue Jan 07 2020 Josh Stone <jistone@redhat.com> - 1.40.0-2
- Fix compiletest with newer (local-rebuild) libtest
- Fix ARM EHABI unwinding

* Thu Dec 19 2019 Josh Stone <jistone@redhat.com> - 1.40.0-1
- Update to 1.40.0.

* Tue Nov 12 2019 Josh Stone <jistone@redhat.com> - 1.39.0-2
- Fix a couple build and test issues with rustdoc.

* Thu Nov 07 2019 Josh Stone <jistone@redhat.com> - 1.39.0-1
- Update to 1.39.0.

* Fri Sep 27 2019 Josh Stone <jistone@redhat.com> - 1.38.0-2
- Filter the libraries included in rust-std (rhbz1756487)

* Thu Sep 26 2019 Josh Stone <jistone@redhat.com> - 1.38.0-1
- Update to 1.38.0.

* Thu Aug 15 2019 Josh Stone <jistone@redhat.com> - 1.37.0-1
- Update to 1.37.0.

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.36.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jul 04 2019 Josh Stone <jistone@redhat.com> - 1.36.0-1
- Update to 1.36.0.

* Wed May 29 2019 Josh Stone <jistone@redhat.com> - 1.35.0-2
- Fix compiletest for rebuild testing.

* Thu May 23 2019 Josh Stone <jistone@redhat.com> - 1.35.0-1
- Update to 1.35.0.

* Tue May 14 2019 Josh Stone <jistone@redhat.com> - 1.34.2-1
- Update to 1.34.2 -- fixes CVE-2019-12083.

* Tue Apr 30 2019 Josh Stone <jistone@redhat.com> - 1.34.1-3
- Set rust.codegen-units-std=1

* Fri Apr 26 2019 Josh Stone <jistone@redhat.com> - 1.34.1-2
- Remove the ThinLTO workaround.

* Thu Apr 25 2019 Josh Stone <jistone@redhat.com> - 1.34.1-1
- Update to 1.34.1.
- Add a ThinLTO fix for rhbz1701339.

* Thu Apr 11 2019 Josh Stone <jistone@redhat.com> - 1.34.0-1
- Update to 1.34.0.

* Fri Mar 01 2019 Josh Stone <jistone@redhat.com> - 1.33.0-2
- Fix deprecations for self-rebuild

* Thu Feb 28 2019 Josh Stone <jistone@redhat.com> - 1.33.0-1
- Update to 1.33.0.

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.32.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jan 17 2019 Josh Stone <jistone@redhat.com> - 1.32.0-1
- Update to 1.32.0.

* Mon Jan 07 2019 Josh Stone <jistone@redhat.com> - 1.31.1-9
- Update to 1.31.1 for RLS fixes.

* Thu Dec 06 2018 Josh Stone <jistone@redhat.com> - 1.31.0-8
- Update to 1.31.0 -- Rust 2018!
- clippy/rls/rustfmt are no longer -preview

* Thu Nov 08 2018 Josh Stone <jistone@redhat.com> - 1.30.1-7
- Update to 1.30.1.

* Thu Oct 25 2018 Josh Stone <jistone@redhat.com> - 1.30.0-6
- Update to 1.30.0.

* Mon Oct 22 2018 Josh Stone <jistone@redhat.com> - 1.29.2-5
- Rebuild without bootstrap binaries.

* Sat Oct 20 2018 Josh Stone <jistone@redhat.com> - 1.29.2-4
- Re-bootstrap armv7hl due to rhbz#1639485

* Fri Oct 12 2018 Josh Stone <jistone@redhat.com> - 1.29.2-3
- Update to 1.29.2.

* Tue Sep 25 2018 Josh Stone <jistone@redhat.com> - 1.29.1-2
- Update to 1.29.1.
- Security fix for str::repeat (pending CVE).

* Thu Sep 13 2018 Josh Stone <jistone@redhat.com> - 1.29.0-1
- Update to 1.29.0.
- Add a clippy-preview subpackage

* Mon Aug 13 2018 Josh Stone <jistone@redhat.com> - 1.28.0-3
- Use llvm6.0 instead of llvm-7 for now

* Tue Aug 07 2018 Josh Stone <jistone@redhat.com> - 1.28.0-2
- Rebuild for LLVM ppc64/s390x fixes

* Thu Aug 02 2018 Josh Stone <jistone@redhat.com> - 1.28.0-1
- Update to 1.28.0.

* Tue Jul 24 2018 Josh Stone <jistone@redhat.com> - 1.27.2-4
- Update to 1.27.2.

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.27.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jul 10 2018 Josh Stone <jistone@redhat.com> - 1.27.1-2
- Update to 1.27.1.
- Security fix for CVE-2018-1000622

* Thu Jun 21 2018 Josh Stone <jistone@redhat.com> - 1.27.0-1
- Update to 1.27.0.

* Tue Jun 05 2018 Josh Stone <jistone@redhat.com> - 1.26.2-4
- Rebuild without bootstrap binaries.

* Tue Jun 05 2018 Josh Stone <jistone@redhat.com> - 1.26.2-3
- Update to 1.26.2.
- Re-bootstrap to deal with LLVM symbol changes.

* Tue May 29 2018 Josh Stone <jistone@redhat.com> - 1.26.1-2
- Update to 1.26.1.

* Thu May 10 2018 Josh Stone <jistone@redhat.com> - 1.26.0-1
- Update to 1.26.0.

* Mon Apr 16 2018 Dan Callaghan <dcallagh@redhat.com> - 1.25.0-3
- Add cargo, rls, and analysis

* Tue Apr 10 2018 Josh Stone <jistone@redhat.com> - 1.25.0-2
- Filter codegen-backends from Provides too.

* Thu Mar 29 2018 Josh Stone <jistone@redhat.com> - 1.25.0-1
- Update to 1.25.0.

* Thu Mar 01 2018 Josh Stone <jistone@redhat.com> - 1.24.1-1
- Update to 1.24.1.

* Wed Feb 21 2018 Josh Stone <jistone@redhat.com> - 1.24.0-3
- Backport a rebuild fix for rust#48308.

* Mon Feb 19 2018 Josh Stone <jistone@redhat.com> - 1.24.0-2
- rhbz1546541: drop full-bootstrap; cmp libs before symlinking.
- Backport pr46592 to fix local_rebuild bootstrapping.
- Backport pr48362 to fix relative/absolute libdir.

* Thu Feb 15 2018 Josh Stone <jistone@redhat.com> - 1.24.0-1
- Update to 1.24.0.

* Mon Feb 12 2018 Iryna Shcherbina <ishcherb@redhat.com> - 1.23.0-4
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Tue Feb 06 2018 Josh Stone <jistone@redhat.com> - 1.23.0-3
- Use full-bootstrap to work around a rebuild issue.
- Patch binaryen for GCC 8

* Thu Feb 01 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.23.0-2
- Switch to %%ldconfig_scriptlets

* Mon Jan 08 2018 Josh Stone <jistone@redhat.com> - 1.23.0-1
- Update to 1.23.0.

* Thu Nov 23 2017 Josh Stone <jistone@redhat.com> - 1.22.1-1
- Update to 1.22.1.

* Thu Oct 12 2017 Josh Stone <jistone@redhat.com> - 1.21.0-1
- Update to 1.21.0.

* Mon Sep 11 2017 Josh Stone <jistone@redhat.com> - 1.20.0-2
- ABI fixes for ppc64 and s390x.

* Thu Aug 31 2017 Josh Stone <jistone@redhat.com> - 1.20.0-1
- Update to 1.20.0.
- Add a rust-src subpackage.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.19.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.19.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 24 2017 Josh Stone <jistone@redhat.com> - 1.19.0-2
- Use find-debuginfo.sh --keep-section .rustc

* Thu Jul 20 2017 Josh Stone <jistone@redhat.com> - 1.19.0-1
- Update to 1.19.0.

* Thu Jun 08 2017 Josh Stone <jistone@redhat.com> - 1.18.0-1
- Update to 1.18.0.

* Mon May 08 2017 Josh Stone <jistone@redhat.com> - 1.17.0-2
- Move shared libraries back to libdir and symlink in rustlib

* Thu Apr 27 2017 Josh Stone <jistone@redhat.com> - 1.17.0-1
- Update to 1.17.0.

* Mon Mar 20 2017 Josh Stone <jistone@redhat.com> - 1.16.0-3
- Make rust-lldb arch-specific to deal with lldb deps

* Fri Mar 17 2017 Josh Stone <jistone@redhat.com> - 1.16.0-2
- Limit rust-lldb arches

* Thu Mar 16 2017 Josh Stone <jistone@redhat.com> - 1.16.0-1
- Update to 1.16.0.
- Use rustbuild instead of the old makefiles.
- Update bootstrapping to include rust-std and cargo.
- Add a rust-lldb subpackage.

* Thu Feb 09 2017 Josh Stone <jistone@redhat.com> - 1.15.1-1
- Update to 1.15.1.
- Require rust-rpm-macros for new crate packaging.
- Keep shared libraries under rustlib/, only debug-stripped.
- Merge and clean up conditionals for epel7.

* Fri Dec 23 2016 Josh Stone <jistone@redhat.com> - 1.14.0-2
- Rebuild without bootstrap binaries.

* Thu Dec 22 2016 Josh Stone <jistone@redhat.com> - 1.14.0-1
- Update to 1.14.0.
- Rewrite bootstrap logic to target specific arches.
- Bootstrap ppc64, ppc64le, s390x. (thanks to Sinny Kumari for testing!)

* Thu Nov 10 2016 Josh Stone <jistone@redhat.com> - 1.13.0-1
- Update to 1.13.0.
- Use hardening flags for linking.
- Split the standard library into its own package
- Centralize rustlib/ under /usr/lib/ for multilib integration.

* Thu Oct 20 2016 Josh Stone <jistone@redhat.com> - 1.12.1-1
- Update to 1.12.1.

* Fri Oct 14 2016 Josh Stone <jistone@redhat.com> - 1.12.0-7
- Rebuild with LLVM 3.9.
- Add ncurses-devel for llvm-config's -ltinfo.

* Thu Oct 13 2016 Josh Stone <jistone@redhat.com> - 1.12.0-6
- Rebuild with llvm-static, preparing for 3.9

* Fri Oct 07 2016 Josh Stone <jistone@redhat.com> - 1.12.0-5
- Rebuild with fixed eu-strip (rhbz1380961)

* Fri Oct 07 2016 Josh Stone <jistone@redhat.com> - 1.12.0-4
- Rebuild without bootstrap binaries.

* Thu Oct 06 2016 Josh Stone <jistone@redhat.com> - 1.12.0-3
- Bootstrap aarch64.
- Use jemalloc's MALLOC_CONF to work around #36944.
- Apply pr36933 to really disable armv7hl NEON.

* Sat Oct 01 2016 Josh Stone <jistone@redhat.com> - 1.12.0-2
- Protect .rustc from rpm stripping.

* Fri Sep 30 2016 Josh Stone <jistone@redhat.com> - 1.12.0-1
- Update to 1.12.0.
- Always use --local-rust-root, even for bootstrap binaries.
- Remove the rebuild conditional - the build system now figures it out.
- Let minidebuginfo do its thing, since metadata is no longer a note.
- Let rust build its own compiler-rt builtins again.

* Sat Sep 03 2016 Josh Stone <jistone@redhat.com> - 1.11.0-3
- Rebuild without bootstrap binaries.

* Fri Sep 02 2016 Josh Stone <jistone@redhat.com> - 1.11.0-2
- Bootstrap armv7hl, with backported no-neon patch.

* Wed Aug 24 2016 Josh Stone <jistone@redhat.com> - 1.11.0-1
- Update to 1.11.0.
- Drop the backported patches.
- Patch get-stage0.py to trust existing bootstrap binaries.
- Use libclang_rt.builtins from compiler-rt, dodging llvm-static issues.
- Use --local-rust-root to make sure the right bootstrap is used.

* Sat Aug 13 2016 Josh Stone <jistone@redhat.com> 1.10.0-4
- Rebuild without bootstrap binaries.

* Fri Aug 12 2016 Josh Stone <jistone@redhat.com> - 1.10.0-3
- Initial import into Fedora (#1356907), bootstrapped
- Format license text as suggested in review.
- Note how the tests already run in parallel.
- Undefine _include_minidebuginfo, because it duplicates ".note.rustc".
- Don't let checks fail the whole build.
- Note that -doc can't be noarch, as rpmdiff doesn't allow variations.

* Tue Jul 26 2016 Josh Stone <jistone@redhat.com> - 1.10.0-2
- Update -doc directory ownership, and mark its licenses.
- Package and declare licenses for libbacktrace and hoedown.
- Set bootstrap_base as a global.
- Explicitly require python2.

* Thu Jul 14 2016 Josh Stone <jistone@fedoraproject.org> - 1.10.0-1
- Initial package, bootstrapped
