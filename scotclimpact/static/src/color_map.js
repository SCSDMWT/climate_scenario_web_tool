function apply_color_map(value, edges, colors) {
    const idx = edges.reduce( (result, edge, index, array) => {
            return (edge <= value) ? index + 1 : result;
        },
        0
    );
    return colors[idx];
}

function make_colorbar_labels(edges, colors) {
}

exports.apply_color_map = apply_color_map;

