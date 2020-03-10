SpotPRIS2
=========

Control Spotify Connect devices using MPRIS2

****

This software provides an MPRIS2 interface for Spotify Connect. It is more complete than the MPRIS2 interface built into
the Spotify Linux client.  
In addition it can be used to control remote Spotify Connect devices (Like spotifyd running on a Raspberry Pi) from your
PC.

This software is still in development. Some things might not work as expected.

Installation
------------
* Arch Linux: Install from AUR  
    ```yay -S python-spotpris2```
* Other distributions: Install using pip  
    ```pip install spotPRIS2```

Then just run `spotpris2`.

Options
-------
```
  -h, --help            show this help message and exit
  -d DEVICE [DEVICE ...], --devices DEVICE [DEVICE ...]
                        Only create interfaces for the listed devices
  -i DEVICE [DEVICE ...], --ignore DEVICE [DEVICE ...]
                        Ignore the listed devices
  -a, --auto            Automatically control the active device
  -l [{name,id}], --list [{name,id}]
                        List available devices and exit
```

In normal mode SpotPRIS2 creates one MPRIS2 interface for each Spotify Connect device connected to your account.

You can use `--devices` to only create interfaces for specified devices or `--ignore` to create interfaces for all but
the specified devices. Devices can be specified either by their name or their ID.  
With `--auto` only one interface gets created. It will always control the currently active device.

`--list` lists the names of all available devices. Use `--list=id` to list their IDs instead.

Known problems
--------------
1. **Podcasts, Radios, etc. aren't supported**  
    This is a limitation of the Spotify Web API. There's currently nothing I can do about it.
2. **The MPRIS2 interface only shows up when something is playing**  
    If you are running SpotPRIS2 in auto mode this is intended. There is no way for SpotPRIS2 to know which device you
    want to control, so we don't offer any interface. You can use normal mode if you want to be able to start playback
    using MPRIS2.

Systemd
--------
To use SpotPRIS2 with systemd, the provided unit file (`contrib/spotpris2.service`) should be copied into `/usr/lib/systemd/user`.

****

This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Spotify AB,
or any of its subsidiaries or its affiliates.


