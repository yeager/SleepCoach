"""SleepCoach GTK4 Application."""
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio
from sleepcoach.window import SleepCoachWindow


class SleepCoachApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="se.danielnylander.sleepcoach",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = SleepCoachWindow(application=self)
        win.present()
