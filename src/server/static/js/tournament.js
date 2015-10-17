function makeLink(team, round) {
    var encoded = encodeURIComponent(team);
    return '<a href="/?team=' + encoded + '&round=' + round + '">Round ' + round + '</a>';
}

$(function() {
    $.get('/teams').done(function(resp) {
        var response = JSON.parse(resp);
        if (response.error) {
            $('table').remove();
            $('.container').append('This page isn\'t available right now. Come back when the tournament starts.');
        } else {
            response.forEach(function(team) {
                $('tbody').append(
                    '<tr>' +
                        '<td>' + team + '</td>' +
                        '<td>' + makeLink(team, 1) + '</td>' +
                        '<td>' + makeLink(team, 2) + '</td>' +
                        '<td>' + makeLink(team, 3) + '</td>' +
                        '<td>' + makeLink(team, 4) + '</td>' +
                        '</tr>');
                var encoded = encodeURIComponent(team);
                $('ul').append('<li><a href="/?team=' + encoded + '">' + team + '</a></li>');
            });
        }
    });
});
