
export const legend_endpoints = {
    in_range: "in_range",
    lower_in_range: "lower_in_range",
    upper_in_range: "upper_in_range",
    out_of_range: "out_of_range"
};

export function apply_color_map(value, edges, colors, range = legend_endpoints.out_of_range) {
    const idx = edges.reduce( (result, edge, index, array) => {
            return (edge <= value) ? index + 1 : result;
        },
        0
    );
    if (range == legend_endpoints.in_range || range == legend_endpoints.lower_in_range)
        return colors[idx - 1];
    return colors[idx];
}

export function make_legend_labels_out_of_range(edges, decimal_places) {
    return [...Array(edges.length+1).keys().map( idx => {
        if (idx == edges.length)
            return edges[edges.length - 1].toFixed(decimal_places) + " <";
        else if (idx == 0)
            return "   < " + edges[0].toFixed(decimal_places);
        else {
            return edges[idx-1].toFixed(decimal_places) + " - " + edges[idx].toFixed(decimal_places);
        }
    })];
}

export function make_legend_labels(edges, range = legend_endpoints.out_of_range, decimal_places = 0) {
    const result = make_legend_labels_out_of_range(edges, decimal_places);
    
    if (range == legend_endpoints.in_range || range == "in_range")
        return result.slice(1, -1);
    if (range == legend_endpoints.lower_in_range || range == "lower_in_range")
        return result.slice(1);
    if (range == legend_endpoints.upper_in_range || range == "upper_in_range")
        return result.slice(0, -1);

    return result;
}
