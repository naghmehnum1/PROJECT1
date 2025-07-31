import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from api import read_ads, read_ad

from models import Ad, Base 

app = FastAPI()


DATABASE_URL = "postgresql://postgres:1234@localhost:5432/divar?client_encoding=utf8"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app.get("/ads/")(read_ads)
app.get("/ads/{ad_id}")(read_ad)
                        
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def scroll_to_end(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    while scroll_attempts < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))  # زمان کمتر بین اسکرول‌ها
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        last_height = new_height

def scrape_ad_details(driver, wait):
    details = {
        'publish_date': '', 'area': '', 'price': '', 'description': '',
        'num_rooms': '', 'meterage': '', 'year_built': ''
    }
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.kt-description-row__text")))

        #  گرفتن تاریخ انتشار و منطقه
        try:
            location_element = driver.find_element(By.CSS_SELECTOR, "div.kt-page-title__subtitle.kt-page-title__subtitle--responsive-sized")
            full_text = location_element.text.strip()
            if ' در ' in full_text:
                publish_part, area_part = full_text.split(' در ', 1)
                details['publish_date'] = publish_part.strip()
                details['area'] = area_part.strip()
            else:
                details['publish_date'] = full_text.strip()
                details['area'] = ''
        except NoSuchElementException:
            details['publish_date'] = ''
            details['area'] = ''

        #  قیمت
        try:
            price_elements = driver.find_elements(By.CSS_SELECTOR, "p.kt-unexpandable-row__value")
            titles = driver.find_elements(By.CSS_SELECTOR, "p.kt-unexpandable-row__title")
            details['price'] = ''
            for title, value in zip(titles, price_elements):
                if title.text.strip() == "قیمت کل":
                    details['price'] = value.text.strip()
                    break
        except NoSuchElementException:
            details['price'] = ''

        # توضیحات
        try:
            details['description'] = driver.find_element(By.CSS_SELECTOR, "p.kt-description-row__text.kt-description-row__text--primary").text
        except NoSuchElementException:
            details['description'] = ''

        #  متراژ، سال ساخت، اتاق
        try:
            values = driver.find_elements(By.CSS_SELECTOR, "td.kt-group-row-item.kt-group-row-item__value.kt-group-row-item--info-row")
            if len(values) >= 3:
                details['meterage'] = values[0].text.strip()
                details['year_built'] = values[1].text.strip()
                details['num_rooms'] = values[2].text.strip()
        except NoSuchElementException:
            pass

        return details
    except TimeoutException:
        print(" بارگذاری جزئیات آگهی زمان‌بر بود.")
        return None

def main():
    driver = setup_driver()
    db = SessionLocal()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://divar.ir/s/tehran/buy-residential")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.kt-post-card__action")))
        scroll_to_end(driver)

        ad_elements = driver.find_elements(By.CSS_SELECTOR, "a.kt-post-card__action")

        for ad_element in ad_elements:
            try:
                link = ad_element.get_attribute("href")
                title = ad_element.find_element(By.CSS_SELECTOR, "h2.kt-post-card__title").text

                if db.query(Ad).filter(Ad.link == link).first():
                    continue

                driver.execute_script("window.open(arguments[0], '_blank');", link)
                driver.switch_to.window(driver.window_handles[1])

                ad_details = scrape_ad_details(driver, wait)

                if ad_details:
                    new_ad = Ad(
                        link=link,
                        title=title,
                        publish_date=ad_details['publish_date'],
                        area=ad_details['area'],
                        price=ad_details['price'],
                        description=ad_details['description'],
                        num_rooms=ad_details['num_rooms'],
                        meterage=ad_details['meterage'],
                        year_built=ad_details['year_built'],
                        crawled_at=datetime.utcnow() 
                    )
                    db.add(new_ad)
                    db.commit()
                    print(f"✔ آگهی ذخیره شد: {title}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(random.uniform(2, 3))  # کمی بیشتر بین آگهی‌ها صبر می‌کنه

            except IntegrityError:
                db.rollback()
                print(" لینک تکراری، رد شد.")
            except Exception as e:
                db.rollback()
                print(f" خطا در ذخیره آگهی: {e}")

    finally:
        db.close()
        driver.quit()

if __name__ == "__main__":
    main()
