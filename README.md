# RedSleeve / EL9

**RedSleeve Linux** is a 3rd party [ARM](http://en.wikipedia.org/wiki/ARM_architecture) port of a Linux distribution of a Prominent North American Enterprise Linux Vendor (PNAELV). They object to being referred to by name in the context of clones and ports of their distribution, but if you are aware of [CentOS](http://en.wikipedia.org/wiki/CentOS), you can probably guess what [RedSleeve](http://www.redsleeve.org) is based on. 


## Extra build instructions

Some packages needed some manual love and care to build, but not really a patch:

### BaseOS ###

| Package | SRPM | instruction
|---|---|---
| acpica-tools | acpica-tools-20210604-5.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| gmp | gmp-6.2.0-10.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| libkcapi | libkcapi-1.3.1-3.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| libxcrypt | libxcrypt-4.4.18-3.el9.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| nettle | nettle-3.8-3.el9_0.src.rpm | must be build on a raspberry for a succesfull test. probably kernel version related 
| python | python3.9-3.9.16-1.el9.src.rpm | build with '-D "_gnu -gnueabihf"'

### AppStream ###

| Package | SRPM | instruction
|---|---|---
| automake | automake-1.16.2-6.el9.src.rpm | must be build with '--nocheck'
| crash | crash-8.0.2-2.el9.src.rpm | build with "linux32"
| criu | criu-3.17-4.el9.src.rpm | build with "linux32"
| festival | festival-2.5.0-17.el9.src.rpm | build with "linux32"
| gcc-toolset-12-annobin | gcc-toolset-12-annobin-11.08-2.el9.src.rpm | must be build with '--nocheck'
| gnome-settings-daemon | gnome-settings-daemon-40.0.1-11.el9_2.src.rpm | must be build with '--without subman' 
| grafana | grafana-9.0.9-2.el9.0.1.src.rpm |  must be build with '--nocheck'
| http-parser | http-parser-2.9.4-6.el9.src.rpm | must be build with '--nocheck'
| ibus | ibus-1.5.25-2.el9.rocky.0.1.src.rpm | must be build with '--nocheck'
| ipa | ipa-4.10.1-6.el9.src.rpm | build with `-D "eln 1"`
| isomd5sum | isomd5sum-1.2.3-14.el9.src.rpm | build with "linux32"
| java-1.8.0-openjdk | java-1.8.0-openjdk-1.8.0.372.b07-2.el9.src.rpm | build with "linux32"
| java-11-openjdk | java-11-openjdk-11.0.19.0.7-4.el9.src.rpm | build with "linux32"
| java-17-openjdk | java-17-openjdk-17.0.7.0.7-3.el9.src.rpm | build with "linux32"
| ksh | ksh-1.0.0~beta.1-2.el9.src.rpm | build with "linux32"
| libomp | libomp-15.0.7-1.el9.redsleeve.src.rpm | build with "linux32"
| nss | nss-3.79.0-18.el9_1.src.rpm | build with "linux32"
| openmpi | openmpi-4.1.1-5.el9.redsleeve.src.rpm | build with "linux32"
| osbuild-composer | osbuild-composer-76-2.el9_2.2.rocky.0.2.src.rpm | must be build with '--nocheck'
| pgaudit | pgaudit-1.5.0-6.el9.src.rpm | remove '(Pre)' from macros.postgresql before build
| pg_repack | pg_repack-1.4.6-4.el9.src.rpm | remove '(Pre)' from macros.postgresql before build
| postgres-decoderbufs | postgres-decoderbufs-1.4.0-4.Final.el9.src.rpm | remove '(Pre)' from macros.postgresql before build
| python3.11-scipy | python3.11-scipy-1.10.0-1.el9.src.rpm | must be build with '--nocheck'
| redis | redis-6.2.7-1.el9.src.rpm | build with "linux32"
| ruby | ruby-3.0.4-160.el9_0.src.rpm | must be build with '--nocheck'
| s-nail | s-nail-14.9.22-6.el9.src.rpm | must be build with '--nocheck'
| satyr | satyr-0.38-3.el9.src.rpm | must be build with '--nocheck'
| squid | squid-5.5-5.el9.src.rpm | must be build with '--nocheck'
| tang | tang-11-2.el9.src.rpm | must be build with '--nocheck'
| tbb | tbb-2020.3-8.el9.src.rpm | build with "linux32"
| varnish | varnish-6.6.2-3.el9.src.rpm | must be build with '--nocheck'
| webkit2gtk3 | webkit2gtk3-2.38.5-1.el9_2.1.src.rpm | build with "linux32"
| woff2 | woff2-1.0.2-15.el9.src.rpm | needs to be build with '-D "_target_platform redhat-linux-build"'


### extra ###

| Package | SRPM | instruction
|---|---|---
| elinks | elinks-0.12-0.58.pre6.el8.armv6hl.rpm | RPM from RedSleeve 8.6 PowerTools
