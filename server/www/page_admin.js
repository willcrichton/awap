$(document).ready(function() {
    var ws = io.connect(location.protocol+'//'+location.hostname+':8080');
    ws.on('returnInfo', function(data) {
        console.log(data);
    });
    ws.emit('infoRequest');
    ws.on('games', function(games) {
        var $list = $('#games');
        $list.html("<tr>\
			          <td>Games</td>\
			          <td>Buttons</td>\
			          <td>Other Title</td>\
			        </tr>");

        games.forEach(function(game) {
            var title = game.players.join(", ");
            $list.append('<tr>\
			            	<td><a href="game.html#' + game.id + '">' + title + '</a></td>\
			            	<td style="text-align:center"> <button type="button">Click Me!</button></td>\
			            	<td>other field</td>\
			              </tr>');
        });
    });
});
