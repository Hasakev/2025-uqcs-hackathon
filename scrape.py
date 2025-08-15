#!/usr/bin/env python3
"""
Modern Blackboard Scraper
Scrapes course information and grades from Blackboard Learn
Author: Updated for 2025
Python Version: 3.8+
Dependencies: selenium, requests, beautifulsoup4
"""

import argparse
import json
import requests
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlackboardScraper:
    def __init__(self, headless=False, browser='chrome'):
        self.driver = None
        self.session = None
        self.browser = browser.lower()
        self.headless = headless
        self.wait_timeout = 20
        
    def setup_driver(self):
        """Initialize the web driver with appropriate options"""
        try:
            if self.browser == 'chrome':
                options = Options()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                self.driver = webdriver.Chrome(options=options)
            elif self.browser == 'firefox':
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument('--headless')
                self.driver = webdriver.Firefox(options=options)
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
                
            self.driver.implicitly_wait(10)
            logger.info(f"Successfully initialized {self.browser} driver")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}")
            return False
    
    def login(self, blackboard_url, username=None, password=None):
        """Handle login to Blackboard"""
        try:
            logger.info("Navigating to Blackboard login page")
            self.driver.get(blackboard_url)
            
            # Wait for login form to appear
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Look for common login form elements
            username_field = None
            password_field = None
            
            # Try different possible selectors for username field
            possible_username_selectors = [
                'input[name="user_id"]',
                'input[name="username"]',
                'input[id="user_id"]',
                'input[id="username"]',
                'input[type="text"]'
            ]
            
            for selector in possible_username_selectors:
                try:
                    username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                logger.warning("Could not find username field automatically")
                logger.info("Please log in manually and press Enter when ready...")
                input()
                return True
            
            # Try different possible selectors for password field
            possible_password_selectors = [
                'input[name="password"]',
                'input[id="password"]',
                'input[type="password"]'
            ]
            
            for selector in possible_password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.warning("Could not find password field automatically")
                logger.info("Please log in manually and press Enter when ready...")
                input()
                return True
            
            # If we found both fields and have credentials, attempt login
            if username and password:
                logger.info("Attempting automatic login...")
                username_field.clear()
                username_field.send_keys(username)
                password_field.clear()
                password_field.send_keys(password)
                
                # Look for submit button
                submit_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'input[value*="Login"]',
                    'input[value*="Sign"]',
                    'button:contains("Login")',
                    'button:contains("Sign")'
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if submit_button:
                    submit_button.click()
                    time.sleep(3)
                else:
                    logger.warning("Could not find submit button, please log in manually")
                    input("Press Enter when logged in...")
            else:
                logger.info("No credentials provided, please log in manually")
                input("Press Enter when logged in...")
            
            # Wait for successful login (look for dashboard or course list)
            try:
                wait.until(lambda driver: "Welcome" in driver.title or "Dashboard" in driver.title or "Courses" in driver.title)
                logger.info("Successfully logged in to Blackboard")
                return True
            except TimeoutException:
                logger.warning("Login status unclear, continuing anyway...")
                return True
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def get_courses(self):
        """Get list of available courses"""
        courses = []
        try:
            logger.info("Searching for course list...")
            
            # Try different possible selectors for course list
            course_selectors = [
                'div[id*="course"] a',
                'div[class*="course"] a',
                'a[href*="course"]',
                'div[class*="course-list"] a',
                'ul[class*="course"] a'
            ]
            
            for selector in course_selectors:
                try:
                    course_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if course_elements:
                        for element in course_elements:
                            href = element.get_attribute('href')
                            text = element.text.strip()
                            if href and text and 'course' in href.lower():
                                courses.append({
                                    'name': text,
                                    'url': href,
                                    'element': element
                                })
                        if courses:
                            break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not courses:
                logger.warning("Could not automatically find courses")
                logger.info("Please navigate to your course list manually")
                input("Press Enter when ready to continue...")
                
                # Try to get current page content
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Look for any links that might be courses
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href and text and ('course' in href.lower() or 'course' in text.lower()):
                        courses.append({
                            'name': text,
                            'url': href,
                            'element': None
                        })
            
            logger.info(f"Found {len(courses)} courses")
            return courses
            
        except Exception as e:
            logger.error(f"Failed to get courses: {e}")
            return []
    
    def get_course_content(self, course_url):
        """Get content structure of a specific course"""
        try:
            logger.info(f"Accessing course: {course_url}")
            self.driver.get(course_url)
            time.sleep(2)
            
            # Look for course menu/navigation
            menu_selectors = [
                'ul[id*="menu"]',
                'ul[class*="menu"]',
                'div[id*="nav"]',
                'div[class*="nav"]',
                'ul[class*="nav"]'
            ]
            
            menu_items = []
            for selector in menu_selectors:
                try:
                    menu_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if menu_elements:
                        for element in menu_elements:
                            links = element.find_elements(By.TAG_NAME, 'a')
                            for link in links:
                                text = link.text.strip()
                                href = link.get_attribute('href')
                                if text and href:
                                    menu_items.append({
                                        'name': text,
                                        'url': href,
                                        'type': 'menu_item'
                                    })
                        if menu_items:
                            break
                except Exception:
                    continue
            
            # Look for content areas
            content_selectors = [
                'div[id*="content"]',
                'div[class*="content"]',
                'div[id*="main"]',
                'div[class*="main"]'
            ]
            
            content_items = []
            for selector in content_selectors:
                try:
                    content_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if content_elements:
                        for element in content_elements:
                            links = element.find_elements(By.TAG_NAME, 'a')
                            for link in links:
                                text = link.text.strip()
                                href = link.get_attribute('href')
                                if text and href:
                                    content_items.append({
                                        'name': text,
                                        'url': href,
                                        'type': 'content_item'
                                    })
                        if content_items:
                            break
                except Exception:
                    continue
            
            return {
                'menu_items': menu_items,
                'content_items': content_items
            }
            
        except Exception as e:
            logger.error(f"Failed to get course content: {e}")
            return {'menu_items': [], 'content_items': []}
    
    def get_grades(self, course_url):
        """Attempt to access grades for a specific course"""
        try:
            logger.info("Attempting to access grades...")
            
            # Navigate to course
            self.driver.get(course_url)
            time.sleep(2)
            
            # Look for grades link
            grade_selectors = [
                'a[href*="grade"]',
                'a[href*="Grade"]',
                'a:contains("Grade")',
                'a:contains("grade")',
                'a[title*="Grade"]',
                'a[title*="grade"]'
            ]
            
            grades_link = None
            for selector in grade_selectors:
                try:
                    grades_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if grades_link:
                logger.info("Found grades link, clicking...")
                grades_link.click()
                time.sleep(3)
                
                # Now try to extract grade information
                return self.extract_grades()
            else:
                logger.warning("Could not find grades link automatically")
                logger.info("Please navigate to grades manually")
                input("Press Enter when you're on the grades page...")
                return self.extract_grades()
                
        except Exception as e:
            logger.error(f"Failed to get grades: {e}")
            return {}
    
    def extract_grades(self):
        """Extract grade information from the current page"""
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for common grade table structures
            grade_tables = soup.find_all('table')
            grades = []
            
            for table in grade_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        if any('grade' in cell.lower() or 'score' in cell.lower() or '%' in cell for cell in row_data):
                            grades.append(row_data)
            
            # Also look for grade information in other formats
            grade_divs = soup.find_all('div', class_=lambda x: x and ('grade' in x.lower() or 'score' in x.lower()))
            for div in grade_divs:
                text = div.get_text(strip=True)
                if text:
                    grades.append(['div_content', text])
            
            return {
                'grades': grades,
                'page_title': self.driver.title,
                'url': self.driver.current_url
            }
            
        except Exception as e:
            logger.error(f"Failed to extract grades: {e}")
            return {}
    
    def save_data(self, data, filename='blackboard_data.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        logger.info("Scraper closed")

def main():
    parser = argparse.ArgumentParser(description='Scrape Blackboard for course information and grades')
    parser.add_argument('url', help='Blackboard base URL')
    parser.add_argument('--username', help='Username for automatic login')
    parser.add_argument('--password', help='Password for automatic login')
    parser.add_argument('--browser', choices=['chrome', 'firefox'], default='chrome', help='Browser to use')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--output', default='blackboard_data.json', help='Output JSON file')
    
    args = parser.parse_args()
    
    scraper = BlackboardScraper(headless=args.headless, browser=args.browser)
    
    try:
        if not scraper.setup_driver():
            logger.error("Failed to setup driver")
            return
        
        if not scraper.login(args.url, args.username, args.password):
            logger.error("Failed to login")
            return
        
        # Get courses
        courses = scraper.get_courses()
        
        all_data = {
            'scraped_at': datetime.now().isoformat(),
            'courses': [],
            'grades': {}
        }
        
        # Process each course
        for course in courses[:5]:  # Limit to first 5 courses for demo
            logger.info(f"Processing course: {course['name']}")
            
            course_data = {
                'name': course['name'],
                'url': course['url'],
                'content': scraper.get_course_content(course['url']),
                'grades': scraper.get_grades(course['url'])
            }
            
            all_data['courses'].append(course_data)
            all_data['grades'][course['name']] = course_data['grades']
            
            # Save progress
            scraper.save_data(all_data, args.output)
            
            time.sleep(2)  # Be respectful
        
        logger.info("Scraping completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
