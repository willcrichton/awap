function renderGraph(graph) {
    var nodes = _.keys(graph).map(function(k) {
        return {name: 'lol'};
    });

    // Links = edges
    var links = _(graph)
        .mapValues(function(v, from) {
            return _.keys(v).map(function(to) {
                return {source: parseInt(from), target: parseInt(to)};
            })
        })
        .values()
        .flatten()
        .value();

    // Uses http://marvl.infotech.monash.edu/webcola/ to simulate physics
    var force = cola.d3adaptor()
        .linkDistance(30)
        .size([window.innerWidth, window.innerHeight])
        .nodes(nodes)
        .links(links);

    // Iterate the force constraint
    force.start();
    for (var i = 0; i < 1000; i++) { force.tick(); }
    force.stop();

    // Create d3 object and find the appropriate SVG elements
    var svg = d3.select('body').append('svg')
        .attr('width', window.innerWidth)
        .attr('height', window.innerHeight);

    var link = svg
        .selectAll('.link')
        .data(links)
        .enter()
        .append('line')
        .attr('class', 'link');

    var node = svg
        .selectAll('node')
        .data(nodes)
        .enter()
        .append('circle')
        .attr('class', 'node')
        .attr('r', 5)

    // Update with values from the force constraint
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    return svg;
}

function updateGraph(svg, state) {
    var link = svg.selectAll('.link');
    var node = svg.selectAll('.node');

    node.attr('fill', function(d) {
        if (d.index == 0) {
            return '#f00';
        }
    });
}

function main() {
    $('#container').css('height', window.innerHeight);

    $.get('/graph').done(function(resp) {
        var svg = renderGraph(JSON.parse(resp).graph);
        setInterval(function() {
            $.get('/step').done(function(resp) {
                updateGraph(svg, JSON.parse(resp));
            });
        }, 5000);
    });
}

$(document).ready(main);
