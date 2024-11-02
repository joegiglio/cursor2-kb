import pytest
from playwright.sync_api import Page, expect
from faker import Faker
import random
import os
from screeninfo import get_monitors

# Initialize faker with multiple locales
fake = Faker(['en_US', 'ja_JP', 'zh_CN', 'ko_KR', 'ru_RU'])

def get_screen_resolution():
    """Get the primary monitor's resolution"""
    try:
        primary_monitor = get_monitors()[0]  # Get the primary monitor
        return {
            'width': primary_monitor.width,
            'height': primary_monitor.height
        }
    except Exception as e:
        print(f"Failed to get screen resolution: {e}")
        # Fallback to a reasonable default if we can't get the screen resolution
        return {'width': 1366, 'height': 768}

@pytest.fixture
def page(browser):
    """Create a new page with maximized browser window."""
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    # Use JavaScript to maximize the window
    page.evaluate("""() => {
        window.moveTo(0, 0);
        window.resizeTo(
            window.screen.availWidth,
            window.screen.availHeight
        );
    }""")
    return page

@pytest.fixture
def admin_page(page: Page):
    """Setup admin access"""
    page.goto("/admin")
    yield page

def generate_test_data():
    """Generate random test data in different languages"""
    languages = ['en_US', 'ja_JP', 'zh_CN', 'ko_KR', 'ru_RU']
    lang = random.choice(languages)
    fake.locale = lang
    
    return {
        'title': fake.catch_phrase()[:25],  # Limit to 25 chars for topic name
        'content': fake.text(max_nb_chars=1000),
        'language': lang
    }

@pytest.fixture
def test_topic(admin_page: Page):
    """Create and yield a test topic with random data"""
    data = generate_test_data()
    
    admin_page.fill("#topic_name", data["title"])
    admin_page.click("button:has-text('Create Topic')")
    
    # Wait for success message
    expect(admin_page.locator(".alert-success")).to_be_visible()
    
    # Get the topic ID from the list item
    topic_id = admin_page.locator(f"li:has-text('{data['title']}')").get_attribute("data-id")
    
    yield {
        "id": topic_id,
        "title": data["title"],
        "language": data["language"]
    }
    
    # Cleanup using the delete button
    delete_button = admin_page.locator(f"li[data-id='{topic_id}'] .delete-topic")
    delete_button.click()
    admin_page.on("dialog", lambda dialog: dialog.accept())

@pytest.fixture
def test_article(admin_page: Page, test_topic):
    """Create and yield a test article with random data"""
    data = generate_test_data()
    
    # Navigate to topic page first
    admin_page.click(f"a:has-text('{test_topic['title']}')")
    
    admin_page.click("text=New Article")
    admin_page.fill("#article_title", data["title"])
    admin_page.fill("#article_content", data["content"])
    admin_page.click("button:has-text('Create Article')")
    
    expect(admin_page.locator(".alert-success")).to_be_visible()
    
    article_id = admin_page.locator(f"li:has-text('{data['title']}')").get_attribute("data-id")
    
    yield {
        "id": article_id,
        "title": data["title"],
        "content": data["content"],
        "topic_id": test_topic["id"],
        "language": data["language"]
    }
    
    # Cleanup using the delete button
    delete_button = admin_page.locator(f"li[data-id='{article_id}'] .delete-article")
    delete_button.click()
    admin_page.on("dialog", lambda dialog: dialog.accept())

@pytest.fixture
def multilingual_articles(admin_page: Page, test_topic):
    """Create articles in different languages"""
    articles = []
    languages = ['ja_JP', 'zh_CN', 'ko_KR', 'ru_RU']
    
    # Navigate to topic page first
    admin_page.click(f"a:has-text('{test_topic['title']}')")
    
    for lang in languages:
        fake.locale = lang
        data = {
            'title': fake.catch_phrase()[:100],
            'content': fake.text(max_nb_chars=500),
            'language': lang
        }
        
        admin_page.click("text=New Article")
        admin_page.fill("#article_title", data["title"])
        admin_page.fill("#article_content", data["content"])
        admin_page.click("button:has-text('Create Article')")
        
        expect(admin_page.locator(".alert-success")).to_be_visible()
        article_id = admin_page.locator(f"li:has-text('{data['title']}')").get_attribute("data-id")
        data["id"] = article_id
        articles.append(data)
    
    yield articles
    
    # Cleanup
    for article in articles:
        delete_button = admin_page.locator(f"li[data-id='{article['id']}'] .delete-article")
        delete_button.click()
        admin_page.on("dialog", lambda dialog: dialog.accept())

def pytest_configure(config):
    """Configure pytest with required options"""
    config.option.screenshot = "on"
    config.option.output = "test-results"

@pytest.fixture(autouse=True)
def ensure_screenshots(page: Page, request):
    """Ensure screenshots are taken after each test"""
    yield
    try:
        # Create test-results directory if it doesn't exist
        os.makedirs("test-results", exist_ok=True)
        
        # Take screenshot after each test
        page.screenshot(
            path=f"test-results/{request.node.name}.png",
            full_page=True
        )
    except Exception as e:
        print(f"Failed to take screenshot: {e}")

@pytest.fixture
def browser_context_args(browser_context_args):
    """Fixture to set browser context arguments for all tests."""
    return {
        **browser_context_args,
        "viewport": None,
        "screen": {
            "width": 1920,
            "height": 1080
        }
    }
