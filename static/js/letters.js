$(function(){
      $('.letters tr a').each(
          function(i, a){
              var $a = $(a);
              $a.parent().parent().click(
                  function(e){
                      window.location = $a.attr('href');
                  });
          }
      );
  }
 );
