# Startup Tycoon

## Setup

1. If you're running Windows, install [Cygwin](http://cygwin.com/install.html). As a part of the installation, select `git` and `python` as packages to install. Boot Cygwin and proceed to step 2. If you're not on Windows, open a terminal.

2. Install [pip](http://pip.readthedocs.org/en/stable/installing/) if you do not already have it.

3. Follow these instructions:

```
sudo pip install virtualenv
git clone git@github.com:willcrichton/awap-2015.git
cd awap-2015
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Exploring the code

You should look at the following files:

* `src/game/player.py` - You will implement your algorithm here.
* `src/game/base_player.py` - Utilities for the Player class.
* `src/game/state.py` - All the state maintained for the game.
* `src/game/order.py` - Representation of orders in the game.
* `src/game/settings.py` - Constants used in the game.
* `src/game/graphs.py` - Functions for generating graphs.

You don't need to look at any other files.

The graphs used in the code are NetworkX graphs. Some useful links:
* [Short tutorial](http://networkx.lanl.gov/networkx_tutorial.pdf)
* [Full documentation](https://networkx.github.io/documentation/latest/)

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

## Submitting for the competition

To submit your algorithm for scoring, go to Autolab: [https://autolab.cs.cmu.edu/courses/15097-f15/assessments/awapcompetition](https://autolab.cs.cmu.edu/courses/15097-f15/assessments/awapcompetition)

Then click "Submit File" and upload `src/game/player.py`. Do not upload anything else (e.g. a zip/tar file, a different Python file, etc.). Your Autolab submission history will now have a new entry. If your score is -1, then your code did not compile or run correctly. Click on your score to see the error logs. Note that **you can only import from src/game/ or the Python 2.7 standard library**. You cannot use any custom packages besides networkx.

Submissions are closed at 7:00pm. Please submit your final bot early (like 6pm) to ensure that it works on our servers--the queue times will grow as we get close to 7:00pm.
