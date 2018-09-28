#this is required since latest glibc (new atomic OPs?)
%global __requires_exclude GLIBC_PRIVATE

Summary:	Scripts to bring up network interfaces and legacy utilities
Name:		initscripts
Version:	10.01
Release:	1
License:	GPLv2
Group:		System/Base
Url:		https://github.com/fedora-sysv/initscripts
Source0:	https://github.com/fedora-sysv/initscripts/archive/%{name}-%{version}.tar.gz
Source1:	60-scheduler.rules
Source100:	%{name}.rpmlintrc
Patch0:		initscripts-10.01-fix-paths.patch
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig
BuildRequires:	popt-devel
BuildRequires:	systemd-macros
Buildrequires:	gettext-devel

Requires(posttrans):	rpm-helper >= 0.24.17
Requires(posttrans):	systemd >= 235
Requires:	chkconfig
Requires:	bash
Requires:	filesystem
Requires:	coreutils
Requires:	gawk
Requires:	findutils
Requires:	grep
Requires:	procps-ng
Requires:	setup >= 2.8.9
Requires:	systemd
Requires:	util-linux > 2.31
Requires:	shadow
Requires:	cpio
Requires:	hostname >= 3.16
Requires:	iproute2
Requires:	ipcalc
Requires:	iputils
Requires:	kmod
Requires:	sed
Requires:	glibc
Requires:	bc
Requires:	dbus
Requires:	net-tools >= 2.0
Requires:	ethtool
Provides:	/sbin/service
%rename %{name}-debugmode

%description
The initscripts package contains the basic system scripts used to boot
your %{distribution} system, change run levels, and shut the system
down cleanly.  Initscripts also contains the scripts that activate and
deactivate most network interfaces.

%prep
%autosetup -p1

%build
%setup_compile_flags
export CC=%{__cc}

%make_build

%install
%make_install udevdir="/lib/udev/"

# (tpg) remove as its not needed
for i in 0 1 2 3 4 5 6; do
rm -rf %{buildroot}%{_sysconfdir}/rc$i.d ;
done

%find_lang %{name}

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-initscripts.preset << EOF
disable import-state.service
enable loadmodules.service
disable readonly.service
disable network
disable netconsole
disable dm
disable network-up
disable partmon
EOF

# add networking file
cat > %{buildroot}%{_sysconfdir}/sysconfig/network << EOF
NETWORKING=yes
NETWORKING_IPV6=no
EOF

install -m644 -D %{SOURCE1} %{buildroot}/lib/udev/rules.d/60-scheduler.rules

%posttrans
%systemd_post loadmodules.service

##Fixme
touch /etc/sysconfig/i18n
##
touch /var/log/wtmp /var/log/btmp
chown root:utmp /var/log/wtmp /var/log/btmp
chmod 664 /var/log/wtmp
chmod 600 /var/log/btmp

%preun
%systemd_preun import-state.service loadmodules.service readonly.service

%transfiletriggerpostun -- %{_initrddir}/
find -L /etc/rc.d/rc{0,1,2,3,4,5,6,7}.d -type l -delete

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
%config(noreplace) %{_sysconfdir}/sysconfig/autofsck
%config(noreplace) %{_sysconfdir}/sysconfig/netconsole
%config(noreplace) %{_sysconfdir}/sysconfig/readonly-root
%{_sysconfdir}/sysconfig/network-scripts/ifdown
%{_presetdir}/86-initscripts.preset
/bin/usleep
/sbin/ifdown
%{_sysconfdir}/sysconfig/network-scripts/ifdown-post
%{_sysconfdir}/sysconfig/network-scripts/ifup
/sbin/ifup
%dir %{_sysconfdir}/sysconfig/console
%dir %{_sysconfdir}/sysconfig/console/consoletrans
%dir %{_sysconfdir}/sysconfig/console/consolefonts
%dir %{_sysconfdir}/sysconfig/modules
%config(noreplace) %{_sysconfdir}/sysconfig/network
%{_sysconfdir}/sysconfig/network-scripts/network-functions
%{_sysconfdir}/sysconfig/network-scripts/network-functions-ipv6
%{_sysconfdir}/sysconfig/network-scripts/init.ipv6-global
%config(noreplace) %{_sysconfdir}/sysconfig/network-scripts/ifcfg-lo
%{_sysconfdir}/sysconfig/network-scripts/ifup-post
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
%dir %{_sysconfdir}/rc.d/init.d
/lib/lsb/init-functions
%{_sysconfdir}/rc.d/init.d/*
%config %{_sysconfdir}/profile.d/*
%dir %{_sysconfdir}/sysconfig/network-scripts/cellular.d
%dir %{_sysconfdir}/sysconfig/network-scripts/hostname.d
%{_sysconfdir}/sysconfig/network-scripts/ifup.d/vpn
%{_sysconfdir}/sysconfig/network-scripts/ifdown.d/vpn
%{_sbindir}/vpn-start
%{_sbindir}/vpn-stop
%{_sbindir}/mdv-network-event
%{_sbindir}/sys-unconfig
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
%{_mandir}/man*/*
%lang(cs) %{_mandir}/cs/man*/*
%lang(et) %{_mandir}/et/man*/*
%lang(fi) %{_mandir}/fi/man*/*
%lang(fr) %{_mandir}/fr/man*/*
%lang(it) %{_mandir}/it/man*/*
%lang(pt_BR) %{_mandir}/pt_BR/man*/*
%lang(ru) %{_mandir}/ru/man*/*
%lang(uk) %{_mandir}/uk/man*/*
%dir %attr(775,root,root) /run/netreport
%dir %{_sysconfdir}/NetworkManager
%dir %{_sysconfdir}/NetworkManager/dispatcher.d
%{_sysconfdir}/NetworkManager/dispatcher.d/00-netreport
%doc sysconfig.txt sysvinitfiles static-routes-ipv6 ipv6-tunnel.howto ipv6-6to4.howto changes.ipv6
/var/lib/stateless
%ghost %attr(0664,root,utmp) /var/log/btmp
%ghost %attr(0664,root,utmp) /var/log/wtmp
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/crypttab
%config(noreplace) %{_sysconfdir}/modules
%{_sysconfdir}/rc.modules
%dir %{_sysconfdir}/modprobe.preload.d/
%{_bindir}/*
%dir /lib/tmpfiles.d
/lib/tmpfiles.d/initscripts.conf
%{_systemdrootdir}/fedora-domainname
%{_systemdrootdir}/fedora-import-state
%{_systemdrootdir}/fedora-loadmodules
%{_systemdrootdir}/fedora-readonly
%{_unitdir}/fedora-domainname.service
%{_unitdir}/fedora-import-state.service
%{_unitdir}/fedora-loadmodules.service
%{_unitdir}/fedora-readonly.service
