$(function(){
      $('.fold').addClass('collapsed');

      $('.foldable').click(
          function(e) {
              if (!$(e.target).is('a')) {
                  var foldable = $(this);
                  var fold = foldable.find('.fold');
                  fold.toggleClass('collapsed');
              }
              return true;
          }
      );

      $(window.location.hash).click();

      $('.letter blockquote')
          .click(
              function(e) {
                  if (!$(e.target).is('a')) {
                      $(this).toggleClass('collapsed');
                      return false;
                  }
                  return true;
              }
          )
          .addClass('collapsed');
  });
