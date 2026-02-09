import $ from 'jquery';

async function postcode_search(postcode) {
    const search_url = new URL("https://api.postcodes.io/postcodes/" + postcode);

    let response = await fetch(search_url);
    if (!response.ok) {
        let alert_root = $("#alert-root");
        if (alert_root.length == 0)
            return;
        alert_root[0].innerHTML = '<div class="alert alert-warning alert-dismissible fade show" role="alert">' +
            'The postcode ' + postcode + ' could not be found.' +
            '<button id="alert-closer" type="button" class="close" data-bs-dismiss="alert" aria-label="Close">' +
            '<span aria-hidden="true">&times;</span>' +
            '</button>' +
            '</div>';
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
            c.click();
        }
        let coordinates = await postcode_search(search_box.value);
        if (coordinates)
            callback(coordinates);
    };
}
