var ws = io.connect(document.baseURI);
var blocks, board, myNum = -1, curBlock = 0, rotation = 0, curPos;

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

function updateBlockList() {
    var $blocks = $('#blocks');
    $blocks.html('');

    var maxHeight = 0;
    for (var i = 0; i < blocks.length; i++) {
        var block = blocks[i], $block = $('<div class="block"></div>');
        $block.data('index', i);
        $blocks.append($block);

        var maxX = 0, maxY = 0, minX = 0, minY = 0;
        for (var j = 0; j < block.length; j++) {
            var $tile = $('<div class="tile p' + myNum + '"></div>');
            $block.append($tile);

            var dim = $tile.width();
            $tile.css({
                left: dim * block[j].x,
                top: dim * block[j].y
            });

            maxX = Math.max(maxX, block[j].x);
            maxY = Math.max(maxY, block[j].y);

            minX = Math.min(minX, block[j].x);
            minY = Math.min(minY, block[j].y);
        }

        var tileDim = $block.find('.tile').width();
        $block.css({
            width: (1 + maxX - minX) * tileDim,
            height: (1 + maxY - minY) * tileDim,
            left: -minX * tileDim,
            top: -minY * tileDim
        });

        maxHeight = Math.max(maxHeight, $block.height() - minY * tileDim);
    }

    $('.block').css('height', maxHeight);

    curBlock = 0;
    $blocks.find('.block').click(function() {
        highlightBlock(false);
        curBlock = $(this).data('index');
        highlightBlock(true);
    });

    highlightBlock(false);
    highlightBlock(true);
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
    blocks = state.blocks;
    board = state.board;
    myNum = state.number;
    
    var $board = $('#board');
    $board.html('');
    for (var y = 0; y < board.dimension; y++) {
        for (var x = 0; x < board.dimension; x++) {
            var $tile = $('<div class="' + x + 'x' + y + ' tile"></div>');
            $tile.data('pos', {x: x, y: y});
            $board.append($tile);
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
    
    updateBlockList();
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

    updateBlockList();
});