import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from urllib.parse import quote_plus


class AmazonBridge:
    def __init__(self, driver):
        self.driver = driver

    def scrape_search_results(self):
        return self.driver.execute_script(
            """
            return [...document.querySelectorAll(".s-result-item")].map((d, i) => {
                let data = {...d.dataset}
                try { data['url'] = d.querySelector('a')['href']; } catch(err) {}
                try { data['img'] = d.querySelector('img')['src']; } catch(err) {}
                try { data['title'] = d.querySelector('h2').innerText; } catch(err) {}
                try { data['is_sponsored'] = d.querySelector('[data-component-type="sp-sponsored-result"]') != null; } catch(err) {}
                try { data['stars'] = d.querySelector('[aria-label*="out of 5 stars"]').ariaLabel; } catch(err) {}
                try { data['ratings'] = d.querySelector('[aria-label*="out of 5 stars"] + span').ariaLabel; } catch(err) {}
                try { data['price'] = d.querySelector('.a-price .a-offscreen').innerText; } catch(err) {}
                try { data['old_price'] = d.querySelector('.a-price[data-a-strike="true"] .a-offscreen').innerText; } catch(err) {}
                try { data['price_range'] = d.querySelectorAll('.a-price-range .a-price .a-offscreen')[0].innerText + " - " + d.querySelectorAll('.a-price-range .a-price .a-offscreen')[1].innerText } catch(err) {}
                try { data['free_shipping'] = d.querySelector('[aria-label*="shipping"]') != null; } catch(err) {}
                try { data['is_prime'] = d.querySelector('.a-icon-prime') != null; } catch(err) {}
                return data;
                });
        """
        )  # noqa: E501

    def force_page_contents_load(self):
        self.driver.execute_script(
            """
            window.scrollTo({
                top: document.body.scrollHeight,
                left: 0,
                behavior: 'smooth'
            });"""
        )
        time.sleep(2)
        self.driver.execute_script(
            """
            window.scrollTo({
                top: document.body.scrollHeight,
                left: 0,
                behavior: 'smooth'
            });"""
        )
        time.sleep(2)
        self.driver.execute_script(
            "document.querySelectorAll('.a-carousel-goto-nextpage').forEach(e => e.click())"
        )
        time.sleep(1)
        self.driver.execute_script(
            "document.querySelectorAll('.a-carousel-goto-nextpage').forEach(e => e.click())"
        )
        time.sleep(1)
        self.driver.execute_script(
            "document.querySelectorAll('.a-carousel-goto-nextpage').forEach(e => e.click())"
        )
        time.sleep(2)

    # This needs a lot of work.
    def scrape_suggested_products(self):
        return self.driver.execute_script(
            """                
                [...document.querySelectorAll(".a-carousel-card:not(.vse-video-card)")].map((d, i) => {
                    let section = d.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode
                    let data = {}
                    try { data['title'] = d.querySelector('img')['alt']; } catch(err) {}
                    try { data['title'] = d.querySelector('.p13n-sc-truncated').innerText; } catch(err) {}
                    /*
                    try { data['asin'] = JSON.parse(d.querySelector("div.p13n-asin").dataset['p13nAsinMetadata'])['asin'] } catch(err) {}
                    try { data['url'] = d.querySelector('a.a-link-normal')['href']; } catch(err) {}
                    try { data['img'] = d.querySelector('img')['src']; } catch(err) {}
                    try { 
                        try { section.querySelector("h2 a").remove() } catch(err) {}
                        data['section_title'] = section.querySelector("h2").innerText;
                    } catch(err) {}
                    try { data['is_sponsored'] = section.innerText.indexOf("Sponsored") != -1 } catch(err) {}

                    try { data['stars'] = d.querySelector('[title*="out of 5 stars"]').title; } catch(err) {}
                    try { data['review_count'] = d.querySelector('[[title*="out of 5 stars"] .a-size-small').innerText; } catch(err) {}

                    if(!data['stars']) {
                        try { data['stars'] = d.querySelector('.adReviewLink i').classList[2]; } catch(err) {}
                    }
                    if(!data['review_count']) {
                        try { data['review_count'] = d.querySelector('.adReviewLink span').innerText; } catch(err) {}
                    }
                    
                    try { data['best_seller'] = d.querySelector('.p13n-best-seller').innerText; } catch(err) {}
                    */
                    try { data['price'] = d.querySelector('.p13n-sc-price,.a-color-price').innerText.trim(); } catch(err) {}
                    try { data['free_shipping'] = d.innerText.indexOf("FREE shipping") != -1 } catch(err) {}
                    try { data['is_prime'] = d.querySelector('.a-icon-prime') != null; } catch(err) {}
                    data['obj'] = d
                    return data;
                });
                """
        )  # noqa: E501

    def scrape_raw_carousel_data(self):
        self.driver.execute_script("""
        [...document.querySelectorAll("[data-a-carousel-options*='}']")].map(d => {
            return {...d.dataset}
        })
        """)

    def get_data(self):
        parsed = urlparse(self.driver.current_url)
        if parsed.path.startswith("/s"):
            return {
                "page_type": "search",
                "query": self.driver.find_element_by_css_selector(
                    ".nav-input"
                ).get_attribute("value"),
                "recommendations": self.scrape_search_results(),
            }
        else:
            return {
                "page_type": "product",
                "title": self.driver.find_element_by_css_selector("h1").text,
                "recommendations": self.scrape_suggested_products(),
                "carousels": self.scrape_raw_carousel_data()
            }

    def run(self, url):
        self.driver.get(url)
        self.force_page_contents_load()

        return self.get_data()