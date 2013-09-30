$(document).ready(function(){
	$('.form-control').popover('show')
	$('.form-control').keydown(function(event) {
        if (event.keyCode == 13) {
            this.form.submit();
            return false;
         }
    });
    $('.image-upload').bind('DOMSubtreeModified', function() {
        var size = $('.image-upload').children().size()
        console.log(size)
        if (size > 2) {
            $('.image-upload').submit()
        }
    });
    $(".comment-button").click(function() {
        var id = $(this).context.id.split('-')[2]
        $("#comment-" + id).toggleClass('hidden', 'shown');
    });
    $('.dislikes').hover(function() {
        console.log("BLA")
        $(this).popover('show')
    }, function() {
        $(this).popover('hide')
    })
});