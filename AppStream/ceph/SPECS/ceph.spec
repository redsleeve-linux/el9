#
# spec file for package ceph
#
# Copyright (C) 2004-2019 The Ceph Project Developers. See COPYING file
# at the top-level directory of this distribution and at
# https://github.com/ceph/ceph/blob/master/COPYING
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon.
#
# This file is under the GNU Lesser General Public License, version 2.1
#
# Please submit bugfixes or comments via http://tracker.ceph.com/
#

#################################################################################
# conditional build section
#
# please read http://rpm.org/user_doc/conditional_builds.html for explanation of
# bcond syntax!
#################################################################################
%global _hardened_build 1

%bcond_with make_check
%bcond_with zbd
%bcond_with cmake_verbose_logging
%bcond_with ceph_test_package
%bcond_with tcmalloc

%if 0%{?fedora} || 0%{?rhel}
%bcond_with amqp_endpoint
%bcond_with kafka_endpoint
%bcond_with lttng
%bcond_without libradosstriper
%bcond_with ocf
%global _remote_tarball_prefix https://download.ceph.com/tarballs/
%endif
%bcond_with jaeger
%bcond_with rbd_rwl_cache
%bcond_with rbd_ssd_cache
%if 0%{?fedora} || 0%{?suse_version} >= 1500
# distros that ship cmd2 and/or colorama
%bcond_without cephfs_shell
%else
# distros that do _not_ ship cmd2/colorama
%bcond_with cephfs_shell
%endif
%if 0%{?fedora} || 0%{?suse_version} || 0%{?rhel} >= 8
%global weak_deps 1
%endif

%{!?_udevrulesdir: %global _udevrulesdir /lib/udev/rules.d}
%{!?tmpfiles_create: %global tmpfiles_create systemd-tmpfiles --create}
%{!?python3_pkgversion: %global python3_pkgversion 3}
%{!?python3_version_nodots: %global python3_version_nodots 3}
%{!?python3_version: %global python3_version 3}

# disable dwz which compresses the debuginfo
%global _find_debuginfo_dwz_opts %{nil}

#################################################################################
# main package definition
#################################################################################
Name:		ceph
Version:	16.2.4
Release:	5%{?dist}
%if 0%{?fedora} || 0%{?rhel}
Epoch:		2
%endif

# define _epoch_prefix macro which will expand to the empty string if epoch is
# undefined
%global _epoch_prefix %{?epoch:%{epoch}:}

Summary:	User space components of the Ceph file system
#License:	LGPL-2.1 and LGPL-3.0 and CC-BY-SA-3.0 and GPL-2.0 and BSL-1.0 and BSD-3-Clause and MIT
License:	LGPLv2+ and CC-BY-SA-3.0 and GPLv2 and Boost and BSD and MIT
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
URL:		http://ceph.com/
Source0:        ceph-16.2.4.tar.gz
Patch0001:	0001-src-common-crc32c_intel_fast.patch
Patch0002:	0002-src-common-CMakeLists.txt.patch
Patch0003:	0003-src-common-bitstr.h.patch
Patch0006:	0006-src-blk-CMakeLists.txt.patch
Patch0007:	0007-src-test-neorados-CMakeLists.txt.patch
Patch0008:	0008-cmake-modules-Finduring.cmake.patch
Patch0009:	0009-librgw-notifications-initialize-kafka-and-amqp.patch
Patch0010:	0010-os-bluestore-strip-trailing-slash-for-directory-list.patch
Patch0011:	0011-src-test-rgw-amqp_mock.cc.patch
Patch0012:	0012-src-compressor-snappy-SnappyCompressor.h.patch
Patch0013:	0013-osdc-Objecter-move-LingerOp-s-ctor-to-.cc.patch
Patch0014:	0014-cmake-add-an-option-WITH_FMT_HEADER_ONLY.patch
Patch0015:	0015-ceph.spec.in-build-with-header-only-fmt-on-RHEL.patch
Patch0016:      0016-cmake-link-bundled-fmt-statically.patch
# ceph 14.0.1 does not support 32-bit architectures, bugs #1727788, #1727787
ExcludeArch:	i686 armv7hl
%if 0%{?suse_version}
# _insert_obs_source_lines_here
ExclusiveArch:	x86_64 aarch64 ppc64le s390x
%endif
#################################################################################
# dependencies that apply across all distro families
#################################################################################
Requires:	ceph-osd = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-mds = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-mgr = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-mon = %{_epoch_prefix}%{version}-%{release}
Requires(post):	binutils
BuildRequires:	gperf
BuildRequires:	cmake > 3.5
BuildRequires:	cryptsetup
BuildRequires:	fuse3-devel
BuildRequires:	doxygen
%if 0%{?rhel} == 7
# devtoolset offers newer make and valgrind-devel, but the old ones are good
# enough.
BuildRequires:	devtoolset-9-gcc-c++ >= 9.2.1-2.3
%else
BuildRequires:	gcc-c++
%endif
BuildRequires:	gdbm
%if 0%{with tcmalloc}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	gperftools-devel >= 2.6.1
%endif
%if 0%{?suse_version}
BuildRequires:	gperftools-devel >= 2.4
%endif
%endif
BuildRequires:	libaio-devel
BuildRequires:	libblkid-devel >= 2.17
BuildRequires:	cryptsetup-devel
BuildRequires:	libcurl-devel
BuildRequires:	libcap-ng-devel
BuildRequires:	pkgconfig(libudev)
BuildRequires:	libnl3-devel
BuildRequires:	libtool
BuildRequires:	libxml2-devel
BuildRequires:	make
BuildRequires:	ncurses-devel
BuildRequires:	parted
BuildRequires:	patch
BuildRequires:	perl
BuildRequires:	pkgconfig
BuildRequires:	procps
BuildRequires:	python%{python3_pkgversion}
BuildRequires:	python%{python3_pkgversion}-devel
BuildRequires:	python%{python3_pkgversion}-setuptools
BuildRequires:	snappy-devel
BuildRequires:	sqlite-devel
BuildRequires:	sudo
BuildRequires:	pkgconfig(udev)
BuildRequires:	util-linux
BuildRequires:	valgrind-devel
BuildRequires:	which
BuildRequires:	xfsprogs
BuildRequires:	xfsprogs-devel
BuildRequires:	lua-devel
BuildRequires:	nasm
%if 0%{with amqp_endpoint}
BuildRequires:	librabbitmq-devel
%endif
%if 0%{with kafka_endpoint}
BuildRequires:	librdkafka-devel
%endif
%if 0%{with lua_packages}
BuildRequires:  %{luarocks_package_name}
%endif
%if 0%{with make_check}
BuildRequires:	jq
BuildRequires:	libuuid-devel
BuildRequires:	python%{python3_pkgversion}-bcrypt
BuildRequires:	python%{python3_pkgversion}-nose
BuildRequires:	python%{python3_pkgversion}-pecan
BuildRequires:	python%{python3_pkgversion}-requests
BuildRequires:	python%{python3_pkgversion}-dateutil
BuildRequires:	python%{python3_pkgversion}-coverage
BuildRequires:	python%{python3_pkgversion}-pyOpenSSL
BuildRequires:	socat
%endif
%if 0%{with zbd}
BuildRequires:  libzbd-devel
%endif
%if 0%{with jaeger}
BuildRequires:	bison
BuildRequires:	flex
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	json-devel
%endif
%if 0%{?suse_version}
BuildRequires:	nlohmann_json-devel
%endif
BuildRequires:	libevent-devel
BuildRequires:	yaml-cpp-devel
%endif
#################################################################################
# distro-conditional dependencies
#################################################################################
%if 0%{?suse_version}
BuildRequires:	pkgconfig(systemd)
BuildRequires:	systemd-rpm-macros
%{?systemd_requires}
PreReq:		%fillup_prereq
BuildRequires:	fdupes
BuildRequires:	net-tools
BuildRequires:	libbz2-devel
BuildRequires:	mozilla-nss-devel
BuildRequires:	keyutils-devel
BuildRequires:	libopenssl-devel
BuildRequires:	lsb-release
BuildRequires:	openldap2-devel
#BuildRequires:	krb5
#BuildRequires:	krb5-devel
BuildRequires:	cunit-devel
BuildRequires:	python%{python3_pkgversion}-setuptools
BuildRequires:	python%{python3_pkgversion}-Cython
BuildRequires:	python%{python3_pkgversion}-PrettyTable
BuildRequires:	python%{python3_pkgversion}-Sphinx
BuildRequires:	rdma-core-devel
BuildRequires:	liblz4-devel >= 1.7
# for prometheus-alerts
BuildRequires:	golang-github-prometheus-prometheus
%endif
%if 0%{?fedora} || 0%{?rhel}
Requires:	systemd
BuildRequires:	boost-devel
BuildRequires:	boost-random
BuildRequires:	nss-devel
BuildRequires:	keyutils-libs-devel
BuildRequires:	libibverbs-devel
BuildRequires:	librdmacm-devel
BuildRequires:	openldap-devel
#BuildRequires:	krb5-devel
BuildRequires:	openssl-devel
BuildRequires:	CUnit-devel
BuildRequires:	redhat-lsb-core
BuildRequires:	python%{python3_pkgversion}-devel
BuildRequires:	python%{python3_pkgversion}-setuptools
BuildRequires:	python%{python3_pkgversion}-Cython
BuildRequires:	python%{python3_pkgversion}-prettytable
BuildRequires:	python%{python3_pkgversion}-sphinx
BuildRequires:	lz4-devel >= 1.7
%endif
# distro-conditional make check dependencies
%if 0%{with make_check}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	libtool-ltdl-devel
BuildRequires:	xmlsec1
BuildRequires:	xmlsec1-devel
%ifarch x86_64
BuildRequires:	xmlsec1-nss
%endif
BuildRequires:	xmlsec1-openssl
BuildRequires:	xmlsec1-openssl-devel
BuildRequires:	python%{python3_pkgversion}-cherrypy
BuildRequires:	python%{python3_pkgversion}-jwt
BuildRequires:	python%{python3_pkgversion}-routes
BuildRequires:	python%{python3_pkgversion}-scipy
BuildRequires:	python%{python3_pkgversion}-werkzeug
BuildRequires:	python%{python3_pkgversion}-pyOpenSSL
%endif
%if 0%{?suse_version}
BuildRequires:	libxmlsec1-1
BuildRequires:	libxmlsec1-nss1
BuildRequires:	libxmlsec1-openssl1
BuildRequires:	python%{python3_pkgversion}-CherryPy
BuildRequires:	python%{python3_pkgversion}-PyJWT
BuildRequires:	python%{python3_pkgversion}-Routes
BuildRequires:	python%{python3_pkgversion}-Werkzeug
BuildRequires:	python%{python3_pkgversion}-numpy-devel
BuildRequires:	xmlsec1-devel
BuildRequires:	xmlsec1-openssl-devel
%endif
%endif
# lttng and babeltrace for rbd-replay-prep
%if %{with lttng}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	lttng-ust-devel
BuildRequires:	libbabeltrace-devel
%endif
%if 0%{?suse_version}
BuildRequires:	lttng-ust-devel
BuildRequires:	babeltrace-devel
%endif
%endif
%if 0%{?suse_version}
BuildRequires:	libexpat-devel
%endif
%if 0%{?rhel} || 0%{?fedora}
BuildRequires:	expat-devel
%endif
#hardened-cc1
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	redhat-rpm-config
%endif
%if 0%{?rhel} >= 8
BuildRequires:	/usr/bin/pathfix.py
%endif

%description
Ceph is a massively scalable, open-source, distributed storage system that runs
on commodity hardware and delivers object, block and file system storage.


#################################################################################
# subpackages
#################################################################################
%package -n ceph-common
Summary:	Ceph Common
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rbd = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-cephfs = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-ceph-argparse = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-ceph-common = %{_epoch_prefix}%{version}-%{release}
%if 0%{with jaeger}
Requires:	libjaeger = %{_epoch_prefix}%{version}-%{release}
%endif
%if 0%{?fedora} || 0%{?rhel}
Requires:	python%{python3_pkgversion}-prettytable
%endif
%if 0%{?suse_version}
Requires:	python%{python3_pkgversion}-PrettyTable
%endif
%if 0%{with libradosstriper}
Requires:	libradosstriper1 = %{_epoch_prefix}%{version}-%{release}
%endif
%{?systemd_requires}
%if 0%{?suse_version}
Requires(pre):	pwdutils
%endif
%description -n ceph-common
Common utilities to mount and interact with a ceph storage cluster.
Comprised of files that are common to Ceph clients and servers.

%package -n librados2
Summary:	RADOS distributed object store client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n librados2
RADOS is a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to access the distributed object
store using a simple file-like interface.

%package -n librados-devel
Summary:	RADOS headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	librados2-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	librados2-devel < %{_epoch_prefix}%{version}-%{release}
%description -n librados-devel
This package contains C libraries and headers needed to develop programs
that use RADOS object store.

%package -n libradospp-devel
Summary:	RADOS headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
%description -n libradospp-devel
This package contains C++ libraries and headers needed to develop programs
that use RADOS object store.

%package -n python%{python3_pkgversion}-rados
Summary:	Python 3 libraries for the RADOS object store
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
Requires:	python%{python3_pkgversion}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-rados}
Provides:	python-rados = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	python-rados < %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-rados
This package contains Python 3 libraries for interacting with Ceph RADOS
object store.

%package -n libcephsqlite
Summary:	SQLite3 VFS for Ceph
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%description -n libcephsqlite
A SQLite3 VFS for storing and manipulating databases stored on Ceph's RADOS
distributed object store.

%package -n libcephsqlite-devel
Summary:	SQLite3 VFS for Ceph headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	sqlite-devel
Requires:	libcephsqlite = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libcephsqlite-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libcephsqlite-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libcephsqlite-devel
A SQLite3 VFS for storing and manipulating databases stored on Ceph's RADOS
distributed object store.

%if 0%{with libradosstriper}
%package -n libradosstriper1
Summary:	RADOS striping interface
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%description -n libradosstriper1
Striping interface built on top of the rados library, allowing
to stripe bigger objects onto several standard rados objects using
an interface very similar to the rados one.

%package -n libradosstriper-devel
Summary:	RADOS striping interface headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	libradosstriper1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libradosstriper1-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libradosstriper1-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libradosstriper-devel
This package contains libraries and headers needed to develop programs
that use RADOS striping interface.
%endif

%package -n librbd1
Summary:	RADOS block device client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%if 0%{?suse_version}
Requires(post): coreutils
%endif
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n librbd1
RBD is a block device striped across multiple distributed objects in
RADOS, a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to manage these block devices.

%package -n librbd-devel
Summary:	RADOS block device headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	librbd1-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	librbd1-devel < %{_epoch_prefix}%{version}-%{release}
%description -n librbd-devel
This package contains libraries and headers needed to develop programs
that use RADOS block device.

%package -n python%{python3_pkgversion}-rbd
Summary:	Python 3 libraries for the RADOS block device
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-rbd}
Provides:	python-rbd = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	python-rbd < %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-rbd
This package contains Python 3 libraries for interacting with Ceph RADOS
block device.

%package -n libcephfs2
Summary:	Ceph distributed file system client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Obsoletes:	libcephfs1 < %{_epoch_prefix}%{version}-%{release}
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-libcephfs < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n libcephfs2
Ceph is a distributed network file system designed to provide excellent
performance, reliability, and scalability. This is a shared library
allowing applications to access a Ceph distributed file system via a
POSIX-like interface.

%package -n libcephfs-devel
Summary:	Ceph distributed file system headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libcephfs2-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libcephfs2-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libcephfs-devel
This package contains libraries and headers needed to develop programs
that use Ceph distributed file system.

%package -n python%{python3_pkgversion}-cephfs
Summary:	Python 3 libraries for Ceph distributed file system
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-ceph-argparse = %{_epoch_prefix}%{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-cephfs}
Provides:	python-cephfs = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	python-cephfs < %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-cephfs
This package contains Python 3 libraries for interacting with Ceph distributed
file system.

%package -n python%{python3_pkgversion}-ceph-argparse
Summary:	Python 3 utility libraries for Ceph CLI
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
%{?python_provide:%python_provide python%{python3_pkgversion}-ceph-argparse}
%description -n python%{python3_pkgversion}-ceph-argparse
This package contains types and routines for Python 3 used by the Ceph CLI as
well as the RESTful interface. These have to do with querying the daemons for
command-description information, validating user command input against those
descriptions, and submitting the command to the appropriate daemon.

%package -n python%{python3_pkgversion}-ceph-common
Summary:	Python 3 utility libraries for Ceph
%if 0%{?fedora} || 0%{?rhel} >= 8
Requires:	python%{python3_pkgversion}-pyyaml
%endif
%if 0%{?suse_version}
Requires:	python%{python3_pkgversion}-PyYAML
%endif
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
%{?python_provide:%python_provide python%{python3_pkgversion}-ceph-common}
%description -n python%{python3_pkgversion}-ceph-common
This package contains data structures, classes and functions used by Ceph.
It also contains utilities used for the cephadm orchestrator.

%if 0%{with ceph_test_package}
%package -n ceph-test
Summary:	Ceph benchmarks and test tools
%if 0%{?suse_version}
Group:		System/Benchmark
%endif
Requires:	ceph-common = %{_epoch_prefix}%{version}-%{release}
Requires:	xmlstarlet
Requires:	jq
Requires:	socat
BuildRequires:	gtest-devel
BuildRequires:	gmock-devel
%description -n ceph-test
This package contains Ceph benchmarks and test tools.
%endif

%package -n rados-objclass-devel
Summary:	RADOS object class development kit
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
%description -n rados-objclass-devel
This package contains libraries and headers needed to develop RADOS object
class plugins.

#################################################################################
# common
#################################################################################
%prep
%autosetup -p1 -n ceph-16.2.4

%build
# LTO can be enabled as soon as the following GCC bug is fixed:
# https://gcc.gnu.org/bugzilla/show_bug.cgi?id=48200
%define _lto_cflags %{nil}

%if 0%{?suse_version}
# the following setting fixed an OOM condition we once encountered in the OBS
RPM_OPT_FLAGS="$RPM_OPT_FLAGS --param ggc-min-expand=20 --param ggc-min-heapsize=32768"
%endif

export CPPFLAGS="$java_inc"
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"

# Parallel build settings ...
CEPH_MFLAGS_JOBS="%{?_smp_mflags}"
CEPH_SMP_NCPUS=$(echo "$CEPH_MFLAGS_JOBS" | sed 's/-j//')
%if 0%{?__isa_bits} == 32
# 32-bit builds can use 3G memory max, which is not enough even for -j2
CEPH_SMP_NCPUS="1"
%endif
# do not eat all memory
echo "Available memory:"
free -h
echo "System limits:"
ulimit -a
if test -n "$CEPH_SMP_NCPUS" -a "$CEPH_SMP_NCPUS" -gt 1 ; then
    mem_per_process=2700
    max_mem=$(LANG=C free -m | sed -n "s|^Mem: *\([0-9]*\).*$|\1|p")
    max_jobs="$(($max_mem / $mem_per_process))"
    test "$CEPH_SMP_NCPUS" -gt "$max_jobs" && CEPH_SMP_NCPUS="$max_jobs" && echo "Warning: Reducing build parallelism to -j$max_jobs because of memory limits"
    test "$CEPH_SMP_NCPUS" -le 0 && CEPH_SMP_NCPUS="1" && echo "Warning: Not using parallel build at all because of memory limits"
fi
export CEPH_SMP_NCPUS
export CEPH_MFLAGS_JOBS="-j$CEPH_SMP_NCPUS"

env | sort

mkdir build
cd build
%{cmake} .. \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DBUILD_CONFIG=rpmbuild \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DCMAKE_INSTALL_LIBEXECDIR=%{_libexecdir} \
    -DCMAKE_INSTALL_LOCALSTATEDIR=%{_localstatedir} \
    -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} \
    -DCMAKE_INSTALL_MANDIR=%{_mandir} \
    -DCMAKE_INSTALL_DOCDIR=%{_docdir}/ceph \
    -DCMAKE_INSTALL_INCLUDEDIR=%{_includedir} \
    -DCMAKE_INSTALL_SYSTEMD_SERVICEDIR=%{_unitdir} \
    -DWITH_MGR=OFF \
    -DWITH_EMBEDDED=OFF \
    -DWITH_MANPAGE=ON \
    -DWITH_PYTHON3=%{python3_version} \
    -DWITH_MGR_DASHBOARD_FRONTEND=OFF \
    -DWITH_SYSTEMD=ON \
    -DWITH_SYSTEM_BOOST=ON \
    -DWITH_SPDK=OFF \
    -DWITH_PMEM=OFF \
    -DWITH_BOOST_CONTEXT=OFF \
    -DWITH_LEVELDB=OFF \
    -DWITH_RADOSGW=OFF \
    -DWITH_SELINUX=OFF \
    -DWITH_CEPHFS_JAVA=OFF \
%if 0%{without ceph_test_package}
    -DWITH_TESTS=OFF \
%endif
%if %{with lttng}
    -DWITH_LTTNG=ON \
    -DWITH_BABELTRACE=ON \
%else
    -DWITH_LTTNG=OFF \
    -DWITH_BABELTRACE=OFF \
%endif
    $CEPH_EXTRA_CMAKE_ARGS \
%if 0%{with ocf}
    -DWITH_OCF=ON \
%endif
    -DWITH_REENTRANT_STRSIGNAL=ON \
    -DWITH_SYSTEM_BOOST=ON \
%if 0%{with cephfs_shell}
    -DWITH_CEPHFS_SHELL=ON \
%endif
%if 0%{with libradosstriper}
    -DWITH_LIBRADOSSTRIPER=ON \
%else
    -DWITH_LIBRADOSSTRIPER=OFF \
%endif
%if 0%{with amqp_endpoint}
    -DWITH_RADOSGW_AMQP_ENDPOINT=ON \
%else
    -DWITH_RADOSGW_AMQP_ENDPOINT=OFF \
%endif
%if 0%{with kafka_endpoint}
    -DWITH_RADOSGW_KAFKA_ENDPOINT=ON \
%else
    -DWITH_RADOSGW_KAFKA_ENDPOINT=OFF \
%endif
%if 0%{without lua_packages}
    -DWITH_RADOSGW_LUA_PACKAGES=OFF \
%endif
%if 0%{with zbd}
    -DWITH_ZBD=ON \
%endif
%if 0%{with cmake_verbose_logging}
    -DCMAKE_VERBOSE_MAKEFILE=ON \
%endif
%if 0%{with rbd_rwl_cache}
    -DWITH_RBD_RWL=ON \
%endif
%if 0%{with rbd_ssd_cache}
    -DWITH_RBD_SSD_CACHE=ON \
%endif
    -DBOOST_J=$CEPH_SMP_NCPUS \
%if 0%{with ceph_test_package}
    -DWITH_SYSTEM_GTEST=ON \
%endif
    -DWITH_FMT_HEADER_ONLY=ON \
    -DWITH_GRAFANA=OFF

%if %{with cmake_verbose_logging}
cat ./CMakeFiles/CMakeOutput.log
cat ./CMakeFiles/CMakeError.log
%endif

export VERBOSE=1
export V=1
%cmake_build "$CEPH_MFLAGS_JOBS"


%if 0%{with make_check}
%check
# run in-tree unittests
# cd build
# ctest "$CEPH_MFLAGS_JOBS"
%endif


%install
pushd build
%cmake_install
# we have dropped sysvinit bits
rm -f %{buildroot}/%{_sysconfdir}/init.d/ceph
popd
install -m 0644 -D src/etc-rbdmap %{buildroot}%{_sysconfdir}/ceph/rbdmap
install -m 0644 -D systemd/ceph.tmpfiles.d %{buildroot}%{_tmpfilesdir}/ceph-common.conf
mkdir -p %{buildroot}%{_sbindir}
chmod 0644 %{buildroot}%{_docdir}/ceph/sample.ceph.conf
install -m 0644 -D COPYING %{buildroot}%{_docdir}/ceph/COPYING

# firewall templates and /sbin/mount.ceph symlink
%if 0%{?suse_version}
mkdir -p %{buildroot}/sbin
ln -sf %{_sbindir}/mount.ceph %{buildroot}/sbin/mount.ceph
%endif

# udev rules
install -m 0644 -D udev/50-rbd.rules %{buildroot}%{_udevrulesdir}/50-rbd.rules

%if 0%{?rhel} >= 8
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" %{buildroot}%{_bindir}/*
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" %{buildroot}%{_sbindir}/*
%endif

#set up placeholder directories
mkdir -p %{buildroot}%{_sysconfdir}/ceph
mkdir -p %{buildroot}%{_localstatedir}/run/ceph
mkdir -p %{buildroot}%{_localstatedir}/log/ceph
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph

# Remove the rbd/fuse bits
rm -f %{buildroot}%{_bindir}/ceph-fuse
rm -f %{buildroot}%{_mandir}/man8/ceph-fuse.8*
rm -f %{buildroot}%{_sbindir}/mount.fuse.ceph
rm -f %{buildroot}%{_mandir}/man8/mount.fuse.ceph.8*
rm -f %{buildroot}%{_unitdir}/ceph-fuse@.service
rm -f %{buildroot}%{_unitdir}/ceph-fuse.target
rm -f %{buildroot}%{_bindir}/rbd-fuse
rm -f %{buildroot}%{_mandir}/man8/rbd-fuse.8*

# Remove the ceph-base package
rm -f %{buildroot}%{_bindir}/ceph-crash
rm -f %{buildroot}%{_bindir}/crushtool
rm -f %{buildroot}%{_bindir}/monmaptool
rm -f %{buildroot}%{_bindir}/osdmaptool
rm -f %{buildroot}%{_bindir}/ceph-kvstore-tool
rm -f %{buildroot}%{_bindir}/ceph-run
rm -f %{buildroot}%{_sbindir}/ceph-create-keys
rm -f %{buildroot}%{_sbindir}/ceph-volume
rm -f %{buildroot}%{_sbindir}/ceph-volume-systemd
rm -f %{buildroot}%{_libexecdir}/ceph/ceph_common.sh
rm -rf %{buildroot}%{_libdir}/rados-classes
rm -rf %{buildroot}%{_libdir}/ceph/erasure-code
rm -rf %{buildroot}%{_libdir}/ceph/compressor
rm -rf %{buildroot}%{_libdir}/ceph/crypto
rm -f %{buildroot}%{_unitdir}/ceph-crash.service
rm -f %{buildroot}%{_unitdir}/ceph-volume@.service
rm -f %{buildroot}%{_unitdir}/ceph.target
rm -rf %{buildroot}%{python3_sitelib}/ceph_volume/*
rm -rf %{buildroot}%{python3_sitelib}/ceph_volume-*
rm -f %{buildroot}%{_mandir}/man8/ceph-deploy.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-create-keys.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-volume.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-volume-systemd.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-run.8*
rm -f %{buildroot}%{_mandir}/man8/crushtool.8*
rm -f %{buildroot}%{_mandir}/man8/osdmaptool.8*
rm -f %{buildroot}%{_mandir}/man8/monmaptool.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-kvstore-tool.8*

# Remove the ceph-mds package
rm -f %{buildroot}%{_bindir}/ceph-mds
rm -f %{buildroot}%{_mandir}/man8/ceph-mds.8*
rm -f %{buildroot}%{_unitdir}/ceph-mds@.service
rm -f %{buildroot}%{_unitdir}/ceph-mds.target

# Remove the ceph-mgr package
rm -f %{buildroot}%{_unitdir}/ceph-mgr@.service
rm -f %{buildroot}%{_unitdir}/ceph-mgr.target

# Remove the ceph-mon package
rm -f %{buildroot}%{_bindir}/ceph-mon
rm -f %{buildroot}%{_bindir}/ceph-monstore-tool
rm -f %{buildroot}%{_mandir}/man8/ceph-mon.8*
rm -f %{buildroot}%{_unitdir}/ceph-mon@.service
rm -f %{buildroot}%{_unitdir}/ceph-mon.target

# Remove the ceph-radosgw package
rm -f %{buildroot}%{_unitdir}/ceph-radosgw@.service
rm -f %{buildroot}%{_unitdir}/ceph-radosgw.target

# Remove the ceph-osd package
rm -f %{buildroot}%{_bindir}/ceph-clsinfo
rm -f %{buildroot}%{_bindir}/ceph-bluestore-tool
rm -f %{buildroot}%{_bindir}/ceph-erasure-code-tool
rm -f %{buildroot}%{_bindir}/ceph-objectstore-tool
rm -f %{buildroot}%{_bindir}/ceph-osdomap-tool
rm -f %{buildroot}%{_bindir}/ceph-osd
rm -f %{buildroot}%{_libexecdir}/ceph/ceph-osd-prestart.sh
rm -f %{buildroot}%{_mandir}/man8/ceph-clsinfo.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-osd.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-bluestore-tool.8*
rm -f %{buildroot}%{_unitdir}/ceph-osd@.service
rm -f %{buildroot}%{_unitdir}/ceph-osd.target

# Remove rbd-mirror
rm -f %{buildroot}%{_bindir}/rbd-mirror
rm -f %{buildroot}%{_mandir}/man8/rbd-mirror.8*
rm -f %{buildroot}%{_unitdir}/ceph-rbd-mirror@.service
rm -f %{buildroot}%{_unitdir}/ceph-rbd-mirror.target

# Remove rbd-nbd
rm -f %{buildroot}%{_bindir}/rbd-nbd
rm -f %{buildroot}%{_mandir}/man8/rbd-nbd.8*

# Remove cephfs-top
rm -rf %{buildroot}%{python3_sitelib}/cephfs_top-*.egg-info
rm -f %{buildroot}%{_bindir}/cephfs-top
rm -f %{buildroot}%{_mandir}/man8/cephfs-top.8*

# Remove additional files
rm -f %{buildroot}%{_bindir}/ceph-diff-sorted
rm -f %{buildroot}%{_mandir}/man8/ceph-diff-sorted.8*

# Remove immutable-object-cache
rm -f %{buildroot}%{_bindir}/ceph-immutable-object-cache
rm -f %{buildroot}%{_mandir}/man8/ceph-immutable-object-cache.8*
rm -f %{buildroot}%{_unitdir}/ceph-immutable-object-cache@.service
rm -f %{buildroot}%{_unitdir}/ceph-immutable-object-cache.target

# Remove cephfs-mirror
rm -f %{buildroot}%{_bindir}/cephfs-mirror
rm -f %{buildroot}%{_mandir}/man8/cephfs-mirror.8*
rm -f %{buildroot}%{_unitdir}/cephfs-mirror@.service
rm -f %{buildroot}%{_unitdir}/cephfs-mirror.target

# Remove cephadm
rm -f %{buildroot}%{_mandir}/man8/cephadm.8*

%if 0%{?suse_version}
# create __pycache__ directories and their contents
%py3_compile %{buildroot}%{python3_sitelib}
# hardlink duplicate files under /usr to save space
%fdupes %{buildroot}%{_prefix}
%endif

%if 0%{?rhel} == 8 || 0%{?fedora} >= 33
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}
%endif

#################################################################################
# files and systemd scriptlets
#################################################################################
%files common
%dir %{_docdir}/ceph
%doc %{_docdir}/ceph/sample.ceph.conf
%license %{_docdir}/ceph/COPYING
%{_bindir}/ceph
%{_bindir}/ceph-authtool
%{_bindir}/ceph-conf
%{_bindir}/ceph-dencoder
%{_bindir}/ceph-rbdnamer
%{_bindir}/ceph-syn
%{_bindir}/cephfs-data-scan
%{_bindir}/cephfs-journal-tool
%{_bindir}/cephfs-table-tool
%{_bindir}/rados
%{_bindir}/rbd
%{_bindir}/rbd-replay
%{_bindir}/rbd-replay-many
%{_bindir}/rbdmap
%{_sbindir}/mount.ceph
%if 0%{?suse_version}
/sbin/mount.ceph
%endif
%if %{with lttng}
%{_bindir}/rbd-replay-prep
%endif
%{_bindir}/ceph-post-file
%{_tmpfilesdir}/ceph-common.conf
%{_mandir}/man8/ceph-authtool.8*
%{_mandir}/man8/ceph-conf.8*
%{_mandir}/man8/ceph-dencoder.8*
%{_mandir}/man8/ceph-rbdnamer.8*
%{_mandir}/man8/ceph-syn.8*
%{_mandir}/man8/ceph-post-file.8*
%{_mandir}/man8/ceph.8*
%{_mandir}/man8/mount.ceph.8*
%{_mandir}/man8/rados.8*
%{_mandir}/man8/rbd.8*
%{_mandir}/man8/rbdmap.8*
%{_mandir}/man8/rbd-replay.8*
%{_mandir}/man8/rbd-replay-many.8*
%{_mandir}/man8/rbd-replay-prep.8*
%dir %{_datadir}/ceph/
%{_datadir}/ceph/known_hosts_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com.pub
%dir %{_sysconfdir}/ceph/
%config %{_sysconfdir}/bash_completion.d/ceph
%config %{_sysconfdir}/bash_completion.d/rados
%config %{_sysconfdir}/bash_completion.d/rbd
%config(noreplace) %{_sysconfdir}/ceph/rbdmap
%{_unitdir}/rbdmap.service
%dir %{_udevrulesdir}
%{_udevrulesdir}/50-rbd.rules
%attr(3770,ceph,ceph) %dir %{_localstatedir}/log/ceph/
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/

%pre common
CEPH_GROUP_ID=167
CEPH_USER_ID=167
%if 0%{?rhel} || 0%{?fedora}
/usr/sbin/groupadd ceph -g $CEPH_GROUP_ID -o -r 2>/dev/null || :
/usr/sbin/useradd ceph -u $CEPH_USER_ID -o -r -g ceph -s /sbin/nologin -c "Ceph daemons" -d %{_localstatedir}/lib/ceph 2>/dev/null || :
%endif
%if 0%{?suse_version}
if ! getent group ceph >/dev/null ; then
    CEPH_GROUP_ID_OPTION=""
    getent group $CEPH_GROUP_ID >/dev/null || CEPH_GROUP_ID_OPTION="-g $CEPH_GROUP_ID"
    groupadd ceph $CEPH_GROUP_ID_OPTION -r 2>/dev/null || :
fi
if ! getent passwd ceph >/dev/null ; then
    CEPH_USER_ID_OPTION=""
    getent passwd $CEPH_USER_ID >/dev/null || CEPH_USER_ID_OPTION="-u $CEPH_USER_ID"
    useradd ceph $CEPH_USER_ID_OPTION -r -g ceph -s /sbin/nologin 2>/dev/null || :
fi
usermod -c "Ceph storage service" \
        -d %{_localstatedir}/lib/ceph \
        -g ceph \
        -s /sbin/nologin \
        ceph
%endif
exit 0

%post common
%tmpfiles_create %{_tmpfilesdir}/ceph-common.conf

%postun common
# Package removal cleanup
if [ "$1" -eq "0" ] ; then
    rm -rf %{_localstatedir}/log/ceph
    rm -rf %{_sysconfdir}/ceph
fi

%files -n librados2
%{_libdir}/librados.so.*
%dir %{_libdir}/ceph
%{_libdir}/ceph/libceph-common.so.*
%if %{with lttng}
%{_libdir}/librados_tp.so.*
%endif
%dir %{_sysconfdir}/ceph

%post -n librados2 -p /sbin/ldconfig

%postun -n librados2 -p /sbin/ldconfig

%files -n librados-devel
%dir %{_includedir}/rados
%{_includedir}/rados/librados.h
%{_includedir}/rados/rados_types.h
%{_libdir}/librados.so
%if %{with lttng}
%{_libdir}/librados_tp.so
%endif
%{_bindir}/librados-config
%{_mandir}/man8/librados-config.8*

%files -n libradospp-devel
%dir %{_includedir}/rados
%{_includedir}/rados/buffer.h
%{_includedir}/rados/buffer_fwd.h
%{_includedir}/rados/crc32c.h
%{_includedir}/rados/inline_memory.h
%{_includedir}/rados/librados.hpp
%{_includedir}/rados/librados_fwd.hpp
%{_includedir}/rados/page.h
%{_includedir}/rados/rados_types.hpp

%files -n python%{python3_pkgversion}-rados
%{python3_sitearch}/rados.cpython*.so
%{python3_sitearch}/rados-*.egg-info

%files -n libcephsqlite
%{_libdir}/libcephsqlite.so

%post -n libcephsqlite -p /sbin/ldconfig

%postun -n libcephsqlite -p /sbin/ldconfig

%files -n libcephsqlite-devel
%{_includedir}/libcephsqlite.h

%if 0%{with libradosstriper}
%files -n libradosstriper1
%{_libdir}/libradosstriper.so.*

%post -n libradosstriper1 -p /sbin/ldconfig

%postun -n libradosstriper1 -p /sbin/ldconfig

%files -n libradosstriper-devel
%dir %{_includedir}/radosstriper
%{_includedir}/radosstriper/libradosstriper.h
%{_includedir}/radosstriper/libradosstriper.hpp
%{_libdir}/libradosstriper.so
%endif

%files -n librbd1
%{_libdir}/librbd.so.*
%if %{with lttng}
%{_libdir}/librbd_tp.so.*
%endif
%dir %{_libdir}/ceph/librbd
%{_libdir}/ceph/librbd/libceph_*.so*

%post -n librbd1 -p /sbin/ldconfig

%postun -n librbd1 -p /sbin/ldconfig

%files -n librbd-devel
%dir %{_includedir}/rbd
%{_includedir}/rbd/librbd.h
%{_includedir}/rbd/librbd.hpp
%{_includedir}/rbd/features.h
%{_libdir}/librbd.so
%if %{with lttng}
%{_libdir}/librbd_tp.so
%endif

%files -n python%{python3_pkgversion}-rbd
%{python3_sitearch}/rbd.cpython*.so
%{python3_sitearch}/rbd-*.egg-info

%files -n libcephfs2
%{_libdir}/libcephfs.so.*
%dir %{_sysconfdir}/ceph

%post -n libcephfs2 -p /sbin/ldconfig

%postun -n libcephfs2 -p /sbin/ldconfig

%files -n libcephfs-devel
%dir %{_includedir}/cephfs
%{_includedir}/cephfs/libcephfs.h
%{_includedir}/cephfs/ceph_ll_client.h
%dir %{_includedir}/cephfs/metrics
%{_includedir}/cephfs/metrics/Types.h
%{_libdir}/libcephfs.so

%files -n python%{python3_pkgversion}-cephfs
%{python3_sitearch}/cephfs.cpython*.so
%{python3_sitearch}/cephfs-*.egg-info
%{python3_sitelib}/ceph_volume_client.py
%{python3_sitelib}/__pycache__/ceph_volume_client.cpython*.py*

%files -n python%{python3_pkgversion}-ceph-argparse
%{python3_sitelib}/ceph_argparse.py
%{python3_sitelib}/__pycache__/ceph_argparse.cpython*.py*
%{python3_sitelib}/ceph_daemon.py
%{python3_sitelib}/__pycache__/ceph_daemon.cpython*.py*

%files -n python%{python3_pkgversion}-ceph-common
%{python3_sitelib}/ceph
%{python3_sitelib}/ceph-*.egg-info

%if 0%{with ceph_test_package}
%files -n ceph-test
%{_bindir}/ceph-client-debug
%{_bindir}/ceph_bench_log
%{_bindir}/ceph_kvstorebench
%{_bindir}/ceph_multi_stress_watch
%{_bindir}/ceph_erasure_code_benchmark
%{_bindir}/ceph_omapbench
%{_bindir}/ceph_objectstore_bench
%{_bindir}/ceph_perf_objectstore
%{_bindir}/ceph_perf_local
%{_bindir}/ceph_perf_msgr_client
%{_bindir}/ceph_perf_msgr_server
%{_bindir}/ceph_psim
%{_bindir}/ceph_radosacl
%{_bindir}/ceph_rgw_jsonparser
%{_bindir}/ceph_rgw_multiparser
%{_bindir}/ceph_scratchtool
%{_bindir}/ceph_scratchtoolpp
%{_bindir}/ceph_test_*
%{_bindir}/ceph-coverage
%{_bindir}/ceph-debugpack
%{_bindir}/ceph-dedup-tool
%{_mandir}/man8/ceph-debugpack.8*
%dir %{_libdir}/ceph
%{_libdir}/ceph/ceph-monstore-update-crush.sh
%endif

%files -n rados-objclass-devel
%dir %{_includedir}/rados
%{_includedir}/rados/objclass.h

%changelog
* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 2:16.2.4-5
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Aug 05 2021 Boris Ranto <branto@redhat.com> - 2:16.2.4-4
- Drop fmt-devel from build requires

* Tue Jul 27 2021 Boris Ranto <branto@redhat.com> - 2:16.2.4-3
- Apply fmt-header-only patches
- Update licence field
- Drop unnecessary dependencies

* Wed Jun 16 2021 Mohan Boddu <mboddu@redhat.com> - 2:16.2.4-2
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Fri May 28 2021 Boris Ranto <branto@redhat.com> - 2:16.2.4-1
- Rebase to 16.2.4
- Add libcephsqlite packages

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 2:16.1.0-0.8.snapshot
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Mon Mar 15 2021 Boris Ranto <branto[at]redhat.com> - 2:16.1.0-0.7.snapshot
- libblk.so -> libblk.a
- remove python3-rgw from ceph-common deps

* Mon Mar 15 2021 Boris Ranto <branto[at]redhat.com> - 2:16.1.0-0.6.snapshot
- disable multiple build options
- disable multiple packages
- remove unnecessary files

* Fri Mar 5 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.5.snapshot
- ceph 16.1.0 RC (ceph-16.1.0-308-gabe639eb)
-  rpmbuild apparently unable to automatically derive 'Requires: rocksdb' from 'BuildRequires: rocksdb-devel' for librocksdb.so.6.13

* Sat Feb 20 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.4.snapshot
- ceph 16.1.0 RC (ceph-16.1.0-308-gabe639eb)

* Thu Feb 4 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.3.snapshot
- rocksdb not available in el8+, use bundled rocksdb

* Mon Feb 1 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.2.snapshot
- libblk.so -> libblk.a
- libneoradostest-support.so -> libneoradostest-support.a
- w/ liburing-devel, -DWITH_SYSTEM_LIBURING=ON
- w/ rocksdb-devel, -DWITH_SYSTEM_ROCKSDB=ON

* Fri Jan 29 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.1.snapshot
- ceph 16.1.0 RC (ceph-16.1.0-43-g6b74fb5c)

* Wed Sep 16 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.5-1
- ceph 15.2.5 GA

* Wed Jul 29 2020 Richard W.M. Jones <rjones@redhat.com> - 2:15.2.4-11
- Rebuild against fmt 7.

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2:15.2.4-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 21 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-9
- %cmake_build and %cmake_install

* Mon Jul 20 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-8
- see 15.2.4-4 (f33-java11) for real this time
- and use %make_install macro

* Mon Jul 20 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-7
- see 15.2.4-3, hopefully for real this time
- and use %make_install macro

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-6
- see 15.2.4-4

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-5
- see 15.2.4-3

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-4
- Rebuilt for JDK-11, see https://fedoraproject.org/wiki/Changes/Java11

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-3
- use `ld -r -z ibt -z shstk...` instead of magic hackery to get CET ibt
  and shstk. N.B. updated yasm in f33/rawhide now has support for
  .note.gnu.properties so even this will go away in the next build
- signal_handler.cc, use HAVE_REENTRANT_STRSIGNAL, strsignal(3)

* Fri Jul 10 2020 Jiri Vanek <jvanek@redhat.com> - 2:15.2.4-2
- Rebuilt for JDK-11, see https://fedoraproject.org/wiki/Changes/Java11

* Wed Jul 1 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-1
- ceph 15.2.4 GA

* Tue Jun 23 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- explicit BuildRequires python3-setuptools

* Mon Jun 1 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.3-1
- ceph 15.2.3 GA

* Tue May 26 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.2-3
- ceph 15.2.2, CET enable src/common/crc32c_intel_*_asm.s; shstk, ibt
- and other fixes
- see https://github.com/intel/isa-l/blob/master/crc/crc32_iscsi_00.asm

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 2:15.2.2-2
- Rebuilt for Python 3.9

* Mon May 18 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.2-1
- ceph 15.2.2 GA

* Mon May 18 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.1-2
- ceph 15.2.1, gmock and gtest. (although gmock last built for f27)

* Fri Apr 10 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.1-1
- ceph 15.2.1 GA

* Mon Mar 23 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.0-1
- ceph 15.2.0 GA

* Mon Mar 16 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.1-2
- ceph 15.1.1 fmt, rhbz#1805422 again

* Mon Mar 16 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.1-1
- ceph 15.1.1 RC

* Thu Mar 5 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.0-3
- ceph 15.1.0, rhbz#1809799

* Thu Feb 20 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.0-2
- ceph 15.1.0, fmt, rhbz#1805422

* Tue Feb 11 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.0-1
- ceph 15.1.0 RC

* Mon Feb 3 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.7-2
- ceph 14.2.7 python3-remoto #1784216

* Sat Feb 1 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.7-1
- ceph 14.2.7 GA

* Wed Jan 29 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-4
- ceph 14.2.6, https://tracker.ceph.com/issues/43649

* Mon Jan 27 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-3
- ceph 14.2.6, (temporarily) disable unit tests

* Fri Jan 24 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- ceph 14.2.6, gcc-10, missing includes

* Thu Jan 9 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-2
- ceph 14.2.6

* Thu Jan 9 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-1
- ceph 14.2.6 GA

* Tue Dec 10 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.5-1
- ceph 14.2.5 GA

* Mon Nov 11 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.4-3
- ceph 14.2.4, fix typo

* Tue Nov 5 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.4-2
- ceph 14.2.4, partial fix for bz#1768017

* Tue Sep 17 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.4-1
- ceph 14.2.4 GA

* Wed Sep 4 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.3-1
- ceph 14.2.3 GA

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 2:14.2.2-3
- Rebuilt for Python 3.8

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:14.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jul 19 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.2-1
- ceph 14.2.2 GA

* Tue May 28 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.0-2
- numpy -> python3-numpy, bz#1712203 (and why I like to keep upstream
  and fedora .spec files in sync)

* Wed May 8 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- sync w/ upstream to minimize diffs/drift

* Mon Apr 29 2019 Boris Ranto <branto@redhat.com> - 2:14.2.1-1
- Rebase to latest upstream version (14.2.1)

* Tue Mar 19 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.0-1
- ceph 14.2.0 GA

* Wed Mar 13 2019 Boris Ranto <branto@redhat.com> - 2:14.1.1-1
- Rebase to latest upstream version

* Thu Mar 07 2019 Adam Williamson <awilliam@redhat.com> - 2:14.1.0-3
- Return epoch to 2, epochs cannot ever go backwards

* Wed Mar 6 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:14.1.0-2
- ceph 14.1.0 w/ static libcrc32

* Wed Feb 27 2019 Boris Ranto <branto@redhat.com> - 1:14.1.0-1
- Rebase to v14.1.0 (updated for fixes in upstream nautilus branch)

* Thu Feb 21 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:14.0.1-2
- Eliminate redundant CMAKE_* macros when using %%cmake global
- Add CMAKE_BUILD_TYPE=RelWithDeb(ug)Info and BUILD_CONFIG=rpmbuild

* Wed Feb 20 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:14.0.1-1
- rebuild for f31/rawhide, including:
- use the %%{cmake} %%global to get all the extra Fedora cmake options.
  (This is Fedora, so don't care so much about rhel/rhel7 cmake3.)
- reset epoch to 1. Note we use (have been using) epoch=1 in Fedora since
  forever. I presume this is so that people can install Ceph RPMs from
  ceph.com if they prefer those, which use epoch=2, and not run into issues
  when updating.

* Thu Feb 7 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.0.1-4
- w/ fixes for gcc9

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:14.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Dec 08 2018 Boris Ranto <branto@redhat.com> - 2:14.0.1-2
- fix pyOpenSSL depemdency

* Tue Dec 04 2018 Boris Ranto <branto@redhat.com> - 2:14.0.1-1
- New release (2:14.0.1-1)
- Sync with upstream
- Drop 32-bit support

* Wed Nov 21 2018 Boris Ranto <branto@redhat.com> - 2:13.2.2-1
- New release (2:13.2.2-1)
- Sync with upstream

* Mon Oct 29 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.9-1
- New release (1:12.2.9-1)

* Wed Sep 12 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.8-2
- Fedora 30 python3. Note ceph-mgr subpackage, ceph-detect-init, ceph-disk,
  ceph-volume, and ceph-volume-systemd are missing in this build

* Fri Aug 31 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.8-1
- New release (1:12.2.8-1)

* Wed Jul 18 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.7-1
- New release (1:12.2.7-1)

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 11 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.6-1
- New release (1:12.2.6-1)

* Mon Jul 2 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.5-3
- New release (1:12.2.5-3) w/ python-3.7

* Fri Jun 29 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.5-2
- New release (1:12.2.5-2)

* Fri Apr 27 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.5-1
- New release (1:12.2.5-1)

* Fri Apr 13 2018 Rafael dos Santos <rdossant@redhat.com> - 1:12.2.4-2
- Use standard Fedora linker flags (bug #1547552)

* Fri Mar 2 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.4-1
- New release (1:12.2.4-1)
- rhbz#1446610, rhbz#1546611, cephbz#23039

* Wed Feb 21 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.3-1
- New release (1:12.2.3-1)

* Thu Feb 15 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.2-3
- no ldconfig in F28

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Dec 5 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.2-1
- New release (1:12.2.2-1)
- Fix build error on arm

* Thu Oct 05 2017 Boris Ranto <branto@redhat.com> - 1:12.2.1-2
- Obsolete ceph-libs-compat package

* Wed Sep 27 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.1-1
- New release (1:12.2.1-1)

* Tue Aug 29 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.0-1
- New release (1:12.2.0-1)

* Thu Aug 24 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-5
- libibverbs(-devel) is superceded by rdma-core(-devel), again

* Thu Aug 24 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-4
- libibverbs(-devel) is superceded by rdma-core(-devel)

* Tue Aug 22 2017 Adam Williamson <awilliam@redhat.com> - 1:12.1.4-3
- Disable RDMA support on 32-bit ARM (#1484155)

* Thu Aug 17 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-2
- fix %%epoch in comment, ppc64le lowmem_builder

* Wed Aug 16 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-1
- New release (1:12.1.4-1)

* Sat Aug 12 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.3-1
- New release (1:12.1.3-1)

* Fri Aug 11 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-3
- rebuild with librpm.so.7

* Thu Aug 10 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-2
- Fix 32-bit alignment

* Thu Aug 3 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-1
- New release (1:12.1.2-1)

* Tue Aug 1 2017 Boris Ranto <branto@redhat.com> - 1:12.1.1-8
- Fix ppc64 build

* Tue Aug 1 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-7
- python34 and other nits
- still no fix for ppc64

* Sun Jul 30 2017 Florian Weimer <fweimer@redhat.com> - 1:12.1.1-6
- Reenable ppc64le, with binutils fix for ppc64le (#1475636)

* Fri Jul 28 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-5
- ppc64le disabled until bz #1475636 resolution

* Fri Jul 28 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-4
- 12.1.1 w/ hacks for armv7hl: low mem, no java jni
- WTIH_BABELTRACE -> WITH_BABELTRACE for all archs
- still no fix for ppc64

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Jul 22 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-2
- 12.1.1 w/ rocksdb patch (i686)

* Sat Jul 22 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-1
- New release (1:12.1.1-1)

* Fri Jul 21 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-0
- New release (1:12.1.1-0)

* Fri Jul 21 2017 Kalev Lember <klember@redhat.com> - 1:10.2.7-3
- Rebuilt for Boost 1.64

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.2.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Mon Apr 17 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:10.2.7-1
- New release (1:10.2.7-1)

* Wed Feb 08 2017 Boris Ranto <branto@redhat.com> - 1:10.2.5-2
- New release (1:10.2.5-2)

* Fri Jan 13 2017 Boris Ranto <branto@redhat.com> - 1:10.2.5-1
- New release (1:10.2.5-1)
- hack: do not test for libxfs, assume it is present

* Wed Dec 14 2016 Boris Ranto <branto@redhat.com> - 1:10.2.4-2
- New version (1:10.2.4-2)
- This syncs up with the upstream 10.2.5
- Doing it this way because of broken lookaside cache
- Fix the -devel obsoletes

* Thu Dec 08 2016 Boris Ranto <branto@redhat.com> - 1:10.2.4-1
- New version (1:10.2.4-1)
- Disable erasure_codelib neon build
- Use newer -devel package format
- Sync up the spec file

* Wed Oct 26 2016 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:10.2.3-4
- librgw: add API version defines for librgw and rgw_file

* Wed Oct 26 2016 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:10.2.3-3
- update patches style for rdopkg

* Thu Sep 29 2016 Boris Ranto <branto@redhat.com> - 1:10.2.3-2
- New release (1:10.2.3-2)
- common: instantiate strict_si_cast<long> not

* Thu Sep 29 2016 Boris Ranto <branto@redhat.com> - 1:10.2.3-1
- New version (1:10.2.3-1)
- Disable erasure_codelib neon build

* Sun Aug 07 2016 Igor Gnatenko <ignatenko@redhat.com> - 1:10.2.2-4
- Rebuild for LevelDB 1.18

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.2.2-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Jun 21 2016 Boris Ranto <branto@redhat.com> - 1:10.2.2-2
- New release (1:10.2.2-2)
- fix tcmalloc handling in spec file

* Mon Jun 20 2016 Boris Ranto <branto@redhat.com> - 1:10.2.2-1
- New version (1:10.2.2-1)
- Disable erasure_codelib neon build
- Do not use -momit-leaf-frame-pointer flag

* Mon May 16 2016 Boris Ranto <branto@redhat.com> - 1:10.2.1-1
- New version (1:10.2.1-1)
- Disable erasure_codelib neon build
- Do not use -momit-leaf-frame-pointer flag

* Fri May 06 2016 Dan Horák <dan[at]danny.cz> - 10.2.0-3
- fix build on s390(x) - gperftools/tcmalloc not available there

* Fri Apr 22 2016 Boris Ranto <branto@redhat.com> - 10.2.0-2
- Do not use -momit-leaf-frame-pointer flag

* Fri Apr 22 2016 Boris Ranto <branto@redhat.com> - -
- Rebase to version 10.2.0
- Disable erasure_codelib neon build

* Mon Apr 11 2016 Richard W.M. Jones <rjones@redhat.com> - 1:9.2.0-5
- Fix large startup times of processes linking to -lrbd.
  Backport upstream commit 1c2831a2, fixes RHBZ#1319483.
- Add workaround for XFS header brokenness.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:9.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 14 2016 Jonathan Wakely <jwakely@redhat.com> - 1:9.2.0-3
- Rebuilt for Boost 1.60

* Mon Dec 14 2015 Dan Horák <dan[at]danny.cz> - 1:9.2.0-2
- fix build on s390(x) - gperftools/tcmalloc not available there

* Tue Nov 10 2015 Boris Ranto <branto@redhat.com> - 1:9.2.0-1
- Rebase to latest stable upstream version (9.2.0 - infernalis)
- Use upstream spec file

* Tue Oct 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.5-1
- Rebase to latest upstream version

* Tue Oct 20 2015 Boris Ranto <branto@redhat.com> - 1:0.94.4-1
- Rebase to latest upstream version
- The rtdsc patch got merged upstream and is already present in the release

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1:0.94.3-2
- Rebuilt for Boost 1.59

* Thu Aug 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.3-1
- Rebase to latest upstream version
- The boost patch got merged upstream and is already present in the release

* Fri Jul 31 2015 Richard W.M. Jones <rjones@redhat.com> - 1:0.94.2-4
- Fix build against boost 1.58 (http://tracker.ceph.com/issues/11576).

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.2-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 1:0.94.2-2
- rebuild for Boost 1.58

* Thu Jul 16 2015 Boris Ranto <branto@redhat.com> - 1:0.94.2-1
- Rebase to latest upstream version

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Dan Horák <dan[at]danny.cz> - 1:0.94.1-4
- fix build on s390(x) - no gperftools there

* Thu May 21 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-3
- Disable lttng support (rhbz#1223319)

* Mon May 18 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-2
- Fix arm linking issue (rhbz#1222286)

* Tue Apr 14 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-1
- Rebase to latest upstream version and sync-up the spec file
- Add arm compilation patches

* Wed Apr 01 2015 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:0.87.1-3
- add version numbers to Obsoletes (RHBZ #1193182)

* Wed Mar 4 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-2
- Perform a hardened build
- Use git-formatted patches
- Add patch for pthreads rwlock unlock problem
- Do not remove conf files on uninstall
- Remove the cleanup function, it is only necessary for f20 and f21

* Wed Feb 25 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-1
- Rebase to latest upstream
- Remove boost patch, it is in upstream tarball
- Build with yasm, tarball contains fix for the SELinux issue

* Thu Jan 29 2015 Petr Machata <pmachata@redhat.com> - 1:0.87-2
- Rebuild for boost 1.57.0
- Include <boost/optional/optional_io.hpp> instead of
  <boost/optional.hpp>.  Keep the old dumping behavior in
  osd/ECBackend.cc (ceph-0.87-boost157.patch)

* Mon Nov 3 2014 Boris Ranto <branto@redhat.com> - 1:0.87-1
- Rebase to latest major version (firefly -> giant)

* Thu Oct 16 2014 Boris Ranto <branto@redhat.com - 1:0.80.7-1
- Rebase to latest upstream version

* Sat Oct 11 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-3
- Fix a typo in librados-devel vs librados2-devel dependency

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-2
- Provide empty file list for python-ceph-compat and ceph-devel-compat

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-1
- Rebase to 0.80.6
- Split ceph-devel and python-ceph packages

* Tue Sep 9 2014 Dan Horák <dan[at]danny.cz> - 1:0.80.5-10
- update Requires for s390(x)

* Wed Sep 3 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-9
- Symlink librd.so.1 to /usr/lib64/qemu only on rhel6+ x86_64 (1136811)

* Thu Aug 21 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-8
- Revert the previous change
- Fix bz 1118504, second attempt (yasm appears to be the package that caused this
- Fix bogus dates

* Wed Aug 20 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-7
- Several more merges from file to try to fix the selinux issue (1118504)

* Sun Aug 17 2014 Kalev Lember <kalevlember@gmail.com> - 1:0.80.5-6
- Obsolete ceph-libcephfs

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-5
- Do not require xfsprogs/xfsprogs-devel for el6
- Require gperftools-devel for non-ppc*/s390* architectures only
- Do not require junit -- no need to build libcephfs-test.jar
- Build without libxfs for el6
- Build without tcmalloc for ppc*/s390* architectures
- Location of mkcephfs must depend on a rhel release
- Use epoch in the Requires fields [1130700]

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-4
- Use the proper version name in Obsoletes

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.80.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-2
- Add the arm pthread hack

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-1
- Bump the Epoch, we need to keep the latest stable, not development, ceph version in fedora
- Use the upstream spec file with the ceph-libs split
- Add libs-compat subpackage [1116546]
- use fedora in rhel 7 checks
- obsolete libcephfs [1116614]
- depend on redhat-lsb-core for the initscript [1108696]

* Wed Aug 13 2014 Kalev Lember <kalevlember@gmail.com> - 0.81.0-6
- Add obsoletes to keep the upgrade path working (#1118510)

* Mon Jul 7 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-5
- revert to old spec until after f21 branch

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- temporary exclude f21/armv7hl. N.B. it builds fine on f20/armv7hl.

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-4
- upstream ceph.spec file

* Tue Jul 1 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-3
- upstream ceph.spec file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.81.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 likewise for tcmalloc, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 does not have gperftools, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-1
- ceph-0.81.0

* Wed Jun  4 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.80.1-5
- gperftools now available on aarch64/ppc64

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 0.80.1-4
- Rebuild for boost 1.55.0

* Fri May 23 2014 David Tardon <dtardon@redhat.com> - 0.80.1-3
- rebuild for boost 1.55.0

* Wed May 14 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-2
- build epel-6
- exclude %%{_libdir}/ceph/erasure-code in base package

* Tue May 13 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-1
- Update to latest stable upstream release, BZ 1095201
- PIE, _hardened_build, BZ 955174

* Thu Feb 06 2014 Ken Dreyer <ken.dreyer@inktank.com> - 0.72.2-2
- Move plugins from -devel into -libs package (#891993). Thanks Michael
  Schwendt.

* Mon Jan 06 2014 Ken Dreyer <ken.dreyer@inktank.com> 0.72.2-1
- Update to latest stable upstream release
- Use HTTPS for URLs
- Submit Automake 1.12 patch upstream
- Move unversioned shared libs from ceph-libs into ceph-devel

* Wed Dec 18 2013 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> 0.67.3-4
- build without tcmalloc on aarch64 (no gperftools)

* Sat Nov 30 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.67.3-3
- gperftools not currently available on aarch64

* Mon Oct 07 2013 Dan Horák <dan[at]danny.cz> - 0.67.3-2
- fix build on non-x86_64 64-bit arches

* Wed Sep 11 2013 Josef Bacik <josef@toxicpanda.com> - 0.67.3-1
- update to 0.67.3

* Wed Sep 11 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.61.7-3
- let base package include all its documentation files via %%doc magic,
  so for Fedora 20 Unversioned Docdirs no files are included accidentally
- include the sample config files again (instead of just an empty docdir
  that has been added for #846735)
- don't include librbd.so.1 also in -devel package (#1003202)
- move one misplaced rados plugin from -devel into -libs package (#891993)
- include missing directories in -devel and -libs packages
- move librados-config into the -devel pkg where its manual page is, too
- add %%_isa to subpackage dependencies
- don't use %%defattr anymore
- add V=1 to make invocation for verbose build output

* Wed Jul 31 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.61.7-2
- re-enable tmalloc on arm now gperftools is fixed

* Mon Jul 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.61.7-1
- Update to 0.61.7

* Sat Jul 27 2013 pmachata@redhat.com - 0.56.4-2
- Rebuild for boost 1.54.0

* Fri Mar 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.4-1
- Update to 0.56.4
- Add upstream d02340d90c9d30d44c962bea7171db3fe3bfba8e to fix logrotate

* Wed Feb 20 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.3-1
- Update to 0.56.3

* Mon Feb 11 2013 Richard W.M. Jones <rjones@redhat.com> - 0.53-2
- Rebuilt to try to fix boost dependency problem in Rawhide.

* Thu Nov  1 2012 Josef Bacik <josef@toxicpanda.com> - 0.53-1
- Update to 0.53

* Mon Sep 24 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-3
- Fix automake 1.12 error
- Rebuild after buildroot was messed up

* Tue Sep 18 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-2
- Use system leveldb

* Fri Sep 07 2012 David Nalley <david@gnsa.us> - 0.51-1
- Updating to 0.51
- Updated url and source url.

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.46-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  9 2012 Josef Bacik <josef@toxicpanda.com> - 0.46-1
- updated to upstream 0.46
- broke out libcephfs (rhbz# 812975)

* Mon Apr 23 2012 Dan Horák <dan[at]danny.cz> - 0.45-2
- fix detection of C++11 atomic header

* Thu Apr 12 2012 Josef Bacik <josef@toxicpanda.com> - 0.45-1
- updating to upstream 0.45

* Wed Apr  4 2012 Niels de Vos <devos@fedoraproject.org> - 0.44-5
- Add LDFLAGS=-lpthread on any ARM architecture
- Add CFLAGS=-DAO_USE_PTHREAD_DEFS on ARMv5tel

* Mon Mar 26 2012 Dan Horák <dan[at]danny.cz> 0.44-4
- gperftools not available also on ppc

* Mon Mar 26 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-3
- Remove unneeded patch

* Sun Mar 25 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-2
- Update to 0.44
- Fix build problems

* Mon Mar  5 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.43-1
- Update to 0.43
- Remove upstreamed compile fixes patch
- Remove obsoleted dump_pop patch

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.41-2
- Rebuilt for c++ ABI breakage

* Thu Feb 16 2012 Tom Callaway <spot@fedoraproject.org> 0.41-1
- update to 0.41
- fix issues preventing build
- rebuild against gperftools

* Sat Dec 03 2011 David Nalley <david@gnsa.us> 0.38-1
- updating to upstream 0.39

* Sat Nov 05 2011 David Nalley <david@gnsa.us> 0.37-1
- create /etc/ceph - bug 745462
- upgrading to 0.37, fixing 745460, 691033
- fixing various logrotate bugs 748930, 747101

* Fri Aug 19 2011 Dan Horák <dan[at]danny.cz> 0.31-4
- google-perftools not available also on s390(x)

* Mon Jul 25 2011 Karsten Hopp <karsten@redhat.com> 0.31-3
- build without tcmalloc on ppc64, BR google-perftools is not available there

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-2
- Remove curl/types.h include since we don't use it anymore

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-1
- Update to 0.31

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26-2
- Add the compile fix patch

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26
- Update to 0.26

* Tue Mar 22 2011 Josef Bacik <josef@toxicpanda.com> 0.25.1-1
- Update to 0.25.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 Steven Pritchard <steve@kspei.com> 0.21.3-1
- Update to 0.21.3.

* Mon Aug 30 2010 Steven Pritchard <steve@kspei.com> 0.21.2-1
- Update to 0.21.2.

* Thu Aug 26 2010 Steven Pritchard <steve@kspei.com> 0.21.1-1
- Update to 0.21.1.
- Sample configs moved to /usr/share/doc/ceph/.
- Added cclass, rbd, and cclsinfo.
- Dropped mkmonfs and rbdtool.
- mkcephfs moved to /sbin.
- Add libcls_rbd.so.

* Tue Jul  6 2010 Josef Bacik <josef@toxicpanda.com> 0.20.2-1
- update to 0.20.2

* Wed May  5 2010 Josef Bacik <josef@toxicpanda.com> 0.20-1
- update to 0.20
- disable hadoop building
- remove all the test binaries properly

* Fri Apr 30 2010 Sage Weil <sage@newdream.net> 0.19.1-5
- Remove java deps (no need to build hadoop by default)
- Include all required librados helpers
- Include fetch_config sample
- Include rbdtool
- Remove misc debugging, test binaries

* Fri Apr 30 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-4
- Add java-devel and java tricks to get hadoop to build

* Mon Apr 26 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-3
- Move the rados and cauthtool man pages into the base package

* Sun Apr 25 2010 Jonathan Dieter <jdieter@lesbg.com> 0.19.1-2
- Add missing libhadoopcephfs.so* to file list
- Add COPYING to all subpackages
- Fix ownership of /usr/lib[64]/ceph
- Enhance description of fuse client

* Tue Apr 20 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-1
- Update to 0.19.1

* Mon Feb  8 2010 Josef Bacik <josef@toxicpanda.com> 0.18-1
- Initial spec file creation, based on the template provided in the ceph src
