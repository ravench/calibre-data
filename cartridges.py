"""Calibre catalogue with approximate cartridge dimensions (mm, CIP/SAAMI-ish).

Shared by Schiesstagebuch, Kaliberfinder and the calibre wall poster (each pins this
repository as a git submodule); outline.py draws the side view of every calibre.
Dimensions are approximations for drawings and matching, not reloading data.
"""

# Kinds
RIMLESS, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET = (
    "rimless", "rimmed", "belted", "rimfire", "shot", "ball", "minie", "pellet")
# Bullet profiles. PATCHED: paper-patched lead body with a steel-capped round nose (GP 1890).
SPITZER, ROUND, FLAT, PATCHED = "spitzer", "round", "flat", "patched"


def c(name, kind, rim, base, shoulder, neck, case, sh_at, oal, bullet, profile, aliases=()):
    return dict(name=name, kind=kind, rim=rim, base=base, shoulder=shoulder, neck=neck,
                case=case, sh_at=sh_at, oal=oal, bullet=bullet, profile=profile, aliases=list(aliases))


def straight(name, kind, rim, base, neck, case, oal, bullet, profile, aliases=()):
    return c(name, kind, rim, base, None, neck, case, None, oal, bullet, profile, aliases)


def shot(name, dia, rim, length, aliases=()):
    return c(name, SHOT, rim, dia, None, dia, length, None, length, dia, FLAT, aliases)


def ball(name, dia, aliases=()):
    return c(name, BALL, dia, dia, None, dia, 0, None, dia, dia, ROUND, aliases)


def minie(name, dia, length, aliases=()):
    return c(name, MINIE, dia, dia, None, dia, 0, None, length, dia, ROUND, aliases)


def pellet(name, dia, length, aliases=()):
    return c(name, PELLET, dia, dia, None, dia, 0, None, length, dia, ROUND, aliases)


CATALOGUE = [
    ("Randfeuer", [
        straight(".22 Short", RIMFIRE, 6.9, 5.7, 5.7, 10.7, 17.7, 5.7, ROUND),
        straight(".22 LR", RIMFIRE, 6.9, 5.7, 5.7, 15.6, 25.4, 5.7, ROUND, ["22lr", "22", "kk", "22l.r."]),
        straight(".22 WMR", RIMFIRE, 7.5, 6.1, 6.1, 26.8, 32.3, 5.7, SPITZER, ["22mag", "22wmr"]),
        c(".17 HMR", RIMFIRE, 7.5, 6.1, 6.1, 4.5, 26.9, 21.5, 32.8, 4.4, SPITZER, ["17hmr"]),
        c(".17 Mach 2", RIMFIRE, 6.9, 5.7, 5.7, 4.5, 18.0, 13.5, 25.0, 4.4, SPITZER),
    ]),
    ("Kurzwaffe", [
        straight("6.35 mm Browning (.25 ACP)", RIMLESS, 7.6, 7.1, 7.0, 15.6, 23.1, 6.4, ROUND, ["6.35", "25acp", "25auto"]),
        straight("7.65 mm Browning (.32 ACP)", RIMLESS, 9.1, 8.6, 8.5, 17.3, 25.0, 7.9, ROUND, ["7.65browning", "32acp", "32auto"]),
        c("7.65 mm Parabellum", RIMLESS, 9.9, 9.9, 9.7, 8.4, 21.6, 15.0, 29.8, 7.85, ROUND, ["7.65para", "30luger"]),
        straight(".32 S&W Long", RIMMED, 9.5, 8.6, 8.5, 23.4, 32.5, 7.9, ROUND, ["32s&w", "32swl", "32long"]),
        straight(".32 H&R Magnum", RIMMED, 9.5, 8.6, 8.5, 27.4, 34.3, 7.9, FLAT),
        c("7.62x25 mm Tokarev", RIMLESS, 9.9, 9.9, 9.6, 8.5, 24.7, 17.5, 34.9, 7.85, ROUND, ["tokarev", "7.62tok"]),
        straight("9 mm Browning kurz (.380 ACP)", RIMLESS, 9.5, 9.5, 9.4, 17.3, 25.0, 9.0, ROUND, ["380acp", "380auto", "9kurz", "9mmkurz"]),
        straight("9x18 mm Makarov", RIMLESS, 9.9, 9.9, 9.7, 18.1, 25.0, 9.27, ROUND, ["makarov"]),
        straight("9x19 mm", RIMLESS, 9.96, 9.96, 9.65, 19.15, 29.7, 9.01, ROUND, ["9x19", "9mm", "9mmpara", "9para", "9mmluger", "9luger", "9x19para", "parabellum"]),
        straight("9x21 mm IMI", RIMLESS, 9.96, 9.96, 9.65, 21.15, 29.7, 9.01, ROUND, ["9x21"]),
        c(".357 SIG", RIMLESS, 10.77, 10.77, 10.7, 9.68, 21.97, 15.8, 28.96, 9.02, ROUND, ["357sig"]),
        straight(".38 Special", RIMMED, 11.2, 9.6, 9.6, 29.3, 39.4, 9.07, ROUND, ["38spl", "38special", "38"]),
        straight(".357 Magnum", RIMMED, 11.2, 9.6, 9.6, 32.8, 40.6, 9.07, FLAT, ["357mag", "357", "357magnum"]),
        straight(".38 Super", RIMLESS, 10.2, 9.7, 9.6, 22.9, 32.5, 9.03, ROUND, ["38super"]),
        straight("10 mm Auto", RIMLESS, 10.8, 10.8, 10.7, 25.2, 32.0, 10.17, FLAT, ["10mm", "10auto"]),
        straight(".40 S&W", RIMLESS, 10.8, 10.8, 10.7, 21.6, 28.8, 10.17, FLAT, ["40s&w", "40sw", "40"]),
        straight(".41 Magnum", RIMMED, 13.0, 11.0, 11.0, 32.8, 40.4, 10.4, FLAT, ["41mag"]),
        straight(".44 Special", RIMMED, 13.1, 11.6, 11.6, 29.5, 37.0, 10.9, FLAT, ["44spl", "44special"]),
        straight(".44 Magnum", RIMMED, 13.1, 11.6, 11.6, 32.6, 40.9, 10.9, FLAT, ["44mag", "44magnum"]),
        straight(".45 ACP", RIMLESS, 12.0, 12.0, 12.0, 22.8, 32.4, 11.5, ROUND, ["45acp", "45auto", "45", "11.43"]),
        straight(".45 Colt", RIMMED, 12.9, 12.2, 12.2, 32.6, 40.6, 11.5, FLAT, ["45colt", "45lc", "45longcolt"]),
        straight(".45 GAP", RIMLESS, 12.0, 12.0, 12.0, 19.2, 27.3, 11.5, ROUND, ["45gap"]),
        straight(".454 Casull", RIMMED, 13.1, 12.1, 12.1, 35.1, 45.0, 11.5, FLAT, ["454casull"]),
        straight(".460 S&W Magnum", RIMMED, 13.2, 12.2, 12.2, 45.7, 58.0, 11.5, FLAT, ["460s&w"]),
        straight(".500 S&W Magnum", RIMMED, 14.2, 13.4, 13.4, 41.3, 57.2, 12.7, FLAT, ["500s&w"]),
        c("5.7x28 mm", RIMLESS, 7.9, 7.9, 7.8, 6.4, 28.9, 22.5, 40.5, 5.7, SPITZER, ["5.7x28", "57x28"]),
        c("4.6x30 mm", RIMLESS, 8.0, 8.0, 7.8, 5.3, 30.5, 24.0, 38.7, 4.65, SPITZER, ["4.6x30"]),
        # Added 2026-11: further mass-produced handgun rounds, current and obsolete. Dimensions from
        # the page named in INTRODUCED (mostly the Wikipedia infobox, which quotes C.I.P./SAAMI),
        # rounded; shoulder heights of bottleneck cases are estimated for drawing.
        c("7.63x25 mm Mauser", RIMLESS, 9.98, 9.86, 9.6, 8.46, 25.15, 18.0, 34.8, 7.86, ROUND, ["7.63mauser", "30mauser"]),
        straight("7.62x38 mm R Nagant", RIMMED, 9.86, 8.94, 7.26, 38.86, 38.86, 7.82, ROUND, ["nagant", "7.62nagant"]),
        straight("7.5 mm Swiss Ordnance 1882", RIMMED, 10.4, 8.4, 8.4, 22.8, 34.6, 8.0, ROUND, ["7.5ord", "7.5revolver", "revolver82"]),
        straight("7.65 mm Longue", RIMLESS, 8.5, 8.53, 8.5, 19.7, 30.24, 7.85, ROUND, ["7.65longue", "7.65mas", "30pedersen"]),
        straight(".30 Super Carry", RIMLESS, 8.74, 8.7, 8.56, 21.0, 29.7, 7.93, ROUND, ["30sc", "30supercarry"]),
        straight(".32 S&W", RIMMED, 9.5, 8.5, 8.5, 15.0, 23.0, 7.9, ROUND, ["32s&wshort", "32sws"]),
        straight(".327 Federal Magnum", RIMMED, 9.5, 8.6, 8.6, 30.0, 37.0, 7.9, FLAT, ["327fed", "327federal"]),
        c(".32-20 Winchester", RIMMED, 10.4, 9.0, 8.7, 8.3, 33.4, 27.0, 40.4, 7.94, FLAT, ["32-20", "32wcf"]),
        c("5.45x18 mm", RIMLESS, 7.64, 7.64, 7.4, 6.26, 18.03, 13.0, 25.0, 5.63, SPITZER, ["5.45x18", "psm"]),
        c(".22 TCM", RIMLESS, 9.6, 9.55, 9.19, 6.48, 25.96, 20.0, 32.13, 5.7, SPITZER, ["22tcm"]),
        c("8 mm Nambu", RIMLESS, 10.5, 10.23, 10.0, 8.71, 21.43, 15.0, 31.56, 8.13, ROUND, ["nambu", "8nambu"]),
        straight("8 mm Lebel revolver", RIMMED, 10.43, 8.96, 8.83, 27.5, 36.7, 8.35, ROUND, ["8lebelrev", "8mm1892"]),
        straight("8 mm Roth-Steyr", RIMLESS, 8.85, 8.85, 8.8, 18.65, 29.0, 8.16, ROUND, ["rothsteyr", "8steyr"]),
        straight("9 mm Glisenti", RIMLESS, 9.98, 9.96, 9.65, 19.15, 29.21, 9.02, ROUND, ["glisenti"]),
        straight("9 mm Browning Long", RIMLESS, 10.2, 9.72, 9.68, 20.2, 28.0, 9.09, ROUND, ["9browninglong", "9x20sr"]),
        straight("9x23 mm Steyr", RIMLESS, 9.7, 9.7, 9.62, 23.2, 32.99, 9.03, ROUND, ["9steyr"]),
        straight("9x23 mm Largo", RIMLESS, 9.9, 9.91, 9.7, 23.1, 33.53, 9.0, ROUND, ["9largo", "bergmann-bayard"]),
        straight(".38 S&W", RIMMED, 11.2, 9.82, 9.79, 19.7, 31.5, 9.2, ROUND, ["38s&w", "38sw", "380-200"]),
        straight(".38 Short Colt", RIMMED, 11.3, 9.6, 9.6, 19.4, 30.48, 9.1, ROUND, ["38shortcolt"]),
        straight(".38 Long Colt", RIMMED, 11.3, 9.7, 9.7, 26.2, 34.54, 9.1, ROUND, ["38longcolt", "38lc"]),
        c(".38-40 Winchester", RIMMED, 13.3, 11.93, 11.54, 10.58, 33.1, 25.0, 40.0, 10.17, FLAT, ["38-40", "38wcf"]),
        straight("10.4 mm Swiss Ordnance 1878", RIMMED, 13.3, 11.2, 10.8, 20.0, 32.0, 10.76, ROUND, ["10.4revolver", "revolver78"]),
        straight(".44 S&W Russian", RIMMED, 13.1, 11.6, 11.6, 24.6, 36.3, 10.9, ROUND, ["44russian"]),
        straight("11 mm French Ordnance", RIMMED, 12.5, 11.45, 11.45, 17.0, 30.0, 11.46, ROUND, ["11mmfrench", "11mm1873"]),
        straight(".45 Schofield", RIMMED, 13.2, 12.2, 12.2, 27.9, 36.3, 11.5, FLAT, ["45schofield", "45s&w"]),
        straight(".45 Auto Rim", RIMMED, 13.09, 11.96, 11.9, 22.87, 32.12, 11.5, ROUND, ["45autorim", "45ar"]),
        straight(".455 Webley", RIMMED, 13.5, 12.2, 12.1, 19.6, 31.2, 11.5, ROUND, ["455webley", "455"]),
        straight(".480 Ruger", RIMLESS, 13.7, 12.8, 12.8, 32.6, 41.9, 12.1, FLAT, ["480ruger"]),
        straight(".50 Action Express", RIMLESS, 13.1, 13.8, 13.5, 32.6, 40.9, 12.7, FLAT, ["50ae"]),
    ]),
    ("Langwaffe", [
        c(".204 Ruger", RIMLESS, 9.6, 9.6, 9.3, 6.0, 47.0, 38.5, 57.4, 5.2, SPITZER),
        c(".222 Remington", RIMLESS, 9.6, 9.6, 9.1, 6.4, 43.2, 34.0, 54.0, 5.7, SPITZER, ["222rem"]),
        c(".223 Remington", RIMLESS, 9.6, 9.6, 9.0, 6.4, 44.7, 36.0, 57.4, 5.7, SPITZER, ["223", "223rem"]),
        c("5.56x45 mm NATO", RIMLESS, 9.6, 9.6, 9.0, 6.4, 44.7, 36.0, 57.4, 5.7, SPITZER, ["5.56", "556", "5.56x45", "5.56nato"]),
        c("5.6 mm GP 90 (Swiss)", RIMLESS, 9.6, 9.6, 9.0, 6.4, 44.7, 36.0, 57.4, 5.7, SPITZER, ["gp90", "gp 90", "5.6", "5.6mm", "5.6gp90", "stgw90"]),
        c(".22-250 Remington", RIMLESS, 12.0, 12.0, 11.5, 6.6, 48.6, 39.0, 60.3, 5.7, SPITZER, ["22-250"]),
        c(".243 Winchester", RIMLESS, 12.0, 12.0, 11.5, 7.0, 51.9, 41.0, 68.8, 6.2, SPITZER, ["243", "243win"]),
        c("6 mm BR Norma", RIMLESS, 12.0, 12.0, 11.6, 6.9, 39.6, 31.5, 58.0, 6.2, SPITZER, ["6br", "6mmbr"]),
        c("6 mm ARC", RIMLESS, 11.2, 11.2, 10.9, 6.9, 38.6, 31.8, 57.4, 6.2, SPITZER, ["6arc"]),
        c("6.5 mm Creedmoor", RIMLESS, 12.0, 12.0, 11.7, 7.5, 48.8, 39.6, 71.8, 6.7, SPITZER, ["6.5cm", "6.5creedmoor", "65cm", "creedmoor"]),
        c("6.5x55 mm Swedish", RIMLESS, 12.2, 12.2, 11.0, 7.6, 55.0, 44.6, 80.0, 6.7, SPITZER, ["6.5x55", "6.5x55se"]),
        c("6.5x47 mm Lapua", RIMLESS, 12.0, 12.0, 11.6, 7.5, 47.0, 38.2, 72.0, 6.7, SPITZER, ["6.5x47"]),
        c("6.5 PRC", RIMLESS, 13.0, 13.0, 12.8, 7.5, 51.2, 41.8, 84.8, 6.7, SPITZER, ["6.5prc"]),
        c(".260 Remington", RIMLESS, 12.0, 12.0, 11.5, 7.5, 51.7, 41.0, 71.1, 6.7, SPITZER),
        c(".270 Winchester", RIMLESS, 12.0, 12.0, 11.2, 7.8, 64.5, 52.6, 84.8, 7.0, SPITZER, ["270", "270win"]),
        c("7 mm-08 Remington", RIMLESS, 12.0, 12.0, 11.5, 8.0, 51.7, 41.0, 71.1, 7.2, SPITZER, ["7mm-08", "7-08"]),
        c("7x57 mm Mauser", RIMLESS, 12.0, 12.0, 10.9, 8.2, 57.0, 45.5, 78.0, 7.24, SPITZER, ["7x57"]),
        c("7x64 mm", RIMLESS, 12.0, 12.0, 11.3, 8.0, 64.0, 52.0, 84.0, 7.24, SPITZER, ["7x64"]),
        c("7 mm Remington Magnum", BELTED, 13.5, 13.0, 12.4, 8.0, 63.5, 54.0, 82.6, 7.2, SPITZER, ["7mmremmag", "7rm"]),
        c("7 mm PRC", RIMLESS, 13.4, 13.4, 13.0, 8.0, 63.5, 54.0, 90.3, 7.2, SPITZER, ["7prc"]),
        c("7.5x55 mm Swiss (GP 11)", RIMLESS, 12.6, 12.6, 11.6, 8.5, 55.6, 45.0, 77.5, 7.77, SPITZER, ["gp11", "gp 11", "7.5x55", "7.5", "7.5mm", "7.5swiss", "k31"]),
        # GP 1890 ("Patrone, Modell 1890", later "Scharfe Patrone 90/23", from about 1960 "7,5 mm GP 90/23"):
        # the original Schmidt-Rubin round of the IG 89/96, KarK 93/05, KG 97 and KG 00. Its bullet is
        # unusual: a lead body wrapped in two turns of paper (the white band above the case mouth) and a
        # long, blunt round nose under a steel cap (13.7 g, 29 mm long, 7.8 mm over the paper). Shorter case
        # than GP 11. Not to be confused with the 5.6 mm GP 90 of the Stgw 90.
        c("7.5x53.5 mm Swiss (GP 1890)", RIMLESS, 12.5, 12.4, 11.5, 8.6, 53.5, 42.5, 77.0, 7.8, PATCHED,
          ["gp1890", "gp 1890", "gp1890/03", "gp90/03", "gp90/23", "7.5 mm gp 90", "patrone 1890", "patrone 90/23",
           "7.5x53.5", "7.5x53", "schmidt-rubin", "ig89"]),
        c("7.5x54 mm French", RIMLESS, 12.25, 12.25, 11.2, 8.6, 54.0, 44.0, 76.0, 7.8, SPITZER, ["7.5x54"]),
        c("7.62x39 mm", RIMLESS, 11.35, 11.35, 10.07, 8.6, 38.7, 30.5, 56.0, 7.9, SPITZER, ["7.62x39", "762x39"]),
        c(".300 AAC Blackout", RIMLESS, 9.6, 9.6, 9.1, 8.4, 34.7, 31.0, 57.0, 7.8, SPITZER, ["300blk", "300blackout", "300aac"]),
        c("7.62x51 mm NATO", RIMLESS, 11.9, 11.9, 11.5, 8.7, 51.2, 39.6, 71.1, 7.82, SPITZER, ["7.62x51", "7.62nato", "762"]),
        c(".308 Winchester", RIMLESS, 11.9, 11.9, 11.5, 8.7, 51.2, 39.6, 71.1, 7.82, SPITZER, ["308", "308win"]),
        c(".30-06 Springfield", RIMLESS, 12.0, 12.0, 11.2, 8.6, 63.3, 49.5, 84.8, 7.82, SPITZER, ["30-06", "3006"]),
        c(".30-30 Winchester", RIMMED, 12.8, 10.7, 10.2, 8.5, 51.8, 38.5, 64.8, 7.82, FLAT, ["30-30", "3030"]),
        c(".300 Winchester Magnum", BELTED, 13.0, 13.0, 12.4, 8.6, 66.7, 58.5, 84.8, 7.82, SPITZER, ["300winmag", "300wm"]),
        c(".300 PRC", RIMLESS, 13.4, 13.4, 13.0, 8.6, 70.4, 59.0, 94.5, 7.82, SPITZER, ["300prc"]),
        c(".300 Norma Magnum", RIMLESS, 14.9, 14.9, 14.4, 8.6, 63.3, 54.0, 91.4, 7.82, SPITZER, ["300norma", "300nm"]),
        c(".303 British", RIMMED, 13.5, 11.7, 10.2, 8.6, 56.4, 42.5, 78.1, 7.92, SPITZER, ["303", "303brit"]),
        c("7.62x54 mm R", RIMMED, 14.5, 12.4, 11.6, 8.5, 53.6, 41.0, 77.2, 7.92, SPITZER, ["7.62x54r", "762x54r"]),
        c("8x57 mm IS", RIMLESS, 11.95, 11.95, 11.0, 9.1, 57.0, 47.0, 82.0, 8.2, SPITZER, ["8x57", "8x57is", "8mmmauser"]),
        c("8x68 mm S", RIMLESS, 13.3, 13.3, 12.4, 9.2, 67.5, 56.5, 87.5, 8.2, SPITZER, ["8x68"]),
        c("9.3x62 mm", RIMLESS, 12.0, 12.0, 11.5, 10.0, 62.0, 52.0, 83.6, 9.3, ROUND, ["9.3x62"]),
        c("9.3x74 mm R", RIMMED, 13.0, 11.9, 10.8, 10.0, 74.0, 58.0, 94.5, 9.3, ROUND, ["9.3x74r"]),
        c(".338 Lapua Magnum", RIMLESS, 14.9, 14.9, 14.4, 9.3, 69.2, 57.5, 93.5, 8.6, SPITZER, ["338lm", "338lapua", "338"]),
        c(".375 H&H Magnum", BELTED, 13.0, 13.0, 11.6, 10.3, 72.4, 62.0, 91.4, 9.5, ROUND, ["375h&h", "375hh"]),
        c(".416 Rigby", RIMLESS, 14.9, 14.9, 13.6, 11.6, 73.7, 59.0, 95.3, 10.6, ROUND, ["416rigby"]),
        straight(".45-70 Government", RIMMED, 15.2, 12.7, 12.2, 53.5, 64.8, 11.6, FLAT, ["45-70", "4570"]),
        c(".50 BMG", RIMLESS, 20.4, 20.4, 18.3, 14.0, 99.0, 76.0, 138.0, 12.98, SPITZER, ["50bmg", "12.7x99"]),
        # Added 2026-11, rifle batch 1: dimensions from the page named in INTRODUCED, rounded;
        # shoulder heights estimated for drawing.
        c("6.5x52 mm Carcano", RIMLESS, 11.45, 11.41, 10.94, 7.55, 52.5, 43.0, 76.5, 6.8, ROUND, ["6.5carcano", "6.5x52"]),
        c("6.5x50 mm SR Arisaka", RIMLESS, 12.08, 11.45, 10.4, 7.37, 51.0, 41.7, 76.0, 6.63, SPITZER, ["6.5arisaka", "6.5x50"]),
        c("7.7x58 mm Arisaka", RIMLESS, 12.07, 12.02, 11.0, 8.58, 57.8, 47.1, 79.6, 7.92, SPITZER, ["7.7arisaka", "7.7x58"]),
        c("8x50 mm R Lebel", RIMMED, 16.0, 13.77, 11.42, 8.85, 50.5, 39.4, 75.0, 8.3, SPITZER, ["8lebel", "8x50rlebel"]),
        c("8x56 mm R Mannlicher", RIMMED, 14.05, 12.47, 12.0, 9.2, 55.63, 44.4, 75.91, 8.35, SPITZER, ["8x56r"]),
        c("8x50 mm R Mannlicher", RIMMED, 14.11, 12.48, 12.01, 9.03, 50.38, 39.3, 76.21, 8.22, ROUND, ["8x50rmannlicher", "8x50r"]),
        c("7.35x51 mm Carcano", RIMLESS, 11.4, 11.4, 10.85, 8.32, 51.5, 41.2, 73.5, 7.57, SPITZER, ["7.35carcano", "7.35x51"]),
        c("6.5x54 mm Mannlicher-Schönauer", RIMLESS, 11.52, 11.47, 10.87, 7.56, 57.2, 47.8, 77.8, 6.7, ROUND, ["6.5x54ms", "6.5x54"]),
        c(".30-40 Krag", RIMMED, 13.8, 11.6, 10.7, 8.6, 58.8, 48.2, 78.5, 7.8, ROUND, ["30-40", "30-40krag", "30army"]),
        c("7.92x33 mm Kurz", RIMLESS, 11.95, 11.94, 11.4, 9.1, 33.0, 22.0, 48.0, 8.22, SPITZER, ["7.92kurz", "8mmkurz", "7.92x33"]),
        c("5.45x39 mm", RIMLESS, 10.0, 10.0, 9.25, 6.29, 39.82, 31.7, 57.0, 5.6, SPITZER, ["5.45x39", "545x39"]),
        c(".22 Hornet", RIMMED, 8.89, 7.57, 7.01, 6.17, 35.64, 27.4, 43.76, 5.69, SPITZER, ["22hornet", "5.6x35r"]),
        c(".25-06 Remington", RIMLESS, 12.0, 11.9, 11.2, 7.4, 63.3, 54.1, 82.6, 6.5, SPITZER, ["25-06"]),
        c(".257 Roberts", RIMLESS, 12.0, 12.0, 10.9, 7.4, 56.7, 47.6, 70.5, 6.5, SPITZER, ["257roberts"]),
        c(".280 Remington", RIMLESS, 12.0, 11.9, 11.2, 8.0, 64.5, 54.6, 84.6, 7.2, SPITZER, ["280rem"]),
        c(".35 Whelen", RIMLESS, 12.0, 12.0, 11.2, 9.8, 63.3, 51.3, 84.8, 9.1, ROUND, ["35whelen"]),
        c(".300 H&H Magnum", BELTED, 13.5, 13.0, 11.4, 8.6, 72.4, 61.8, 91.4, 7.8, SPITZER, ["300h&h", "300hh"]),
        c(".338 Winchester Magnum", BELTED, 13.5, 13.0, 12.5, 9.4, 63.5, 52.0, 84.8, 8.6, SPITZER, ["338winmag", "338wm"]),
        straight(".444 Marlin", RIMMED, 13.1, 11.95, 11.5, 56.5, 65.0, 10.9, FLAT, ["444marlin"]),
        straight(".458 Winchester Magnum", BELTED, 13.5, 13.0, 12.2, 63.5, 84.8, 11.63, ROUND, ["458winmag", "458wm"]),
        straight(".350 Legend", RIMLESS, 9.6, 9.9, 9.6, 43.0, 57.0, 9.07, SPITZER, ["350legend"]),
    ]),
    ("Schwarzpulver", [
        ball(".36 Rundkugel (.375)", 9.5, ["36", "36navy", ".375ball"]),
        ball(".44 Rundkugel (.454)", 11.5, ["44", "44ball", ".454", "454ball"]),
        ball(".45 Rundkugel (.440)", 11.2, ["45ball", ".440"]),
        ball(".50 Rundkugel (.490)", 12.4, ["50", "50ball", ".490"]),
        ball(".54 Rundkugel (.530)", 13.5, ["54", "54ball", ".530"]),
        minie(".58 Minié", 14.6, 25.0, ["58", "58minie"]),
        minie(".69 Minié", 17.3, 27.0, ["69", "69minie"]),
        c("10.4x38 mm R Vetterli", RIMMED, 17.6, 14.4, 13.4, 11.4, 38.0, 25.0, 58.5, 10.8, ROUND, ["vetterli", "10.4", "10.4vetterli", "10.4x38"]),
        straight(".577 Snider", RIMMED, 19.2, 17.0, 16.4, 50.8, 62.0, 14.6, ROUND, ["577snider"]),
        c(".577/450 Martini-Henry", RIMMED, 19.0, 17.0, 16.0, 12.3, 59.7, 38.0, 79.0, 11.6, ROUND, ["martini-henry", "577/450"]),
        straight(".50-70 Government", RIMMED, 16.9, 14.2, 13.4, 44.5, 57.0, 13.0, ROUND, ["50-70"]),
        c(".44-40 WCF", RIMMED, 13.1, 11.9, 11.5, 11.1, 33.2, 22.0, 40.6, 10.8, FLAT, ["44-40", "4440"]),
    ]),
    ("Flinte", [
        shot("12/70", 20.6, 22.3, 64.0, ["12", "12/70", "12ga", "12gauge"]),
        shot("12/76", 20.6, 22.3, 70.0, ["12/76"]),
        shot("12/89", 20.6, 22.3, 82.0, ["12/89"]),
        shot("16/70", 18.9, 20.5, 64.0, ["16", "16/70"]),
        shot("20/70", 17.6, 19.0, 64.0, ["20", "20/70"]),
        shot("20/76", 17.6, 19.0, 70.0, ["20/76"]),
        shot("28/70", 16.0, 17.5, 64.0, ["28", "28/70"]),
        shot(".410/76", 11.8, 13.3, 70.0, [".410", "410"]),
    ]),
    ("Luftdruck", [
        pellet("4.5 mm Diabolo (.177)", 4.5, 5.5, ["4.5", "4.5mm", "177", "luftgewehr", "lg", "lp"]),
        pellet("5.5 mm Diabolo (.22)", 5.5, 6.5, ["5.5", "5.5mm"]),
    ]),
]

# Printable alternative names (max 2), shown in the app's calibre lists and search,
# and on the calibre poster. Never alias calibres that are separate cartridges:
# .223 Rem / 5.56 NATO / GP 90 and .308 Win / 7.62 NATO differ in loading and are
# not necessarily interchangeable, so each stays its own entry.
DISPLAY_ALIASES = {
    ".22 LR": [".22 Long Rifle", "KK"],
    ".22 WMR": [".22 Magnum"],
    "7.65 mm Browning (.32 ACP)": [".32 ACP", ".32 Auto"],
    "7.65 mm Parabellum": [".30 Luger"],
    "9 mm Browning kurz (.380 ACP)": [".380 ACP", ".380 Auto"],
    "9x19 mm": ["9 mm Luger", "9 mm Para"],
    ".38 Special": [".38 Spl"],
    ".45 ACP": [".45 Auto", "11,43 mm"],
    ".45 Colt": [".45 Long Colt"],
    ".30-06 Springfield": ["7.62x63 mm"],
    ".300 AAC Blackout": [".300 BLK", "7.62x35 mm"],
    "7.5x55 mm Swiss (GP 11)": ["GP 11", "7.5 mm Swiss"],
    "7.5x53.5 mm Swiss (GP 1890)": ["GP 1890", "GP 90/23"],
    "8x57 mm IS": ["8 mm Mauser"],
    ".50 BMG": ["12,7x99 mm NATO"],
}

# Primer per calibre (Boxer sizes of commercial, reloadable brass). Primers sit in the
# centre of the case head. Military surplus can be Berdan-primed with other sizes
# (e.g. 7.62x39, 7.62x54R, 7.5x54 French); rimfire and caseless entries have none.
SMALL_PISTOL, LARGE_PISTOL, SMALL_RIFLE, LARGE_RIFLE, SHOTSHELL_209, BMG_35 = (
    "small-pistol", "large-pistol", "small-rifle", "large-rifle", "shotshell-209", "bmg-35")
PRIMER_DIAMETERS = {  # mm, nominal primer cup diameter
    SMALL_PISTOL: 4.45, SMALL_RIFLE: 4.45,     # .175"
    LARGE_PISTOL: 5.33, LARGE_RIFLE: 5.33,     # .210"
    SHOTSHELL_209: 6.15,                       # .242"
    BMG_35: 8.03,                              # .316", CCI #35
}
PRIMERS = {
    "6.35 mm Browning (.25 ACP)": SMALL_PISTOL, "7.65 mm Browning (.32 ACP)": SMALL_PISTOL,
    "7.65 mm Parabellum": SMALL_PISTOL, ".32 S&W Long": SMALL_PISTOL, ".32 H&R Magnum": SMALL_PISTOL,
    "7.62x25 mm Tokarev": SMALL_PISTOL, "9 mm Browning kurz (.380 ACP)": SMALL_PISTOL,
    "7.63x25 mm Mauser": SMALL_PISTOL, "7.62x38 mm R Nagant": SMALL_PISTOL, "7.5 mm Swiss Ordnance 1882": SMALL_PISTOL,
    "7.65 mm Longue": SMALL_PISTOL, ".30 Super Carry": SMALL_PISTOL, ".32 S&W": SMALL_PISTOL,
    ".327 Federal Magnum": SMALL_PISTOL, ".32-20 Winchester": SMALL_PISTOL, "5.45x18 mm": SMALL_PISTOL,
    ".22 TCM": SMALL_RIFLE, "8 mm Nambu": SMALL_PISTOL, "8 mm Lebel revolver": SMALL_PISTOL,
    "8 mm Roth-Steyr": SMALL_PISTOL, "9 mm Glisenti": SMALL_PISTOL, "9 mm Browning Long": SMALL_PISTOL,
    "9x23 mm Steyr": SMALL_PISTOL, "9x23 mm Largo": SMALL_PISTOL, ".38 S&W": SMALL_PISTOL,
    ".38 Short Colt": SMALL_PISTOL, ".38 Long Colt": SMALL_PISTOL, ".38-40 Winchester": LARGE_PISTOL,
    "10.4 mm Swiss Ordnance 1878": LARGE_PISTOL, ".44 S&W Russian": LARGE_PISTOL, "11 mm French Ordnance": LARGE_PISTOL,
    ".45 Schofield": LARGE_PISTOL, ".45 Auto Rim": LARGE_PISTOL, ".455 Webley": LARGE_PISTOL,
    ".480 Ruger": LARGE_PISTOL, ".50 Action Express": LARGE_PISTOL,
    "9x18 mm Makarov": SMALL_PISTOL, "9x19 mm": SMALL_PISTOL, "9x21 mm IMI": SMALL_PISTOL,
    ".357 SIG": SMALL_PISTOL, ".38 Special": SMALL_PISTOL, ".357 Magnum": SMALL_PISTOL,
    ".38 Super": SMALL_PISTOL, "10 mm Auto": LARGE_PISTOL, ".40 S&W": SMALL_PISTOL,
    ".41 Magnum": LARGE_PISTOL, ".44 Special": LARGE_PISTOL, ".44 Magnum": LARGE_PISTOL,
    ".45 ACP": LARGE_PISTOL, ".45 Colt": LARGE_PISTOL, ".45 GAP": SMALL_PISTOL,
    ".454 Casull": SMALL_RIFLE, ".460 S&W Magnum": LARGE_RIFLE, ".500 S&W Magnum": LARGE_RIFLE,
    "5.7x28 mm": SMALL_RIFLE, "4.6x30 mm": SMALL_RIFLE,
    ".204 Ruger": SMALL_RIFLE, ".222 Remington": SMALL_RIFLE, ".223 Remington": SMALL_RIFLE,
    "5.56x45 mm NATO": SMALL_RIFLE, "5.6 mm GP 90 (Swiss)": SMALL_RIFLE, ".22-250 Remington": LARGE_RIFLE,
    ".243 Winchester": LARGE_RIFLE, "6 mm BR Norma": SMALL_RIFLE, "6 mm ARC": SMALL_RIFLE,
    "6.5 mm Creedmoor": LARGE_RIFLE, "6.5x55 mm Swedish": LARGE_RIFLE, "6.5x47 mm Lapua": SMALL_RIFLE,
    "6.5 PRC": LARGE_RIFLE, ".260 Remington": LARGE_RIFLE, ".270 Winchester": LARGE_RIFLE,
    "7 mm-08 Remington": LARGE_RIFLE, "7x57 mm Mauser": LARGE_RIFLE, "7x64 mm": LARGE_RIFLE,
    "7 mm Remington Magnum": LARGE_RIFLE, "7 mm PRC": LARGE_RIFLE, "7.5x55 mm Swiss (GP 11)": LARGE_RIFLE,
    "7.5x53.5 mm Swiss (GP 1890)": LARGE_RIFLE,
    "7.5x54 mm French": LARGE_RIFLE, "7.62x39 mm": SMALL_RIFLE, ".300 AAC Blackout": SMALL_RIFLE,
    "7.62x51 mm NATO": LARGE_RIFLE, ".308 Winchester": LARGE_RIFLE, ".30-06 Springfield": LARGE_RIFLE,
    ".30-30 Winchester": LARGE_RIFLE, ".300 Winchester Magnum": LARGE_RIFLE, ".300 PRC": LARGE_RIFLE,
    ".300 Norma Magnum": LARGE_RIFLE, ".303 British": LARGE_RIFLE, "7.62x54 mm R": LARGE_RIFLE,
    "8x57 mm IS": LARGE_RIFLE, "8x68 mm S": LARGE_RIFLE, "9.3x62 mm": LARGE_RIFLE, "9.3x74 mm R": LARGE_RIFLE,
    ".338 Lapua Magnum": LARGE_RIFLE, ".375 H&H Magnum": LARGE_RIFLE, ".416 Rigby": LARGE_RIFLE,
    ".45-70 Government": LARGE_RIFLE, ".50 BMG": BMG_35,
    "6.5x52 mm Carcano": LARGE_RIFLE, "6.5x50 mm SR Arisaka": LARGE_RIFLE, "7.7x58 mm Arisaka": LARGE_RIFLE,
    "8x50 mm R Lebel": LARGE_RIFLE, "8x56 mm R Mannlicher": LARGE_RIFLE, "8x50 mm R Mannlicher": LARGE_RIFLE,
    "7.35x51 mm Carcano": LARGE_RIFLE, "6.5x54 mm Mannlicher-Schönauer": LARGE_RIFLE,
    ".30-40 Krag": LARGE_RIFLE, "7.92x33 mm Kurz": LARGE_RIFLE, "5.45x39 mm": SMALL_RIFLE,
    ".22 Hornet": SMALL_RIFLE, ".25-06 Remington": LARGE_RIFLE, ".257 Roberts": LARGE_RIFLE,
    ".280 Remington": LARGE_RIFLE, ".35 Whelen": LARGE_RIFLE, ".300 H&H Magnum": LARGE_RIFLE,
    ".338 Winchester Magnum": LARGE_RIFLE, ".444 Marlin": LARGE_RIFLE, ".458 Winchester Magnum": LARGE_RIFLE,
    ".350 Legend": SMALL_RIFLE,
    # Vetterli: the original Swiss service round is rimfire; modern centrefire cases take large rifle.
    "10.4x38 mm R Vetterli": LARGE_RIFLE, ".577 Snider": LARGE_RIFLE, ".577/450 Martini-Henry": LARGE_RIFLE,
    ".50-70 Government": LARGE_RIFLE, ".44-40 WCF": LARGE_PISTOL,
    "12/70": SHOTSHELL_209, "12/76": SHOTSHELL_209, "12/89": SHOTSHELL_209, "16/70": SHOTSHELL_209,
    "20/70": SHOTSHELL_209, "20/76": SHOTSHELL_209, "28/70": SHOTSHELL_209, ".410/76": SHOTSHELL_209,
}

# Year each calibre was first introduced: released as factory ammunition or adopted for
# service (for a wildcat, the year it became a factory round; for a military round, the year
# of adoption). Each entry names the page the year was checked against. Calibres without a
# introduction year (shot shells, loose balls, pellets) are listed in INTRODUCED_UNKNOWN with
# the reason, so a new calibre has to be put in one of the two. Where sources disagree or give
# only a period, the earliest probable year is used.
_WP = "https://en.wikipedia.org/wiki/"
INTRODUCED = {
    ".22 Short": (1857, _WP + ".22_Short"),
    ".22 LR": (1887, _WP + ".22_Long_Rifle"),
    ".22 WMR": (1959, _WP + ".22_Winchester_Magnum_Rimfire"),
    ".17 HMR": (2002, _WP + ".17_Hornady_Magnum_Rimfire"),
    ".17 Mach 2": (2004, _WP + ".17_Hornady_Mach_2"),
    "6.35 mm Browning (.25 ACP)": (1905, _WP + ".25_ACP"),
    "7.65 mm Browning (.32 ACP)": (1899, _WP + ".32_ACP"),
    "7.65 mm Parabellum": (1898, _WP + "7.65×21mm_Parabellum"),
    ".32 S&W Long": (1896, _WP + ".32_S%26W_Long"),
    ".32 H&R Magnum": (1984, _WP + ".32_H%26R_Magnum"),
    "7.62x25 mm Tokarev": (1930, _WP + "7.62×25mm_Tokarev"),
    "9 mm Browning kurz (.380 ACP)": (1908, _WP + ".380_ACP"),
    "9x18 mm Makarov": (1951, _WP + "9×18mm_Makarov"),
    "9x19 mm": (1902, _WP + "9×19mm_Parabellum"),
    ".357 SIG": (1994, _WP + ".357_SIG"),
    ".38 Special": (1898, _WP + ".38_Special"),
    ".357 Magnum": (1935, _WP + ".357_Magnum"),
    ".38 Super": (1929, _WP + ".38_Super"),
    "10 mm Auto": (1983, _WP + "10mm_Auto"),
    ".40 S&W": (1990, _WP + ".40_S%26W"),
    ".41 Magnum": (1964, _WP + ".41_Remington_Magnum"),
    ".44 Special": (1907, _WP + ".44_Special"),
    ".44 Magnum": (1956, _WP + ".44_Magnum"),
    ".45 ACP": (1905, _WP + ".45_ACP"),           # designed 1904, produced from 1905
    ".45 Colt": (1873, _WP + ".45_Colt"),         # designed 1872, produced from 1873
    ".45 GAP": (2003, _WP + ".45_GAP"),
    ".454 Casull": (1997, _WP + ".454_Casull"),   # wildcat from 1958, commercial (SAAMI) 1997
    ".460 S&W Magnum": (2005, _WP + ".460_S%26W_Magnum"),
    ".500 S&W Magnum": (2003, _WP + ".500_S%26W_Magnum"),
    "5.7x28 mm": (1990, _WP + "FN_5.7×28mm"),
    "4.6x30 mm": (1999, _WP + "HK_4.6×30mm"),
    ".204 Ruger": (2004, _WP + ".204_Ruger"),
    ".222 Remington": (1950, _WP + ".222_Remington"),
    ".223 Remington": (1963, _WP + ".223_Remington"),
    "5.56x45 mm NATO": (1980, _WP + "5.56×45mm_NATO"),   # STANAG 4172, 28 Oct 1980
    "5.6 mm GP 90 (Swiss)": (1990, _WP + "SIG_SG_550"),  # adopted with the Stgw 90
    ".22-250 Remington": (1965, _WP + ".22-250_Remington"),  # wildcat from 1937
    ".243 Winchester": (1955, _WP + ".243_Winchester"),
    "6 mm BR Norma": (1996, _WP + "6mm_BR"),
    "6 mm ARC": (2020, _WP + "6mm_ARC"),
    "6.5 mm Creedmoor": (2007, _WP + "6.5mm_Creedmoor"),
    "6.5x55 mm Swedish": (1894, _WP + "6.5×55mm_Swedish"),
    "6.5x47 mm Lapua": (2005, _WP + "6.5×47mm_Lapua"),
    "6.5 PRC": (2018, _WP + "Hornady"),
    ".260 Remington": (1997, _WP + ".260_Remington"),
    ".270 Winchester": (1925, _WP + ".270_Winchester"),
    "7 mm-08 Remington": (1980, _WP + "7mm-08_Remington"),
    "7x57 mm Mauser": (1892, _WP + "7×57mm_Mauser"),
    "7x64 mm": (1917, _WP + "7×64mm"),
    "7 mm Remington Magnum": (1962, _WP + "7mm_Remington_Magnum"),
    "7 mm PRC": (2022, _WP + "Hornady"),
    "7.5x55 mm Swiss (GP 11)": (1911, _WP + "7.5×55mm_Swiss"),
    "7.5x54 mm French": (1929, _WP + "7.5×54mm_French"),
    "7.62x39 mm": (1943, _WP + "7.62×39mm"),
    ".300 AAC Blackout": (2010, _WP + ".300_AAC_Blackout"),
    "7.62x51 mm NATO": (1954, _WP + "7.62×51mm_NATO"),
    ".308 Winchester": (1952, _WP + ".308_Winchester"),
    ".30-06 Springfield": (1906, _WP + ".30-06_Springfield"),
    ".30-30 Winchester": (1895, _WP + ".30-30_Winchester"),
    ".300 Winchester Magnum": (1963, _WP + ".300_Winchester_Magnum"),
    ".300 PRC": (2018, _WP + "Hornady"),
    ".300 Norma Magnum": (2012, _WP + ".300_Norma_Magnum"),
    ".303 British": (1888, _WP + ".303_British"),
    "7.62x54 mm R": (1891, _WP + "7.62×54mmR"),
    "8x57 mm IS": (1903, _WP + "7.92×57mm_Mauser"),     # S bullet; the round-nosed Patrone 88 is 1888
    "8x68 mm S": (1939, _WP + "8×68mm_S"),
    "9.3x62 mm": (1905, _WP + "9.3×62mm"),
    ".338 Lapua Magnum": (1989, _WP + ".338_Lapua_Magnum"),
    ".375 H&H Magnum": (1912, _WP + ".375_H%26H_Magnum"),
    ".416 Rigby": (1912, _WP + ".416_Rigby"),           # designed 1911, produced from 1912
    ".45-70 Government": (1873, _WP + ".45-70"),
    ".50 BMG": (1921, _WP + ".50_BMG"),
    ".577 Snider": (1866, _WP + ".577_Snider"),
    ".577/450 Martini-Henry": (1871, _WP + ".577/450_Martini–Henry"),
    ".50-70 Government": (1866, _WP + ".50-70_Government"),
    ".44-40 WCF": (1873, _WP + ".44-40_Winchester"),
    "6.5x52 mm Carcano": (1890, _WP + "6.5×52mm_Carcano"),
    "6.5x50 mm SR Arisaka": (1897, _WP + "6.5×50mmSR_Arisaka"),
    "7.7x58 mm Arisaka": (1940, _WP + "7.7×58mm_Arisaka"),
    "8x50 mm R Lebel": (1886, _WP + "8×50mmR_Lebel"),
    "8x56 mm R Mannlicher": (1930, _WP + "8×56mmR"),
    "8x50 mm R Mannlicher": (1890, _WP + "8×50mmR_Mannlicher"),
    "7.35x51 mm Carcano": (1938, _WP + "7.35×51mm_Carcano"),
    "6.5x54 mm Mannlicher-Schönauer": (1900, _WP + "6.5×54mm_Mannlicher–Schönauer"),
    ".30-40 Krag": (1892, _WP + ".30-40_Krag"),
    "7.92x33 mm Kurz": (1942, _WP + "7.92×33mm_Kurz"),
    "5.45x39 mm": (1974, _WP + "5.45×39mm"),
    ".22 Hornet": (1930, _WP + ".22_Hornet"),
    ".25-06 Remington": (1969, _WP + ".25-06_Remington"),
    ".257 Roberts": (1934, _WP + ".257_Roberts"),
    ".280 Remington": (1957, _WP + ".280_Remington"),
    ".35 Whelen": (1988, _WP + ".35_Whelen"),
    ".300 H&H Magnum": (1925, _WP + ".300_H%26H_Magnum"),
    ".338 Winchester Magnum": (1958, _WP + ".338_Winchester_Magnum"),
    ".444 Marlin": (1964, _WP + ".444_Marlin"),
    ".458 Winchester Magnum": (1956, _WP + ".458_Winchester_Magnum"),
    ".350 Legend": (2019, _WP + ".350_Legend"),
    "7.63x25 mm Mauser": (1896, _WP + "7.63×25mm_Mauser"),
    "7.62x38 mm R Nagant": (1895, _WP + "7.62×38mmR"),
    "7.5 mm Swiss Ordnance 1882": (1880, _WP + "7.5mm_1882_Ordnance"),
    "7.65 mm Longue": (1917, _WP + "7.65×20mm_Long"),
    ".30 Super Carry": (2022, _WP + ".30_Super_Carry"),
    ".32 S&W": (1878, _WP + ".32_S%26W"),
    ".327 Federal Magnum": (2008, _WP + ".327_Federal_Magnum"),
    ".32-20 Winchester": (1882, _WP + ".32-20_Winchester"),
    "5.45x18 mm": (1973, _WP + "5.45×18mm"),
    "8 mm Nambu": (1904, _WP + "8×22mm_Nambu"),
    "8 mm Lebel revolver": (1892, _WP + "8mm_French_Ordnance"),
    "8 mm Roth-Steyr": (1907, _WP + "Roth–Steyr_M1907"),
    "9 mm Glisenti": (1909, _WP + "Glisenti_Model_1910"),
    "9 mm Browning Long": (1903, _WP + "9mm_Browning_Long"),
    "9x23 mm Steyr": (1912, _WP + "9×23mm_Steyr"),
    "9x23 mm Largo": (1905, _WP + "9×23mm_Largo"),
    ".38 S&W": (1877, _WP + ".38_S%26W"),
    ".38 Long Colt": (1875, _WP + ".38_Long_Colt"),
    ".38-40 Winchester": (1874, _WP + ".38-40_Winchester"),
    "10.4 mm Swiss Ordnance 1878": (1878, _WP + "10.4mm_Swiss_Centerfire"),
    ".44 S&W Russian": (1870, _WP + ".44_S%26W_Russian"),
    "11 mm French Ordnance": (1873, _WP + "11mm_French_Ordnance"),
    ".45 Schofield": (1875, _WP + ".45_Schofield"),
    ".45 Auto Rim": (1920, _WP + ".45_Auto_Rim"),
    ".455 Webley": (1891, _WP + ".455_Webley"),
    ".480 Ruger": (2003, _WP + ".480_Ruger"),
    ".50 Action Express": (1988, _WP + ".50_Action_Express"),
    # Sources disagree or give only a period: the earliest probable year is used.
    "9x21 mm IMI": (1980, _WP + "9×21mm"),                         # "1980–present", text says the 1980s
    "7.5x53.5 mm Swiss (GP 1890)": (1889, _WP + "7.5×55mm_Swiss"),  # named Modell 1890, in service 1889
    "10.4x38 mm R Vetterli": (1867, _WP + ".41_Swiss"),             # adopted 1867, issued with the rifle 1869
    "9.3x74 mm R": (1900, _WP + "9.3×74mmR"),                       # "c. 1900"
}

INTRODUCED_UNKNOWN = {
    ".22 TCM": "no year in the source",
    ".38 Short Colt": "no year in the source",
    # Not one cartridge with one launch: shot shell sizes, loose balls and air gun pellets.
    **{n: "not a single cartridge" for n in (
        "12/70", "12/76", "12/89", "16/70", "20/70", "20/76", "28/70", ".410/76",
        ".36 Rundkugel (.375)", ".44 Rundkugel (.454)", ".45 Rundkugel (.440)", ".50 Rundkugel (.490)",
        ".54 Rundkugel (.530)", ".58 Minié", ".69 Minié", "4.5 mm Diabolo (.177)", "5.5 mm Diabolo (.22)")},
}

# Calibres no longer in regular factory production (only surplus, boutique loads or reloading).
# Everything else is current. The apps can hide these by default; the poster can mark them.
OBSOLETE = {
    "7.5x53.5 mm Swiss (GP 1890)", "10.4x38 mm R Vetterli", ".577 Snider", ".577/450 Martini-Henry",
    ".50-70 Government", ".58 Minié", ".69 Minié",
    "7.5 mm Swiss Ordnance 1882", "7.65 mm Longue", "8 mm Nambu", "8 mm Lebel revolver", "8 mm Roth-Steyr",
    "9 mm Glisenti", "9x23 mm Steyr", "9x23 mm Largo", ".38 Long Colt", "10.4 mm Swiss Ordnance 1878",
    "11 mm French Ordnance",
    "8x50 mm R Mannlicher", "7.35x51 mm Carcano",
}


def is_obsolete(name):
    return name in OBSOLETE
