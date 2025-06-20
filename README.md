# Amazon Product Scraper

This project is a Scrapy-based spider for scraping product data from Amazon using [ScraperAPI](https://www.scraperapi.com/) to bypass anti-bot measures.

## Project Structure

```
AMAZON/
├── scrapy.cfg
└── AMAZON/
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── settings.py
    └── spiders/
        ├── amazon.py
        ├── Input_ASIN.txt
        ├── proxy.txt
        └── ...
```

## Features

- Scrapes product data for a list of ASINs from Amazon.
- Uses ScraperAPI for reliable scraping.
- Outputs results to a timestamped CSV file.

---

## Prerequisites

- Python 3.7+
- [pip](https://pip.pypa.io/en/stable/)
- A [ScraperAPI](https://www.scraperapi.com/) account and API key

---

## Setup Instructions

1. **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd <repo-folder>
    ```

2. **Create and activate a virtual environment (recommended):**
    ```sh
    python -m venv scrapyenv
    # On Windows:
    .\scrapyenv\Scripts\activate
    # On Mac/Linux:
    source scrapyenv/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install scrapy
    ```

4. **Add your ScraperAPI key:**
    - Create a file named `proxy.txt` inside `AMAZON/spiders/`.
    - Paste your ScraperAPI key (just the key, nothing else) into this file.

5. **Add your ASINs:**
    - Create a file named `Input_ASIN.txt` inside `AMAZON/spiders/`.
    - Add one ASIN per line.

---

## Running the Spider

1. **Navigate to the project root (where `scrapy.cfg` is):**
    ```sh
    cd AMAZON
    ```

2. **Run the spider:**
    ```sh
    scrapy crawl amazon
    ```

3. **Output:**
    - Results will be saved in the `Results_CSV_Files` folder as a timestamped CSV file.

---

## Troubleshooting

- **FileNotFoundError:**  
  Make sure `proxy.txt` and `Input_ASIN.txt` are in the `AMAZON/spiders/` directory.
- **ModuleNotFoundError:**  
  Ensure your virtual environment is activated and dependencies are installed.
- **ScraperAPI errors:**  
  Make sure your API key is valid and you have enough credits.

---

## Customization

- To change what data is scraped or how it is processed, edit `AMAZON/spiders/amazon.py`.

---

## License

MIT License

---

## Credits

- [Scrapy](https://scrapy.org/)
- [ScraperAPI](https://www.scraperapi.com/) 