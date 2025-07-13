"""
Login to screener.in using selenium with login email and password
- then will go to https://www.screener.in/explore/ and open screen named v200 except bank
- then will open each stock and get nse code and write it to a file
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os
load_dotenv()

username = os.getenv("username")
password = os.getenv("password")
base_url = "https://www.screener.in"


class ScreenerExtractor:
    def __init__(self) -> None:
        self.driver  = webdriver.Chrome()

    def login(self):
        """
        login to screener.in using selenium with login 
        """
        try:
            self.driver.get(f"{base_url}/login/")
            print("Page loaded successfully")
            
            # Wait for page to load
            # time.sleep(3)
            
            # First, let's see what's actually on the page
            print("Current page title:", self.driver.title)
            print("Current URL:", self.driver.current_url)
            
            # Look for any form elements
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"Found {len(forms)} forms on the page")
            
            # Look for all input elements
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"Found {len(inputs)} input elements:")
            for i, inp in enumerate(inputs):
                print(f"  Input {i}: type={inp.get_attribute('type')}, id={inp.get_attribute('id')}, name={inp.get_attribute('name')}, placeholder={inp.get_attribute('placeholder')}")
            
            # Look for all button elements
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(buttons)} button elements:")
            for i, btn in enumerate(buttons):
                print(f"  Button {i}: text={btn.text}, type={btn.get_attribute('type')}, id={btn.get_attribute('id')}")
            
            # Now try to find the login form elements based on what we found
            username_field = None
            password_field = None
            login_button = None
            
            # Try to find username/email field
            for inp in inputs:
                input_type = inp.get_attribute('type')
                input_id = inp.get_attribute('id')
                input_name = inp.get_attribute('name')
                input_placeholder = inp.get_attribute('placeholder')
                
                if (input_type == 'email' or 
                    'email' in (input_id or '').lower() or 
                    'username' in (input_id or '').lower() or
                    'email' in (input_placeholder or '').lower()):
                    username_field = inp
                    print(f"Found username field: id={input_id}, name={input_name}")
                    break
            
            # Try to find password field
            for inp in inputs:
                input_type = inp.get_attribute('type')
                if input_type == 'password':
                    password_field = inp
                    print(f"Found password field: id={inp.get_attribute('id')}, name={inp.get_attribute('name')}")
                    break
            
            # Try to find login button
            for btn in buttons:
                btn_text = btn.text.lower()
                btn_type = btn.get_attribute('type')
                btn_id = btn.get_attribute('id')
                # Look for the LOGIN button specifically
                if ('login' in btn_text or btn_type == 'submit') and btn_text == 'login':
                    login_button = btn
                    print(f"Found login button: text={btn.text}, type={btn_type}, id={btn_id}")
                    break
            
            # If we found all elements, try to login
            if username_field and password_field and login_button:
                print("Attempting to login...")
                
                # Clear fields first
                username_field.clear()
                password_field.clear()
                
                # Fill in credentials
                username_field.send_keys(username)
                password_field.send_keys(password)
                
                # Wait a moment for the form to be ready
                # time.sleep(1)
                
                # Try to click the login button
                try:
                    login_button.click()
                    print("Login button clicked")
                    
                    # Wait for login to complete and redirect
                    wait = WebDriverWait(self.driver, 1)
                    try:
                        # Wait for URL to change from login page
                        wait.until(lambda driver: driver.current_url != f"{base_url}/login/")
                        print(f"Successfully redirected to: {self.driver.current_url}")
                        
                        # Additional wait to ensure page is fully loaded
                        time.sleep(3)
                        
                    except Exception as wait_error:
                        print(f"Login redirect timeout: {wait_error}")
                        print(f"Current URL after login attempt: {self.driver.current_url}")
                        
                except Exception as e:
                    print(f"Could not click login button: {e}")
                    # Try alternative approach - submit the form
                    try:
                        username_field.submit()
                        print("Form submitted via submit()")
                        
                        # Wait for login to complete
                        wait = WebDriverWait(self.driver, 1)
                        try:
                            wait.until(lambda driver: self.driver.current_url != f"{base_url}/login/")
                            print(f"Successfully redirected to: {self.driver.current_url}")
                            time.sleep(1)
                        except Exception as wait_error:
                            print(f"Login redirect timeout: {wait_error}")
                            
                    except Exception as e2:
                        print(f"Could not submit form: {e2}")
            else:
                print("Could not find all required login elements:")
                print(f"  Username field: {'Found' if username_field else 'Not found'}")
                print(f"  Password field: {'Found' if password_field else 'Not found'}")
                print(f"  Login button: {'Found' if login_button else 'Not found'}")
                
                # Try to find any submit button that might work
                print("Trying to find any working submit button...")
                for i, btn in enumerate(buttons):
                    if btn.get_attribute('type') == 'submit':
                        try:
                            print(f"Trying button {i}: {btn.text}")
                            btn.click()
                            print(f"Successfully clicked button {i}")
                            break
                        except Exception as e:
                            print(f"Button {i} not clickable: {e}")
            
        except Exception as e:
            print(f"Error during login: {e}")
            import traceback
            traceback.print_exc()
        
        return self.driver

    def is_logged_in(self):
        """
        Check if user is logged in by looking for logout link or user profile elements
        """
        try:
            # Look for logout link or user profile elements
            logout_selectors = [
                "//a[contains(text(), 'Logout')]",
                "//a[contains(text(), 'Sign Out')]",
                "//div[contains(@class, 'user')]",
                "//span[contains(@class, 'user')]"
            ]
            
            for selector in logout_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        print("User is logged in")
                        return True
                except:
                    continue
            
            # Check if we're on login page
            if "/login/" in self.driver.current_url:
                print("User is not logged in (on login page)")
                return False
                
            print("Could not determine login status")
            return False
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False

    def extract_screen_data(self,screen,extractor):
        screen.open_screen() 
        
class Screen:
    def __init__(self,driver,screen_url,extractor) -> None:
        self.driver = driver
        self.url = f"{base_url}/{screen_url}"
        # self.url = f"{base_url}/screens/2940605/v200-except-bank/"
        self.extractor = extractor

        
    def open_screen(self):    
        """
        open screen named v200 except bank with pagination
        """

        print(f"Navigating to screen URL: {self.url}")
        self.driver.get(self.url)
        
        # Wait for page to load and verify we're on the correct page
        wait = WebDriverWait(self.driver, 10)
        try:
            # Wait for the page to load (look for table or specific elements)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.data-table")))
            print("Successfully loaded the screen page")
            print(f"Current URL: {self.driver.current_url}")
            
            # Check if we're still on login page (authentication failed)
            if "/login/" in self.driver.current_url:
                print("ERROR: Still on login page. Authentication may have failed.")
                return
                
        except Exception as e:
            print(f"Error loading screen page: {e}")
            print(f"Current URL: {self.driver.current_url}")
            
            # Check if we need to login again
            if "/login/" in self.driver.current_url:
                print("Redirected to login page. Trying to login again...")
                self.driver = ScreenerExtractor().login()
                # Try to navigate to the screen again
                self.driver.get(self.url)
                time.sleep(3)
        
        page_number = 1
        all_nse_codes = []
        
        while True:
            print(f"Processing page {page_number}...")
            
            # Process current page
            page_nse_codes = self.extractor.extract(self.driver)
            if page_nse_codes:
                all_nse_codes.extend(page_nse_codes)
            
            # Try to find next page link
            try:
                next_page_xpath = f"//a[normalize-space()='{page_number + 1}']"
                print(f"Next page XPath: {next_page_xpath}")
                next_page_link = self.driver.find_element(By.XPATH, next_page_xpath)
                print(f"Found next page link: {page_number + 1}")
                
                # Click on next page
                next_page_link.click()
                time.sleep(3)  # Wait for page to load
                
                page_number += 1
                
            except Exception as e:
                print(f"No more pages available. Last page was {page_number} {e}")
                break
        file_name = [part for part in self.url.split('/') if part.strip()!=""][-1]
        file_name = f"{file_name}.txt"
        self.extractor.write_to_file(all_nse_codes,file_name=file_name)

        

class ExtractorBase:
    def extract(self,driver):
        raise NotImplemented("Implement Extractor logic") 
    def write_to_file(self,data,file_name):
        raise NotImplemented("Extract file writing strategry")

class ExtractNSECode(ExtractorBase):
    pass 


class UrlNSECodeStrategy(ExtractNSECode):

    def extract(self,driver):
        """
        Iterate through table with class data-table text-nowrap striped mark-visited no-scroll-right
        for each tr having data-row-company-id attribute naviagate to td having href /company/* 
        get the nse code if present from the detail page
        returns list of dictionaries with company info and nse codes
        """
        try:
            print("Looking for the data table...")
            
            # Wait for the table to load
            time.sleep(3)
            
            # Find the table with the specified class
            table = driver.find_element(By.CSS_SELECTOR, "table.data-table.text-nowrap.striped.mark-visited.no-scroll-right")
            print("Found the data table")
            
            # Find all rows with data-row-company-id attribute
            rows = table.find_elements(By.CSS_SELECTOR, "tr[data-row-company-id]")
            print(f"Found {len(rows)} company rows")
            
            # First, collect all company URLs and names
            company_data = []
            for i, row in enumerate(rows):
                try:
                    company_link = row.find_element(By.CSS_SELECTOR, "td a[href*='/company/']")
                    company_url = company_link.get_attribute('href')
                    company_name = company_link.text.strip()
                    company_data.append({
                        'name': company_name,
                        'url': company_url
                    })
                    print(f"Collected: {company_name} - {company_url}")
                except Exception as e:
                    print(f"Error collecting data from row {i+1}: {e}")
                    continue
            
            print(f"Successfully collected {len(company_data)} companies")
            
            nse_codes = []
            
            # Now process each company URL
            for i, company in enumerate(company_data):
                try:
                    print(f"Processing company {i+1}/{len(company_data)}: {company['name']}")
                    
                    # Look for NSE code on the company page
                    nse_code = None
                    
                    
                    # If still not found, try to extract from URL or page title
                    if not nse_code:
                        # Sometimes the NSE code is in the URL
                        if '/company/' in company['url']:
                            url_parts = [c for c in company['url'].split('/') if c.strip()!=""]
                            if len(url_parts) > 2:
                                if "consolidated" in url_parts[-1]:
                                    potential_code = url_parts[-2]
                                else:
                                    potential_code = url_parts[-1]

                                if len(potential_code) <= 10:  # NSE codes are usually short
                                    try:
                                        int(nse_code)
                                    except Exception as ex: # nse codes are not numeric only
                                        nse_code = potential_code

                                print(f"  Extracted NSE code from URL: {nse_code} {potential_code}")
                        else:
                            print('not a valid url')
                    
                    if nse_code:
                        nse_codes.append({
                            'company': company['name'],
                            'nse_code': nse_code,
                            'url': company['url']
                        })
                    else:
                        print(f"  No NSE code found for {company['name']}")
                    
                except Exception as e:
                    print(f"  Error processing company {company['name']}: {e}")
                    continue
            
            print(f"Found {len(nse_codes)} NSE codes on this page")
            return nse_codes
                
        except Exception as e:
            print(f"Error in get_nse_code: {e}")
            import traceback
            traceback.print_exc()
            return []


    def write_to_file(self,data,file_name):
                
        # Write all collected NSE codes to file
        all_nse_codes = sorted(data,key=lambda x: x["nse_code"])
        print(f"total nse code found {all_nse_codes}")
        if all_nse_codes:
            nse_codes_str = ", ".join([f"NSE:{code['nse_code']}" for code in all_nse_codes])
            with open(file_name, 'w') as f:
                f.write(nse_codes_str)
            print(f"Total NSE codes collected: {len(all_nse_codes)}")
        else:
            print("No NSE codes found across all pages")

class PageDetailNSECodeStrategy(ExtractNSECode):
    def extract(self,driver):
        return super().extract()
    

    
def main():

    
    # # Login first
    # login(driver)
    
    
    # print("Login successful! Proceeding to screen...")
    
    # # Call the other functions
    # open_screen(driver)
    screen_extractor = ScreenerExtractor()
    driver = screen_extractor.login()
    nse_code_screens = [
        # "screens/2940605/v200-except-bank/"
        "screens/2940613/v200-refined/"
    ]
    for screen in nse_code_screens:
        extractor = UrlNSECodeStrategy()
        screener = Screen(driver=driver,screen_url=screen,extractor=extractor)
        
        screen_extractor.extract_screen_data(screener,extractor)
    
    # Keep browser open until user presses Enter
    # input("Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    main()
