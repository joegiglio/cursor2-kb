$(document).ready(function() {
    const searchInput = $('#search-input');
    const searchButton = $('#search-button');
    const searchResults = $('#search-results');
    const resultsList = $('#results-list');
    const topicsContainer = $('#topics-container');
    const searchError = $('#search-error');
    const paginationContainer = $('#pagination-container');
    const searchResultsTitle = $('#search-results-title');

    let currentQuery = '';
    let currentPage = 1;

    searchButton.on('click', () => performSearch(1));
    searchInput.on('keypress', function(e) {
        if (e.which === 13) {
            performSearch(1);
        }
    });

    searchInput.on('input', function() {
        searchError.hide();
    });

    function performSearch(page) {
        const query = searchInput.val().trim();
        if (!isValidSearchQuery(query)) {
            showError('Please enter at least 3 characters for your search query.');
            return;
        }

        currentQuery = query;
        currentPage = page;

        $.ajax({
            url: '/search',
            method: 'GET',
            data: { query: query, page: page },
            success: function(response) {
                console.log('Search response:', response); // Debug log
                if (response.total_results !== undefined) {
                    displayResults(response.results, response.total_results);
                    displayPagination(response.total_pages, response.current_page);
                } else {
                    console.error('total_results is undefined in the response');
                    showError('An error occurred while processing search results.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Search error:', error); // Debug log
                showError('An error occurred while searching. Please try again.');
            }
        });
    }

    function isValidSearchQuery(query) {
        const validQueryRegex = /^[\p{L}\p{N}\s]{3,}$/u;
        return validQueryRegex.test(query);
    }

    function showError(message) {
        searchError.text(message).show();
        searchResults.hide();
        topicsContainer.show();
        paginationContainer.hide();
    }

    function displayResults(results, totalResults) {
        console.log('Displaying results. Total results:', totalResults); // Debug log
        resultsList.empty();
        if (results.length === 0) {
            resultsList.append('<li class="list-group-item">No results found.</li>');
            searchResultsTitle.text('Search Results (0 articles)');
        } else {
            searchResultsTitle.text(`Search Results (${totalResults} article${totalResults !== 1 ? 's' : ''})`);
            results.forEach(function(result, index) {
                const resultItem = `
                    <li class="list-group-item ${index % 2 === 0 ? 'bg-light' : ''}" style="background-color: ${index % 2 === 0 ? '#f0f0f0' : '#ffffff'};">
                        <h5><a href="/knowledge-base/topic/${result.topic_id}/article/${result.id}">${result.title}</a></h5>
                        <p>${result.blurb}</p>
                    </li>
                `;
                resultsList.append(resultItem);
            });
        }
        searchError.hide();
        searchResults.show();
        topicsContainer.hide();
    }

    function displayPagination(totalPages, currentPage) {
        paginationContainer.empty();

        if (totalPages <= 1) {
            paginationContainer.hide();
            return;
        }

        let paginationHtml = '<ul class="pagination justify-content-center">';

        // Previous button
        paginationHtml += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">&laquo;</a>
            </li>
        `;

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            paginationHtml += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        // Next button
        paginationHtml += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">&raquo;</a>
            </li>
        `;

        paginationHtml += '</ul>';
        paginationContainer.html(paginationHtml).show();

        // Add click event for pagination links
        paginationContainer.find('a.page-link').on('click', function(e) {
            e.preventDefault();
            const page = $(this).data('page');
            performSearch(page);
        });
    }
});