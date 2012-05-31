/**
 * Base JS enhancements
 */

// Set up Google Analytics
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-32268013-1']);
_gaq.push(['_setDomainName', 'badg.us']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();

$(document).ready(function () {

    $('.browserid-signin').click(function (e) {
        e.preventDefault();
        navigator.id.getVerifiedEmail(function(assertion) {
            if (assertion) {
                var $e = $('#id_assertion');
                $e.val(assertion.toString());
                $e.parent().submit();
            }
        });
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
