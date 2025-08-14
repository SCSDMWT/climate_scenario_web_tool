import $ from 'jquery';
import { SVG } from '@svgdotjs/svg.js'
import {make_legend_labels} from "../src/color_map.js";

export function draw_legend(edges, colors, endpoint_type, div_id = "#legend", box_size = 30, legend_width = 300) {
    const labels = make_legend_labels(edges, endpoint_type);

    for (const svg of $("svg"))
        svg.remove();
    var pos = box_size * (colors.length - 1);
    var draw = SVG().addTo(div_id).size(legend_width, box_size * colors.length );

    colors.forEach( (color, idx) => {
        draw
            .rect(box_size, box_size)
            .move(0, pos)
            .attr({fill: color});
        draw
            .text(labels[idx])
            .move(box_size + 5, pos);
        pos -= box_size;
    });
};
