$(function() {
    $.get('/teams').done(function(resp) {
        var teams = JSON.parse(resp);
        teams.forEach(function(team) {
            var encoded = encodeURIComponent(team);
            $('ul').append('<li><a href="/?team=' + encoded + '">' + team + '</a></li>');
        });
    });
});
