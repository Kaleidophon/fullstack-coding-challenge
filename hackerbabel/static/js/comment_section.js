$(document).ready(function() {

	// Parse html in comments
	$(".comment-content").each(function() {
		var raw_comment = $(this).text(); // Get
		$(this).text("");
		var html_comment = $.parseHTML(raw_comment); // Parse

		$(html_comment).appendTo($(this));
	});
});