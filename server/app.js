/***********************************************************************
 * SBR SERVER: Responsible for creating, managing, and verifying games *
 ***********************************************************************/

/* GENERAL TODO:
 *  SERVER
 *  - Accept team NAMES as well when taking games from the lobby 
        (there is already a function 'getTeamIdFromName')
 *
 *  WEBPAGE
 *  - when you refresh a previous game, show the board
 *  - show blocks over coins (defer)
 *  - on receive new match, go to next match (defer)
 *  - add a 'back to scores' from board
 *  - add a 'back to lobby' from game
 */

var nodestatic = require('node-static');
var express = require('express');
var fs = require('fs');
var path = require('path');
var childProcess = require('child_process');
var crypto = require('crypto');
var geoip = require('geoip-lite')

var TESTING = false;

var TEAMS = {
    'will'  : 'Will Crichton',
    'patrick': 'Pitrack',
    'chris' : 'Christopher Yingerston',
    'thomson' : 'Termsern',
    'dillon' : 'Dillareau',
    'brandon' : 'B-DAWG',
    'test'  : 'Anonymous',
};

var BOT_NAMES = [
    'Agnes Bot',
    'Alfred Bot',
    'Archy Bot',
    'Bart Bot',
    'Benjamin Bot',
    'Bertram Bot',
    'Bruni Bot',
    'Buster Bot',
    'Edith Bot',
    'Ester Bot',
    'Flo Bot',
    'Francis Bot',
    'Francisco Bot',
    'Gil Bot',
    'Gob Bot',
    'Gus Bot',
    'Hank Bot',
    'Harold Bot',
    'Harriet Bot',
    'Henry Bot',
    'Jacques Bot',
    'Jorge Bot',
    'Juan Bot',
    'Kitty Bot',
    'Lionel Bot',
    'Louie Bot',
    'Lucille Bot',
    'Lupe Bot',
    'Mabel Bot',
    'Maeby Bot',
    'Marco Bot',
    'Marta Bot',
    'Maurice Bot',
    'Maynard Bot',
    'Mildred Bot',
    'Monty Bot',
    'Mordecai Bot',
    'Morty Bot',
    'Pablo Bot',
    'Seymour Bot',
    'Stan Bot',
    'Tobias Bot',
    'Vivian Bot',
    'Walter Bot',
    'Wilbur Bot'
];

//In the form of [x, y, value].
var BONUS_SQUARES = [
    [2, 9],
    [9, 17],
    [10, 2],
    [17, 10],
    [7, 7], [7, 12], [12, 12], [12, 7]
];

var BLOCKED_SQUARES = [
    [6, 6], [6, 7], [7, 6],
    [12, 6], [13, 6], [13, 7],
    [6, 12], [6, 13], [7, 13],
    [12, 13], [13, 12], [13, 13],
    [2, 2], [2, 17], [17, 17], [17, 2]
];

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

var NUM_BLOCKS = 8; //BLOCKS.length;

var TURN_LENGTH = 5000;
var DELAY_BETWEEN_TURNS = 300;

//use express to protect admin page
var fileserver = new nodestatic.Server('./www', {cache: 600});
var server = require('http').createServer(function(request, response) {
    request.addListener('end', function() {
        fileserver.serve(request, response);
    }).resume();
});
server.listen(8080);

var io = require('socket.io').listen(server, {log: false});

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

        if (this.teamId in bots) {
            bots[this.teamId].kill();
        }
    }
};

//Board is 2d array with -1 for no block and a players number for their block
var Board = function() {
    this.dimension = 20; //Square board is assumed
    this.grid = [];
    this.bonus_squares = BONUS_SQUARES;

    // populate the board with empty values
    for (var i = 0; i < this.dimension; i++) {
        this.grid[i] = [];
        for (var j = 0; j < this.dimension; j++) {
            this.grid[i][j] = -1;
        }
    }

    for (i = 0; i < BLOCKED_SQUARES.length; i++) {
        this.grid[BLOCKED_SQUARES[i][0]][BLOCKED_SQUARES[i][1]] = -2;
    }
};

Board.prototype = {
    canPlaceBlock: function(plNum, block, point) {
        var onAbsCorner = false, onRelCorner = false;
        var N = this.dimension - 1, corner;

        // Determine which corner is player's starting corner
        switch (plNum) {
        case 0: corner = {x: 0, y: 0}; break;
        case 1: corner = {x: N, y: 0}; break;
        case 2: corner = {x: N, y: N}; break;
        case 3: corner = {x: 0, y: N}; break;
        }

        for (var i = 0; i < block.length; i++) {
            var x = point.x + block[i].x, y = point.y + block[i].y;

            // TODO: informative errors
            // Check bounds and illegal plays
            if (x >= this.dimension || x < 0 ||
                y >= this.dimension || y < 0 ||
                this.grid[x][y] != -1 ||
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
};

function getRandomSubset(set, length) {
    var ids = [];
    for (var i = 0; i < length; i++) {
        while (true) {
            var idx = Math.floor(Math.random() * set.length);
            if (ids.indexOf(idx) < 0) {
                ids.push(idx);
                break;
            }
        }
    }

    return ids;
}

var Game = function(players, fast) {
    this.turn = 0;
    this.players = players;
    this.board = new Board();
    this.over = false;
    this.started = false;
    this.fast = fast;
    this.scores = [0, 0, 0, 0];
    this.gameId = crypto.randomBytes(8).toString('hex'); //unique ID

    // Generate a random list of Ids
    // TODO: This should be re-written to be O(n) (Fisher-Yates)
    var blockIds = getRandomSubset(BLOCKS, NUM_BLOCKS);
    var blocks = [];

    // Convert array blocks to x,y blocks, then sort by the above permutation
    for (var i = 0; i < NUM_BLOCKS; i++) {
        var oldBlock = BLOCKS[blockIds[i]], newBlock = [];
        for (var j = 0; j < oldBlock.length; j++) {
            newBlock[j] = {x: oldBlock[j][0], y: oldBlock[j][1]};
        }
        blocks.push(newBlock);
    }

    // Give each player a copy of the blocks
    for (i = 0; i < this.players.length; i++) {
        this.players[i].blocks = blocks.slice(0);
    }

    for (i = 0; i < this.players.length; i++) {
        this.sendSetup(this.players[i]);
        this.players[i].canMove = true;
    }

    if (this.fast) {
        this.sendMoveRequest();
    }

    console.log("Made a new game with " + players.map(function(p){return getNameFromTeamId(p.teamId);}).join(", ") + ".");
};

Game.prototype = {

    // rotation is in range [0, 3]
    rotateBlock: function(oldBlock, rotation) {
        var newBlock = [];
        for (var i = 0; i < oldBlock.length; i++) {
            var cx = oldBlock[i].x, cy = oldBlock[i].y;
            switch (rotation) {
            case 1: newBlock[i] = {x: -cy, y: cx}; break;
            case 2: newBlock[i] = {x: -cx, y: -cy}; break;
            case 3: newBlock[i] = {x: cy, y: -cx}; break;
            default: newBlock[i] = {x: cx, y: cy}; break;
            }
        }
        return newBlock;
    },

    // returns false if no error, string if error
    doMove: function(pl, move) {

        // Check for invalid or out of turn moves.
        if (this.turn != pl.number) { return 'not your turn'; }
        if (move.block === undefined || move.pos === undefined || move.rotation === undefined ||
            move.pos.x === undefined || move.pos.y === undefined || move.block < 0 ||
            move.block >= pl.blocks.length || move.rotation < 0 || move.rotation > 3)
        {
            return 'malformatted move ' + JSON.stringify(move);
        }

        // Properly rotate old block. (Maybe this should be a function)
        var newBlock = this.rotateBlock(pl.blocks[move.block], move.rotation);

        if (!this.board.placeBlock(pl.number, newBlock, move.pos)) {
            return 'illegal move ' + JSON.stringify(move);
        }

        var mult = 1;
        var block = pl.blocks[move.block];
        for (var i = 0; i < BONUS_SQUARES.length; i++) {
            var bonus = BONUS_SQUARES[i];
            for (var j = 0; j < block.length; j++) {
                if (bonus[0] == move.pos.x + block[j].x && bonus[1] == move.pos.y + block[j].y) {
                    mult = 2;
                }
            }
        }

        this.scores[pl.number] += mult * pl.blocks[move.block].length;

        pl.blocks.splice(move.block, 1);

        this.updateCanMove();
        if (this.checkIsOver()) {
            this.getRoom().emit('update', this.clientState());
            this.quit();
            return false;
        }

        do {
            this.turn = (this.turn + 1) % this.players.length;
        } while (!this.players[this.turn].canMove);

        this.getRoom().emit('update', this.clientState());

        // Clear the last players timer and set the current players timer
        this.clearTimer();
        this.setTimer();

        this.sendMoveRequest();//Ask the next player for their move

        return false;
    },

    getRoom: function() {
        return io.sockets.in(this.gameId);
    },

    quit: function() {
        if (this.over) return;
        this.over = true;
        this.clearTimer();

        var scores = this.getScores();
        var to_print = [];
        this.getRoom().emit('end', scores);
        this.players.forEach(function(player, idx) {
            to_print.push(player.teamId + ' ' + scores[idx][1]);
            player.quit();
        });

        startOpenGames();

        if (!TESTING) {
            io.sockets.emit('games', getCurrentGames());
        }

        if (!this.fast) {
            fs.appendFileSync('scores', to_print.join(',') + "\n");
        }
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
        this.started = true;
        var currplayer = this.players[this.turn];
        setTimeout(function(){ currplayer.socket.emit('moveRequest', {move: 1}); }, this.fast ? 0 : DELAY_BETWEEN_TURNS);
    },

    // Skips the current player, and will stop advancing if all players skip.
    advance: function() {
        if (this.checkIsOver()) {
            this.quit();
        } else {
            var oldTurn = this.turn;
            do {
                this.turn = (this.turn + 1) % this.players.length;
            } while (!this.players[this.turn].canMove);

            if (this.turn == oldTurn) return;

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
                return getNameFromTeamId(player.teamId);
            })
        };
    },

    clientState: function() {
        return {
            blocks: this.players.map(function(p){ return p.blocks; }),
            board: this.board,
            turn: this.turn,
            url: 'http://game.acmalgo.com/game.html#' + this.gameId // TODO: change this on prod
        };
    },

    sendSetup: function(player) {
        var number = this.players.indexOf(player);
        var state = this.clientState();
        state.number = number;

        state.players = this.players.map(function(pl) {
            return getNameFromTeamId(pl.teamId);
        });

        player.game = this;
        player.number = number;
        player.socket.join(this.gameId);
        player.socket.emit('setup', state);
    },

    getScore: function(player) {
        // gets the number of squares on the board that belong to the player
        return this.scores[this.players.indexOf(player)];
    },

    getScores: function() {
        return this.players.map((function(player) {
            return [player.teamId.split('@')[0] in TEAMS ? getNameFromTeamId(player.teamId) : 'Anonymous', this.getScore(player)];
        }).bind(this));
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

            if (blocks.length === 0) {
                player.canMove = false;
                return;
            }

            for (var b = 0; b < blocks.length; b++) {
                for (var rot = 0; rot < 4; rot++) {
                    var block = this.rotateBlock(blocks[b], rot);
                    for (var i = 0; i < this.board.dimension; i++) {
                        for (var j = 0; j < this.board.dimension; j++) {
                            if (this.board.canPlaceBlock(player.number, block, {x: i, y: j})) {
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
    var newTeamId = String(teamId);
    var i = 1;
    var teams = connectedPlayers.map(function(p) {return p.teamId; });

    while(teams.indexOf(newTeamId) != -1){
        newTeamId = newTeamId.replace(/_\d+/,"");
        newTeamId += ("@" + i);
        i++;
    }
    return newTeamId;
}

function isValidTeamId(teamId) {
    //teamId = teamId.split('@')[0];  
    return (teamId in TEAMS) || (teamId.substring(0,3) == "bot");
}

function getNameFromTeamId(teamId){
    var two_part_team = teamId.split('@');
    if(two_part_team.length == 2){
        return TEAMS[two_part_team[0]] + "@" + two_part_team[1];
    }
    return TEAMS[two_part_team[0]];
}

function getTeamIdFromName(TeamName){
    for (key in TEAMS)
        if(TEAMS[key] == TeamName){
            return key;
        }
    return undefined;
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
function startOpenGames() {
    var openTeams = connectedPlayers.filter(function(player) {
        return !player.isInGame();
    }).map(function(player) {
        return player.teamId;
    });

    var filter = function(t) {return openTeams.indexOf(t) >= 0; };
    for (var i = 0; i < plannedGames.length; i++) {
        var game = plannedGames[i];
        if(game.players.every(filter)) {
            var newGame = new Game(game.players.map(getPlayerByTeam), game.fast);
            addGame(newGame);

            if (game.creator) {
                game.creator.emit('onNewGame', newGame.gameId);
            }

            plannedGames.splice(i, 1);
            break;
        }
    }

}

function getCurrentGames() {
    var currentGames = [];
    games.forEach(function(game) {
        if (!game.over) {
            currentGames.push(game.sanitize());
        }
    });

    return currentGames;
}

function addGame(game) {
    games.push(game);
    if (!TESTING) {
        io.sockets.emit('games', getCurrentGames());
    }
}

function createBots(numBots) {
    var names = getRandomSubset(BOT_NAMES, numBots);
    var botIds = [];
    for (var i = 0; i < numBots; i++) {
        var botId = 'bot' + crypto.randomBytes(4).toString('hex');

        // TODO: delegate this out to Brandon's distributor
        var child = childProcess.exec('./client_nfg acmalgo.com:9010 ' + botId);

        bots[botId] = child;
        TEAMS[botId] = BOT_NAMES[names[i]];
        botIds.push(botId);
    }

    return botIds;
}

// Basic server functionality
var games = []; // List of all games, not just running games
var connectedPlayers = []; // All players who are connected
var plannedGames = [];
var bots = {};

process.on('exit', function() {
    for (var botId in bots) {
        bots[botId].kill();
    }
});

// Generate planned games
var filePath = path.join(__dirname + '/matches');
var matches = fs.readFileSync(filePath, {encoding: 'utf-8'});
matches.split("\n").forEach(function(line) {
    var players = line.split(" ");
    for(var i = 0; i < players.length; i++){
        if(players[i] == "bot"){
            var testers = createBots(1);
            players[i] = testers[0];
        }
    }

    plannedGames.push({players: players, fast: false, creator: null});
});

io.set('heartbeat timeout', 600); // set heartbeat timeout to 10min

io.sockets.on('connection', function (socket) {
    socket.player = new Player(socket);

    if (!TESTING) {
        socket.emit('games', getCurrentGames()); // only relevant to lobby.js
    }

    socket.on('clientInfo', function(args) {
        var teamId = getUniqueTeamId(args.teamId);
        if (!(isValidTeamId(teamId)) && !TESTING) {
            socket.emit('rejected');
            return;
        }
        socket.emit('name', teamId);

        socket.player.teamId = teamId;
        var address = socket.handshake.address;
        var location = geoip.lookup(address.address);
        console.log('Player ' + teamId + ' has joined from address ' + address.address + ' (' + location.city + ', ' + location.region + ', ' + location.country + ')');
        connectedPlayers.push(socket.player);

        // Matching code - Needs fixing
        if (teamId.toLowerCase().slice(0,4) == 'test' || args.fast) {
            var testers = createBots(3);
            testers.unshift(teamId);
            plannedGames.push({players: testers, fast: args.fast, creator: socket});
        } else {
            startOpenGames();
        }
    });

    socket.on('newGame', function(teams) {
        var numBots = 4 - teams.length;
        var testers = createBots(numBots);
        teams = teams.concat(testers);
        plannedGames.push({players: teams, fast: false, creator: socket});
        console.log("added game with: " + teams.join(', '));
        startOpenGames();
    });

    socket.on('adminInfoRequest', function() {
          socket.emit('returnInfo',{
              games: games
              plannedGames, plannedGames,
              teams: TEAMS,
              connectedTeams: connectedPlayers
          });
      });

    socket.on('move', function(move) {
        if(socket.player.game !== null){
            socket.emit('moveResponse', socket.player.game.doMove(socket.player, move));
        }
    });

    socket.on('disconnect', function() {
        var teamId = socket.player.teamId;
        if (socket.player && socket.player.game && socket.player.number !== -1) {
            console.log(getNameFromTeamId(teamId) + ' (' + teamId + ') has quit an active game.');
            socket.player.game.quit();
        } else {
            console.log((teamId === undefined ? 'Spectator' : teamId) + ' has disconnected.');
        }

        if(socket.player.teamId !== undefined){
            connectedPlayers.splice(connectedPlayers.indexOf(socket.player), 1);
        }
    });

    socket.on('info', function(info) {
        console.log(socket.player.teamId + 'says, "' + info + '".');
    });

    socket.on('spectate', function(id) {
        var game = getGameById(id);
        if (game === null) return;

        if (game.over) {
            game.sendSetup(socket.player);
            socket.emit('end', game.getScores());
        } else {
            if (!game.started) {
                game.sendMoveRequest(); // start the game once there is a spectator
            }
            game.sendSetup(socket.player);
        }
    });

    socket.on('getGames', function(id) {
        var pl = getPlayerByTeam(id);
        socket.emit('games', games.filter(function(game) {
            return game.players.indexOf(pl) > -1;
        }).map(function(game) {
            return game.sanitize();
        }));
    });
});
