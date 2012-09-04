rcon-tool
=========

rcon-tool is an open-source tool written in Python and GTK+ for managing SRCDS servers on linux. Uses modified SourceLib library.

![Screenshot of rcon-tool](/gavintlgold/rcon-tool/raw/master/interface.png)

Ignore the ping, an annoying housemate was stealing my webs.

Features
--------

rcon-tool is an unstable, but semi-working tool along the lines of HLSW. Since HLSW is not an open source program (despite being freeware), I decided to create my own tool so that I could administrate my TF2 servers at [The Crit Sandvich Network](http://critsandvich.com) without needing to use windows.

First of all, rcon-tool allows you to track multiple servers' status (number of players, current map, hostname, ping). It has a ping graph for easy visualization of the health of your servers.

rcon-tool also has support for sending rcon commands and receiving a response from the server. In order to enable this feature, you must enter your server's rcon password in the indicated field. You can then type a command in the "console" tab.

Finally, rcon-tool has support for receiving the udp log stream from SRCDS servers. This will allow you to see what's going on in your server (what players are saying, who's connecting, who's killing who, etc).

Known Bugs/Problems/Feature improvements
-------------------

Before you start complaining about something, please see the Issues tab. rcon-tool is in development, so many interface elements may not be implemented yet (for example, the 'player list' section does not list players yet, so ignore it)


Installation
------------

There is no simple way to install rcon-tool yet. This will change very soon! I also have not tested rcon-tool on anything except Ubuntu 12.04. I'd love to hear how it works on other distributions and versions, by the way.

For now, I'll provide instructions on how to run this on the latest distribution of Ubuntu in the hope that this will be helpful to someone. I might be forgetting a step or a requirement, just let me know.

- Prerequisites that probably don't come with Ubuntu
    - python-twisted
- clone the latest version on git
- make sure main.py is executable
    -    chmod u+x main.py
- double-clicking on the .desktop file should work
- alternatively, open a terminal. This will help catch bugs and exceptions due to my sloppy coding.
    -    cd path/to/rcontool/
    -    ./main.py

New Bugs
----

Let me know if you find a bug or want a feature. Use the 'Issues' tab in github, please. rcon-tool has not been extensively tested, and hasn't been tested on anything but tf2 servers! rcon-tool has not been officially 'released' yet, so don't expect to get a bugfix very quickly. And remember that rcon-tool does not have a warranty, so I'm not responsible for any problems or bugs!

Nevertheless, I hope that rcon-tool will be useful as it becomes more stable.
