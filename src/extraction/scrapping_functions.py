import requests
import time
import logging
import pandas as pd

from transformers import pipeline
from bs4 import BeautifulSoup as BeautifulSoup
from transformers import AutoTokenizer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement


class Scrapping:
    def __init__(self, url):
        """
        Initialize scrapping .

        :param url: The base URL for the API.
        """
        self.url = url
        self.driver = None


    def setup_driver(self):
        """
        Set up and return the Chrome WebDriver instance.
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    def scrap(self, main):
        """
        Scrape product names and links from the given main HTML element.

        :param main: The main element containing the product list.
        :return: A DataFrame with product names and href links.
        """
        # Find product list inside the HTML
        all_lists = main.find_elements(By.TAG_NAME, "ul")
        logging.info(f"Total products {len(all_lists)}")

        if len(all_lists) > 1:
            first_list = all_lists[0]  # Select only the first list

            # Find all elements within the first list
            lista_elementos = first_list.find_elements(By.TAG_NAME, "li")  # Replace "li" with the tag of list items
            logging.info("Products added")

        else:
            lista_elementos = main.find_elements(By.TAG_NAME, "li")

        # Product names
        names = []

        # Product href
        links = []

        # Get product list from webpages
        for i in lista_elementos:
            try:
                link = i.find_element(By.TAG_NAME, "a")

                # Get the href
                href = link.get_attribute("href")
                logging.info(f"Href: {href}")

                # Coffee name
                nombre = i.find_elements(By.TAG_NAME, "h3")

                if not nombre:  # If no <h3> elements are found
                    nombre = i.find_elements(By.TAG_NAME, "p")

                if len(nombre) > 1:
                    # Check and assign the text from the first or second <h3> element
                    nombre = nombre[0].text.strip() if nombre[0].text else nombre[1].text.strip()
                elif len(nombre) == 1:
                    # If only one <h3> element exists, assign its text
                    nombre = nombre[0].text.strip()
                else:
                    # If no <h3> elements exist, handle the case gracefully
                    logging.info("No <h3> elements found.")
                    continue  # Skip to the next item in the list

                names.append(nombre)
                links.append(href)

                logging.info(f"Nombre: {nombre}")

            except Exception as e:
                logging.warning(f"Error processing item: {e}")
                continue

        df = pd.DataFrame({
            'names': names,
            'href': links
        })

        return df
    

    def get_prod_list(self):
        """
        Open the webpage, scrape the product list, and return a DataFrame.

        :return: A DataFrame containing product names and URLs.
        """
        self.setup_driver()

        driver = self.driver

        driver.get(self.url)

        # Wait for the page to load (adjust sleep time as needed)
        time.sleep(5)

        # Use the main HTML tag
        # main = 

        try:
            # Try to find the <main> tag first
            main = driver.find_element(By.TAG_NAME, "main")
            logging.info("Main element found in HTML")

        except Exception:
            # If <main> is not found, fall back to <body>
            main = driver.find_element(By.TAG_NAME, "body")
            logging.info("Body element found in HTML")

        except Exception:
            return "Web page cannot be scrapped"

        try:
            df = self.scrap(main)

        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            df = pd.DataFrame()

        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Browser closed.")

        return df
