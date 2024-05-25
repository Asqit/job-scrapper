# Job Scraper

## Usage

To use the job scraper, follow these steps:

1. Install the required dependencies by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the `main.py` script with the `search` mode and provide `url`. For example:

   ```bash
   python main.py --mode scrape --url "https://sample-url.com/..." --title-class "title title-link" --pagination-class "pagination-item"
   ```

3. The script can also search the scraped results for keywords in the job title

   ```base
   python main.py --mode search --url ./results.csv --keywords junior frontend react vue angular remote
   ```

That's it! You can now use the job scraper to find relevant job listings. Happy job hunting!
