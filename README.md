# Startup Tycoon

## Setup

0. If you're running Windows, install [Cygwin](http://cygwin.com/install.html). As a part of the installation, select `git` and `python` as packages to install. Boot Cygwin and proceed to 1. If you're not on Windows, open a terminal.

1. Follow these instructions:

```
sudo pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Getting started

To run your algorithm quickly with no visuals, do

```
./run.sh shell
```

To step through your algorithm and see it work, do

```
./run.sh web
```

Then visit [http://localhost:5000](http://localhost:5000) in your browser.