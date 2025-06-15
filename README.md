# Google Maps Scraper AI Agent

A smart and scalable lead-generation tool that scrapes Google Maps for business data, extracts emails from websites using a hybrid Scrapy Crawler and Gemini AI pipeline, and provides a clean CSV output—all within an interactive Streamlit interface.

---

## 🧠 What It Does

* Scrapes business **name**, **address**, **website**, **emails** and more from Google Maps based on search queries.
* Uses the website/domain collected from Google Maps to extract **emails** using:

  * A **Scrapy Email Crawler**
  * **Gemini API** to enrich results and extract hard-to-find emails
* Automatically **cleans, deduplicates**, and **preprocesses** the final dataset.
* Presents results in a **Pandas DataFrame** with export options.

---

## ⚙️ Tech Stack

* `Streamlit`: GUI interface
* `Selenium`: Browser automation for Google Maps
* `BeautifulSoup`: HTML parsing
* `Scrapy`: Custom email crawler
* `Google Gemini API`: AI-powered fallback for email extraction and data enrichment
* `pandas`, `re`, `json`: Data handling & cleanup

---

## 🚀 How It Works

### Step 1: User Input

In the Streamlit GUI, the user provides:

* **Search Query** (e.g., "Coffee Shops")
* **Search Location** (e.g., "New York, USA")
* **Number of Leads** to collect

### Step 2: Google Maps Automation

Selenium automates a browser session to search Google Maps and scrape visible business cards.

### Step 3: Website Scraping

Each business website and its domain is collected from Google Maps and scraped using Scrapy to find any public-facing emails.

### Step 4: AI Email Completion (Fallback)

If Scrapy fails, the website content is passed to Gemini via prompt engineering to extract potential emails searching the web.

### Step 5: Cleanup & Display

* Removes duplicate entries based on name, website, and emails
* Outputs to a DataFrame in the Streamlit interface
* Enables **CSV export** with a click

---

## ✨ Features

* Hybrid Email Extraction: Scrapy + Gemini AI fallback.
* Custom Search Query & Lead Targeting.
* Data Preprocessing & Deduplication.
* Interactive Streamlit UI.
* CSV Export.

---

## 📸 Demo Screenshots
![Screenshot (57)](https://github.com/user-attachments/assets/9a8bf487-1182-48f4-8191-825a78dd07e7)
![Screenshot (59)](https://github.com/user-attachments/assets/88a45070-5ce0-41f4-abc7-42426b40b027)
![Screenshot (62)](https://github.com/user-attachments/assets/f07ab4cc-24b6-44ae-b679-be8c529cb4e8)
---

## 🔍 Code Snippets & Function Highlights

* `scrape_google_maps()` — Automates search in Google Maps
```python
def scrape_google_maps(query, location, num_results):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    st.write('Starting Name & URL Scrapping...')
    search_query = f"{query} in {location}"
    search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
    driver.get(search_url)
    sleep(5)

    scroll_window(driver, search_query, num_results)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listings = soup.find_all('div', class_='Nv2PK THOPZb CpccDe')

    local_info = []
    for listing in listings:
        a_tag = listing.find('a', class_='hfpxzc')
        name = a_tag.get('aria-label', '').strip()
        url = a_tag.get('href', '').strip()

        info_dict = {
            'name': name,
            'url': url,
        }
        local_info.append(info_dict)
    st.write('Starting Business Info Scrapping...')
    return scrape_business_details(driver, local_info)
```

* `scrape_business_details()` — Parses Name, Address and Website to get business data
```python
def scrape_business_details(driver, local_info):
    progress_bar = st.progress(0, text="Scraping in Progress...")
    business_info = []
    for info_dict in local_info:
        name = info_dict['name']
        map_url = info_dict['url']

        driver.get(map_url)
        sleep(5)

        address, website = '', ''
        email_data = {'emails': []}
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        business_div = soup.find_all(
            'div', class_='Io6YTe fontBodyMedium kR99db fdkmkc')
        website_div = soup.find('a', class_='lcr4fd S9kvJb', href=True)
        address_div = soup.find('button', class_='CsEnBe')

        if business_div and website_div and address_div:
            website = website_div['href']
            address = address_div['aria-label'].strip('Address: ')
            rating = soup.find(
                'div', class_='fontDisplayLarge').get_text(strip=True)

        if website:
            ''' Just change the location and put the path where 
            you saved the Email Scraper's spiders folder '''
            email_scraper_path = r"D:\AI Automation\email_scraper\email_scraper\spiders"
            command = f"cd {email_scraper_path} && python email_scraper.py {website}"
            result = subprocess.run(command, shell=True,
                                    capture_output=True, text=True)
            if result.returncode == 0:
                #print('Output:', result.stdout)
                f = open(r'D:\AI Automation\email_scraper\email_scraper\spiders\emails.json')
                email_data = json.load(f)
            print(email_data)

        business_info_dict = {
            'name': name,
            'website': website,
            'addreess': address,
            'rating': rating,
            'emails': email_data['emails']
        }
        business_info.append(business_info_dict)
        sleep(5)
        progress_bar.progress((len(business_info)/len(local_info)),
                              text="Scraping in Progress...")

    progress_bar.empty()
    driver.close()
    return business_info
```

* `EmailSpider()` — Scrapy Spider code to extract emails from websites
```python
class EmailSpider(scrapy.Spider):
    name = 'email_spider'
    start_urls = [str(sys.argv[1])]
    allowed_domains = [urlparse(str(sys.argv[1])).netloc]
    emails_found = set()
    link_extractor = LinkExtractor()

    def parse(self, response):
        email_pattern = r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'
        self.emails_found.update(re.findall(
            email_pattern, response.text, re.IGNORECASE))
        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse)

    def close(spider, reason):
        output_data = {'emails': list(spider.emails_found)}
        with open('emails.json', 'w') as f:
            import json
            json.dump(output_data, f, indent=4)
```
* `enhance_data()` — Prompts Gemini API to retrieve missing email info
```python
def enhance_data(scraped_data):
    st.write('Enhancing data using Gemini API...')
    prompt = f"""
    I have given you a JSON data, which contains scraped business information from 
    Google Maps. You can see many of the comapany emails are missing. Your task is 
    to fillup the blank emails by searching for the company. The company name, address 
    and website are given. Only return the completed data in json format, nothing else 
    should be printed. You will also see some of the emails are crooked or temporary mail
    or they are like user@domain.org. Make sure to replace them. Again, just 
    only return the JSON data.
    
    Scraped Google Maps JSON data:
    {str(scraped_data)}
    """
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        match = re.search(r'\[\s*{.*?}\s*\]', response.text, re.DOTALL)
        data = json.loads(match.group(0))
        return data

    except Exception as e:
        return str(e)
```
---

## 📁 Folder & File Structure

```
Google-Maps-Scraper-Ai-Agent/
├── main.py                      # Main Streamlit GUI and control logic
├── requirements.txt             # Dependencies list
├── bg.jpg                       # Streamlit Background Image
├── scraper.py                   # Scraper Code for scraping data from Google Maps
├── utils.py                     # Ai enhancement and other necessary fucntions
├── email_scraper/               # Scrapy project structure
|   └── scrapy.cfg
│   └── email_scraper/        
|       ├── __init__.py
│       ├── items.py
│       ├── middlewares.py
│       ├── pipelines.py
│       ├── settings.py
│       └── spiders/
|           └── __init__.py
│           └── email_scraper.py
|           └── emails.json
└── README.md                    # Project documentation
```

---

## 📦 Installation

```bash
git clone https://github.com/Ragib301/Google-Maps-Scraper-Ai-Agent.git
cd Google-Maps-Scraper-Ai-Agent
pip install -r requirements.txt
streamlit run main.py
```

---

## 📜 License

MIT License — feel free to fork, modify, and share!

---

## 📬 Feedback & Contributions

Open to issues, improvements, and ideas. PRs welcome!
