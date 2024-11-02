import pytest
from playwright.sync_api import expect, Page
from conftest import generate_test_data

@pytest.fixture
def admin_page(page: Page, base_url):
    """Setup admin access"""
    page.goto(f"{base_url}/admin")
    return page

def test_create_topic(admin_page: Page):
    """Test topic creation"""
    data = generate_test_data()
    
    admin_page.fill("#topic_name", data["title"])
    admin_page.click("button:has-text('Create Topic')")
    
    # Verify success
    expect(admin_page.locator(".alert-success")).to_be_visible()
    expect(admin_page.locator(f"li:has-text('{data['title']}')")).to_be_visible()
    
    # Get topic ID for cleanup
    topic_id = admin_page.locator(f"li:has-text('{data['title']}')").get_attribute("data-id")
    
    # Set up dialog handler BEFORE clicking delete
    admin_page.once("dialog", lambda dialog: dialog.accept())
    
    # Cleanup
    delete_button = admin_page.locator(f"li[data-id='{topic_id}'] .delete-topic")
    delete_button.click()
    
    # Verify deletion
    expect(admin_page.locator(f"li:has-text('{data['title']}')")).not_to_be_visible()

def test_edit_topic(admin_page: Page):
    """Test topic editing"""
    # Generate initial and new test data
    initial_data = generate_test_data()
    new_data = generate_test_data()
    
    # Create initial topic
    admin_page.fill("#topic_name", initial_data["title"])
    admin_page.click("button:has-text('Create Topic')")
    
    # Verify initial creation
    expect(admin_page.locator(".alert-success")).to_be_visible()
    expect(admin_page.locator(f"li:has-text('{initial_data['title']}')")).to_be_visible()
    
    # Get topic ID for editing and cleanup
    topic_id = admin_page.locator(f"li:has-text('{initial_data['title']}')").get_attribute("data-id")
    
    # Click edit button
    admin_page.click(f"li[data-id='{topic_id}'] button:text('Edit')")
    
    # Wait for modal and fill in new name (using modal-specific selector)
    modal = admin_page.locator(".modal:visible")
    expect(modal).to_be_visible()
    modal.locator("input[type='text']").fill(new_data["title"])
    modal.locator("button:has-text('Save changes')").click()
    
    # Verify the edit was successful
    expect(admin_page.locator(".alert-success")).to_be_visible()
    expect(admin_page.locator(f"li:has-text('{new_data['title']}')")).to_be_visible()
    expect(admin_page.locator(f"li:has-text('{initial_data['title']}')")).not_to_be_visible()
    
    # Cleanup
    admin_page.once("dialog", lambda dialog: dialog.accept())
    delete_button = admin_page.locator(f"li[data-id='{topic_id}'] .delete-topic")
    delete_button.click()
    
    # Verify deletion
    expect(admin_page.locator(f"li:has-text('{new_data['title']}')")).not_to_be_visible()

def test_create_article(admin_page: Page, test_topic):
    """Test article creation with known topic"""
    data = generate_test_data()
    
    # Navigate to topic page first
    admin_page.click(f"a:has-text('{test_topic['title']}')")
    
    admin_page.click("text=New Article")
    admin_page.fill("#article_title", data["title"])
    admin_page.fill("#article_content", data["content"])
    admin_page.click("button:has-text('Create Article')")
    
    expect(admin_page.locator(".alert-success")).to_be_visible()
    expect(admin_page.locator(f"li:has-text('{data['title']}')")).to_be_visible()
    
    # Cleanup
    article_id = admin_page.locator(f"li:has-text('{data['title']}')").get_attribute("data-id")
    delete_button = admin_page.locator(f"li[data-id='{article_id}'] .delete-article")
    delete_button.click()
    admin_page.on("dialog", lambda dialog: dialog.accept())

def test_edit_article(admin_page: Page, test_article):
    """Test article editing with known article"""
    new_data = generate_test_data()
    
    # Navigate to topic page first
    admin_page.click(f"a:has-text('{test_article['topic_title']}')")
    admin_page.click(f"li[data-id='{test_article['id']}'] button.btn-outline-primary")
    admin_page.fill("#article_title", new_data["title"])
    admin_page.fill("#article_content", new_data["content"])
    admin_page.click("button:has-text('Save changes')")
    
    expect(admin_page.locator(".alert-success")).to_be_visible()
    expect(admin_page.locator(f"li:has-text('{new_data['title']}')")).to_be_visible()

def test_delete_article(admin_page: Page, test_article):
    """Test article deletion with known article"""
    # Navigate to topic page first
    admin_page.click(f"a:has-text('{test_article['topic_title']}')")
    delete_button = admin_page.locator(f"li[data-id='{test_article['id']}'] .delete-article")
    delete_button.click()
    admin_page.on("dialog", lambda dialog: dialog.accept())
    expect(admin_page.locator(f"li:has-text('{test_article['title']}')")).not_to_be_visible()

def test_responsive_admin_dashboard(admin_page: Page, test_topic, test_article):
    """Test responsive layout for admin dashboard"""
    admin_page.goto("/admin")
    
    # Mobile view
    admin_page.set_viewport_size({"width": 375, "height": 667})
    expect(admin_page.locator(".admin-panel")).to_be_visible()
    expect(admin_page.locator(f"li:has-text('{test_topic['title']}')")).to_be_visible()
    
    # Tablet view
    admin_page.set_viewport_size({"width": 768, "height": 1024})
    expect(admin_page.locator(".admin-panel")).to_be_visible()
    
    # Desktop view
    admin_page.set_viewport_size({"width": 1024, "height": 768})
    expect(admin_page.locator(".admin-panel")).to_be_visible()

def test_multilingual_content_creation(admin_page: Page):
    """Test creating content with different language characters"""
    test_data = [
        {
            'lang': 'ja_JP',
            'title': '日本語のテストトピック'
        },
        {
            'lang': 'zh_CN',
            'title': '中文测试主题'
        },
        {
            'lang': 'ko_KR',
            'title': '한국어 테스트 주제'
        },
        {
            'lang': 'ru_RU',
            'title': 'Тестовая тема'
        }
    ]
    
    created_topics = []
    
    for data in test_data:
        admin_page.fill("#topic_name", data["title"])
        admin_page.click("button:has-text('Create Topic')")
        
        expect(admin_page.locator(".alert-success")).to_be_visible()
        expect(admin_page.locator(f"li:has-text('{data['title']}')")).to_be_visible()
        
        topic_id = admin_page.locator(f"li:has-text('{data['title']}')").get_attribute("data-id")
        created_topics.append({"id": topic_id, "title": data["title"]})
    
    # Cleanup
    for topic in created_topics:
        delete_button = admin_page.locator(f"li[data-id='{topic['id']}'] .delete-topic")
        delete_button.click()
        admin_page.on("dialog", lambda dialog: dialog.accept())