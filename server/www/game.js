var init = (function() {
    var ws = io.connect(location.protocol+'//'+location.hostname+':8080');
    var blocks, board, myNum = -1, curBlock = 0, rotation = 0, curPos, turn = 0;

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
        if (curPos === undefined || myNum === -1) return;

        var block = rotate(blocks[myNum][curBlock]);
        for (var i = 0; i < block.length; i++) {
            var tile = getTile(curPos.x + block[i].x, curPos.y + block[i].y);
            if (active) tile.addClass('hover');
            else tile.removeClass('hover');
        }
    }

    function updateBlockList() {
        var $blocks = $('#blocks');
        $blocks.html('');
        
        console.log(turn);

        var maxHeight = 0;
        for (var i = 0; i < blocks.length; i++) {
            var $group = $('<div class="blockgroup p' + i + ' ' + (i == turn ? 'active' : '') + '"></div>');
            $blocks.append($group);

            for (var j = 0; j < blocks[i].length; j++) {
                var block = blocks[i][j], $block = $('<div class="block"></div>');
                $block.data('index', j);
                $group.append($block);

                var maxX = 0, maxY = 0, minX = 0, minY = 0;
                for (var k = 0; k < block.length; k++) {
                    var $tile = $('<div class="tile p' + i + '"></div>');
                    $block.append($tile);

                    var dim = $tile.width();
                    $tile.css({
                        left: dim * block[k].x,
                        top: dim * block[k].y
                    });

                    maxX = Math.max(maxX, block[k].x);
                    maxY = Math.max(maxY, block[k].y);

                    minX = Math.min(minX, block[k].x);
                    minY = Math.min(minY, block[k].y);
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
        }

        $('.block').css('height', maxHeight);

        curBlock = 0;
        $('.blockgroup.p' + myNum).find('.block').click(function() {
            highlightBlock(false);
            curBlock = $(this).data('index');
            highlightBlock(true);
        });

        $('.blockgroup:not(.p' + myNum + ') .block').css('cursor', 'default');

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
        turn = state.turn;

        $('#waiting').hide();
        showBoard();
        $(document.body).attr('class', '').addClass(myNum == -1 ? 'spectate' : ('p' + myNum));

        var $board = $('#board');
        $board.html('');

        for (var i = 0; i < state.blocks.length; i++) {
            $board.append('<div class="corner"></div>');
        }
        
        for (var x = 0; x < board.dimension; x++) {
            for (var y = 0; y < board.dimension; y++) {
                var $tile = $('<div class="' + x + 'x' + y + ' tile"></div>');
                $tile.data('pos', {x: x, y: y});
                $board.append($tile);
            }
        }

        $board.css('width', board.dimension * $('.tile').outerWidth());

        for (var x = 0; x < board.dimension; x++) {
            for (var y = 0; y < board.dimension; y++) {
                if (board.grid[x][y] >= 0) {
                    getTile(x, y).addClass('p' + board.grid[x][y]);
                }
                if (board.grid[x][y] == -2) {
                    getTile(x, y).addClass('blocked');
                }
            }
        }
        for (var i = 0; i < board.bonus_squares.length; i++) {
            getTile(board.bonus_squares[i][0], board.bonus_squares[i][1]).html("<div class='bonus'></div>");
        }

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

        $board.append('<div class="clear"></div>');
    });

    ws.on('moveResponse', function(resp) {
        if (resp) {
            alert(resp);
        }
    });

    ws.on('update', function(state) {
        board = state.board;
        blocks = state.blocks;
        turn = state.turn;

        for (var x = 0; x < board.dimension; x++) {
            for (var y = 0; y < board.dimension; y++) {
                if (board.grid[x][y] >= 0) {
                    getTile(x, y).addClass('p' + board.grid[x][y]).removeClass('hover');
                }
            }
        }

        updateBlockList();
    });

    ws.on('end', function(scores) {
        $('#board-wrapper, #blocks, #waiting').hide();
        var names = ['Red', 'Yellow', 'Green', 'Blue']
        scores.forEach(function(scoreInfo) {
            $('#scores table').append('<tr><td class="name">' + scoreInfo[0] + ':</td> <td class="score">' + scoreInfo[1] + '</td></tr>');
        });

        $('#scores').show();
    });

    ws.on('connect', function() {
        var hash = window.location.hash.replace('#', '');
        if (hash != '') {
            ws.emit('spectate', hash);
        } else {
            ws.emit('clientInfo', {
                teamId: 'test',
                fast: false
            });
        }
    });
});

function showBoard(){
    $('#scores, #waiting').hide();
    $('#board-wrapper, #blocks').show();
}

$(window).load(function() {
    var count = 1;
    var $ellipsis = $('#waiting span');

    setInterval(function() {
        $ellipsis.html('');
        for (var i = 0; i < count; i++) $ellipsis.append('.');
        count = (count + 1) % 4;
    }, 300);

    init();
});
