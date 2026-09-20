from scraper.browser import BrowserManager
# Sample code for testing, to be modified later
def main():
    try:
        browser = BrowserManager(headless= True)
        page = browser.start()
    
        page.goto("https://www.temu.com", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
    
        print("Title:", page.title())
    finally:
        browser.close()

if __name__ == "__main__":
    main()
