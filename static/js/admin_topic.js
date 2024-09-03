console.log('Admin_topic.js loaded');

$(document).ready(function() {
    console.log('Document ready in admin_topic.js');
    
    $(".sortable-articles").sortable({
        update: function(event, ui) {
            var newOrder = $(this).sortable('toArray', {attribute: 'data-id'});
            var topicId = $(this).data('topic-id');
            $.ajax({
                url: '/admin/topic/' + topicId + '/update_article_sort_order',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({new_order: newOrder}),
                success: function(response) {
                    if (response.status !== 'success') {
                        console.error('Failed to update article sort order');
                    }
                },
                error: function() {
                    console.error('Error occurred while updating article sort order');
                }
            });
        }
    });
});