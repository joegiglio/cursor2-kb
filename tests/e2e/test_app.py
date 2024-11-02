import pytest
from playwright.sync_api import expect, Page

def test_homepage_loads(page: Page):
    """Test public homepage and navigation"""
    page.goto("/")
    expect(page).to_have_title("Knowledge Base Help Desk")
    expect(page.locator("h1")).to_contain_text("Knowledge Base Help Desk")
    expect(page.locator("form")).to_be_visible()

def test_basic_search(page: Page, test_article):
    """Test search functionality with known article"""
    page.goto("/")
    search_input = page.locator("input[type='search']")
    search_input.fill(test_article["title"])
    page.click("button.btn-primary")
    expect(page.locator(".search-results")).to_be_visible()
    expect(page.locator(f"a:has-text('{test_article['title']}')")).to_be_visible()

def test_view_article(page: Page, test_article):
    """Test article viewing with known article"""
    page.goto(f"/article/{test_article['id']}")
    expect(page.locator(".article-title")).to_contain_text(test_article["title"])
    expect(page.locator(".article-content")).to_be_visible()
    expect(page.locator(".article-metadata")).to_be_visible()

def test_view_topic_articles(page: Page, test_topic, test_article):
    """Test viewing articles within a topic"""
    page.goto(f"/topic/{test_topic['id']}")
    expect(page.locator(".topic-title")).to_contain_text(test_topic["title"])
    expect(page.locator(".article-list")).to_be_visible()
    expect(page.locator(f"text={test_article['title']}")).to_be_visible()

def test_responsive_article_view(page: Page, test_article):
    """Test responsive layout for article viewing"""
    page.goto(f"/article/{test_article['id']}")
    
    # Mobile view
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator(".article-content")).to_be_visible()
    
    # Tablet view
    page.set_viewport_size({"width": 768, "height": 1024})
    expect(page.locator(".article-content")).to_be_visible()
    
    # Desktop view
    expect(page.locator(".article-content")).to_be_visible()

def test_multilingual_article_display(page: Page, multilingual_articles):
    """Test displaying articles with different language characters"""
    for article in multilingual_articles:
        page.goto(f"/article/{article['id']}")
        expect(page.locator(".article-title")).to_contain_text(article["title"])
        expect(page.locator(".article-content")).to_contain_text(article["content"])
        
        # Verify no character encoding issues (no replacement characters)
        title_text = page.locator(".article-title").text_content()
        content_text = page.locator(".article-content").text_content()
        assert "?" not in title_text
        assert "" not in title_text
        assert "?" not in content_text
        assert "" not in content_text

def test_multilingual_search(page: Page, multilingual_articles):
    """Test searching with different language characters"""
    for article in multilingual_articles:
        page.goto("/")
        search_input = page.locator("#search-input")
        # Search for part of the title
        search_term = article["title"][:10]
        search_input.fill(search_term)
        page.locator("button.btn-primary").click()
        
        expect(page.locator("#search-results")).to_be_visible()
        expect(page.locator(f"text={article['title']}")).to_be_visible() 