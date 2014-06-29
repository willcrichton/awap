///////////////////
// BLOKUS SERVER //
///////////////////

// create the static file server
var nodestatic = require('node-static');
var fs = new nodestatic.Server('./www');
var server = require('http').createServer(function(request, response) {
    request.addListener('end', function() {
        fs.serve(request, response);
    }).resume();
});
server.listen(8080);

// spin up the websocket server
var io = require('socket.io').listen(server, {log: false});

var Player = function(socket) {
    this.socket = socket;
    this.id = socket.id;
    this.blocks = [];
    this.game = null;
    this.number = -1;
};

Player.prototype = {
    clientState: function() {

        // TODO: include other players' block states
        return {
            blocks: this.game.players.map(function(p){ return p.blocks; }),
            board: this.game.board,
            turn: this.game.turn,
            number: this.number
        }
    },

    setup: function(game) {
        this.game = game;

        for (var i = 0; i < game.players.length; i++) {
            if (game.players[i].id == this.id) { this.number = i; }
        }

        this.socket.emit('setup', this.clientState());
    },
    
    update: function() {
        this.socket.emit('update', this.clientState());
    },

    isInGame: function() {
        return this.game !== null;
    },

    quit: function(msg) {
        this.game = null;
        this.socket.emit('end', msg);
    }
};

var Board = function() {
    this.dimension = 20;
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
    placeBlock: function(plNum, block, point) {
        var onAbsCorner = false, onRelCorner = false;
        var N = this.dimension - 1, corner;

        switch (plNum) {
        case 0: corner = {x: 0, y: 0}; break
        case 1: corner = {x: N, y: 0}; break
        case 2: corner = {x: N, y: N}; break
        case 3: corner = {x: 0, y: N}; break
        }

        for (var i = 0; i < block.length; i++) {
            var x = point.x + block[i].x, y = point.y + block[i].y;

            // TODO: informative errors
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

        for (var i = 0; i < block.length; i++) {
            var x = point.x + block[i].x, y = point.y + block[i].y;
            this.grid[x][y] = plNum;
        }

        return true;
    }
}


// TODO: more blocks
var BLOCKS = [
    [[0, 0], [0, 1], [1, 0]],
    [[0,0], [0, 1], [0, 2]],
    [[0, 0], [0, 1], [1, 0], [0, 2]],
    [[0, 0], [1, 1], [1, 0], [1, 2], [2, 1]],
    [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]],
    [[0, 0], [-1, 0], [0, -1], [1, 0], [0, 1]]
];

var NUM_BLOCKS = 6;

var Game = function(players) {
    this.turn = 0;
    this.players = players;
    this.board = new Board();

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

    for (var i = 0; i < NUM_BLOCKS; i++) {
        var oldBlock = BLOCKS[blockIds[i]], newBlock = [];
        for (var j = 0; j < oldBlock.length; j++) {
            newBlock[j] = {x: oldBlock[j][0], y: oldBlock[j][1]}
        }
        blocks.push(newBlock);
    }

    for (var i = 0; i < this.players.length; i++) {
        this.players[i].blocks = blocks.slice(0);
    }

    for (var i = 0; i < this.players.length; i++) {
        this.players[i].setup(this);
    }
};

Game.prototype = {
    doMove: function(pl, move) {

        // TODO: informative errors
        if (this.turn != pl.number) return false;
        if (move.block === undefined || move.pos === undefined || move.rotation === undefined ||
            move.pos.x === undefined || move.pos.y === undefined || move.block < 0 || 
            move.block >= pl.blocks.length || move.rotation < 0 || move.rotation > 3) 
        { 
            console.log(move.pos, move.block);
            return false; 
        }

        var oldBlock = pl.blocks[move.block], newBlock = [];
        for (var i = 0; i < oldBlock.length; i++) {
            var cx = oldBlock[i].x, cy = oldBlock[i].y;
            switch (move.rotation) {
            case 0: newBlock[i] = {x: cx, y: cy}; break
            case 1: newBlock[i] = {x: -cy, y: cx}; break
            case 2: newBlock[i] = {x: -cx, y: -cy}; break
            case 3: newBlock[i] = {x: cy, y: -cx}; break
            }
        }

        if (!this.board.placeBlock(pl.number, newBlock, move.pos)) return false;
        
        pl.blocks.splice(move.block, 1);
        this.turn = (this.turn + 1) % this.players.length;
        this.players.forEach(function(pl) { pl.update(); });

        return true;
    },

    quit: function() {
        for (var i = 0; i < this.players.length; i++) {
            this.players[i].quit("A player quit the game.");
        }
    }
};

var NUM_PLAYERS = 1;
io.sockets.on('connection', function (socket) {

    socket.player = new Player(socket);

    var waitingPlayers = [];
    for (var k in io.sockets.sockets) {
        var pl = io.sockets.sockets[k].player;
        if (!pl.isInGame()) waitingPlayers.push(pl);
    }

    if (waitingPlayers.length >= NUM_PLAYERS) {
        new Game(waitingPlayers.slice(0, NUM_PLAYERS));
    }

    socket.on('move', function(move) {
        socket.emit('moveResponse', socket.player.game.doMove(socket.player, move));
    });

    socket.on('disconnect', function() {
        if (socket.player.game) {
            socket.player.game.quit();
        }
    });
});




