$(document).ready(function() {
    const searchInput = $('#search-input');
    const searchButton = $('#search-button');
    const searchResults = $('#search-results');
    const resultsList = $('#results-list');
    const topicsContainer = $('#topics-container');

    searchButton.on('click', performSearch);
    searchInput.on('keypress', function(e) {
        if (e.which === 13) {
            performSearch();
        }
    });

    function performSearch() {
        const query = searchInput.val().trim();
        if (query.length === 0) return;

        $.ajax({
            url: '/search',
            method: 'GET',
            data: { query: query },
            success: function(response) {
                displayResults(response.results);
            },
            error: function(xhr, status, error) {
                alert('An error occurred while searching. Please try again.');
            }
        });
    }

    function displayResults(results) {
        resultsList.empty();
        if (results.length === 0) {
            resultsList.append('<li class="list-group-item">No results found.</li>');
        } else {
            results.forEach(function(result) {
                const resultItem = `
                    <li class="list-group-item">
                        <h5><a href="/knowledge-base/topic/${result.topic_id}/article/${result.id}">${result.title}</a></h5>
                        <p>${result.snippet}</p>
                    </li>
                `;
                resultsList.append(resultItem);
            });
        }
        searchResults.show();
        topicsContainer.hide();
    }
});