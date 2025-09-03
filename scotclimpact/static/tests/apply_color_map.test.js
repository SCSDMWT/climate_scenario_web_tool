//import {apply_color_map} from "map.js"; 
import {expect, describe, test} from '@jest/globals';
import {apply_color_map, legend_endpoints, make_legend_labels} from "../src/color_map.js";
//const color_map = require("../src/color_map.js");



describe("apply_color_map [basic]", () => {
    const edges = [0.5, 1.5, 5.0];
    const colors = ["blue", "green", "red", "cyan"];
    test("values between the edges should be the middle color", () => {
        expect(
            apply_color_map(1.0, edges, colors)
        ).toBe(colors[1]);
    })
    test("values smaller than the first edge should be the first color", () => {
        expect(
            apply_color_map(0.0, edges, colors)
        ).toBe(colors[0]);
    });
    test("values larger than the second edge should be the last color", () => {
        expect(
            apply_color_map(2.0, edges, colors)
        ).toBe(colors[2]);
    });

    test("values larger than the third edge should be the last color", () => {
        expect(
            apply_color_map(10.0, edges, colors)
        ).toBe(colors[3]);
    });

    test("edges[0] -> colors[1]", () => {
        expect(
            apply_color_map(edges[0], edges, colors)
        ).toBe(colors[1]);
    });

    test("edges[1] -> colors[2]", () => {
        expect(
            apply_color_map(edges[1], edges, colors)
        ).toBe(colors[2]);
    });
    test("edges[2] -> colors[3]", () => {
        expect(
            apply_color_map(edges[2], edges, colors)
        ).toBe(colors[3]);
    });
});


describe("make_legend_labels [out_of_range]", () => {
    const edges = [0.5, 1.5, 5.0];
    const labels = make_legend_labels(edges, legend_endpoints.out_of_range, 1);
    test("labels.length", () => {expect(labels.length).toBe(4)});
    test("label 0", () => {expect(labels[0]).toBe("   < 0.5")});
    test("label 1", () => {expect(labels[1]).toBe("0.5 - 1.5")});
    test("label 2", () => {expect(labels[2]).toBe("1.5 - 5.0")});
    test("label 3", () => {expect(labels[3]).toBe("5.0 <")});
});

describe("make_legend_labels [in_range]", () => {
    const edges = [0.5, 1.5, 5.0];
    const labels = make_legend_labels(edges, legend_endpoints.in_range, 1);
    test("labels.length", () => {expect(labels.length).toBe(2)});
    test("label 0", () => {expect(labels[0]).toBe("0.5 - 1.5")});
    test("label 1", () => {expect(labels[1]).toBe("1.5 - 5.0")});
});

describe("make_legend_labels [lower_in_range]", () => {
    const edges = [0.5, 1.5, 5.0];
    const labels = make_legend_labels(edges, legend_endpoints.lower_in_range, 1);
    test("labels.length", () => {expect(labels.length).toBe(3)});
    test("label 0", () => {expect(labels[0]).toBe("0.5 - 1.5")});
    test("label 1", () => {expect(labels[1]).toBe("1.5 - 5.0")});
    test("label 2", () => {expect(labels[2]).toBe("5.0 <")});
});

describe("make_legend_labels [upper_in_range]", () => {
    const edges = [0.5, 1.5, 5.0];
    const labels = make_legend_labels(edges, legend_endpoints.upper_in_range, 1);
    test("labels.length", () => {expect(labels.length).toBe(3)});
    test("label 0", () => {expect(labels[0]).toBe("   < 0.5")});
    test("label 1", () => {expect(labels[1]).toBe("0.5 - 1.5")});
    test("label 2", () => {expect(labels[2]).toBe("1.5 - 5.0")});
});
