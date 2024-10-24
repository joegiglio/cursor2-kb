from playwright.sync_api import Page, expect
import re
import random
import string
import time

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
    # This stupid test took forever.  Wasted a lot of AI time.  I am not sure why it was so 
    # difficult to get the correct locators.  Frustrating!  - JG 10/23/24

    # Generate a random topic name
    random_topic = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    new_topic_name = f"Updated {random_topic}"

    # Create a new topic
    page.goto("http://localhost:5000/admin")
    page.fill("input#topic_name", random_topic)
    page.click("button:has-text('Create Topic')")

    # Verify the new topic exists
    expect(page.locator("#topics-list")).to_contain_text(random_topic)

    # Find all edit buttons and click the last one
    edit_buttons = page.query_selector_all("button[id^='edit-topic-']")
    if not edit_buttons:
        raise Exception("No edit buttons found on the page")
    last_edit_button = edit_buttons[-1]
    last_edit_button_id = last_edit_button.get_attribute('id')
    topic_id = last_edit_button_id.split('-')[-1]
    last_edit_button.click()

    # Wait for the specific modal to be visible
    modal_selector = f"#editModal{topic_id}"
    modal = page.locator(modal_selector)
    expect(modal).to_be_visible()

    # Update the topic name in the active modal
    input_field = modal.locator(f"#new_name{topic_id}")
    expect(input_field).to_be_visible()
    input_field.fill(new_topic_name)
    modal.locator("button:has-text('Save changes')").click()

    # Wait for the modal to close
    expect(modal).to_be_hidden()

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

def test_search_functionality(page: Page):
    page.goto("http://localhost:5000")
    page.fill("#search-input", "test")
    page.click("button:has-text('Search')")
    expect(page.locator("#search-results")).to_be_visible()
    expect(page.locator("#results-list")).to_contain_text("Test Article")
