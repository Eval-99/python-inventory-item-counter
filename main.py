import sqlite3
from functools import partial

from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.widgets import Label

con = sqlite3.connect("items.db")
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS items('name' TEXT, 'count' INTEGER, 'weight' REAL)
""")

ITEMS = {row[0] for row in cur.execute("SELECT name FROM items").fetchall()}


class ItemSearch(Provider):
    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)

        for name in ITEMS:
            score = matcher.match(name)
            if score > 0 and not self.app.delete and not self.app.update:  # pyright: ignore[reportAttributeAccessIssue]
                yield Hit(
                    score,
                    matcher.highlight(name),
                    partial(self.app.calc, name),  # pyright: ignore[reportAttributeAccessIssue]
                    help="",
                )


class CountCalc(App[None]):
    COMMANDS = {ItemSearch}
    CSS_PATH = "style.css"
    # COMMAND_PALETTE_BINDING = "ctrl+backslash"

    def compose(self) -> ComposeResult:
        self.delete = False
        self.update = False
        yield Label("", id="output", classes="box")

    def calc(self, name: str) -> None:
        self.item = cur.execute(
            "SELECT * FROM items WHERE name = ? ", (name,)
        ).fetchone()
        self.label = self.query_one("#output", Label)
        self.label.update(f"{self.item[0]}, {self.item[1]}, {self.item[2]}")


if __name__ == "__main__":
    app = CountCalc()
    app.run()
    con.close()
