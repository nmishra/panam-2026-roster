# PanAm 2026 Wushu roster site

Static GitHub Pages site (https://nmishra.github.io/panam-2026-roster/, short link https://tinyurl.com/panam2026roster) that parents use to filter the athlete entry list and see when each group competes. No build step: `index.html` fetches the files in `data/` at load time, so editing data and pushing to `main` is enough (Pages redeploys in ~1 min).

## Data files
- `data/entries.csv`: one row per entry, transcribed from the official entry-list screenshots, **in the same order as the list**. Columns: `group` (`Group A`…), `gender` (`Female`/`Male`), `type` (`Barehand`, `Weapon`, `Addl. Weapon`), `category`, `style`, `country`, `athlete`. Copy text exactly as printed (accents, capitalization, Spanish terms like `Otros estilos sureños.`).
- `data/sessions.json`: `ages` per group, and `sessions` keyed `"<group> <kind>"` → `{day, time, fop, note}`. Kind is derived in `index.html` (`kindOf`): Taijiquan Routines → `Taijiquan`; styles starting with Taiji / containing Taijijian → `Taiji Weapon`; Wing Chun (barehand) → `Barehand`; else Barehand/Weapon by type (Addl. Weapon and Wing Chun Weapon → `Weapon`). Every group+kind in entries.csv needs a sessions entry or it shows "TBD".
- `data/timetable.csv`: organizers' detailed per-event timetable (Oct 8–9, issued Oct 8 13:33, from `Dia1y2_14hs0810.pdf`). `entries.csv` columns `ev_day, ev_fop, ev_start, ev_end, ev_name, ev_note` hold each entry's matched slot; the page uses them over `sessions.json`. Regenerate with `python3 tools/match_timetable.py write` (run from the repo root). It prints unmatched entries and per-event count mismatches vs the PDF; review them before pushing. Ties and overflowing "unified" events get a combined window plus a note.
- `data/program.json`: full Competition Detailed Program (all days, all FOPs), shown in the collapsible section.

## Updating from new screenshots
1. Transcribe every row; group headers look like `Grupo D — Masculino (18 a 39 años …)`. A cell split over two lines is one value; "Addl. / Weapon" is type `Addl. Weapon`.
2. Verify: count rows per screenshot against the image, and compare per-group totals with the "N atleta(s)" header and with program block counts (e.g. "Group D Barehand (125)"). Report any mismatch to the user instead of guessing.
3. Watch for duplicate or overlapping screenshots: don't add a row twice.
4. Commit and push to `main`.

## Known gaps (as of Oct 8 2026)
- Group D Male is partial (90 of 180 entries; stops after Shuangbishou León Prado Ricardo Alexis). Groups E/F are not in the entry list yet.
- Program says Group C Weapon = 20 entries at 10:15 Fri, but the roster has 91; flagged in the `note`.

## Preferences
- The user rejected estimated per-athlete/per-event time windows inside a block; show only the official block start time, day and FOP.

## Live announcements
`data/announcement.txt` is shown as a yellow banner at the top of the page. Edit it for delays and other day-of updates, and empty the file to hide the banner. Include the time the update was posted.
- Day-of delays: `data/sessions.json` → `"delays": {"Thu Oct 8": 120}` (minutes per day). The page shifts that day's roster and program times and shows the original crossed out. Remove the entry when the schedule is back on time.
