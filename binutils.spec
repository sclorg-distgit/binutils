# rpmbuild parameters:
# --define "binutils_target arm-linux-gnu" to create arm-linux-gnu-binutils.
# --with debug: Build without optimizations and without splitting the debuginfo.
# --without testsuite: Do not run the testsuite.  Default is to run it.
# --with testsuite: Run the testsuite.  Default --with debug is not to run it.

%{?scl:%{?scl_package:%scl_package binutils}}

%if 0%{!?binutils_target:1}
%define binutils_target %{_target_platform}
%define isnative 1
%define enable_shared 1
%else
%define cross %{binutils_target}-
%define isnative 0
%define enable_shared 0
%endif
# Disable deterministic archives by default.
# This is for package builders who do not want to have to change
# their build scripts to work with deterministic archives.
%define enable_deterministic_archives 0

Summary: A GNU collection of binary utilities
Name: %{?scl_prefix}%{?cross}binutils%{?_with_debug:-debug}
Version: 2.25.1
Release: 10%{?dist}
License: GPLv3+
Group: Development/Tools
URL: http://sources.redhat.com/binutils

# Note - the Linux Kernel binutils releases are too unstable and contain too
# many controversial patches so we stick with the official FSF version
# instead.

Source: http://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.gz

Source2: binutils-2.19.50.0.1-output-format.sed
Patch01: binutils-2.20.51.0.2-libtool-lib64.patch
Patch02: binutils-2.20.51.0.10-ppc64-pie.patch
Patch03: binutils-2.20.51.0.2-ia64-lib64.patch
Patch04: binutils-2.25-version.patch
Patch05: binutils-2.25-set-long-long.patch
Patch06: binutils-2.20.51.0.10-copy-osabi.patch
Patch07: binutils-2.20.51.0.10-sec-merge-emit.patch
# Enable -zrelro by default: BZ #621983
Patch08: binutils-2.22.52.0.1-relro-on-by-default.patch
# Local patch - export demangle.h with the binutils-devel rpm.
Patch09: binutils-2.22.52.0.1-export-demangle.h.patch
# Disable checks that config.h has been included before system headers.  BZ #845084
Patch10: binutils-2.22.52.0.4-no-config-h-check.patch
# Fix addr2line to use the dynamic symbol table if it could not find any ordinary symbols.
Patch11: binutils-2.23.52.0.1-addr2line-dynsymtab.patch
# Patch12: binutils-2.23.2-kernel-ld-r.patch
Patch12: binutils-2.25-kernel-ld-r.patch
# Correct bug introduced by patch 12
Patch13: binutils-2.23.2-aarch64-em.patch
# Fix detections little endian PPC shared libraries
Patch14: binutils-2.24-ldforcele.patch

Patch1010: binutils-2.23.51.0.3-Provide-std-tr1-hash.patch
Patch1011: binutils-rh1038339.patch
Patch1012: binutils-2.24-rh919508.patch
Patch1013: binutils-rh1224751.patch
Patch1014: binutils-rh895241.patch

# Fix preservation of section headers whilst stripping out non-debug information.
Patch1015: binutils-2.25-only-keep-debug.patch
# Fix seg-fault in readelf reading a corrupt binary.
Patch1016: binutils-pr18879.patch
# Fix failures in GOLD testsuite.
Patch1017: binutils-2.25.1-gold-testsuite-fixes.patch
# Add support for Intel Memory Protection Key instructions.
Patch1018: binutils-rh1309347.patch
Patch1019: binutils-2.25-kernel-ld-r.bugfix.patch


Provides: bundled(libiberty)

%define gold_arches %ix86 x86_64 %arm

%ifarch %gold_arches
%define build_gold	both
%else
%define build_gold	no
%endif

%define alternatives_cmd %{!?scl:%{_sbindir}}%{?scl:%{_root_sbindir}}/alternatives
%define alternatives_cmdline %{alternatives_cmd}%{?scl: --altdir %{_sysconfdir}/alternatives --admindir %{_scl_root}/var/lib/alternatives}

%if 0%{?_with_debug:1}
# Define this if you want to skip the strip step and preserve debug info.
# Useful for testing.
%define __debug_install_post : > %{_builddir}/%{?buildsubdir}/debugfiles.list
%define debug_package %{nil}
%define run_testsuite 0%{?_with_testsuite:1}
%else
%define run_testsuite 0%{!?_without_testsuite:1}
%endif

Buildroot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires: texinfo >= 4.0, gettext, flex, bison, zlib-devel
# BZ 920545: We need pod2man in order to build the manual pages.
BuildRequires: /usr/bin/pod2man
# Required for: ld-bootstrap/bootstrap.exp bootstrap with --static
# It should not be required for: ld-elf/elf.exp static {preinit,init,fini} array
%if %{run_testsuite}
# relro_test.sh uses dc which is part of the bc rpm, hence its inclusion here.
BuildRequires: dejagnu, zlib-static, glibc-static, sharutils, bc
%if "%{build_gold}" == "both"
# The GOLD testsuite needs a static libc++
%if 0%{?rhel} >= 7
BuildRequires: libstdc++-static
%endif
%endif
%endif
Conflicts: gcc-c++ < 4.0.0
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
%ifarch ia64
Obsoletes: gnupro <= 1117-1
%endif
%{?scl:Requires:%scl_runtime}


# The higher of these two numbers determines the default ld.
%{!?ld_bfd_priority: %define ld_bfd_priority	50}
%{!?ld_gold_priority:%define ld_gold_priority	30}

%if "%{build_gold}" == "both"
Requires(post): coreutils
Requires(post): %{alternatives_cmd}
Requires(preun): %{alternatives_cmd}
%endif

# On ARM EABI systems, we do want -gnueabi to be part of the
# target triple.
%ifnarch %{arm}
%define _gnu %{nil}
%endif

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

%package devel
Summary: BFD and opcodes static and dynamic libraries and header files
Group: System Environment/Libraries
Provides: binutils-static = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
Requires: %{?scl_prefix}binutils = %{version}-%{release}
Requires: zlib-devel
# BZ 1215242: We need touch...
Requires: coreutils

%description devel
This package contains BFD and opcodes static and dynamic libraries.

The dynamic libraries are in this package, rather than a seperate
base package because they are actually linker scripts that force
the use of the static libraries.  This is because the API of the
BFD library is too unstable to be used dynamically.

The static libraries are here because they are now needed by the
dynamic libraries.

Developers starting new projects are strongly encouraged to consider
using libelf instead of BFD.

%prep
%setup -q -n binutils-%{version}
%patch01 -p1 -b .libtool-lib64~
%patch02 -p1 -b .ppc64-pie~
%ifarch ia64
%if "%{_lib}" == "lib64"
%patch03 -p1 -b .ia64-lib64~
%endif
%endif
%patch04 -p1 -b .version~
%patch05 -p1 -b .set-long-long~
%patch06 -p1 -b .copy-osabi~
%patch07 -p1 -b .sec-merge-emit~
%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
%patch08 -p1 -b .relro~
%endif
%patch09 -p1 -b .export-demangle-h~
%patch10 -p1 -b .no-config-h-check~
%patch11 -p1 -b .addr2line~
%patch12 -p1 -b .kernel-ld-r~
%patch13 -p1 -b .aarch64~
%ifarch ppc64le
%patch14 -p1 -b .ldforcele~
%endif

%patch1010 -p1 -b .provide-hash~
%patch1011 -p1 -b .manpage~
%patch1012 -p1 
%patch1013 -p1 
%patch1014 -p1
%patch1015 -p1
%patch1016 -p1
%patch1017 -p0
%patch1018 -p1
%patch1019 -p1

# We cannot run autotools as there is an exact requirement of autoconf-2.59.

# On ppc64 and aarch64, we might use 64KiB pages
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*ppc.c
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*aarch64.c
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
touch */configure

%ifarch %{power64}
%define _target_platform %{_arch}-%{_vendor}-%{_host_os}
%endif

%build
echo target is %{binutils_target}
%ifarch %{power64}
#CFLAGS=`echo $RPM_OPT_FLAGS | sed -e -s "s/-Werror//g"`
#export CFLAGS
export CFLAGS="$RPM_OPT_FLAGS -Wno-error"
%else
export CFLAGS="$RPM_OPT_FLAGS"
%endif
CARGS=

case %{binutils_target} in i?86*|sparc*|ppc*|s390*|sh*|arm*|aarch64*)
  CARGS="$CARGS --enable-64-bit-bfd"
  ;;
esac

case %{binutils_target} in ia64*)
  CARGS="$CARGS --enable-targets=i386-linux"
  ;;
esac

# We could optimize the cross builds size by --enable-shared but the produced
# binaries may be less convenient in the embedded environment.
# The seemingly unncessary --with-sysroot argument is merely meant to enable
# sysroot capabilities in the resulting executables.  That allows customers
# to then use the sysroot capability to set up host-x-host build environments
# easier.
%configure \
  --build=%{_target_platform} --host=%{_target_platform} \
  --target=%{binutils_target} \
  --with-sysroot=/ \
%ifarch %gold_arches
%if "%{build_gold}" == "both"
  --enable-gold=default --enable-ld \
%else
  --enable-gold \
%endif
%endif
%if !%{isnative}
  --enable-targets=%{_host} \
  --with-sysroot=%{_prefix}/%{binutils_target}/sys-root \
  --program-prefix=%{cross} \
%endif
%if %{enable_shared}
  --enable-shared \
%else
  --disable-shared \
%endif
%if %{enable_deterministic_archives}
  --enable-deterministic-archives \
%endif
  $CARGS \
  --enable-plugins \
  --with-bugurl=http://bugzilla.redhat.com/bugzilla/
make %{_smp_mflags} tooldir=%{_prefix} all
make %{_smp_mflags} tooldir=%{_prefix} info

# Do not use %%check as it is run after %%install where libbfd.so is rebuild
# with -fvisibility=hidden no longer being usable in its shared form.
%if !%{run_testsuite}
echo ====================TESTSUITE DISABLED=========================
%else
make -k check < /dev/null || :
echo ====================TESTING=========================
cat {gas/testsuite/gas,ld/ld,binutils/binutils}.sum
echo ====================TESTING END=====================
for file in {gas/testsuite/gas,ld/ld,binutils/binutils}.{sum,log}
do
  ln $file binutils-%{_target_platform}-$(basename $file) || :
done
tar cjf binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}-*.{sum,log}
uuencode binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}.tar.bz2
rm -f binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}-*.{sum,log}
%endif

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
%if %{isnative}
make prefix=%{buildroot}%{_prefix} infodir=%{buildroot}%{_infodir} install-info

# Rebuild libiberty.a with -fPIC.
# Future: Remove it together with its header file, projects should bundle it.
make -C libiberty clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C libiberty

# Rebuild libbfd.a with -fPIC.
# Without the hidden visibility the 3rd party shared libraries would export
# the bfd non-stable ABI.
make -C bfd clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS -fvisibility=hidden" -C bfd

# Rebuild libopcodes.a with -fPIC.
make -C opcodes clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C opcodes

install -m 644 bfd/libbfd.a %{buildroot}%{_libdir}
install -m 644 libiberty/libiberty.a %{buildroot}%{_libdir}
install -m 644 include/libiberty.h %{buildroot}%{_prefix}/include
install -m 644 opcodes/libopcodes.a %{buildroot}%{_libdir}
# Remove Windows/Novell only man pages
rm -f %{buildroot}%{_mandir}/man1/{dlltool,nlmconv,windmc,windres}*

%if %{enable_shared}
chmod +x %{buildroot}%{_libdir}/lib*.so*
%endif

# Prevent programs from linking against libbfd and libopcodes
# dynamically, as they are change far too often.
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.so

# Remove libtool files, which reference the .so libs
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.la

# Sanity check --enable-64-bit-bfd really works.
grep '^#define BFD_ARCH_SIZE 64$' %{buildroot}%{_prefix}/include/bfd.h
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
    %{buildroot}%{_prefix}/include/bfd.h
%endif
touch -r bfd/bfd-in2.h %{buildroot}%{_prefix}/include/bfd.h

# Generate .so linker scripts for dependencies; imported from glibc/Makerules:

# This fragment of linker script gives the OUTPUT_FORMAT statement
# for the configuration we are building.
OUTPUT_FORMAT="\
/* Ensure this .so library will not be used by a link for a different format
   on a multi-architecture system.  */
$(gcc $CFLAGS $LDFLAGS -shared -x c /dev/null -o /dev/null -Wl,--verbose -v 2>&1 | sed -n -f "%{SOURCE2}")"

tee %{buildroot}%{_libdir}/libbfd.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

/* The libz dependency is unexpected by legacy build scripts.  */
/* The libdl dependency is for plugin support.  (BZ 889134)  */
INPUT ( %{_libdir}/libbfd.a -liberty -lz -ldl )
EOH

tee %{buildroot}%{_libdir}/libopcodes.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

INPUT ( %{_libdir}/libopcodes.a -lbfd )
EOH

%else # !%{isnative}
# For cross-binutils we drop the documentation.
rm -rf %{buildroot}%{_infodir}
# We keep these as one can have native + cross binutils of different versions.
#rm -rf %{buildroot}%{_prefix}/share/locale
#rm -rf %{buildroot}%{_mandir}
rm -rf %{buildroot}%{_libdir}/libiberty.a
%endif # !%{isnative}

# This one comes from gcc
rm -f %{buildroot}%{_infodir}/dir
rm -rf %{buildroot}%{_prefix}/%{binutils_target}

%find_lang %{?cross}binutils
%find_lang %{?cross}opcodes
%find_lang %{?cross}bfd
%find_lang %{?cross}gas
%find_lang %{?cross}gprof
cat %{?cross}opcodes.lang >> %{?cross}binutils.lang
cat %{?cross}bfd.lang >> %{?cross}binutils.lang
cat %{?cross}gas.lang >> %{?cross}binutils.lang
cat %{?cross}gprof.lang >> %{?cross}binutils.lang

if [ -x ld/ld-new ]; then
  %find_lang %{?cross}ld
  cat %{?cross}ld.lang >> %{?cross}binutils.lang
fi
if [ -x gold/ld-new ]; then
  %find_lang %{?cross}gold
  cat %{?cross}gold.lang >> %{?cross}binutils.lang
fi

%clean
rm -rf %{buildroot}

%post
%if "%{build_gold}" == "both"
%__rm -f %{_bindir}/%{?cross}ld
%{alternatives_cmdline} --install %{_bindir}/%{?cross}ld %{?cross}ld \
  %{_bindir}/%{?cross}ld.bfd %{ld_bfd_priority}
%{alternatives_cmdline} --install %{_bindir}/%{?cross}ld %{?cross}ld \
  %{_bindir}/%{?cross}ld.gold %{ld_gold_priority}
%{alternatives_cmdline} --auto %{?cross}ld
%endif
%if %{isnative}
/sbin/ldconfig
# For --excludedocs:
if [ -e %{_infodir}/binutils.info.gz ]
then
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/as.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/ld.info.gz
fi
%endif # %{isnative}
exit 0

%preun
%if "%{build_gold}" == "both"
if [ $1 = 0 ]; then
  %{alternatives_cmdline} --remove %{?cross}ld %{_bindir}/%{?cross}ld.bfd
  %{alternatives_cmdline} --remove %{?cross}ld %{_bindir}/%{?cross}ld.gold
fi
%endif
%if %{isnative}
if [ $1 = 0 ]; then
  if [ -e %{_infodir}/binutils.info.gz ]
  then
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/as.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/ld.info.gz
  fi
fi
%endif
exit 0

%if %{isnative}
%postun -p /sbin/ldconfig
%endif # %{isnative}

%files -f %{?cross}binutils.lang
%defattr(-,root,root,-)
%doc README
%{_bindir}/%{?cross}[!l]*
%if "%{build_gold}" == "both"
%{_bindir}/%{?cross}ld.*
%ghost %{_bindir}/%{?cross}ld
%else
%{_bindir}/%{?cross}ld*
%endif
%{_mandir}/man1/*
%if %{enable_shared}
%{_libdir}/lib*.so
%exclude %{_libdir}/libbfd.so
%exclude %{_libdir}/libopcodes.so
%endif

%if %{isnative}
%{_infodir}/[^b]*info*
%{_infodir}/binutils*info*

%files devel
%defattr(-,root,root,-)
%{_prefix}/include/*
%{_libdir}/lib*.a
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.so
%{_infodir}/bfd*info*

%endif # %{isnative}

%changelog
* Mon Apr 04 2016 Patsy Franklin <pfrankli@redhat.com> 2.25.1-10
- Fix a case where the string was being used after the memory
  containing the string had been freed.

* Wed Mar 02 2016 Nick Clifton <nickc@redhat.com> 2.25.1-9
- Bump release number by 2 in order to enable build.

* Wed Mar 02 2016 Nick Clifton <nickc@redhat.com> 2.25.1-7
- Fix GOLD testsuite failures.
  (#1312376)

* Thu Feb 25 2016 Nick Clifton <nickc@redhat.com> 2.25.1-6
- Change ar's default to be the creation of non-deterministic archives.

* Thu Feb 18 2016 Nick Clifton <nickc@redhat.com> 2.25.1-4
- Add support for Intel Memory Protection Key instructions.
  (#1309347)

* Thu Feb 04 2016 Nick Clifton <nickc@redhat.com> 2.25.1-2
- Import patch for FSF PR 18879
  (#1260034)

* Thu Jan 14 2016 Nick Clifton <nickc@redhat.com> 2.25.1-1
- Rebase on FSF binutils 2.25.1 release.
- Retire patch binutils-2.25-x86_64-pie-relocs.patch

* Tue Sep 22 2015 Nick Clifton <nickc@redhat.com> 2.25-10
- Improved patch to preserve the sh_link and sh_info fields in stripped ELF sections.
  (#1246390)

* Wed Aug 5 2015 Nick Clifton <nickc@redhat.com> 2.25-9
- Import patch from FSF to preserve the sh_link and sh_info fields in stripped ELF sections.
  (#1246390)

* Tue Aug 4 2015 Jeff Law <law@redhat.com> 2.25-8
- Backport Cary's patch to silence pedantic warning in gold
  (#895241)

* Thu Jun 4 2015 Jeff Law <law@redhat.com> 2.25-7
- Resync with Fedora (binutils-2.25)
  Reapply DTS specific patches
  Backport testsuite patch to fix gold testsuite failure
  
