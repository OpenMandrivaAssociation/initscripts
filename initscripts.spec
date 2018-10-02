#this is required since latest glibc (new atomic OPs?)
%global __requires_exclude GLIBC_PRIVATE

%define _systemdrootdir /lib/systemd

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
BuildRequires:	gettext-devel

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
%make_build CC="%{__cc}" RPM_OPT_FLAGS="%{optflags}" RPM_LD_FLAGS="%{ldflags}" udevdir="/lib/udev/"

%install
mkdir -p %{buildroot}/lib/udev
%make_install CC="%{__cc}" RPM_OPT_FLAGS="%{optflags}" RPM_LD_FLAGS="%{ldflags}" libdir="/%{_lib}" libexecdir="%{_libexecdir}" datadir="%{_datadir}" mandir="%{_mandir}" sysconfdir="%{_sysconfdir}" udevdir="/lib/udev/" bindir="/bin" sbindir="/sbin"

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
%dir %{_sysconfdir}/sysconfig/console
%dir %{_sysconfdir}/sysconfig/modules
%dir %{_sysconfdir}/rwtab.d
%dir %{_sysconfdir}/statetab.d
%dir %{_sysconfdir}/rc.d/init.d

%config %{_sysconfdir}/profile.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/netconsole
%config(noreplace) %{_sysconfdir}/sysconfig/readonly-root
%{_sysconfdir}/sysconfig/network-scripts/*
%{_sysconfdir}/X11/prefdm
%{_sysconfdir}/X11/lookupdm
%{_presetdir}/86-initscripts.preset
/bin/usleep
/sbin/consoletype
/sbin/genhostid
/sbin/netreport
/sbin/ifdown
/sbinifup
%{_sysconfdir}/rwtab
%{_sysconfdir}/statetab
/lib/udev/rules.d/*
/lib/lsb/init-functions
%{_sysconfdir}/rc.d/init.d/*
%attr(4755,root,root) %{_sbindir}/usernetctl
/lib/udev/rename_device
%ifarch s390 s390x
/lib/udev/ccw_init
%endif
/sbin/service
/sbin/sushell
#mdv
/sbin/hibernate-cleanup.sh
%{_mandir}/man*/*
%dir %attr(775,root,root) /run/netreport
%dir %{_sysconfdir}/NetworkManager
%dir %{_sysconfdir}/NetworkManager/dispatcher.d
%{_sysconfdir}/NetworkManager/dispatcher.d/00-netreport
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
%{_libexecdir}/domainname
%{_libexecdir}/import-state
%{_libexecdir}/loadmodules
%{_libexecdir}/readonly
%{_unitdir}/domainname.service
%{_unitdir}/import-state.service
%{_unitdir}/loadmodules.service
%{_unitdir}/readonly.service
