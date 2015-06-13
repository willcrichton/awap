function renderGraph(graph) {
    var nodes = _.keys(graph).map(function(k) {
        return {name: '', label: 'Test'};
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
        .linkDistance(50)
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

    svg.append("defs").selectAll("marker")
        .data(["end"])
        .enter().append("marker")
        .attr("id", function(d) { return d; })
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20) // change this if circles change size
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5");

    var link = svg
        .selectAll('.link')
        .data(links)
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', function(d) {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
        })
        .attr('marker-end', 'url(#end)');

        /*.append('line')
        .attr('class', 'link')
        .attr('marker-end', 'url(#end)');*/

    var node = svg
        .selectAll('node')
        .data(nodes)
        .enter()
        .append('g')

    node.append('circle')
        .attr('class', 'node')
        .attr('r', 12);

    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('y', 5)
        .text(function(d) { return d.index; });

    // Update with values from the force constraint
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) {
        return "translate(" + d.x + ", " + d.y + ")";
    });

    return svg;
}

function updateGraph(svg, state) {
    var link = svg.selectAll('.link');
    var node = svg.selectAll('.node');

    node.attr('class', function(d) {
        var c = 'node';
        var data = state.node_data[d.index];
        if (data.building) {
            c += ' building';
        }

        if (data.num_orders > 0) {
            c += ' has-order';
        }

        return c;
    });

    link.attr('class', function(d) {
        var c = 'link';
        if (state.graph[d.source.index][d.target.index].in_use) {
            c += ' in-use';
        }

        return c;
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
