console.log('Admin_topic.js loaded');

$(document).ready(function() {
    var el = document.getElementById('sortable-articles');
    var sortable = Sortable.create(el, {
        handle: '.handle',
        animation: 150,
        onEnd: function (evt) {
            var newOrder = $('#sortable-articles').children().map(function() {
                return $(this).data('id');
            }).get();
            
            $.ajax({
                url: '/admin/topic/' + topicId + '/update_article_sort_order',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({new_order: newOrder}),
                success: function(data) {
                    if (data.status === 'success') {
                        console.log('Article order updated successfully');
                    } else {
                        console.error('Failed to update article order');
                    }
                },
                error: function() {
                    console.error('Failed to update article order');
                }
            });
        },
    });

    // Function to add a new flash message
    function addFlashMessage(message, category) {
        var alertClass = category === 'success' ? 'alert-success' : 'alert-danger';
        var flashMessage = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                             message +
                             '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                             '</div>');
        $('#flash-messages').append(flashMessage);
        
        // Fade out and remove the message after 5 seconds
        setTimeout(function() {
            flashMessage.fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    }

    // Delete article confirmation
    $('.delete-article').on('click', function() {
        var topicId = $(this).data('topic-id');
        var articleId = $(this).data('article-id');
        
        if (confirm('Are you sure you want to delete this article?')) {
            $.post('/admin/topic/' + topicId + '/article/' + articleId + '/delete', function(response) {
                if (response.status === 'success') {
                    addFlashMessage('Article deleted successfully.', 'success');
                    $('li[data-id="' + articleId + '"]').remove();
                } else {
                    addFlashMessage('Failed to delete the article. Please try again.', 'error');
                }
            }).fail(function() {
                addFlashMessage('An error occurred while deleting the article. Please try again.', 'error');
            });
        }
    });

    // Handle new article creation
    $('#new-article-btn').on('click', function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        window.location.href = href;
    });

    // Handle article editing
    $('.edit-article-btn').on('click', function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        window.location.href = href;
    });

    // Check for flash messages in URL parameters
    var urlParams = new URLSearchParams(window.location.search);
    var flashMessage = urlParams.get('flash');
    var flashCategory = urlParams.get('category');
    if (flashMessage) {
        addFlashMessage(decodeURIComponent(flashMessage), flashCategory || 'success');
        // Remove flash message from URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});