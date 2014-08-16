To use, please alter the constants in the file for the number of teams (numPlayers)
and the number of total matches wanted (numGames). Please do not try to schedule more than
floor((n^2 - n)/15) matches unless you plan on letting it run for a REALLY
long time.

As this is a bruteforce algorithm with a random starting point, sometimes
it is possible you picked a bad starting point. At the moment, it should take
no longer than 40 seconds to run for teams < 50 and the amount of matches
specified above. I recommend restarting it if it doesn't seem to be getting anywhere

It will output the matches in a file in lines of the form 

(#, #, #, #) 

where the the numbers are player numbers and those 4 people are a match. 