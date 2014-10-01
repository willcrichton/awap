$(document).ready(function() {
    var ws = io.connect(location.protocol+'//'+location.hostname+':8080');
    ws.on('games', function(games) {
        var $list = $('#games');
        $list.html('');

        games.forEach(function(game) {
            var title = game.players.join(", ");
            $list.append('<li><a href="game.html#' + game.id + '">' + title + '</a></li>');
        });
    });
    $("#matchButton").click(function() {
        teams = [];
        for (var i = 0; i < 4; i++) {
            temp = $("input[name='teamid" + (i+1) + "']").val()
            if(temp != ""){
                teams.push(temp);
            }
        }
        ws.emit('newGame', teams);
    });
});
