$(function(){
      $('.fold').hide();

      $('.foldable').click(
          function() {
              var foldable = $(this);
              var fold = foldable.find('.fold');
              fold.slideToggle('fast');
          }
      );

      // When a link inside a foldable is clicked, go to its location.
      $('.foldable a').click(
          function() {
              window.location.href = this.href; return false;
          }
      );

      $(window.location.hash).click();

      $('.letter blockquote')
          .click(
              function() {
                  $(this).toggleClass('collapsed');
                  return false;
              }
          )
          .addClass('collapsed');
      $('.letter blockquote a').click(
          function() {
              window.location.href = this.href; return false;
          }
      );
  });
