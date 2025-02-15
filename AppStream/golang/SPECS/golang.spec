%undefine _missing_build_ids_terminate_build

%global bcond_with strict_fips

# build ids are not currently generated:
# https://code.google.com/p/go/issues/detail?id=5238
#
# also, debuginfo extraction currently fails with
# "Failed to write file: invalid section alignment"
%global debug_package %{nil}

# we are shipping the full contents of src in the data subpackage, which
# contains binary-like things (ELF data for tests, etc)
%global _binaries_in_noarch_packages_terminate_build 0

# Do not check any files in doc or src for requires
%global __requires_exclude_from ^(%{_datadir}|/usr/lib)/%{name}/(doc|src)/.*$

# Don't alter timestamps of especially the .a files (or else go will rebuild later)
# Actually, don't strip at all since we are not even building debug packages and this corrupts the dwarf testdata
%global __strip /bin/true

# rpmbuild magic to keep from having meta dependency on libc.so.6
%define _use_internal_dependency_generator 0
%define __find_requires %{nil}
%global __spec_install_post /usr/lib/rpm/check-rpaths   /usr/lib/rpm/check-buildroot  \
  /usr/lib/rpm/brp-compress

# Define GOROOT macros
%global goroot          %{_prefix}/lib/%{name}
%global gopath          %{_datadir}/gocode
%global golang_arches   x86_64 aarch64 ppc64le s390x %{arm}
%global golibdir        %{_libdir}/%{name}

# Golang build options.

# Build golang using external/internal(close to cgo disabled) linking.
%ifarch x86_64 ppc64le %{arm} aarch64 s390x
%global external_linker 1
%else
%global external_linker 0
%endif

# Build golang with cgo enabled/disabled(later equals more or less to internal linking).
%ifarch x86_64 ppc64le %{arm} aarch64 s390x
%global cgo_enabled 1
%else
%global cgo_enabled 0
%endif

# Use golang/gcc-go as bootstrap compiler
%ifarch %{golang_arches}
%global golang_bootstrap 1
%else
%global golang_bootstrap 0
%endif

# Controls what ever we fail on failed tests
%ifarch x86_64 %{arm} ppc64le s390x
%global fail_on_tests 1
%else
%global fail_on_tests 0
%endif

# Build golang shared objects for stdlib
%ifarch 0
%global shared 1
%else
%global shared 0
%endif

# Pre build std lib with -race enabled
# Disabled due to 1.20 new cache usage, see 1.20 upstream release notes
%global race 0

%ifarch x86_64
%global gohostarch  amd64
%endif
%ifarch %{arm}
%global gohostarch  arm
%endif
%ifarch aarch64
%global gohostarch  arm64
%endif
%ifarch ppc64
%global gohostarch  ppc64
%endif
%ifarch ppc64le
%global gohostarch  ppc64le
%endif
%ifarch s390x
%global gohostarch  s390x
%endif

%global go_api 1.22
%global go_version 1.22.9
%global version %{go_version}
%global pkg_release 1

# LLVM compiler-rt version for race detector
#global llvm_compiler_rt_version 18.1.8

Name:           golang
Version:        %{version}
Release:        2%{?dist}.redsleeve
Summary:        The Go Programming Language
# source tree includes several copies of Mark.Twain-Tom.Sawyer.txt under Public Domain
License:        BSD and Public Domain
URL:            http://golang.org/
Source0:        https://github.com/golang/go/archive/refs/tags/go%{version}.tar.gz
# Go's FIPS mode bindings are now provided as a standalone
# module instead of in tree.  This makes it easier to see
# the actual changes vs upstream Go.  The module source is
# located at https://github.com/golang-fips/openssl-fips,
# And pre-genetated patches to set up the module for a given
# Go release are located at https://github.com/golang-fips/go.
Source1:	https://github.com/golang-fips/go/archive/refs/tags/go%{version}-%{pkg_release}-openssl-fips.tar.gz
# make possible to override default traceback level at build time by setting build tag rpm_crashtraceback
Source2:        fedora.go
#Source3: 	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{llvm_compiler_rt_version}/compiler-rt-%{llvm_compiler_rt_version}.src.tar.xz

# The compiler is written in Go. Needs go(1.4+) compiler for build.
# Actual Go based bootstrap compiler provided by above source.
%if !%{golang_bootstrap}
BuildRequires:  gcc-go >= 5
%else
BuildRequires:  golang
%endif
%if 0%{?rhel} > 6 || 0%{?fedora} > 0
BuildRequires:  hostname
%else
BuildRequires:  net-tools
%endif
# For OpenSSL FIPS
BuildRequires:  openssl-devel
# for tests
BuildRequires:  pcre-devel, glibc-static, perl

# Necessary for building llvm address sanitizer for Go race detector
#BuildRequires: libstdc++-devel
#BuildRequires: clang

Provides:       go = %{version}-%{release}
Requires:       %{name}-bin = %{version}-%{release}
Requires:       %{name}-src = %{version}-%{release}
#Requires:       %{name}-race = %{version}-%{release}
Requires:       openssl-devel
Requires:       diffutils

# Proposed patch by jcajka https://golang.org/cl/86541
Patch221:       fix_TestScript_list_std.patch

Patch1939923:   skip_test_rhbz1939923.patch

Patch4:		modify_go.env.patch
Patch6:		skip_TestCrashDumpsAllThreads.patch

# Having documentation separate was broken
Obsoletes:      %{name}-docs < 1.1-4

# RPM can't handle symlink -> dir with subpackages, so merge back
Obsoletes:      %{name}-data < 1.1.1-4

# These are the only RHEL/Fedora architectures that we compile this package for
ExclusiveArch:  %{golang_arches}

Source100:      golang-gdbinit
Source101:      golang-prelink.conf

%description
%{summary}.

%package       docs
Summary:       Golang compiler docs
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch
Obsoletes:     %{name}-docs < 1.1-4

%description   docs
%{summary}.

%package       misc
Summary:       Golang compiler miscellaneous sources
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description   misc
%{summary}.

%package       tests
Summary:       Golang compiler tests for stdlib
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description   tests
%{summary}.

%package        src
Summary:        Golang compiler source tree
BuildArch:      noarch

%description    src
%{summary}

%package        bin
Summary:        Golang core compiler tools
Requires:       %{name} = %{version}-%{release}

# We strip the meta dependency, but go does require glibc.
# This is an odd issue, still looking for a better fix.
Requires:       glibc
Requires:       /usr/bin/gcc
%description    bin
%{summary}

# Workaround old RPM bug of symlink-replaced-with-dir failure
%pretrans -p <lua>
for _,d in pairs({"api", "doc", "include", "lib", "src"}) do
  path = "%{goroot}/" .. d
  if posix.stat(path, "type") == "link" then
    os.remove(path)
    posix.mkdir(path)
  end
end

%if %{shared}
%package        shared
Summary:        Golang shared object libraries

%description    shared
%{summary}.
%endif

%package -n go-toolset
Summary:        Package that installs go-toolset
Requires:       %{name} = %{version}-%{release}
%ifarch x86_64 aarch64 ppc64le
Requires:       delve
%endif

%description -n go-toolset
This is the main package for go-toolset.


#package race
#Summary:	Race detetector library object files.
#Requires:       %{name} = %{version}-%{release}

#description    race
#Binary library objects for Go's race detector.

%prep
%setup -q -n go-go%{version}

pushd ..
tar -xf %{SOURCE1}
popd
patch_dir="../go-go%{version}-%{pkg_release}-openssl-fips/patches"
# Add --no-backup-if-mismatch option to avoid creating .orig temp files
for p in "$patch_dir"/*.patch; do
	echo "Applying $p"
	patch --no-backup-if-mismatch -p1 < $p
done

# Configure crypto tests
pushd ../go-go%{version}-%{pkg_release}-openssl-fips
ln -s ../go-go%{version} go
./scripts/configure-crypto-tests.sh
popd

%autopatch -p1

sed -i '1s/$/ (%{?rhel:Red Hat} %{version}-%{release})/' VERSION

cp %{SOURCE2} ./src/runtime/
# Delete the bundled race detector objects.
find ./src/runtime/race/ -name "race_*.syso" -exec rm {} \;

# Delete the boring binary blob.  We use the system OpenSSL instead.
rm -rf src/crypto/internal/boring/syso

%build
set -xe
# print out system information
uname -a
cat /proc/cpuinfo
cat /proc/meminfo

# Build race detector .syso's from llvm sources
#global tsan_buildflags %(echo %{build_cflags} | sed 's/-mtls-dialect=gnu2//')
#mkdir ../llvm

#tar -xf %{SOURCE3} -C ../llvm
#tsan_go_dir="../llvm/compiler-rt-%{llvm_compiler_rt_version}.src/lib/tsan/go"

# The script uses uname -a and grep to set the GOARCH.  This
# is unreliable and can get the wrong architecture in
# circumstances like cross-architecture emulation.  We fix it
# by just reading GOARCH directly from Go.
#export GOARCH=$(go env GOARCH)


#ifarch x86_64
#pushd "${tsan_go_dir}"
#  CFLAGS="${tsan_buildflags}" CC=clang GOAMD64=v3 ./buildgo.sh
#popd
#cp "${tsan_go_dir}"/race_linux_amd64.syso ./src/runtime/race/internal/amd64v3/race_linux.syso

#pushd "${tsan_go_dir}"
#  CFLAGS="${tsan_buildflags}" CC=clang GOAMD64=v1 ./buildgo.sh
#popd
#cp "${tsan_go_dir}"/race_linux_amd64.syso ./src/runtime/race/internal/amd64v1/race_linux.syso

#else
#pushd "${tsan_go_dir}"
#  CFLAGS="${tsan_buildflags}" CC=clang ./buildgo.sh
#popd
#cp "${tsan_go_dir}"/race_linux_%{gohostarch}.syso ./src/runtime/race/race_linux_%{gohostarch}.syso
#endif


# bootstrap compiler GOROOT
%if !%{golang_bootstrap}
export GOROOT_BOOTSTRAP=/
%else
export GOROOT_BOOTSTRAP=/opt/rh/go-toolset-1.10/root/usr/lib/go-toolset-1.10-golang
%endif

# set up final install location
export GOROOT_FINAL=%{goroot}

export GOHOSTOS=linux
export GOHOSTARCH=%{gohostarch}

pushd src
# use our gcc options for this build, but store gcc as default for compiler
export CFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"
export CC="gcc"
export CC_FOR_TARGET="gcc"
export GOOS=linux
export GOARCH=%{gohostarch}

DEFAULT_GO_LD_FLAGS=""
%if !%{external_linker}
export GO_LDFLAGS="-linkmode internal $DEFAULT_GO_LD_FLAGS"
%else
# Only pass a select subset of the external hardening flags. We do not pass along
# the default $RPM_LD_FLAGS as on certain arches Go does not fully, correctly support
# building in PIE mode.
export GO_LDFLAGS="\"-extldflags=-Wl,-z,now,-z,relro\" $DEFAULT_GO_LD_FLAGS"
%endif
%if !%{cgo_enabled}
export CGO_ENABLED=0
%endif
./make.bash --no-clean
popd

# build shared std lib
%if %{shared}
GOROOT=$(pwd) PATH=$(pwd)/bin:$PATH go install -buildmode=shared std
%endif

%if %{race}
GOROOT=$(pwd) PATH=$(pwd)/bin:$PATH go install -race std
%endif


%install

rm -rf $RPM_BUILD_ROOT

# create the top level directories
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{goroot}

# remove bootstrap binaries
rm -rf pkg/bootstrap/bin

# install everything into libdir (until symlink problems are fixed)
# https://code.google.com/p/go/issues/detail?id=5830
cp -apv api bin doc lib pkg src misc test go.env VERSION \
   $RPM_BUILD_ROOT%{goroot}

# bz1099206
find $RPM_BUILD_ROOT%{goroot}/src -exec touch -r $RPM_BUILD_ROOT%{goroot}/VERSION "{}" \;
# and level out all the built archives
touch $RPM_BUILD_ROOT%{goroot}/pkg
find $RPM_BUILD_ROOT%{goroot}/pkg -exec touch -r $RPM_BUILD_ROOT%{goroot}/pkg "{}" \;
# generate the spec file ownership of this source tree and packages
cwd=$(pwd)
src_list=$cwd/go-src.list
pkg_list=$cwd/go-pkg.list
shared_list=$cwd/go-shared.list
misc_list=$cwd/go-misc.list
docs_list=$cwd/go-docs.list
tests_list=$cwd/go-tests.list
rm -f $src_list $pkg_list $docs_list $misc_list $tests_list $shared_list
touch $src_list $pkg_list $docs_list $misc_list $tests_list $shared_list
pushd $RPM_BUILD_ROOT%{goroot}
    find src/ -type d -a \( ! -name testdata -a ! -ipath '*/testdata/*' \) -printf '%%%dir %{goroot}/%p\n' >> $src_list
    find src/ ! -type d -a \( ! -ipath '*/testdata/*' -a ! -name '*_test*.go' \) -printf '%{goroot}/%p\n' >> $src_list

    find bin/ pkg/ -type d -a ! -path '*_dynlink/*' -a ! -path '*_race/*' -printf '%%%dir %{goroot}/%p\n' >> $pkg_list
    find bin/ pkg/ ! -type d -a ! -path '*_dynlink/*' -a ! -path '*_race/*' -printf '%{goroot}/%p\n' >> $pkg_list

    find doc/ -type d -printf '%%%dir %{goroot}/%p\n' >> $docs_list
    find doc/ ! -type d -printf '%{goroot}/%p\n' >> $docs_list

    find misc/ -type d -printf '%%%dir %{goroot}/%p\n' >> $misc_list
    find misc/ ! -type d -printf '%{goroot}/%p\n' >> $misc_list

%if %{shared}
    mkdir -p %{buildroot}/%{_libdir}/
    mkdir -p %{buildroot}/%{golibdir}/
    for file in $(find .  -iname "*.so" ); do
        chmod 755 $file
        mv  $file %{buildroot}/%{golibdir}
        pushd $(dirname $file)
        ln -fs %{golibdir}/$(basename $file) $(basename $file)
        popd
        echo "%%{goroot}/$file" >> $shared_list
        echo "%%{golibdir}/$(basename $file)" >> $shared_list
    done

    find pkg/*_dynlink/ -type d -printf '%%%dir %{goroot}/%p\n' >> $shared_list
    find pkg/*_dynlink/ ! -type d -printf '%{goroot}/%p\n' >> $shared_list
%endif

    find test/ -type d -printf '%%%dir %{goroot}/%p\n' >> $tests_list
    find test/ ! -type d -printf '%{goroot}/%p\n' >> $tests_list
    find src/ -type d -a \( -name testdata -o -ipath '*/testdata/*' \) -printf '%%%dir %{goroot}/%p\n' >> $tests_list
    find src/ ! -type d -a \( -ipath '*/testdata/*' -o -name '*_test*.go' \) -printf '%{goroot}/%p\n' >> $tests_list
    # this is only the zoneinfo.zip
    find lib/ -type d -printf '%%%dir %{goroot}/%p\n' >> $tests_list
    find lib/ ! -type d -printf '%{goroot}/%p\n' >> $tests_list
popd

# remove the doc Makefile
rm -rfv $RPM_BUILD_ROOT%{goroot}/doc/Makefile

# put binaries to bindir, linked to the arch we're building,
# leave the arch independent pieces in {goroot}
mkdir -p $RPM_BUILD_ROOT%{goroot}/bin/linux_%{gohostarch}
ln -sf %{goroot}/bin/go $RPM_BUILD_ROOT%{_bindir}/go
ln -sf %{goroot}/bin/gofmt $RPM_BUILD_ROOT%{_bindir}/gofmt

# ensure these exist and are owned
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/github.com
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/bitbucket.org
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/code.google.com/p
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/golang.org/x

# gdbinit
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/gdbinit.d
cp -av %{SOURCE100} $RPM_BUILD_ROOT%{_sysconfdir}/gdbinit.d/golang.gdb

# prelink blacklist
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/prelink.conf.d
cp -av %{SOURCE101} $RPM_BUILD_ROOT%{_sysconfdir}/prelink.conf.d/golang.conf

# Quick fix for the rhbz#2014704
sed -i 's/const defaultGO_LDSO = `.*`/const defaultGO_LDSO = ``/' $RPM_BUILD_ROOT%{goroot}/src/internal/buildcfg/zbootstrap.go

%check
export GOROOT=$(pwd -P)
export PATH="$GOROOT"/bin:"$PATH"
cd src

# Add some sanity checks.
echo "GO VERSION:"
go version

echo "GO ENVIRONMENT:"
go env

export CC="gcc"
export CFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"
%if !%{external_linker}
export GO_LDFLAGS="-linkmode internal"
%else
export GO_LDFLAGS="-extldflags '$RPM_LD_FLAGS'"
%endif
%if !%{cgo_enabled} || !%{external_linker}
export CGO_ENABLED=0
%endif

# make sure to not timeout
export GO_TEST_TIMEOUT_SCALE=2

export GO_TEST_RUN=""
%ifarch aarch64
  export GO_TEST_RUN="-run=!testshared"
%endif

%if %{fail_on_tests}

./run.bash --no-rebuild -v -v -v -k $GO_TEST_RUN

# Run tests with FIPS enabled.
export GOLANG_FIPS=1
export OPENSSL_FORCE_FIPS_MODE=1
pushd crypto
  # Run all crypto tests but skip TLS, we will run FIPS specific TLS tests later
  go test -timeout 50m $(go list ./... | grep -v tls) -v
  # Check that signature functions have parity between boring and notboring
  CGO_ENABLED=0 go test -timeout 50m $(go list ./... | grep -v tls) -v
popd
# Run all FIPS specific TLS tests
pushd crypto/tls
  go test -v -run "Boring"
popd
%else
./run.bash --no-rebuild -v -v -v -k || :
%endif
cd ..

%files

%doc LICENSE PATENTS
# VERSION has to be present in the GOROOT, for `go install std` to work
%doc %{goroot}/VERSION
%dir %{goroot}/doc
%doc %{goroot}/doc/*

# go files
%dir %{goroot}
%exclude %{goroot}/bin/
%exclude %{goroot}/pkg/
%exclude %{goroot}/src/
%exclude %{goroot}/doc/
%exclude %{goroot}/misc/
%exclude %{goroot}/test/
%{goroot}/*

# ensure directory ownership, so they are cleaned up if empty
%dir %{gopath}
%dir %{gopath}/src
%dir %{gopath}/src/github.com/
%dir %{gopath}/src/bitbucket.org/
%dir %{gopath}/src/code.google.com/
%dir %{gopath}/src/code.google.com/p/
%dir %{gopath}/src/golang.org
%dir %{gopath}/src/golang.org/x

# gdbinit (for gdb debugging)
%{_sysconfdir}/gdbinit.d

# prelink blacklist
%{_sysconfdir}/prelink.conf.d

%files -f go-src.list src
#ifarch x86_64
#exclude %{goroot}/src/runtime/race/internal/amd64v1/race_linux.syso
#exclude %{goroot}/src/runtime/race/internal/amd64v3/race_linux.syso
#else
#exclude %{goroot}/src/runtime/race/race_linux_%{gohostarch}.syso
#endif

%files -f go-docs.list docs

%files -f go-misc.list misc

%files -f go-tests.list tests

%files -f go-pkg.list bin
%{_bindir}/go
%{_bindir}/gofmt
%{goroot}/go.env

%if %{shared}
%files -f go-shared.list shared
%endif

%files -n go-toolset

#files race
#ifarch x86_64
#{goroot}/src/runtime/race/internal/amd64v1/race_linux.syso
#{goroot}/src/runtime/race/internal/amd64v3/race_linux.syso
#else
#{goroot}/src/runtime/race/race_linux_%{gohostarch}.syso
#endif

%changelog
* Tue Dec 24 2024 Jacco Ligthart <jacco@redsleeve.org> - 1.22.9-2.redsleeve
- added arm to golang_arches
- removed custom race detector

* Thu Nov 14 2024 David Benoit <dbenoit@redhat.com> - 1.22.9-2
- Fix sources
- Related: RHEL-67672

* Thu Nov 14 2024 David Benoit <dbenoit@redhat.com> - 1.22.9-1
- Update to Go 1.22.9
- Resolves: RHEL-67672

* Thu Oct 03 2024 Archana <aravinda@redhat.com> - 1.22.7-2
- Rebuilt to use right build target
- Related: RHEL-57867

* Tue Sep 24 2024 David Benoit <dbenoit@redhat.com> - 1.22.7-1
- Update to Go 1.22.7
- Remove fix-standard-crypto-panic.patch (upstreamed)
- Resolves: RHEL-57867

* Wed Aug 14 2024 David Benoit <dbenoit@redhat.com> - 1.22.5-2
- Rebuild race detector archives from LLVM sources
- Add golang-race subpackage
- Resolves: RHEL-33421
- Remove unused crypto/internal/boring/syso package
- Resolves: RHEL-54335

* Thu Jul 11 2024 Archana <aravinda@redhat.com> - 1.22.5-1
- Rebase to Go1.22.5 to address CVE-2024-24791
- Resolves: RHEL-46973

* Thu Jun 27 2024 David Benoit <dbenoit@redhat.com> - 1.22.4-2
- Fix panic in standard crypto mode without openssl
- Resolves: RHEL-45359

* Thu Jun 6 2024 Archana Ravindar <aravinda@redhat.com> - 1.22.4-1
- Rebase to Go1.22.4 that includes fixes for CVE-2024-24789 and CVE-2024-24790
- Resolves: RHEL-40156

* Thu May 30 2024 Derek Parker <deparker@redhat.com> - 1.22.3-3
- Update openssl backend
- Resolves: RHEL-36101

* Thu May 23 2024 Derek Parker <deparker@redhat.com> - 1.22.3-2
- Restore HashSign / HashVerify API
- Resolves: RHEL-35883

* Wed May 22 2024 Alejandro Sáez <asm@redhat.com> - 1.22.3-1
- Rebase to 1.22.3
- Removes re-enable-cgo.patch
- Resolves: RHEL-35634
- Resolves: RHEL-35883
- Resolves: RHEL-10068
- Resolves: RHEL-34924

* Thu Apr 18 2024 Derek Parker <deparker@redhat.com> - 1.22.2-1
- Rebase to 1.22.2
- Resolves: RHEL-28941

* Tue Apr 09 2024 Alejandro Sáez <asm@redhat.com> - 1.22.1-2
- Set the AMD64 baseline to v2

* Tue Mar 19 2024 Alejandro Sáez <asm@redhat.com> - 1.22.1-1
- Rebase to Go 1.22.1
- Re-enable CGO
- Resolves: RHEL-29527
- Resolves: RHEL-28175

* Fri Feb 09 2024 Alejandro Sáez <asm@redhat.com> - 1.21.7-1
- Rebase to Go 1.21.7
- Set GOTOOLCHAIN to local
- Resolves: RHEL-24334
- Resolves: RHEL-18364
- Resolves: RHEL-18365

* Thu Nov 30 2023 Alejandro Sáez <asm@redhat.com> - 1.21.4-2
- Add release information

* Tue Nov 14 2023 Alejandro Sáez <asm@redhat.com> - 1.21.4-1
- Rebase to Go 1.21.4
- Resolves: RHEL-11871

* Wed Nov 08 2023 David Benoit <dbenoit@redhat.com> - 1.21.3-5
- Don't change GOPROXY/GOSUMDB
- Related: RHEL-12624

* Thu Nov 02 2023 David Benoit <dbenoit@redhat.com> - 1.21.3-4
- Fix missing go.env in Go 1.21
- Related: RHEL-12624

* Tue Oct 31 2023 Archana Ravindar <aravinda@redhat.com> - 1.21.3-3
- Add missing strict fips runtime detection patch
- Temporarily disable FIPS tests on aarch64 due to builder kernel bugs
- Related: RHEL-12624

* Wed Oct 25 2023 Archana Ravindar <aravinda@redhat.com> - 1.21.3-2
- Rebase disable_static_tests_part2.patch to Go 1.21.3
- Related: RHEL-12624

* Fri Oct 20 2023 Archana Ravindar <aravinda@redhat.com> - 1.21.3-1
- Rebase to Go 1.21.3
- Resolves: RHEL-12624

* Wed Sep 27 2023 Alejandro Sáez <asm@redhat.com> - 1.20.8-1
- Rebase to Go 1.20.8
- Remove fix-memory-leak-evp-sign-verify.patch as it is already included in the source
- Resolves: RHEL-2775

* Mon Aug 14 2023 Alejandro Sáez <asm@redhat.com> - 1.20.6-5
- Retire golang-race package
- Resolves: rhbz#2230705

* Tue Jul 18 2023 Alejandro Sáez <asm@redhat.com> - 1.20.6-1
- Rebase to Go 1.20.6
- Change to autopatch
- Resolves: rhbz#2222313

* Fri Jun 23 2023 Alejandro Sáez <asm@redhat.com> - 1.20.4-3
- Increase the timeout in the tests
- Related: rhbz#2204477

* Fri Jun 09 2023 Carl George <carl@redhat.com> - 1.20.4-2
- Add go-toolset subpackage to ensure golang and go-toolset are published together
- Resolves: rhbz#2117248

* Mon May 29 2023 Alejandro Sáez <asm@redhat.com> - 1.20.4-1
- Rebase to Go 1.20.4
- Resolves: rhbz#2204477

* Tue Apr 11 2023 David Benoit <dbenoit@redhat.com> - 1.20.3-1
- Rebase to Go 1.20.3
- Remove race archives
- Update static test patches
- Resolves: rhbz#2185259

* Wed Mar 01 2023 David Benoit <dbenoit@redhat.com> - 1.19.6-1
- Rebase to Go 1.19.6
- Resolves: rhbz#2174429
- Fix memory leak
- Resolves: rhbz#2157602
- Enable tests in check phase

* Wed Dec 21 2022 David Benoit <dbenoit@redhat.com> - 1.19.4-1
- Rebase to Go 1.19.4
- Fix ppc64le linker issue
- Remove defunct patches
- Remove downstream generated FIPS mode patches
- Add golang-fips/go as the source for FIPS mode patches
- Resolves: rhbz#2144539

* Wed Nov 30 2022 David Benoit <dbenoit@redhat.com> - 1.19.2-2
- Fix endian issue in FIPS mode
- Resolves: rhbz#1966992

* Fri Oct 21 2022 David Benoit <dbenoit@redhat.com> - 1.19.2-1
- Update go to version 1.19.2
- Resolves: rhbz#2134407

* Wed Sep 14 2022 David Benoit <dbenoit@redhat.com> - 1.19.1-2
- Rebase to Go 1.19.1
- Temporarily disable crypto tests
- Resolves: rhbz#2131028

* Wed Aug 10 2022 Alejandro Sáez <asm@redhat.com> - 1.18.4-2
- Update to Go 1.18.4
- Resolves: rhbz#2109180
- Deprecates keys smaller than 2048 bits in TestDecryptOAEP in boring mode

* Fri Aug 05 2022 Alejandro Sáez <asm@redhat.com> - 1.18.4-1
- Update to Go 1.18.4
- Resolves: rhbz#2109180

* Fri Jun 10 2022 David Benoit <dbenoit@redhat.com> - 1.18.2-2
- Update deprecated openssl algorithms patch
- Rebuild against openssl-3.0.1-33
- Resolves: rhbz#2092136
- Related: rhbz#2092016

* Mon May 02 2022 David Benoit <dbenoit@redhat.com> - 1.18.2-1
- Rebase to Go 1.18.2
- Move to github.com/golang-fips/go
- Resolves: rhbz#2075169
- Resolves: rhbz#2060769
- Resolves: rhbz#2067531
- Resolves: rhbz#2067536
- Resolves: rhbz#2067552
- Resolves: rhbz#2025637

* Mon Dec 13 2021 Alejandro Sáez <asm@redhat.com> - 1.17.5-1
- Rebase to Go 1.17.5
- Add remove_waitgroup_misuse_tests patch
- Add remove_ed25519vectors_test.patch
- Remove FIPS checks to avoid issues in the CI
- Related: rhbz#2031116
- Resolves: rhbz#2022829
- Resolves: rhbz#2024687
- Resolves: rhbz#2030851
- Resolves: rhbz#2031253

* Wed Nov 03 2021 Alejandro Sáez <asm@redhat.com> - 1.17.2-1
- Rebase to Go 1.17.2
- Related: rhbz#2014087
- Remove favicon.ico and robots.txt references
- Exclude TestEd25519Vectors test
- Update patch rhbz1952381
- Remove rhbz1904567 patch
- Remove rhbz1939923 patch

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.16.6-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Aug 4 2021 Derek Parker <deparker@redhat.com> - 1.16.6-3
- Include ppc64le VDSO segfault backport fix
- Resolves: rhbz#1966622

* Mon Aug 2 2021 Derek Parker <deparker@redhat.com> - 1.16.6-2
- Bump release
- Resolves: rhbz#1904567

* Mon Aug 2 2021 Derek Parker <deparker@redhat.com> - 1.16.6-2
- Backport fix allowing LTO to be enabled on cgo sources
- Resolves: rhbz#1904567

* Tue Jul 20 2021 Derek Parker <deparker@redhat.com> - 1.16.6-1
- Rebase to 1.16.6
- Resolves: rhbz#1984124
- Replace symbols no longer present in OpenSSL 3.0 ABI
- Resolves: rhbz#1984110
- Fix TestBoringServerCurves failing when ran by itself
- Resolves: rhbz#1977914

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 1.16.4-3
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Fri May 28 2021 David Benoit <dbenoit@redhat.com> - 1.16.4-2
- Port to OpenSSL 3.0
- Resolves: rhbz#1952381

* Fri May 14 2021 Alejandro Sáez <asm@redhat.com> - 1.16.4-1
- Rebase to 1.16.4
- Resolves: rhbz#1955035
- Resolves: rhbz#1957961

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 1.16.1-3
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Mar 30 2021 Alejandro Sáez <asm@redhat.com> - 1.16.1-2
- Rebase to go-1.16.1-2-openssl-fips
- Resolves: rhbz#1922455

* Tue Mar 30 2021 Alejandro Sáez <asm@redhat.com> - 1.16.1-1
- Rebase to go-1.16.1-2-openssl-fips
- Adds a workaround for rhbz#1939923
- Removes Patch224, it's on upstream -> rhbz#1888673
- Removes Patch225, it's on upstream -> https://go-review.googlesource.com/c/text/+/238238
- Removes old patches for cleaning purposes
- Related: rhbz#1942898

* Fri Jan 22 2021 David Benoit <dbenoit@redhat.com> - 1.15.7-1
- Rebase to 1.15.7
- Resolves: rhbz#1892207
- Resolves: rhbz#1918755

* Tue Nov 24 2020 David Benoit <dbenoit@redhat.com> - 1.15.5-1
- Rebase to 1.15.5
- Resolves: rhbz#1899184
- Resolves: rhbz#1899185
- Resolves: rhbz#1899186

* Thu Nov 12 2020 David Benoit <dbenoit@redhat.com> - 1.15.3-2
- Rebase to 1.15.3
- fix x/text infinite loop
- Resolves: rhbz#1881539

* Tue Nov 03 2020 Alejandro Sáez <asm@redhat.com> - 1.15.2-2
- Resolves: rhbz#1850045

* Mon Oct 19 2020 David Benoit <dbenoit@redhat.com> - 1.15.2-1
- Rebase to 1.15.2
- fix rhbz#1872622 in commit af9a1b1f6567a1c5273a134d395bfe7bb840b7f8
- Resolves: rhbz#1872622
- add net/http graceful shutdown patch
- Resolves: rhbz#1888673
- add x509warnCN patch
- Resolves: rhbz#1889437

* Wed Sep 09 2020 Alejandro Sáez <asm@redhat.com> - 1.15.0-1
- Rebase to 1.15.0
- Related: rhbz#1870531

* Thu Aug 27 2020 Alejandro Sáez <asm@redhat.com> - 1.14.7-2
- Improve test suite
- Resolves: rhbz#1854693

* Tue Aug 18 2020 Alejandro Sáez <asm@redhat.com> - 1.14.7-1
- Rebase to 1.14.7

* Mon Aug 03 2020 Alejandro Sáez <asm@redhat.com> - 1.14.6-1
- Rebase to 1.14.6
- Resolves: rhbz#1820596

* Wed Jul 08 2020 Alejandro Sáez <asm@redhat.com> - 1.14.4-2
- Include patch to fix missing deferreturn on linux/ppc64le
- Resolves: rhbz#1854836

* Thu Jun 25 2020 Alejandro Sáez <asm@redhat.com> - 1.14.4-1
- Rebase to 1.14.4

* Thu May 21 2020 Alejandro Sáez <asm@redhat.com> - 1.14.2-2
- Remove i686 references
- Related: rhbz#1752991

* Wed May 06 2020 Alejandro Sáez <asm@redhat.com> - 1.14.2-1
- Rebase to 1.14.2
- Related: rhbz#1820596

* Wed Nov 27 2019 Alejandro Sáez <asm@redhat.com> - 1.13.4-2
- Remove patches
- Related: rhbz#1747150

* Mon Nov 25 2019 Alejandro Sáez <asm@redhat.com> - 1.13.4-1
- Rebase to 1.13.4
- Related: rhbz#1747150

* Tue Sep 17 2019 Tom Stellard <tstellar@redhat.com> - 1.12.8-4
- Reduce number of threads when testing on i686

* Wed Sep 11 2019 Tom Stellard <tstellar@redhat.com> - 1.12.8-3
- Relax FIPS requirements to unblock OpenShift testing

* Wed Aug 28 2019 Tom Stellard <tstellar@redhat.com> - 1.12.8-2
- Rebase to 1.12.8
- Resolves: rhbz#1745706
- Resolves: rhbz#1745712

* Mon Aug 5 2019 Derek Parker <deparker@redhat.com> - 1.12.6-3
- Add README for more documentation
- Resolves: rhbz#1734788

* Fri Aug 2 2019 Derek Parker <deparker@redhat.com> - 1.12.6-3
- Revert some TLS FIPS changes for now
- Resolves: rhbz#1734788

* Thu Aug 1 2019 Derek Parker <deparker@redhat.com> - 1.12.6-2
- Updates to be less strict on key size in FIPS mode
- Resolves: rhbz#1734788

* Thu Jun 13 2019 Derek Parker <deparker@redhat.com> - 1.12.6-1
- Rebase to 1.12.6
- Resolves: rhbz#1677819

* Thu Jun 13 2019 Derek Parker <deparker@redhat.com> - 1.12.5-2
- Remove macros present in go-compiler
- Resolves: rhbz#1700109

* Wed Jun 12 2019 Derek Parker <deparker@redhat.com> - 1.12.5-1
- Rebase to 1.12.5
- Resolves: rhbz#1677819

* Wed May 29 2019 Derek Parker <deparker@redhat.com> - 1.12.1-2
- Lock OpenSSL to specific built version and include more initialization.
- Resolves: rhbz#1709603

* Fri May 10 2019 Derek Parker <deparker@redhat.com> - 1.12.1-1
- Rebase to 1.12.1
- Include FIPS compliance updates
- Resolves: rhbz#1709603

* Thu Apr 4 2019 Derek Parker <deparker@redhat.com> - 1.11.5-2
- Include patch to fix CVE-2019-9741
- Resolves: rhbz#1690443

* Mon Feb 18 2019 Derek Parker <deparker@redhat.com> - 1.11.5-2
- Switch to pagure fork for Go FIPS

* Thu Feb 7 2019 Derek Parker <deparker@redhat.com> - 1.11.5-1
- Rebase to Go 1.11.5
- Resolves: rhbz#1671277
- Fixes CVE-2019-6486

* Thu Jan 3 2019 Derek Parker <deparker@redhat.com> - 1.11.4-1
- Rebase to Go 1.11.4
- Fixes CVE-2018-16873, CVE-2018-16874, CVE-2018-16875

* Thu Dec 6 2018 Derek Parker <deparker@redhat.com> - 1.11.2-1
- Rebase to Go 1.11.2

* Fri Nov 16 2018 Derek Parker <deparker@redhat.com> - 1.10.3-18
- Remove SCL from macros

* Wed Nov 7 2018 Derek Parker <deparker@redhat.com> - 1.10.3-17
- Prefer go-toolset over go-toolset-1.10
- Resolves: rhbz#1630786

* Mon Nov 5 2018 Derek Parker <deparker@redhat.com> - 1.10.3-16
- Fix implicit syscall declaration warning

* Mon Nov 5 2018 Derek Parker <deparker@redhat.com> - 1.10.3-15
- Remove usage of redhat hardening flag file, just pass a select few manually
- Resolves: rhbz#1642798

* Wed Oct 31 2018 Derek Parker <deparker@redhat.com> - 1.10.3-14
- Do not build toolchain in PIE mode
- Resolves: rhbz#1642798

* Fri Oct 26 2018 Derek Parker <deparker@redhat.com> - 1.10.3-13
- Fix setting of internal FIPS enabled flag
- Resolves: rhbz#1643653

* Wed Oct 10 2018 Derek Parker <deparker@redhat.com> - 1.10.3-12
- Pass external linker flags to fix annocheck errors
- Resolves: rhbz#1624421

* Wed Oct 10 2018 Derek Parker <deparker@redhat.com> - 1.10.3-11
- Fix UnreachableExceptTests false panic
- Resolves: rhbz#1634748

* Fri Oct 5 2018 Derek Parker <deparker@redhat.com> - 1.10.3-10
- Remove SCL, fix bug in boringcrypto with ecdsa
- Related: rhbz#1635066
- Resolves: rhbz#1636221

* Wed Sep 26 2018 Derek Parker <deparker@redhat.com> - 1.10.3-9
- Add runtime FIPS detection patches
- Resolves: rhbz#1633351

* Fri Sep 21 2018 Derek Parker <deparker@redhat.com> - 1.10.3-8
- Add `gobuild` and `gotest` macros from go-compilers
- Resolves: rhbz#1631846

* Thu Sep 20 2018 Derek Parker <deparker@redhat.com> - 1.10.3-7
- Bootstrap package using old build of same package
- Resolves: rhbz#1630786

* Mon Aug 13 2018 Derek Parker <deparker@redhat.com> - 1.10.3-6
- Update stack allocation of OpenSSL type patch
- Resolves: rhbz#1615032

* Sat Aug 11 2018 Troy Dawson <tdawson@redhat.com> - 1.10.3-5
- Build on i686
- Related: bug#1614611

* Tue Aug 7 2018 Derek Parker <deparker@redhat.com> - 1.10.3-4
- Add patch fixing stack allocation of opaque OpenSSL type bug.
- Resolves: rhbz#1613538

* Thu Aug 2 2018 Derek Parker <deparker@redhat.com> - 1.10.3-3
- Add patch with tag to opt out of OpenSSL during build

* Wed Jul 25 2018 Derek Parker <deparker@redhat.com> - 1.10.3-2
- Add runtime requirement for openssl-devel and misc updates

* Tue Jul 24 2018 Derek Parker <deparker@redhat.com> - 1.10.3-1
- Bump to 1.10.3

* Tue Jul 24 2018 Derek Parker <deparker@redhat.com> - 1.10.2-3
- Prepare for module build

* Wed Jun 27 2018 Derek Parker <deparker@redhat.com> - 1.10.2-2
- Include FIPS patches

* Wed May 23 2018 Derek Parker <deparker@redhat.com> - 1.10.2-1
- Bump to Go 1.10.2

* Thu Mar 15 2018 Derek Parker <deparker@redhat.com> - 1.10-1
- Bump to Go 1.10

* Wed Oct 18 2017 Jakub Čajka <jcajka@redhat.com> - 1.8.5-1
- Fix CVE-2017-15041 and CVE-2017-15042
- Resolves: BZ#1499160, BZ#1498073, BZ#1512063

* Thu Aug 31 2017 Tom Stellard <tstellar@redhat.com> - 1.8.3-4
- Explicitly require /usr/bin/gcc
- Resolves: #1487345

* Thu Jun 22 2017 Jakub Čajka <jcajka@redhat.com> - 1.8.3-3
- apply asn1 patch
- add ppc64le trampolines patch

* Wed Jun 14 2017 Jakub Čajka <jcajka@redhat.com> - 1.8.3-2
- regular GTS build

* Tue Jun 06 2017 Jakub Čajka <jcajka@redhat.com> - 1.8.3-1
- initial GTS build

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8-0.rc3.2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Jakub Čajka <jcajka@redhat.com> - 1.8-0.rc3.2
- make possible to override default traceback level at build time
- add sub-package race containing std lib built with -race enabled
- Related: BZ#1411242

* Fri Jan 27 2017 Jakub Čajka <jcajka@redhat.com> - 1.8-0.rc3.1
- rebase to go1.8rc3
- Resolves: BZ#1411242

* Fri Jan 20 2017 Jakub Čajka <jcajka@redhat.com> - 1.7.4-2
- Resolves: BZ#1404679
- expose IfInfomsg.X__ifi_pad on s390x

* Fri Dec 02 2016 Jakub Čajka <jcajka@redhat.com> - 1.7.4-1
- Bump to 1.7.4
- Resolves: BZ#1400732

* Thu Nov 17 2016 Tom Callaway <spot@fedoraproject.org> - 1.7.3-2
- re-enable the NIST P-224 curve

* Thu Oct 20 2016 Jakub Čajka <jcajka@redhat.com> - 1.7.3-1
- Resolves: BZ#1387067 - golang-1.7.3 is available
- added fix for tests failing with latest tzdata

* Fri Sep 23 2016 Jakub Čajka <jcajka@redhat.com> - 1.7.1-2
- fix link failure due to relocation overflows on PPC64X

* Thu Sep 08 2016 Jakub Čajka <jcajka@redhat.com> - 1.7.1-1
- rebase to 1.7.1
- Resolves: BZ#1374103

* Tue Aug 23 2016 Jakub Čajka <jcajka@redhat.com> - 1.7-1
- update to released version
- related: BZ#1342090, BZ#1357394

* Mon Aug 08 2016 Jakub Čajka <jcajka@redhat.com> - 1.7-0.3.rc5
- Obsolete golang-vet and golang-cover from golang-googlecode-tools package
  vet/cover binaries are provided by golang-bin rpm (thanks to jchaloup)
- clean up exclusive arch after s390x boostrap
- resolves: #1268206

* Wed Aug 03 2016 Jakub Čajka <jcajka@redhat.com> - 1.7-0.2.rc5
- rebase to go1.7rc5
- Resolves: BZ#1342090

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7-0.1.rc2
- https://fedoraproject.org/wiki/Changes/golang1.7

* Tue Jul 19 2016 Jakub Čajka <jcajka@redhat.com> - 1.7-0.0.rc2
- rebase to 1.7rc2
- added s390x build
- improved shared lib packaging
- Resolves: bz1357602 - CVE-2016-5386
- Resolves: bz1342090, bz1342090

* Tue Apr 26 2016 Jakub Čajka <jcajka@redhat.com> - 1.6.2-1
- rebase to 1.6.2
- Resolves: bz1329206 - golang-1.6.2.src is available

* Wed Apr 13 2016 Jakub Čajka <jcajka@redhat.com> - 1.6.1-1
- rebase to 1.6.1
- Resolves: bz1324344 - CVE-2016-3959
- Resolves: bz1324951 - prelink is gone, /etc/prelink.conf.d/* is no longer used
- Resolves: bz1326366 - wrong epoll_event struct for ppc64le/ppc64

* Mon Feb 22 2016 Jakub Čajka <jcajka@redhat.com> - 1.6-1
- Resolves: bz1304701 - rebase to go1.6 release
- Resolves: bz1304591 - fix possible stack miss-alignment in callCgoMmap

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.6-0.3.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 29 2016 Jakub Čajka <jcajka@redhat.com> - 1.6-0.2.rc1
- disabled cgo and external linking on ppc64

* Thu Jan 28 2016 Jakub Čajka <jcajka@redhat.com> - 1.6-0.1.rc1
- Resolves bz1292640, rebase to pre-release 1.6
- bootstrap for PowerPC
- fix rpmlint errors/warning

* Thu Jan 14 2016 Jakub Čajka <jcajka@redhat.com> - 1.5.3-1
- rebase to 1.5.3
- resolves bz1293451, CVE-2015-8618
- apply timezone patch, avoid using bundled data
- print out rpm build system info

* Fri Dec 11 2015 Jakub Čajka <jcajka@redhat.com> - 1.5.2-2
- bz1290543 Accept x509 certs with negative serial

* Tue Dec 08 2015 Jakub Čajka <jcajka@redhat.com> - 1.5.2-1
- bz1288263 rebase to 1.5.2
- spec file clean up
- added build options
- scrubbed "Project Gutenberg License"

* Mon Oct 19 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5.1-1
- bz1271709 include patch from upstream fix

* Wed Sep 09 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5.1-0
- update to go1.5.1

* Fri Sep 04 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-8
- bz1258166 remove srpm macros, for go-srpm-macros

* Thu Sep 03 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-7
- bz1258166 remove srpm macros, for go-srpm-macros

* Thu Aug 27 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-6
- starting a shared object subpackage. This will be x86_64 only until upstream supports more arches shared objects.

* Thu Aug 27 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-5
- bz991759 gdb path fix

* Wed Aug 26 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-4
- disable shared object until linux/386 is ironned out
- including the test/ directory for tests

* Tue Aug 25 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-3
- bz1256910 only allow the golang zoneinfo.zip to be used in tests
- bz1166611 add golang.org/x directory
- bz1256525 include stdlib shared object. This will let other libraries and binaries
  build with `go build -buildmode=shared -linkshared ...` or similar.

* Sun Aug 23 2015 Peter Robinson <pbrobinson@fedoraproject.org> 1.5-2
- Enable aarch64
- Minor cleanups

* Thu Aug 20 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-1
- updating to go1.5

* Thu Aug 06 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-0.11.rc1
- fixing the sources reference

* Thu Aug 06 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-0.10.rc1
- updating to go1.5rc1
- checks are back in place

* Tue Aug 04 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-0.9.beta3
- pull in upstream archive/tar fix

* Thu Jul 30 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-0.8.beta3
- updating to go1.5beta3

* Thu Jul 30 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-0.7.beta2
- add the patch ..

* Thu Jul 30 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-0.6.beta2
- increase ELFRESERVE (bz1248071)

* Tue Jul 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5-0.5.beta2
- correct package version and release tags as per naming guidelines

* Fri Jul 17 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.99-4.1.5beta2
- adding test output, for visibility

* Fri Jul 10 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.99-3.1.5beta2
- updating to go1.5beta2

* Fri Jul 10 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.99-2.1.5beta1
- add checksum to sources and fixed one patch

* Fri Jul 10 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.99-1.1.5beta1
- updating to go1.5beta1

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Mar 18 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.2-2
- obsoleting deprecated packages

* Wed Feb 18 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.2-1
- updating to go1.4.2

* Fri Jan 16 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.1-1
- updating to go1.4.1

* Fri Jan 02 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4-2
- doc organizing

* Thu Dec 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.4-1
- update to go1.4 release

* Wed Dec 03 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.99-3.1.4rc2
- update to go1.4rc2

* Mon Nov 17 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.99-2.1.4rc1
- update to go1.4rc1

* Thu Oct 30 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.99-1.1.4beta1
- update to go1.4beta1

* Thu Oct 30 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.3-3
- macros will need to be in their own rpm

* Fri Oct 24 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.3-2
- split out rpm macros (bz1156129)
- progress on gccgo accomodation

* Wed Oct 01 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.3-1
- update to go1.3.3 (bz1146882)

* Mon Sep 29 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.2-1
- update to go1.3.2 (bz1147324)

* Thu Sep 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.1-3
- patching the tzinfo failure

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.1-1
- update to go1.3.1

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-11
- merged a line wrong

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-10
- more work to get cgo.a timestamps to line up, due to build-env
- explicitly list all the files and directories for the source and packages trees
- touch all the built archives to be the same

* Mon Aug 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-9
- make golang-src 'noarch' again, since that was not a fix, and takes up more space

* Mon Aug 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-8
- update timestamps of source files during %%install bz1099206

* Fri Aug 08 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-7
- update timestamps of source during %%install bz1099206

* Wed Aug 06 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-6
- make the source subpackage arch'ed, instead of noarch

* Mon Jul 21 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-5
- fix the writing of pax headers

* Tue Jul 15 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-4
- fix the loading of gdb safe-path. bz981356

* Tue Jul 08 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-3
- `go install std` requires gcc, to build cgo. bz1105901, bz1101508

* Mon Jul 07 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-2
- archive/tar memory allocation improvements

* Thu Jun 19 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-1
- update to go1.3

* Fri Jun 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3rc2-1
- update to go1.3rc2

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3rc1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun 03 2014 Vincent Batts <vbatts@redhat.com> 1.3rc1-1
- update to go1.3rc1
- new arch file shuffling

* Wed May 21 2014 Vincent Batts <vbatts@redhat.com> 1.3beta2-1
- update to go1.3beta2
- no longer provides go-mode for xemacs (emacs only)

* Wed May 21 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-7
- bz1099206 ghost files are not what is needed

* Tue May 20 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-6
- bz1099206 more fixing. The packages %%post need golang-bin present first

* Tue May 20 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-5
- bz1099206 more fixing. Let go fix its own timestamps and freshness

* Tue May 20 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-4
- fix the existence and alternatives of `go` and `gofmt`

* Mon May 19 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-3
- bz1099206 fix timestamp issue caused by koji builders

* Fri May 09 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-2
- more arch file shuffling

* Fri May 09 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-1
- update to go1.2.2

* Thu May 08 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-8
- RHEL6 rpm macros can't %%exlude missing files

* Wed May 07 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-7
- missed two arch-dependent src files

* Wed May 07 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-6
- put generated arch-dependent src in their respective RPMs

* Fri Apr 11 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-5
- skip test that is causing a SIGABRT on fc21 bz1086900

* Thu Apr 10 2014 Vincent Batts <vbatts@fedoraproject.org> 1.2.1-4
- fixing file and directory ownership bz1010713

* Wed Apr 09 2014 Vincent Batts <vbatts@fedoraproject.org> 1.2.1-3
- including more to macros (%%go_arches)
- set a standard goroot as /usr/lib/golang, regardless of arch
- include sub-packages for compiler toolchains, for all golang supported architectures

* Wed Mar 26 2014 Vincent Batts <vbatts@fedoraproject.org> 1.2.1-2
- provide a system rpm macros. Starting with gopath

* Tue Mar 04 2014 Adam Miller <maxamillion@fedoraproject.org> 1.2.1-1
- Update to latest upstream

* Thu Feb 20 2014 Adam Miller <maxamillion@fedoraproject.org> 1.2-7
- Remove  _BSD_SOURCE and _SVID_SOURCE, they are deprecated in recent
  versions of glibc and aren't needed

* Wed Feb 19 2014 Adam Miller <maxamillion@fedoraproject.org> 1.2-6
- pull in upstream archive/tar implementation that supports xattr for
  docker 0.8.1

* Tue Feb 18 2014 Vincent Batts <vbatts@redhat.com> 1.2-5
- provide 'go', so users can yum install 'go'

* Fri Jan 24 2014 Vincent Batts <vbatts@redhat.com> 1.2-4
- skip a flaky test that is sporadically failing on the build server

* Thu Jan 16 2014 Vincent Batts <vbatts@redhat.com> 1.2-3
- remove golang-godoc dependency. cyclic dependency on compiling godoc

* Wed Dec 18 2013 Vincent Batts <vbatts@redhat.com> - 1.2-2
- removing P224 ECC curve

* Mon Dec 2 2013 Vincent Batts <vbatts@fedoraproject.org> - 1.2-1
- Update to upstream 1.2 release
- remove the pax tar patches

* Tue Nov 26 2013 Vincent Batts <vbatts@redhat.com> - 1.1.2-8
- fix the rpmspec conditional for rhel and fedora

* Thu Nov 21 2013 Vincent Batts <vbatts@redhat.com> - 1.1.2-7
- patch tests for testing on rawhide
- let the same spec work for rhel and fedora

* Wed Nov 20 2013 Vincent Batts <vbatts@redhat.com> - 1.1.2-6
- don't symlink /usr/bin out to ../lib..., move the file
- seperate out godoc, to accomodate the go.tools godoc

* Fri Sep 20 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-5
- Pull upstream patches for BZ#1010271
- Add glibc requirement that got dropped because of meta dep fix

* Fri Aug 30 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-4
- fix the libc meta dependency (thanks to vbatts [at] redhat.com for the fix)

* Tue Aug 27 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-3
- Revert incorrect merged changelog

* Tue Aug 27 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-2
- This was reverted, just a placeholder changelog entry for bad merge

* Tue Aug 20 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-1
- Update to latest upstream

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1.1.1-6
- Perl 5.18 rebuild

* Wed Jul 10 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-5
- Blacklist testdata files from prelink
- Again try to fix #973842

* Fri Jul  5 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-4
- Move src to libdir for now (#973842) (upstream issue https://code.google.com/p/go/issues/detail?id=5830)
- Eliminate noarch data package to work around RPM bug (#975909)
- Try to add runtime-gdb.py to the gdb safe-path (#981356)

* Wed Jun 19 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-3
- Use lua for pretrans (http://fedoraproject.org/wiki/Packaging:Guidelines#The_.25pretrans_scriptlet)

* Mon Jun 17 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-2
- Hopefully really fix #973842
- Fix update from pre-1.1.1 (#974840)

* Thu Jun 13 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-1
- Update to 1.1.1
- Fix basically useless package (#973842)

* Sat May 25 2013 Dan Horák <dan[at]danny.cz> - 1.1-3
- set ExclusiveArch

* Fri May 24 2013 Adam Goode <adam@spicenitz.org> - 1.1-2
- Fix noarch package discrepancies

* Fri May 24 2013 Adam Goode <adam@spicenitz.org> - 1.1-1
- Initial Fedora release.
- Update to 1.1

* Thu May  9 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.3.rc3
- Update to rc3

* Thu Apr 11 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.2.beta2
- Update to beta2

* Tue Apr  9 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.1.beta1
- Initial packaging.
