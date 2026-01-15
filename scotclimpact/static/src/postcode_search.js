import $ from 'jquery';

async function postcode_search(postcode) {
    const search_url = new URL("https://api.postcodes.io/postcodes/" + postcode);

    let response = await fetch(search_url);
    if (!response.ok) {
      return;
    }

    let data = await response.json()
    if (!data.status == 200) {
      return;
    }

    return [ data.result.eastings, data.result.northings ];
}

/// Use the api at https://api.postcodes.io to lookup coordinates for a post code
export function attach_postcode_search(button, search_box, callback) {
    button.onclick = async () => {
        let closers = $('#alert-closer');
        for (let c of closers) {
            console.log(c);
            c.click();
        }
        let coordinates = await postcode_search(search_box.value);
        callback(coordinates);
    };
}
