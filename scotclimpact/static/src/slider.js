
/// Make an input slider
/// args should be an abject with the following keys:
//   range_start:
//   range_end:
//   range_step:
//   label:
//   root_div_id:
//   on_user_input:
export function make_slider(args) {
    /*
        <div id="tauReturnGroup" class="input-item">
          <label for="tauReturnParam" class="form-label" id="tauReturnParamLabel">Set the return time (in years) to visualise the 1-in-# year extreme:</label>
          <div class="slider-options">
            <input type="range" class="slider" min="10" max="100" step="10" defaultValue="50" id="tauReturnParam" list="tauReturnValues"/>
            <div id="tauReturnTicks" class="ticks">
              <span class="ticks-txt">10</span>
              <span class="ticks-txt">20</span>
              <span class="ticks-txt">30</span>
              <span class="ticks-txt">40</span>
              <span class="ticks-txt">50</span>
              <span class="ticks-txt">60</span>
              <span class="ticks-txt">70</span>
              <span class="ticks-txt">80</span>
              <span class="ticks-txt">90</span>
              <span class="ticks-txt">100</span>
            </div>
          </div>
        </div>
    */
    const group_div = document.createElement("div");
    group_div.setAttribute("id", args["range_id"] + "Group");
    group_div.setAttribute("class", "input-item");

    // Create the datalist for tick marks
    const datalist_id = args["range_id"] + "TickValues";
    const datalist = document.createElement("datalist");
    datalist.setAttribute("id", datalist_id);
    group_div.appendChild(datalist);

    // Label
    const label = document.createElement("label");
    const label_text = document.createTextNode(args["label"])
    label.appendChild(label_text);
    group_div.appendChild(label);

    // slider-div
    const slider_div = document.createElement("div");
    slider_div.setAttribute("class", "slider-options");
    group_div.append(slider_div);

    // slider
    const slider = document.createElement("input");
    slider.setAttribute("type", "range");
    slider.setAttribute("id", args["range_id"]);
    slider.setAttribute("class", "slider");
    slider.setAttribute("min", args["values"][0]);
    slider.setAttribute("max", args["values"][args["values"].length-1]);
    slider.setAttribute("step", args["values"][1] - args["values"][0]);
    slider.setAttribute("list", datalist_id);
    slider_div.appendChild(slider);

    // Ticks div
    const ticks_div = document.createElement("div");
    ticks_div.setAttribute("class", "ticks");
    slider_div.appendChild(ticks_div);

    // Add each tick label and datalist option
    for (var val of args["values"]) {
        // Ticks
        const tick = document.createElement("span");
        tick.setAttribute("class", "ticks-txt");
        tick.innerText = String(val);
        ticks_div.appendChild(tick);
        // Datalist option
        const option = document.createElement("option");
        option.setAttribute("value", val);
        datalist.appendChild(option);
    }

    const root_div = document.getElementById(args["root_div_id"]);
    root_div.appendChild(group_div);
    // Input for the actual slider
    // Div for ticks
    // spans for each value
    
    // Function to highlight the selection
    let on_user_input = args["on_user_input"];
    const decimal_places = 1;
    slider.oninput = () => {
        /*
        const slider_txt = input_values[slider_id].toFixed(decimal_places);
        for (var tick of $(tick_collection)[0].children) {
            tick.classList = (tick.innerHTML === slider_txt)
                ? "ticks-txt ticks-on"
                : "ticks-txt";
        }
        */

        on_user_input();
    };
}
