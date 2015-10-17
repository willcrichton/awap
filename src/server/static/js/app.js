$(function() {
    function renderGraph(graph) {
        var nodes = _.keys(graph).map(function(k) {
            return {name: '', label: 'Test'};
        });

        // Links = edges
        var links = _(graph)
            .mapValues(function(v, from) {
                return _.keys(v).map(function(to) {
                    return {source: parseInt(from), target: parseInt(to)};
                });
            })
        .values()
        .flatten()
        .value();

        // Uses http://marvl.infotech.monash.edu/webcola/ to simulate physics
        var force = cola.d3adaptor()
            .linkDistance(10)
            .symmetricDiffLinkLengths(20)
            .size([window.innerWidth, window.innerHeight])
            .nodes(nodes)
            .links(links);

        // Iterate the force constraint
        force.start();
        for (var i = 0; i < 100; i++) { force.tick(); }
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
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5");

        var group = svg.append('g');

        var link = group
            .selectAll('.link')
            .data(links)
            .enter()
            .append('path')
            .attr('class', 'link')

            .attr('d', function(d) {
                var dx = d.target.x - d.source.x,
                    dy = d.target.y - d.source.y,
                    dr = Math.sqrt(dx * dx + dy * dy);
                return "M" + d.source.x + "," + d.source.y + "L" + d.target.x + "," + d.target.y;
            })
            .attr('marker-end', 'url(#end)');

        var node = group
            .selectAll('node')
            .data(nodes)
            .enter()
            .append('g');

        node.append('circle')
            .attr('class', 'node')
            .attr('r', 10);

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

        svgPanZoom(svg[0][0])
        return svg;
    }

    function updateGraph(svg, state) {
        var link = svg.selectAll('.link');
        var node = svg.selectAll('.node');

        node.attr('class', function(d) {
            var c = 'node';
            if (state.buildings.indexOf(d.index) > -1) {
                c += ' building';
            }

            state.pending_orders.forEach(function(order) {
                if (order.node == d.index) {
                    c += ' has-order';
                }
            });

            state.active_orders.forEach(function(order) {
                if (order[0].node == d.index) {
                    c += ' has-order';
                }
            });

            return c;
        });

        link.attr('class', function(d) {
            var c = 'link';

            state.active_orders.forEach(function(data) {
                var order = data[0];
                var path = data[1];

                for (var i = 0; i < path.length - 1; ++i) {
                    if ((d.target.index == path[i] &&
                         d.source.index == path[i + 1]) ||
                        (d.source.index == path[i] &&
                         d.target.index == path[i + 1])) {
                        c += ' in-use';

                        if (state.time - order.time_started == i + 1) {
                            c += ' is-train';
                        }

                        break;
                    }
                }
            });

            return c;
        });

        $('#time').text('Time: ' + state.time);
        $('#money').text('Money: ' + state.money);
    }

    var playing = false;
    var interval;
    var speed = $('#speed').val();

    function togglePlay(step) {
        if (!playing) {
            $(this).text('Pause');
            interval = setInterval(step, 1000 / speed);
        } else {
            $(this).text('Play');
            clearInterval(interval);
        }

        playing = !playing;
    }

    function $get(url) {
        return $.get(url).fail(function() {
            alert('Server is down.');
            if (playing) {
                togglePlay();
            }
        });
    }

    function playGame(step) {
        $('#step').click(step);

        $('#play').click(function() { togglePlay.call(this, step); });

        $('#speed').change(function() {
            speed = $(this).val();
            clearInterval(interval);
            if (playing) {
                interval = setInterval(step, 1000 / speed);
            }
        });
    }

    function main() {
        $('#container').css('height', window.innerHeight);

        if (LOG != '') {
            if (LOG.error !== undefined) {
                $('body').append('<div class="error">This team has not completed this round or did not run correctly.</div>');
                return;
            }
            var svg = renderGraph(LOG.graph);
            var curStep = 0;

            function step() {
                if (curStep == LOG.orders.length) {
                    alert('Game is over');
                    togglePlay(step);
                }

                updateGraph(svg, LOG.orders[curStep]);
                curStep++;
            }

            playGame(step);
        } else {
            console.log('No log detected, querying server...');
            $get('/graph').done(function(resp) {
                var svg = renderGraph(JSON.parse(resp));

                function step() {
                    $get('/step').done(function(resp) {
                        updateGraph(svg, JSON.parse(resp));
                    });
                }

                playGame(step);
            });
        }
    }

    main();
});
