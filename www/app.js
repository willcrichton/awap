var ws = io.connect(document.baseURI);
var blocks, board, curBlock = 0, rotation = 0, curPos;

function getTile(x, y) {
    return $('.tile.' + x + 'x' + y);
}

function rotate(block) {
    if (rotation === 0) return block;

    var newBlock = [block[0]];
    for (var i = 1; i < block.length; i++) {
        var cx = block[i].x, cy = block[i].y;
        if (rotation === 1) {
            newBlock[i] = {x: -cy, y: cx};
        } else if (rotation === 2) {
            newBlock[i] = {x: -cx, y: -cy};            
        } else if (rotation === 3) {
            newBlock[i] = {x: cy, y: -cx};
        }
    }

    console.log(rotation, block[1]);

    return newBlock;
}

function highlightBlock(active) {
    if (curPos === undefined) return;

    var block = rotate(blocks[curBlock]);
    for (var i = 0; i < block.length; i++) {
        var tile = getTile(curPos.x + block[i].x, curPos.y + block[i].y);
        if (active) tile.addClass('hover');
        else tile.removeClass('hover');
    }
}

$(document).keyup(function(e) {
    var key = e.which;

    if (key == 32) { 
        e.preventDefault();

        highlightBlock(false);
        rotation = (rotation + 1) % 4; 
        highlightBlock(true);
    }
});

ws.on('setup', function(state) {
    console.log(state);
    blocks = state.blocks;
    board = state.board;

    var $board = $('#board');
    for (var y = 0; y < board.dimension; y++) {
        for (var x = 0; x < board.dimension; x++) {
            var $sqr = $('<div class="' + x + 'x' + y + ' tile"></div>');
            $sqr.data('pos', {x: x, y: y});
            $board.append($sqr);
        }
    }

    $board.css('width', board.dimension * $('.tile').outerWidth());

    var $tiles = $('#board .tile');
    $tiles.hover(function() {
        curPos = $(this).data('pos');
        highlightBlock(true);
    }, function() {
        highlightBlock(false);
        curPos = undefined;
    }).click(function() {
        var pos = $(this).data('pos');
        ws.emit('move', {
            block: curBlock,
            rotation: rotation,
            pos: pos
        });
    });
});

ws.on('moveResponse', function(resp) {
    if (!resp) {
        alert('Invalid move or not your turn.');
    }
});

ws.on('update', function(state) {
    board = state.board;
    blocks = state.blocks;

    for (var x = 0; x < board.dimension; x++) {
        for (var y = 0; y < board.dimension; y++) {
            if (board.grid[x][y] >= 0) {
                getTile(x, y).addClass('p' + board.grid[x][y]);
            }
        }
    }
});