import $ from 'jquery';
import Cookies from 'js-cookie';

function onaccept(element) {
    /// Sets the accepted_tos cookie according to user input. Redirects to the index
    /// page if terms are accepted.
    if (element.checked) {
        Cookies.set('accepted_tos', 'yes');
        window.location.href = window.location.href.replace('/disclaimer', '');
    }
    else {
        Cookies.remove('accepted_tos');
    }
}

function update_accept_state(accept) {
    /// Updates the state of the ToS checkbox to be consistent
    /// with the value of the accepted_tos cookie.
    accept.checked = Cookies.get('accepted_tos');
}

function main() {
    const accept = $("#accept")[0];
    accept.onchange = () => onaccept(accept);
    update_accept_state(accept);
}

main()
