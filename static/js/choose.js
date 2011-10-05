function toggleDescription(description, callback) {
    $(description).animate({height: 'toggle'},
                           200,
                           callback);
}

function toggleDescription(e) {
    $('.description').toggle();
}
