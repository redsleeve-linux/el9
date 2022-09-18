# RedSleeve / EL9

**RedSleeve Linux** is a 3rd party [ARM](http://en.wikipedia.org/wiki/ARM_architecture) port of a Linux distribution of a Prominent North American Enterprise Linux Vendor (PNAELV). They object to being referred to by name in the context of clones and ports of their distribution, but if you are aware of [CentOS](http://en.wikipedia.org/wiki/CentOS), you can probably guess what [RedSleeve](http://www.redsleeve.org) is based on. 


## Extra build instructions

Some packages needed some manual love and care to build, but not really a patch:

### BaseOS ###

| Package | SRPM | instruction
|---|---|---
| acpica-tools | acpica-tools-20210604-3.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| elfutils | elfutils-0.186-1.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| gmp | gmp-6.2.0-10.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| gnutls | gnutls-3.7.3-9.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| libkcapi | libkcapi-1.3.1-3.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| libxcrypt | libxcrypt-4.4.18-3.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| libssh | libssh-0.9.6-3.el9.src.rpm | must be build with '--nocheck'
| nettle | nettle-3.7.3-2.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| python-dmidecode | python-dmidecode-3.12.2-27.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| python-dns | python-dns-2.1.0-6.el9.src.rpm | must be build with '--nocheck'
| sudo | sudo-1.9.5p2-7.el9.src.rpm | must be build with '--nocheck'

### AppStream ###

| Package | SRPM | instruction
|---|---|---
| annobin | annobin-10.54-2.el9.src.rpm | must be build with '--without clangplugin --without llvmplugin --nocheck'
| automake | automake-1.16.2-6.el9.src.rpm | must be build with '--nocheck'
| babl | babl-0.1.86-3.el9.src.rpm | install openssh-clients before build
| certmonger | certmonger-0.79.14-5.el9.src.rpm | must be build with '--nocheck'
| crash | crash-8.0.0-6.el9.src.rpm | build with "linux32"
| criu | criu-3.15-13.el9.src.rpm | build with "linux32"
| festival | festival-2.5.0-17.el9.src.rpm | build with "linux32"
| http-parser | http-parser-2.9.4-6.el9.src.rpm | must be build with '--nocheck'
| ibus | ibus-1.5.25-2.el9.rocky.0.1.src.rpm | must be build with '--nocheck'
| ignition | ignition-2.13.0-1.el9.src.rpm | build with `go-rpm-macros-3.0.9-8.el9` from C9-beta
| ipa | ipa-4.9.8-7.el9_0.src.rpm | build with `-D "eln 1"`
| isomd5sum | isomd5sum-1.2.3-14.el9.src.rpm | build with "linux32"
| ksh | ksh-1.0.0~beta.1-2.el9.src.rpm | build with "linux32"
| lasso | lasso-2.7.0-8.el9.src.rpm | must be build with '--nocheck'
| libomp | libomp-13.0.1-1.el9.src.rpm | build with "linux32"
| llvm | llvm-13.0.1-1.el9.src.rpm | build with "linux32"
| mptcpd | mptcpd-0.8-2.el9.src.rpm | build with `kernel-headers-5.14.0-39.el9` from C9-beta
| nss | nss-3.71.0-7.el9.src.rpm | build with "linux32" and '--nocheck'
| openmpi | openmpi-4.1.1-5.el9.redsleeve.src.rpm | build with "linux32"
| perl-Net-SSLeay | perl-Net-SSLeay-1.92-1.el9.src.rpm | must be build with '--nocheck'
| pgaudit | pgaudit-1.5.0-6.el9.src.rpm | remove '(Pre)' from macros.postgresql before build
| pg_repack | pg_repack-1.4.6-4.el9.src.rpm | remove '(Pre)' from macros.postgresql before build
| postgres-decoderbufs | postgres-decoderbufs-1.4.0-4.Final.el9.src.rpm | remove '(Pre)' from macros.postgresql before build
| postgresql | postgresql-13.7-1.el9_0.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related
| redis | redis-6.2.6-1.el9.src.rpm | build with "linux32"
| ruby | ruby-3.0.3-159.el9.src.rpm | must be build with '--nocheck'
| s-nail | s-nail-14.9.22-6.el9.src.rpm | must be build with '--nocheck'
| satyr | satyr-0.38-3.el9.src.rpm | must be build with '--nocheck'
| squid | squid-5.2-1.el9_0.1.src.rpm | must be build with '--nocheck'
| sscg | sscg-3.0.0-5.el9_0.src.rpm | must be build with '--nocheck'
| tang | tang-11-1.el9.src.rpm | must be build with '--nocheck'
| tbb | tbb-2020.3-8.el9.src.rpm | build with "linux32"
| varnish | varnish-6.6.2-2.el9.src.rpm | must be build with '--nocheck'
| webkit2gtk3 | webkit2gtk3-2.34.6-1.el9.src.rpm | build with "linux32"
| woff2 | woff2-1.0.2-14.el9.src.rpm | needs to be build with '-D "_target_platform redhat-linux-build"'


### extra ###

| Package | SRPM | instruction
|---|---|---
| elinks | elinks-0.12-0.58.pre6.el8.armv6hl.rpm | RPM from RedSleeve 8.6 PowerTools
