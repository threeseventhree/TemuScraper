from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Label, Static
from textual.screen import ModalScreen

from config import ScraperConfig

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
            self.updateStatus("Search button pressed.")

        elif event.button.id == "export":
            self.updateStatus("Export button pressed.")

    def updateStatus(self, message: str):
        self.query_one("#status", Static).update(
            f"Status: {message}"
        )


if __name__ == "__main__":
    TemuScraperApp().run()
