import logging
import re
import time
from typing import Callable, Dict, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from agentic.common import Agent, AgentRunner, RunContext
from agentic.tools.base import BaseAgenticTool
from agentic.tools.utils.registry import (ConfigRequirement, Dependency,
                                          tool_registry)


@tool_registry.register(
    name="WebCrawler",
    description="A tool to browse the academic calendar for Western University which contains information on all courses and their requirements.",
    dependencies=[
        Dependency(
            name="beautifulsoup4",
            version="4.12.2",
            type="pip",
        ),
        Dependency(
            name="selenium",
            version="4.15.2",
            type="pip",
        ),
        Dependency(
            name="webdriver-manager",
            version="4.0.2",
            type="pip",
        )
    ],  # Any pip packages your tool depends on
    config_requirements=[],  # Any required configuration settings
)
class WebCrawler(BaseAgenticTool):
    """A tool to browse the academic calendar for Western University which contains information on all courses and their requirements."""

    def __init__(self):
        """Initialize the Web Crawler tool"""
        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')  # Run in headless mode
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--log-level=3')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Add user agent to avoid detection
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
        
        # Initialize the driver
        self.driver = None
        self.courses_data = []
        logging.getLogger("WDM").setLevel(logging.CRITICAL)
        logging.getLogger("selenium").setLevel(logging.CRITICAL)

    def get_tools(self) -> list[Callable]:
        """Return a list of functions that will be exposed to the agent."""
        return [
            self.close_driver,
            self.go_to_course_lookup,
            self.select_course_category,
            self.select_course_level,
            self.click_course_lookup_search,
            self.get_course_details
        ]
        
    def start_driver(self):
        """Start the Chrome web driver. Use this function to start up the web driver that allows you to browse websites."""
        if not self.driver:
            try:
                # Set up Chrome options
                self.options.add_argument('--headless')
                self.options.add_argument('--no-sandbox')
                self.options.add_argument('--disable-dev-shm-usage')
                self.options.add_argument('--disable-gpu')
                
                # Initialize ChromeDriver with proper architecture detection
                service = ChromeService()
                self.driver = webdriver.Chrome(service=service, options=self.options)
                self.driver.implicitly_wait(10)  # Wait up to 10 seconds for elements
            except Exception as e:
                print(f"Error initializing ChromeDriver: {str(e)}")
                raise
        
    def close_driver(self):
        """Close the Chrome web driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def navigate_to_page(self, url: str) -> bool:
        """Navigate to the specified URL
        
        Args:
            url: String of the URL of the website to navigate to
        Returns:
            A boolean of whether the function operation was a success
        """
        try:
            if not self.driver:
                self.start_driver()
            self.driver.get(url)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error navigating to {url}: {str(e)}")
            return False
        
    def go_to_course_lookup(self):
        """Navigate to the course lookup page, where you can search for details about any course."""

        self.navigate_to_page("https://www.westerncalendar.uwo.ca/allCourses.cfm?SelectedCalendar=Live&ArchiveID=")

    def select_course_level(self, level):
        """Select the level of the course that you are searching for when on the course lookup page using the web driver.
        
        Args:
            level: The level of the course that you're looking for. Enter 0 for courses numbered 0001-0999, 1 for courses numbered
            1000-1999, 2 for courses numbered 2000-2999, 3 for courses numbered 3000-3999, and 4 for courses numbered 4000-4999
        """
        levelZero = self.driver.find_element(By.ID, "LevelFilter_0")
        levelOne = self.driver.find_element(By.ID, "LevelFilter_1")
        levelTwo = self.driver.find_element(By.ID, "LevelFilter_2")
        levelThree = self.driver.find_element(By.ID, "LevelFilter_3")
        levelFour = self.driver.find_element(By.ID, "LevelFilter_4")

        if levelZero.is_selected(): levelZero.click()
        if levelOne.is_selected(): levelOne.click()
        if levelTwo.is_selected(): levelTwo.click()
        if levelThree.is_selected(): levelThree.click()
        if levelFour.is_selected(): levelFour.click()

        if level == 0:
            element = self.driver.find_element(By.ID, "LevelFilter_0")
            element.click()
        elif level == 1:
            element = self.driver.find_element(By.ID, "LevelFilter_1")
            element.click()
        elif level == 2:
            element = self.driver.find_element(By.ID, "LevelFilter_2")
            element.click()
        elif level == 3:
            element = self.driver.find_element(By.ID, "LevelFilter_3")
            element.click()
        elif level == 4:
            element = self.driver.find_element(By.ID, "LevelFilter_4")
            element.click()

    def select_course_category(self, category):
        """Select the category of course when on the course lookup page using the web driver. 
        
        Args:
            category: A string of the category of courses to select. Ex. Computer Science, Chemistry, Biology
        """

        select_object = self.driver.find_element(By.ID, "start")
        select = Select(select_object)

        for option in select.options:
            # if re.search(category, option.text, re.IGNORECASE):
            if category == option.text:
                option.click()
                break
        
        print("Selected option: " + select.all_selected_options[0].text)

    def click_course_lookup_search(self):
        """Click the search button in the course lookup page. Use this function after selecting course category and course level"""
        
        search_button = self.driver.find_element(By.NAME, "searchWithBoxes")
        search_button.click()
        time.sleep(5)

    def get_page_content(self) -> str:
        """Get the current page's text content"""
        return BeautifulSoup(self.driver.page_source, 'html.parser')
    
    def get_course_details(self, courseName):
        """Returns info on the specified course including prerequisites, antirequisites, and a description of the course. Function
        should only be used after using click_course_lookup_search. The user cannot see the output from this function so make sure
        to give them a message about the acquired information.
        
        Args:
            courseName: The name of the course to get details from. Ex. Data Science 1000, Computer Science 1027. 
            Do not include the letters at the end of the course number (Ex. Do not use Data Science 1000B).
        """
        soup = self.get_page_content()
        sections = soup.find_all(class_="col-md-12")
        
        i = 0
        for tag in sections:
            if i < 3: 
                i += 1
                continue
            header = tag.find("h4")
            if re.search(courseName, header.contents[0].get_text().strip(), re.IGNORECASE):
                courseInfo = header.parent.next_sibling.next_sibling.get_text()
                courseInfo = re.sub(r'\s+', ' ', courseInfo).strip()
                return courseInfo
        return "Could not find course " + courseName
          
    
def main():
    web_crawler = WebCrawler()

    searcher = Agent(
        name="Western University course helper",
        instructions="You help obtain information on courses at Western University. You use tools to obtain course details and immediately provide the requested information in the same turn.",
        tools=[web_crawler],
    )

    AgentRunner(searcher).repl_loop()

    # obj = WebCrawler()
    # obj.go_to_course_lookup()
    # obj.select_course_category("Data Science")
    # obj.select_course_level(1)
    # obj.click_course_lookup_search()
    # print(obj.get_course_details("Data Science 1000"))

if __name__ == "__main__":
    main()