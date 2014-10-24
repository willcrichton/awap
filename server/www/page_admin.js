$(document).ready(function() {
    var ws = io.connect(location.protocol+'//'+location.hostname+':8080');
    ws.on('returnInfo', function(data) {
        var $list = $('#games');
        $list.html("<tr>\
                      <td>Games</td>\
                      <td>Buttons</td>\
                      <td>Other Title</td>\
                    </tr>");
        data.plannedGames.forEach(function(game) {
            if(game.length == 4){
                var title = game.join(", ");
                $list.append('<tr style="background-color: red">\
                                <td>' + title + '</td>\
                                <td style="text-align:center"> <button type="button">Click Me!</button></td>\
                                <td>other field</td>\
                              </tr>');
            }
        });
        data.games.forEach(function(game) {
            if(game.over == false){
                var title = game.teams.join(", ");
                $list.append('<tr style="background-color: orange">\
                                <td><a href="game.html#' + game.id + '">' + title + '</a></td>\
                                <td style="text-align:center"> <button type="button">Click Me!</button></td>\
                                <td>other field</td>\
                              </tr>');
            }
        });
        data.games.forEach(function(game) {
            if(game.over == true){
                var title = game.teams.join(", ");
                $list.append('<tr style="background-color: green">\
                                <td><a href="game.html#' + game.id + '">' + title + '</a></td>\
                                <td style="text-align:center"> <button type="button">Click Me!</button></td>\
                                <td>other field</td>\
                              </tr>');
            }
        });
        $list = $('#teams');
        $list.html("<tr>\
                      <td>Teams</td>\
                      <td>Buttons</td>\
                    </tr>");
        for(team in data.teams){
            if(data.plannedGames.indexOf(team) >= 0){
                $list.append('<tr style="background-color: green>\
                                  <td>' + team + '</td>\
                                  <td>Buttons</td>\
                              </tr>');
            }
            else{
                $list.append('<tr style="background-color: red>\
                                  <td>' + team + '</td>\
                                  <td>Buttons</td>\
                              </tr>');
            }
        });
    });
    ws.emit('adminInfoRequest');
});
