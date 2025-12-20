import sqlite3
from functools import partial

from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.containers import Container
from textual.widgets import Input, Label

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
            if score > 0 and not self.app.delete and not self.app.update:  # ty:ignore[unresolved-attribute]
                yield Hit(
                    score,
                    matcher.highlight(name),
                    partial(self.app.calc, name),  # ty:ignore[unresolved-attribute]
                    help="",
                )


class CountCalc(App[None]):
    COMMANDS = {ItemSearch}
    CSS_PATH = "style.css"
    # COMMAND_PALETTE_BINDING = "ctrl+backslash"

    def compose(self) -> ComposeResult:
        self.delete = False
        self.update = False
        yield Container(Label("Start. Hello", id="startscreen", classes="start"))

    def calc(self, name: str) -> None:
        self.item = cur.execute(
            "SELECT * FROM items WHERE name = ? ", (name,)
        ).fetchone()

        res = round(
            (float(0.300) / float(self.item[2]) * float(self.item[1])),
            2,
        )

        # self.mount(Input("Hi", id="inputbox", classes="itemInput"))
        #
        # self.mount(
        #     Label(
        #         f"{self.item[0]}, {self.item[1]}, {self.item[2]}\n{res}",
        #         id="output",
        #         classes="result",
        #     )
        # )
        # self.mount(Input("Hi", id="inputbox", classes="itemInput"))

        self.label = self.query_one("#startscreen", Label)
        self.label.update(f"{self.item[0]}, {self.item[1]}, {self.item[2]}\n{res}")


if __name__ == "__main__":
    app = CountCalc()
    app.run()
    con.close()
