"""Selenium browser tests for template selection and form interactions.

Run with:  venv/bin/python -m pytest tests/test_browser.py -m browser -v
"""
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.browser


# --- Kids Tier Tests ---


class TestKidsTier:
    @staticmethod
    def _get_visible_card(browser):
        """Return the first visible (displayed) template card."""
        cards = browser.find_elements(By.CSS_SELECTOR, ".template-card")
        for card in cards:
            if card.is_displayed():
                return card
        raise AssertionError("No visible template cards found on kids home page")

    def test_home_page_loads(self, browser, live_server):
        """Kids home page loads with template cards visible."""
        browser.get(f"{live_server}/kids/")
        assert "Choose Your Own Adventure" in browser.title or browser.find_element(
            By.CSS_SELECTOR, ".home-header h1"
        )
        cards = browser.find_elements(By.CSS_SELECTOR, ".template-card")
        assert len(cards) > 0, "Expected template cards on kids home page"

    def test_template_selection(self, browser, live_server):
        """Clicking a template card fills the prompt and marks it selected."""
        browser.get(f"{live_server}/kids/")
        card = self._get_visible_card(browser)
        expected_prompt = card.get_attribute("data-prompt")

        card.click()

        assert "selected" in card.get_attribute("class")
        prompt = browser.find_element(By.ID, "prompt")
        assert prompt.get_attribute("value") == expected_prompt

    def test_template_deselection(self, browser, live_server):
        """Clicking a selected template card again clears the prompt."""
        browser.get(f"{live_server}/kids/")
        card = self._get_visible_card(browser)

        # Select
        card.click()
        assert "selected" in card.get_attribute("class")

        # Deselect
        card.click()
        assert "selected" not in card.get_attribute("class")
        prompt = browser.find_element(By.ID, "prompt")
        assert prompt.get_attribute("value") == ""

    def test_start_story_redirects(self, browser, live_server):
        """Selecting a template and submitting redirects toward a scene page."""
        browser.get(f"{live_server}/kids/")
        card = self._get_visible_card(browser)
        card.click()

        submit = browser.find_element(By.CSS_SELECTOR, "#start-form .btn-primary")
        submit.click()

        # Wait for navigation away from /kids/ home
        WebDriverWait(browser, 15).until(
            lambda d: "/kids/" in d.current_url and d.current_url != f"{live_server}/kids/"
        )
        # Should land on a scene page or at least leave the home page
        assert "/kids/" in browser.current_url


# --- Bible Tier Tests ---


class TestBibleTier:
    def test_home_page_loads(self, browser, live_server):
        """Bible home page loads with section headers visible."""
        browser.get(f"{live_server}/bible/")
        headers = browser.find_elements(By.CSS_SELECTOR, ".bible-section-header")
        assert len(headers) > 0, "Expected Bible section headers"

    def test_template_selection_fills_reference(self, browser, live_server):
        """Clicking a Bible template fills the prompt with scripture reference, not story text."""
        browser.get(f"{live_server}/bible/")

        # Ensure the first section is open
        first_section = browser.find_element(By.CSS_SELECTOR, "details.bible-section")
        if not first_section.get_attribute("open"):
            first_section.find_element(By.CSS_SELECTOR, "summary").click()
            time.sleep(0.3)

        card = first_section.find_element(
            By.CSS_SELECTOR, ".template-card[data-scripture-reference]"
        )
        scripture_ref = card.get_attribute("data-scripture-reference")
        full_prompt = card.get_attribute("data-prompt")

        # Use JS click to avoid scroll/visibility issues with accordion content
        browser.execute_script("arguments[0].click();", card)

        prompt = browser.find_element(By.ID, "prompt")
        prompt_value = prompt.get_attribute("value")

        # Should contain the scripture reference, NOT the full story text
        assert prompt_value == scripture_ref
        assert prompt_value != full_prompt or scripture_ref == full_prompt

        # bible_reference_mode hidden field should still be "on"
        hidden = browser.find_element(
            By.CSS_SELECTOR, 'input[name="bible_reference_mode"]'
        )
        assert hidden.get_attribute("value") == "on"

    def test_manual_reference_entry(self, browser, live_server):
        """Typing a valid Bible reference and submitting doesn't show a validation error."""
        browser.get(f"{live_server}/bible/")
        prompt = browser.find_element(By.ID, "prompt")
        prompt.clear()
        prompt.send_keys("Genesis 1")

        submit = browser.find_element(By.CSS_SELECTOR, "#start-form .btn-primary")
        submit.click()

        # Wait for page to respond
        WebDriverWait(browser, 15).until(
            lambda d: d.current_url != f"{live_server}/bible/"
            or d.find_elements(By.CSS_SELECTOR, ".flash-error")
        )

        # Should NOT show a validation error for a valid reference
        errors = browser.find_elements(By.CSS_SELECTOR, ".flash-error")
        error_texts = [e.text for e in errors]
        for text in error_texts:
            assert "valid Bible book" not in text, f"Unexpected validation error: {text}"

    def test_invalid_reference_rejected(self, browser, live_server):
        """Typing an invalid reference shows an error message."""
        browser.get(f"{live_server}/bible/")
        prompt = browser.find_element(By.ID, "prompt")
        prompt.clear()
        prompt.send_keys("not a bible reference at all")

        submit = browser.find_element(By.CSS_SELECTOR, "#start-form .btn-primary")
        submit.click()

        # Wait for the page to reload with an error
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".flash-error"))
        )

        error = browser.find_element(By.CSS_SELECTOR, ".flash-error")
        assert error.text, "Expected an error message for invalid Bible reference"

    def test_accordion_sections_toggle(self, browser, live_server):
        """Clicking a collapsed Bible section opens it and reveals template cards."""
        browser.get(f"{live_server}/bible/")

        sections = browser.find_elements(By.CSS_SELECTOR, "details.bible-section")
        assert len(sections) >= 2, "Expected at least 2 Bible sections"

        # Find a closed section (not the first one which is open by default)
        closed_section = None
        for section in sections:
            if not section.get_attribute("open"):
                closed_section = section
                break

        if closed_section is None:
            pytest.skip("All sections already open — cannot test toggle")

        # Click to open
        closed_section.find_element(By.CSS_SELECTOR, "summary").click()

        # Wait for cards to be visible inside
        WebDriverWait(browser, 5).until(
            lambda d: len(
                closed_section.find_elements(By.CSS_SELECTOR, ".template-card")
            )
            > 0
        )

        cards = closed_section.find_elements(By.CSS_SELECTOR, ".template-card")
        assert len(cards) > 0, "Expected template cards inside opened section"
