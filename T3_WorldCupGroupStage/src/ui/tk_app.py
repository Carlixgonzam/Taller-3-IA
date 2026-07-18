"""Tkinter briefing UI — walk matches with a cursor; Q/E via scenarios."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.logic.predicate.engine import ScenarioEngine
from src.worldcup.config import display_name, flag_emoji, groups
from src.worldcup.matches import (
    best_third_teams,
    load_matches,
    standings_from_matches,
    state_for,
)
from src.worldcup.rules import register_rules

GROUP_IDS = list("abcdefghijkl")

_TAG_STYLE = {
    "Q": {"background": "#1b7f4e", "foreground": "#ffffff"},
    "E": {"background": "#b33a3a", "foreground": "#ffffff"},
    "best_third": {"background": "#1a5f9e", "foreground": "#ffffff"},
}

_LIMITATION_NOTE = (
    "Note: best third-place teams are NOT modeled in scenario logic. "
    "The blue highlight appears only after the last match (visual ranking)."
)


class BriefingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("FIFA 2026 — Group stage")
        self.geometry("1180x740")

        self.matches = load_matches()
        self.cursor = 0
        self.engine = ScenarioEngine()
        register_rules(self.engine)

        style = ttk.Style(self)
        style.configure("Standings.Treeview", rowheight=26)

        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)
        self.progress = ttk.Label(top, text="")
        self.progress.pack(side=tk.LEFT)
        self.last_lbl = ttk.Label(top, text="Last: —")
        self.last_lbl.pack(side=tk.LEFT, padx=16)

        btns = ttk.Frame(top)
        btns.pack(side=tk.RIGHT)
        ttk.Button(btns, text="Back (b)", command=self._back).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Next (n)", command=self._next).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Reset (r)", command=self._reset).pack(side=tk.LEFT, padx=2)

        body = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        tables_frame = ttk.Frame(body)
        side = ttk.Frame(body, width=340)
        body.add(tables_frame, weight=3)
        body.add(side, weight=1)

        canvas = tk.Canvas(tables_frame, highlightthickness=0)
        scroll = ttk.Scrollbar(tables_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.tables_inner = ttk.Frame(canvas)
        self.tables_inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.tables_inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(side, text="Scenario deductions", font=("", 11, "bold")).pack(anchor="w")
        self.feed = tk.Text(side, height=22, wrap=tk.WORD, font=("Menlo", 10))
        self.feed.pack(fill=tk.BOTH, expand=True, pady=4)

        ttk.Label(
            side,
            text=_LIMITATION_NOTE,
            wraplength=320,
            foreground="#666",
            font=("", 9),
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            side,
            text="Keys: n next · b back · r reset",
            foreground="#666",
        ).pack(anchor="w", pady=(8, 0))

        self.bind("<n>", lambda e: self._next())
        self.bind("<b>", lambda e: self._back())
        self.bind("<r>", lambda e: self._reset())
        self.bind("<Right>", lambda e: self._next())
        self.bind("<Left>", lambda e: self._back())

        self._refresh()

    @property
    def played(self):
        return self.matches[: self.cursor]

    def _next(self) -> None:
        if self.cursor < len(self.matches):
            self.cursor += 1
            self._refresh()

    def _back(self) -> None:
        if self.cursor > 0:
            self.cursor -= 1
            self._refresh()

    def _reset(self) -> None:
        self.cursor = 0
        self._refresh()

    def _logic_status(self, team: str, group: str) -> str:
        state = state_for(self.matches, self.played, group)
        if self.engine.entails("definitely_qualified", state, team):
            return "Q"
        if self.engine.entails("definitely_eliminated", state, team):
            return "E"
        return ""

    def _row_tag(self, team: str, group: str, best_thirds: set[str]) -> str:
        """Priority: Q > best_third > E."""
        mark = self._logic_status(team, group)
        if mark == "Q":
            return "Q"
        if team in best_thirds:
            return "best_third"
        return mark

    def _refresh(self) -> None:
        self.progress.config(text=f"Match {self.cursor}/{len(self.matches)}")
        last = self.played[-1] if self.played else None
        if last:
            ko = last.kickoff.strftime("%Y-%m-%d %H:%M %z") if last.kickoff else ""
            self.last_lbl.config(
                text=(
                    f"Last: {last.scoreline()} · G{last.group.upper()} MD{last.matchday}"
                    + (f" · {ko}" if ko else "")
                )
            )
        else:
            self.last_lbl.config(text="Last: —")

        best_thirds: set[str] = set()
        if self.cursor == len(self.matches):
            best_thirds = best_third_teams(self.played)

        self.feed.delete("1.0", tk.END)
        if last is None:
            self.feed.insert(tk.END, "(no matches yet)\n")
        else:
            focus = last.group
            state = state_for(self.matches, self.played, focus)
            self.feed.insert(
                tk.END,
                f"Group {focus.upper()} · "
                f"{len(state.known)} known · {len(state.pending)} pending "
                f"({3 ** len(state.pending)} scenarios)\n\n",
            )
            for team in groups()[focus]:
                tag = self._row_tag(team, focus, best_thirds)
                label = {
                    "Q": "definitely_qualified",
                    "E": "definitely_eliminated",
                    "best_third": "best_third (visual only)",
                }.get(tag, "—")
                self.feed.insert(
                    tk.END,
                    f"{flag_emoji(team)} {display_name(team)}: {label}\n",
                )
            if best_thirds:
                self.feed.insert(
                    tk.END,
                    f"\nBest thirds (top 8): {', '.join(sorted(best_thirds))}\n",
                )

        for child in self.tables_inner.winfo_children():
            child.destroy()

        for g in GROUP_IDS:
            frm = ttk.LabelFrame(self.tables_inner, text=f"Group {g.upper()}", padding=4)
            frm.pack(fill=tk.X, pady=4, padx=4)
            cols = ("#", "Team", "MP", "W", "D", "L", "GF", "GA", "GD", "Pts")
            tree = ttk.Treeview(frm, columns=cols, show="headings", height=4)
            tree.configure(style="Standings.Treeview")
            for tag, style in _TAG_STYLE.items():
                tree.tag_configure(tag, **style)
            widths = (36, 220, 36, 36, 36, 36, 36, 36, 40, 40)
            for c, w in zip(cols, widths):
                tree.heading(c, text=c)
                tree.column(c, width=w, anchor="center" if c != "Team" else "w")
            rows = standings_from_matches(self.played, g)
            for i, row in enumerate(rows, start=1):
                gd = f"+{row.gd}" if row.gd > 0 else str(row.gd)
                tag = self._row_tag(row.team, g, best_thirds)
                tags: tuple[str, ...] = (tag,) if tag else ()
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        i,
                        f"{flag_emoji(row.team)} {display_name(row.team)}",
                        row.played,
                        row.wins,
                        row.draws,
                        row.losses,
                        row.gf,
                        row.ga,
                        gd,
                        row.pts,
                    ),
                    tags=tags,
                )
            tree.pack(fill=tk.X)


def run_app() -> None:
    BriefingApp().mainloop()
