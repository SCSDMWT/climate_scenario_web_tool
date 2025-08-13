//import apply_color_map from "map.js"; 
const color_map = require("../src/color_map.js");


describe("basic", () => {
    const edges = [0.5, 1.5, 5.0];
    const colors = ["blue", "green", "red", "cyan"];
    test("values between the edges should be the middle color", () => {
        expect(
            color_map.apply_color_map(1.0, edges, colors)
        ).toBe(colors[1]);
    })
    test("values smaller than the first edge should be the first color", () => {
        expect(
            color_map.apply_color_map(0.0, edges, colors)
        ).toBe(colors[0]);
    });
    test("values larger than the second edge should be the last color", () => {
        expect(
            color_map.apply_color_map(2.0, edges, colors)
        ).toBe(colors[2]);
    });

    test("values larger than the third edge should be the last color", () => {
        expect(
            color_map.apply_color_map(10.0, edges, colors)
        ).toBe(colors[3]);
    });

    test("edges[0] -> colors[1]", () => {
        expect(
            color_map.apply_color_map(edges[0], edges, colors)
        ).toBe(colors[1]);
    });

    test("edges[1] -> colors[2]", () => {
        expect(
            color_map.apply_color_map(edges[1], edges, colors)
        ).toBe(colors[2]);
    });
    test("edges[2] -> colors[3]", () => {
        expect(
            color_map.apply_color_map(edges[2], edges, colors)
        ).toBe(colors[3]);
    });
});
