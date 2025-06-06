from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import logging
import re
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WesternScraper:
    def __init__(self):
        # Initialize Chrome options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')  # Run in headless mode
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        # Add user agent to avoid detection
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
        
        # Initialize the driver
        self.driver = None
        self.courses_data = []
        
    def start_driver(self):
        """Start the Chrome driver"""
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
                logger.error(f"Error initializing ChromeDriver: {str(e)}")
                raise
        
    def close_driver(self):
        """Close the Chrome driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def navigate_to_page(self, url: str) -> bool:
        """Navigate to the specified URL"""
        try:
            if not self.driver:
                self.start_driver()
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
        
    def wait_and_click(self, by: By, value: str, timeout: int = 10) -> bool:
        """Wait for an element to be clickable and click it"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return True
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {value}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element {value}: {str(e)}")
            return False
            
    def get_page_content(self) -> BeautifulSoup:
        """Get the current page content as BeautifulSoup object"""
        return BeautifulSoup(self.driver.page_source, 'html.parser')
        
    def scrape_department_courses(self, department_url: str) -> list[dict]:
        """Scrape all courses from a department page"""
        try:
            if not self.navigate_to_page(department_url):
                return []
            
            time.sleep(2)  # Wait for content to load
            soup = self.get_page_content()

            courses = []
            course_boxes = soup.find_all(class_="panel-group", limit=3)

            index = 0
            for course in course_boxes:
                print(course)
                print(index)
                index += 1

            # for link in course_links:
            #     course_url = f"https://westerncalendar.uwo.ca{link['href']}"
            #     course_details = self.scrape_course_details(course_url)
            #     if course_details:
            #         courses.append(course_details)
            #         print(f"Scraped course: {course_details['course_name']}")
            
            return courses
        except Exception as e:
            print(f"Error scraping department {department_url}: {str(e)}")
            return []

    def scrape_faculty_departments(self, faculty_url: str) -> None:
        """Scrape all departments from a faculty page"""
        try:
            if not self.navigate_to_page(faculty_url):
                return
            
            time.sleep(2)  # Wait for content to load
            soup = self.get_page_content()
            
            department_links = soup.find_all('a', href=lambda href: href and 'Department.cfm' in href)
            
            for link in department_links:
                dept_url = f"https://westerncalendar.uwo.ca{link['href']}"
                logger.info(f"Scraping department: {link.text.strip()}")
                courses = self.scrape_department_courses(dept_url)
                self.courses_data.extend(courses)
                
        except Exception as e:
            logger.error(f"Error scraping faculty {faculty_url}: {str(e)}")

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and visible"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_elements(self, by, value, timeout=10):
        """Wait for elements to be present"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def save_to_json(self) -> None:
        """Save the scraped data to a JSON file"""
        try:
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(self.courses_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved {len(self.courses_data)} courses to requirements.json")
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")

    
        #Scrape detailed information about a course
    def scrape_course_details(self, course_link: str) -> dict:
        try:
            if not self.navigate_to_page(course_link):
                return None
            
            time.sleep(2)  # Wait for content to load
            soup = self.get_page_content()
            course_name = soup.find('h2').get_text()

            # Compile antirequisites
            antireq_title = soup.find(name="strong", string=re.compile("Antirequisite"))
            if antireq_title: 
                antirequisites = antireq_title.parent.text.strip().split(",")
                antirequisites[0] = antirequisites[0][18:]

                for i in range(len(antirequisites)):
                    antirequisites[i] = antirequisites[i].strip()
            else: 
                antirequisites = None

            prereq_title= soup.find(name="strong", string=re.compile("Prerequisite"))
            if prereq_title: 

                # Separate requirement clauses by ';'
                prerequisites = prereq_title.parent.text.strip().split(";")
                index = 0

                #Remove 'Prerequisites(s):'
                prerequisites[0] = prerequisites[0][17:]

                # Strip white space around the corses
                for i in range(len(prerequisites)):
                    prerequisites[i] = prerequisites[i].strip()

                while index < len(prerequisites):
                    item = prerequisites[index]
                    if item == "or":
                        prerequisites[index] = prerequisites[index - 1] + " or " + prerequisites[index + 1]
                        prerequisites.pop(index + 1)
                        prerequisites.pop(index - 1)
                    elif item == "and" or item == ";":
                        prerequisites.pop(index)
                        continue
                    index += 1
            else:
                prerequisites = None

            credit = soup.find("strong", string="Course Weight:").parent.text[-4:]
            category = soup.find("strong", string="Breadth:").parent.text.strip()[:-1].strip()[-1:]

            return {
                "course_name": course_name if course_name else "",
                "course_link": course_link,
                "antirequisites": antirequisites if antirequisites else "None",
                "prerequisites": prerequisites if prerequisites else "None",
                "credit": credit,
                "category": category
            }
        except Exception as e:
            print(f"Error scraping course {course_link}: {str(e)}")
            return None
        
    def scrape_module_details(self, module_link: str) -> dict:
        try:
            if not self.navigate_to_page(module_link):
                print("Error")
                return None
            
            time.sleep(2.5)  # Wait for content to load
            soup = self.get_page_content()

            # Code for finding module NAME and TYPE (MAJOR, MINOR, ETC...)
            header = soup.find("h2").contents[2].strip()
            programType = header.split()[0]
            moduleName = header.split("IN")[1].strip()

            # Code for finding module GRADUATION requirements
            moduleReqs = soup.find(class_="moduleInfo")
        
            try:
                gradReqs = {}
                currKey = ""
                index = 3
            
                while True:
                    # Next line throws an IndexError
                    curr = moduleReqs.contents[index].contents[0]
                    while curr:
                        if (re.search("course", curr.text)): 
                            if curr.text in gradReqs:
                                currKey = "Also " + curr.text
                            else:
                                currKey = curr.text 

                            curr = curr.next_sibling
                            currKey += curr.text
                            currKey = currKey.strip(", ").replace("\u00a0", "")
                            gradReqs[currKey] = []
                        else:
                            if curr.text.strip(",.: "):
                                gradReqs[currKey].append(curr.text.strip(", "))

                        curr = curr.next_sibling
                    index += 2
            except IndexError:
                print("End of grad reqs reached.")

            # Code for finding module ADMISSION requirements
            labels = soup.find(id="AdmissionRequirements")

            admissionReqs = {}
            index = 0
            for item in labels:
                courses = item.next_siblings

                creditsNeeded = item.get_text().strip()
                dict2 = {creditsNeeded: []}

                for thing in courses:
                    courseName = thing.get_text().strip()
                    if courseName: dict2[creditsNeeded].append(courseName)

                admissionReqs["course" + str(index)] = dict2

            return {
                "programType": programType,
                "moduleName": moduleName,
                "requirements": gradReqs, 
                "admissionReqs": admissionReqs 
            }
        except Exception as e:
            print(f"Error scraping module {module_link}: {str(e)}")
            return None

    def get_course_details(self, course_link: str):
        if not self.navigate_to_page(course_link):
                return None
            
        time.sleep(2.5)  # Wait for content to load
        soup = self.get_page_content()
        course_name = soup.find('h2').get_text()

        antireq_title = soup.find(name="strong", string=re.compile("Antirequisite"))
        if antireq_title: antireqs = antireq_title.parent.get_text().strip()
        else: antireqs = "None"

        prereq_title= soup.find(name="strong", string=re.compile("Prerequisite"))
        if prereq_title: prereqs = prereq_title.parent.get_text().strip()
        else: prereqs = "None"

        credit = soup.find("strong", string="Course Weight:").parent.text[-4:]
        category = soup.find("strong", string="Breadth:").parent.text.strip()[:-1].strip()[-1:]

        return {
            'credit': credit,
            'category': category,
            'prereqs': prereqs,
            'antireqs': antireqs,
            'course_name': course_name
        }

    def get_module_details(self, module_link: str):
        if not self.navigate_to_page(module_link):
                print("Error")
                return None
        time.sleep(2.5)  # Wait for content to load
        soup = self.get_page_content()

        graduationRequirements = soup.find(class_="moduleInfo").get_text()

        header = soup.find("h2").contents[2].strip()
        programType = header.split("IN")[0].strip()
        moduleName = header.split("IN")[1].strip()
        admissionRequirements = soup.find(id="AdmissionRequirements").get_text()

        return {
            'graduationRequirements': graduationRequirements,
            'programType': programType,
            'moduleName': moduleName,
            'admissionRequirements':  admissionRequirements
        }
    
    def get_department_modules(self, module_link: str):
        if not self.navigate_to_page(module_link):
                print("Error")
                return None
        time.sleep(2.5)  # Wait for content to load
        soup = self.get_page_content()
        dept_info = soup.find(id="collapseOne").contents[1]

        index = 1
        module_names_and_links = {}
        curr = dept_info.contents[index]
        while curr:
            module_name = curr.get_text().strip()
            module_names_and_links[module_name] = curr.contents[1]['href']

            try:
                curr = dept_info.contents[index]
            except IndexError:
                break
            
            index += 2

        return module_names_and_links
    
    # Just a function to get the department links data (important_files/dpt_links.json)
    def get_department_links(self):
        departments_page = "https://www.westerncalendar.uwo.ca/departments.cfm?SelectedCalendar=Live&ArchiveID="

        if not self.navigate_to_page(departments_page):
                print("Error")
                return None
        time.sleep(2.5)  # Wait for content to load

        soup = self.get_page_content()

        links_dict = {}
        def is_department(tag):
            if tag.has_attr('href'):
                if tag['href'].startswith("Departments"):

                    links_dict[tag.text] = tag['href']
                    return True
            return False

        for x in range (4):
            soup.find_all(is_department)
            next_button = self.driver.find_element(By.LINK_TEXT, 'Next')
            next_button.click()

        return links_dict
    
    def get_module_links(self, dpt_link):
        if not self.navigate_to_page(dpt_link):
                print("Error")
                return None
        time.sleep(2.5)  # Wait for content to load

        soup = self.get_page_content()
        links = soup.find(id='collapseOne').find_all('a')

        links_dict = {}
        for tag in links:
            links_dict[tag.text.strip()] = tag['href']

        return links_dict

def main():
    scraper = WesternScraper()
    link = "https://www.westerncalendar.uwo.ca/Modules.cfm?ModuleID=21112&SelectedCalendar=Live&ArchiveID="
    results = scraper.get_module_details(link)
    print(results) 

    # with open("front_end/static/data/module.json", "w") as file:
    #     json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()