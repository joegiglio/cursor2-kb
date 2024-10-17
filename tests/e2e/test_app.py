from playwright.sync_api import Page, expect

def test_homepage(page: Page):
    page.goto("http://localhost:5000")
    expect(page).to_have_title("Knowledge Base")
    expect(page.locator("h1")).to_contain_text("Knowledge Base")


def test_admin_page(page: Page):
    page.goto("http://localhost:5000/admin")

    locator = page.locator("#test-title")

    expect(locator).to_contain_text("Knowledge Base Admin")


def test_create_topic_japanese(page: Page):
    import random
    import string

    # Generate a random 10-character string with Japanese characters
    japanese_chars = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
    random_topic = ''.join(random.choice(japanese_chars) for _ in range(10))

    page.goto("http://localhost:5000/admin")
    page.fill("input[name='topic_name']", random_topic)
    page.click("button:has-text('Create Topic')")
    expect(page.locator("#topics-list")).to_contain_text(random_topic)


def test_edit_topic(page: Page):
    import random
    import string

    # Generate a random topic name
    random_topic = ''.join(random.choice(string.ascii_letters) for _ in range(10))

    page.goto("http://localhost:5000/admin")
    page.fill("input[name='topic_name']", random_topic)
    page.click("button:has-text('Create Topic')")
    expect(page.locator("#topics-list")).to_contain_text(random_topic)

    # Edit the newly created topic
    page.click(f"text=Edit >> nth=0")
    new_topic_name = f"Updated {random_topic}"
    page.fill("input[name='new_name']", new_topic_name)
    page.click("button:has-text('Save Changes')")

    # Verify the topic was updated successfully
    expect(page.locator(".alert-success")).to_contain_text("Topic updated successfully")
    expect(page.locator("#topics-list")).to_contain_text(new_topic_name)


def xtest_delete_empty_topic(page: Page):

    import random
    import string

    # Generate a random topic name
    random_topic = ''.join(random.choice(string.ascii_letters) for _ in range(10))

    page.goto("http://localhost:5000/admin")
    page.fill("input[name='topic_name']", random_topic)
    page.click("button:has-text('Create Topic')")

    #page.click("button:has-text('Delete')")
    page.click(f"text=Delete")
 
   
    # Wait for the dialog to appear and be handled
    page.wait_for_event("dialog")

    expect(page.locator(".alert-success")).to_contain_text("Topic and associated articles deleted successfully")
    expect(page.locator("table")).not_to_contain_text(random_topic)

def test_create_article(page: Page):
    # First, create a topic
    page.goto("http://localhost:5000/admin")
    page.fill("input[name='topic_name']", "Article Test Topic")
    page.click("button:has-text('Create Topic')")
    
    # Now create an article
    page.click("text=Article Test Topic")
    page.click("text=New Article")
    page.fill("input[name='title']", "Test Article")
    page.fill(".ql-editor", "This is a test article content.")
    page.fill("input[name='keywords']", "test, article, keywords")
    page.click("button:has-text('Create Article')")
    expect(page.locator(".alert-success")).to_contain_text("Article created successfully")
    expect(page.locator(".list-group")).to_contain_text("Test Article")

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
    # page.goto("http://localhost:5000")
    # page.fill("input[name='query']", "test")
    # page.click("button:has-text('Search')")
    # expect(page.locator("#search-results")).to_be_visible()