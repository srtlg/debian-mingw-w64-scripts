# MinGW-W64 Cross-Compile Scripts

Cross-compile programs for Windows with MinGW-W64 and [CMake](https://cmake.org/)
from [Debian GNU/Linux](https://www.debian.org/),
similar to the ones found in [AUR](https://aur.archlinux.org/packages?K=mingw-w64).

Maybe only useful for me, since [MXE](https://mxe.cc) failed to build more than once and here
one could easily use a debugger and IDE to understand what is going on.  This is
a fully static build, however the runtime seems to require ``libgcc_s_seh-1.dll``  and
``libwinpthread-1.dll``.

Potentially, this could also be used to build the projects natively with MS VS++
(which is where this type of build script came from).

Currently, it supports building

* ceres-solver
* basic Qt6 GUIs


## Usage

Create a container for systemd-nspawn (please be sure to review the scripts):

```bash
sudo sh -x debian-nspawn/*.sh
````

Then start the machine

```bash
sudo machinectl start debian-bullseye
```

and use it

```bash
machinectl shell $USER@debian-bullseye
```

The default is to use the current directory as staging area, e. g.

```bash
mkdir staging
( cd staging; python ~/nspawn/build-ava-ceres.py )
mkdir build-ava-ceres
( cd build-ava-ceres; x86_64-w64-mingw32-cmake ~/nspawn/ava-ceres; ninja )
```

If a particular build fails, you can single it out by running (``ceres-solver`` is
``NAME`` used in `mingw_scripts/ceres_solver.py`):

```bash
python ~/nspawn/build-ava-ceres.py ceres-solver -c
```

You'll find

* the sources in ``src/ceres-solver`` (and you can edit them and see what changes for the configuration)
* the CMake errors in ``build/ceres-solver/CMakeFiles/CMakeError.log``
* packages are installed into ``/usr/*-w64-mingw32`` and at least discovery for the cmake files works,
  however, some manual intervention for zlib was always necessary
