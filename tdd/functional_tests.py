"""
Functional (browser) tests — run with: python manage.py runserver
in another terminal, then: python functional_tests.py

Minimum viable To-Do app (outline):
- Home page with clear title and heading.
- A place to type a new item (input + placeholder).
- A list/table area to show items later (empty at first).
"""
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By


class NewVisitorTest(unittest.TestCase):
    """MVP: homepage shows To-Do title, heading, input, and empty list table."""

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_see_homepage_mvp(self):
        # User story: open site, see To-Do branding, find input and list area.
        self.browser.get("http://localhost:8000")

        self.assertIn("To-Do", self.browser.title)

        header = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertIn("To-Do Lists", header.text)

        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertEqual(
            inputbox.get_attribute("placeholder"),
            "Enter a to-do item",
        )

        table = self.browser.find_element(By.ID, "id_list_table")
        self.assertIsNotNone(table)


if __name__ == "__main__":
    unittest.main()
