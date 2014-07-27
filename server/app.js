/////////////////////////////////////////////////////////////////////////
// SBR SERVER: Responsible for creating, managing, and verifying games //
/////////////////////////////////////////////////////////////////////////

/* GENERAL TODO: 
 *   - determine why players get skipped when NUM_BLOCKS = 1
 *   - give more informative errors when we get invalid moves
 *   - verify matchmaking + lobbying works on scale
 *   - allow multiple tests (bot_1, ...) at once
 *   - headless tests (don't see game, just get scores)
 *   - show spectator scores if they load page after game ends
 */

var nodestatic = require('node-static');
var express = require('express');
var fs = require('fs');
var path = require('path');
var childProcess = require('child_process');
var crypto = require('crypto');
var testing = true;

var TEAMS = {
    'will'  : 'Will Crichton',
    'test'  : 'Anonymous',
    'bot_1' : 'Bot 1',
    'bot_2' : 'Bot 2',
    'bot_3' : 'Bot 3',
    'p1'    : 'Bill',
    'p2'    : 'Bob',
    'p3'    : 'Joe',
    'p4'    : 'Ted'
};

var BLOCKS = [
    [[0, 0]], // single
    [[0, 0], [0, 1]], // double
    [[0, 0], [0, 1], [1, 0]], // elbow
    [[0, 0], [0, 1], [0, 2]], // tiny line
    [[0, 0], [0, 1], [1, 0], [1, 1]], // square
    [[0, 0], [1, 0], [2, 0], [1, 1]], // little T
    [[0, 0], [1, 0], [2, 0], [3, 0]], // little line
    [[0, 0], [0, 1], [1, 0], [0, 2]], // little L
    [[0, 0], [1, 0], [1, 1], [2, 1]], // tetris S
    [[0, 0], [1, 0], [2, 0], [3, 0], [0, 1]], // big L
    [[0, 0], [1, 0], [2, 0], [1, 1], [2, 1]], // big T
    [[0, 0], [1, 0], [2, 0], [0, 1], [0, 2]], // corner piece
    [[0, 0], [1, 0], [1, 1], [2, 1], [3, 1]], // elongated S
    [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]], // Z shape
    [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]], // big line
    [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2]], // chair
    [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]], // staircase
    [[0, 0], [1, 0], [0, 1], [0, 2], [1, 2]], // corner capper
    [[0, 0], [1, 0], [1, 1], [1, 2], [2, 1]], // weird dual-elbow
    [[0, 0], [-1, 0], [0, -1], [1, 0], [0, 1]], // plus sign
    [[0, 0], [1, 0], [2, 0], [3, 0], [1, 1]] // line with a tumor (http://goo.gl/1nz2zY)
];

var NUM_BLOCKS = 1; //BLOCKS.length;

var TURN_LENGTH = 5000;
var DELAY_BETWEEN_TURNS = 300;

//use express to protect admin page
var fileserver = new nodestatic.Server('./www', {cache: 600});
var server = express();
var auth = express.basicAuth('user', 'password12345'); // pro security
server.get('/admin*', auth, function(req, res) {
    req.addListener('end', function() {
        fileserver.serve(req, res);
    }).resume();
});

//catch all other requests with the static file server
server.get('/*', function(request, response) {
    request.addListener('end', function() {
        fileserver.serve(request, response);
    }).resume();
});

var ioServer = server.listen(8080);
var io = require('socket.io').listen(ioServer, {log: false});

var Player = function(socket) {
    this.socket = socket;
    this.id = socket.id;
    this.blocks = [];
    this.game = null;
    this.number = -1;
    this.canMove = false;
};

Player.prototype = {
    isInGame: function() {
        return this.game !== null;
    },

    quit: function(msg) {
        this.game = null;
    }
};

//Board is 2d array with -1 for no block and a players number for their block
var Board = function() {
    this.dimension = 20; //Square board is assumed 
    this.grid = []; 

    // populate the board with empty values
    for (var i = 0; i < this.dimension; i++) {
        this.grid[i] = [];
        for (var j = 0; j < this.dimension; j++) {
            this.grid[i][j] = -1;
        }
    }
};

Board.prototype = {
    canPlaceBlock: function(plNum, block, point) {
        var onAbsCorner = false, onRelCorner = false;
        var N = this.dimension - 1, corner;

        // Determine which corner is player's starting corner
        switch (plNum) {
        case 0: corner = {x: 0, y: 0}; break
        case 1: corner = {x: N, y: 0}; break
        case 2: corner = {x: N, y: N}; break
        case 3: corner = {x: 0, y: N}; break
        }

        for (var i = 0; i < block.length; i++) {
            var x = point.x + block[i].x, y = point.y + block[i].y;

            // TODO: informative errors
            // Check bounds and illegal plays
            if (x >= this.dimension || x < 0 ||
                y >= this.dimension || y < 0 ||
                this.grid[x][y] >= 0 ||
                (x > 0 && this.grid[x - 1][y] == plNum) || 
                (y > 0 && this.grid[x][y - 1] == plNum) ||
                (x < N && this.grid[x + 1][y] == plNum) ||
                (y < N && this.grid[x][y + 1] == plNum))
            {
                return false;
            }

            // Check to make sure piece is placed on starting or continuing corner
            onAbsCorner = onAbsCorner || (x === corner.x && y === corner.y);
            onRelCorner = onRelCorner ||
                (x > 0 && y > 0 && this.grid[x - 1][y - 1] == plNum) ||
                (x > 0 && y < N && this.grid[x - 1][y + 1] == plNum) ||
                (x < N && y > 0 && this.grid[x + 1][y - 1] == plNum) ||
                (x < N && y < N && this.grid[x + 1][y + 1] == plNum);
        }

        // ensure initial play is on the player's absolute corner of the board
        if (this.grid[corner.x][corner.y] < 0 && !onAbsCorner) return false;

        // ensure that placed block is on the corner of another block players owns
        if (!onAbsCorner && !onRelCorner) return false;
        
        return true;
    },
    
    placeBlock: function(plNum, block, point) {
        if (!this.canPlaceBlock(plNum, block, point)) {
            return false;
        }

        for (var i = 0; i < block.length; i++) {
            var x = point.x + block[i].x, y = point.y + block[i].y;
            this.grid[x][y] = plNum;
        }

        return true;
    }
}

var Game = function(players) {
    this.turn = 0;
    this.players = players;
    this.board = new Board();
    this.over = false;
    this.gameId = crypto.randomBytes(20).toString('hex');//unique ID

    // Generate a random list of Ids
    // TODO: This should be re-written to be O(n) (Fisher-Yates)
    var blockIds = [], blocks = [];
    for (var i = 0; i < NUM_BLOCKS; i++) {
        while (true) {
            var idx = Math.floor(Math.random() * BLOCKS.length);
            if (blockIds.indexOf(idx) < 0) {
                blockIds.push(idx);
                break;
            }
        }
    }

    // Convert array blocks to x,y blocks, then sort by the above permutation
    for (var i = 0; i < NUM_BLOCKS; i++) {
        var oldBlock = BLOCKS[blockIds[i]], newBlock = [];
        for (var j = 0; j < oldBlock.length; j++) {
            newBlock[j] = {x: oldBlock[j][0], y: oldBlock[j][1]}
        }
        blocks.push(newBlock);
    }

    // Give each player a copy of the blocks
    for (var i = 0; i < this.players.length; i++) {
        this.players[i].blocks = blocks.slice(0);
    }

    for (var i = 0; i < this.players.length; i++) {
        this.sendSetup(this.players[i]);
        this.players[i].canMove = true;
    }

    console.log("Made a new game with " + players.map(function(p){return TEAMS[p.teamId]}).join(", ") + ".");
};

Game.prototype = {
    // rotation is in range [0, 3]
    rotateBlock: function(oldBlock, rotation) {
        var newBlock = [];
        for (var i = 0; i < oldBlock.length; i++) {
            var cx = oldBlock[i].x, cy = oldBlock[i].y;
            switch (rotation) {
            case 1: newBlock[i] = {x: -cy, y: cx}; break
            case 2: newBlock[i] = {x: -cx, y: -cy}; break
            case 3: newBlock[i] = {x: cy, y: -cx}; break
            default: newBlock[i] = {x: cx, y: cy}; break
            }
        }
        return newBlock;
    },

    doMove: function(pl, move) {

        // TODO: informative errors
        // Check for invalid or out of turn moves.
        if (this.turn != pl.number ||
            move.block === undefined || move.pos === undefined || move.rotation === undefined ||
            move.pos.x === undefined || move.pos.y === undefined || move.block < 0 || 
            move.block >= pl.blocks.length || move.rotation < 0 || move.rotation > 3) 
        { 
            return false; 
        }

        // Properly rotate old block. (Maybe this should be a function)
        var newBlock = this.rotateBlock(pl.blocks[move.block], move.rotation);

        if (!this.board.placeBlock(pl.number, newBlock, move.pos)) return false;        
        pl.blocks.splice(move.block, 1);

        this.updateCanMove();
        if (this.checkIsOver()) {
            this.getRoom().emit('update', this.clientState());
            this.quit();
            return;
        }

        do {
            this.turn = (this.turn + 1) % this.players.length;   
        } while (!this.players[this.turn].canMove);

        this.getRoom().emit('update', this.clientState());
        this.sendMoveRequest();//Ask the next player for their move
        
        // Clear the last players timer and set the current players timer
        this.clearTimer();
        this.setTimer();

        return true;
    },

    getRoom: function() {
        return io.sockets.in(this.gameId);
    },

    quit: function() {
        if (this.over) return;
        this.over = true;

        var scores = this.players.map(this.getScore.bind(this));
        var to_print = []
        this.getRoom().emit('end', scores);
        this.players.forEach(function(player, idx) {
            to_print.push(player.teamId + ': ' + scores[idx])
            player.quit();
        });
        
        fs.appendFileSync('scores', to_print.join(', ') + "\n");
    },

    // starts a timer 3 second that will advance to the
    // next player if no move has been made before it is done
    setTimer: function() {
        this.moveTimer = setTimeout((function() {
            this.advance();
        }).bind(this), TURN_LENGTH);
    },

    // gets rid of the turn timeout timer
    clearTimer: function() {
        if(this.moveTimer !== undefined){
            clearTimeout(this.moveTimer);
        }
    },

    // Sends a request for a move to the current player
    sendMoveRequest: function(){
        currplayer = this.players[this.turn];
        setTimeout(function(){currplayer.socket.emit('moveRequest', {move: 1});}, DELAY_BETWEEN_TURNS);
    },

    // Skips the current player, and will stop advancing if all players skip.
    advance: function() {
        if (this.checkIsOver()) {
            this.quit();
        } else {
            do {
                this.turn = (this.turn + 1) % this.players.length;   
            } while (!this.players[this.turn].canMove)

            this.getRoom().emit('update', this.clientState());
            this.sendMoveRequest();
            this.clearTimer();
            this.setTimer();
        }
    },

    sanitize: function() {
        return {
            id: this.gameId,
            players: this.players.map(function(player) {
                return TEAMS[player.teamId];
            })
        }
    },

    clientState: function() {
        return {
            blocks: this.players.map(function(p){ return p.blocks; }),
            board: this.board,
            turn: this.turn
        }
    },

    sendSetup: function(player) {
        var number = this.players.indexOf(player);
        var state = this.clientState();
        state.number = number;

        player.game = this;
        player.number = number;
        player.socket.join(this.gameId);
        player.socket.emit('setup', state);
    },

    getScore: function(player) {
        // gets the number of squares on the board that belong to the player
        numSquares = this.board.grid.reduce(function(s1, xs) {
            return s1 + xs.reduce(function(s2, x) {
                if (x == player.number) {
                    return s2+1;
                } else{
                    return s2;
                };
            }, 0);
        }, 0);
        return numSquares;
    },

    checkIsOver: function() {
        return this.players.every(function(currPlayer) {
            return !currPlayer.canMove;
        });
    },

    updateCanMove: function() {
        this.players.forEach((function(player) {
            if (!player.canMove) return;
            var blocks = player.blocks;

            if (blocks.length == 0) {
                player.canMove = false;
                return;
            }
            
            for (var b = 0; b < blocks.length; b++) {
                for (var rot = 0; rot < 4; rot++) {
                    var block = this.rotateBlock(blocks[b], rot);
                    for (var i = 0; i < this.board.dimension; i++) {
                        for (var j = 0; j < this.board.dimension; j++) {
                            if (this.board.canPlaceBlock(player.number, blocks[b], {x: i, y: j})) {
                                player.canMove = true;
                                return;
                            }
                        }
                    }
                }
            }

            player.canMove = false;
        }).bind(this));
    }
};

// Returns first connected player that has a matching teamId
function getPlayerByTeam(teamId) {
    var sockets = io.sockets.clients();

    for (var i = 0; i < sockets.length; i++) {
        var player = sockets[i].player;
        if (player && player.teamId == teamId) return player;
    }

    return null;
}

function getUniqueTeamId (teamId) {
    newTeamId = String(teamId);
    i = 1;
    var teams = connectedPlayers.map(function(p) {return p.teamId; })

    while(teams.indexOf(newTeamId) != -1){
        newTeamId = newTeamId.replace(/_\d+/,"");
        newTeamId += ("_" + i);
        i++;
    }
    return newTeamId;
}

// Returns first (and hopefully only) game with matching gameId
function getGameById(gameId) {
    for (var i = 0; i < games.length; i++) {
        var game = games[i];
        if (game.gameId == gameId) {
            return game;
        }
    }
    return null;
}

// Gets open players, looks at planned game and starts first open game
function startOpenGames () {
    var openTeams = connectedPlayers.filter(function(player) {
        return !player.isInGame();
    }).map(function(player) {
        return player.teamId;
    });

    for (var i = 0; i < plannedGames.length; i++) {
        if(plannedGames[i].every(function(t) {return openTeams.indexOf(t) >= 0; })) {
            console.log(plannedGames[i]);
            addGame(new Game(plannedGames[i].map(getPlayerByTeam)));
            plannedGames.splice(i, 1);
            break;
        }
    }

}

function getCurrentGames() {
    var currentGames = []
    games.forEach(function(game) {
        if (!game.over) {
            currentGames.push(game.sanitize());
        }
    });

    return currentGames;
}

function addGame(game) {
    games.push(game);
    io.sockets.emit('games', getCurrentGames());
}


// Have the server spin up the bots
if(testing){
    var children = []
    children.push(childProcess.exec('../client/run.sh bot_1'));
    children.push(childProcess.exec('../client/run.sh bot_2'));
    children.push(childProcess.exec('../client/run.sh bot_3'));

    process.on('exit', function() {
        children.forEach(function(child) {
            child.kill();
        });
    });
}


// Basic server functionality
var games = []; // List of all games, not just running games
var connectedPlayers = []; // All players who are connected
var plannedGames = [];

// Generate planned games
var filePath = path.join(__dirname + '/matches');
var matches = fs.readFileSync(filePath, {encoding: 'utf-8'});
matches.split("\n").forEach(function(line) {
    var players = line.split(" ");
    plannedGames.push(players);
});

io.set("heartbeat timeout", 600);//set heartbeat timeout to 10min

io.sockets.on('connection', function (socket) {

    socket.player = new Player(socket);
    socket.emit('games', getCurrentGames()); //only relevant to lobby.js

    socket.on('teamId', function(tID) {
        teamId = getUniqueTeamId(tID);
        socket.player.teamId = teamId;
        console.log('Player ' + teamId + ' has joined.');
        connectedPlayers.push(socket.player);

        // Matching code - Needs fixing
        if (teamId.toLowerCase() == 'test') {
            var players = ['bot_1', 'bot_2', 'bot_3'].map(getPlayerByTeam);
            players.unshift(socket.player);
            addGame(new Game(players));
        } else {
            startOpenGames();
        }
    });

    socket.on('infoRequest', function() {
        socket.emit('returnInfo',{
            games: getCurrentGames(),
            teams: teams
        });
    });

    socket.on('move', function(move) {
        if(socket.player.game != null){
            socket.emit('moveResponse', socket.player.game.doMove(socket.player, move));
        }
    });

    socket.on('disconnect', function() {
        var teamId = socket.player.teamId;
        console.log((teamId === undefined ? 'Spectator' : teamId) + ' has disconnected.');
        if(socket.player.teamId != undefined){
            connectedPlayers.splice(connectedPlayers.indexOf(socket.player), 1);
        }
        if (socket.player && socket.player.game && socket.player.number !== -1) {
            socket.player.game.quit();
        }
    });

    socket.on('info', function(info) {
        console.log(socket.player.teamId + 'says, "' + info + '".');
    });

    socket.on('spectate', function(room) {
        var game = getGameById(room);

        if (game !== null) {
            game.sendMoveRequest(); // start the game once there is a spectator
            game.sendSetup(socket.player);
        }
    });
});




