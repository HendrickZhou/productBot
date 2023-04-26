import json
import requests
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import crud
import llm
from scrapping.scrap_exception import *
from util import run_once
import scrapping.logging_config as logging_config
import logging

def scrap(url,con):
    error_flag=False
    # setup headless chrome and selenium driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.page_load_strategy='none'
    chrome_path= ChromeDriverManager().install() # this is safe since it will use cache
    chrome_servie = Service(chrome_path)
    driver = Chrome(options=options, service=chrome_servie)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(5)

    # handle invalid url
    try:
        driver.get(url)
        time.sleep(15)
    except Exception as e:
        logging.error("url invalid")
        driver.quit()
        return SITE_NULL_CONTENT

    # import pdb;pdb.set_trace()

    # scrapping for details
    try:
        main_tag = driver.find_element(By.TAG_NAME, 'main')
    except Exception as e:
        logging.error("main tag doesn't exist, it's probably a corrupted website")
        driver.quit()
        return SITE_NULL_CONTENT

    try:
        product_details = main_tag.find_element(By.XPATH, "//*[contains(@class,'ProductDetailPage__right')]").text
    except Exception as e:
        logging.error("product_detail section not found")
        driver.quit()
        return SITE_MISSING_CRITICAL_CONTENT
    
    # import pdb;pdb.set_trace()
    # None critical exception
    try:
        # import pdb;pdb.set_trace()
        product_rate_overview_code = main_tag.find_element(By.XPATH, ".//span[contains(@itemprop, 'ratingValue')]")
        product_rate_overview = float(product_rate_overview_code.get_attribute('innerText'))
    except Exception as e:
        logging.warning("rate overview section not found")
        logging.warning("continue without rating")
        product_rate_overview = None
        
    try:
        product_fit_img = main_tag.find_element(By.XPATH, ".//*[contains(@class, 'RatingSliderImage')]")
        product_fit_overview = product_fit_img.find_element(By.TAG_NAME, 'img').get_attribute('title')
    except Exception as e:
        logging.warning("product_fit_overview_code not found")
        logging.warning("continue without fitting overview")
        product_fit_overview = None

    # save to database
    product_id = url.split('/')[-1]
    organized_tuple = organize_pdp_mixed_with_llm_and_manual(product_details,product_rate_overview, product_fit_overview)
    crud.ADD_PRODUCT(con, product_id, *organized_tuple)

    ##############################
    # Step2 scrapping for reviews
    try:
        product_reviews_section = main_tag.find_element(By.ID,"c-product__reviews--ratings")
    except Exception:
        logging.warning("not review section, stop scrapping review section")
        driver.quit()
        return SITE_MISSING_CONTENT

    try:
        review_blocks = product_reviews_section.find_elements(By.XPATH, ".//*[contains(@id, 'DisplayContentReviewID')]")
    except Exception:
        review_blocks = None
        logging.warning("not review, stop scrapping review section")
    
    if review_blocks is not None:
        for review_block in review_blocks:
            # mock click read more
            link = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable(review_block.find_element(By.NAME, "BV_TrackingTag_Review_Display_ToggleReadMore")))
            ActionChains(driver).move_to_element(link).perform()
            link.click()
            try:
                result = review_block.find_element(By.XPATH, ".//*[contains(@class,'ReviewText')]")
            except:
                logging.error("missing reviewtext, abandon current review")
                error_flag = True
                continue
            # get user avatar
            try:
                user_avatar_code = review_block.find_element(By.XPATH, ".//*[contains(@class, 'CustomUserContainer')]").get_attribute('outerHTML')
            except:
                error_flag = True
                logging.error("missing user information, abandon current review")
                continue
            # save it to database
            organized_review_tuple = organize_review_mixed_with_llm_and_manual(result.text, user_avatar_code)
            crud.ADD_REVIEW(con, product_id, *organized_review_tuple)
    else:
        logging.warning("no review section, won't do anything to review table")
    
    if error_flag:
        driver.quit()
        return SITE_MISSING_CONTENT
    driver.quit()

def scrap_safe(url, con):
    error_code = scrap(url, con)
    if error_code is not None:
        error_code = err_map[error_code]
        crud.ADD_ERROR_URL(con, url, error_code)

#####################
# text processing
#####################
def organize_review_mixed_with_llm_and_manual(review_text, user_avatar):
    # must be safe!
    final_user_avatar = llm.get_user_avatar(user_avatar)
    return final_user_avatar, user_avatar, review_text

def organize_pdp_mixed_with_llm_and_manual(product_details, product_rate_overview, product_fit_overview):
    # must be safe!
    product_details = preprocess_text(product_details)

    if product_rate_overview is not None:
        average_rate = product_rate_overview
    else:
        average_rate = None
    if product_fit_overview is not None:
        overall_fit = product_fit_overview
    else:
        overall_fit = ""

    product_details += ". Overall fitting " + overall_fit + ", where 0 means running small and 5 means running large"
    final_details = llm.organize_product_detail(product_details)
    return product_details, final_details, average_rate

def preprocess_text(text):
    text = text.replace('\n', ' ')
    text = text.replace('\\n', ' ')
    text = text.replace('   ', ' ')
    text = text.replace('   ', ' ')
    return text

if __name__ == "__main__":
    # try:
    #     crud.create_db()
    # except Exception:
    #     raise("can't create db")

    test_urls = []
    with open("./pdp_url.json",'r') as f:
        jo = json.load(f)
        for url in jo:
            test_urls.append(url)    

    test_case = ["https://www.jcrew.com/p/boys/categories/accessories/back-to-school-gear/kids-herschel-supply-co-pencil-case-in-camo/H0892",
            "https://www.jcrew.com/p/BM724",
            "https://www.jcrew.com/p/mixed/re-imagined/womens/BF401",]

    con = crud.connect()
    # 0-50
    # working on url #13300
    for i in range(100, len(test_urls)-100, 100):
        url = test_urls[i]
        print("******************************")
        print("working on url #" + str(i))
        print("url == " + url)

        logging.info("******************************")
        logging.info("working on url #" + str(i))
        logging.info("url == " + url) 

        try:
            scrap_safe(url,con)
        except Exception as e:
            logging.error("failed to scrap")
        else:
            logging.error("url:" + url + " scraped!")
    con.close()

    # scrap("https://www.jcrew.com/p/BB117",con)
    # con.close()