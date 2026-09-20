# Temu Scraper V1
A product-scraping tool built with **Python** and **Playwright** that helps analyze and compare Temu products efficiently.

The scraper collects product information such as reviews, ratings, and prices, then calculates a score to help identify products that offer the best overall value.

### Project Diagram:
![alt](img/paste_1789895296973.png)

### How to use:
1. Upon installing all of the files, run login.py to authenticate with your temu account and avoid any sorts of errors or problems.
2. All of the search and filtering parameters are editable in the custom config.py file, you can add as many queries as you like and filter them however you want.
3. After you have went through the initial setup, you can run it using python main.py.
4. Upon the completion of the extraction, all of your data will appear in "data/products.json", sorted by score(highest to lowest) and with links you can click and add to your cart.

### Future updates:
1. Adding a GUI for easier navigation and config setup.
2. Possibly adding a Google Drive export option through the API and storing the exported data in a neat Google Sheets file on your personal drive.

This has been a fun project and learning experience for me, many more to come.
### - 373
