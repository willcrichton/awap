$(document).ready(function() {
    var ws = io.connect(location.protocol+'//'+location.hostname+':8080');
    ws.on('games', function(games) {
        console.log(games);
        var $list = $('#games');
        $list.html('');

        games.forEach(function(game) {
            var title = game.players.join(", ");
            $list.append('<li><a href="game.html#' + game.id + '">' + title + '</a></li>');
        });
    });

    $("#matchButton").click(function() {
        var teams = [];
        for (var i = 0; i < 4; i++) {
            var $input = $("input[name='teamid" + (i+1) + "']");
            var temp = $input.val();
            if(temp != ""){
                teams.push(temp);
            }
            $input.val('');
        }
        alert('Submitted your game. TODO: make this not an alert box');
        ws.emit('newGame', teams);
    });

    $('#grabGamesButton').click(function() {
        var $input = $('#getGamesId');
        ws.emit('getGames', $input.val());
        $input.val('');
    });
});
