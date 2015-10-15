# Startup Tycoon

## Setup

0. If you're running Windows, install [Cygwin](http://cygwin.com/install.html). As a part of the installation, select `git` and `python` as packages to install. Boot Cygwin and proceed to 1. If you're not on Windows, open a terminal.

1. Install [pip](http://pip.readthedocs.org/en/stable/installing/) if you do not already have it.

2. Follow these instructions:

```
sudo pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Exploring the code

You should look at the following files:

* `src/game/player.py` - You will implement your algorithm here.
* `src/game/state.py` - All the state maintained for the game.
* `src/game/order.py` - Representation of orders in the game.
* `src/game/settings.py` - Constants and graphs used in the game.

The graphs used in the code are NetworkX graphs. Some useful links:
* [Documentation](https://networkx.github.io/documentation/latest/)
* [Short tutorial](http://networkx.lanl.gov/networkx_tutorial.pdf)

You don't need to look at any other files.

## Running the code

To run your algorithm quickly with no visuals, do

```
./run.sh shell
```

To step through your algorithm and see it work, do

```
./run.sh web
```

Then visit [http://localhost:5000](http://localhost:5000) in your browser.
