%define _requires_exceptions GLIBC_PRIVATE

Summary:	Scripts to bring up network interfaces and legacy utilities
Name:		initscripts
Version:	9.66
Release:	3
License:	GPLv2
Group:		System/Base
# Upstream URL: http://git.fedorahosted.org/git/initscripts.git
Url:		https://github.com/OpenMandrivaSoftware/initscripts
Source0:	%{name}-%{version}.tar.xz
Source100:	%{name}.rpmlintrc
Patch0:		0001-usr-bin-systemd-escape-to-bin-systemd-escape-in-serv.patch

BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig
BuildRequires:	popt-devel
BuildRequires:	pkgconfig(python3)

Requires:	basesystem-minimal
Requires(pre):	basesystem-minimal
Requires(post):	rpm-helper
Requires(post):	util-linux
Requires(post):	chkconfig
Requires:	gettext-base >= 0.10.35-20mdk
# for /sbin/ip
Requires:	iproute2
Requires:	hostname >= 3.16
Requires:	net-tools >= 2.0
Requires:	ipcalc
# (blino) for pidof -c
# (bor) for pidof -m
Requires:	procps-ng
Requires:	ifplugd >= 0.24
Requires:	ethtool
Requires:	ifmetric
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

%apply_patches

%build
%setup_compile_flags
export CC=%{__cc}

%make
%make -C mandriva

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

# (cg) Upstream should stop shipping this too IMO (it's systemd's job now)
rm -f %{buildroot}/var/run/utmp

# (cg) Clean up danging symlinks after initscript removal
install -d %{buildroot}%{_var}/lib/rpm/filetriggers
cat > %{buildroot}%{_var}/lib/rpm/filetriggers/clean-legacy-sysv-symlinks.filter << EOF
^.%{_initrddir}/
EOF
cat > %{buildroot}%{_var}/lib/rpm/filetriggers/clean-legacy-sysv-symlinks.script << EOF
#!/bin/sh
find -L /etc/rc.d/rc{0,1,2,3,4,5,6,7}.d -type l -exec rm -f {} +
EOF
chmod 755 %{buildroot}%{_var}/lib/rpm/filetriggers/clean-legacy-sysv-symlinks.script

# (tpg) kill it with fire
rm -rf %{buildroot}%{_initddir}/dm

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-initscripts.preset << EOF
enable network
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

# (tpg) remove broken links
rm -rf %{buildroot}%{_systemunitdir}/basic.target.wants/fedora-autorelabel.service
rm -rf %{buildroot}%{_systemunitdir}/basic.target.wants/fedora-autorelabel-mark.service

%pre
if [ $1 -ge 2 ]; then
    if [ -e %{_sysconfdir}/sysctl.conf ] && [ ! -L %{_sysconfdir}/sysctl.conf ]; then
	mv -f %{_sysconfdir}/sysctl.conf %{_sysconfdir}/sysctl.d/99-sysctl.conf
	ln -s %{_sysconfdir}/sysctl.d/99-sysctl.conf %{_sysconfdir}/sysctl.conf
    fi
fi


%posttrans
##
touch /var/log/wtmp /var/log/btmp
chown root:utmp /var/log/wtmp /var/log/btmp
chmod 664 /var/log/wtmp
chmod 600 /var/log/btmp

# Add right translation file
for i in `echo $LANGUAGE:$LC_ALL:$LC_COLLATE:$LANG:C | tr ':' ' '`
do
    if [ -r %{_datadir}/locale/$i/LC_MESSAGES/initscripts.mo ]; then
	mkdir -p /etc/locale/$i/LC_MESSAGES/
	cp %{_datadir}/locale/$i/LC_MESSAGES/initscripts.mo /etc/locale/$i/LC_MESSAGES/
#
# warly
# FIXME: this should be done by each locale when installed or upgraded
#
	pushd %{_datadir}/locale/$i/ > /dev/null && for j in LC_*
	do
	    if [ -r $j -a ! -d $j ]; then
		cp $j /etc/locale/$i/
	    fi
	done && popd > /dev/null
	if [ -r %{_datadir}/locale/$i/LC_MESSAGES/SYS_LC_MESSAGES ]; then
	    cp %{_datadir}/locale/$LANG/LC_MESSAGES/SYS_LC_MESSAGES /etc/locale/$i/LC_MESSAGES/
	fi
#
#
	break
    fi
done

if [ $1 -ge 2 ]; then
# (tpg) die! systemd takes care of this
chkconfig --del dm > /dev/null 2>&1 || :
# (tpg) kill this too
chkconfig --del partmon > /dev/null 2>&1 || :
fi

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
%dir %attr(775,root,root) /var/run/netreport
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
/lib/tmpfiles.d/mandriva.conf
%{_var}/lib/rpm/filetriggers/clean-legacy-sysv-symlinks.*
%{_systemdrootdir}/fedora-domainname
%{_systemdrootdir}/fedora-import-state
%{_systemdrootdir}/fedora-loadmodules
%{_systemdrootdir}/fedora-readonly
%{_systemdrootdir}/mandriva-save-dmesg
%{_systemunitdir}/basic.target.wants/fedora-loadmodules.service
%{_systemunitdir}/basic.target.wants/mandriva-everytime.service
%{_systemunitdir}/fedora-domainname.service
%{_systemunitdir}/fedora-import-state.service
%{_systemunitdir}/fedora-loadmodules.service
%{_systemunitdir}/fedora-readonly.service
%{_systemunitdir}/mandriva-everytime.service
%{_systemunitdir}/mandriva-save-dmesg.service
%{_systemunitdir}/local-fs.target.wants/fedora-import-state.service
%{_systemunitdir}/local-fs.target.wants/fedora-readonly.service
%{_systemunitdir}/mandriva-kmsg-loglevel.service

%files debugmode
%config(noreplace) %{_sysconfdir}/sysconfig/debug
%config %{_sysconfdir}/profile.d/debug*
