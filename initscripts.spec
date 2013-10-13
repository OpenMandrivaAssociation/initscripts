Summary:	The inittab file and the %{_sysconfdir}/init.d scripts
Name:		initscripts
Version:	9.45
Release:	4
# ppp-watch is GPLv2+, everything else is GPLv2
License:	GPLv2 and GPLv2+
Group:		System/Base
# Upstream URL: http://git.fedorahosted.org/git/initscripts.git
Url:		https://abf.rosalinux.ru/omv_software/initscripts
# https://abf.rosalinux.ru/omv_software/initscripts
Source0:	%{name}-%{version}.tar.xz
# udev rules for speeding up SSDs by using the noop scheduler
Source1:	60-ssd.rules
Source100:	%{name}.rpmlintrc

BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig
BuildRequires:	popt-devel
BuildRequires:	python

Requires:	basesystem-minimal
Requires(pre):	basesystem-minimal
Requires(post):	rpm-helper
Requires(post):	util-linux
Requires:	gettext-base >= 0.10.35-20mdk
# for /sbin/ip
Requires:	iproute2
# for /sbin/arping
Requires:	iputils
Requires:	net-tools
# (blino) for pidof -c
# (bor) for pidof -m
Requires:	sysvinit-tools >= 2.87-8mdv2011.0
Requires:	ifplugd >= 0.24
Requires:	iproute2
Requires:	ethtool
Requires:	ifmetric
Requires:	resolvconf >= 1.41
Requires:	dmsetup
# http://bugzilla.redhat.com/show_bug.cgi?id=252973
Conflicts:	nut < 2.2.0
Obsoletes:	rhsound < %{version}-%{release}
Obsoletes:	sapinit < %{version}-%{release}
Provides:	rhsound = %{version}-%{release}
Provides:	sapinit = %{version}-%{release}
Conflicts:	kernel <= 2.2
Conflicts:	timeconfig < 3.0
Conflicts:	pppd <= 2.4.4-3mdv2008.1
Conflicts:	wvdial < 1.40-3
Conflicts:	initscripts < 1.22.1-5
Conflicts:	Aurora <= 7.2-17mdk
Conflicts:	dhcpcd < 1.3.21pl1
Conflicts:	XFree86-xfs < 4.2.0-12mdk
Conflicts:	xinitrc < 2.4.12
Conflicts:	lsb < 3.1-11mdv2007.1
Conflicts:	lsb-core < 3.1-15mdv2008.1
Conflicts:	suspend-scripts < 1.27
Conflicts:	mdadm < 2.6.4-2mdv2008.1
Conflicts:	systemd <= 19-2
Conflicts:	networkmanager < 0.8.2-8
Conflicts:	prcsys

%description
The initscripts package contains the basic system scripts used to boot
your %{distribution} system, change run levels, and shut the system
down cleanly.  Initscripts also contains the scripts that activate and
deactivate most network interfaces.

%package debugmode
Summary:	Scripts for running in debugging mode
Requires:	initscripts
Group:		System/Base
%rename		debugmode

%description debugmode
The debugmode package contains some basic scripts that are used to run
the system in a debugging mode.

Currently, this consists of various memory checking code.

%prep
%setup -q
rm -rf po
ln -s mandriva/po

xz --text ChangeLog

%apply_patches

%build
%global optflags %{optflags} -Os
%setup_compile_flags
make
make -C mandriva

%install
mkdir -p %{buildroot}%{_sysconfdir}
make ROOT=%{buildroot} SUPERUSER=`id -un` SUPERGROUP=`id -gn` mandir=%{_mandir} install

#MDK
make -C mandriva install ROOT=%{buildroot} mandir=%{_mandir}

python mandriva/gprintify.py \
	`find %{buildroot}%{_sysconfdir}/rc.d -type f` \
	`find %{buildroot}/sysconfig/network-scripts -type f` \
	%{buildroot}%{_systemdrootdir}/fedora-* \
	%{buildroot}%{_systemdrootdir}/mandriva-*

install -c -m 644 %{SOURCE1} %{buildroot}/lib/udev/rules.d/

# (tpg) remove as its not needed
for i in 0 1 2 3 4 5 6; do
rm -rf %{buildroot}%{_sysconfdir}/rc$i.d ;
done

%find_lang %{name}

# we have our own copy of gprintify
export DONT_GPRINTIFY=1

touch %{buildroot}%{_sysconfdir}/crypttab
chmod 600 %{buildroot}%{_sysconfdir}/crypttab

if [ -f %{buildroot}%{_sysconfdir}/sysctl.conf ]; then
mkdir -p %{buildroot}%{_sysconfdir}/sysctl.d/
mv -f %{buildroot}%{_sysconfdir}/sysctl.conf %{buildroot}%{_sysconfdir}/sysctl.d/99-sysctl.conf
ln -s %{_sysconfdir}/sysctl.d/99-sysctl.conf %{buildroot}%{_sysconfdir}/sysctl.conf
fi

%pre
if [ $1 -ge 2 ]; then
    if [ -e %{_sysconfdir}/sysctl.conf ] && [ ! -L %{_sysconfdir}/sysctl.conf ]; then
	mv -f %{_sysconfdir}/sysctl.conf %{_sysconfdir}/sysctl.d/99-sysctl.conf
	ln -s %{_sysconfdir}/sysctl.d/99-sysctl.conf %{_sysconfdir}/sysctl.conf
    fi
fi

%post
##
touch /var/log/wtmp /var/run/utmp /var/log/btmp
chown root:utmp /var/log/wtmp /var/run/utmp /var/log/btmp
chmod 664 /var/log/wtmp /var/run/utmp
chmod 600 /var/log/btmp

%_post_service partmon

%_post_service network

%_post_service network-up

%_post_service dm

%_post_service netconsole


%preun
%_preun_service netconsole

%_preun_service dm

%_preun_service network-up

%_preun_service network

%_preun_service partmon

%files -f %{name}.lang
%dir %{_sysconfdir}/sysconfig/network-scripts
%dir %{_sysconfdir}/sysconfig/network-scripts/ifup.d
%dir %{_sysconfdir}/sysconfig/network-scripts/ifdown.d
%dir %{_sysconfdir}/sysconfig/network-scripts/wireless.d
%dir %{_sysconfdir}/sysconfig/network-scripts/vpn.d
%dir %{_sysconfdir}/sysconfig/network-scripts/vpn.d/openvpn
%dir %{_sysconfdir}/sysconfig/network-scripts/vpn.d/pptp
%dir %{_sysconfdir}/sysconfig/network-scripts/vpn.d/vpnc
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/adjtime
%config(noreplace) %{_sysconfdir}/sysconfig/init
%config(noreplace) %{_sysconfdir}/sysconfig/autofsck
%config(noreplace) %{_sysconfdir}/sysconfig/partmon
%config(noreplace) %{_sysconfdir}/sysconfig/netconsole
%config(noreplace) %{_sysconfdir}/sysconfig/readonly-root
%{_sysconfdir}/sysconfig/network-scripts/ifdown
/sbin/ifdown
%{_sysconfdir}/sysconfig/network-scripts/ifdown-post
%{_sysconfdir}/sysconfig/network-scripts/ifup
/sbin/ifup
%dir %{_sysconfdir}/sysconfig/console
%dir %{_sysconfdir}/sysconfig/console/consoletrans
%dir %{_sysconfdir}/sysconfig/console/consolefonts
%dir %{_sysconfdir}/sysconfig/modules
%{_sysconfdir}/sysconfig/network-scripts/network-functions
%{_sysconfdir}/sysconfig/network-scripts/network-functions-ipv6
%{_sysconfdir}/sysconfig/network-scripts/init.ipv6-global
%config(noreplace) %{_sysconfdir}/sysconfig/network-scripts/ifcfg-lo
%{_sysconfdir}/sysconfig/network-scripts/ifup-ipx
%{_sysconfdir}/sysconfig/network-scripts/ifup-post
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ppp
%{_sysconfdir}/sysconfig/network-scripts/ifup-ppp
%{_sysconfdir}/sysconfig/network-scripts/ifup-routes
%{_sysconfdir}/sysconfig/network-scripts/ifdown-routes
%{_sysconfdir}/sysconfig/network-scripts/ifup-plip
%{_sysconfdir}/sysconfig/network-scripts/ifup-plusb
%{_sysconfdir}/sysconfig/network-scripts/ifup-bnep
%{_sysconfdir}/sysconfig/network-scripts/ifdown-bnep
%{_sysconfdir}/sysconfig/network-scripts/ifup-eth
%{_sysconfdir}/sysconfig/network-scripts/ifdown-eth
%{_sysconfdir}/sysconfig/network-scripts/ifup-ipv6
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ipv6
%{_sysconfdir}/sysconfig/network-scripts/ifup-sit
%{_sysconfdir}/sysconfig/network-scripts/ifdown-sit
%{_sysconfdir}/sysconfig/network-scripts/ifup-tunnel
%{_sysconfdir}/sysconfig/network-scripts/ifdown-tunnel
%{_sysconfdir}/sysconfig/network-scripts/ifup-aliases
%{_sysconfdir}/sysconfig/network-scripts/ifup-isdn
%{_sysconfdir}/sysconfig/network-scripts/ifdown-isdn
%{_sysconfdir}/sysconfig/network-scripts/ifup-wireless
%{_sysconfdir}/sysconfig/network-scripts/ifup-hso
%{_sysconfdir}/sysconfig/network-scripts/ifdown-hso
%{_sysconfdir}/X11/prefdm
%{_sysconfdir}/X11/lookupdm
%config(noreplace) %{_sysconfdir}/networks
%{_sysconfdir}/rwtab
%dir %{_sysconfdir}/rwtab.d
%{_sysconfdir}/statetab
%dir %{_sysconfdir}/statetab.d
/lib/udev/rules.d/*
%config(noreplace) %{_sysconfdir}/inittab
%dir %{_sysconfdir}/rc.d/init.d
/lib/lsb/init-functions
%{_sysconfdir}/rc.d/init.d/*
%config(noreplace) %{_sysconfdir}/sysctl.d/99-sysctl.conf
%{_sysconfdir}/sysctl.conf
%dir %{_prefix}/lib/sysctl.d
%{_prefix}/lib/sysctl.d/00-system.conf
%exclude %{_sysconfdir}/profile.d/debug*
%config %{_sysconfdir}/profile.d/*
%dir %{_sysconfdir}/sysconfig/network-scripts/cellular.d
%dir %{_sysconfdir}/sysconfig/network-scripts/hostname.d
%{_sysconfdir}/sysconfig/network-scripts/ifup.d/vpn
%{_sysconfdir}/sysconfig/network-scripts/ifdown.d/vpn
%{_sbindir}/vpn-start
%{_sbindir}/vpn-stop
%{_sbindir}/mdv-network-event
%{_sbindir}/sys-unconfig
/bin/ipcalc
/bin/usleep
%attr(4755,root,root) %{_sbindir}/usernetctl
/sbin/consoletype
/sbin/genhostid
/sbin/netreport
/lib/udev/rename_device
%ifarch s390 s390x
/lib/udev/ccw_init
%endif
/sbin/service
/sbin/sushell
#mdv
/sbin/hibernate-cleanup.sh
/sbin/ppp-watch
%{_mandir}/man*/*
%lang(cs) %{_mandir}/cs/man*/*
%lang(et) %{_mandir}/et/man*/*
%lang(fi) %{_mandir}/fi/man*/*
%lang(fr) %{_mandir}/fr/man*/*
%lang(it) %{_mandir}/it/man*/*
%lang(pt_BR) %{_mandir}/pt_BR/man*/*
%lang(ru) %{_mandir}/ru/man*/*
%lang(uk) %{_mandir}/uk/man*/*
%dir %attr(775,root,root) /var/run/netreport
%dir %{_sysconfdir}/ppp
%dir %{_sysconfdir}/ppp/ip-down.d
%dir %{_sysconfdir}/ppp/ip-up.d
%dir %{_sysconfdir}/ppp/peers
%{_sysconfdir}/ppp/ip-up
%{_sysconfdir}/ppp/ip-down
%{_sysconfdir}/ppp/ip-up.ipv6to4
%{_sysconfdir}/ppp/ip-down.ipv6to4
%{_sysconfdir}/ppp/ipv6-up
%{_sysconfdir}/ppp/ipv6-down
%dir %{_sysconfdir}/NetworkManager
%dir %{_sysconfdir}/NetworkManager/dispatcher.d
%{_sysconfdir}/NetworkManager/dispatcher.d/00-netreport
%doc sysconfig.txt sysvinitfiles ChangeLog.xz static-routes-ipv6 ipv6-tunnel.howto ipv6-6to4.howto changes.ipv6
/var/lib/stateless
%ghost %attr(0664,root,utmp) /var/log/btmp
%ghost %attr(0664,root,utmp) /var/log/wtmp
%ghost %attr(0664,root,utmp) /var/run/utmp
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/crypttab
%config(noreplace) %{_sysconfdir}/modules
%{_sysconfdir}/rc.modules
%dir %{_sysconfdir}/modprobe.preload.d/
%{_bindir}/*
%dir /lib/tmpfiles.d
/lib/tmpfiles.d/initscripts.conf
/lib/tmpfiles.d/mandriva.conf
%{_systemdrootdir}/fedora-autorelabel
%{_systemdrootdir}/fedora-configure
%{_systemdrootdir}/fedora-import-state
%{_systemdrootdir}/fedora-loadmodules
%{_systemdrootdir}/fedora-readonly
%{_systemdrootdir}/mandriva-save-dmesg
%{_systemunitdir}/basic.target.wants/fedora-autorelabel.service
%{_systemunitdir}/basic.target.wants/fedora-autorelabel-mark.service
%{_systemunitdir}/basic.target.wants/fedora-configure.service
%{_systemunitdir}/basic.target.wants/fedora-loadmodules.service
%{_systemunitdir}/basic.target.wants/mandriva-everytime.service
%{_systemunitdir}/basic.target.wants/mandriva-save-dmesg.service
%{_systemunitdir}/fedora-autorelabel.service
%{_systemunitdir}/fedora-autorelabel-mark.service
%{_systemunitdir}/fedora-configure.service
%{_systemunitdir}/fedora-import-state.service
%{_systemunitdir}/fedora-loadmodules.service
%{_systemunitdir}/fedora-readonly.service
%{_systemunitdir}/mandriva-everytime.service
%{_systemunitdir}/mandriva-save-dmesg.service
%{_systemunitdir}/local-fs.target.wants/fedora-import-state.service
%{_systemunitdir}/local-fs.target.wants/fedora-readonly.service
%{_systemunitdir}/mandriva-kmsg-loglevel.service
%{_systemunitdir}/sysinit.target.wants/mandriva-kmsg-loglevel.service

%files -n debugmode
%config(noreplace) %{_sysconfdir}/sysconfig/debug
%config %{_sysconfdir}/profile.d/debug*

%changelog
* Fri Jan  4 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.43-3
- add missing /etc/profile.d/inputrc.sh script (P2)
- fix sourced-script-with-shebang for /etc/profile.d/10tmpdir.sh (P1)
- rewrite partmon script from perl to shell (P0), freeing ourself from any
  perl dependencies

* Thu Dec 20 2012 Tomasz Paweł Gajc <tpg@mandriva.org> 9.43-2
- do not require module-init-tools and psmisc as these pkgs are pulled in by
  basesystem package, do not obsolete itself btw.

* Fri Dec 14 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.43-1
- drop dead /etc/sysctl.d, /usr/lib/sysctl.d replaces it
- compile with -Os
- drop supermount script, supermount has been dead for ages!
- clean out old junk
- drop ancient triggers
- merge all changes into our own git branch
- new version

* Thu Dec 13 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.34-6
- remove some more bashism from scripts

* Sat Nov  3 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.34-3
+ Revision: 821733
- remove some bashism in %{_sysconfdir}/rc.d/init.d/functions which prevents it from being
  used with drakx/busybox

* Fri Sep 07 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.34-2
+ Revision: 816501
- drop dependency on mingetty, we're now working agetty provided by util-linux

* Wed Sep 05 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.34-1
+ Revision: 816409
- Mask netfs initscript under systemd as native support is built in
- clean up a bit at least..
- build with our own set of compiler and linker flags
- filter out some rpmlint errors
- don't try filter out dependencies no longer generated with a filter no longer
  used
- don't disable rpmlint checks
- new version (synced up with patches from mageia)

* Wed Jun 06 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.25-10
+ Revision: 802989
- fall back to using ifup & ifdown when there's no networkmanager running
  (avahi-daemon seems to have some issues allowing it to stay allow though!, P3)

* Mon Apr 23 2012 Antoine Ginies <aginies@mandriva.com> 9.25-9
+ Revision: 792964
- typo patch (oden)

* Wed Jan 04 2012 Stéphane Téletchéa <steletch@mandriva.org> 9.25-8
+ Revision: 754507
- Remove the last bit of haldaemon in our initscripts (Mdv bug #62975)

* Wed Nov 23 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.25-7
+ Revision: 732774
- add conflicts on prcsys if systemd is used (from TPG)

* Wed Nov 16 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 9.25-6
+ Revision: 731148
- don't own %{_sysconfdir}/sysconfig, it's already owned by 'filesystem' package

* Wed Apr 27 2011 Antoine Ginies <aginies@mandriva.com> 9.25-5
+ Revision: 659668
- remove requires on sound-scripts, should be elsewhere...

* Fri Apr 22 2011 Anssi Hannula <anssi@mandriva.org> 9.25-4
+ Revision: 656754
- Several bugfixes to speedboot, not affecting systemd boot:
  o In very early boot, call display_driver_helper to check if there is a
    pending dkms build (that may cause a wrong older binary dkms driver
    to be loaded by X server) or a conflicting driver loaded by initrd
    (which may cause graphical corruption / freeze when starting server)
    and disable speedboot in those cases.
  o Load display drivers before X when in speedboot.
  o In speedboot mode, reopen file descriptors after X should've started.
    This ensures that harddrake_service (and other sysinit output) is
    shown to the user if the X startup failed. (plymouth grabs the output,
    and when it shuts down the output is lost until descriptors are
    reopened).

* Sat Mar 19 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.25-3
+ Revision: 647049
- service: check for running systemd before redirect
- network-up: ask NM for status for NM_CONTROLLED interfaces or skip
  if NM is not available

* Thu Mar 10 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.25-2
+ Revision: 643651
- more systemd units tweaks
  add unit to clean up /var/run and /var/lock
  do not call console_init under systemd

* Tue Mar 01 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.25-1
+ Revision: 641173
- merge in 9.25; from upstream:
  o rc.sysinit: add support for sysctl.d
  o /sbin/service: accept --ignore-dependencies, --skip-redirect as options
- needs systemd >= 19 due to --ignore-dependencies
- own %{_sysconfdir}/sysctl.d

* Sat Feb 26 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.24-5
+ Revision: 640139
- remove ONBOOT hack for NM and conflict with NM < 0.8.2-8

* Sat Feb 26 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.24-4
+ Revision: 640120
- ifup/ifdown: skip interfaces controlled by NetworkManager

* Sun Feb 20 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.24-3
+ Revision: 638847
- order mandriva-everytime.service before basic.target
- gprintify scripts under %{_systemdrootdir}/system as well

* Sat Feb 19 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.24-2
+ Revision: 638827
- fix caculation of PREFIX/NETMASK/... in network_functions (we do not
  use multiple addresses)
- fix nscd call in network_functions, was wrong condition

* Sat Feb 19 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 9.24-1
+ Revision: 638691
- dynamically link with glib2, it is in /lib now
- merge 9.24
- add unit to set console loglevel
- add tmpfiles.d configuration from rc.sysinit
- add unit to setup standard links in /boot
- add unit to save boot dmesg output
- add unit for mandriva_everytime

* Fri Dec 03 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 9.21-4mdv2011.0
+ Revision: 606521
- add conflict with systemd for smooth update
- remove shutdown services provided natively by systemd

* Wed Dec 01 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 9.21-3mdv2011.0
+ Revision: 604580
- fix sysinit.service not launched with systemd v15
- add prefdm alias back to dm.service

* Tue Nov 30 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 9.21-2mdv2011.0
+ Revision: 603785
- enable systemd units
  install prefdm.service as dm.service to hide initscript
- fix prefdm.service for Mandriva
- network-functions need not be %%config

* Sun Nov 28 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 9.21-1mdv2011.0
+ Revision: 602277
- merge 9.21
- do not unmount /proc in halt, it is not needed and confuses systemd
- use LC_ALL for nmcli output (we set LC_MESSAGES with overrides LANG)
- export INIT_VERSION in systemd units (patch from systemd)
- export SINGLE in single.service in case %{_sysconfdir}/sysconfig/init was not
  updated (patch from systemd)
- conditional build systemd units (disabled for now)

* Wed Nov 17 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 9.17-1mdv2011.0
+ Revision: 598268
- sync with Fedora 9.17

  + Frederic Crozat <fcrozat@mandriva.com>
    - call chvt with --userwait to prevent deadlock at shutdown (Novell bug #540482)

* Wed Jun 23 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-15mdv2010.1
+ Revision: 548707
- Update translations

* Wed May 26 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-14mdv2010.1
+ Revision: 546243
- do not quit plymouth in runlevel 5, prefdm or gdm handles that (Mdv bug #59431)
- hide splash for luks passphrase, do not quit it
- do not call plymouth hide twice for Fsck
- update translations

* Wed May 19 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-13mdv2010.1
+ Revision: 545346
- Disable smooth X transition for KDE for now

* Wed May 05 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-12mdv2010.1
+ Revision: 542583
- Ensure prefdm and rc don't call plymouth quit for smooth plymouth => X transition

* Tue May 04 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-11mdv2010.1
+ Revision: 542072
- Updated translations
- add wait point for rc.modules in speedboot mode

* Thu Apr 22 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-10mdv2010.1
+ Revision: 537862
- ensure udev trigger is called with add action, default action will change in next udev releases

* Fri Feb 26 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-9mdv2010.1
+ Revision: 511930
- ensure loadkeys is really called in the right order (Mdv bug #57134)
- try to wake-up stopped process at shutdown (from Debian) (Mdv bug #57781)
- translations update

* Mon Feb 01 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-8mdv2010.1
+ Revision: 499120
- remove false check for volume saving on Mandriva (Mdv bug #57265)
- ensure dm-mod is loaded in speedboot mode too (Mdv bug #57351)
- Ensure loadkeys is called in sequence (Mdv bug #57134)

* Thu Jan 14 2010 Frederic Crozat <fcrozat@mandriva.com> 8.99-7mdv2010.1
+ Revision: 491529
- Fix obsolete syntax in udev rules file
- Restore old wireless behavior (revert bug #47791 fix and add fixes from
  bug #54002) (eugeni)
- Avoid 'no block devices found' message on boot when checking for dmraid
  (#55344) (eugeni)
- Update ifup script to properly work with new dhcpcd versions (#52673) (eugeni)
- Use correct address when waiting for network to be up (#56496) (eugeni)
- translation updates

* Tue Oct 27 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.99-6mdv2010.0
+ Revision: 459539
- ensure wpa_supplicant is properly restarted (#54002)

* Thu Oct 22 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.99-5mdv2010.0
+ Revision: 458941
- fix connecting to wireless networks after suspend/resume (#54002)
- try to load tun module when necessary (#54748)
- do not hardcode path to tunctl (#54740)
- translation updates

  + Frederic Crozat <fcrozat@mandriva.com>
    - Really put back hacks for unicode_start/stop and console font loading
    - update translations messages
    - Try to detect if /usr is not mounted yet when booting
    - udev failed events are now handled in udev-post
    - fix network link up detection (anssi, eugeni)
    - fix plymouth splash for crypto  (buchan)

* Fri Oct 16 2009 Frederic Crozat <fcrozat@mandriva.com> 8.99-3mdv2010.0
+ Revision: 457932
- Change keymaps and console fonts loading, use udev for most of it (like Fedora)
- failed udev events are now handled by udev-post, not rc.sysinit
- Plymouth startup / shutdown text are now translated (and different for shutdown / reboot)
- Remove leftover of splashy support
- Ensure /usr is mounted before showing plymouth prompt
- Unmount filesystems in reverse order (Eugeni, mdv bug #53042)
- Do not try to remove obsolete files in /tmp at startup
- do rtc init in first udev pass in speedboot mode
- various speed optimisations from upstream
- link udev help with glib statically, to reduce initrd size
- Fix "no raid disk" error at startup (GIT)

* Mon Oct 05 2009 Frederic Crozat <fcrozat@mandriva.com> 8.99-2mdv2010.0
+ Revision: 453964
- Fix hardware clock setting if hctosys is not available in sysfs
- Ensure killall return code is correctly handled in halt (Fedora)

* Fri Oct 02 2009 Frederic Crozat <fcrozat@mandriva.com> 8.99-1mdv2010.0
+ Revision: 452642
- Release 8.99 (resync with RH)
- Fix VT race preventing reboot (Mdv bug #53757)
- Save alsa levels in halt and not in alsa service anymore at shutdown
- do not wait 2s if not needed at shutdown

* Wed Sep 23 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.97-11mdv2010.0
+ Revision: 447850
- Correctly wait for network to be up (#43654).

* Wed Sep 23 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-10mdv2010.0
+ Revision: 447746
- Ensure plymouth is terminated when using xdm/autologin
- Add signals for network status and properly select wpa_supplicant (Mdv bug #47791)

* Thu Sep 10 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-9mdv2010.0
+ Revision: 437109
- Ensure plymouth is terminated when running in single-user mode

* Tue Sep 01 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-8mdv2010.0
+ Revision: 423711
- Ensure password is correctly asked when splash is disabled (Mdv bug #53301)

* Wed Aug 26 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-7mdv2010.0
+ Revision: 421465
- Replace file dependencies with package dependencies

* Tue Aug 25 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-6mdv2010.0
+ Revision: 421192
- Fix shutdown which could be blocked by plymouthd (Mdv bug #53051)
- Ensure plymouthd is stopped if started from initrd but splash isn't on cmdline
- Fix message in runlevel 0 and 6 hidden when no framebuffer is available but plymouth is enabled (Mdv bug #53110)

* Wed Aug 19 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-5mdv2010.0
+ Revision: 418132
- Send text message to plymouth for boot / reboot / shutdown

* Mon Aug 17 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-4mdv2010.0
+ Revision: 417398
- Fix speedboot broken by plymouth support
- Hide plymouth client output

* Mon Aug 17 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-3mdv2010.0
+ Revision: 417226
- Replace obsolete --retry-failed with --type=failed for udevadm settle call

* Thu Aug 13 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-2mdv2010.0
+ Revision: 416089
- Improve plymouth support

* Wed Aug 12 2009 Frederic Crozat <fcrozat@mandriva.com> 8.97-1mdv2010.0
+ Revision: 415626
- Release 8.97

* Tue Jul 28 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.88-26mdv2010.0
+ Revision: 402779
- Prevent partial wireless key disclosure when wireless password contains spaces and is of certain length.
- Removed redefinition of action() routine in halt script (#52324)
- Unify handling of RedHat-style and Mandriva-style ifcfg files.
- Do not configure CRDA twice on boot.
- Properly support TMPDIR configuration from SECURE_TMP msec variable.

* Tue Jun 30 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-25mdv2010.0
+ Revision: 391025
- do not use wc to check for netprofiles (Mdv bug #51902, patch from Pascal Terjan)
- Add support for created TUN/TAP devices on the fly (Mdv bug #51964)
- Stop crypto devices before LVM (Mdv bug #51951)

* Fri Jun 26 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-24mdv2010.0
+ Revision: 389408
- improvement for readahead : early and later readhead are now blocking calls

* Wed Jun 24 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-23mdv2010.0
+ Revision: 388885
- Fix many speedboot issues :
 - disable speedboot when netprofile needs to be manually selected
 - disable speedboot on the fly when %{_sysconfdir}/crypttab exists
 - fix status not being updated when using kdm
 - disable speedboot in failsafe mode
 - disable speedboot only when MD RAID / LVM volumes are detected
 - do not disable speedboot when quota is installed
- hide readahead error message

  + Eugeni Dodonov <eugeni@mandriva.com>
    - Added correct upstream url.
    - Corrected initscripts URL.

* Tue May 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.88-22mdv2010.0
+ Revision: 372160
- Automatically detecting screen width to fit long messages (#16509)
- Updated network-scripts to work with bash-4.0 (#50511)

* Wed Apr 22 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-21mdv2009.1
+ Revision: 368741
- Fix usleep value for usb_storage timeout

* Wed Apr 22 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-20mdv2009.1
+ Revision: 368725
- speedboot: Load usb controller in first boot phase and ensure usb_storage module is loaded before waiting for usb storage devices to land (Mdv bug #50179
- rc.d/init.d/halt: Prevent "Sending all processes the KILL signal [Failed]" error (#45059)

* Tue Apr 21 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-19mdv2009.1
+ Revision: 368556
- load acpi in first pass in speedboot mode, fix clock timezone in syslog (Mdv bug #49513)-
- ensure usb keyboard is available under speedboot for single user rescue login
- ensure splashy is killed correctly if dropping to single user login (for fsck)
- Restrict agp module load to pci system (speedboot)
- put back udev in non-startup mode after latest udev settle (speedboot)

* Thu Apr 16 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-18mdv2009.1
+ Revision: 367749
- Enable back hdparm in speedboot mode, run it in parallel (both in speedboot and standard mode)
- remove obsolete libsafe support
- Add support for system-wide wireless ruglartory domain (Eugeni) (Mdv bug #49982, #49983, #49171)
- Fix usb-storage detection (Mdv bug #49474)
- Drop specific support for firewire stage, it should work with udev out of the box (and was broken for several releases).
- Translation updates
- Improve network-up logic (Mdv bug #49702)
- Fix ifup-ppp syntax error (Mdv bug #49942)

* Wed Apr 08 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-17mdv2009.1
+ Revision: 365193
- improve translations
- no longer limit udev child numbers, fix DRI being disabled in speedboot (Mdv bug #49490)

* Thu Apr 02 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-16mdv2009.1
+ Revision: 363589
- translations updates
- speedboot is not in automatic mode : it will try to enable itself if system can support it, or disable automatically in case of failure

* Fri Mar 27 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-15mdv2009.1
+ Revision: 361663
- fix detection of runlevel for usage in speedboot and stop splashy very early when starting in single user runlevel (me and eugeni)
- disable speedboot when runlevel is not 5
- disable speedboot when booting on a new kernel version for the first time
- disable speedboot when network authentication is enabled
- flag critical path when speedboot shouldn't be enabled (for speedboot auto-enabling, work in progress, not ready yet)
- add ypbind / winbkind and ldpa to network-auth dependencies (Eugeni)
- accept booting after some fsck errors like missing disk (Mdv bug #47242) (pterjan)
- cleanup rc.sysinit
- ensure /proc is mounted before reading /proc/cmdline (blino)

* Thu Mar 26 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.88-14mdv2009.1
+ Revision: 361229
- Properly killing splashy when going to single-user mode.

* Tue Mar 24 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-13mdv2009.1
+ Revision: 360878
- Fix text not being displayed in splashy when booting

* Mon Mar 23 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-12mdv2009.1
+ Revision: 360729
- Enable readahead in speedboot mode
- Don't process some udev events twice in speedboot mode

* Thu Mar 19 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-11mdv2009.1
+ Revision: 358089
- Various speedboot fixes :
 - fix guest support under Virtualbox (Mdv bug #47726)
 - fix module preloading (Mdv bug #47974)
 - fix keyboard configuration in X with speedboot (Mdv bug #47638)
 - remove hardcoded delay after starting X server

* Wed Mar 18 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.88-10mdv2009.1
+ Revision: 357493
- Fixed typo (missing white space).
- Added support for CRDA regulatory domains (#47324).

* Mon Mar 16 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.88-9mdv2009.1
+ Revision: 356214
- Stopping splashy when going to single-user mode (#46169).
- Suggesting portreserve via ShouldStart in network-up.
- Support hdparm parameters for sd* devices (#45746).
- Stopping splashy when asking for LUKS password (#43325).

* Tue Feb 10 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-8mdv2009.1
+ Revision: 339180
- Ensure /proc/bus/usb is mounted in speedboot mode
- Disable fastboot mode when using speedboot : fsck is done in speedboot mode now

* Tue Feb 10 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.88-7mdv2009.1
+ Revision: 339054
- Do not rely on plymouth for asking for LUKS partition passwords (#47670)
- Do not enable comgt for ADSL/xDSL connections (#47673)

* Fri Feb 06 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-6mdv2009.1
+ Revision: 338098
- Trigger block subsystem udev events early in speedboot mode (Mdv bug #47607)

* Thu Feb 05 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-5mdv2009.1
+ Revision: 337917
- Add support for runlevel 7, acting as runlevel S
- Speedboot, phase 1, implemented

* Wed Feb 04 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-4mdv2009.1
+ Revision: 337494
- Fix mismerge in rc.sysinit

* Wed Feb 04 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-3mdv2009.1
+ Revision: 337474
- package RH ChangeLog too
- mandriva_everytime :
    Don't handle supermount anymore, don't create /var/log/dmesg twice
- rc.sysinit : Cleanup obsolete stuff
    -ensure cmdline is set before using it
    -mount devpts / shm unconditionnaly
    -no longer load sound module (let udev do the job)
    -no longer call devlabel (no longer exist)
    -no longer modprobe aes (module no longer exist)
    -no longer remove rpm __db* at startup (rpm is autocleaning itself now)
    -no longer remove some temporary files twice
    -remove duplicate work for encrypted swap
    -merge back some stuff from RH initscript (to ease merge)
    -cache uname -r result

* Fri Jan 23 2009 Eugeni Dodonov <eugeni@mandriva.com> 8.88-2mdv2009.1
+ Revision: 333037
- Do not kill xsupplicant in ifdown-eth, as it could still be in use (#47052).

* Thu Jan 22 2009 Frederic Crozat <fcrozat@mandriva.com> 8.88-1mdv2009.1
+ Revision: 332568
- Release 8.88

* Fri Dec 19 2008 Olivier Blin <blino@mandriva.org> 8.81-9mdv2009.1
+ Revision: 316078
- use Patch0 instead of Patch for new rpm

  + Frederic Crozat <fcrozat@mandriva.com>
    - Update dm initscript to start after hald

* Wed Nov 26 2008 Olivier Blin <blino@mandriva.org> 8.81-8mdv2009.1
+ Revision: 307154
- add support for ATM bridging (for pppoe over USB modems, #35797)
- do not source 10lang.sh twice, it is useless for autologin

* Tue Sep 30 2008 Olivier Blin <blino@mandriva.org> 8.81-7mdv2009.0
+ Revision: 290076
- dm service:
  o require messagebus instead of consolekit (dbus now spawns consolekit)
  o harddrake and dkms are not services anymore, do not soft-require them

* Mon Sep 29 2008 Olivier Blin <blino@mandriva.org> 8.81-6mdv2009.0
+ Revision: 289231
- add support for readahead / readahead-collector early at boot time
  (from Frederic Crozat)

* Tue Sep 23 2008 Olivier Blin <blino@mandriva.org> 8.81-5mdv2009.0
+ Revision: 287633
- check that /proc/cmdline exists before checking for splash inside
  (to hide error messages at One shutdown)
- rc.modules:
  o use modprobe -a to run modprobe one time only
  o support modprobedebug debug option (#28212)
  o do not hide modprobe stdout
  o drop 2.4 modules support (removes one more modprobe call)
  o use full path for modprobe

* Sat Sep 20 2008 Olivier Blin <blino@mandriva.org> 8.81-4mdv2009.0
+ Revision: 286079
- implement $PERSISTENT_DHCLIENT that causes dhclient to be run in
  persistent mode, i.e. not giving up after one try to get an IP
  address (ported from upstream, by Anssi)

* Fri Sep 19 2008 Olivier Blin <blino@mandriva.org> 8.81-3mdv2009.0
+ Revision: 285992
- start dkms and harddrake in mandrake_everytime
  (faster than running them in parallel init)
- load usb-storage module very early so that the usb-stor-scan process
  gets a chance to run in background sooner, not to block boot waiting
  for it later (thanks to Frederic Crozat for the debugging)
- make partmon configurable in %{_sysconfdir}/sysconfig/partmon (#40625)
- fix improper quoting in 10tmpdir.sh (from vdanen, #40256)

* Tue Sep 02 2008 Olivier Blin <blino@mandriva.org> 8.81-2mdv2009.0
+ Revision: 279131
- network-up: do not incorrectly wait for DNS to be set if not needed
  (patch from AAW, #42687)

* Mon Sep 01 2008 Olivier Blin <blino@mandriva.org> 8.81-1mdv2009.0
+ Revision: 278334
- 8.81

* Tue Aug 19 2008 Olivier Blin <blino@mandriva.org> 8.80-3mdv2009.0
+ Revision: 273671
- add network-auth meta-service that requires network to be up
  (to be enabled when auth requires network)
- dm: depend on network-auth instead of network-up
  (not to slow down boot when auth does not require network)
- do not follow symlinks when cleaning /var/lock and /var/run
  (breaks vserver)

* Fri Aug 08 2008 Olivier Blin <blino@mandriva.org> 8.80-2mdv2009.0
+ Revision: 267991
- do not try to unmount mountpoints in /live at halt or when unmounting loopbacks

* Wed Aug 06 2008 Olivier Blin <blino@mandriva.org> 8.80-1mdv2009.0
+ Revision: 264128
- fix group of debugmode package
- 8.80
- build without upstart
- do not create %{_sysconfdir}/sysconfig/networking/tmp
- do not link %{_sysconfdir}/init.d, it's done in chkconfig
- do not make ifcfg-lo a symlink to old networking directory
- do not load sysctl conf twice
- do not set loglevel twice
- fix ip route syntax (#42503)

* Fri Aug 01 2008 Olivier Blin <blino@mandriva.org> 8.63-15mdv2009.0
+ Revision: 259573
- run wpa_cli reassociate if WIRELESS_WPA_REASSOCIATE is "yes"
  (for rt61pci)
- add more splash steps during shutdown

* Tue Jul 29 2008 Olivier Blin <blino@mandriva.org> 8.63-14mdv2009.0
+ Revision: 252732
- allow splash to be enabled at shutdown
- fix checking that fb0 is present (by using sysfs)

* Fri Jul 25 2008 Olivier Blin <blino@mandriva.org> 8.63-13mdv2009.0
+ Revision: 249732
- network-up: wait for DNS changes to be propagated by resolvconf if
  needed (thanks to Guillaume Rousse)
- check that splashy is available with "splashy_update test"
  (a zombie process might still live for a while if splashy is
  terminated from initrd)

* Wed Jul 23 2008 Olivier Blin <blino@mandriva.org> 8.63-12mdv2009.0
+ Revision: 243732
- allow not to kill pids contained in /var/run/sendsigs.omit
  (inspired by Debian, to be used by splashy)
- detect splashy
- do not create fb0, this will be done in initrd
- avoid tty to be corrupted by splashy (from debian initscript)
- do not start brltty if BRLTTY is set to "no" in %{_sysconfdir}/sysconfig/init
- prefdm (ander): quote the argument $dm since the preferred window
  manager may contain whitespace in its name (i.e. KDM 3)

* Fri Jun 20 2008 Pixel <pixel@mandriva.com> 8.63-10mdv2009.0
+ Revision: 227382
- lookupdm: %{_sysconfdir}/X11/dm.d is now /usr/share/X11/dm.d

* Tue Jun 03 2008 Olivier Blin <blino@mandriva.org> 8.63-9mdv2009.0
+ Revision: 214498
- ppp connections:
  o do not delete random route if there is no route matching a ppp
    interface that is brought up
  o use multipledefaultroutes option to add a default route for the
    ppp connection even if a default route already exists
    (and conflicts with pppd <= 2.4.4-3mdv2008.1)
  o set PIN code if needed when bringing ppp devices up (#34940, #40531)
- add ifup/ifdown scripts for hso devices (using custom AT_OWAN commands)
- retry failed udev events after local filesystems are mounted read-write
  (useful for rules creating network ifcfg files)

* Tue May 06 2008 Olivier Blin <blino@mandriva.org> 8.63-8mdv2009.0
+ Revision: 202422
- init splash after font is reset (to make splash text messages
  reappear, #38882)
- create /dev/fb0 before splash is initialized (#38338)
- make sure resolvconf is available before network service is stopped
  (for cleaner stop of network-related services)

* Thu Apr 03 2008 Olivier Blin <blino@mandriva.org> 8.63-7mdv2008.1
+ Revision: 192200
- do not use DNS* variables from config file if PEERDNS is true and
  BOOTPROTO is dhcp, this is handled by dhcp clients (#39312)
  (still use DNS* if RESOLV_MODS is true)
- support new WIRELESS_ENC_MODE variable (for open/restricted, to help
  fixing #26025)
- run ifplugd with -I by default (so that it does not abort when
  ifup/ifdown/dhclient fails)
- do not allow to run wpa_supplicant twice for the same interface,
  wpa_supplicant deauthenticate the connection when it fails (#38565)
- wait for wireless interfaces associated to an access point (#36964)
- do not add incorrect -D option for dhcpcd
- mount /dev/pts and /dev/shm after /dev is mounted by udev (so that
  /dev/pts gets correctly mounted when not using initrd, #30866)
- enable netfs/netconsole/dm services after network-up in post and
  preun (from Anssi)
- allow to display netfs status if network is disabled
  (from Pascal Terjan, #24579)

* Tue Mar 25 2008 Olivier Blin <blino@mandriva.org> 8.63-6mdv2008.1
+ Revision: 190051
- do not start hclcollector in mandrake_firstime anymore, will be done by drakfirsttime (#39259)

* Fri Mar 21 2008 Olivier Blin <blino@mandriva.org> 8.63-5mdv2008.1
+ Revision: 189326
- do not require messagebus in network service (it looks like network
  has to be up when dbus is started, with pam_ldap)
- export LC_ALL and LANG instead of running lang.sh for ntfs-3g mount
  (#38880)
- fix console mode setup in lang scripts when charset is not UTF-8
  (from Herton, #35082)
- mdv-network-event: do not check for /var/run/dbus/system_bus_socket,
  just hide errors
- run /sbin/halt.pre if present before umounting filesystems in
  %{_sysconfdir}/init.d/halt

* Mon Mar 10 2008 Olivier Blin <blino@mandriva.org> 8.63-4mdv2008.1
+ Revision: 183583
- export locale when mounting local filesystem (for ntfs-3g, #32436)
- do not check / if already rw (for example with unionfs)
- remove /tmp/esd-<uid> and /tmp/pulse-* directories at startup (fcrozat)

* Thu Feb 21 2008 Olivier Blin <blino@mandriva.org> 8.63-3mdv2008.1
+ Revision: 173656
- keep UUID of swap partitions when resuming from hibernation (#37915)
- require util-linux-ng >= 2.13.1-4mdv2008.1 for mkswap -U <uuid> support

* Mon Feb 18 2008 Olivier Blin <blino@mandriva.org> 8.63-2mdv2008.1
+ Revision: 171866
- rc.sysinit:
  o don't source %{_sysconfdir}/sysconfig/init (already done by /etc/init.d/functions)
  o mount /proc/bus/usb before udev is started
  o remove duplicate pam_console reset
  o reduce diff with RH by moving quota and crypto code around

* Fri Feb 08 2008 Olivier Blin <blino@mandriva.org> 8.63-1mdv2008.1
+ Revision: 163839
- 8.63
- raid is not enabled in rc.sysinit anymore, but in udev rules from the mdadm package
- clock is now initialized with udev rules
- drop EVMS support and duplicate LVM2 activation
- do not require bootloader-utils anymore

* Thu Jan 17 2008 Olivier Blin <blino@mandriva.org> 8.60-2mdv2008.1
+ Revision: 154214
- conflicts with lsb-core < 3.1-15mdv2008.1 (%{_sysconfdir}/networks has been moved in initscripts)
- set MIN_LINK_DETECTION_DELAY (to zero)
- do not make profile scripts executable
  (based on input from Guillaume Rousse)
- prefix inputrc and tmpdir profile scripts with a level number

* Tue Jan 15 2008 Olivier Blin <blino@mandriva.org> 8.60-1mdv2008.1
+ Revision: 153094
- 8.60
- remove default MIN_LINK_DETECTION_DELAY (to catch buggy drivers)
- add support for an optional %{_sysconfdir}/rc.early.local file, to be run at
  the very start of rc.sysinit (suggested by Colin Guthrie)
- nfs-common should be started before netfs (Anssi)

* Wed Oct 03 2007 Olivier Blin <blino@mandriva.org> 8.54-8mdv2008.0
+ Revision: 95267
- 8.54-8mdv
- update translations

* Thu Sep 27 2007 Olivier Blin <blino@mandriva.org> 8.54-7mdv2008.0
+ Revision: 93319
- fix regexps with non-working obsoleted syntax
  (from Nicolas Vigier, thanks to Anssi Hannula, #32501)
- add should-start/stop for messagebus, since ifup/ifdown run mdv-network-event (#34076)
- add explicit provides in netconsole initscript
- more typo fixes (from Jose Da Silva)

* Thu Sep 20 2007 Olivier Blin <blino@mandriva.org> 8.54-6mdv2008.0
+ Revision: 91318
- 8.54-6mdv
- ifdown: do not kill wpa_supplicant when link gets down
  (#31904, thanks to Anssi Hannula)
- ifup/ifdown: send D-Bus events when interfaces get up/down
- mandrake_firstime: start hclcollector in mandrake_firstime
- rc.sysinit: delete core files located in gdm directory, at startup
  (#28166, from Frederic Crozat)
- netconsole: add LSB header (from Goetz Waschk)
- service: fix typos and do not exceed 80 chars (from Jose Da Silva)
- lang.sh: move LANGUAGE redefine (CONSOLE_NOT_LOCALIZED) later, so
  that it will not overrided by *.UTF-8 step (from Funda Wang)
- po: use local mirror to extract init.d files (from Funda Wang)
- remove obsolete usb service (2.4 specific)

* Mon Aug 20 2007 Olivier Blin <blino@mandriva.org> 8.54-5mdv2008.0
+ Revision: 68050
- really use MIN_LINK_DETECTION_DELAY (#31864, thanks to Emmanuel Blindauer for the debugging)
- add dependency on consolekit (#32555, from fcrozat)

* Fri Aug 10 2007 Olivier Blin <blino@mandriva.org> 8.54-4mdv2008.0
+ Revision: 61663
- disable supermount on upgrade, it's not supported anymore in our kernels (from Pixel)
- fix locking in udev rules (from Andrey Borzenkov, #32281)
- fix UTF-8 support by removing mandrake_consmap since we use kdb (from Herton Ronaldo Krzesinski, #32256)
- remove duplicate "Press 'I' to enter interactive startup." phase
- start brltty after udev so that vcsa device nodes are created (thanks to fcrozat)

* Wed Aug 01 2007 Olivier Blin <blino@mandriva.org> 8.54-3mdv2008.0
+ Revision: 57809
- remove setsysfont, use kbd and update doc (from Herton Ronaldo Krzesinski)
- modprobe IDE controller at system start (#32150)

* Sat Jul 07 2007 Olivier Blin <blino@mandriva.org> 8.54-2mdv2008.0
+ Revision: 49354
- from Ademar:
  add xfs to dm's 'Should-Start:', since it's still supported,
  just not enabled by default (thanks Blino for spotting this)

* Fri Jul 06 2007 Olivier Blin <blino@mandriva.org> 8.54-1mdv2008.0
+ Revision: 48955
- 8.54
- set LANGUAGE and LC_ALL for prcsys (#27663)
- from Herton: small typo fix in setsysfont script
- from Ademar: xfs is not needed by dm anymore,
  xorg now uses fontpath.d and xfs is deprecated (see #31756)
- exclude supermount on all sparc archs (Per Oyvind Karlsen, #30622)

* Tue May 01 2007 Olivier Blin <blino@mandriva.org> 8.53-1mdv2008.0
+ Revision: 19999
- 8.53

