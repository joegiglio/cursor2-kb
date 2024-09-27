$(document).ready(function() {
    const searchInput = $('#search-input');
    const searchButton = $('#search-button');
    const searchResults = $('#search-results');
    const resultsList = $('#results-list');
    const topicsContainer = $('#topics-container');
    const searchError = $('#search-error');

    searchButton.on('click', performSearch);
    searchInput.on('keypress', function(e) {
        if (e.which === 13) {
            performSearch();
        }
    });

    searchInput.on('input', function() {
        searchError.hide();
    });

    function performSearch() {
        const query = searchInput.val().trim();
        if (!isValidSearchQuery(query)) {
            showError('Please enter at least 3 characters for your search query.');
            return;
        }

        $.ajax({
            url: '/search',
            method: 'GET',
            data: { query: query },
            success: function(response) {
                displayResults(response.results);
            },
            error: function(xhr, status, error) {
                showError('An error occurred while searching. Please try again.');
            }
        });
    }

    function isValidSearchQuery(query) {
        // Allow letters (including international characters), numbers, and spaces
        const validQueryRegex = /^[\p{L}\p{N}\s]{3,}$/u;
        return validQueryRegex.test(query);
    }

    function showError(message) {
        searchError.text(message).show();
        searchResults.hide();
        topicsContainer.show();
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
        searchError.hide();
        searchResults.show();
        topicsContainer.hide();
    }
});