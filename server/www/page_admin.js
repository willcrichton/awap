$(document).ready(function() {
    var ws = io.connect(location.protocol+'//'+location.hostname+(location.port ? (':'+location.port) : ''));
    ws.on('games', function(games) {
        var $list = $('#games');
        $list.html('');

        games.forEach(function(game) {
            var title = game.players.join(", ");
            $list.append('<li><a href="game.html#' + game.id + '">' + title + '</a></li>');
        });
    });
});
