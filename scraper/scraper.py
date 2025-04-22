"""

TLDR on how this works:
    We use click_hall() and click_ortega() to click into specific dining halls. When using click_hall, we use
    another function, click_each_meal_and_scrape() to click into every "lunch", "brunch", "dinner", and "breakfast"
    on the page. The common goal is to arrive on the final page with every single food item listed out, where we
    can then call scrape_all_items() to get the nutritional value for all the items and export it to a csv.

TODO: change filepath for csv to database folder

"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import export_to_csv
import os

import time # used for testing

opts = Options()
opts.add_argument("--headless") # turn off for debugging, hides tab
service = Service(ChromeDriverManager().install())
driver  = webdriver.Chrome(service=service, options=opts)

driver.get("https://nutrition.info.dining.ucsb.edu/NetNutrition/1#")

def main():
    halls = ["Carrillo", "De La Guerra", "Portola"]
    takeout = "Ortega"

    all_data = []
    for hall in halls:
        print(f"{hall} in progress...")
        hall_data = click_hall(driver, hall)
        
        # hall_data is a list-of-lists of (name, text) tuples if you did per-meal scrape
        # flatten it:
        flat = [item for sub in hall_data for item in sub]

        # dedupe before exporting or appending to all_data
        # flat = dedupe_results(flat)
        all_data.extend(flat)
        return_home(driver)

    print("ortega in progress....")
    ortega_data = click_ortega(driver, takeout)
    # ortega_data = dedupe_results(ortega_data)
    all_data.extend(ortega_data)
    all_data = dedupe_results(all_data)


    # create filepath
    this_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(this_dir, os.pardir))
    db_dir = os.path.join(project_root, 'database')

    # now all_data has no duplicate names across halls/meals
    export_to_csv(all_data, db_dir, mode='w', filename='full_export.csv')


# function that clicks into each item on the page and scrapes the nutrition label
# used once we arrive at the page that lists all the items served during breakfast, brunch, lunch, or dinner
def scrape_all_items(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cbo_nn_itemHover")))
    items = driver.find_elements(By.CSS_SELECTOR, "a.cbo_nn_itemHover")
    count = len(items)

    results = []
    # sub range in for count when actually runnning it
    for i in range(1):
        # re-find anchors
        items = driver.find_elements(By.CSS_SELECTOR, "a.cbo_nn_itemHover")
        item = items[i]

        name = item.text
        item.click()  # this fires the JS to open the nutrition label

        # wait for nutrition label to appear
        panel = wait.until(EC.visibility_of_element_located((
            By.CSS_SELECTOR, "div#nutritionLabel")))

        nutrition_text = panel.text
        results.append((name, nutrition_text))

        close_btn = wait.until(EC.element_to_be_clickable((
            By.ID, "btn_nn_nutrition_close"
        )))
        close_btn.click()

        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div#nutritionLabel")))

    return results

# clicks into ortega specifically. it has one less page than the other dining halls
def click_ortega(driver, hall_name, timeout=5):
    """
    Finds and clicks the dining‑hall card matching `hall_name`.
    Assumes driver is already on the “all units” page.
    """
    wait = WebDriverWait(driver, timeout)
    # XPath looks for a div.card.unit containing the hall_name text
    locator = (By.XPATH,
               f"//div[contains(@class,'card unit') and .//text()[contains(.,'{hall_name}')]]")
    card = wait.until(EC.element_to_be_clickable(locator))
    card.click()

    # give the page a moment to load the next view
    # using By.LINK_TEXT because the text has an apostrophe which kinda fucks with the previous method
    wait = WebDriverWait(driver, 10)
    link = wait.until(EC.element_to_be_clickable((
        By.PARTIAL_LINK_TEXT, "Daily Menu"
    )))
    link.click()
    
    return scrape_all_items(driver)

# for the main 3 dining halls: dlg, portola, carrillo
def click_hall(driver, hall_name, timeout=5):
    wait = WebDriverWait(driver, timeout)
    # click the first page
    locator = (By.XPATH,
               f"//div[contains(@class,'card unit') and .//text()[contains(.,'{hall_name}')]]")
    card = wait.until(EC.element_to_be_clickable(locator))
    card.click()

    # click on the daily menu
    wait = WebDriverWait(driver, 10)
    link = wait.until(EC.element_to_be_clickable((
        By.PARTIAL_LINK_TEXT, "Daily Menu"
    )))
    link.click()

    rval = click_each_meal_and_scrape(driver)
    print(f"finished {hall_name}!")
    return rval

    # i = 0
    # while len(anchors) > 0:
    #     anchors[i].click()
    #     time.sleep(2)
    #     results = scrape_all_items(driver)
    #     arr_results.append(results)

    # return arr_results

# function to click into "breakfast", "lunch", and "dinner"
# calls scrape_all_items once clicked
def click_each_meal_and_scrape(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cbo_nn_menuLink")))
    total = len(driver.find_elements(By.CSS_SELECTOR, "a.cbo_nn_menuLink"))
    results = []

    for idx in range(total):
        # refind elemennts
        links = driver.find_elements(By.CSS_SELECTOR, "a.cbo_nn_menuLink")
        link = links[idx]

        link.click()
        
        # make a list of results - all meals
        result = scrape_all_items(driver)
        results.append(result)

        # go back
        back_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button[id='btn_Back*Menu Details']"
        )
        back_btn.click()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cbo_nn_menuLink")))

    return results

# function to remove duplicates
def dedupe_results(results):
    """
    Given results = [(name, text), …], return a new list
    with only the first occurrence of each `name`.
    """
    seen = set()
    clean = []
    for name, text in results:
        if name in seen:
            continue
        seen.add(name)
        clean.append((name, text))
    return clean

# go back two pages
def return_home(driver):
    back_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button[id='btn_BackmenuList1']"
        )
    back_btn.click()

    child_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
        By.XPATH,
        "//button[@id='btn_Back*Child Units']"
        ))
    )
    child_btn.click()


if __name__ == "__main__":
    main()