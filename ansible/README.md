# Ansible Configuration for OpenRailwayMap Server

## Requirements

In order to run the Ansible playbook, you have to install Python on the server using `apt install
python3`.

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

This repository contains an inventory file called `hosts`. Add your host to the the hosts file
in order to install the services on it.

By default, the following components will be installed on a host provided in the hosts file:

* tileserver
* website and API

The following playbooks are optional:

* blog (the OpenRailwayMap blog)
* mail (Postfix and Mailman 3, you very likely do not need this)
* backup_access (not recommended for use because it prepares the server for access by Nakaner's
  backup machine)
* munin_node (not recommened for use because it sends data to Nakaner's personal Munin master)

All other services (Blog, Mailman, Munin etc.) are installed only if you add the hostname to the
specific group.

Run a whole Playbook:

```sh
ansible-playbook -l THE_HOSTNAME -v site.yml
```

Add `--check` for a dry run. Add `--diff` to display the changes to text files. Add
`--private-key ~/.ssh/id_rsa` if Ansible does not find your private SSH key.


## OSM Import

OSM raw data import takes some time (downloading the planet dump and importing it into the database).
If you run Ansible for the first time, the download and import will be started. Tasks depending on a
finished import are left out. Please run the playbook a second time when the import is complete.
The playbook makes use of [Systemd's transient units](https://www.freedesktop.org/software/systemd/man/systemd-run.html)
and therefore is idempotent. This means, you can run the playbook multiple times on the same host.


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
git clone --branch openrailwaymap/0.40.0+ds-3 https://github.com/Nakaner/django-allauth-debian.git
cd django-allauth-debian
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone --branch openrailwaymap/0+20180916-11 https://github.com/Nakaner/mailman-suite.git
cd mailman-suite
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone --branch openrailwaymap/1.3.0-4 https://github.com/Nakaner/django_mailman3-debian.git
cd django_mailman3-debian
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone --branch openrailwaymap/1.2.2-2 https://github.com/Nakaner/hyperkitty-debian.git
cd hyperkitty-debian
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone --branch openrailwaymap/1.2.4-2 https://github.com/Nakaner/postorius-debian.git
cd postorius-debian
dpkg-buildpackage -us -uc -b -rfakeroot
cd ..
git clone --branch openrailwaymap/3.2.1-3 https://github.com/Nakaner/mailman3-debian.git
cd mailman3-debian
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
