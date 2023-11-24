%global toolchain gcc

%global maj_ver 16
%global libomp_version %{maj_ver}.0.6
%global libomp_srcdir openmp-%{libomp_version}%{?rc_ver:rc%{rc_ver}}.src
%global cmake_srcdir cmake-%{libomp_version}%{?rc_ver:rc%{rc_ver}}.src


%ifarch ppc64le
%global libomp_arch ppc64
%else
%global libomp_arch %{_arch}
%endif

Name: libomp
Version: %{libomp_version}
Release: 1%{?dist}
Summary: OpenMP runtime for clang

License: NCSA
URL: http://openmp.llvm.org
Source0: https://github.com/llvm/llvm-project/releases/download/llvmorg-%{libomp_version}/%{libomp_srcdir}.tar.xz
Source1: https://github.com/llvm/llvm-project/releases/download/llvmorg-%{libomp_version}/%{libomp_srcdir}.tar.xz.sig
Source2: release-keys.asc
Source3: run-lit-tests
Source4: lit.fedora.cfg.py
Source5:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{libomp_version}%{?rc_ver:-rc%{rc_ver}}/%{cmake_srcdir}.tar.xz
Source6:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{libomp_version}%{?rc_ver:-rc%{rc_ver}}/%{cmake_srcdir}.tar.xz.sig

BuildRequires: clang
# For clang-offload-packager
BuildRequires: clang-tools-extra
BuildRequires: cmake
BuildRequires: ninja-build
BuildRequires: elfutils-libelf-devel
BuildRequires: perl
BuildRequires: perl-Data-Dumper
BuildRequires: perl-Encode
BuildRequires: libffi-devel

# For gpg source verification
BuildRequires:	gnupg2

# libomptarget needs the llvm cmake files
BuildRequires: llvm-devel

Requires: elfutils-libelf%{?isa}

# libomp does not support s390x.
ExcludeArch: s390x

%description
OpenMP runtime for clang.

%package devel
Summary: OpenMP header files
Requires: %{name}%{?isa} = %{version}-%{release}
Requires: clang-resource-filesystem%{?isa} = %{version}

%description devel
OpenMP header files.

%package test
Summary: OpenMP regression tests
Requires: %{name}%{?isa} = %{version}-%{release}
Requires: %{name}-devel%{?isa} = %{version}-%{release}
Requires: clang
Requires: llvm
Requires: python3-lit

%description test
OpenMP regression tests

%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE6}' --data='%{SOURCE5}'
%setup -T -q -b 5 -n %{cmake_srcdir}
# TODO: It would be more elegant to set -DLLVM_COMMON_CMAKE_UTILS=%{_builddir}/%{cmake_srcdir},
# but this is not a CACHED variable, so we can't actually set it externally :(
cd ..
mv %{cmake_srcdir} cmake
%autosetup -n %{libomp_srcdir} -p2

%build

%if "%toolchain" == "gcc"
# Building openmp with LTO fails with GCC but works with Clang
%define _lto_cflags %{nil}
%endif

%cmake	-GNinja \
	-DLIBOMP_INSTALL_ALIASES=OFF \
	-DCMAKE_MODULE_PATH=%{_libdir}/cmake/llvm \
	-DLLVM_DIR=%{_libdir}/cmake/llvm \
	-DCMAKE_INSTALL_INCLUDEDIR=%{_libdir}/clang/%{maj_ver}/include \
%if 0%{?__isa_bits} == 64
	-DOPENMP_LIBDIR_SUFFIX=64 \
%else
	-DOPENMP_LIBDIR_SUFFIX= \
%endif
	-DCMAKE_SKIP_RPATH:BOOL=ON

%cmake_build


%install
%cmake_install

# Test package setup
%global libomp_srcdir %{_datadir}/libomp/src/
%global libomp_testdir %{libomp_srcdir}/runtime/test/
%global lit_cfg %{libomp_testdir}/%{_arch}.site.cfg.py
%global lit_fedora_cfg %{_datadir}/libomp/lit.fedora.cfg.py

install -d %{buildroot}%{libomp_srcdir}/runtime
cp -R runtime/test  %{buildroot}%{libomp_srcdir}/runtime
cp -R runtime/src  %{buildroot}%{libomp_srcdir}/runtime

# Generate lit config files.  Strip off the last line that initiates the
# test run, so we can customize the configuration.
head -n -1 %{_vpath_builddir}/runtime/test/lit.site.cfg >> %{buildroot}%{lit_cfg}

# Install custom fedora config file
cp %{SOURCE4} %{buildroot}%{lit_fedora_cfg}

# Patch lit config files to load custom fedora config
echo "lit_config.load_config(config, '%{lit_fedora_cfg}')" >> %{buildroot}%{lit_cfg}

# Install test script
install -d %{buildroot}%{_libexecdir}/tests/libomp
install -m 0755 %{SOURCE3} %{buildroot}%{_libexecdir}/tests/libomp

# Remove static libraries with equivalent shared libraries
rm -rf %{buildroot}%{_libdir}/libarcher_static.a

%check
%cmake_build --target check-openmp

%files
%license LICENSE.TXT
%{_libdir}/libomp.so
%{_libdir}/libompd.so
%ifnarch %{arm}
%{_libdir}/libarcher.so
%endif
%ifnarch %{ix86} %{arm}
%{_libdir}/libomptarget.rtl.amdgpu.so.%{maj_ver}
%{_libdir}/libomptarget.rtl.amdgpu.nextgen.so.%{maj_ver}
%{_libdir}/libomptarget.rtl.cuda.so.%{maj_ver}
%{_libdir}/libomptarget.rtl.cuda.nextgen.so.%{maj_ver}
%{_libdir}/libomptarget.rtl.%{libomp_arch}.so.%{maj_ver}
%{_libdir}/libomptarget.rtl.%{libomp_arch}.nextgen.so.%{maj_ver}
%{_libdir}/libomptarget.so.%{maj_ver}
%endif

%files devel
%{_libdir}/clang/%{maj_ver}/include/omp.h
%{_libdir}/cmake/openmp/FindOpenMPTarget.cmake
%ifnarch %{arm}
%{_libdir}/clang/%{maj_ver}/include/omp-tools.h
%{_libdir}/clang/%{maj_ver}/include/ompt.h
%{_libdir}/clang/%{maj_ver}/include/ompt-multiplex.h
%endif
%ifnarch %{ix86} %{arm}
%{_libdir}/libomptarget.rtl.amdgpu.so
%{_libdir}/libomptarget.rtl.amdgpu.nextgen.so
%{_libdir}/libomptarget.rtl.cuda.so
%{_libdir}/libomptarget.rtl.cuda.nextgen.so
%{_libdir}/libomptarget.rtl.%{libomp_arch}.so
%{_libdir}/libomptarget.rtl.%{libomp_arch}.nextgen.so
%{_libdir}/libomptarget.devicertl.a
%{_libdir}/libomptarget-amdgpu-*.bc
%{_libdir}/libomptarget-nvptx-*.bc
%{_libdir}/libomptarget.so
%endif

%files test
%{_datadir}/libomp
%{_libexecdir}/tests/libomp/

%changelog
* Wed Jul 05 2023 Nikita Popov <npopov@redhat.com> - 16.0.6-1
- Update to LLVM 16.0.6

* Wed Apr 19 2023 Nikita Popov <npopov@redhat.com> - 16.0.1-1
- Update to LLVM 16.0.1

* Mon Jan 16 2023 Konrad Kleine <kkleine@redhat.com> - 15.0.7-1
- Update to LLVM 15.0.7

* Fri Dec 09 2022 Konrad Kleine <kkleine@redhat.com> - 15.0.6-1
- 15.0.6 Release

* Fri Oct 28 2022 Konrad Kleine <kkleine@redhat.com> - 15.0.1-2
- Build libomp runtime library with gcc

* Thu Sep 29 2022 Konrad Kleine <kkleine@redhat.com> - 15.0.1-1
- 15.0.1 Release

* Wed Jul 20 2022 Timm Bäder <tbaeder@redhat.com> - 14.0.6-1
- 14.0.6 Release

* Tue Jun 21 2022 Timm Bäder <tbaeder@redhat.com> - 14.0.5-1
- 14.0.5 Release

* Mon Apr 25 2022 Timm Bäder <tbaeder@redhat.com> - 14.0.0-1
- 14.0.0 Release

* Thu Feb 03 2022 Tom Stellard <tstellar@redhat.com> - 13.0.1-1
- 13.0.1 Release

* Tue Oct 12 2021 Timm Bäder <tbaeder@redhat.com> 13.0.0-1
- Release 13.0.0

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 12.0.1-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jul 13 2021 Tom Stellard <tstellar@redhat.com> - 12.0.1-1
- 12.0.1 Release

* Fri Apr 16 2021 Tom Stellard <tstellar@redhat.com> - 12.0.0-1
- 12.0.0 Release

* Thu Apr 08 2021 sguelton@redhat.com - 12.0.0-0.7.rc5
- New upstream release candidate

* Fri Apr 02 2021 sguelton@redhat.com - 12.0.0-0.6.rc4
- New upstream release candidate

* Wed Mar 31 2021 Jonathan Wakely <jwakely@redhat.com> - 12.0.0-0.5.rc3
- Rebuilt for removed libstdc++ symbols (#1937698)

* Thu Mar 11 2021 sguelton@redhat.com - 12.0.0-0.4.rc3
- LLVM 12.0.0 rc3

* Tue Mar 09 2021 sguelton@redhat.com - 12.0.0-0.3.rc2
- rebuilt

* Wed Feb 24 2021 sguelton@redhat.com - 12.0.0-0.2.rc2
- 12.0.0-rc2 release

* Mon Feb 22 2021 sguelton@redhat.com - 12.0.0-0.1.rc1
- 12.0.0-rc1 release

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 11.1.0-0.3.rc2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 22 2021 Serge Guelton - 11.1.0-0.2.rc2
- llvm 11.1.0-rc2 release

* Thu Jan 14 2021 Serge Guelton - 11.1.0-0.1.rc1
- 11.1.0-rc1 release

* Wed Jan 06 2021 Serge Guelton - 11.0.1-3
- LLVM 11.0.1 final

* Tue Dec 22 2020 sguelton@redhat.com - 11.0.1-2.rc2
- llvm 11.0.1-rc2

* Tue Dec 01 2020 sguelton@redhat.com - 11.0.1-1.rc1
- llvm 11.0.1-rc1

* Wed Oct 28 2020 Tom Stellard <tstellar@redhat.com> - 11.0.0-2
- Replace clang-devel dependency with clang-resource-filesystem

* Thu Oct 15 2020 sguelton@redhat.com - 11.0.0-1
- Fix NVR

* Mon Oct 12 2020 sguelton@redhat.com - 11.0.0-0.5
- llvm 11.0.0 - final release

* Thu Oct 08 2020 sguelton@redhat.com - 11.0.0-0.4.rc6
- 11.0.0-rc6

* Fri Oct 02 2020 sguelton@redhat.com - 11.0.0-0.3.rc5
- 11.0.0-rc5 Release

* Sun Sep 27 2020 sguelton@redhat.com - 11.0.0-0.2.rc3
- Fix NVR

* Thu Sep 24 2020 sguelton@redhat.com - 11.0.0-0.1.rc3
- 11.0.0-rc3 Release

* Tue Sep 01 2020 sguelton@redhat.com - 11.0.0-0.1.rc2
- 11.0.0-rc2 Release

* Mon Aug 10 2020 Tom Stellard <tstellar@redhat.com> - 11.0.0-0.1.rc1
- 11.0.0-rc1 Release

* Mon Aug 10 2020 sguelton@redhat.com - 10.0.0-8
- Make gcc dependency explicit, see https://fedoraproject.org/wiki/Packaging:C_and_C%2B%2B#BuildRequires_and_Requires
- use %%license macro

* Sat Aug 08 2020 Jeff Law <releng@fedoraproject.org> - 10.0.0-7
- Disable LTO for now

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 10.0.0-6
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 10.0.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 20 2020 sguelton@redhat.com - 10.0.0-4
- Use modern cmake macro
- Use gnupg verify

* Tue Jun 16 2020 sguelton@redhat.com - 10.0.0-3
- Add Requires: libomp = %%{version}-%%{release} to libomp-test to avoid
  the need to test interoperability between the various combinations of old
  and new subpackages.

* Mon Jun 01 2020 sguelton@redhat.com - 10.0.0-2
- Add Requires: libomp-devel = %%{version}-%%{release} to libomp-test to avoid
  the need to test interoperability between the various combinations of old
  and new subpackages.

* Mon Mar 30 2020 sguelton@redhat.com - 10.0.0-1
- 10.0.0 final

* Wed Mar 25 2020 sguelton@redhat.com - 10.0.0-0.6.rc6
- 10.0.0 rc6

* Fri Mar 20 2020 sguelton@redhat.com - 10.0.0-0.5.rc5
- 10.0.0 rc5

* Sun Mar 15 2020 sguelton@redhat.com - 10.0.0-0.4.rc4
- 10.0.0 rc4

* Thu Mar 05 2020 sguelton@redhat.com - 10.0.0-0.3.rc3
- 10.0.0 rc3

* Fri Feb 14 2020 sguelton@redhat.com - 10.0.0-0.2.rc2
- 10.0.0 rc2

* Fri Jan 31 2020 sguelton@redhat.com - 10.0.0-0.1.rc1
- 10.0.0 rc1

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 9.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Dec 19 2019 Tom Stellard <tstellar@redhat.com> - 9.0.1-1
- 9.0.1 Release

* Thu Sep 19 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-1
- 9.0.0 Release

* Thu Aug 22 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-0.1.rc3
- 9.0.0-rc3 Release

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 8.0.0-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Apr 25 2019 Tom Stellard <tstellar@redhat.com> - 8.0.0-2
- Simplify libomp-test package

* Wed Mar 20 2019 sguelton@redhat.com - 8.0.0-1
- 8.0.0 final

* Tue Mar 12 2019 sguelton@redhat.com - 8.0.0-0.3.rc4
- 8.0.0 Release candidate 4

* Mon Feb 11 2019 sguelton@redhat.com - 8.0.0-0.2.rc2
- 8.0.0 Release candidate 2

* Mon Feb 11 2019 sguelton@redhat.com - 8.0.0-0.1.rc1
- 8.0.0 Release candidate 1

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 7.0.1-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 17 2018 sguelton@redhat.com - 7.0.1-1
- 7.0.1 Release

* Wed Sep 12 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-1
- 7.0.1 Release

* Wed Sep 12 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.2.rc3
- 7.0.0-rc3 Release

* Tue Aug 14 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.1.rc1
- 7.0.1-rc1 Release

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 02 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-2
- Add -threads option to runtest.sh

* Thu Jun 28 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-1
- 6.0.1 Release

* Fri May 11 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.1.rc1
- 6.0.1-rc1 Release

* Wed Mar 28 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-3
- Add test package

* Wed Mar 28 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-2
- Enable libomptarget plugins

* Fri Mar 09 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-1
- 6.0.0 Release

* Tue Feb 13 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.3.rc2
- 6.0.0-rc2 Release

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.0-0.2.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 25 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.1.rc1
- 6.0.0-rc1 Release

* Thu Dec 21 2017 Tom Stellard <tstellar@redhat.com> - 5.0.1-1
- 5.0.1 Release.

* Mon May 15 2017 Tom Stellard <tstellar@redhat.com> - 5.0.0-1
- Initial version.
