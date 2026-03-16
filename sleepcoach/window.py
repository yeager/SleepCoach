"""Main application window."""
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from sleepcoach.i18n import _
from sleepcoach.database import SleepDatabase


class SleepCoachWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = SleepDatabase()
        self.set_title(_("SleepCoach"))
        self.set_default_size(420, 700)

        # Main layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        # Header
        header = Adw.HeaderBar()
        box.append(header)

        # View stack
        stack = Adw.ViewStack()
        switcher = Adw.ViewSwitcherBar()
        switcher.set_stack(stack)

        box.append(stack)
        box.append(switcher)
        switcher.set_reveal(True)

        # Routine page
        routine_page = self._build_routine_page()
        stack.add_titled(routine_page, "routine", _("Routine"))

        # Log page
        log_page = self._build_log_page()
        stack.add_titled(log_page, "log", _("Sleep Log"))

        # Tips page
        tips_page = self._build_tips_page()
        stack.add_titled(tips_page, "tips", _("Tips"))

        # Stats page
        stats_page = self._build_stats_page()
        stack.add_titled(stats_page, "stats", _("Statistics"))

    def _build_routine_page(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.add_css_class("boxed-list")
        scroll.set_child(listbox)

        clamp = Adw.Clamp()
        clamp.set_child(scroll)
        clamp.set_maximum_size(500)

        steps = self.db.get_routine()
        for step_id, order, title, duration, enabled in steps:
            row = Adw.ActionRow()
            row.set_title(_(title))
            row.set_subtitle(_("%d minutes") % duration if duration > 0 else _("Done!"))
            check = Gtk.CheckButton()
            row.add_prefix(check)
            listbox.append(row)

        # Start routine button
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.append(clamp)

        start_btn = Gtk.Button(label=_("Start Bedtime Routine"))
        start_btn.add_css_class("suggested-action")
        start_btn.add_css_class("pill")
        vbox.append(start_btn)

        return vbox

    def _build_log_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)

        # Input fields
        group = Adw.PreferencesGroup()
        group.set_title(_("Log Tonight's Sleep"))

        bedtime_row = Adw.EntryRow()
        bedtime_row.set_title(_("Bedtime (HH:MM)"))
        group.add(bedtime_row)

        waketime_row = Adw.EntryRow()
        waketime_row.set_title(_("Wake time (HH:MM)"))
        group.add(waketime_row)

        quality_row = Adw.SpinRow.new_with_range(1, 5, 1)
        quality_row.set_title(_("Sleep quality (1-5)"))
        quality_row.set_value(3)
        group.add(quality_row)

        notes_row = Adw.EntryRow()
        notes_row.set_title(_("Notes (optional)"))
        group.add(notes_row)

        vbox.append(group)

        save_btn = Gtk.Button(label=_("Save Sleep Log"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", lambda b: self._save_log(
            bedtime_row.get_text(), waketime_row.get_text(),
            int(quality_row.get_value()), notes_row.get_text()
        ))
        vbox.append(save_btn)

        # History
        history_group = Adw.PreferencesGroup()
        history_group.set_title(_("Recent Sleep History"))
        self._history_group = history_group
        vbox.append(history_group)
        self._refresh_history()

        return vbox

    def _save_log(self, bedtime, waketime, quality, notes):
        if bedtime and waketime:
            self.db.log_sleep(bedtime, waketime, quality, notes)
            self._refresh_history()

    def _refresh_history(self):
        # Clear
        while child := self._history_group.get_first_child():
            if isinstance(child, Adw.ActionRow):
                self._history_group.remove(child)
            else:
                break

        for date_str, bedtime, waketime, quality, notes in self.db.get_logs(7):
            stars = "★" * quality + "☆" * (5 - quality)
            row = Adw.ActionRow()
            row.set_title(f"{date_str}")
            row.set_subtitle(f"{bedtime} → {waketime}  {stars}")
            self._history_group.add(row)

    def _build_tips_page(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.add_css_class("boxed-list")

        tips = [
            (_("Avoid screens 30 min before bed"), _("Blue light suppresses melatonin production.")),
            (_("Keep a consistent schedule"), _("Go to bed and wake up at the same time every day.")),
            (_("Cool bedroom temperature"), _("18-20°C is ideal for sleep.")),
            (_("No caffeine after lunch"), _("Caffeine has a half-life of 5-6 hours.")),
            (_("Exercise during the day"), _("But not within 2 hours of bedtime.")),
            (_("Use the bed only for sleep"), _("Avoid working or watching TV in bed.")),
            (_("Try deep breathing"), _("4-7-8 technique: inhale 4s, hold 7s, exhale 8s.")),
            (_("Reduce noise"), _("Use earplugs or white noise if needed.")),
            (_("Write down worries"), _("A worry journal before bed can calm the mind.")),
            (_("Dim the lights"), _("Start dimming lights 1 hour before bedtime.")),
        ]

        for title, subtitle in tips:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(subtitle)
            listbox.append(row)

        scroll.set_child(listbox)
        clamp = Adw.Clamp()
        clamp.set_child(scroll)
        clamp.set_maximum_size(500)
        return clamp

    def _build_stats_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)

        logs = self.db.get_logs(30)
        if not logs:
            label = Gtk.Label(label=_("No sleep data yet. Start logging!"))
            label.add_css_class("dim-label")
            vbox.append(label)
            return vbox

        # Average quality
        qualities = [q for _, _, _, q, _ in logs]
        avg = sum(qualities) / len(qualities)

        group = Adw.PreferencesGroup()
        group.set_title(_("Sleep Statistics"))

        avg_row = Adw.ActionRow()
        avg_row.set_title(_("Average quality"))
        avg_row.set_subtitle(f"{'★' * round(avg)}{'☆' * (5 - round(avg))} ({avg:.1f}/5)")
        group.add(avg_row)

        count_row = Adw.ActionRow()
        count_row.set_title(_("Nights logged"))
        count_row.set_subtitle(str(len(logs)))
        group.add(count_row)

        vbox.append(group)
        return vbox
