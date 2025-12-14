import sqlite3
from functools import partial

from textual.app import App
from textual.command import Hit, Hits, Provider

con = sqlite3.connect("items.db")
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS pubs('name' TEXT, 'count' INTEGER, 'weight' REAL)
""")

ITEMS = set(cur.execute('SELECT "name" FROM "pubs"').fetchall()[0])


class ItemSearch(Provider):
    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)

        for name in ITEMS:
            score = matcher.match(name)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(name),
                    partial(self.app.calc, name),
                    help="",
                )


class CountCalc(App[None]):
    COMMANDS = {ItemSearch}

    def calc(self, name: str) -> None:
        item = cur.execute("SELECT * FROM pubs WHERE name = ? ", (name,))


if __name__ == "__main__":
    app = CountCalc()
    app.run()
    con.close()
