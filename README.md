Remaking UI for UCSB's dining

**Goals**:

- Easier lookup for specific items, and anything in general
- Easier search for macro-friendly items
- Better display for nutrition and ingredients

**Files**:

/backend
- backend for the website (not touched yet)

/database
- automates inputting data and searching through the database
- commonsapi.py - uses ucsb's api to find dining hall hours, etc.
- menuapi.py - uses ucsb's api to find all items on daily menu
- NOTE: will be moving ucsb api calls to frontend (typescript) so it can be called when the site loads

/frontend
- frontend for the website (not touched yet)

/scraper
- Files for web scraping
- scraper.py: main scraper that takes from ucsb's dining website
- utils.py: helper functions, like export_to_csv
- mostly complete, still has to sort filepaths

**Progress**:

- 4/18: Laid out files, began building web scraper
- 4/19: Finishing touches to web scraper: sorting out duplicate headers, began working with UCSB dining API
