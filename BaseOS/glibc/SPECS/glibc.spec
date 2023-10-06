%define glibcsrcdir glibc-2.34
%define glibcversion 2.34
# Pre-release tarballs are pulled in from git using a command that is
# effectively:
#
# git archive HEAD --format=tar --prefix=$(git describe --match 'glibc-*')/ \
#	> $(git describe --match 'glibc-*').tar
# gzip -9 $(git describe --match 'glibc-*').tar
#
# glibc_release_url is only defined when we have a release tarball.
# Conversly, glibc_autorequires is set for development snapshots, where
# dependencies based on symbol versions are inaccurate.
%{lua: if string.match(rpm.expand("%glibcsrcdir"), "^glibc%-[0-9.]+$") then
    rpm.define("glibc_release_url https://ftp.gnu.org/gnu/glibc/")
  end
  local major, minor = string.match(rpm.expand("%glibcversion"),
                                    "^([0-9]+)%.([0-9]+)%.9000$")
  if major and minor then
    rpm.define("glibc_autorequires 1")
    -- The minor version in a .9000 development version lags the actual
    -- symbol version by one.
    local symver = "GLIBC_" .. major .. "." .. (minor + 1)
    rpm.define("glibc_autorequires_symver " .. symver)
  else
    rpm.define("glibc_autorequires 0")
  end}
##############################################################################
# We support the following options:
# --with/--without,
# * testsuite - Running the testsuite.
# * benchtests - Running and building benchmark subpackage.
# * bootstrap - Bootstrapping the package.
# * werror - Build with -Werror
# * docs - Build with documentation and the required dependencies.
# * valgrind - Run smoke tests with valgrind to verify dynamic loader.
#
# You must always run the testsuite for production builds.
# Default: Always run the testsuite.
%bcond_without testsuite
# Default: Always build the benchtests.
%bcond_without benchtests
# Default: Not bootstrapping.
%bcond_with bootstrap
# Default: Enable using -Werror
%bcond_without werror
# Default: Always build documentation.
%bcond_without docs

# Default: Always run valgrind tests if there is architecture support.
%ifarch %{valgrind_arches}
%bcond_without valgrind
%else
%bcond_with valgrind
%endif
# Restrict %%{valgrind_arches} further in case there are problems with
# the smoke test.
%if %{with valgrind}
%ifarch ppc64 ppc64p7
# The valgrind smoke test does not work on ppc64, ppc64p7 (bug 1273103).
%undefine with_valgrind
%endif
%endif

%if %{with bootstrap}
# Disable benchtests, -Werror, docs, and valgrind if we're bootstrapping
%undefine with_benchtests
%undefine with_werror
%undefine with_docs
%undefine with_valgrind
%endif

# Build the POWER10 runtime on POWER, but only for downstream.
%ifarch ppc64le
%define buildpower10 0%{?rhel} > 0
%else
%define buildpower10 0
%endif

# The annobin annotations cause binutils to produce broken ARM EABI
# unwinding information.  Symptom is a hang/test failure for
# malloc/tst-malloc-stats-cancellation.  See
# <https://bugzilla.redhat.com/show_bug.cgi?id=1951492>.
%ifarch armv7hl
%undefine _annotated_build
%endif

##############################################################################
# Any architecture/kernel combination that supports running 32-bit and 64-bit
# code in userspace is considered a biarch arch.
%define biarcharches %{ix86} x86_64 s390 s390x

# Avoid generating a glibc-headers package on architectures which are
# not biarch.
%ifarch %{biarcharches}
%define need_headers_package 1
%if 0%{?rhel} > 0
%define headers_package_name glibc-headers
%else
%ifarch %{ix86} x86_64
%define headers_package_name glibc-headers-x86
%endif
%ifarch s390 s390x
%define headers_package_name glibc-headers-s390
%endif
%dnl !rhel
%endif
%else
%define need_headers_package 0
%dnl !biarcharches
%endif

##############################################################################
# Utility functions for pre/post scripts.  Stick them at the beginning of
# any lua %pre, %post, %postun, etc. sections to have them expand into
# those scripts.  It only works in lua sections and not anywhere else.
%define glibc_post_funcs() \
-- We use lua posix.exec because there may be no shell that we can \
-- run during glibc upgrade.  We used to implement much of %%post as a \
-- C program, but from an overall maintenance perspective the lua in \
-- the spec file was simpler and safer given the operations required. \
-- All lua code will be ignored by rpm-ostree; see: \
-- https://github.com/projectatomic/rpm-ostree/pull/1869 \
-- If we add new lua actions to the %%post code we should coordinate \
-- with rpm-ostree and ensure that their glibc install is functional. \
function post_exec (program, ...) \
  local pid = posix.fork () \
  if pid == 0 then \
    posix.exec (program, ...) \
    assert (nil) \
  elseif pid > 0 then \
    posix.wait (pid) \
  end \
end \
\
function update_gconv_modules_cache () \
  local iconv_dir = "%{_libdir}/gconv" \
  local iconv_cache = iconv_dir .. "/gconv-modules.cache" \
  local iconv_modules = iconv_dir .. "/gconv-modules" \
  if (posix.utime (iconv_modules) == 0) then \
    if (posix.utime (iconv_cache) == 0) then \
      post_exec ("%{_prefix}/sbin/iconvconfig", \
		 "-o", iconv_cache, \
		 "--nostdlib", \
		 iconv_dir) \
    else \
      io.stdout:write ("Error: Missing " .. iconv_cache .. " file.\n") \
    end \
  end \
end \
%{nil}

##############################################################################
# %%package glibc - The GNU C Library (glibc) core package.
##############################################################################
Summary: The GNU libc libraries
Name: glibc
Version: %{glibcversion}
Release: 60%{?dist}.7

# In general, GPLv2+ is used by programs, LGPLv2+ is used for
# libraries.
#
# LGPLv2+ with exceptions is used for things that are linked directly
# into dynamically linked programs and shared libraries (e.g. crt
# files, lib*_nonshared.a).  Historically, this exception also applies
# to parts of libio.
#
# GPLv2+ with exceptions is used for parts of the Arm unwinder.
#
# GFDL is used for the documentation.
#
# Some other licenses are used in various places (BSD, Inner-Net,
# ISC, Public Domain).
#
# HSRL and FSFAP are only used in test cases, which currently do not
# ship in binary RPMs, so they are not listed here.  MIT is used for
# scripts/install-sh, which does not ship, either.
#
# GPLv3+ is used by manual/texinfo.tex, which we do not use.
#
# LGPLv3+ is used by some Hurd code, which we do not build.
#
# LGPLv2 is used in one place (time/timespec_get.c, by mistake), but
# it is not actually compiled, so it does not matter for libraries.
License: LGPLv2+ and LGPLv2+ with exceptions and GPLv2+ and GPLv2+ with exceptions and BSD and Inner-Net and ISC and Public Domain and GFDL

URL: http://www.gnu.org/software/glibc/
Source0: %{?glibc_release_url}%{glibcsrcdir}.tar.xz
Source1: nscd.conf
Source2: bench.mk
Source3: glibc-bench-compare
Source4: glibc.req.in
Source5: glibc.attr
Source10: wrap-find-debuginfo.sh
Source11: parse-SUPPORTED.py
# Include in the source RPM for reference.
Source12: ChangeLog.old

######################################################################
# Activate the wrapper script for debuginfo generation, by rewriting
# the definition of __debug_install_post.
%{lua:
local wrapper = rpm.expand("%{SOURCE10}")
local sysroot = rpm.expand("%{glibc_sysroot}")
local original = rpm.expand("%{macrobody:__debug_install_post}")
-- Strip leading newline.  It confuses the macro redefinition.
-- Avoid embedded newlines that confuse the macro definition.
original = original:match("^%s*(.-)%s*$"):gsub("\\\n", "")
rpm.define("__debug_install_post bash " .. wrapper
  .. " " .. sysroot .. " " .. original)
}

# sysroot package support.  These contain arch-specific packages, so
# turn off the rpmbuild check.
%global _binaries_in_noarch_packages_terminate_build 0
# Variant of %%dist that contains just the distribution release, no affixes.
%{?fedora:%global sysroot_dist fc%{fedora}}
%{?rhel:%global sysroot_dist el%{rhel}}
%{?!sysroot_dist:%global sysroot_dist root}
# The name of the sysroot package.
%global sysroot_package_arch sysroot-%{_arch}-%{sysroot_dist}-%{name}
# Installed path for the sysroot tree.  Must contain /sys-root/, which
# triggers filtering.
%global sysroot_prefix /usr/%{_arch}-redhat-linux/sys-root/%{sysroot_dist}

# The wrapper script relies on the fact that debugedit does not change
# build IDs.
%define _no_recompute_build_ids 1
%undefine _unique_build_ids

##############################################################################
# Patches:
# - See each individual patch file for origin and upstream status.
# - For new patches follow template.patch format.
##############################################################################
Patch1: glibc-fedora-nscd.patch
Patch4: glibc-fedora-linux-tcsetattr.patch
Patch8: glibc-fedora-manual-dircategory.patch
Patch9: glibc-rh827510.patch
Patch13: glibc-fedora-localedata-rh61908.patch
Patch15: glibc-rh1070416.patch
Patch16: glibc-nscd-sysconfig.patch
Patch17: glibc-cs-path.patch
Patch18: glibc-c-utf8-locale-1.patch
Patch19: glibc-c-utf8-locale-2.patch
Patch23: glibc-python3.patch
Patch29: glibc-fedora-nsswitch.patch
Patch30: glibc-deprecated-selinux-makedb.patch
Patch31: glibc-deprecated-selinux-nscd.patch
Patch32: glibc-upstream-2.34-1.patch
Patch33: glibc-upstream-2.34-2.patch
Patch34: glibc-upstream-2.34-3.patch
Patch35: glibc-upstream-2.34-4.patch
Patch36: glibc-upstream-2.34-5.patch
Patch37: glibc-upstream-2.34-6.patch
Patch38: glibc-upstream-2.34-7.patch
Patch39: glibc-upstream-2.34-8.patch
Patch40: glibc-upstream-2.34-9.patch
Patch41: glibc-upstream-2.34-10.patch
Patch42: glibc-upstream-2.34-11.patch
Patch43: glibc-upstream-2.34-12.patch
Patch44: glibc-upstream-2.34-13.patch
Patch45: glibc-upstream-2.34-14.patch
Patch46: glibc-upstream-2.34-15.patch
Patch47: glibc-upstream-2.34-16.patch
Patch48: glibc-upstream-2.34-17.patch
Patch49: glibc-upstream-2.34-18.patch
Patch50: glibc-upstream-2.34-19.patch
Patch51: glibc-upstream-2.34-20.patch
Patch52: glibc-upstream-2.34-21.patch
Patch53: glibc-upstream-2.34-22.patch
Patch54: glibc-upstream-2.34-23.patch
Patch55: glibc-upstream-2.34-24.patch
Patch56: glibc-upstream-2.34-25.patch
Patch57: glibc-upstream-2.34-26.patch
Patch58: glibc-upstream-2.34-27.patch
Patch59: glibc-upstream-2.34-28.patch
Patch60: glibc-upstream-2.34-29.patch
Patch61: glibc-upstream-2.34-30.patch
Patch62: glibc-upstream-2.34-31.patch
Patch63: glibc-upstream-2.34-32.patch
Patch64: glibc-upstream-2.34-33.patch
Patch65: glibc-upstream-2.34-34.patch
Patch66: glibc-upstream-2.34-35.patch
Patch67: glibc-upstream-2.34-36.patch
Patch68: glibc-upstream-2.34-37.patch
Patch69: glibc-upstream-2.34-38.patch
Patch70: glibc-upstream-2.34-39.patch
Patch71: glibc-upstream-2.34-40.patch
Patch72: glibc-upstream-2.34-41.patch
Patch73: glibc-upstream-2.34-42.patch
Patch74: glibc-upstream-2.34-43.patch
Patch75: glibc-upstream-2.34-44.patch
Patch76: glibc-upstream-2.34-45.patch
Patch77: glibc-upstream-2.34-46.patch
Patch78: glibc-upstream-2.34-47.patch
Patch79: glibc-upstream-2.34-48.patch
Patch80: glibc-upstream-2.34-49.patch
Patch81: glibc-rh2027789.patch
Patch82: glibc-rh2023422-1.patch
Patch83: glibc-rh2023422-2.patch
Patch84: glibc-rh2023422-3.patch
Patch85: glibc-rh2029410.patch
Patch86: glibc-upstream-2.34-50.patch
Patch87: glibc-upstream-2.34-51.patch
Patch88: glibc-upstream-2.34-52.patch
Patch89: glibc-upstream-2.34-53.patch
Patch90: glibc-rh1988382.patch
Patch91: glibc-upstream-2.34-54.patch
Patch92: glibc-upstream-2.34-55.patch
Patch93: glibc-upstream-2.34-56.patch
Patch94: glibc-upstream-2.34-57.patch
Patch95: glibc-upstream-2.34-58.patch
Patch96: glibc-upstream-2.34-59.patch
Patch97: glibc-upstream-2.34-60.patch
Patch98: glibc-upstream-2.34-61.patch
Patch99: glibc-upstream-2.34-62.patch
Patch100: glibc-upstream-2.34-63.patch
Patch101: glibc-upstream-2.34-64.patch
Patch102: glibc-upstream-2.34-65.patch
Patch103: glibc-upstream-2.34-66.patch
Patch104: glibc-upstream-2.34-67.patch
Patch105: glibc-upstream-2.34-68.patch
Patch106: glibc-upstream-2.34-69.patch
Patch107: glibc-upstream-2.34-70.patch
Patch108: glibc-upstream-2.34-71.patch
Patch109: glibc-upstream-2.34-72.patch
Patch110: glibc-upstream-2.34-73.patch
Patch111: glibc-rh2032647-1.patch
Patch112: glibc-rh2032647-2.patch
Patch113: glibc-rh2032647-3.patch
Patch114: glibc-rh2032647-4.patch
Patch115: glibc-rh2032647-5.patch
Patch116: glibc-rh2032647-6.patch
Patch117: glibc-rh2024347-1.patch
Patch118: glibc-rh2024347-2.patch
Patch119: glibc-rh2024347-3.patch
Patch120: glibc-rh2024347-4.patch
Patch121: glibc-rh2024347-5.patch
Patch122: glibc-rh2024347-6.patch
Patch123: glibc-rh2024347-7.patch
Patch124: glibc-rh2024347-8.patch
Patch125: glibc-rh2024347-9.patch
Patch126: glibc-rh2024347-10.patch
Patch127: glibc-rh2024347-11.patch
Patch128: glibc-rh2024347-12.patch
Patch129: glibc-rh2024347-13.patch
Patch130: glibc-rh2040657-1.patch
Patch131: glibc-rh2040657-2.patch
Patch132: glibc-rh2040657-3.patch
Patch133: glibc-rh2040657-4.patch
Patch134: glibc-rh2040657-5.patch
Patch135: glibc-rh2040657-6.patch
Patch136: glibc-rh2040657-7.patch
Patch137: glibc-rh2040657-8.patch
Patch138: glibc-rh2040657-9.patch
Patch139: glibc-rh2040657-10.patch
Patch140: glibc-rh2040657-11.patch
Patch141: glibc-rh2040657-12.patch
Patch142: glibc-upstream-2.34-74.patch
Patch143: glibc-upstream-2.34-75.patch
Patch144: glibc-upstream-2.34-76.patch
Patch145: glibc-upstream-2.34-77.patch
Patch146: glibc-upstream-2.34-78.patch
Patch147: glibc-upstream-2.34-79.patch
Patch148: glibc-upstream-2.34-80.patch
Patch149: glibc-upstream-2.34-81.patch
Patch150: glibc-upstream-2.34-82.patch
Patch151: glibc-upstream-2.34-83.patch
Patch152: glibc-upstream-2.34-84.patch
Patch153: glibc-upstream-2.34-85.patch
Patch154: glibc-upstream-2.34-86.patch
Patch155: glibc-upstream-2.34-87.patch
Patch156: glibc-upstream-2.34-88.patch
Patch157: glibc-upstream-2.34-89.patch
# glibc-2.34-90-g1b9cd6a721 only changes NEWS.
Patch158: glibc-upstream-2.34-91.patch
Patch159: glibc-upstream-2.34-92.patch
# glibc-2.34-93-g72123e1b56 only changes NEWS.
# glibc-2.34-94-g31186e2cb7 is glibc-rh2040657-1.patch.
# glibc-2.34-95-g511b244cc5 is glibc-rh2040657-2.patch.
# glibc-2.34-96-gde6cdd6875 is glibc-rh2040657-6.patch.
Patch160: glibc-upstream-2.34-97.patch
Patch161: glibc-upstream-2.34-98.patch
Patch162: glibc-upstream-2.34-99.patch
Patch163: glibc-c-utf8-locale-3.patch
Patch164: glibc-c-utf8-locale-4.patch
Patch165: glibc-c-utf8-locale-5.patch
Patch166: glibc-upstream-2.34-100.patch
Patch167: glibc-upstream-2.34-101.patch
Patch168: glibc-upstream-2.34-102.patch
Patch169: glibc-upstream-2.34-103.patch
Patch170: glibc-upstream-2.34-104.patch
Patch171: glibc-upstream-2.34-105.patch
Patch172: glibc-upstream-2.34-106.patch
Patch173: glibc-upstream-2.34-107.patch
Patch174: glibc-rh2058224-1.patch
Patch175: glibc-rh2058224-2.patch
Patch176: glibc-rh2058230.patch
Patch177: glibc-rh2054789.patch
Patch178: glibc-upstream-2.34-108.patch
# glibc-2.34-109-gd64b08d5ba only changes NEWS.
Patch179: glibc-upstream-2.34-110.patch
Patch180: glibc-upstream-2.34-111.patch
Patch181: glibc-upstream-2.34-112.patch
Patch182: glibc-upstream-2.34-113.patch
Patch183: glibc-upstream-2.34-114.patch
# glibc-2.34-115-gd5d1c95aaf only changes NEWS.
# glibc-2.34-116-g852361b5a3 is glibc-rh2054789.patch.
Patch184: glibc-upstream-2.34-117.patch
Patch185: glibc-upstream-2.34-118.patch
Patch186: glibc-upstream-2.34-119.patch
Patch187: glibc-upstream-2.34-120.patch
Patch188: glibc-upstream-2.34-121.patch
Patch189: glibc-upstream-2.34-122.patch
Patch190: glibc-upstream-2.34-123.patch
Patch191: glibc-upstream-2.34-124.patch
Patch192: glibc-upstream-2.34-125.patch
Patch193: glibc-upstream-2.34-126.patch
Patch194: glibc-upstream-2.34-127.patch
Patch195: glibc-upstream-2.34-128.patch
Patch196: glibc-upstream-2.34-129.patch
Patch197: glibc-upstream-2.34-130.patch
Patch198: glibc-upstream-2.34-131.patch
Patch199: glibc-upstream-2.34-132.patch
Patch200: glibc-upstream-2.34-133.patch
Patch201: glibc-upstream-2.34-134.patch
Patch202: glibc-upstream-2.34-135.patch
Patch203: glibc-upstream-2.34-136.patch
Patch204: glibc-upstream-2.34-137.patch
Patch205: glibc-upstream-2.34-138.patch
Patch206: glibc-upstream-2.34-139.patch
Patch207: glibc-upstream-2.34-140.patch
Patch208: glibc-upstream-2.34-141.patch
Patch209: glibc-upstream-2.34-142.patch
Patch210: glibc-upstream-2.34-143.patch
Patch211: glibc-upstream-2.34-144.patch
Patch212: glibc-upstream-2.34-145.patch
Patch213: glibc-upstream-2.34-146.patch
Patch214: glibc-upstream-2.34-147.patch
Patch215: glibc-upstream-2.34-148.patch
Patch216: glibc-upstream-2.34-149.patch
Patch217: glibc-upstream-2.34-150.patch
Patch218: glibc-upstream-2.34-151.patch
Patch219: glibc-upstream-2.34-152.patch
Patch220: glibc-upstream-2.34-153.patch
Patch221: glibc-upstream-2.34-154.patch
Patch222: glibc-upstream-2.34-155.patch
Patch223: glibc-upstream-2.34-156.patch
Patch224: glibc-upstream-2.34-157.patch
Patch225: glibc-upstream-2.34-158.patch
Patch226: glibc-upstream-2.34-159.patch
Patch227: glibc-upstream-2.34-160.patch
# glibc-2.34-161-gceed89d089 only changes NEWS.
Patch228: glibc-upstream-2.34-162.patch
Patch229: glibc-upstream-2.34-163.patch
Patch230: glibc-upstream-2.34-164.patch
Patch231: glibc-upstream-2.34-165.patch
Patch232: glibc-upstream-2.34-166.patch
Patch233: glibc-upstream-2.34-167.patch
Patch234: glibc-upstream-2.34-168.patch
Patch235: glibc-upstream-2.34-169.patch
Patch236: glibc-upstream-2.34-170.patch
Patch237: glibc-upstream-2.34-171.patch
Patch238: glibc-upstream-2.34-172.patch
Patch239: glibc-upstream-2.34-173.patch
Patch240: glibc-upstream-2.34-174.patch
Patch241: glibc-upstream-2.34-175.patch
Patch242: glibc-upstream-2.34-176.patch
Patch243: glibc-upstream-2.34-177.patch
Patch244: glibc-upstream-2.34-178.patch
Patch245: glibc-upstream-2.34-179.patch
Patch246: glibc-upstream-2.34-180.patch
Patch247: glibc-upstream-2.34-181.patch
Patch248: glibc-upstream-2.34-182.patch
Patch249: glibc-upstream-2.34-183.patch
Patch250: glibc-upstream-2.34-184.patch
Patch251: glibc-upstream-2.34-185.patch
Patch252: glibc-upstream-2.34-186.patch
Patch253: glibc-upstream-2.34-187.patch
Patch254: glibc-upstream-2.34-188.patch
Patch255: glibc-upstream-2.34-189.patch
Patch256: glibc-upstream-2.34-190.patch
Patch257: glibc-upstream-2.34-191.patch
Patch258: glibc-upstream-2.34-192.patch
Patch259: glibc-upstream-2.34-193.patch
Patch260: glibc-upstream-2.34-194.patch
Patch261: glibc-upstream-2.34-195.patch
Patch262: glibc-upstream-2.34-196.patch
Patch263: glibc-upstream-2.34-197.patch
Patch264: glibc-upstream-2.34-198.patch
Patch265: glibc-upstream-2.34-199.patch
Patch266: glibc-upstream-2.34-200.patch
Patch267: glibc-upstream-2.34-201.patch
Patch268: glibc-upstream-2.34-202.patch
Patch269: glibc-upstream-2.34-203.patch
Patch270: glibc-upstream-2.34-204.patch
Patch271: glibc-upstream-2.34-205.patch
Patch272: glibc-upstream-2.34-206.patch
Patch273: glibc-upstream-2.34-207.patch
Patch274: glibc-upstream-2.34-208.patch
Patch275: glibc-upstream-2.34-209.patch
Patch276: glibc-upstream-2.34-210.patch
Patch277: glibc-upstream-2.34-211.patch
Patch278: glibc-upstream-2.34-212.patch
Patch279: glibc-upstream-2.34-213.patch
Patch280: glibc-upstream-2.34-214.patch
Patch281: glibc-upstream-2.34-215.patch
Patch282: glibc-upstream-2.34-216.patch
Patch283: glibc-upstream-2.34-217.patch
Patch284: glibc-upstream-2.34-218.patch
Patch285: glibc-upstream-2.34-219.patch
Patch286: glibc-upstream-2.34-220.patch
Patch287: glibc-upstream-2.34-221.patch
Patch288: glibc-upstream-2.34-222.patch
Patch289: glibc-upstream-2.34-223.patch
Patch290: glibc-upstream-2.34-224.patch
Patch291: glibc-upstream-2.34-225.patch
Patch292: glibc-upstream-2.34-226.patch
Patch293: glibc-upstream-2.34-227.patch
Patch294: glibc-upstream-2.34-228.patch
Patch295: glibc-upstream-2.34-229.patch
Patch296: glibc-upstream-2.34-230.patch
Patch297: glibc-upstream-2.34-231.patch
Patch298: glibc-upstream-2.34-232.patch
Patch299: glibc-upstream-2.34-233.patch
Patch300: glibc-upstream-2.34-234.patch
Patch301: glibc-upstream-2.34-235.patch
Patch302: glibc-upstream-2.34-236.patch
Patch303: glibc-upstream-2.34-237.patch
Patch304: glibc-upstream-2.34-238.patch
Patch305: glibc-upstream-2.34-239.patch
Patch306: glibc-upstream-2.34-240.patch
Patch307: glibc-upstream-2.34-241.patch
Patch308: glibc-upstream-2.34-242.patch
Patch309: glibc-upstream-2.34-243.patch
Patch310: glibc-upstream-2.34-244.patch
Patch311: glibc-upstream-2.34-245.patch
Patch312: glibc-upstream-2.34-246.patch
Patch313: glibc-upstream-2.34-247.patch
Patch314: glibc-upstream-2.34-248.patch
Patch315: glibc-upstream-2.34-249.patch
Patch316: glibc-upstream-2.34-250.patch
Patch317: glibc-upstream-2.34-251.patch
Patch318: glibc-upstream-2.34-252.patch
Patch319: glibc-upstream-2.34-253.patch
Patch320: glibc-upstream-2.34-254.patch
Patch321: glibc-upstream-2.34-255.patch
Patch322: glibc-upstream-2.34-256.patch
Patch323: glibc-upstream-2.34-257.patch
Patch324: glibc-upstream-2.34-258.patch
Patch325: glibc-upstream-2.34-259.patch
Patch326: glibc-upstream-2.34-260.patch
Patch327: glibc-upstream-2.34-261.patch
Patch328: glibc-upstream-2.34-262.patch
Patch329: glibc-upstream-2.34-263.patch
Patch330: glibc-upstream-2.34-264.patch
Patch331: glibc-upstream-2.34-265.patch
Patch332: glibc-upstream-2.34-266.patch
Patch333: glibc-upstream-2.34-267.patch
Patch334: glibc-upstream-2.34-268.patch
Patch335: glibc-rh2085529-1.patch
Patch336: glibc-rh2085529-2.patch
Patch337: glibc-rh2085529-3.patch
Patch338: glibc-rh2085529-4.patch
Patch339: glibc-upstream-2.34-269.patch
Patch340: glibc-upstream-2.34-270.patch
Patch341: glibc-upstream-2.34-271.patch
Patch342: glibc-upstream-2.34-272.patch
Patch343: glibc-upstream-2.34-273.patch
Patch344: glibc-rh2096191-1.patch
Patch345: glibc-rh2096191-2.patch
Patch346: glibc-upstream-2.34-274.patch
Patch347: glibc-upstream-2.34-275.patch
Patch348: glibc-upstream-2.34-276.patch
Patch349: glibc-upstream-2.34-277.patch
Patch350: glibc-upstream-2.34-278.patch
Patch351: glibc-upstream-2.34-279.patch
Patch352: glibc-upstream-2.34-280.patch
Patch353: glibc-upstream-2.34-281.patch
Patch354: glibc-upstream-2.34-282.patch
Patch355: glibc-upstream-2.34-283.patch
Patch356: glibc-upstream-2.34-284.patch
Patch357: glibc-upstream-2.34-285.patch
Patch358: glibc-upstream-2.34-286.patch
Patch359: glibc-upstream-2.34-287.patch
Patch360: glibc-upstream-2.34-288.patch
Patch361: glibc-upstream-2.34-289.patch
Patch362: glibc-upstream-2.34-290.patch
Patch363: glibc-upstream-2.34-291.patch
Patch364: glibc-upstream-2.34-292.patch
Patch365: glibc-upstream-2.34-293.patch
Patch366: glibc-upstream-2.34-294.patch
Patch367: glibc-upstream-2.34-295.patch
Patch368: glibc-upstream-2.34-296.patch
Patch369: glibc-upstream-2.34-297.patch
Patch370: glibc-upstream-2.34-298.patch
Patch371: glibc-upstream-2.34-299.patch
Patch372: glibc-upstream-2.34-300.patch
Patch373: glibc-upstream-2.34-301.patch
Patch374: glibc-upstream-2.34-302.patch
Patch375: glibc-upstream-2.34-303.patch
Patch376: glibc-upstream-2.34-304.patch
Patch377: glibc-upstream-2.34-305.patch
Patch378: glibc-upstream-2.34-306.patch
Patch379: glibc-upstream-2.34-307.patch
Patch380: glibc-upstream-2.34-308.patch
Patch381: glibc-rh2118666.patch
Patch382: glibc-rh2128615-1.patch
Patch383: glibc-rh2128615-2.patch
Patch384: glibc-rh2128615-3.patch
Patch385: glibc-rh2117712-1.patch
Patch386: glibc-rh2117712-2.patch
Patch387: glibc-rh2117712-3.patch
Patch388: glibc-rh2117712-4.patch
Patch389: glibc-rh2117712-5.patch
Patch390: glibc-rh2117712-6.patch
Patch391: glibc-upstream-2.34-309.patch
Patch392: glibc-upstream-2.34-310.patch
Patch393: glibc-upstream-2.34-311.patch
Patch394: glibc-upstream-2.34-312.patch
# glibc-2.34-313-gbc5cb538e5 backported above as glibc-rh2118666.patch.
Patch395: glibc-upstream-2.34-314.patch
Patch396: glibc-upstream-2.34-315.patch
Patch397: glibc-upstream-2.34-316.patch
Patch398: glibc-upstream-2.34-317.patch
Patch399: glibc-upstream-2.34-318.patch
Patch400: glibc-upstream-2.34-319.patch
Patch401: glibc-upstream-2.34-320.patch
Patch402: glibc-upstream-2.34-321.patch
Patch403: glibc-upstream-2.34-322.patch
Patch404: glibc-upstream-2.34-323.patch
Patch405: glibc-upstream-2.34-324.patch
Patch406: glibc-upstream-2.34-325.patch
Patch407: glibc-upstream-2.34-326.patch
Patch408: glibc-upstream-2.34-327.patch
# glibc-2.34-328-g2def56a349 conflicts with glibc-rh2096191-2.patch;
# glibc-rh2129005.patch contains the original master branch commit instead.
Patch409: glibc-rh2129005.patch
Patch410: glibc-upstream-2.34-329.patch
Patch411: glibc-upstream-2.34-330.patch
Patch412: glibc-upstream-2.34-331.patch
Patch413: glibc-upstream-2.34-332.patch
Patch414: glibc-upstream-2.34-333.patch
Patch415: glibc-upstream-2.34-334.patch
Patch416: glibc-upstream-2.34-335.patch
Patch417: glibc-upstream-2.34-336.patch
Patch418: glibc-upstream-2.34-337.patch
Patch419: glibc-upstream-2.34-338.patch
Patch420: glibc-upstream-2.34-339.patch
Patch421: glibc-upstream-2.34-340.patch
Patch422: glibc-upstream-2.34-341.patch
Patch423: glibc-upstream-2.34-342.patch
Patch424: glibc-upstream-2.34-343.patch
Patch425: glibc-upstream-2.34-344.patch
Patch426: glibc-upstream-2.34-345.patch
Patch427: glibc-upstream-2.34-346.patch
Patch428: glibc-upstream-2.34-347.patch
Patch429: glibc-upstream-2.34-348.patch
Patch430: glibc-upstream-2.34-349.patch
Patch431: glibc-upstream-2.34-350.patch
Patch432: glibc-upstream-2.34-351.patch
Patch433: glibc-upstream-2.34-352.patch
Patch434: glibc-upstream-2.34-353.patch
Patch435: glibc-upstream-2.34-354.patch
Patch436: glibc-upstream-2.34-355.patch
Patch437: glibc-upstream-2.34-356.patch
Patch438: glibc-upstream-2.34-357.patch
Patch439: glibc-upstream-2.34-358.patch
Patch440: glibc-upstream-2.34-359.patch
# glibc-2.34-360-g75b0edb7ef only changes NEWS.
Patch441: glibc-upstream-2.34-361.patch
Patch442: glibc-upstream-2.34-362.patch
Patch443: glibc-upstream-2.34-363.patch
Patch444: glibc-upstream-2.34-364.patch
Patch445: glibc-upstream-2.34-365.patch
Patch446: glibc-rh2149102.patch
Patch447: glibc-upstream-2.34-366.patch
Patch448: glibc-upstream-2.34-367.patch
Patch449: glibc-upstream-2.34-368.patch
Patch450: glibc-upstream-2.34-369.patch
Patch451: glibc-upstream-2.34-370.patch
Patch452: glibc-upstream-2.34-371.patch
Patch453: glibc-upstream-2.34-372.patch
Patch454: glibc-upstream-2.34-373.patch
Patch455: glibc-upstream-2.34-374.patch
Patch456: glibc-upstream-2.34-375.patch
Patch457: glibc-upstream-2.34-376.patch
Patch458: glibc-upstream-2.34-377.patch
Patch459: glibc-upstream-2.34-378.patch
Patch460: glibc-upstream-2.34-379.patch
Patch461: glibc-upstream-2.34-380.patch
Patch462: glibc-upstream-2.34-381.patch
Patch463: glibc-upstream-2.34-382.patch
Patch464: glibc-upstream-2.34-383.patch
Patch465: glibc-upstream-2.34-384.patch
Patch466: glibc-rh2162962.patch
Patch467: glibc-upstream-2.34-385.patch
Patch468: glibc-upstream-2.34-386.patch
# glibc-upstream-2.34-387.patch is a NEWS-only update.  Skipped downstream.
Patch469: glibc-upstream-2.34-388.patch
Patch470: glibc-upstream-2.34-389.patch
# (Reverted fixes for RHEL-3385 were here.)
Patch476: glibc-rh2234715.patch
Patch477: glibc-RHEL-2437.patch
Patch478: glibc-RHEL-2425-1.patch
Patch479: glibc-RHEL-2425-2.patch
Patch480: glibc-RHEL-2425-3.patch
Patch481: glibc-RHEL-2425-4.patch
Patch482: glibc-RHEL-2425-5.patch
Patch483: glibc-RHEL-2425-6.patch
Patch484: glibc-RHEL-2425-7.patch
Patch485: glibc-RHEL-2425-8.patch
Patch486: glibc-RHEL-2425-9.patch
Patch487: glibc-RHEL-2425-10.patch
Patch488: glibc-RHEL-2425-11.patch
Patch489: glibc-RHEL-2425-12.patch
Patch490: glibc-RHEL-2425-13.patch
Patch491: glibc-RHEL-2425-14.patch
Patch492: glibc-RHEL-2999.patch
Patch493: glibc-RHEL-2425-15.patch
Patch494: glibc-RHEL-2425-16.patch

##############################################################################
# Continued list of core "glibc" package information:
##############################################################################
Obsoletes: glibc-profile < 2.4
Provides: ldconfig

# The dynamic linker supports DT_GNU_HASH
Provides: rtld(GNU_HASH)

# We need libgcc for cancellation support in POSIX threads.
Requires: libgcc%{_isa}

Requires: glibc-common = %{version}-%{release}

# Various components (regex, glob) have been imported from gnulib.
Provides: bundled(gnulib)

Requires(pre): basesystem
Requires: basesystem

%ifarch %{ix86}
# Automatically install the 32-bit variant if the 64-bit variant has
# been installed.  This covers the case when glibc.i686 is installed
# after nss_*.x86_64.  (See below for the other ordering.)
Recommends: (nss_db(x86-32) if nss_db(x86-64))
Recommends: (nss_hesiod(x86-32) if nss_hesiod(x86-64))
%endif

# This is for building auxiliary programs like memusage, nscd
# For initial glibc bootstraps it can be commented out
%if %{without bootstrap}
BuildRequires: gd-devel libpng-devel zlib-devel
%endif
%if %{with docs}
%endif
%if %{without bootstrap}
BuildRequires: libselinux-devel >= 1.33.4-3
%endif
BuildRequires: audit-libs-devel >= 1.1.3, sed >= 3.95, libcap-devel, gettext
# We need procps-ng (/bin/ps), util-linux (/bin/kill), and gawk (/bin/awk),
# but it is more flexible to require the actual programs and let rpm infer
# the packages. However, until bug 1259054 is widely fixed we avoid the
# following:
# BuildRequires: /bin/ps, /bin/kill, /bin/awk
# And use instead (which should be reverted some time in the future):
BuildRequires: procps-ng, util-linux, gawk
BuildRequires: systemtap-sdt-devel

%if %{with valgrind}
# Require valgrind for smoke testing the dynamic loader to make sure we
# have not broken valgrind.
BuildRequires: valgrind
%endif

# We use systemd rpm macros for nscd
BuildRequires: systemd

# We use python for the microbenchmarks and locale data regeneration
# from unicode sources (carried out manually). We choose python3
# explicitly because it supports both use cases.  On some
# distributions, python3 does not actually install /usr/bin/python3,
# so we also depend on python3-devel.
BuildRequires: python3 python3-devel

# This GCC version is needed for -fstack-clash-protection support.
BuildRequires: gcc >= 7.2.1-6
%define enablekernel 3.2
Conflicts: kernel < %{enablekernel}
%define target %{_target_cpu}-redhat-linux
%ifarch %{arm}
%define target %{_target_cpu}-redhat-linuxeabi
%endif
%ifarch ppc64le
%define target ppc64le-redhat-linux
%endif

# GNU make 4.0 introduced the -O option.
BuildRequires: make >= 4.0

# The intl subsystem generates a parser using bison.
BuildRequires: bison >= 2.7

# binutils 2.30-17 is needed for --generate-missing-build-notes.
BuildRequires: binutils >= 2.30-17

# Earlier releases have broken support for IRELATIVE relocations
Conflicts: prelink < 0.4.2

%if %{without bootstrap}
%if %{with testsuite}
# The testsuite builds static C++ binaries that require a C++ compiler,
# static C++ runtime from libstdc++-static, and lastly static glibc.
BuildRequires: gcc-c++
BuildRequires: libstdc++-static
# A configure check tests for the ability to create static C++ binaries
# before glibc is built and therefore we need a glibc-static for that
# check to pass even if we aren't going to use any of those objects to
# build the tests.
BuildRequires: glibc-static

# libidn2 (but not libidn2-devel) is needed for testing AI_IDN/NI_IDN.
BuildRequires: libidn2

# The testsuite runs mtrace, which is a perl script
BuildRequires: perl-interpreter
%endif
%endif

# Filter out all GLIBC_PRIVATE symbols since they are internal to
# the package and should not be examined by any other tool.
%global __filter_GLIBC_PRIVATE 1
%global __provides_exclude ^libc_malloc_debug\\.so.*$

# For language packs we have glibc require a virtual dependency
# "glibc-langpack" wich gives us at least one installed langpack.
# If no langpack providing 'glibc-langpack' was installed you'd
# get language-neutral support e.g. C, POSIX, and C.UTF-8 locales.
# In the past we used to install the glibc-all-langpacks by default
# but we no longer do this to minimize container and VM sizes.
# Today you must actively use the language packs infrastructure to
# install language support.
Requires: glibc-langpack = %{version}-%{release}
Suggests: glibc-minimal-langpack = %{version}-%{release}

# Suggest extra gconv modules so that they are installed by default but can be
# removed if needed to build a minimal OS image.
Recommends: glibc-gconv-extra%{_isa} = %{version}-%{release}
# Use redhat-rpm-config as a marker for a buildroot configuration, and
# unconditionally pull in glibc-gconv-extra in that case.
Requires: (glibc-gconv-extra%{_isa} = %{version}-%{release} if redhat-rpm-config)

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

######################################################################
# libnsl subpackage
######################################################################

%package -n libnsl
Summary: Legacy support library for NIS
Requires: %{name}%{_isa} = %{version}-%{release}

%description -n libnsl
This package provides the legacy version of libnsl library, for
accessing NIS services.

This library is provided for backwards compatibility only;
applications should use libnsl2 instead to gain IPv6 support.

##############################################################################
# glibc "devel" sub-package
##############################################################################
%package devel
Summary: Object files for development using standard C libraries.
Requires: %{name} = %{version}-%{release}
Requires: libxcrypt-devel%{_isa} >= 4.0.0
Requires: kernel-headers >= 3.2
BuildRequires: kernel-headers >= 3.2
%if %{need_headers_package}
Requires: %{headers_package_name} = %{version}-%{release}
%endif
%if !(0%{?rhel} > 0 && %{need_headers_package})
# For backwards compatibility, when the glibc-headers package existed.
Provides: glibc-headers = %{version}-%{release}
Provides: glibc-headers(%{_target_cpu})
Obsoletes: glibc-headers < %{version}-%{release}
%endif

%description devel
The glibc-devel package contains the object files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard object files available in order to create the
executables.

Install glibc-devel if you are going to develop programs which will
use the standard C libraries.

##############################################################################
# glibc "doc" sub-package
##############################################################################
%if %{with docs}
%package doc
Summary: Documentation for GNU libc
BuildArch: noarch
Requires: %{name} = %{version}-%{release}

# Removing texinfo will cause check-safety.sh test to fail because it seems to
# trigger documentation generation based on dependencies.  We need to fix this
# upstream in some way that doesn't depend on generating docs to validate the
# texinfo.  I expect it's simply the wrong dependency for that target.
BuildRequires: texinfo >= 5.0

%description doc
The glibc-doc package contains The GNU C Library Reference Manual in info
format.  Additional package documentation is also provided.
%endif

##############################################################################
# glibc "static" sub-package
##############################################################################
%package static
Summary: C library static libraries for -static linking.
Requires: %{name}-devel = %{version}-%{release}
Requires: libxcrypt-static%{?_isa} >= 4.0.0

%description static
The glibc-static package contains the C library static libraries
for -static linking.  You don't need these, unless you link statically,
which is highly discouraged.

##############################################################################
# glibc "headers" sub-package
# - The headers package includes all common headers that are shared amongst
#   the multilib builds. It avoids file conflicts between the architecture-
#   specific glibc-devel variants.
#   Files like gnu/stubs.h which have gnu/stubs-32.h (i686) and gnu/stubs-64.h
#   are included in glibc-headers, but the -32 and -64 files are in their
#   respective i686 and x86_64 devel packages.
##############################################################################
%if %{need_headers_package}
%package -n %{headers_package_name}
Summary: Additional internal header files for glibc-devel.
Requires: %{name} = %{version}-%{release}
%if 0%{?rhel} > 0
Provides: %{name}-headers(%{_target_cpu})
Obsoletes: glibc-headers-x86 < %{version}-%{release}
Obsoletes: glibc-headers-s390 < %{version}-%{release}
%else
BuildArch: noarch
%endif

%description -n %{headers_package_name}
The %{headers_package_name} package contains the architecture-specific
header files which cannot be included in glibc-devel package.
%endif

##############################################################################
# glibc "common" sub-package
##############################################################################
%package common
Summary: Common binaries and locale data for glibc
Requires: %{name} = %{version}-%{release}
Requires: tzdata >= 2003a

%description common
The glibc-common package includes common binaries for the GNU libc
libraries, as well as national language (locale) support.

######################################################################
# File triggers to do ldconfig calls automatically (see rhbz#1380878)
######################################################################

# File triggers for when libraries are added or removed in standard
# paths.
%transfiletriggerin common -P 2000000 -- /lib /usr/lib /lib64 /usr/lib64
/sbin/ldconfig
%end

%transfiletriggerpostun common -P 2000000 -- /lib /usr/lib /lib64 /usr/lib64
/sbin/ldconfig
%end

# We need to run ldconfig manually because __brp_ldconfig assumes that
# glibc itself is always installed in $RPM_BUILD_ROOT, but with sysroots
# we may be installed into a subdirectory of that path.  Therefore we
# unset __brp_ldconfig and run ldconfig by hand with the sysroots path
# passed to -r.
%undefine __brp_ldconfig

######################################################################

%package locale-source
Summary: The sources for the locales
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}

%description locale-source
The sources for all locales provided in the language packs.
If you are building custom locales you will most likely use
these sources as the basis for your new locale.

%{lua:
-- To make lua-mode happy: '

-- List of supported locales.  This is used to generate the langpack
-- subpackages below.  This table needs adjustments if the set of
-- glibc locales changes.  "code" is the glibc code for the language
-- (before the "_".  "name" is the English translation of the language
-- name (for use in subpackage descriptions).  "regions" is a table of
-- variant specifiers (after the "_", excluding "@" and "."
-- variants/charset specifiers).  The table must be sorted by the code
-- field, and the regions table must be sorted as well.
--
-- English translations of language names can be obtained using (for
-- the "aa" language in this example):
--
-- python3 -c 'import langtable; print(langtable.language_name("aa", languageIdQuery="en"))'

local locales =  {
  { code="aa", name="Afar", regions={ "DJ", "ER", "ET" } },
  { code="af", name="Afrikaans", regions={ "ZA" } },
  { code="agr", name="Aguaruna", regions={ "PE" } },
  { code="ak", name="Akan", regions={ "GH" } },
  { code="am", name="Amharic", regions={ "ET" } },
  { code="an", name="Aragonese", regions={ "ES" } },
  { code="anp", name="Angika", regions={ "IN" } },
  {
    code="ar",
    name="Arabic",
    regions={
      "AE",
      "BH",
      "DZ",
      "EG",
      "IN",
      "IQ",
      "JO",
      "KW",
      "LB",
      "LY",
      "MA",
      "OM",
      "QA",
      "SA",
      "SD",
      "SS",
      "SY",
      "TN",
      "YE" 
    } 
  },
  { code="as", name="Assamese", regions={ "IN" } },
  { code="ast", name="Asturian", regions={ "ES" } },
  { code="ayc", name="Southern Aymara", regions={ "PE" } },
  { code="az", name="Azerbaijani", regions={ "AZ", "IR" } },
  { code="be", name="Belarusian", regions={ "BY" } },
  { code="bem", name="Bemba", regions={ "ZM" } },
  { code="ber", name="Berber", regions={ "DZ", "MA" } },
  { code="bg", name="Bulgarian", regions={ "BG" } },
  { code="bhb", name="Bhili", regions={ "IN" } },
  { code="bho", name="Bhojpuri", regions={ "IN", "NP" } },
  { code="bi", name="Bislama", regions={ "VU" } },
  { code="bn", name="Bangla", regions={ "BD", "IN" } },
  { code="bo", name="Tibetan", regions={ "CN", "IN" } },
  { code="br", name="Breton", regions={ "FR" } },
  { code="brx", name="Bodo", regions={ "IN" } },
  { code="bs", name="Bosnian", regions={ "BA" } },
  { code="byn", name="Blin", regions={ "ER" } },
  { code="ca", name="Catalan", regions={ "AD", "ES", "FR", "IT" } },
  { code="ce", name="Chechen", regions={ "RU" } },
  { code="chr", name="Cherokee", regions={ "US" } },
  { code="ckb", name="Central Kurdish", regions={ "IQ" } },
  { code="cmn", name="Mandarin Chinese", regions={ "TW" } },
  { code="crh", name="Crimean Turkish", regions={ "UA" } },
  { code="cs", name="Czech", regions={ "CZ" } },
  { code="csb", name="Kashubian", regions={ "PL" } },
  { code="cv", name="Chuvash", regions={ "RU" } },
  { code="cy", name="Welsh", regions={ "GB" } },
  { code="da", name="Danish", regions={ "DK" } },
  {
    code="de",
    name="German",
    regions={ "AT", "BE", "CH", "DE", "IT", "LI", "LU" } 
  },
  { code="doi", name="Dogri", regions={ "IN" } },
  { code="dsb", name="Lower Sorbian", regions={ "DE" } },
  { code="dv", name="Divehi", regions={ "MV" } },
  { code="dz", name="Dzongkha", regions={ "BT" } },
  { code="el", name="Greek", regions={ "CY", "GR" } },
  {
    code="en",
    name="English",
    regions={
      "AG",
      "AU",
      "BW",
      "CA",
      "DK",
      "GB",
      "HK",
      "IE",
      "IL",
      "IN",
      "NG",
      "NZ",
      "PH",
      "SC",
      "SG",
      "US",
      "ZA",
      "ZM",
      "ZW" 
    } 
  },
  { code="eo", name="Esperanto", regions={} },
  {
    code="es",
    name="Spanish",
    regions={
      "AR",
      "BO",
      "CL",
      "CO",
      "CR",
      "CU",
      "DO",
      "EC",
      "ES",
      "GT",
      "HN",
      "MX",
      "NI",
      "PA",
      "PE",
      "PR",
      "PY",
      "SV",
      "US",
      "UY",
      "VE" 
    } 
  },
  { code="et", name="Estonian", regions={ "EE" } },
  { code="eu", name="Basque", regions={ "ES" } },
  { code="fa", name="Persian", regions={ "IR" } },
  { code="ff", name="Fulah", regions={ "SN" } },
  { code="fi", name="Finnish", regions={ "FI" } },
  { code="fil", name="Filipino", regions={ "PH" } },
  { code="fo", name="Faroese", regions={ "FO" } },
  { code="fr", name="French", regions={ "BE", "CA", "CH", "FR", "LU" } },
  { code="fur", name="Friulian", regions={ "IT" } },
  { code="fy", name="Western Frisian", regions={ "DE", "NL" } },
  { code="ga", name="Irish", regions={ "IE" } },
  { code="gd", name="Scottish Gaelic", regions={ "GB" } },
  { code="gez", name="Geez", regions={ "ER", "ET" } },
  { code="gl", name="Galician", regions={ "ES" } },
  { code="gu", name="Gujarati", regions={ "IN" } },
  { code="gv", name="Manx", regions={ "GB" } },
  { code="ha", name="Hausa", regions={ "NG" } },
  { code="hak", name="Hakka Chinese", regions={ "TW" } },
  { code="he", name="Hebrew", regions={ "IL" } },
  { code="hi", name="Hindi", regions={ "IN" } },
  { code="hif", name="Fiji Hindi", regions={ "FJ" } },
  { code="hne", name="Chhattisgarhi", regions={ "IN" } },
  { code="hr", name="Croatian", regions={ "HR" } },
  { code="hsb", name="Upper Sorbian", regions={ "DE" } },
  { code="ht", name="Haitian Creole", regions={ "HT" } },
  { code="hu", name="Hungarian", regions={ "HU" } },
  { code="hy", name="Armenian", regions={ "AM" } },
  { code="ia", name="Interlingua", regions={ "FR" } },
  { code="id", name="Indonesian", regions={ "ID" } },
  { code="ig", name="Igbo", regions={ "NG" } },
  { code="ik", name="Inupiaq", regions={ "CA" } },
  { code="is", name="Icelandic", regions={ "IS" } },
  { code="it", name="Italian", regions={ "CH", "IT" } },
  { code="iu", name="Inuktitut", regions={ "CA" } },
  { code="ja", name="Japanese", regions={ "JP" } },
  { code="ka", name="Georgian", regions={ "GE" } },
  { code="kab", name="Kabyle", regions={ "DZ" } },
  { code="kk", name="Kazakh", regions={ "KZ" } },
  { code="kl", name="Kalaallisut", regions={ "GL" } },
  { code="km", name="Khmer", regions={ "KH" } },
  { code="kn", name="Kannada", regions={ "IN" } },
  { code="ko", name="Korean", regions={ "KR" } },
  { code="kok", name="Konkani", regions={ "IN" } },
  { code="ks", name="Kashmiri", regions={ "IN" } },
  { code="ku", name="Kurdish", regions={ "TR" } },
  { code="kw", name="Cornish", regions={ "GB" } },
  { code="ky", name="Kyrgyz", regions={ "KG" } },
  { code="lb", name="Luxembourgish", regions={ "LU" } },
  { code="lg", name="Ganda", regions={ "UG" } },
  { code="li", name="Limburgish", regions={ "BE", "NL" } },
  { code="lij", name="Ligurian", regions={ "IT" } },
  { code="ln", name="Lingala", regions={ "CD" } },
  { code="lo", name="Lao", regions={ "LA" } },
  { code="lt", name="Lithuanian", regions={ "LT" } },
  { code="lv", name="Latvian", regions={ "LV" } },
  { code="lzh", name="Literary Chinese", regions={ "TW" } },
  { code="mag", name="Magahi", regions={ "IN" } },
  { code="mai", name="Maithili", regions={ "IN", "NP" } },
  { code="mfe", name="Morisyen", regions={ "MU" } },
  { code="mg", name="Malagasy", regions={ "MG" } },
  { code="mhr", name="Meadow Mari", regions={ "RU" } },
  { code="mi", name="Maori", regions={ "NZ" } },
  { code="miq", name="Miskito", regions={ "NI" } },
  { code="mjw", name="Karbi", regions={ "IN" } },
  { code="mk", name="Macedonian", regions={ "MK" } },
  { code="ml", name="Malayalam", regions={ "IN" } },
  { code="mn", name="Mongolian", regions={ "MN" } },
  { code="mni", name="Manipuri", regions={ "IN" } },
  { code="mnw", name="Mon", regions={ "MM" } },
  { code="mr", name="Marathi", regions={ "IN" } },
  { code="ms", name="Malay", regions={ "MY" } },
  { code="mt", name="Maltese", regions={ "MT" } },
  { code="my", name="Burmese", regions={ "MM" } },
  { code="nan", name="Min Nan Chinese", regions={ "TW" } },
  { code="nb", name="Norwegian Bokmål", regions={ "NO" } },
  { code="nds", name="Low German", regions={ "DE", "NL" } },
  { code="ne", name="Nepali", regions={ "NP" } },
  { code="nhn", name="Tlaxcala-Puebla Nahuatl", regions={ "MX" } },
  { code="niu", name="Niuean", regions={ "NU", "NZ" } },
  { code="nl", name="Dutch", regions={ "AW", "BE", "NL" } },
  { code="nn", name="Norwegian Nynorsk", regions={ "NO" } },
  { code="nr", name="South Ndebele", regions={ "ZA" } },
  { code="nso", name="Northern Sotho", regions={ "ZA" } },
  { code="oc", name="Occitan", regions={ "FR" } },
  { code="om", name="Oromo", regions={ "ET", "KE" } },
  { code="or", name="Odia", regions={ "IN" } },
  { code="os", name="Ossetic", regions={ "RU" } },
  { code="pa", name="Punjabi", regions={ "IN", "PK" } },
  { code="pap", name="Papiamento", regions={ "AW", "CW" } },
  { code="pl", name="Polish", regions={ "PL" } },
  { code="ps", name="Pashto", regions={ "AF" } },
  { code="pt", name="Portuguese", regions={ "BR", "PT" } },
  { code="quz", name="Cusco Quechua", regions={ "PE" } },
  { code="raj", name="Rajasthani", regions={ "IN" } },
  { code="ro", name="Romanian", regions={ "RO" } },
  { code="ru", name="Russian", regions={ "RU", "UA" } },
  { code="rw", name="Kinyarwanda", regions={ "RW" } },
  { code="sa", name="Sanskrit", regions={ "IN" } },
  { code="sah", name="Sakha", regions={ "RU" } },
  { code="sat", name="Santali", regions={ "IN" } },
  { code="sc", name="Sardinian", regions={ "IT" } },
  { code="sd", name="Sindhi", regions={ "IN" } },
  { code="se", name="Northern Sami", regions={ "NO" } },
  { code="sgs", name="Samogitian", regions={ "LT" } },
  { code="shn", name="Shan", regions={ "MM" } },
  { code="shs", name="Shuswap", regions={ "CA" } },
  { code="si", name="Sinhala", regions={ "LK" } },
  { code="sid", name="Sidamo", regions={ "ET" } },
  { code="sk", name="Slovak", regions={ "SK" } },
  { code="sl", name="Slovenian", regions={ "SI" } },
  { code="sm", name="Samoan", regions={ "WS" } },
  { code="so", name="Somali", regions={ "DJ", "ET", "KE", "SO" } },
  { code="sq", name="Albanian", regions={ "AL", "MK" } },
  { code="sr", name="Serbian", regions={ "ME", "RS" } },
  { code="ss", name="Swati", regions={ "ZA" } },
  { code="st", name="Southern Sotho", regions={ "ZA" } },
  { code="sv", name="Swedish", regions={ "FI", "SE" } },
  { code="sw", name="Swahili", regions={ "KE", "TZ" } },
  { code="szl", name="Silesian", regions={ "PL" } },
  { code="ta", name="Tamil", regions={ "IN", "LK" } },
  { code="tcy", name="Tulu", regions={ "IN" } },
  { code="te", name="Telugu", regions={ "IN" } },
  { code="tg", name="Tajik", regions={ "TJ" } },
  { code="th", name="Thai", regions={ "TH" } },
  { code="the", name="Chitwania Tharu", regions={ "NP" } },
  { code="ti", name="Tigrinya", regions={ "ER", "ET" } },
  { code="tig", name="Tigre", regions={ "ER" } },
  { code="tk", name="Turkmen", regions={ "TM" } },
  { code="tl", name="Tagalog", regions={ "PH" } },
  { code="tn", name="Tswana", regions={ "ZA" } },
  { code="to", name="Tongan", regions={ "TO" } },
  { code="tpi", name="Tok Pisin", regions={ "PG" } },
  { code="tr", name="Turkish", regions={ "CY", "TR" } },
  { code="ts", name="Tsonga", regions={ "ZA" } },
  { code="tt", name="Tatar", regions={ "RU" } },
  { code="ug", name="Uyghur", regions={ "CN" } },
  { code="uk", name="Ukrainian", regions={ "UA" } },
  { code="unm", name="Unami language", regions={ "US" } },
  { code="ur", name="Urdu", regions={ "IN", "PK" } },
  { code="uz", name="Uzbek", regions={ "UZ" } },
  { code="ve", name="Venda", regions={ "ZA" } },
  { code="vi", name="Vietnamese", regions={ "VN" } },
  { code="wa", name="Walloon", regions={ "BE" } },
  { code="wae", name="Walser", regions={ "CH" } },
  { code="wal", name="Wolaytta", regions={ "ET" } },
  { code="wo", name="Wolof", regions={ "SN" } },
  { code="xh", name="Xhosa", regions={ "ZA" } },
  { code="yi", name="Yiddish", regions={ "US" } },
  { code="yo", name="Yoruba", regions={ "NG" } },
  { code="yue", name="Cantonese", regions={ "HK" } },
  { code="yuw", name="Yau", regions={ "PG" } },
  { code="zh", name="Mandarin Chinese", regions={ "CN", "HK", "SG", "TW" } },
  { code="zu", name="Zulu", regions={ "ZA" } } 
}

-- Prints a list of LANGUAGE "_" REGION pairs.  The output is expected
-- to be identical to parse-SUPPORTED.py.  Called from the %%prep section.
function print_locale_pairs()
   for i = 1, #locales do
      local locale = locales[i]
      if #locale.regions == 0 then
	 print(locale.code .. "\n")
      else
	 for j = 1, #locale.regions do
	    print(locale.code .. "_" .. locale.regions[j] .. "\n")
	 end
      end
   end
end

local function compute_supplements(locale)
   local lang = locale.code
   local regions = locale.regions
   result = "langpacks-core-" .. lang
   for i = 1, #regions do
      result = result .. " or langpacks-core-" .. lang .. "_" .. regions[i]
   end
   return result
end

-- Emit the definition of a language pack package.
local function lang_package(locale)
   local lang = locale.code
   local langname = locale.name
   local suppl = compute_supplements(locale)
   print(rpm.expand([[

%package langpack-]]..lang..[[

Summary: Locale data for ]]..langname..[[

Provides: glibc-langpack = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
Supplements: (glibc and (]]..suppl..[[))
%description langpack-]]..lang..[[

The glibc-langpack-]]..lang..[[ package includes the basic information required
to support the ]]..langname..[[ language in your applications.
%files -f langpack-]]..lang..[[.filelist langpack-]]..lang..[[
]]))
end

for i = 1, #locales do
   lang_package(locales[i])
end
}

# The glibc-all-langpacks provides the virtual glibc-langpack,
# and thus satisfies glibc's requirement for installed locales.
# Users can add one more other langauge packs and then eventually
# uninstall all-langpacks to save space.
%package all-langpacks
Summary: All language packs for %{name}.
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
Provides: %{name}-langpack = %{version}-%{release}
%description all-langpacks

# No %files, this is an empty package. The C/POSIX and
# C.UTF-8 files are already installed by glibc. We create
# minimal-langpack because the virtual provide of
# glibc-langpack needs at least one package installed
# to satisfy it. Given that no-locales installed is a valid
# use case we support it here with this package.
%package minimal-langpack
Summary: Minimal language packs for %{name}.
Provides: glibc-langpack = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
%description minimal-langpack
This is a Meta package that is used to install minimal language packs.
This package ensures you can use C, POSIX, or C.UTF-8 locales, but
nothing else. It is designed for assembling a minimal system.
%files minimal-langpack

# Infrequently used iconv converter modules.
%package gconv-extra
Summary: All iconv converter modules for %{name}.
Requires: %{name}%{_isa} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}

%description gconv-extra
This package contains all iconv converter modules built in %{name}.

##############################################################################
# glibc "nscd" sub-package
#
# Deprecated in Fedora 34 and planned for removal in Fedora 35.
#
# systemd-resolved is now enabled by default for DNS caching in Fedora, and
# sssd is capable of caching the remaining named services that nscd handles.
# It is therefore time to retire nscd in Fedora and move to more modern named
# services caches.
#
# For details, see:
# bug 1905135: https://fedoraproject.org/wiki/Changes/DeprecateNSCD
# bug 1905142: https://fedoraproject.org/wiki/Changes/RemoveNSCD
##############################################################################
%package -n nscd
Summary: A Name Service Caching Daemon (nscd).
# Fedora 35 is planned for release on Oct 26 2021, with nscd removed
Provides: deprecated() = 20211026
Requires: %{name} = %{version}-%{release}
%if %{without bootstrap}
Requires: libselinux >= 1.17.10-1
%endif
Requires: audit-libs >= 1.1.3
Requires(pre): /usr/sbin/useradd, coreutils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd, /usr/sbin/userdel

%description -n nscd
The nscd daemon caches name service lookups and can improve
performance with LDAP, and may help with DNS as well.

##############################################################################
# Subpackages for NSS modules except nss_files, nss_compat, nss_dns
##############################################################################

# This should remain it's own subpackage or "Provides: nss_db" to allow easy
# migration from old systems that previously had the old nss_db package
# installed. Note that this doesn't make the migration that smooth, the
# databases still need rebuilding because the formats were different.
# The nss_db package was deprecated in F16 and onwards:
# https://lists.fedoraproject.org/pipermail/devel/2011-July/153665.html
# The different database format does cause some issues for users:
# https://lists.fedoraproject.org/pipermail/devel/2011-December/160497.html
%package -n nss_db
Summary: Name Service Switch (NSS) module using hash-indexed files
Requires: %{name}%{_isa} = %{version}-%{release}
%ifarch x86_64
# Automatically install the 32-bit variant if the 64-bit variant has
# been installed.  This covers the case when glibc.i686 is installed
# before nss_db.x86_64.  (See above for the other ordering.)
Recommends: (nss_db(x86-32) if glibc(x86-32))
%endif

%description -n nss_db
The nss_db Name Service Switch module uses hash-indexed files in /var/db
to speed up user, group, service, host name, and other NSS-based lookups.

%package -n nss_hesiod
Summary: Name Service Switch (NSS) module using Hesiod
Requires: %{name}%{_isa} = %{version}-%{release}
%ifarch x86_64
# Automatically install the 32-bit variant if the 64-bit variant has
# been installed.  This covers the case when glibc.i686 is installed
# before nss_hesiod.x86_64.  (See above for the other ordering.)
Recommends: (nss_hesiod(x86-32) if glibc(x86-32))
%endif

%description -n nss_hesiod
The nss_hesiod Name Service Switch module uses the Domain Name System
(DNS) as a source for user, group, and service information, following
the Hesiod convention of Project Athena.

%package nss-devel
Summary: Development files for directly linking NSS service modules
Requires: %{name}%{_isa} = %{version}-%{release}
Requires: nss_db%{_isa} = %{version}-%{release}
Requires: nss_hesiod%{_isa} = %{version}-%{release}

%description nss-devel
The glibc-nss-devel package contains the object files necessary to
compile applications and libraries which directly link against NSS
modules supplied by glibc.

This is a rare and special use case; regular development has to use
the glibc-devel package instead.

##############################################################################
# glibc "utils" sub-package
##############################################################################
%package utils
Summary: Development utilities from GNU C library
Requires: %{name} = %{version}-%{release}

%description utils
The glibc-utils package contains memusage, a memory usage profiler,
mtrace, a memory leak tracer and xtrace, a function call tracer
which can be helpful during program debugging.

If unsure if you need this, don't install this package.

%if %{with benchtests}
%package benchtests
Summary: Benchmarking binaries and scripts for %{name}
%description benchtests
This package provides built benchmark binaries and scripts to run
microbenchmark tests on the system.
%endif

##############################################################################
# compat-libpthread-nonshared
# See: https://sourceware.org/bugzilla/show_bug.cgi?id=23500
##############################################################################
%package -n compat-libpthread-nonshared
Summary: Compatibility support for linking against libpthread_nonshared.a.

%description -n compat-libpthread-nonshared
This package provides compatibility support for applications that expect
libpthread_nonshared.a to exist. The support provided is in the form of
an empty libpthread_nonshared.a that allows dynamic links to succeed.
Such applications should be adjusted to avoid linking against
libpthread_nonshared.a which is no longer used. The static library
libpthread_nonshared.a is an internal implementation detail of the C
runtime and should not be expected to exist.

%if %{without bootstrap}
%package -n %sysroot_package_arch
Summary: Sysroot package for glibc, %{_arch} architecture
BuildArch: noarch
Provides: sysroot-%{_arch}-%{name}
# The files are not usable for execution, so do not provide nor
# require anything.
AutoReqProv: no

%description -n %sysroot_package_arch
This package contains development files for the glibc package
that can be installed across architectures.
%dnl %%{without bootstrap}
%endif

##############################################################################
# Prepare for the build.
##############################################################################
%prep
%autosetup -n %{glibcsrcdir} -p1

##############################################################################
# %%prep - Additional prep required...
##############################################################################
# Make benchmark scripts executable
chmod +x benchtests/scripts/*.py scripts/pylint

# Remove all files generated from patching.
find . -type f -size 0 -o -name "*.orig" -exec rm -f {} \;

# Ensure timestamps on configure files are current to prevent
# regenerating them.
touch `find . -name configure`

# Ensure *-kw.h files are current to prevent regenerating them.
touch locale/programs/*-kw.h

# Verify that our locales table is compatible with the locales table
# in the spec file.
set +x
echo '%{lua: print_locale_pairs()}' > localedata/SUPPORTED.spec
set -x
python3 %{SOURCE11} localedata/SUPPORTED > localedata/SUPPORTED.glibc
diff -u \
  --label "spec file" localedata/SUPPORTED.spec \
  --label "glibc localedata/SUPPORTED" localedata/SUPPORTED.glibc
rm localedata/SUPPORTED.spec localedata/SUPPORTED.glibc

##############################################################################
# Build glibc...
##############################################################################
%build
# Log osystem information
uname -a
LD_SHOW_AUXV=1 /bin/true
cat /proc/cpuinfo
cat /proc/sysinfo 2>/dev/null || true
cat /proc/meminfo
df

# We build using the native system compilers.
GCC=gcc
GXX=g++

# Part of rpm_inherit_flags.  Is overridden below.
rpm_append_flag ()
{
    BuildFlags="$BuildFlags $*"
}

# Propagates the listed flags to rpm_append_flag if supplied by
# redhat-rpm-config.
BuildFlags="-O2 -g"
rpm_inherit_flags ()
{
	local reference=" $* "
	local flag
	for flag in $RPM_OPT_FLAGS $RPM_LD_FLAGS ; do
		if echo "$reference" | grep -q -F " $flag " ; then
			rpm_append_flag "$flag"
		fi
	done
}

# Propgate select compiler flags from redhat-rpm-config.  These flags
# are target-dependent, so we use only those which are specified in
# redhat-rpm-config.  We keep the -m32/-m32/-m64 flags to support
# multilib builds.
#
# Note: For building alternative run-times, care is required to avoid
# overriding the architecture flags which go into CC/CXX.  The flags
# below are passed in CFLAGS.

rpm_inherit_flags \
	"-Wp,-D_GLIBCXX_ASSERTIONS" \
	"-fasynchronous-unwind-tables" \
	"-fstack-clash-protection" \
	"-funwind-tables" \
	"-m31" \
	"-m32" \
	"-m64" \
	"-march=armv8-a+lse" \
	"-march=armv8.1-a" \
	"-march=haswell" \
	"-march=i686" \
	"-march=x86-64" \
	"-march=x86-64-v2" \
	"-march=x86-64-v3" \
	"-march=x86-64-v4" \
	"-march=z13" \
	"-march=z14" \
	"-march=z15" \
	"-march=zEC12" \
	"-mbranch-protection=standard" \
	"-mcpu=power10" \
	"-mcpu=power8" \
	"-mcpu=power9" \
	"-mfpmath=sse" \
	"-msse2" \
	"-mstackrealign" \
	"-mtune=generic" \
	"-mtune=power10" \
	"-mtune=power8" \
	"-mtune=power9" \
	"-mtune=z13" \
	"-mtune=z14" \
	"-mtune=z15" \
	"-mtune=zEC12" \
	"-specs=/usr/lib/rpm/redhat/redhat-annobin-cc1" \

# Use the RHEL 8 baseline for the early dynamic loader code, so that
# running on too old CPUs results in a diagnostic.
%if 0%{?rhel} >= 9
%ifarch ppc64le
%define glibc_rtld_early_cflags -mcpu=power8
%endif
%ifarch s390x
%define glibc_rtld_early_cflags -march=z13
%endif
%ifarch x86_64
%define glibc_rtld_early_cflags -march=x86-64
%endif
%endif

# libc_nonshared.a cannot be built with the default hardening flags
# because the glibc build system is incompatible with
# -D_FORTIFY_SOURCE.  The object files need to be marked as to be
# skipped in annobin annotations.  (The -specs= variant of activating
# annobin does not work here because of flag ordering issues.)
# See <https://bugzilla.redhat.com/show_bug.cgi?id=1668822>.
BuildFlagsNonshared="-fplugin=annobin -fplugin-arg-annobin-disable -Wa,--generate-missing-build-notes=yes"

# Special flag to enable annobin annotations for statically linked
# assembler code.  Needs to be passed to make; not preserved by
# configure.
%define glibc_make_flags_as ASFLAGS="-g -Wa,--generate-missing-build-notes=yes"
%define glibc_make_flags %{glibc_make_flags_as}

##############################################################################
# %%build - Generic options.
##############################################################################
EnableKernel="--enable-kernel=%{enablekernel}"
# Save the used compiler and options into the file "Gcc" for use later
# by %%install.
echo "$GCC" > Gcc

##############################################################################
# build()
#	Build glibc in `build-%{target}$1', passing the rest of the arguments
#	as CFLAGS to the build (not the same as configure CFLAGS). Several
#	global values are used to determine build flags, kernel version,
#	system tap support, etc.
##############################################################################
build()
{
	local builddir=build-%{target}${1:+-$1}
	${1+shift}
	rm -rf $builddir
	mkdir $builddir
	pushd $builddir
	../configure CC="$GCC" CXX="$GXX" CFLAGS="$BuildFlags $*" \
		--prefix=%{_prefix} \
		--with-headers=%{_prefix}/include $EnableKernel \
		--with-nonshared-cflags="$BuildFlagsNonshared" \
		--enable-bind-now \
		--build=%{target} \
		--enable-stack-protector=strong \
		--enable-tunables \
		--enable-systemtap \
		${core_with_options} \
		%{?glibc_rtld_early_cflags:--with-rtld-early-cflags=%glibc_rtld_early_cflags} \
%ifarch x86_64 %{ix86}
	       --enable-cet \
%endif
%ifarch %{ix86}
		--disable-multi-arch \
%endif
%if %{without werror}
		--disable-werror \
%endif
		--disable-profile \
%if %{with bootstrap}
		--without-selinux \
%endif
%ifarch aarch64
		--enable-memory-tagging \
%endif
		--disable-crypt ||
		{ cat config.log; false; }

	%make_build -r %{glibc_make_flags}
	popd
}

# Default set of compiler options.
build

%if %{buildpower10}
(
  GCC="$GCC -mcpu=power10 -mtune=power10"
  GXX="$GXX -mcpu=power10 -mtune=power10"
  core_with_options="--with-cpu=power10"
  build power10
)
%endif

##############################################################################
# Install glibc...
##############################################################################
%install

# The built glibc is installed into a subdirectory of $RPM_BUILD_ROOT.
# For a system glibc that subdirectory is "/" (the root of the filesystem).
# This is called a sysroot (system root) and can be changed if we have a
# distribution that supports multiple installed glibc versions.
%define glibc_sysroot $RPM_BUILD_ROOT

# Remove existing file lists.
find . -type f -name '*.filelist' -exec rm -rf {} \;

# Reload compiler and build options that were used during %%build.
GCC=`cat Gcc`

%ifarch riscv64
# RISC-V ABI wants to install everything in /lib64/lp64d or /usr/lib64/lp64d.
# Make these be symlinks to /lib64 or /usr/lib64 respectively.  See:
# https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/thread/DRHT5YTPK4WWVGL3GIN5BF2IKX2ODHZ3/
for d in %{glibc_sysroot}%{_libdir} %{glibc_sysroot}/%{_lib}; do
	mkdir -p $d
	(cd $d && ln -sf . lp64d)
done
%endif

# Build and install:
pushd build-%{target}
%make_build install_root=%{glibc_sysroot} install
%make_build install_root=%{glibc_sysroot} \
	install-locale-files -C ../localedata objdir=`pwd`
popd
# Locale creation via install-locale-files does not group identical files
# via hardlinks, so we must group them ourselves.
hardlink -c %{glibc_sysroot}/usr/lib/locale

# install_different:
#	Install all core libraries into DESTDIR/SUBDIR. Either the file is
#	installed as a copy or a symlink to the default install (if it is the
#	same). The path SUBDIR_UP is the prefix used to go from
#	DESTDIR/SUBDIR to the default installed libraries e.g.
#	ln -s SUBDIR_UP/foo.so DESTDIR/SUBDIR/foo.so.
#	When you call this function it is expected that you are in the root
#	of the build directory, and that the default build directory is:
#	"../build-%{target}" (relatively).
#	The primary use of this function is to install alternate runtimes
#	into the build directory and avoid duplicating this code for each
#	runtime.
install_different()
{
	local lib libbase libbaseso dlib
	local destdir="$1"
	local subdir="$2"
	local subdir_up="$3"
	local libdestdir="$destdir/$subdir"
	# All three arguments must be non-zero paths.
	if ! [ "$destdir" \
	       -a "$subdir" \
	       -a "$subdir_up" ]; then
		echo "One of the arguments to install_different was emtpy."
		exit 1
	fi
	# Create the destination directory and the multilib directory.
	mkdir -p "$destdir"
	mkdir -p "$libdestdir"
	# Walk all of the libraries we installed...
	for lib in libc math/libm
	do
		libbase=${lib#*/}
		# Take care that `libbaseso' has a * that needs expanding so
		# take care with quoting.
		libbaseso=$(basename %{glibc_sysroot}/%{_lib}/${libbase}.so.*)
		# Only install if different from default build library.
		if cmp -s ${lib}.so ../build-%{target}/${lib}.so; then
			ln -sf "$subdir_up"/$libbaseso $libdestdir/$libbaseso
		else
			cp -a ${lib}.so $libdestdir/$libbaseso
		fi
	done
}

%if %{buildpower10}
pushd build-%{target}-power10
install_different "$RPM_BUILD_ROOT/%{_libdir}/glibc-hwcaps" power10 ..
popd
%endif

##############################################################################
# Remove the files we don't want to distribute
##############################################################################

# Remove the libNoVersion files.
# XXX: This looks like a bug in glibc that accidentally installed these
#      wrong files. We probably don't need this today.
rm -f %{glibc_sysroot}/%{_libdir}/libNoVersion*
rm -f %{glibc_sysroot}/%{_lib}/libNoVersion*

# Remove the old nss modules.
rm -f %{glibc_sysroot}/%{_lib}/libnss1-*
rm -f %{glibc_sysroot}/%{_lib}/libnss-*.so.1

# This statically linked binary is no longer necessary in a world where
# the default Fedora install uses an initramfs, and further we have rpm-ostree
# which captures the whole userspace FS tree.
# Further, see https://github.com/projectatomic/rpm-ostree/pull/1173#issuecomment-355014583
rm -f %{glibc_sysroot}/{usr/,}sbin/sln

######################################################################
# Run ldconfig to create all the symbolic links we need
######################################################################

# Note: This has to happen before creating /etc/ld.so.conf.

mkdir -p %{glibc_sysroot}/var/cache/ldconfig
truncate -s 0 %{glibc_sysroot}/var/cache/ldconfig/aux-cache

# ldconfig is statically linked, so we can use the new version.
%{glibc_sysroot}/sbin/ldconfig -N -r %{glibc_sysroot}

##############################################################################
# Install info files
##############################################################################

%if %{with docs}
# Move the info files if glibc installed them into the wrong location.
if [ -d %{glibc_sysroot}%{_prefix}/info -a "%{_infodir}" != "%{_prefix}/info" ]; then
  mkdir -p %{glibc_sysroot}%{_infodir}
  mv -f %{glibc_sysroot}%{_prefix}/info/* %{glibc_sysroot}%{_infodir}
  rm -rf %{glibc_sysroot}%{_prefix}/info
fi

# Compress all of the info files.
gzip -9nvf %{glibc_sysroot}%{_infodir}/libc*

# Copy the debugger interface documentation over to the right location
mkdir -p %{glibc_sysroot}%{_docdir}/glibc
cp elf/rtld-debugger-interface.txt %{glibc_sysroot}%{_docdir}/glibc
%else
rm -f %{glibc_sysroot}%{_infodir}/dir
rm -f %{glibc_sysroot}%{_infodir}/libc.info*
%endif

##############################################################################
# Create locale sub-package file lists
##############################################################################

olddir=`pwd`
pushd %{glibc_sysroot}%{_prefix}/lib/locale
rm -f locale-archive
$olddir/build-%{target}/elf/ld.so \
        --library-path $olddir/build-%{target}/ \
        $olddir/build-%{target}/locale/localedef \
	--alias-file=$olddir/intl/locale.alias \
        --prefix %{glibc_sysroot} --add-to-archive \
        eo *_*
# Historically, glibc-all-langpacks deleted the file on updates (sic),
# so we need to restore it in the posttrans scriptlet (like the old
# glibc-all-langpacks versions)
ln locale-archive locale-archive.real

# Almost half the LC_CTYPE files in langpacks are identical to the C.utf8
# variant which is installed by default.  When we keep them as hardlinks,
# each langpack ends up retaining a copy.  If we convert these to symbolic
# links instead, we save ~350K each when they get installed that way.
#
# LC_MEASUREMENT and LC_PAPER also have several duplicates but we don't
# bother with these because they are only ~30 bytes each.
pushd %{glibc_sysroot}/usr/lib/locale
for f in $(find eo *_* -samefile C.utf8/LC_CTYPE); do
  rm $f && ln -s '../C.utf8/LC_CTYPE' $f
done
popd

# Create the file lists for the language specific sub-packages:
for i in eo *_*
do
    lang=${i%%_*}
    if [ ! -e langpack-${lang}.filelist ]; then
        echo "%dir %{_prefix}/lib/locale" >> langpack-${lang}.filelist
    fi
    echo "%dir  %{_prefix}/lib/locale/$i" >> langpack-${lang}.filelist
    echo "%{_prefix}/lib/locale/$i/*" >> langpack-${lang}.filelist
done
popd
pushd %{glibc_sysroot}%{_prefix}/share/locale
for i in */LC_MESSAGES/libc.mo
do
    locale=${i%%%%/*}
    lang=${locale%%%%_*}
    echo "%lang($lang) %{_prefix}/share/locale/${i}" \
         >> %{glibc_sysroot}%{_prefix}/lib/locale/langpack-${lang}.filelist
done
popd
mv  %{glibc_sysroot}%{_prefix}/lib/locale/*.filelist .

##############################################################################
# Install configuration files for services
##############################################################################

install -p -m 644 nss/nsswitch.conf %{glibc_sysroot}/etc/nsswitch.conf

# This is for ncsd - in glibc 2.2
install -m 644 nscd/nscd.conf %{glibc_sysroot}/etc
mkdir -p %{glibc_sysroot}%{_tmpfilesdir}
install -m 644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}
mkdir -p %{glibc_sysroot}/lib/systemd/system
install -m 644 nscd/nscd.service nscd/nscd.socket %{glibc_sysroot}/lib/systemd/system

# Include ld.so.conf
echo 'include ld.so.conf.d/*.conf' > %{glibc_sysroot}/etc/ld.so.conf
truncate -s 0 %{glibc_sysroot}/etc/ld.so.cache
chmod 644 %{glibc_sysroot}/etc/ld.so.conf
mkdir -p %{glibc_sysroot}/etc/ld.so.conf.d
mkdir -p %{glibc_sysroot}/etc/sysconfig
truncate -s 0 %{glibc_sysroot}/etc/sysconfig/nscd
truncate -s 0 %{glibc_sysroot}/etc/gai.conf

# Include %{_libdir}/gconv/gconv-modules.cache
truncate -s 0 %{glibc_sysroot}%{_libdir}/gconv/gconv-modules.cache
chmod 644 %{glibc_sysroot}%{_libdir}/gconv/gconv-modules.cache

# Remove any zoneinfo files; they are maintained by tzdata.
rm -rf %{glibc_sysroot}%{_prefix}/share/zoneinfo

# Make sure %config files have the same timestamp across multilib packages.
#
# XXX: Ideally ld.so.conf should have the timestamp of the spec file, but there
# doesn't seem to be any macro to give us that.  So we do the next best thing,
# which is to at least keep the timestamp consistent. The choice of using
# SOURCE0 is arbitrary.
touch -r %{SOURCE0} %{glibc_sysroot}/etc/ld.so.conf
touch -r inet/etc.rpc %{glibc_sysroot}/etc/rpc

%if %{with benchtests}
# Build benchmark binaries.  Ignore the output of the benchmark runs.
pushd build-%{target}
make BENCH_DURATION=1 bench-build
popd

# Copy over benchmark binaries.
mkdir -p %{glibc_sysroot}%{_prefix}/libexec/glibc-benchtests
cp $(find build-%{target}/benchtests -type f -executable) %{glibc_sysroot}%{_prefix}/libexec/glibc-benchtests/
# ... and the makefile.
for b in %{SOURCE2} %{SOURCE3}; do
	cp $b %{glibc_sysroot}%{_prefix}/libexec/glibc-benchtests/
done
# .. and finally, the comparison scripts.
cp benchtests/scripts/benchout.schema.json %{glibc_sysroot}%{_prefix}/libexec/glibc-benchtests/
cp benchtests/scripts/compare_bench.py %{glibc_sysroot}%{_prefix}/libexec/glibc-benchtests/
cp benchtests/scripts/import_bench.py %{glibc_sysroot}%{_prefix}/libexec/glibc-benchtests/
cp benchtests/scripts/validate_benchout.py %{glibc_sysroot}%{_prefix}/libexec/glibc-benchtests/
%endif

# The #line directives gperf generates do not give the proper
# file name relative to the build directory.
pushd locale
ln -s programs/*.gperf .
popd
pushd iconv
ln -s ../locale/programs/charmap-kw.gperf .
popd

%if %{with docs}
# Remove the `dir' info-heirarchy file which will be maintained
# by the system as it adds info files to the install.
rm -f %{glibc_sysroot}%{_infodir}/dir
%endif

mkdir -p %{glibc_sysroot}/var/{db,run}/nscd
touch %{glibc_sysroot}/var/{db,run}/nscd/{passwd,group,hosts,services}
touch %{glibc_sysroot}/var/run/nscd/{socket,nscd.pid}

# Move libpcprofile.so and libmemusage.so into the proper library directory.
# They can be moved without any real consequences because users would not use
# them directly.
mkdir -p %{glibc_sysroot}%{_libdir}
mv -f %{glibc_sysroot}/%{_lib}/lib{pcprofile,memusage}.so \
	%{glibc_sysroot}%{_libdir}

# Disallow linking against libc_malloc_debug.
rm %{glibc_sysroot}%{_libdir}/libc_malloc_debug.so

# Strip all of the installed object files.
strip -g %{glibc_sysroot}%{_libdir}/*.o

# The xtrace and memusage scripts have hard-coded paths that need to be
# translated to a correct set of paths using the $LIB token which is
# dynamically translated by ld.so as the default lib directory.
for i in %{glibc_sysroot}%{_prefix}/bin/{xtrace,memusage}; do
%if %{with bootstrap}
  test -w $i || continue
%endif
  sed -e 's~=/%{_lib}/libpcprofile.so~=%{_libdir}/libpcprofile.so~' \
      -e 's~=/%{_lib}/libmemusage.so~=%{_libdir}/libmemusage.so~' \
      -e 's~='\''/\\\$LIB/libpcprofile.so~='\''%{_prefix}/\\$LIB/libpcprofile.so~' \
      -e 's~='\''/\\\$LIB/libmemusage.so~='\''%{_prefix}/\\$LIB/libmemusage.so~' \
      -i $i
done

##############################################################################
# Build an empty libpthread_nonshared.a for compatiliby with applications
# that have old linker scripts that reference this file. We ship this only
# in compat-libpthread-nonshared sub-package.
##############################################################################
ar cr %{glibc_sysroot}%{_prefix}/%{_lib}/libpthread_nonshared.a

###############################################################################
# Sysroot package creation.
###############################################################################

%if %{without bootstrap}
mkdir -p %{glibc_sysroot}/%{sysroot_prefix}
pushd %{glibc_sysroot}/%{sysroot_prefix}
mkdir -p usr/lib usr/lib64

cp -a %{glibc_sysroot}/%{_prefix}/include usr/.
for lib in lib lib64;  do
    for pfx in "" %{_prefix}/; do
	if test -d %{glibc_sysroot}/$pfx$lib ; then
	    # Implement UsrMove: everything goes into usr/$lib.  Only
	    # copy files directly in $lib.
	    find %{glibc_sysroot}/$pfx$lib -maxdepth 1 -type f \
		| xargs -I '{}' cp  '{}' usr/$lib/.
	    # Symbolic links need to be adjusted for UsrMove: They
	    # need to stay within the same directory.
	    for sl in `find %{glibc_sysroot}/$pfx$lib -maxdepth 1 -type l`; do
		set +x
		slbase=$(basename $sl)
		sltarget=$(basename $(readlink $sl))
		if ! test -r usr/$lib/$sltarget; then
		    echo "$sl: inferred $sltarget ($(readlink $sl)) missing"
		    exit 1
		fi
		set -x
		ln -s $sltarget usr/$lib/$slbase
	    done
	fi
    done
done

# Workaround for the lack of a kernel sysroot package.  Copy the
# kernel headers into the sysroot.
rpm -ql kernel-headers | grep "^/usr/include" | while read f ; do
    if test -f "$f" ; then
        install -D "$f" "./$f"
    fi
done

# Remove the executable bit from files in the sysroot.  This prevents
# debuginfo extraction.
find -type f | xargs chmod a-x

# Use sysroot-relative paths in linker script.  Ignore symbolic links.
sed -e 's,\([^0-9a-zA-Z=*]/lib\),=/usr/lib,g' \
    -e 's,\([^0-9a-zA-Z=*]\)/,\1=/,g' \
    -i $(find -type f -name 'lib[cm].so')

popd
%dnl %%{without bootstrap}
%endif

##############################################################################
# Beyond this point in the install process we no longer modify the set of
# installed files.
##############################################################################

##############################################################################
# Build the file lists used for describing the package and subpackages.
##############################################################################
# There are several main file lists (and many more for
# the langpack sub-packages (langpack-${lang}.filelist)):
# * master.filelist
#	- Master file list from which all other lists are built.
# * glibc.filelist
#	- Files for the glibc packages.
# * common.filelist
#	- Flies for the common subpackage.
# * utils.filelist
#	- Files for the utils subpackage.
# * nscd.filelist
#	- Files for the nscd subpackage.
# * devel.filelist
#	- Files for the devel subpackage.
# * doc.filelist
#	- Files for the documentation subpackage.
# * headers.filelist
#	- Files for the headers subpackage.
# * static.filelist
#	- Files for the static subpackage.
# * libnsl.filelist
#       - Files for the libnsl subpackage
# * nss_db.filelist
# * nss_hesiod.filelist
#       - File lists for nss_* NSS module subpackages.
# * nss-devel.filelist
#       - File list with the .so symbolic links for NSS packages.
# * compat-libpthread-nonshared.filelist.
#	- File list for compat-libpthread-nonshared subpackage.

# Create the main file lists. This way we can append to any one of them later
# wihtout having to create it. Note these are removed at the start of the
# install phase.
touch master.filelist
touch glibc.filelist
touch common.filelist
touch utils.filelist
touch gconv.filelist
touch nscd.filelist
touch devel.filelist
touch doc.filelist
touch headers.filelist
touch static.filelist
touch libnsl.filelist
touch nss_db.filelist
touch nss_hesiod.filelist
touch nss-devel.filelist
touch compat-libpthread-nonshared.filelist

###############################################################################
# Master file list, excluding a few things.
###############################################################################
{
  # List all files or links that we have created during install.
  # Files with 'etc' are configuration files, likewise 'gconv-modules'
  # and 'gconv-modules.cache' are caches, and we exclude them.
  find %{glibc_sysroot} \( -type f -o -type l \) \
       \( \
	 -name etc -printf "%%%%config " -o \
	 -name gconv-modules.cache \
	 -printf "%%%%verify(not md5 size mtime) " -o \
	 -name gconv-modules* \
	 -printf "%%%%verify(not md5 size mtime) %%%%config(noreplace) " \
	 , \
	 ! -path "*/lib/debug/*" -printf "/%%P\n" \)
  # List all directories with a %%dir prefix.  We omit the info directory and
  # all directories in (and including) /usr/share/locale.
  find %{glibc_sysroot} -type d \
       \( -path '*%{_prefix}/share/locale' -prune -o \
       \( -path '*%{_prefix}/share/*' \
%if %{with docs}
	! -path '*%{_infodir}' -o \
%endif
	  -path "*%{_prefix}/include/*" \
       \) -printf "%%%%dir /%%P\n" \)
} | {
  # Also remove the *.mo entries.  We will add them to the
  # language specific sub-packages.
  # libnss_ files go into subpackages related to NSS modules.
  # and .*/share/i18n/charmaps/.*), they go into the sub-package
  # "locale-source".  /sys-root/ files are put into the sysroot package.
  sed -e '\,.*/share/locale/\([^/_]\+\).*/LC_MESSAGES/.*\.mo,d' \
      -e '\,.*/share/i18n/locales/.*,d' \
      -e '\,.*/share/i18n/charmaps/.*,d' \
      -e '\,.*/etc/\(localtime\|nsswitch.conf\|ld\.so\.conf\|ld\.so\.cache\|default\|rpc\|gai\.conf\),d' \
      -e '\,.*/%{_libdir}/lib\(pcprofile\|memusage\)\.so,d' \
      -e '\,.*/bin/\(memusage\|mtrace\|xtrace\|pcprofiledump\),d' \
      -e '\,.*/sys-root,d'
} | sort > master.filelist

# The master file list is now used by each subpackage to list their own
# files. We go through each package and subpackage now and create their lists.
# Each subpackage picks the files from the master list that they need.
# The order of the subpackage list generation does not matter.

# Make the master file list read-only after this point to avoid accidental
# modification.
chmod 0444 master.filelist

###############################################################################
# glibc
###############################################################################

# Add all files with the following exceptions:
# - The info files '%{_infodir}/dir'
# - The partial (lib*_p.a) static libraries, include files.
# - The static files, objects, unversioned DSOs, and nscd.
# - The bin, locale, some sbin, and share.
#   - We want iconvconfig in the main package and we do this by using
#     a double negation of -v and [^i] so it removes all files in
#     sbin *but* iconvconfig.
# - All the libnss files (we add back the ones we want later).
# - All bench test binaries.
# - The aux-cache, since it's handled specially in the files section.
# - Extra gconv modules.  We add the required modules later.
cat master.filelist \
	| grep -v \
	-e '%{_infodir}' \
	-e '%{_libdir}/lib.*_p.a' \
	-e '%{_prefix}/include' \
	-e '%{_libdir}/lib.*\.a' \
        -e '%{_libdir}/.*\.o' \
	-e '%{_libdir}/lib.*\.so' \
	-e '%{_libdir}/gconv/.*\.so$' \
	-e '%{_libdir}/gconv/gconv-modules.d/gconv-modules-extra\.conf$' \
	-e 'nscd' \
	-e '%{_prefix}/bin' \
	-e '%{_prefix}/lib/locale' \
	-e '%{_prefix}/sbin/[^i]' \
	-e '%{_prefix}/share' \
	-e '/var/db/Makefile' \
	-e '/libnss_.*\.so[0-9.]*$' \
	-e '/libnsl' \
	-e 'glibc-benchtests' \
	-e 'aux-cache' \
	> glibc.filelist

# Add specific files:
# - The nss_files, nss_compat, and nss_db files.
# - The libmemusage.so and libpcprofile.so used by utils.
for module in compat files dns; do
    cat master.filelist \
	| grep -E \
	-e "/libnss_$module(\.so\.[0-9.]+|-[0-9.]+\.so)$" \
	>> glibc.filelist
done
grep -e "libmemusage.so" -e "libpcprofile.so" master.filelist >> glibc.filelist

###############################################################################
# glibc-gconv-extra
###############################################################################

grep -e "gconv-modules-extra.conf" master.filelist > gconv.filelist

# Put the essential gconv modules into the main package.
GconvBaseModules="ANSI_X3.110 ISO8859-15 ISO8859-1 CP1252"
GconvBaseModules="$GconvBaseModules UNICODE UTF-16 UTF-32 UTF-7"
%ifarch s390 s390x
GconvBaseModules="$GconvBaseModules ISO-8859-1_CP037_Z900 UTF8_UTF16_Z9"
GconvBaseModules="$GconvBaseModules UTF16_UTF32_Z9 UTF8_UTF32_Z9"
%endif
GconvAllModules=$(cat master.filelist |
                 sed -n 's|%{_libdir}/gconv/\(.*\)\.so|\1|p')

# Put the base modules into glibc and the rest into glibc-gconv-extra
for conv in $GconvAllModules; do
    if echo $GconvBaseModules | grep -q $conv; then
	grep -E -e "%{_libdir}/gconv/$conv.so$" \
	    master.filelist >> glibc.filelist
    else
	grep -E -e "%{_libdir}/gconv/$conv.so$" \
	    master.filelist >> gconv.filelist
    fi
done

###############################################################################
# glibc-devel
###############################################################################

# Static libraries that land in glibc-devel, not glibc-static.
devel_static_library_pattern='/lib\(\(c\|nldbl\|mvec\)_nonshared\|g\|ieee\|mcheck\|pthread\|dl\|rt\|util\|anl\)\.a$'
# Static libraries neither in glibc-devel nor in glibc-static.
other_static_library_pattern='/libpthread_nonshared\.a'

grep '%{_libdir}/lib.*\.a' master.filelist \
  | grep "$devel_static_library_pattern" \
  | grep -v "$other_static_library_pattern" \
  > devel.filelist

# Put all of the object files and *.so (not the versioned ones) into the
# devel package.
grep '%{_libdir}/.*\.o' < master.filelist >> devel.filelist
grep '%{_libdir}/lib.*\.so' < master.filelist >> devel.filelist
# The exceptions are:
# - libmemusage.so and libpcprofile.so in glibc used by utils.
# - libnss_*.so which are in nss-devel.
sed -i -e '\,libmemusage.so,d' \
	-e '\,libpcprofile.so,d' \
	-e '\,/libnss_[a-z]*\.so$,d' \
	devel.filelist

%if %{glibc_autorequires}
mkdir -p %{glibc_sysroot}/%{_rpmconfigdir} %{glibc_sysroot}/%{_fileattrsdir}
sed < %{SOURCE4} \
    -e s/@VERSION@/%{version}/ \
    -e s/@RELEASE@/%{release}/ \
    -e s/@SYMVER@/%{glibc_autorequires_symver}/ \
    > %{glibc_sysroot}/%{_rpmconfigdir}/glibc.req
cp %{SOURCE5} %{glibc_sysroot}/%{_fileattrsdir}/glibc.attr
%endif

###############################################################################
# glibc-doc
###############################################################################

%if %{with docs}
# Put the info files into the doc file list, but exclude the generated dir.
grep '%{_infodir}' master.filelist | grep -v '%{_infodir}/dir' > doc.filelist
grep '%{_docdir}' master.filelist >> doc.filelist
%endif

###############################################################################
# glibc-headers
###############################################################################

%if %{need_headers_package}
# The glibc-headers package includes only common files which are identical
# across all multilib packages. We must keep gnu/stubs.h and gnu/lib-names.h
# in the glibc-headers package, but the -32, -64, -64-v1, and -64-v2 versions
# go into glibc-devel.
grep '%{_prefix}/include/gnu/stubs-.*\.h$' < master.filelist >> devel.filelist || :
grep '%{_prefix}/include/gnu/lib-names-.*\.h$' < master.filelist >> devel.filelist || :
# Put the include files into headers file list.
grep '%{_prefix}/include' < master.filelist \
  | egrep -v '%{_prefix}/include/gnu/stubs-.*\.h$' \
  | egrep -v '%{_prefix}/include/gnu/lib-names-.*\.h$' \
  > headers.filelist
%else
# If there is no glibc-headers package, all header files go into the
# glibc-devel package.
grep '%{_prefix}/include' < master.filelist >> devel.filelist
%endif

###############################################################################
# glibc-static
###############################################################################

# Put the rest of the static files into the static package.
grep '%{_libdir}/lib.*\.a' < master.filelist \
  | grep -v "$devel_static_library_pattern" \
  | grep -v "$other_static_library_pattern" \
  > static.filelist

###############################################################################
# glibc-common
###############################################################################

# All of the bin and certain sbin files go into the common package except
# iconvconfig which needs to go in glibc. Likewise nscd is excluded because
# it goes in nscd. The iconvconfig binary is kept in the main glibc package
# because we use it in the post-install scriptlet to rebuild the
# gconv-modules.cache.  The makedb binary is in nss_db.
grep '%{_prefix}/bin' master.filelist \
	| grep -v '%{_prefix}/bin/makedb' \
	>> common.filelist
grep '%{_prefix}/sbin' master.filelist \
	| grep -v '%{_prefix}/sbin/iconvconfig' \
	| grep -v 'nscd' >> common.filelist
# All of the files under share go into the common package since they should be
# multilib-independent.
# Exceptions:
# - The actual share directory, not owned by us.
# - The info files which go into doc, and the info directory.
# - All documentation files, which go into doc.
grep '%{_prefix}/share' master.filelist \
	| grep -v \
	-e '%{_prefix}/share/info/libc.info.*' \
	-e '%%dir %{prefix}/share/info' \
	-e '%%dir %{prefix}/share' \
	-e '%{_docdir}' \
	>> common.filelist

###############################################################################
# nscd
###############################################################################

# The nscd binary must go into the nscd subpackage.
echo '%{_prefix}/sbin/nscd' > nscd.filelist

###############################################################################
# glibc-utils
###############################################################################

# Add the utils scripts and programs to the utils subpackage.
cat > utils.filelist <<EOF
%if %{without bootstrap}
%{_prefix}/bin/memusage
%{_prefix}/bin/memusagestat
%endif
%{_prefix}/bin/mtrace
%{_prefix}/bin/pcprofiledump
%{_prefix}/bin/xtrace
EOF

###############################################################################
# nss_db, nss_hesiod
###############################################################################

# Move the NSS-related files to the NSS subpackages.  Be careful not
# to pick up .debug files, and the -devel symbolic links.
for module in db hesiod; do
  grep -E "/libnss_$module\\.so\\.[0-9.]+\$" \
    master.filelist > nss_$module.filelist
done
grep -E "%{_prefix}/bin/makedb$" master.filelist >> nss_db.filelist

###############################################################################
# nss-devel
###############################################################################

# Symlinks go into the nss-devel package (instead of the main devel
# package).
grep '/libnss_[a-z]*\.so$' master.filelist > nss-devel.filelist

###############################################################################
# libnsl
###############################################################################

# Prepare the libnsl-related file lists.
grep -E '/libnsl\.so\.[0-9]+$' master.filelist > libnsl.filelist
test $(wc -l < libnsl.filelist) -eq 1

%if %{with benchtests}
###############################################################################
# glibc-benchtests
###############################################################################

# List of benchmarks.
find build-%{target}/benchtests -type f -executable | while read b; do
	echo "%{_prefix}/libexec/glibc-benchtests/$(basename $b)"
done >> benchtests.filelist
# ... and the makefile.
for b in %{SOURCE2} %{SOURCE3}; do
	echo "%{_prefix}/libexec/glibc-benchtests/$(basename $b)" >> benchtests.filelist
done
# ... and finally, the comparison scripts.
echo "%{_prefix}/libexec/glibc-benchtests/benchout.schema.json" >> benchtests.filelist
echo "%{_prefix}/libexec/glibc-benchtests/compare_bench.py*" >> benchtests.filelist
echo "%{_prefix}/libexec/glibc-benchtests/import_bench.py*" >> benchtests.filelist
echo "%{_prefix}/libexec/glibc-benchtests/validate_benchout.py*" >> benchtests.filelist
%endif

###############################################################################
# compat-libpthread-nonshared
###############################################################################
echo "%{_libdir}/libpthread_nonshared.a" >> compat-libpthread-nonshared.filelist

##############################################################################
# Run the glibc testsuite
##############################################################################
%check
%if %{with testsuite}

# Run the glibc tests. If any tests fail to build we exit %check with
# an error, otherwise we print the test failure list and the failed
# test output and continue.  Write to standard error to avoid
# synchronization issues with make and shell tracing output if
# standard output and standard error are different pipes.
run_tests () {
  # This hides a test suite build failure, which should be fatal.  We
  # check "Summary of test results:" below to verify that all tests
  # were built and run.
  %make_build check |& tee rpmbuild.check.log >&2
  test -n tests.sum
  if ! grep -q '^Summary of test results:$' rpmbuild.check.log ; then
    echo "FAIL: test suite build of target: $(basename "$(pwd)")" >& 2
    exit 1
  fi
  set +x
  grep -v ^PASS: tests.sum > rpmbuild.tests.sum.not-passing || true
  if test -n rpmbuild.tests.sum.not-passing ; then
    echo ===================FAILED TESTS===================== >&2
    echo "Target: $(basename "$(pwd)")" >& 2
    cat rpmbuild.tests.sum.not-passing >&2
    while read failed_code failed_test ; do
      for suffix in out test-result ; do
        if test -e "$failed_test.$suffix"; then
	  echo >&2
          echo "=====$failed_code $failed_test.$suffix=====" >&2
          cat -- "$failed_test.$suffix" >&2
	  echo >&2
        fi
      done
    done <rpmbuild.tests.sum.not-passing
  fi

  # Unconditonally dump differences in the system call list.
  echo "* System call consistency checks:" >&2
  cat misc/tst-syscall-list.out >&2
  set -x
}

# Increase timeouts
export TIMEOUTFACTOR=16
parent=$$
echo ====================TESTING=========================

# Default libraries.
pushd build-%{target}
run_tests
popd

%if %{buildpower10}
# Run this test only if the server supports Power10 instructions.
if LD_SHOW_AUXV=1 /bin/true | grep -E "AT_HWCAP2:[^$]*arch_3_1" > /dev/null; then
  echo ====================TESTING -mcpu=power10=============
  pushd build-%{target}-power10
  run_tests
  popd
fi
%endif

echo ====================TESTING END=====================
PLTCMD='/^Relocation section .*\(\.rela\?\.plt\|\.rela\.IA_64\.pltoff\)/,/^$/p'
echo ====================PLT RELOCS LD.SO================
readelf -Wr %{glibc_sysroot}/%{_lib}/ld-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS LIBC.SO==============
readelf -Wr %{glibc_sysroot}/%{_lib}/libc-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS END==================

# Obtain a way to run the dynamic loader.  Avoid matching the symbolic
# link and then pick the first loader (although there should be only
# one).  Use -maxdepth 2 to avoid descending into the /sys-root/
# sub-tree.  See wrap-find-debuginfo.sh.
ldso_path="$(find %{glibc_sysroot}/ -maxdepth 2 -regextype posix-extended \
  -regex '.*/ld(-.*|64|)\.so\.[0-9]+$' -type f | LC_ALL=C sort | head -n1)"
run_ldso="$ldso_path --library-path %{glibc_sysroot}/%{_lib}"

# Show the auxiliary vector as seen by the new library
# (even if we do not perform the valgrind test).
LD_SHOW_AUXV=1 $run_ldso /bin/true

%if 0%{?_enable_debug_packages}
# Finally, check if valgrind runs with the new glibc.
# We want to fail building if valgrind is not able to run with this glibc so
# that we can then coordinate with valgrind to get it fixed before we update
# glibc.
%if %{with valgrind}
$run_ldso /usr/bin/valgrind --error-exitcode=1 \
	$run_ldso /usr/bin/true
# true --help performs some memory allocations.
$run_ldso /usr/bin/valgrind --error-exitcode=1 \
	$run_ldso /usr/bin/true --help >/dev/null
%endif
%endif

%endif


%pre -p <lua>
-- Check that the running kernel is new enough
required = '%{enablekernel}'
rel = posix.uname("%r")
if rpm.vercmp(rel, required) < 0 then
  error("FATAL: kernel too old", 0)
end

-- (1) Remove multilib libraries from previous installs.
-- In order to support in-place upgrades, we must immediately remove
-- all platform directories before installing a new glibc
-- version.  RPM only deletes files removed by updates near the end
-- of the transaction.  If we did not remove all platform
-- directories here, they may be preferred by the dynamic linker
-- during the execution of subsequent RPM scriptlets, likely
-- resulting in process startup failures.

-- Full set of libraries glibc may install.
install_libs = { "anl", "BrokenLocale", "c", "dl", "m", "mvec",
		 "nss_compat", "nss_db", "nss_dns", "nss_files",
		 "nss_hesiod", "pthread", "resolv", "rt", "SegFault",
		 "thread_db", "util" }

-- We are going to remove these libraries. Generally speaking we remove
-- all core libraries in the multilib directory.
-- For the versioned install names, the version are [2.0,9.9*], so we
-- match "libc-2.0.so" and so on up to "libc-9.9*".
-- For the unversioned install names, we match the library plus ".so."
-- followed by digests.
remove_regexps = {}
for i = 1, #install_libs do
  -- Versioned install name.
  remove_regexps[#remove_regexps + 1] = ("lib" .. install_libs[i]
                                         .. "%%-[2-9]%%.[0-9]+%%.so$")
  -- Unversioned install name.
  remove_regexps[#remove_regexps + 1] = ("lib" .. install_libs[i]
                                         .. "%%.so%%.[0-9]+$")
end

-- Two exceptions:
remove_regexps[#install_libs + 1] = "libthread_db%%-1%%.0%%.so"
remove_regexps[#install_libs + 2] = "libSegFault%%.so"

-- We are going to search these directories.
local remove_dirs = { "%{_libdir}/i686",
		      "%{_libdir}/i686/nosegneg",
		      "%{_libdir}/power6",
		      "%{_libdir}/power7",
		      "%{_libdir}/power8",
		      "%{_libdir}/power9",
		    }

-- Add all the subdirectories of the glibc-hwcaps subdirectory.
repeat
  local iter = posix.files("%{_libdir}/glibc-hwcaps")
  if iter ~= nil then
    for entry in iter do
      if entry ~= "." and entry ~= ".." then
        local path = "%{_libdir}/glibc-hwcaps/" .. entry
        if posix.access(path .. "/.", "x") then
          remove_dirs[#remove_dirs + 1] = path
        end
      end
    end
  end
until true

-- Walk all the directories with files we need to remove...
for _, rdir in ipairs (remove_dirs) do
  if posix.access (rdir) then
    -- If the directory exists we look at all the files...
    local remove_files = posix.files (rdir)
    for rfile in remove_files do
      for _, rregexp in ipairs (remove_regexps) do
	-- Does it match the regexp?
	local dso = string.match (rfile, rregexp)
        if (dso ~= nil) then
	  -- Removing file...
	  os.remove (rdir .. '/' .. rfile)
	end
      end
    end
  end
end

%post -p <lua>
%glibc_post_funcs
-- (1) Update /etc/ld.so.conf
-- Next we update /etc/ld.so.conf to ensure that it starts with
-- a literal "include ld.so.conf.d/*.conf".

local ldsoconf = "/etc/ld.so.conf"
local ldsoconf_tmp = "/etc/glibc_post_upgrade.ld.so.conf"

if posix.access (ldsoconf) then

  -- We must have a "include ld.so.conf.d/*.conf" line.
  local have_include = false
  for line in io.lines (ldsoconf) do
    -- This must match, and we don't ignore whitespace.
    if string.match (line, "^include ld.so.conf.d/%%*%%.conf$") ~= nil then
      have_include = true
    end
  end

  if not have_include then
    -- Insert "include ld.so.conf.d/*.conf" line at the start of the
    -- file. We only support one of these post upgrades running at
    -- a time (temporary file name is fixed).
    local tmp_fd = io.open (ldsoconf_tmp, "w")
    if tmp_fd ~= nil then
      tmp_fd:write ("include ld.so.conf.d/*.conf\n")
      for line in io.lines (ldsoconf) do
        tmp_fd:write (line .. "\n")
      end
      tmp_fd:close ()
      local res = os.rename (ldsoconf_tmp, ldsoconf)
      if res == nil then
        io.stdout:write ("Error: Unable to update configuration file (rename).\n")
      end
    else
      io.stdout:write ("Error: Unable to update configuration file (open).\n")
    end
  end
end

-- (2) Rebuild ld.so.cache early.
-- If the format of the cache changes then we need to rebuild
-- the cache early to avoid any problems running binaries with
-- the new glibc.

-- Note: We use _prefix because Fedora's UsrMove says so.
post_exec ("%{_prefix}/sbin/ldconfig")

-- (3) Update gconv modules cache.
-- If the /usr/lib/gconv/gconv-modules.cache exists, then update it
-- with the latest set of modules that were just installed.
-- We assume that the cache is in _libdir/gconv and called
-- "gconv-modules.cache".

update_gconv_modules_cache()

-- (4) On upgrades, restart systemd if installed.  "systemctl -q" does
-- not suppress the error message (which is common in chroots), so
-- open-code post_exec with standard error suppressed.
if tonumber(arg[2]) >= 2
   and posix.access("%{_prefix}/bin/systemctl", "x")
then
  local pid = posix.fork()
  if pid == 0 then
    posix.redirect2null(2)
    assert(posix.exec("%{_prefix}/bin/systemctl", "daemon-reexec"))
  elseif pid > 0 then
    posix.wait(pid)
  end
end

%posttrans all-langpacks -e -p <lua>
-- The old glibc-all-langpacks postun scriptlet deleted the locale-archive
-- file, so we may have to resurrect it on upgrades.
local archive_path = "%{_prefix}/lib/locale/locale-archive"
local real_path = "%{_prefix}/lib/locale/locale-archive.real"
local stat_archive = posix.stat(archive_path)
local stat_real = posix.stat(real_path)
-- If the hard link was removed, restore it.
if stat_archive ~= nil and stat_real ~= nil
    and (stat_archive.ino ~= stat_real.ino
         or stat_archive.dev ~= stat_real.dev) then
  posix.unlink(archive_path)
  stat_archive = nil
end
-- If the file is gone, restore it.
if stat_archive == nil then
  posix.link(real_path, archive_path)
end
-- Remove .rpmsave file potentially created due to config file change.
local save_path = archive_path .. ".rpmsave"
if posix.access(save_path) then
  posix.unlink(save_path)
end

%post gconv-extra -p <lua>
%glibc_post_funcs
update_gconv_modules_cache ()

%postun gconv-extra -p <lua>
%glibc_post_funcs
update_gconv_modules_cache ()

%pre -n nscd
getent group nscd >/dev/null || /usr/sbin/groupadd -g 28 -r nscd
getent passwd nscd >/dev/null ||
  /usr/sbin/useradd -M -o -r -d / -s /sbin/nologin \
		    -c "NSCD Daemon" -u 28 -g nscd nscd

%post -n nscd
%systemd_post nscd.service

%preun -n nscd
%systemd_preun nscd.service

%postun -n nscd
if test $1 = 0; then
  /usr/sbin/userdel nscd > /dev/null 2>&1 || :
fi
%systemd_postun_with_restart nscd.service

%files -f glibc.filelist
%dir %{_prefix}/%{_lib}/audit
%if %{buildpower10}
%dir /%{_libdir}/glibc-hwcaps/power10
%endif
%verify(not md5 size mtime) %config(noreplace) /etc/nsswitch.conf
%verify(not md5 size mtime) %config(noreplace) /etc/ld.so.conf
%verify(not md5 size mtime) %config(noreplace) /etc/rpc
%dir /etc/ld.so.conf.d
%dir %{_prefix}/libexec/getconf
%dir %{_libdir}/gconv
%dir %{_libdir}/gconv/gconv-modules.d
%dir %attr(0700,root,root) /var/cache/ldconfig
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/cache/ldconfig/aux-cache
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /etc/ld.so.cache
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /etc/gai.conf
# If rpm doesn't support %license, then use %doc instead.
%{!?_licensedir:%global license %%doc}
%license COPYING COPYING.LIB LICENSES

%files -f common.filelist common
%dir %{_prefix}/lib/locale
%dir %{_prefix}/lib/locale/C.utf8
%{_prefix}/lib/locale/C.utf8/*

%files all-langpacks
%{_prefix}/lib/locale/locale-archive
%{_prefix}/lib/locale/locale-archive.real
%{_prefix}/share/locale/*/LC_MESSAGES/libc.mo

%files locale-source
%dir %{_prefix}/share/i18n/locales
%{_prefix}/share/i18n/locales/*
%dir %{_prefix}/share/i18n/charmaps
%{_prefix}/share/i18n/charmaps/*

%files -f devel.filelist devel
%if %{glibc_autorequires}
%attr(0755,root,root) %{_rpmconfigdir}/glibc.req
%{_fileattrsdir}/glibc.attr
%endif

%if %{with docs}
%files -f doc.filelist doc
%endif

%files -f static.filelist static

%if  %{need_headers_package}
%files -f headers.filelist -n %{headers_package_name}
%endif

%files -f utils.filelist utils

%files -f gconv.filelist gconv-extra

%files -f nscd.filelist -n nscd
%config(noreplace) /etc/nscd.conf
%dir %attr(0755,root,root) /var/run/nscd
%dir %attr(0755,root,root) /var/db/nscd
/lib/systemd/system/nscd.service
/lib/systemd/system/nscd.socket
%{_tmpfilesdir}/nscd.conf
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/nscd.pid
%attr(0666,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/socket
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/passwd
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/group
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/hosts
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/services
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/passwd
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/group
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/hosts
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/services
%ghost %config(missingok,noreplace) /etc/sysconfig/nscd

%files -f nss_db.filelist -n nss_db
/var/db/Makefile
%files -f nss_hesiod.filelist -n nss_hesiod
%doc hesiod/README.hesiod
%files -f nss-devel.filelist nss-devel

%files -f libnsl.filelist -n libnsl
/%{_lib}/libnsl.so.1

%if %{with benchtests}
%files benchtests -f benchtests.filelist
%endif

%files -f compat-libpthread-nonshared.filelist -n compat-libpthread-nonshared

%if %{without bootstrap}
%files -n sysroot-%{_arch}-%{sysroot_dist}-glibc
%{sysroot_prefix}
%endif

%changelog
* Mon Sep 25 2023 Florian Weimer <fweimer@redhat.com> - 2.34-60.7
- Fix memory leak regression in getaddrinfo (RHEL-2425)

* Tue Sep 19 2023 Carlos O'Donell <carlos@redhat.com> - 2.34-60.6
- CVE-2023-4911 glibc: buffer overflow in ld.so leading to privilege escalation (RHEL-2999)

* Tue Sep 19 2023 Carlos O'Donell <carlos@redhat.com> - 2.34-60.5
- Revert: Always call destructors in reverse constructor order (RHEL-3385)

* Mon Sep 18 2023 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.34-60.4
- CVE-2023-4806 glibc: potential use-after-free in getaddrinfo (RHEL-2425)

* Fri Sep 15 2023 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.34-60.3
- CVE-2023-4813: potential use-after-free in gaih_inet (RHEL-2437)

* Fri Sep 15 2023 Carlos O'Donell <carlos@redhat.com> - 2.34-60.2
- CVE-2023-4527: Stack read overflow in getaddrinfo in no-aaaa mode (#2234715)

* Wed Sep 13 2023 Florian Weimer <fweimer@redhat.com> - 2.34-60.1
- Always call destructors in reverse constructor order (RHEL-3385)

* Wed Feb  8 2023 Florian Weimer <fweimer@redhat.com> - 2.34-60
- Upstream test for ldconfig -p (#2167811)

* Wed Feb  8 2023 Florian Weimer <fweimer@redhat.com> - 2.34-59
- Fix ldconfig -p on i686 (#2167811)

* Wed Jan 25 2023 Florian Weimer <fweimer@redhat.com> - 2.34-58
- Enhance internal tunables ABI stability (awk iteration order) (#2162962)

* Tue Jan 17 2023 Florian Weimer <fweimer@redhat.com> - 2.34-57
- Sync with upstream branch release/2.34/master,
  commit 6484ae5b8c4d4314f748e4d3c9a9baa5385e57c5
- malloc: Fix -Wuse-after-free warning in tst-mallocalign1 [BZ #26779]
- s_sincosf.h: Change pio4 type to float [BZ #28713]
- math: Properly cast X_TLOSS to float [BZ #28713]
- Regenerate ulps on x86_64 with GCC 12
- Avoid -Wuse-after-free in tests [BZ #26779].
- Fix build of nptl/tst-thread_local1.cc with GCC 12
- Fix stdio-common tests for GCC 12 -Waddress
- Fix stdlib/tst-setcontext.c for GCC 12 -Warray-compare
- resolv: Avoid GCC 12 false positive warning [BZ #28439].
- intl: Avoid -Wuse-after-free [BZ #26779]
- elf: Drop elf/tls-macros.h in favor of __thread and tls_model attributes [BZ #28152] [BZ #28205]
- time: Set daylight to 1 for matching DST/offset change (RHBZ#2155352)
- elf/tst-tlsopt-powerpc fails when compiled with -mcpu=power10 (BZ# 29776)
- time: Use 64 bit time on tzfile
- nscd: Use 64 bit time_t on libc nscd routines (BZ# 29402)
- nis: Build libnsl with 64 bit time_t
- Use LFS and 64 bit time for installed programs (BZ #15333)

* Mon Dec 12 2022 Tulio Magno Quites Machado Filho <tuliom@redhat.com> - 2.34-56
- Earlier removal of alternative multilibs (#2149994)

* Mon Dec 12 2022 Tulio Magno Quites Machado Filho <tuliom@redhat.com> - 2.34-55
- Earlier removal of alternative multilibs (#2149994)

* Mon Dec 12 2022 Florian Weimer <fweimer@redhat.com> - 2.34-54
- Install kernel header files into the sysroot subpackage (#2149644)

* Wed Dec 07 2022 Arjun Shankar <arjun@redhat.com> - 2.34-53
- Sync with upstream branch release/2.34/master,
  commit a4217408a3d6050a7f42ac23adb6ac7218dca85f:
- Apply asm redirections in syslog.h before first use [BZ #27087]
- _Static_assert needs two arguments for compatibility with GCC before 9

* Wed Nov 30 2022 Florian Weimer <fweimer@redhat.com> - 2.34-52
- Add noarch sysroot subpackages (#2149644)

* Tue Nov 29 2022 Florian Weimer <fweimer@redhat.com> - 2.34-51
- Prepare for integration of GCC 8 compatible _Static_assert (#2149102)

* Fri Nov 25 2022 Arjun Shankar <arjun@redhat.com> - 2.34-50
- Sync with upstream branch release/2.34/master,
  commit 405b8ae13540e9fd614df614e3361ebf9abd14cf:
- elf: Fix wrong fscanf usage on tst-pldd
- Allow for unpriviledged nested containers
- elf: Fix wrong fscanf usage on tst-pldd
- x86: Fix wcsnlen-avx2 page cross length comparison [BZ #29591]
- elf: Fix rtld-audit trampoline for aarch64

* Mon Nov 14 2022 Arjun Shankar <arjun@redhat.com> - 2.34-49
- Sync with upstream branch release/2.34/master,
  commit: 75b0edb7ef338084e53925139ae81fb0dfc07dd4:
- Update NEWS file in the right place
- Linux: Support __IPC_64 in sysvctl *ctl command arguments (bug 29771)
- io: Fix use-after-free in ftw [BZ #26779]
- io: Fix ftw internal realloc buffer (BZ #28126)
- regex: fix buffer read overrun in search [BZ#28470]
- regex: copy back from Gnulib
- Allow #pragma GCC in headers in conformtest
- Fix memmove call in vfprintf-internal.c:group_number
- mktime: improve heuristic for ca-1986 Indiana DST
- Makerules: fix MAKEFLAGS assignment for upcoming make-4.4 [BZ# 29564]
- linux: Fix generic struct_stat for 64 bit time (BZ# 29657)
- elf: Do not completely clear reused namespace in dlmopen (bug 29600)
- nss: Use shared prefix in IPv4 address in tst-reload1
- nss: Fix tst-nss-files-hosts-long on single-stack hosts (bug 24816)
- nss: Implement --no-addrconfig option for getent

* Thu Oct 13 2022 Arjun Shankar <arjun@redhat.com> - 2.34-48
- Handle non-hostname CNAME aliases during name resolution (#2129005)
- Sync with upstream branch release/2.34/master,
  commit e3976287b22422787f3cc6fc9adda58304b55bd9:
- nscd: Drop local address tuple variable [BZ #29607]
- x86-64: Require BMI1/BMI2 for AVX2 strrchr and wcsrchr implementations
- x86-64: Require BMI2 and LZCNT for AVX2 memrchr implementation
- x86-64: Require BMI2 for AVX2 (raw|w)memchr implementations
- x86-64: Require BMI2 for AVX2 wcs(n)cmp implementations
- x86-64: Require BMI2 for AVX2 strncmp implementation
- x86-64: Require BMI2 for AVX2 strcmp implementation
- x86-64: Require BMI2 for AVX2 str(n)casecmp implementations
- x86: include BMI1 and BMI2 in x86-64-v3 level
- nptl: Add backoff mechanism to spinlock loop
- sysdeps: Add 'get_fast_jitter' interace in fast-jitter.h
- nptl: Effectively skip CAS in spinlock loop
- Move assignment out of the CAS condition
- Add LLL_MUTEX_READ_LOCK [BZ #28537]
- Avoid extra load with CAS in __pthread_mutex_clocklock_common [BZ #28537]
- Avoid extra load with CAS in __pthread_mutex_lock_full [BZ #28537]
- resolv: Fix building tst-resolv-invalid-cname for earlier C standards
- nss_dns: Rewrite _nss_dns_gethostbyname4_r using current interfaces
- resolv: Add new tst-resolv-invalid-cname
- nss_dns: In gaih_getanswer_slice, skip strange aliases (bug 12154)
  (#2129005)
- nss_dns: Rewrite getanswer_r to match getanswer_ptr (bug 12154, bug 29305)
- nss_dns: Remove remnants of IPv6 address mapping
- nss_dns: Rewrite _nss_dns_gethostbyaddr2_r and getanswer_ptr
- nss_dns: Split getanswer_ptr from getanswer_r
- resolv: Add DNS packet parsing helpers geared towards wire format
- resolv: Add internal __ns_name_length_uncompressed function
- resolv: Add the __ns_samebinaryname function
- resolv: Add internal __res_binary_hnok function
- resolv: Add tst-resolv-aliases
- resolv: Add tst-resolv-byaddr for testing reverse lookup
- gconv: Use 64-bit interfaces in gconv_parseconfdir (bug 29583)
- elf: Fix hwcaps string size overestimation
- nscd: Fix netlink cache invalidation if epoll is used [BZ #29415]
- Apply asm redirections in wchar.h before first use
- Apply asm redirections in stdio.h before first use [BZ #27087]
- elf: Call __libc_early_init for reused namespaces (bug 29528)

* Tue Oct 11 2022 Florian Weimer <fweimer@redhat.com> - 2.34-47
- Simplify the glibc system call profile (#2117712)

* Tue Oct 11 2022 Florian Weimer <fweimer@redhat.com> - 2.34-46
- DSO dependency sort must put new map first even if in cycle (#2128615)

* Tue Oct 11 2022 Florian Weimer <fweimer@redhat.com> - 2.34-45
- Run tst-audit-tlsdesc{,-dlopen} on all architectures (#2118666)

* Thu Oct 06 2022 Arjun Shankar <arjun@redhat.com> - 2.34-44
- wrap-find-debuginfo.sh: Use nm --format=posix instead of --format=just-symbols

* Mon Oct 03 2022 Arjun Shankar <arjun@redhat.com> - 2.34-43
- Remove .annobin* symbols from ld.so (#2126477)

* Tue Sep 06 2022 Arjun Shankar <arjun@redhat.com> - 2.34-42
- Co-Authored-By: Benjamin Herrenschmidt <benh@amazon.com>
- Retain .gnu_debuglink section in libc.so.6 (#2090744)
- Remove redundant ld.so debuginfo file (#2090744)

* Tue Aug 23 2022 Arjun Shankar <arjun@redhat.com> - 2.34-41
- Sync with upstream branch release/2.34/master,
  commit 68507377f249d165f1f35502d96e9365edb07d9a:
- socket: Check lengths before advancing pointer in CMSG_NXTHDR
- alpha: Fix generic brk system call emulation in __brk_call (bug 29490)
- stdlib: Fixup mbstowcs NULL __dst handling. [BZ #29279]
- stdlib: Remove attr_write from mbstows if dst is NULL [BZ: 29265]
- Update syscall lists for Linux 5.19
- dlfcn: Pass caller pointer to static dlopen implementation (bug 29446)

* Fri Jul 22 2022 Arjun Shankar <arjun@redhat.com> - 2.34-40
- Sync with upstream branch release/2.34/master,
  commit b2f32e746492615a6eb3e66fac1e766e32e8deb1:
- malloc: Simplify implementation of __malloc_assert
- Update syscall-names.list for Linux 5.18
- x86: Add missing IS_IN (libc) check to strncmp-sse4_2.S
- x86: Move mem{p}{mov|cpy}_{chk_}erms to its own file
- x86: Move and slightly improve memset_erms
- x86: Add definition for __wmemset_chk AVX2 RTM in ifunc impl list
- x86: Put wcs{n}len-sse4.1 in the sse4.1 text section
- x86: Align entry for memrchr to 64-bytes.
- x86: Add BMI1/BMI2 checks for ISA_V3 check
- x86: Cleanup bounds checking in large memcpy case
- x86: Add bounds `x86_non_temporal_threshold`
- x86: Add sse42 implementation to strcmp's ifunc
- x86: Fix misordered logic for setting `rep_movsb_stop_threshold`
- x86: Align varshift table to 32-bytes
- x86: ZERO_UPPER_VEC_REGISTERS_RETURN_XTEST expect no transactions
- x86: Shrink code size of memchr-evex.S
- x86: Shrink code size of memchr-avx2.S
- x86: Optimize memrchr-avx2.S
- x86: Optimize memrchr-evex.S
- x86: Optimize memrchr-sse2.S
- x86: Add COND_VZEROUPPER that can replace vzeroupper if no `ret`
- x86: Create header for VEC classes in x86 strings library
- x86_64: Add strstr function with 512-bit EVEX
- x86-64: Ignore r_addend for R_X86_64_GLOB_DAT/R_X86_64_JUMP_SLOT
- x86_64: Implement evex512 version of strlen, strnlen, wcslen and wcsnlen
- x86_64: Remove bzero optimization
- x86_64: Remove end of line trailing spaces
- nptl: Fix ___pthread_unregister_cancel_restore asynchronous restore
- linux: Fix mq_timereceive check for 32 bit fallback code (BZ 29304)

* Fri Jun 24 2022 Florian Weimer <fweimer@redhat.com> - 2.34-39
- Add the no-aaaa DNS stub resolver option (#2096191)

* Tue Jun 14 2022 Arjun Shankar <arjun@redhat.com> - 2.34-38
- Sync with upstream branch release/2.34/master,
  commit 94ab2088c37d8e4285354af120b7ed6b887b9e53:
- nss: handle stat failure in check_reload_and_get (BZ #28752)
- nss: add assert to DB_LOOKUP_FCT (BZ #28752)
- nios2: Remove _dl_skip_args usage (BZ# 29187)
- hppa: Remove _dl_skip_args usage (BZ# 29165)
- nptl: Fix __libc_cleanup_pop_restore asynchronous restore (BZ#29214)

* Wed Jun  8 2022 Florian Weimer <fweimer@redhat.com> - 2.34-37
- Enable rseq by default and add GLIBC_2.35 rseq symbols (#2085529)

* Wed Jun  8 2022 Florian Weimer <fweimer@redhat.com> - 2.34-36
- Sync with upstream branch release/2.34/master,
  commit 4c92a1041257c0155c6aa7a182fe5f78e477b0e6:
- powerpc: Fix VSX register number on __strncpy_power9 [BZ #29197]
- socket: Fix mistyped define statement in socket/sys/socket.h (BZ #29225)
- iconv: Use 64 bit stat for gconv_parseconfdir (BZ# 29213)
- catgets: Use 64 bit stat for __open_catalog (BZ# 29211)
- inet: Use 64 bit stat for ruserpass (BZ# 29210)
- socket: Use 64 bit stat for isfdtype (BZ# 29209)
- posix: Use 64 bit stat for fpathconf (_PC_ASYNC_IO) (BZ# 29208)
- posix: Use 64 bit stat for posix_fallocate fallback (BZ# 29207)
- misc: Use 64 bit stat for getusershell (BZ# 29204)
- misc: Use 64 bit stat for daemon (BZ# 29203)

* Tue May 31 2022 Arjun Shankar <arjun@redhat.com> - 2.34-35
- Sync with upstream branch release/2.34/master,
  commit ff450cdbdee0b8cb6b9d653d6d2fa892de29be31:
- Fix deadlock when pthread_atfork handler calls pthread_atfork or dlclose
- x86: Fallback {str|wcs}cmp RTM in the ncmp overflow case [BZ #29127]
- string.h: fix __fortified_attr_access macro call [BZ #29162]
- linux: Add a getauxval test [BZ #23293]
- rtld: Use generic argv adjustment in ld.so [BZ #23293]
- S390: Enable static PIE

* Thu May 19 2022 Florian Weimer <fweimer@redhat.com> - 2.34-34
- Sync with upstream branch release/2.34/master,
  commit ede8d94d154157d269b18f3601440ac576c1f96a:
- csu: Implement and use _dl_early_allocate during static startup
- Linux: Introduce __brk_call for invoking the brk system call
- Linux: Implement a useful version of _startup_fatal
- ia64: Always define IA64_USE_NEW_STUB as a flag macro
- Linux: Define MMAP_CALL_INTERNAL
- i386: Honor I386_USE_SYSENTER for 6-argument Linux system calls
- i386: Remove OPTIMIZE_FOR_GCC_5 from Linux libc-do-syscall.S
- elf: Remove __libc_init_secure
- Linux: Consolidate auxiliary vector parsing (redo)
- Linux: Include <dl-auxv.h> in dl-sysdep.c only for SHARED
- Revert "Linux: Consolidate auxiliary vector parsing"
- Linux: Consolidate auxiliary vector parsing
- Linux: Assume that NEED_DL_SYSINFO_DSO is always defined
- Linux: Remove DL_FIND_ARG_COMPONENTS
- Linux: Remove HAVE_AUX_SECURE, HAVE_AUX_XID, HAVE_AUX_PAGESIZE
- elf: Merge dl-sysdep.c into the Linux version
- elf: Remove unused NEED_DL_BASE_ADDR and _dl_base_addr
- x86: Optimize {str|wcs}rchr-evex
- x86: Optimize {str|wcs}rchr-avx2
- x86: Optimize {str|wcs}rchr-sse2
- x86: Cleanup page cross code in memcmp-avx2-movbe.S
- x86: Remove memcmp-sse4.S
- x86: Small improvements for wcslen
- x86: Remove AVX str{n}casecmp
- x86: Add EVEX optimized str{n}casecmp
- x86: Add AVX2 optimized str{n}casecmp
- x86: Optimize str{n}casecmp TOLOWER logic in strcmp-sse42.S
- x86: Optimize str{n}casecmp TOLOWER logic in strcmp.S
- x86: Remove strspn-sse2.S and use the generic implementation
- x86: Remove strpbrk-sse2.S and use the generic implementation
- x86: Remove strcspn-sse2.S and use the generic implementation
- x86: Optimize strspn in strspn-c.c
- x86: Optimize strcspn and strpbrk in strcspn-c.c
- x86: Code cleanup in strchr-evex and comment justifying branch
- x86: Code cleanup in strchr-avx2 and comment justifying branch
- x86_64: Remove bcopy optimizations
- x86-64: Remove bzero weak alias in SS2 memset
- x86_64/multiarch: Sort sysdep_routines and put one entry per line
- x86: Improve L to support L(XXX_SYMBOL (YYY, ZZZ))
- fortify: Ensure that __glibc_fortify condition is a constant [BZ #29141]

* Thu May 12 2022 Florian Weimer <fweimer@redhat.com> - 2.34-33
- Sync with upstream branch release/2.34/master,
  commit 91c2e6c3db44297bf4cb3a2e3c40236c5b6a0b23:
- dlfcn: Implement the RTLD_DI_PHDR request type for dlinfo
- manual: Document the dlinfo function
- x86: Fix fallback for wcsncmp_avx2 in strcmp-avx2.S [BZ #28896]
- x86: Fix bug in strncmp-evex and strncmp-avx2 [BZ #28895]
- x86: Set .text section in memset-vec-unaligned-erms
- x86-64: Optimize bzero
- x86: Remove SSSE3 instruction for broadcast in memset.S (SSE2 Only)
- x86: Improve vec generation in memset-vec-unaligned-erms.S
- x86-64: Fix strcmp-evex.S
- x86-64: Fix strcmp-avx2.S
- x86: Optimize strcmp-evex.S
- x86: Optimize strcmp-avx2.S
- manual: Clarify that abbreviations of long options are allowed
- Add HWCAP2_AFP, HWCAP2_RPRES from Linux 5.17 to AArch64 bits/hwcap.h
- aarch64: Add HWCAP2_ECV from Linux 5.16
- Add SOL_MPTCP, SOL_MCTP from Linux 5.16 to bits/socket.h
- Update kernel version to 5.17 in tst-mman-consts.py
- Update kernel version to 5.16 in tst-mman-consts.py
- Update syscall lists for Linux 5.17
- Add ARPHRD_CAN, ARPHRD_MCTP to net/if_arp.h
- Update kernel version to 5.15 in tst-mman-consts.py
- Add PF_MCTP, AF_MCTP from Linux 5.15 to bits/socket.h

* Thu Apr 28 2022 Carlos O'Donell <carlos@redhat.com> - 2.34-32
- Sync with upstream branch release/2.34/master,
  commit c66c92181ddbd82306537a608e8c0282587131de:
- posix/glob.c: update from gnulib (BZ#25659)
- linux: Fix fchmodat with AT_SYMLINK_NOFOLLOW for 64 bit time_t (BZ#29097)

* Wed Apr 27 2022 Carlos O'Donell <carlos@redhat.com> - 2.34-31
- Sync with upstream branch release/2.34/master,
  commit 55640ed3fde48360a8e8083be4843bd2dc7cecfe:
- i386: Regenerate ulps
- linux: Fix missing internal 64 bit time_t stat usage
- x86: Optimize L(less_vec) case in memcmp-evex-movbe.S
- x86: Don't set Prefer_No_AVX512 for processors with AVX512 and AVX-VNNI
- x86-64: Use notl in EVEX strcmp [BZ #28646]
- x86: Shrink memcmp-sse4.S code size
- x86: Double size of ERMS rep_movsb_threshold in dl-cacheinfo.h
- x86: Optimize memmove-vec-unaligned-erms.S
- x86-64: Replace movzx with movzbl
- x86-64: Remove Prefer_AVX2_STRCMP
- x86-64: Improve EVEX strcmp with masked load
- x86: Replace sse2 instructions with avx in memcmp-evex-movbe.S
- x86: Optimize memset-vec-unaligned-erms.S
- x86: Optimize memcmp-evex-movbe.S for frontend behavior and size
- x86: Modify ENTRY in sysdep.h so that p2align can be specified
- x86-64: Optimize load of all bits set into ZMM register [BZ #28252]
- scripts/glibcelf.py: Mark as UNSUPPORTED on Python 3.5 and earlier
- dlfcn: Do not use rtld_active () to determine ld.so state (bug 29078)
- INSTALL: Rephrase -with-default-link documentation
- misc: Fix rare fortify crash on wchar funcs. [BZ 29030]
- Default to --with-default-link=no (bug 25812)
- scripts: Add glibcelf.py module

* Thu Apr 21 2022 Carlos O'Donell <carlos@redhat.com> - 2.34-30
- Sync with upstream branch release/2.34/master,
  commit 71326f1f2fd09dafb9c34404765fb88129e94237:
- nptl: Fix pthread_cancel cancelhandling atomic operations
- mips: Fix mips64n32 64 bit time_t stat support (BZ#29069)
- hurd: Fix arbitrary error code
- nptl: Handle spurious EINTR when thread cancellation is disabled (BZ#29029)
- S390: Add new s390 platform z16.
- NEWS: Update fixed bug list for LD_AUDIT backports.
- hppa: Fix bind-now audit (BZ #28857)
- elf: Replace tst-audit24bmod2.so with tst-audit24bmod2
- Fix elf/tst-audit25a with default bind now toolchains
- elf: Fix runtime linker auditing on aarch64 (BZ #26643)
- elf: Issue la_symbind for bind-now (BZ #23734)
- elf: Fix initial-exec TLS access on audit modules (BZ #28096)
- elf: Add la_activity during application exit
- elf: Do not fail for failed dlmopen on audit modules (BZ #28061)
- elf: Issue audit la_objopen for vDSO
- elf: Add audit tests for modules with TLSDESC
- elf: Avoid unnecessary slowdown from profiling with audit (BZ#15533)
- elf: Add _dl_audit_pltexit
- elf: Add _dl_audit_pltenter
- elf: Add _dl_audit_preinit
- elf: Add _dl_audit_symbind_alt and _dl_audit_symbind
- elf: Add _dl_audit_objclose
- elf: Add _dl_audit_objsearch
- elf: Add _dl_audit_activity_map and _dl_audit_activity_nsid
- elf: Add _dl_audit_objopen
- elf: Move la_activity (LA_ACT_ADD) after _dl_add_to_namespace_list() (BZ #28062)
- elf: Move LAV_CURRENT to link_lavcurrent.h
- elf: Fix elf_get_dynamic_info() for bootstrap
- elf: Fix dynamic-link.h usage on rtld.c
- elf: Fix elf_get_dynamic_info definition
- elf: Avoid nested functions in the loader [BZ #27220]
- powerpc: Delete unneeded ELF_MACHINE_BEFORE_RTLD_RELOC
- hppa: Use END instead of PSEUDO_END in swapcontext.S
- hppa: Implement swapcontext in assembler (bug 28960)

* Tue Mar 15 2022 Florian Weimer <fweimer@redhat.com> - 2.34-29
- Sync with upstream branch release/2.34/master,
  commit 224d8c1890b6c57c7e4e8ddbb792dd9552086704:
- debug: Synchronize feature guards in fortified functions [BZ #28746]
- debug: Autogenerate _FORTIFY_SOURCE tests
- Enable _FORTIFY_SOURCE=3 for gcc 12 and above
- fortify: Fix spurious warning with realpath
- __glibc_unsafe_len: Fix comment
- debug: Add tests for _FORTIFY_SOURCE=3
- Make sure that the fortified function conditionals are constant
- Don't add access size hints to fortifiable functions
- nss: Protect against errno changes in function lookup (bug 28953)
- nss: Do not mention NSS test modules in <gnu/lib-names.h>
- io: Add fsync call in tst-stat
- hppa: Fix warnings from _dl_lookup_address
- nptl: Fix cleanups for stack grows up [BZ# 28899]
- hppa: Revise gettext trampoline design
- hppa: Fix swapcontext
- Fix elf/tst-audit2 on hppa
- localedef: Handle symbolic links when generating locale-archive
- NEWS: Add a bug fix entry for BZ #28896
- x86: Fix TEST_NAME to make it a string in tst-strncmp-rtm.c
- x86: Test wcscmp RTM in the wcsncmp overflow case [BZ #28896]
- x86: Fallback {str|wcs}cmp RTM in the ncmp overflow case [BZ #28896]
- string: Add a testcase for wcsncmp with SIZE_MAX [BZ #28755]
- linux: fix accuracy of get_nprocs and get_nprocs_conf [BZ #28865]
- Add reference to BZ#28860 on NEWS
- linux: Fix missing __convert_scm_timestamps (BZ #28860)

* Tue Mar 08 2022 Arjun Shankar <arjun@redhat.com> - 2.34-28
- Reduce installed size of some langpacks by de-duplicating LC_CTYPE (#2054789)
- Fix localedef so it can handle symbolic links when generating locale-archive.
- Drop glibc-fedora-localedef.patch and adjust locale installation
  accordingly so that installed content remains unchanged.

* Mon Feb 28 2022 Florian Weimer <fweimer@redhat.com> - 2.34-27
- Fix regression (ldd crash) during dependency sorting in ld.so (#2058230)

* Mon Feb 28 2022 Florian Weimer <fweimer@redhat.com> - 2.34-26
- Fix localedef compilation of C.UTF-8 (empty LC_MONETARY keywords) (#2058224)

* Thu Feb  3 2022 Florian Weimer <fweimer@redhat.com> - 2.34-25
- Sync with upstream branch release/2.34/master,
  commit 6eaf10cbb78d22eae7999d9de55f6b93999e0860:
- socket: Do not use AF_NETLINK in __opensock
- hurd if_index: Explicitly use AF_INET for if index discovery
- Linux: Simplify __opensock and fix race condition [BZ #28353]
- linux: __get_nprocs_sched: do not feed CPU_COUNT_S with garbage [BZ #28850]

* Tue Feb  1 2022 Florian Weimer <fweimer@redhat.com> - 2.34-24
- Sync with upstream branch release/2.34/master,
  commit 008003dc6e83439c5e04a744b7fd8197df19096e:
- tst-socket-timestamp-compat.c: Check __TIMESIZE [BZ #28837]
- Linux: Only generate 64 bit timestamps for 64 bit time_t recvmsg/recvmmsg
- linux: Fix ancillary 64-bit time timestamp conversion (BZ #28349, BZ#28350)
- support: Add support_socket_so_timestamp_time64

* Tue Feb  1 2022 Florian Weimer <fweimer@redhat.com> - 2.34-23
- Align with glibc 2.35 version of C.UTF-8

* Tue Feb  1 2022 Florian Weimer <fweimer@redhat.com> - 2.34-22
- Sync with upstream branch release/2.34/master,
  commit aa601d024424c40ae9a69b0c4e394a70ea0570c8:
- x86: Use CHECK_FEATURE_PRESENT to check HLE [BZ #27398]
- x86: Filter out more Intel CPUs for TSX [BZ #27398]
- Fix glibc 2.34 ABI omission (missing GLIBC_2.34 in dynamic loader)
- x86: Fix __wcsncmp_evex in strcmp-evex.S [BZ# 28755]
- x86: Fix __wcsncmp_avx2 in strcmp-avx2.S [BZ# 28755]

* Mon Jan 24 2022 Florian Weimer <fweimer@redhat.com> - 2.34-21
- Sync with upstream branch release/2.34/master,
  commit 3438bbca90895d32825a52e31a77dc44d273c1c1:
- Linux: Detect user namespace support in io/tst-getcwd-smallbuff
- realpath: Avoid overwriting preexisting error
- CVE-2021-3999: getcwd: Set errno to ERANGE for size == 1
- tst-realpath-toolong: Fix hurd build
- CVE-2021-3998: realpath: ENAMETOOLONG for result larger than PATH_MAX
- stdlib: Fix formatting of tests list in Makefile
- stdlib: Sort tests in Makefile
- support: Add helpers to create paths longer than PATH_MAX
- powerpc: Fix unrecognized instruction errors with recent binutils
- x86: use default cache size if it cannot be determined [BZ #28784]
- CVE-2022-23218: Buffer overflow in sunrpc svcunix_create (bug 28768)
- sunrpc: Test case for clnt_create "unix" buffer overflow (bug 22542)
- CVE-2022-23219: Buffer overflow in sunrpc clnt_create for "unix" (bug 22542)
- socket: Add the __sockaddr_un_set function
- Disable debuginfod in printer tests [BZ #28757]
- Update syscall lists for Linux 5.16

* Wed Jan 19 2022 Florian Weimer <fweimer@redhat.com> - 2.34-20
- More reliable CPU compatibility diagnostics (#2040657)

* Fri Jan 14 2022 Florian Weimer <fweimer@redhat.com> - 2.34-19
- Optionally accelerate sched_getcpu using rseq (#2024347)

* Thu Jan 13 2022 Florian Weimer <fweimer@redhat.com> - 2.34-18
- Backport optimized ELF dependency sorting algorithm (#2032647)

* Thu Jan 13 2022 Florian Weimer <fweimer@redhat.com> - 2.34-17
- Sync with upstream branch release/2.34/master,
  commit 2fe2af88abd13ae5636881da2e26f461ecb7dfb5
- i386: Remove broken CAN_USE_REGISTER_ASM_EBP (bug 28771)
- Update syscall lists for Linux 5.15
- powerpc: Fix unrecognized instruction errors with recent GCC
- timezone: test-case for BZ #28707
- timezone: handle truncated timezones from tzcode-2021d and later (BZ #28707)
- Fix subscript error with odd TZif file [BZ #28338]
- AArch64: Check for SVE in ifuncs [BZ #28744]
- intl/plural.y: Avoid conflicting declarations of yyerror and yylex
- Linux: Fix 32-bit vDSO for clock_gettime on powerpc32
- linux: Add sparck brk implementation
- Update sparc libm-test-ulps
- Update hppa libm-test-ulps
- riscv: align stack before calling _dl_init [BZ #28703]
- riscv: align stack in clone [BZ #28702]
- powerpc64[le]: Allocate extra stack frame on syscall.S
- elf: Fix tst-cpu-features-cpuinfo for KVM guests on some AMD systems [BZ #28704]
- nss: Use "files dns" as the default for the hosts database (bug 28700)
- arm: Guard ucontext _rtld_global_ro access by SHARED, not PIC macro
- mips: increase stack alignment in clone to match the ABI
- mips: align stack in clone [BZ #28223]

* Tue Dec 14 2021 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.34-16
- Enable PIE by default on all architectures (#1988382)

* Tue Dec 14 2021 Florian Weimer <fweimer@redhat.com> - 2.34-15
- Sync with upstream branch release/2.34/master,
  commit 06865865151579d1aa17d38110060a68b85c5d90:
- pthread/tst-cancel28: Fix barrier re-init race condition
- Use $(pie-default) with conformtest
- Run conform/ tests using newly built libc
- nptl: Add one more barrier to nptl/tst-create1

* Fri Dec 10 2021 Florian Weimer <fweimer@redhat.com> - 2.34-13
- x86-64: Remove LD_PREFER_MAP_32BIT_EXEC support (#2029410)

* Fri Dec 10 2021 Florian Weimer <fweimer@redhat.com> - 2.34-12
- Add /usr/bin/ld.so --list-diagnostics (#2023422)

* Tue Dec  7 2021 Florian Weimer <fweimer@redhat.com> - 2.34-11
- backtrace function crashes without vDSO on ppc64le (#2027789)

* Fri Dec  3 2021 Florian Weimer <fweimer@redhat.com> - 2.34-10
- Sync with upstream branch release/2.34/master,
  commit 387bff63dc2dccd62b09aa26dccf8cdc5f3c985c:
- powerpc64[le]: Fix CFI and LR save address for asm syscalls [BZ #28532]
- linux: Use /proc/stat fallback for __get_nprocs_conf (BZ #28624)
- nptl: Do not set signal mask on second setjmp return [BZ #28607]
- s390: Use long branches across object boundaries (jgh instead of jh)
- elf: Earlier missing dynamic segment check in _dl_map_object_from_fd
- gconv: Do not emit spurious NUL character in ISO-2022-JP-3 (bug 28524)

* Tue Nov 16 2021 Arjun Shankar <arjun@redhat.com> - 2.34-9
- Create /{bin,lib,lib64,sbin} as symbolic links in test-container

* Wed Nov  3 2021 Florian Weimer <fweimer@redhat.com> - 2.34-8
- Sync with upstream branch release/2.34/master,
  commit 6548a9bdba95b3e1fcdbd85445342467e4b0cd4f:
- Avoid warning: overriding recipe for .../tst-ro-dynamic-mod.so
- ld.so: Initialize bootstrap_map.l_ld_readonly [BZ #28340]
- ld.so: Replace DL_RO_DYN_SECTION with dl_relocate_ld [BZ #28340]
- Handle NULL input to malloc_usable_size [BZ #28506]
- elf: Avoid deadlock between pthread_create and ctors [BZ #28357]
- timex: Use 64-bit fields on 32-bit TIMESIZE=64 systems (BZ #28469)
- y2038: Use a common definition for stat for sparc32
- elf: Replace nsid with args.nsid [BZ #27609]
- S390: Add PCI_MIO and SIE HWCAPs
- support: Also return fd when it is 0

* Fri Oct  1 2021 Florian Weimer <fweimer@redhat.com> - 2.34-7
- Drop glibc-rh1992702-*.patch, applied upstream.  (#1992702)
- Sync with upstream branch release/2.34/master,
  commit a996d13b8a2e101bedbb1bdaa7ffcfea3b959bb2:
- Add missing braces to bsearch inline implementation [BZ #28400]
- Suppress -Wcast-qual warnings in bsearch
- linux: Revert the use of sched_getaffinity on get_nproc (BZ #28310)
- linux: Simplify get_nprocs
- misc: Add __get_nprocs_sched
- nptl: pthread_kill must send signals to a specific thread [BZ #28407]
- support: Add check for TID zero in support_wait_for_thread_exit

* Thu Sep 23 2021 Florian Weimer <fweimer@redhat.com> - 2.34-6
- Sync with upstream branch release/2.34/master,
  commit 33adeaa3e2b9143c38884bc5aa65ded222ed274e:
- nptl: Avoid setxid deadlock with blocked signals in thread exit [BZ #28361]
- Use support_open_dev_null_range io/tst-closefrom, misc/tst-close_range, and
  posix/tst-spawn5 (BZ #28260)
- support: Add support_open_dev_null_range
- nptl: Fix type of pthread_mutexattr_getrobust_np,
  pthread_mutexattr_setrobust_np (bug 28036)
- nptl: pthread_kill needs to return ESRCH for old programs (bug 19193)

* Wed Sep 15 2021 Florian Weimer <fweimer@redhat.com> - 2.34-5
- Use system CPU count for sysconf(_SC_NPROCESSORS_*) (#1992702)

* Wed Sep 15 2021 Florian Weimer <fweimer@redhat.com> - 2.34-4
- Sync with upstream branch release/2.34/master,
  commit 4ed990e5b97a61f29f929bdeb36c5b2abb547a64:
- Add MADV_POPULATE_READ and MADV_POPULATE_WRITE from Linux 5.14 to
  bits/mman-linux.h
- Update kernel version to 5.14 in tst-mman-consts.py
- Update syscall lists for Linux 5.14
- Use Linux 5.14 in build-many-glibcs.py
- Fix failing nss/tst-nss-files-hosts-long with local resolver
- iconvconfig: Fix behaviour with --prefix [BZ #28199]
- nptl: Fix race between pthread_kill and thread exit (swbz#12889, #1994068)
- nptl: pthread_kill, pthread_cancel should not fail after exit
  (swbz#19193, #1994068)
- support: Add support_wait_for_thread_exit
- MIPS: Setup errno for {f,l,}xstat
- x86-64: Use testl to check __x86_string_control
- elf: Fix missing colon in LD_SHOW_AUXV output (swbz#28253, #1995648)
- librt: add test (swbz#28213, #1994264)
- CVE-2021-38604: fix NULL pointer dereference in mq_notify
  (swbz#28213, #1994264)
- Linux: Fix fcntl, ioctl, prctl redirects for _TIME_BITS=64 (bug 28182)
- iconv_charmap: Close output file when done
- copy_and_spawn_sgid: Avoid double calls to close()
- gaiconf_init: Avoid double-free in label and precedence lists
- gconv_parseconfdir: Fix memory leak
- ldconfig: avoid leak on empty paths in config file

* Wed Sep 15 2021 Florian Weimer <fweimer@redhat.com> - 2.34-3
- Switch to upstream version of C.UTF-8 (#1997589)

* Wed Aug 25 2021 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.34-2
- Disable dependencies and linking for libc_malloc_debug.so (#1985048).

* Mon Aug  2 2021 Florian Weimer <fweimer@redhat.com> - 2.34-1
- Switch to glibc 2.34 release tarball:
- Update ChangeLog.old/ChangeLog.23.
- Prepare for glibc 2.34 release.
- po/nl.po: Update Dutch translation.
- Update install.texi, and regenerate INSTALL.
- Update translations.
- Update NEWS.
- NEWS: Fix typos, grammar, and missing words
- elf: Fix audit regression
