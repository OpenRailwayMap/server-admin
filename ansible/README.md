# Ansible Configuration for OpenRailwayMap Server

## Requirements

In order to run the Ansible playbook, you have to install Python on the server using `apt install
python`.

On client side, install Ansible from your package manager or Pip (or Pip in a Virtualenv):

* Debian/Ubuntu (root permissions required): `apt install ansible`
* Pip: `pip3 install --user ansible`

Virtualenv:

```sh
# Create Virtualenv
virtualenv --python python3 venv
# Change a couple of environment variables (e.g. Python path, Python packages location)
source venv/bin/activate
pip install ansible
```

You can leave the virtualenv using `deactivate`.



## Calling Ansible

This repository contains an inventory file called `hosts.yml`. You have to append `-i hosts.yml` to
all Ansible commands to make Ansible use this inventory instead of `/etc/ansible/hosts`.

Run a whole Playbook:

```sh
ansible-playbook -i hosts.yml -v roles/base/tasks/main.yml
```

Add `--check` for a dry run. Add `--private-key ~/.ssh/id_rsa` if Ansible does not find your private
SSH key.


## Order of the Playbooks of the Tileserver Setup

Not all steps are full automatised. You have to do the following steps yourself:

* Initially download of the planet dump and initial Osm2pgsql data import. This is done by the Bash
  script [import.sh](../scripts/import.sh) which should be executed as user `osmimport`.
* Build Debian packages for Tirex and mod_tile. They are not available in Apt. Build them in your
  home directory on the server. The Ansible playbook will finally install them. See below for build
  instructions.
* The Mapnik XML file is not build by Ansible. Build it on your computer or in your home directory
  on the server.

Building the dependencies and the Mapnik XML files is explained below.

The general order of the playbooks is:

* base
* security
* tileserver
* Run the data import manually: `sudo -u osmimport import.sh`*
* tileserver_step2
* Start bulk rendering of tiles on zoom levels 0 to 12 manually using
  `tirex-batch --prio 15 map=standard,maxspeed,signals z=0-12 bbox=-180,-80,180,80`
* website

## Building Packages

The tile server setup requires a couple of Debian packages which are not available in the Debian repositories.
You have to build them yourself.

The Mailman 3 setup works with the packages from Debian repositories but lists.openrailwaymap.org
runs with self-built packages of Mailman 3.2.1-3 which include a couple of patches fixing encoding
and programming bugs. The Git repository with these packages is available
[here](https://github.com/fossgis/mailman3-debian). See the
[changelog](https://github.com/fossgis/mailman3-debian/blob/debian-3.2.1-3/debian/changelog) for
details.

### Build mod_tile

```sh
git clone https://github.com/openstreetmap/mod_tile.git
cd mod_tile
sudo apt install build-essential autoconf apache2-dev libmapnik-dev mapnik-utils
dpkg-checkbuilddeps
dpkg-buildpackage -rfakeroot -b -uc
```

This will result in a mod_tile and a rendered .deb package in the parent directory. We only need the
mod_tile package. Copy it to `/root/packages`:

```sh
sudo cp libapache2-mod-tile_*.deb /root/packages
```


### Build Tirex

```sh
git clone https://github.com/OpenStreetMap/tirex.git
cd tirex
git checkout tags/v0.6.1
dpkg-checkbuilddeps
dpkg-buildpackage -rfakeroot -b -uc
```

You will now have a couple of Tirex .deb packages in the parent directory. Copy them (except the debug symbols packages to `/root/packages`):

```sh
sudo cp tirex-backend-mapnik_*.deb tirex-core_*.deb /root/packages
```


### Build Mapfiles

Install Carto either using `npm install carto` or from your system's package manager if available.
Transpiling the map styles from CartoCSS to Mapnik XML does not require database access. Ansible
expects the XML files at /root/packages.

```sh
git clone https://github.com/OpenRailwayMap/OpenRailwayMap-CartoCSS
cd OpenRailwayMap-CartoCSS
carto project.mm > project.xml
carto maxspeed.mm > maxspeed.xml
carto signals.mm > signals.xml
cp project.xml maxspeed.xml signals.xml /root/packages`
```

### Build Mailman 3

Our setup of Mailman 3 includes a couple of patches to comply with German
law, protect users' privacy and bug fixes w.r.t. handling non-ASCII
characters. This includes customizable links for imprint and privacy
policy, a disabled Gravatar support. In addition, the signup form has got
a captcha to prevent subscription spam which harms the reputation of our
mail server.

Therefore, you have to build some Mailman 3 packages yourself:

```sh
sudo apt build-dep mailman3 mailman3-full
git clone https://github.com/fossgis/mailman3-debian.git
cd mailman3-debian
git checkout tags/openrailwaymap/3.2.1-3
dpkg-buildpackage -us -uc -b
for PKG_NAME in django-allauth-debian mailman-suite django_mailman3-debian hyperkitty-debian postorius-debian mailman3-debian ; do
git clone https://github.com/Nakaner/django-allauth-debian.git
cd django-allauth-debian
git checkout tags/openrailwaymap/0.40.0+ds-3
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone https://github.com/Nakaner/mailman-suite.git
cd mailman-suite
git checkout tags/openrailwaymap/0+20180916-11
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone https://github.com/Nakaner/django_mailman3-debian.git
cd django_mailman3-debian
git checkout tags/openrailwaymap/1.3.0-4
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone https://github.com/Nakaner/hyperkitty-debian.git
cd hyperkitty-debian
git checkout tags/openrailwaymap/1.2.2-2
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone https://github.com/Nakaner/postorius-debian.git
cd postorius-debian
git checkout tags/openrailwaymap/1.2.4-2
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone https://github.com/Nakaner/mailman3-debian.git
cd mailman3-debian
git checkout tags/openrailwaymap/3.2.1-3
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
```

You will find the built packages in the parent directory. Copy them to `/root/packages`.

## Porting to other Linux distributions

If you consider porting this to other Linux distributions, you might have to change the following things:

* Replace `apache` by `httpd` in a couple of paths and change the location of the Apache configuration files for VirtualHosts.
* Replace the default location of the document roots (defaults to `/var/www/*` in Debian but other distributions use other paths, e.g. `/srv/http/` on Arch Linux)
* Change the PostgreSQL version
* Mailman setup is heavily customized to Debian. This Ansible role is only helpful as a rough guide or for Debian-like distributions.

## License

The Ansible Playbooks are licensed under the terms of the MIT License. See the COPYING file for details.
