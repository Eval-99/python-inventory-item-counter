import sqlite3
from functools import partial

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import CommandPalette, Hit, Hits, Provider
from textual.containers import Center, Container
from textual.css.query import NoMatches
from textual.widgets import Footer, Input, Label

con = sqlite3.connect("items.db")
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS items('name' TEXT, 'count' INTEGER, 'weight' REAL)
""")

items = {row[0] for row in cur.execute("SELECT name FROM items").fetchall()}


class ItemSearch(Provider):
    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)

        for name in items:
            score = matcher.match(name)
            if score > 0 and not self.app.delete and not self.app.update:  # ty:ignore[unresolved-attribute]
                yield Hit(
                    score,
                    matcher.highlight(name),
                    partial(self.app.calc, name),  # ty:ignore[unresolved-attribute]
                    help="",
                )


class CustomCommandPalette(CommandPalette):
    def __init__(self):
        super().__init__(placeholder=" Search database", providers=[ItemSearch])


class CountCalc(App):
    CSS_PATH = "style.css"
    ENABLE_COMMAND_PALETTE = False
    COMMAND_PALETTE_DISPLAY = CustomCommandPalette

    BINDINGS = [
        Binding(
            "ctrl+q",
            "quit",
            "Quit",
            key_display="Ctrl+q",
            tooltip="Press Ctrl+q or click this button to quit",
        ),
        Binding(
            "ctrl+f",
            "custom_palette",
            "Search",
            key_display="Ctrl+f",
            tooltip="Press Ctrl+f or click this button to search database",
        ),
    ]

    def action_custom_palette(self):
        self.push_screen(self.COMMAND_PALETTE_DISPLAY())

    def compose(self) -> ComposeResult:
        self.delete = False
        self.update = False
        yield Container(
            Center(Label("Start. Hello", id="startscreen", classes="start"))
        )
        yield Footer()

    def calc(self, name: str) -> None:
        self.item = cur.execute(
            "SELECT * FROM items WHERE name = ? ", (name,)
        ).fetchone()

        self.label = self.query_one("#startscreen", Label)
        self.label.update(f"{self.item[0]}")

        try:
            self.center = self.query_one(".remove", Center)
            self.center.remove()
        except NoMatches:
            pass

        container = self.query_one(Container)
        container.mount(Center(Input(classes="itemInput"), classes="remove"))
        input = self.query_one(".itemInput", Input)
        input.focus()

        res = round(
            (float(0.300) / float(self.item[2]) * float(self.item[1])),
            2,
        )


if __name__ == "__main__":
    app = CountCalc()
    app.run()
    con.close()
