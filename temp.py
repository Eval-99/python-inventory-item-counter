from textual.app import App
from textual.command import CommandPalette, Hit, Provider


class MyProvider(Provider):
    def hits(self, query: str) -> list[Hit]:
        # always return at least one dummy hit so the palette renders
        return [Hit("Dummy command")]


class MyApp(App):
    BINDINGS = [("ctrl+p", "toggle_palette", "Command Palette")]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.palette = None

    def action_toggle_palette(self):
        if self.palette is None:
            self.palette = CommandPalette(
                placeholder="Search commands…", providers=[MyProvider()]
            )
            self.mount(self.palette)
        self.palette.display = not self.palette.display
        if self.palette.display:
            self.palette.focus()


if __name__ == "__main__":
    MyApp().run()
