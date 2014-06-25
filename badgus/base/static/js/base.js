/**
 * Base JS enhancements
 */

// Set up Google Analytics
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-49796218-6', 'mozilla.org');
ga('send', 'pageview');

$(document).ready(function () {

    var signed_in_email = $('.signed-in-user').data('email');
    var signout_url = $('.browserid-signout').attr('href');

    $('.browserid-signin').click(function () {
        navigator.id.request();
        return false;
    });

    $('.browserid-signout').click(function () {
        navigator.id.logout();
        return false;
    });

    navigator.id.watch({
        loggedInUser: signed_in_email,
        onlogin: function (assertion) {
            if (!assertion) { return; }
            var el = $('#id_assertion');
            el.val(assertion.toString());
            el.parent().submit();
        },
        onlogout: function () {
            if (signed_in_email && signout_url) {
                location.href = signout_url;
            }
        }
    });

    $("form.obi_issuer button.issue").click(function () {
        // Grab the hosted assertion URL from the header link.
        var assertion_url =
            $('head link[rel="alternate"][type="application/json"]')
             .attr('href');
        // Fire up the backpack lightbox.
        OpenBadges.issue([assertion_url], function (errors, successes) {
            if (errors.length) {
                // TODO: Do something better here.
                window.alert("Failed to add award to your backpack.");
            }
            if (successes.length) {
                // TODO: Do something... at all?
            }
        });
        return false;
    });

});
