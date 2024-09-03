console.log('Admin.js loaded');

$(document).ready(function() {
    $(".sortable").sortable({
        update: function(event, ui) {
            var newOrder = $(this).sortable('toArray', {attribute: 'data-id'});
            $.ajax({
                url: '/update_sort_order',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({new_order: newOrder}),
                success: function(response) {
                    if (response.status !== 'success') {
                        console.error('Failed to update sort order');
                    }
                },
                error: function() {
                    console.error('Error occurred while updating sort order');
                }
            });
        }
    });
});