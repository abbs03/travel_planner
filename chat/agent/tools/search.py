from typing import TypedDict, Annotated, Optional, Literal, Sequence
from pydantic import BaseModel, Field
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from langchain.agents import Tool
from langchain_core.tools import tool


class SearchInput(BaseModel):
    """Input Schema for Web search tool"""
    query: str = Field(description="The search query.")
    k: int = Field(default=3, description="The number of search results to return.")

def get_visible_text_from_html(html: str) -> str:
    """
    Extracts all visible text from an HTML string.
    Removes script, style, and noscript tags, and then cleans up whitespace.
    
    Args:
        html: The HTML content as a string.
        
    Returns:
        A string containing the cleaned, visible text.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    
    text = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())[:2000]

@tool(args_schema=SearchInput)
def web_search(query: str, k: int = 3) -> str:
    """
    Performs a web search on DuckDuckGo for a given query and returns the visible text
    from the top 'k' search results. Useful for getting up-to-date information,
    finding IATA airport codes, or discovering travel destinations and activities.
    """
    
    options = Options()
    #options.add_argument("--headless=new")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://duckduckgo.com/")
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "searchbox_input")))
        
        search_box.send_keys(query)
        search_box.submit()
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@data-testid='result-title-a']")))
        
        links = driver.find_elements(By.XPATH, "//a[@data-testid='result-title-a']")[:k]
        urls = [link.get_attribute("href") for link in links if link.get_attribute("href")]
        
        all_results_text = []
        for url in urls:
            try:
                driver.get(url)
                time.sleep(2)  
                html = driver.page_source
                text_content = get_visible_text_from_html(html)
                all_results_text.append(f"--- Content from {url} ---\n{text_content}\n")
            except Exception as e:
                all_results_text.append(f"--- Error scraping {url}: {e} ---")
                
        return "\n\n".join(all_results_text)
    finally:
        driver.quit()
