from playwright.sync_api import Page, expect

def test_homepage(page: Page):
    page.goto("http://localhost:5000")
    expect(page).to_have_title("Knowledge Base")
    expect(page.locator("h1")).to_contain_text("Knowledge Base")

def test_admin_page(page: Page):
    page.goto("http://localhost:5000/admin")

    locator = page.locator("#test-title")

    expect(locator).to_contain_text("Knowledge Base Admin")


# def test_create_topic(page: Page):
#     page.goto("http://localhost:5000/admin")
#     page.fill("input[name='topic_name']", "Yankee1")
#     page.click("button:has-text('Create Topic')")
#     #page.wait_for_timeout(1000)
#     #expect(page.locator(".alert-success")).to_contain_text("Topic created successfully")
#     #page.wait_for_timeout(1000)
#     expect(page.locator("#topics-list")).to_contain_text("Walk")


def xtest_create_topic(page: Page):
    page.goto("http://localhost:5000/admin")
    page.fill("input[name='topic_name']", "Yankee1")
    
    # Add console log listener
    page.on("console", lambda msg: print(f"Browser log: {msg.text}"))
    
    # Click the button and wait for navigation
    with page.expect_navigation(wait_until="networkidle") as navigation_info:
        page.click("button:has-text('Create Topic')")
    
    # Print navigation information
    print(f"Navigation info: {navigation_info.value}")
    
    # Check the current URL
    current_url = page.url
    print(f"Current URL after navigation: {current_url}")
    
    # Capture a screenshot for debugging
    page.screenshot(path="after_create_topic.png")
    
    # Continue with your assertions
    expect(page.locator("#topics-list")).to_contain_text("Walk")





# def test_edit_topic(page: Page):
#     page.goto("http://localhost:5000/admin")
#     page.click("text=Test Topic")
#     page.fill("input[name='new_name']", "Updated Test Topic")
#     page.click("button:has-text('Update')")
#     expect(page.locator(".alert-success")).to_contain_text("Topic updated successfully")
#     expect(page.locator("table")).to_contain_text("Updated Test Topic")

# def test_delete_topic(page: Page):
#     page.goto("http://localhost:5000/admin")
#     page.click("text=Updated Test Topic")
#     page.click("button:has-text('Delete')")
#     page.fill("input[name='confirmation']", "delete")
#     page.click("button:has-text('Confirm Delete')")
#     expect(page.locator(".alert-success")).to_contain_text("Topic and associated articles deleted successfully")
#     expect(page.locator("table")).not_to_contain_text("Updated Test Topic")

# def test_create_article(page: Page):
#     # First, create a topic
#     page.goto("http://localhost:5000/admin")
#     page.fill("input[name='topic_name']", "Article Test Topic")
#     page.click("button:has-text('Create Topic')")
    
#     # Now create an article
#     page.click("text=Article Test Topic")
#     page.click("text=New Article")
#     page.fill("input[name='title']", "Test Article")
#     page.fill(".ql-editor", "This is a test article content.")
#     page.fill("input[name='keywords']", "test, article, keywords")
#     page.click("button:has-text('Create Article')")
#     expect(page.locator(".alert-success")).to_contain_text("Article created successfully")
#     expect(page.locator("table")).to_contain_text("Test Article")

# def test_edit_article(page: Page):
#     page.goto("http://localhost:5000/admin")
#     page.click("text=Article Test Topic")
#     page.click("text=Test Article")
#     page.fill("input[name='title']", "Updated Test Article")
#     page.fill(".ql-editor", "This is an updated test article content.")
#     page.fill("input[name='keywords']", "updated, test, article, keywords")
#     page.click("button:has-text('Update Article')")
#     expect(page.locator(".alert-success")).to_contain_text("Article updated successfully")
#     expect(page.locator("table")).to_contain_text("Updated Test Article")

# def test_delete_article(page: Page):
#     page.goto("http://localhost:5000/admin")
#     page.click("text=Article Test Topic")
#     page.click("text=Updated Test Article")
#     page.click("button:has-text('Delete Article')")
#     expect(page.locator(".alert-success")).to_contain_text("Article deleted successfully")
#     expect(page.locator("table")).not_to_contain_text("Updated Test Article")

# def test_search_functionality(page: Page):
    page.goto("http://localhost:5000")
    page.fill("input[name='query']", "test")
    page.click("button:has-text('Search')")
    expect(page.locator("#search-results")).to_be_visible()