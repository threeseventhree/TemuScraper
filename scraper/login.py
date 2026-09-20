from browser import BrowserManager


TEMU_URL = "https://www.temu.com"


def main():
    browser = BrowserManager(headless=False)

    try:
        browser.start()
        browser.navigate(TEMU_URL)

        print()
        print("Please log in to Temu in the browser.")
        input("Press ENTER after you have finished logging in...")

        browser.save_state()

    finally:
        browser.close()


if __name__ == "__main__":
    main()
