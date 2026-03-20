"""Runtime setup for Skyfield ephemeris cache directories (legacy setuptools post-install hook)."""

from __future__ import annotations

import os
import sys


def _import_skyfield():
    import skyfield

    return skyfield


def ensure_skyfield_bsp_files() -> None:
    """Create skyfield ``bsp_files`` directory if missing."""
    try:
        skyfield = _import_skyfield()

        bsp_directory = os.path.join(skyfield.__path__[0], "bsp_files")
        if not os.path.exists(bsp_directory):
            os.mkdir(bsp_directory)
            os.chmod(bsp_directory, 0o777)
    except ModuleNotFoundError:
        site_package_dir = os.path.join(
            sys.prefix,
            "lib",
            "python{}.{}".format(sys.version_info.major, sys.version_info.minor),
            "site-packages",
        )
        egg_ext = "-py{}.{}.egg".format(sys.version_info.major, sys.version_info.minor)
        try:
            dir_names = os.listdir(site_package_dir)
        except OSError:
            # Missing/broken prefix layout (e.g. site-packages path absent) — same as "no egg found".
            dir_names = []
        for d in dir_names:
            if d.startswith("skyfield") and d.endswith(egg_ext):
                path = os.path.join(site_package_dir, d, "skyfield", "bsp_files")
                os.mkdir(path)
                os.chmod(path, 0o777)
                break
        else:
            print(
                "Unable to create bsp_files directory for skyfield module. "
                "Please create it manually with user & group write permissions"
            )