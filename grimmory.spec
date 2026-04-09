Name:           grimmory
Version:        2.3.0
Release:        1%{?dist}
Summary:        Self-Hosted Ebook Library Manager

License:        AGPL-3.0-only
URL:            https://opencollective.com/grimmory
Source0:        https://github.com/grimmory-tools/%{name}/archive/refs/tags/v%{version}/%{name}-v%{version}.tar.gz
Source1:        grimmory.service
Source2:        grimmory.sysusers
Source3:        grimmory.tmpfiles
Source4:        grimmory.conf

BuildRequires:  java-25-openjdk-devel
%if 0%{?fedora} >= 44
BuildRequires:  nodejs, /usr/bin/node, /usr/bin/npm
%else
BuildRequires:  nodejs20
BuildRequires:  nodejs-npm
%endif
BuildRequires:  systemd-units
BuildRequires:  systemd-rpm-macros
%{?sysusers_requires_compat}

Requires:       java-headless >= 1:25
Requires:       mariadb-server
Requires:       fontconfig
Requires:       dejavu-sans-fonts
Requires:       systemd-units

Conflicts:      booklore

%description
Grimmory is a self-hosted application for managing your entire book collection in one place. Organize, read, annotate, sync across devices, and share without relying on third-party services.

%global debug_package %{nil}

%prep
%setup -q

%build
# Build web UI
cd booklore-ui
npm install
npm run build
cd ..

# Build server
cd booklore-api
sed -i 's|/app/data|/var/lib/grimmory/app/data|' src/main/resources/application.yaml
sed -i 's|/bookdrop|/var/lib/grimmory/bookdrop|' src/main/resources/application.yaml
sed -i 's|development|%{version}|' src/main/resources/application.yaml
sed -i 's|6060|8095|' src/main/resources/application.yaml
./gradlew build
cd ..

%install
install -d %{buildroot}%{_datadir}/webapps/%{name}
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_sysconfdir}/%{name}

mkdir -p %{buildroot}%{_sharedstatedir}/%{name}/app/data
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}/bookdrop

install -p -m 0644 booklore-api/build/libs/booklore-api-0.0.1-SNAPSHOT.jar %{buildroot}%{_datadir}/webapps/%{name}/%{name}.jar
install -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysusersdir}/%{name}.conf
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -p -m 0640 %{SOURCE4} %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf

%pre
%sysusers_create_compat %{SOURCE2}

%post
%systemd_post %{name}.service
mkdir /var/lib/grimmory
echo -e "\033[1;34mINFO\033[0m\033[1m: Final steps to have a working grimmory instance:"
echo -e "\033[1;34mINFO\033[0m\033[1m:     * initialise mariadb and create a database called 'booklore' (https://wiki.archlinux.org/title/MariaDB)\033[0m"
echo -e "\033[1;34mINFO\033[0m\033[1m:     * Update db info in /etc/grimmory\033[0m"
echo -e "\033[1;34mINFO\033[0m\033[1m:     * To run, systemctl start grimmory\033[0m"
echo -e "\033[1;34mINFO\033[0m\033[1m:     * To access, go to localhost:8095/\033[0m"

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%{_datadir}/webapps/%{name}/%{name}.jar
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%dir %attr(0755,grimmory,grimmory) %{_sharedstatedir}/%{name}

%changelog
