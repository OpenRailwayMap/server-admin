# Ansible Configuration for OpenRailwayMap Server

## Requirements

In order to run the Ansible playbook, you have to install Python on the server using `apt install python`.

On client side, install Ansible from your package manager or Pip (or Pip in a Virtualenv).

Debian/Ubuntu (root permissions required): `apt install ansible`

Pip: `pip3 install --user ansible`

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

This repository contains an inventory file called `hosts.yml`. You have to append `-i hosts.yml` to all Ansible commands to make Ansible use this inventory instead of `/etc/ansible/hosts`.

Run a whole Playbook:

```sh
ansible-playbook -i hosts.yml -v roles/base/tasks/main.yml
```

Add `--check` for a dry run.


## Notes about Tileserver Setup

Not all steps are full automatised. You have to do the following steps yourself:

* Initially download the planetdump
* Build Debian packages for Tirex and mod_tile. They are not available in Apt. Build them in your home directory on the server. The Ansible playbook will finally install them. See below for build instructions.
* The Mapnik XML file is not build by Ansible. Build it on your computer or in your home directory on the server.

### Build mod_tile

```sh
git clone https://github.com/openstreetmap/mod_tile.git
cd mod_tile
sudo apt install build-essential autoconf apache2-dev libmapnik-dev mapnik-utils
dpkg-checkbuilddeps
dpkg-buildpackage -rfakeroot -b -uc
```

This will result in a mod_tile and a rendered .deb package in the parent directory. We only need the mod_tile package. Copy it to `/root/packages`:

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


## License

The Ansible Playbooks are licensed under the terms of the MIT License. See the COPYING file for details.
