from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll # useful customizable containers and scrollers, easy to implement
from textual.widgets import Button, Footer, Header, Input, Label, Static # responsible for the widgets in the main app and the config
from textual.screen import ModalScreen # modal screen for config window
from textual.worker import Worker, WorkerState # a worker that runs in the background and performs certain tasks, in this case the scraping logic

from config import ScraperConfig
from scraper.runner import runScraper
from scraper.exporter import exportTxt

from functools import partial

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
        self.searchResults = []

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
                yield Button("Search", id="search", variant="primary")
                yield Button("Export TXT", id="export")

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
            self.updateStatus("Login button pressed.")

        elif event.button.id == "config":
            self.push_screen(
                ConfigScreen(self.config),
                self.configUpdated
            )

        elif event.button.id == "search":
            queryText = self.query_one("#query-input", Input).value
            queries = parseQueries(queryText)

            if not queries:
                self.updateStatus("You haven't added any queries to search.")
                return

            self.updateStatus(f"Starting search for {len(queries)} queries...")
            self.runSearch(queries)

        elif event.button.id == "export":
            exportTxt(self.searchResults or [])
            self.updateStatus("Successfully exported the data as TXT file.")

    def runSearch(self, queries: list[str]):
        work = partial(runScraper, queries, self.config) 
        # partial is used to create a new function and pass the arguments to it, avoiding the error we would get typically

        self.searchWorker = self.run_worker(
            work,
            name="temu-search",
            group="scraping",
            exclusive=True,
            thread=True,
        )

    def on_worker_state_changed(self, event: Worker.StateChanged):
        if event.worker is not self.searchWorker:
            return

        if event.state == WorkerState.SUCCESS:
            self.searchResults = event.worker.result

            totalProducts = sum(
                len(result["products"])
                for result in (self.searchResults or [])
            )

            self.updateStatus(
                f"Search complete — "
                f"{totalProducts} products found."
            )
        elif event.state == WorkerState.ERROR:
            self.updateStatus(
                f"Search failed: {event.worker.error}"
            )
            
    def updateStatus(self, message: str):
        self.query_one("#status", Static).update(
            f"Status: {message}"
        )

if __name__ == "__main__":
    TemuScraperApp().run()
