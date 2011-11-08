function makeTogglable(elem, hiddenText, hiddenByDefault) {
    var normal =
        $('<div class="normal">')
        .html($(elem).html());
    var alternate =
        $('<div class="alternate">')
        .html(hiddenText);

    if (hiddenByDefault) {
        normal.hide();
    } else {
        alternate.hide();
    }

    $(elem)
        .html('')
        .append(normal)
        .append(alternate);
}

function toggle(elem) {
    $(elem).find('.normal, .alternate')
        .slideToggle(50);
}

$(function(){
      $('.foldable')
          .each(function (i, elem) {
                    makeTogglable($(elem).find('.fold'), '(rodyti)', true);
                })
          .click(function (e) {
                     if (!$(e.target).is('a')) {
                         toggle(this);
                     }
                 });

      $(window.location.hash).click();

      $('.message blockquote')
          .each(function(idx, elem) {
                  makeTogglable(elem, '...', true);
              })
          .click(function(e) {
                     if (!$(e.target).is('a')) {
                         toggle(this);
                     }
                 });
  });
