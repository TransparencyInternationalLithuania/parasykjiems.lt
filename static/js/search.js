function browserSupportsHistory() {
    return !!(window.history && history.replaceState);
}

var useHistory = browserSupportsHistory();

function encodeQuery(q) {
    return encodeURI(q.replace(/ /g, '+'));
}

function decodeQuery(q) {
    return decodeURI(q).replace(/\+/g, ' ');
}

function setLocationTerms(terms) {
    if (useHistory) {
        var url;
        if (terms == '') {
            url = '/';
        } else {
            url = '/?q=' + encodeQuery(terms);
        }
        history.replaceState(null, '', url);
    } else {
        if (terms == '') {
            window.location.replace('');
        } else {
            window.location.replace('#' + encodeQuery(terms));
        }
    }
}

function fetchResults(terms) {
    var results = $('#results');
    $.ajax({
               dataType: 'text',
               url: '/?results',
               data: { q: terms },
               success: function(newResults) {
                   results.html(newResults);
                   results.fadeTo(0, 1);
                   setLocationTerms(terms);
                   resultsTerms = terms;
                   resultsTimeout = null;
               }
           });
}

var resultsTimeout = null;
var resultsTerms = '';

function trim(str) {
    return str.replace(/^\s+|\s+$/g, '');
}

function startUpdate(delay, terms) {
    terms = trim(terms);
    if (terms == resultsTerms) return;
    if (resultsTimeout != null) {
        clearTimeout(resultsTimeout);
    }
    resultsTimeout = setTimeout(
        function() {
            fetchResults(terms);
            clearTimeout(resultsTimeout);
        },
        600
    );

    $('#results').fadeTo(0, 0.5);
}

$(function() {
      var q = $(document.search.q);
      q.focus();

      if ((window.location.hash != "") || !useHistory) {
          var terms = decodeQuery(window.location.hash.slice(1));
          q.val(terms);
          startUpdate(1, terms);
      }

      // Hide search button
      $("form input[type=submit]").hide();
      q.css({width: '100%'});

      resultsTerms = trim(q.val());

      function setq(e) {
          // Key pressed, so maybe we should update the
          // search results.
          var terms = q.val();
          if (terms == "") {
              q.addClass("q-empty");
          } else {
              q.removeClass("q-empty");
          }
          startUpdate(600, terms);
      }

      setq();
      q.keyup(setq);

      $('body').keypress(
          function(e) {
              if (e.which == 13) {
                  // Enter key pressed. If there is exactly one search
                  // result, follow it.
                  var resultItems = $('#result-list li');
                  if (resultsTimeout == null && resultItems.size() == 1) {
                      var href = resultItems.children('a').attr('href');
                      window.location.href = href;
                  } else {
                      // Otherwise, start AJAX update immediately to
                      // imitate submitting the search form.
                      startUpdate(1, q.val());
                  }
                  return false;
              } else {
                  return true;
              }
          }
      );

  }
 );
