$(document).ready(function() {
    var ws = io.connect(location.protocol+'//'+location.hostname+(location.port ? (':'+location.port) : ''));
    ws.on('returnInfo', function(data) {
    	var teams = data['teams'];
    	console.log(teams);
        var $list = $('#teams');
        $list.html("<tr>\
			          <td>Team Names</td>\
			          <td>Buttons</td>\
			        </tr>");

        data['teams'].forEach(function(team) {
            $list.append('<tr>\
			            	<td> ' + team + '</td>\
			            	<td style="text-align:center"> <button type="button">Click Me!</button></td>\
			              </tr>');
        });
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
