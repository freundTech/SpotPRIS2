SpotPRIS2
=========

Control Spotify Connect devices using MPRIS2

****

This software provides an MPRIS2 interface for Spotify Connect. It is more complete than the MPRIS2 interface built into the Spotify Linux client.  
In addition it can be used to control remote Spotify Connect devices (Like spotifyd running on a Raspberry Pi) from your PC.

This software is still in development. While most features are implemented there are still some null checks missing, so doing something unexpected (like listening to a podcast on Spotify) can break this software :wink:

You can install it using pip:
```pip install spotPRIS2```

Known problems
--------------
1. **Podcasts, Radios, etc. aren't supported.**  
   This is a limitation of the Spotify Web API. There's currently nothing I can do about it.

2. **SpotPRIS2 breaks after some time, because the token expires**  
   I'm working on it.

****

This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Spotify AB, or any of its subsidiaries or its affiliates.

