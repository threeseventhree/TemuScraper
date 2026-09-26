from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll # useful customizable containers and scrollers, easy to implement
from textual.widgets import Button, Footer, Header, Input, Label, Static # responsible for the widgets in the main app and the config
from textual.screen import ModalScreen # modal screen for config window
from textual.worker import Worker, WorkerState # a worker that runs in the background and performs certain tasks, in this case the scraping logic

from config import ScraperConfig
from scraper.runner import runScraper
from scraper.exporter import exportTxt
from scraper.login import TemuLogin

from functools import partial
from pathlib import Path

# Getting the query from the searchbox, splitting at commas and adding it to the list of queries
def parseQueries(queryText: str) -> list[str]:
    return [
        query.strip()
        for query in queryText.split(",")
        if query.strip()
    ]

# Adding a modal config screen
class ConfigScreen(ModalScreen):
    def __init__(self, config: ScraperConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with Container(id="config-container"):
            yield Static("CONFIG", id="config-title")
            with VerticalScroll(id="config-scroll"):
                yield Label("Minimum Rating")
                yield Input(
                    value=str(self.config.minRating),
                    id="min-rating"
                )

                yield Label("Minimum Reviews")
                yield Input(
                    value=str(self.config.minReviews),
                    id="min-reviews"
                )

                yield Label("Minimum Sales")
                yield Input(
                    value=str(self.config.minSales),
                    id="min-sales"
                )

                yield Label("Maximum Products")
                yield Input(
                    value=str(self.config.maxProducts),
                    id="max-products"
                )

                yield Label("Maximum Scrolls")
                yield Input(
                    value=str(self.config.maxScrolls),
                    id="max-scrolls"
                )

                with Horizontal(id="config-buttons"):
                    yield Button("Cancel", id="cancel-config")
                    yield Button("Save", id="save-config", variant="primary")
    
    def saveConfig(self):
        try:
            self.config.minRating = float(
                self.query_one("#min-rating", Input).value
            )

            self.config.minReviews = int(
                self.query_one("#min-reviews", Input).value
            )

            self.config.minSales = int(
                self.query_one("#min-sales", Input).value
            )

            self.config.maxProducts = int(
                self.query_one("#max-products", Input).value
            )

            self.config.maxScrolls = int(
                self.query_one("#max-scrolls", Input).value
            )

        except ValueError:
            self.notify(
                "Please enter valid numbers.",
                severity="error"
            )
            return

        self.dismiss(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-config":
            self.dismiss(False)

        elif event.button.id == "save-config":
            self.saveConfig()

# Main application code
class TemuScraperApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #main-container {
        width: 90%;
        height: 90%;
        border: solid #3d78a6;
        padding: 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }

    #query-label {
        margin-bottom: 1;
    }

    #query-input {
        margin-bottom: 2;
    }

    #buttons {
        height: auto;
        align: center middle;
    }

    Button {
        margin: 1;
    }

    #status {
        margin-top: 2;
        padding: 1;
        border: solid #444444;
    }

    #config-container {
        width: 60;
        height: 80%;
        padding: 2;
        border: solid #3d78a6;
        background: $surface;
    }

    #config-title {
        height: 3;
        text-align: center;
        text-style: bold;
    }

    #config-scroll {
        height: 1fr;
    }

    #config-container Input {
        margin-bottom: 1;
    }

    #config-buttons {
        height: 4;
        align: center middle;
    }

    #config-buttons Button {
        margin: 1;
    }
    """
    def __init__(self):
        super().__init__()
        self.config = ScraperConfig()

        self.searchWorker = None
        self.loginWorker = None

        self.searchResults = []
        self.loginSession = None

        self.sessionValid = Path("temu_state.json").exists()

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="main-container"):
            yield Static(
                "Temu Scraper v2",
                id="title"
            )

            yield Label(
                "Search queries (separated by commas):",
                id="query-label"
            )

            yield Input(
                placeholder="Enter comma separated queries...",
                id="query-input"
            )

            with Horizontal(id="buttons"):
                yield Button("Login", id="login")
                yield Button("Config", id="config")
                yield Button("Search", id="search", variant="primary", disabled=not self.isLoggedIn()) # searching is disabled if the user isn't logged in
                yield Button("Export TXT", id="export", disabled=True) # exporting disabled by default, enabling once we get search results

            yield Static(
                "Status: Ready",
                id="status"
            )

        yield Footer()

    def configUpdated(self, saved: bool | None):
        if saved:
            self.updateStatus("Configuration saved.")
        else:
            self.updateStatus("Configuration unchanged.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login":
            if self.loginSession:
                self.finishLogin()
            else:
                self.startLogin()

        elif event.button.id == "config":
            self.push_screen(ConfigScreen(self.config), self.configUpdated)

        elif event.button.id == "search":
            if (self.searchWorker and self.searchWorker.is_running):
                self.updateStatus("A search is already in progress...")
                return
            if not self.isLoggedIn():
                self.updateStatus("You are not logged in! Please log in.")
                return
            
            queryText = self.query_one("#query-input", Input).value
            queries = parseQueries(queryText)
            if not queries:
                self.updateStatus("You haven't added any queries to search.")
                return
            
            self.searchResults = []
            self.setControlsEnabled(False)

            self.updateStatus(f"Starting search for {len(queries)} queries...")
            self.runSearch(queries)

        elif event.button.id == "export":
            if not self.searchResults:
                self.updateStatus("There are no search results to export.")
                return
            try:
                exportTxt(self.searchResults)
                self.updateStatus("Successfully exported the data as TXT file.")
            except Exception as error:
                self.updateStatus(f"Export failed: {error}")

    def runSearch(self, queries: list[str]):
        work = partial(runScraper, queries, self.config) 
        # partial is used to create a new function and pass the arguments to it, avoiding the error we would get typically

        self.searchWorker = self.run_worker(
            work,
            name="temu-search",
            group="scraping",
            exclusive=True,
            thread=True,
            exit_on_error=False
        )

    def on_worker_state_changed(self, event: Worker.StateChanged):
        if event.worker is self.searchWorker:
            if event.state == WorkerState.SUCCESS:
                self.searchResults = event.worker.result or []
                totalProducts = sum(
                    len(result["products"])
                    for result in self.searchResults
                )
                self.setControlsEnabled(True)
                if totalProducts == 0:
                    self.updateStatus("Search complete, but we haven't found any products.")
                else:
                    self.updateStatus(f"Search complete — {totalProducts} products found.")
            elif event.state == WorkerState.ERROR:
                self.searchResults = []
                error = str(event.worker.error)
                if "Temu session expired" in error:
                        self.sessionValid = False
                        self.updateStatus("Temu session expired. Please log in again.")
                else:
                    self.updateStatus(f"Search failed: {error}")
                self.setControlsEnabled(True)
                

        elif event.worker is self.loginWorker:
            if event.state == WorkerState.SUCCESS:
                self.sessionValid = True
                self.loginSession = None
                self.loginWorker = None

                self.query_one("#login", Button).label = "Login"
                self.setControlsEnabled(True)

                self.updateStatus("Login successful.")
            elif event.state == WorkerState.ERROR:
                self.loginSession = None
                self.loginWorker = None
                self.query_one("#login", Button).label = "Login"
                self.setControlsEnabled(True)
                self.updateStatus(f"Login failed: {event.worker.error}")
            
    def updateStatus(self, message: str):
        self.query_one("#status", Static).update(f"Status: {message}")

    def isLoggedIn(self) -> bool:
        return self.sessionValid

    def setControlsEnabled(self, enabled: bool):
        self.query_one("#login", Button).disabled = not enabled
        self.query_one("#config", Button).disabled = not enabled
        self.query_one("#search", Button).disabled = (not enabled or not self.isLoggedIn()) # search enables itself once we log in or once we set it as enabled
        self.query_one("#export", Button).disabled = (not enabled or not self.searchResults) # export enables itself if we enable it or if we have search results

    def startLogin(self):
        if self.loginWorker and self.loginWorker.is_running:
            self.updateStatus("Login is already in progress.")
            return

        if self.searchWorker and self.searchWorker.is_running:
            self.updateStatus("Please wait for the search to finish.")
            return
        
        self.setControlsEnabled(False)
        self.updateStatus("Opening Temu, please log in!")

        self.loginSession = TemuLogin()
        self.loginWorker = self.run_worker(
            self.loginSession.start,
            name="temu-login",
            group="login",
            exclusive=True,
            thread=True,
            exit_on_error=False
        )
        self.query_one("#login", Button).disabled = False
        self.query_one("#login", Button).label = "Finish Login"

    def finishLogin(self):
        if not self.loginSession:
            return
        
        if not self.loginWorker or not self.loginWorker.is_running:
            self.updateStatus("Login session is no longer active.")
            return
    
        self.loginSession.requestFinish()
    
        self.query_one("#login", Button).disabled = True
        self.updateStatus("Saving Temu login session...")

if __name__ == "__main__":
    TemuScraperApp().run()
