# 	$Id: initscripts.spec 252003 2009-01-22 17:26:21Z eugeni $	

# The restart part in the real _post_service doesn't work with netfs and isn't needed
# for other scripts
%define _mypost_service() if [ $1 = 1 ]; then /sbin/chkconfig --add %{1}; fi;

%define with_upstart 0%{nil} 

Summary: The inittab file and the /etc/init.d scripts
Name: initscripts
Version: 8.99
Release: %mkrel 10
# ppp-watch is GPLv2+, everything else is GPLv2
License: GPLv2 and GPLv2+
Group: System/Base
Source0: initscripts-%{version}.tar.bz2
Patch0:	initscripts-mdkconf.patch
BuildRoot: /%{_tmppath}/%{name}-%{version}-%{release}-root
Requires: mingetty
# for /bin/awk
Requires: gawk
# for /bin/sed
Requires: sed
Requires: mktemp
Requires: e2fsprogs >= 1.18-2mdk
Requires: procps >= 2.0.7-8mdk
Requires: gettext-base >= 0.10.35-20mdk
Requires: module-init-tools
#Requires: sysklogd >= 1.3.31
# for /sbin/fuser
Requires: psmisc
Requires: which
Requires: setup >= 2.2.0-14mdk
%if %{with_upstart}
Requires: upstart
Obsoletes: event-compat-sysv
%else
Requires: SysVinit >= 2.85-38
%endif
# for /sbin/ip
Requires: iproute2
# for /sbin/arping
Requires: iputils
Requires: net-tools
# for /bin/find
Requires: findutils
# (blino) for pidof -c
Requires: sysvinit-tools >= 2.87

Requires: perl-MDK-Common >= 1.0.1
Requires: ifplugd >= 0.24
Requires: sound-scripts
# (tv) unused:
#Prereq: gawk
Requires: iproute2
Requires: ethtool
# http://bugzilla.redhat.com/show_bug.cgi?id=252973
Conflicts: nut < 2.2.0
Obsoletes: rhsound sapinit
Provides: rhsound sapinit
Conflicts: kernel <= 2.2, timeconfig < 3.0, pppd <= 2.4.4-3mdv2008.1, wvdial < 1.40-3
Conflicts: initscripts < 1.22.1-5, Aurora <= 7.2-17mdk
Conflicts: dhcpcd < 1.3.21pl1
Conflicts: XFree86-xfs < 4.2.0-12mdk
Conflicts: xinitrc < 2.4.12
Conflicts: lsb < 3.1-11mdv2007.1
Conflicts: lsb-core < 3.1-15mdv2008.1
Conflicts: suspend-scripts < 1.27
Conflicts: mdadm < 2.6.4-2mdv2008.1
Requires: util-linux-ng >= 2.16
Requires: mount >= 2.11l
Requires: udev >= 108-2mdv2007.1
Requires: ifmetric, resolvconf >= 1.41
Requires: dmsetup
Requires: prcsys
Requires(post): /usr/bin/tr grep, chkconfig >= 1.3.37-3mdk
BuildRequires: glib2-devel
BuildRequires: pkgconfig
BuildRequires: popt-devel
BuildRequires: python
# Upstream URL: http://git.fedorahosted.org/git/initscripts.git
Url: http://svn.mandriva.com/cgi-bin/viewvc.cgi/soft/initscripts/trunk/

#this is required since latest glibc (new atomic OPs?)
%define _requires_exceptions GLIBC_PRIVATE


%description
The initscripts package contains the basic system scripts used to boot
your Mandriva Linux system, change run levels, and shut the system
down cleanly.  Initscripts also contains the scripts that activate and
deactivate most network interfaces.

%package -n debugmode
Summary: Scripts for running in debugging mode
Requires: initscripts
Group: System/Base

%description -n debugmode
The debugmode package contains some basic scripts that are used to run
the system in a debugging mode.

Currently, this consists of various memory checking code.

%prep
%setup -q
rm -rf po
%patch0 -p0
rm -f po
ln -s mandriva/po

gzip -9 mandriva/ChangeLog
mv ChangeLog ChangeLog-RH
gzip -9 ChangeLog-RH

%build
make
make -C mandriva CFLAGS="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc
make ROOT=$RPM_BUILD_ROOT SUPERUSER=`id -un` SUPERGROUP=`id -gn` mandir=%{_mandir} install

#MDK
make -C mandriva install ROOT=$RPM_BUILD_ROOT mandir=%{_mandir}

python mandriva/gprintify.py `find %{buildroot}/etc/rc.d -type f` `find %{buildroot}/sysconfig/network-scripts -type f`

# warly 
# put locale in /usr, gettext need /usr/share
#
# extracted from /usr/lib/rpm/find-lang.sh and adapted to find locales in /etc
#find $RPM_BUILD_ROOT -type f|sed '
#1i\
#%defattr (644, root, root, 755)
#s:'"$RPM_BUILD_ROOT"'::
#s:\(.*/etc/locale/\)\([^/_]\+\)\(.*'"$NAME"'\.mo$\):%lang(\2) \1\2\3:
#s:^\([^%].*\)::
#s:%lang(C) ::
#' >> %{name}.lang

%find_lang %{name}

%if %{with_upstart}
 mv -f $RPM_BUILD_ROOT/etc/inittab.upstart $RPM_BUILD_ROOT/etc/inittab
 rm -f $RPM_BUILD_ROOT/etc/rc.d/rc1.d/S99single
 rm -f $RPM_BUILD_ROOT/etc/rc.d/init.d/single
%else
 mv -f $RPM_BUILD_ROOT/etc/inittab.sysv $RPM_BUILD_ROOT/etc/inittab
 rm -rf $RPM_BUILD_ROOT/etc/event.d
%endif
rm -f $RPM_BUILD_ROOT/etc/inittab.*

%ifnarch s390 s390x
rm -f \
 $RPM_BUILD_ROOT/etc/sysconfig/network-scripts/ifup-ctc \
 $RPM_BUILD_ROOT/etc/sysconfig/network-scripts/ifup-iucv \
 $RPM_BUILD_ROOT/lib/udev/rules.d/55-ccw.rules \
 $RPM_BUILD_ROOT/lib/udev/ccw_init
%else
rm -f \
 $RPM_BUILD_ROOT/etc/rc.d/rc.sysinit.s390init \
 $RPM_BUILD_ROOT/etc/sysconfig/init.s390
%endif

# remove unused hotplug helper and ipsec/isdn stuff
rm -f $RPM_BUILD_ROOT/etc/sysconfig/network-scripts/{ifdown-ippp,ifup-ippp,ifdown-ipsec,ifup-ipsec,net.hotplug}

# we use network rules from the udev package
rm -f $RPM_BUILD_ROOT/lib/udev/rules.d/60-net.rules

# we have our own copy of gprintify
export DONT_GPRINTIFY=1

%post
##Fixme
touch /etc/sysconfig/i18n
##
touch /var/log/wtmp /var/run/utmp /var/log/btmp
chown root:utmp /var/log/wtmp /var/run/utmp /var/log/btmp
chmod 664 /var/log/wtmp /var/run/utmp
chmod 600 /var/log/btmp

%_mypost_service partmon

%_mypost_service network

%_mypost_service network-up

%_mypost_service dm

%_mypost_service netconsole

%_mypost_service netfs

# /etc/sysconfig/desktop format has changed
if [ -r /etc/sysconfig/desktop ]; then
    if ! grep -q = /etc/sysconfig/desktop; then
        DESK=`cat /etc/sysconfig/desktop`
        echo "DESKTOP=$DESK" > /etc/sysconfig/desktop
    fi
fi

# Add right translation file
for i in `echo $LANGUAGE:$LC_ALL:$LC_COLLATE:$LANG:C | tr ':' ' '`
do
	if [ -r %{_datadir}/locale/$i/LC_MESSAGES/initscripts.mo ]; then
		mkdir -p /etc/locale/$i/LC_MESSAGES/
		cp %{_datadir}/locale/$i/LC_MESSAGES/initscripts.mo \
			/etc/locale/$i/LC_MESSAGES/
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

%define initlvl_chg() if [[ -f /etc/rc3.d/S%{2}%{1} ]] && [[ -f /etc/rc5.d/S%{2}%{1} ]] && egrep -q 'chkconfig: [0-9]+ %{3}' /etc/init.d/%{1}; then chkconfig --add %{1} || : ; fi; \
%{nil}

# only needed on upgrade
if [ $1 != 0 ]; then
	# handle the switch to an independant prefdm initscript
	if grep -q '^x:5' /etc/inittab; then
		rm -f /etc/inittab.new
		sed 's/x:5/#x:5/' < /etc/inittab > /etc/inittab.new
		mv -f /etc/inittab.new /etc/inittab
		chkconfig --add dm || :
	fi

	# handle single user mode declaration
	if ! grep -q '..:S:' /etc/inittab; then
		cat >> /etc/inittab <<EOF

# Single user mode
~~:S:wait:/bin/sh
EOF
	fi
	
	# Handle boot sequence changes on upgrade
	%initlvl_chg partmon 80 13
	
fi

%preun
%_preun_service netfs

%_preun_service netconsole

%_preun_service dm

%_preun_service network-up

%_preun_service network

%_preun_service partmon

%triggerpostun -- initscripts <= 4.72

. /etc/sysconfig/init
. /etc/sysconfig/network

# These are the non-default settings. By putting them at the end
# of the /etc/sysctl.conf file, it will override the default
# settings earlier in the file.

if [ -n "$FORWARD_IPV4" -a "$FORWARD_IPV4" != "no" -a "$FORWARD_IPV4" != "false" ]; then
	echo "# added by initscripts install on `date`" >> /etc/sysctl.conf
	echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
fi

newnet=`mktemp /etc/sysconfig/network.XXXXXX`
if [ -n "$newnet" ]; then
  sed "s|FORWARD_IPV4.*|# FORWARD_IPV4 removed; see /etc/sysctl.conf|g" \
   /etc/sysconfig/network > $newnet
  sed "s|DEFRAG_IPV4.*|# DEFRAG_IPV4 removed; obsolete in 2.4. kernel|g" \
   $newnet > /etc/sysconfig/network
  rm -f $newnet
fi

if [ -n "$MAGIC_SYSRQ" -a "$MAGIC_SYSRQ" != "no" ]; then
	echo "# added by initscripts install on `date`" >> /etc/sysctl.conf
	echo "kernel.sysrq = 1" >> /etc/sysctl.conf
fi
if uname -m | grep -q sparc ; then
   if [ -n "$STOP_A" -a "$STOP_A" != "no" ]; then
	echo "# added by initscripts install on `date`" >> /etc/sysctl.conf
	echo "kernel.stop-a = 1" >> /etc/sysctl.conf
   fi
fi

%triggerun -- initscripts < 7.62
/sbin/chkconfig --del random
/sbin/chkconfig --del rawdevices
exit 0

%triggerpostun -- initscripts <= 8.38-2mdv2007.0
/sbin/chkconfig --add network-up
exit 0

%triggerpostun -- initscripts < 8.54-4mdv2008.0
echo "disabling supermount which is not supported anymore"
/usr/sbin/supermount -i disable
exit 0

%triggerpostun -- initscripts < 8.88-5mdv2008.0
/sbin/chkconfig --level 7 dm reset

%postun
if [ -f /var/lock/TMP_1ST ];then 
		rm -f /var/lock/TMP_1ST
fi
if [ "$1" = "0" ]; then
	for i in /etc/locale/*/LC_MESSAGES/initscripts.mo
	do
		rm -f $i
		rmdir `dirname $i` >/dev/null 2> /dev/null
	done
	rmdir /etc/locale/* >/dev/null 2> /dev/null
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root)
%dir /etc/sysconfig/network-scripts
%dir /etc/sysconfig/network-scripts/ifup.d
%dir /etc/sysconfig/network-scripts/ifdown.d
%dir /etc/sysconfig/network-scripts/wireless.d
%dir /etc/sysconfig/network-scripts/vpn.d
%dir /etc/sysconfig/network-scripts/vpn.d/openvpn
%dir /etc/sysconfig/network-scripts/vpn.d/pptp
%dir /etc/sysconfig/network-scripts/vpn.d/vpnc
%config(noreplace) %verify(not md5 mtime size) /etc/adjtime
%config(noreplace) /etc/sysconfig/init
%config(noreplace) /etc/sysconfig/autofsck
%config(noreplace) /etc/sysconfig/partmon
%config(noreplace) /etc/sysconfig/netconsole
%config(noreplace) /etc/sysconfig/readonly-root
%config(noreplace) /etc/sysconfig/speedboot
/etc/sysconfig/network-scripts/ifdown
/sbin/ifdown
/etc/sysconfig/network-scripts/ifdown-post
/etc/sysconfig/network-scripts/ifup
/sbin/ifup
%dir /etc/sysconfig
%dir /etc/sysconfig/console
%dir /etc/sysconfig/console/consoletrans
%dir /etc/sysconfig/console/consolefonts
%dir /etc/sysconfig/modules
%dir /etc/sysconfig/networking
%dir /etc/sysconfig/networking/devices
%dir /etc/sysconfig/networking/profiles
%dir /etc/sysconfig/networking/profiles/default
%config(noreplace) /etc/sysconfig/network-scripts/network-functions
%config(noreplace) /etc/sysconfig/network-scripts/network-functions-ipv6
/etc/sysconfig/network-scripts/init.ipv6-global
%config(noreplace) /etc/sysconfig/network-scripts/ifcfg-lo
/etc/sysconfig/network-scripts/ifup-ipx
/etc/sysconfig/network-scripts/ifup-post
/etc/sysconfig/network-scripts/ifdown-ppp
/etc/sysconfig/network-scripts/ifup-ppp
/etc/sysconfig/network-scripts/ifup-routes
/etc/sysconfig/network-scripts/ifdown-routes
/etc/sysconfig/network-scripts/ifup-plip
/etc/sysconfig/network-scripts/ifup-plusb
/etc/sysconfig/network-scripts/ifup-bnep
/etc/sysconfig/network-scripts/ifdown-bnep
/etc/sysconfig/network-scripts/ifup-eth
/etc/sysconfig/network-scripts/ifdown-eth
/etc/sysconfig/network-scripts/ifup-ipv6
/etc/sysconfig/network-scripts/ifdown-ipv6
/etc/sysconfig/network-scripts/ifup-sit
/etc/sysconfig/network-scripts/ifdown-sit
/etc/sysconfig/network-scripts/ifup-tunnel
/etc/sysconfig/network-scripts/ifdown-tunnel
/etc/sysconfig/network-scripts/ifup-aliases
#/etc/sysconfig/network-scripts/ifup-ippp
#/etc/sysconfig/network-scripts/ifdown-ippp
/etc/sysconfig/network-scripts/ifup-wireless
/etc/sysconfig/network-scripts/ifup-hso
/etc/sysconfig/network-scripts/ifdown-hso
/etc/X11/prefdm
/etc/X11/lookupdm
%dir /etc/X11/xsetup.d
/etc/X11/xsetup.d/90speedboot.xsetup
%config(noreplace) /etc/networks 
/etc/rwtab
%dir /etc/rwtab.d
/etc/statetab
%dir /etc/statetab.d
%if %{with_upstart}
%config(noreplace) /etc/event.d/*
%endif
/lib/udev/rules.d/*
%config(noreplace) /etc/inittab
%config(noreplace missingok) /etc/rc.d/rc[0-9].d/*
/etc/rc[0-9].d
/etc/rcS.d
/etc/rc
%dir /etc/rc.d/init.d
%config(noreplace) /etc/rc.local
/etc/rc.sysinit
/lib/lsb/init-functions
/etc/rc.d/init.d/*
/etc/rc.d/rc
%config(noreplace) /etc/rc.d/rc.local
/etc/rc.d/rc.sysinit
%config(noreplace) /etc/sysctl.conf
%exclude /etc/profile.d/debug*
%config /etc/profile.d/*
%dir /etc/sysconfig/network-scripts/cellular.d
%dir /etc/sysconfig/network-scripts/hostname.d
/etc/sysconfig/network-scripts/ifup.d/vpn
/etc/sysconfig/network-scripts/ifdown.d/vpn
/usr/sbin/vpn-start
/usr/sbin/vpn-stop
/usr/sbin/mdv-network-event
/usr/sbin/sys-unconfig
/bin/doexec
/bin/ipcalc
/bin/usleep
%attr(4755,root,root) /usr/sbin/usernetctl
/sbin/consoletype
/sbin/fstab-decode
/sbin/genhostid
/sbin/getkey
/sbin/securetty
%attr(2755,root,root) /sbin/netreport
/sbin/initlog
/lib/udev/rename_device
/lib/udev/console_init
/lib/udev/console_check
%ifarch s390 s390x
/lib/udev/ccw_init
%endif
/sbin/service
#mdv
/sbin/hibernate-cleanup.sh
/sbin/ppp-watch
%{_mandir}/man*/*
%lang(cs)	%{_mandir}/cs/man*/*
%lang(et)	%{_mandir}/et/man*/*
%lang(fi)	%{_mandir}/fi/man*/*
%lang(fr)	%{_mandir}/fr/man*/*
%lang(it)	%{_mandir}/it/man*/*
%lang(pt_BR)	%{_mandir}/pt_BR/man*/*
%lang(ru)	%{_mandir}/ru/man*/*
%lang(uk)	%{_mandir}/uk/man*/*
%dir %attr(775,root,root) /var/run/netreport
%dir /etc/ppp
%dir /etc/ppp/ip-down.d
%dir /etc/ppp/ip-up.d
%dir /etc/ppp/peers
/etc/ppp/ip-up
/etc/ppp/ip-down
/etc/ppp/ip-up.ipv6to4
/etc/ppp/ip-down.ipv6to4
/etc/ppp/ipv6-up
/etc/ppp/ipv6-down
%config(noreplace) /etc/initlog.conf
%dir /etc/NetworkManager
%dir /etc/NetworkManager/dispatcher.d
/etc/NetworkManager/dispatcher.d/00-netreport
/etc/NetworkManager/dispatcher.d/05-netfs
%doc sysconfig.txt sysvinitfiles mandriva/ChangeLog.gz ChangeLog-RH.gz static-routes-ipv6 ipv6-tunnel.howto ipv6-6to4.howto changes.ipv6 README-event.d
/var/lib/stateless
%dir /var/lib/speedboot
%ghost %attr(0664,root,utmp) /var/log/btmp
%ghost %attr(0664,root,utmp) /var/log/wtmp
%ghost %attr(0664,root,utmp) /var/run/utmp
%config(noreplace) /etc/modules
/etc/rc.modules
%dir /etc/modprobe.preload.d/
%ifnarch %{sunsparc}
/usr/sbin/supermount
%endif
/usr/bin/*
# warly
# gettext need /use/share/locale anyway
#%dir /etc/locale
#%dir /etc/locale/*
#%dir /etc/locale/*/LC_MESSAGES

%files -n debugmode
%config(noreplace) /etc/sysconfig/debug
%config /etc/profile.d/debug*
