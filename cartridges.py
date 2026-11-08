"""Calibre catalogue with approximate cartridge dimensions (mm, CIP/SAAMI-ish).

Shared by Schiesstagebuch, Kaliberfinder and the calibre wall poster (each pins this
repository as a git submodule); outline.py draws the side view of every calibre.
Dimensions are approximations for drawings and matching, not reloading data.
"""

# Kinds
RIMLESS, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET = (
    "rimless", "rimmed", "belted", "rimfire", "shot", "ball", "minie", "pellet")
# Bullet profiles. PATCHED: paper-patched lead body with a steel-capped round nose (GP 1890).
# CRIMPED: no bullet; the case mouth is folded shut in a star (blanks and power-tool loads).
SPITZER, ROUND, FLAT, PATCHED, CRIMPED = "spitzer", "round", "flat", "patched", "crimped"


def c(name, kind, rim, base, shoulder, neck, case, sh_at, oal, bullet, profile, aliases=()):
    return dict(name=name, kind=kind, rim=rim, base=base, shoulder=shoulder, neck=neck,
                case=case, sh_at=sh_at, oal=oal, bullet=bullet, profile=profile, aliases=list(aliases))


def straight(name, kind, rim, base, neck, case, oal, bullet, profile, aliases=()):
    return c(name, kind, rim, base, None, neck, case, None, oal, bullet, profile, aliases)


def blank(name, rim, base, mouth, length, aliases=(), kind=RIMFIRE):
    """A crimped blank: no bullet, the case (`length` long) narrows to `mouth` at the star crimp.
    `bullet` holds the nominal bore so drawings and tables keep a width."""
    return c(name, kind, rim, base, None, mouth, length, None, length, base, CRIMPED, aliases)


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
        straight(".22 WMR", RIMFIRE, 7.5, 6.1, 6.1, 26.8, 34.3, 5.7, SPITZER, ["22mag", "22wmr"]),
        c(".17 HMR", RIMFIRE, 7.5, 6.1, 6.1, 4.5, 26.9, 22.2, 32.8, 4.4, SPITZER, ["17hmr"]),
        c(".17 Mach 2", RIMFIRE, 6.9, 5.7, 5.7, 4.5, 18.0, 14.23, 25.0, 4.4, SPITZER),
        # Added 2026-11: dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        straight(".22 Long", RIMFIRE, 6.9, 5.7, 5.7, 15.6, 22.6, 5.7, ROUND, ["22long"]),
        # Measured specimens on municion.org (AECC drawings 06-020-CBR-010, 08-014-CBR-020, 08-020-CBR-020).
        straight(".22 Extra Long", RIMFIRE, 6.95, 5.74, 5.72, 19.83, 29.89, 5.63, ROUND, ["22extralong", "22xl"]),
        straight(".32 Short Rimfire", RIMFIRE, 9.47, 8.02, 8.02, 14.22, 23.79, 7.88, ROUND, ["32shortrf", "32rfshort"]),
        straight(".32 Long Rimfire", RIMFIRE, 9.51, 8.09, 8.09, 20.0, 30.85, 7.92, ROUND, ["32longrf", "32rflong"]),
        straight(".22 BB Cap", RIMFIRE, 6.9, 5.7, 5.7, 7.2, 8.7, 5.7, ROUND, ["22bb", "bbcap", "flobert"]),
        # 9 mm Flobert ball round (BB cap with a round ball, «Bosquette»), Wikipedia infobox, rounded.
        # Raven's copper-cased specimen (2026-11-08) measured ball 8.5, rim 10.3, case 9.4, length 14.0.
        straight("9 mm Flobert Bosquette", RIMFIRE, 10.16, 8.85, 8.85, 10.18, 14.98, 8.84, ROUND,
                 ["9mmflobert", "9flobert", "bosquette", "9mmbosquette", "9mmbbcap", "flobertkugel", "9mmflobertkugel"]),
        c("5 mm Remington Rimfire Magnum", RIMFIRE, 8.3, 6.6, 6.6, 5.7, 25.9, 20.22, 33.0, 5.2, SPITZER, ["5mmrmr", "5rmr"]),
        c(".17 Winchester Super Magnum", RIMFIRE, 8.5, 6.8, 6.8, 5.0, 30.5, 24.75, 36.6, 4.4, SPITZER, ["17wsm"]),
        # Batch 8 (2026-11): old American sporting rounds; dimensions from the page named in INTRODUCED, rounded (.32 Remington from the .25 Remington family); shoulder heights estimated.
        straight(".22 Winchester Rimfire", RIMFIRE, 7.6, 6.24, 6.18, 24.5, 30.0, 5.8, ROUND, ["22wrf"]),
        # .22 crimped blank, the size of the yellow/green/red power-tool loads and starter pistol
        # blanks ("6.8/11": 6.8 mm rim, 11 mm long). Crimp shape after fired ones in Raven's
        # photos (2026-11-04): the star opens on firing but the petals stay narrower than the body.
        blank(".22 Blank (6.8/11)", 6.8, 5.7, 3.4, 11.0,
              ["22blank", "6.8/11", "6.8x11", "platzpatrone", "kartusche", "setzkartusche", "bolzensetzer"]),
        # 9 mm P.A.K. alarm-pistol blank and gas round (centrefire), C.I.P. Tab. VIII "9 mm PA Blanc"
        # maximum cartridge (sheet 1991-07-30); length = L3 (L6 is 22.7). The front is closed inside the
        # case, not star-crimped, so it is a plain cylinder with nothing above the mouth (Raven 2026-11-04).
        straight("9 mm P.A.K.", RIMLESS, 9.5, 9.5, 9.5, 22.5, 22.5, 9.5, FLAT,
                 ["9mmpak", "pak", "9pak", "9x22", "9mmpa", "9mmpablanc", "gaspatrone", "reizstoffpatrone"]),
        # Alarm and starter blanks from C.I.P. Tab. VIII, maximum cartridge (sheets 1991-07-29 to
        # 1991-08-02). Closed-front ones (8 mm, .315) are plain cylinders like the 9 mm P.A.K., length = L3.
        # Star-crimped ones use L6 (the crimped length); their mouth is estimated at 0.6 x the base,
        # the ratio of the measured .22 blank above, because C.I.P. gives no crimp size.
        straight("8 mm Knall", RIMLESS, 8.0, 8.0, 8.0, 20.3, 20.3, 8.0, FLAT,
                 ["8mmknall", "8mmpak", "8pak", "8x20", "8mmblanc", "8mmblank"]),
        straight(".315 Knall", RIMLESS, 8.0, 8.0, 8.0, 17.65, 17.65, 8.0, FLAT,
                 ["315knall", "315", "315blanc"]),
        blank("9 mm R Knall", 11.0, 9.58, 5.7, 17.5,
              ["9mmrk", "9rk", "9mmr", "380r", "380knall", "9x17r", "revolverknall"], kind=RIMMED),
        blank(".320 Knall", 9.55, 8.09, 4.9, 16.0, ["320knall", "320", "320blanc"], kind=RIMMED),
        blank(".45 Knall", 13.0, 12.1, 7.3, 16.6, ["45knall", "45k", "45shortknall", "45kblanc"], kind=RIMMED),
        blank(".22 Long Knall", 7.06, 5.74, 3.4, 15.0, ["22longknall", "22langknall", "22longblank", "5.6/16", "5.6x16"]),
        blank("6 mm Flobert Knall", 7.15, 5.75, 3.4, 6.6, ["6mmflobert", "6mmknall", "6mmflobertblanc", "flobertknall"]),
        straight(".44 Henry", RIMFIRE, 13.2, 11.2, 11.0, 22.9, 34.2, 11.3, FLAT, ["44henry"]),
        # Batch 12 (2026-11): British Nitro and Rigby rounds, .310 Cadet, Portuguese 6.5x58, .30 R Blaser, .22 Rem Auto; dimensions from the page named in INTRODUCED (.475 No. 2 from its Wikipedia page), rounded; shoulder heights estimated.
        straight(".22 Remington Automatic", RIMFIRE, 7.4, 6.2, 6.2, 16.8, 23.4, 5.7, ROUND, ["22remauto"]),
        # Batch 11 (2026-11): old rimfire, black-powder and British rounds plus 9x25 Dillon and .300 Lapua; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        straight(".25 Stevens", RIMFIRE, 8.5, 7.0, 7.0, 28.6, 35.4, 6.4, FLAT, ["25stevens"]),
        straight(".41 Short", RIMFIRE, 11.9, 10.3, 10.3, 11.9, 23.2, 10.3, ROUND, ["41short", "41rf"]),
        straight(".56-56 Spencer", RIMFIRE, 16.4, 14.2, 14.2, 22.2, 39.2, 14.0, ROUND, ["56-56", "spencer"]),
    ]),
    ("Kurzwaffe", [
        straight("6.35 mm Browning (.25 ACP)", RIMLESS, 7.6, 7.1, 7.0, 15.6, 23.1, 6.4, ROUND, ["6.35", "25acp", "25auto"]),
        straight("7.65 mm Browning (.32 ACP)", RIMLESS, 9.1, 8.6, 8.5, 17.3, 25.0, 7.9, ROUND, ["7.65browning", "32acp", "32auto"]),
        # Swiss Army box label «Pistolen-Patronen Cal. 7,65 mm» (Raven's 1938 M+F Thun box); Ordonnanzpistole 1900.
        c("7.65 mm Parabellum", RIMLESS, 9.9, 9.9, 9.7, 8.4, 21.6, 15.58, 29.8, 7.85, ROUND, ["7.65para", "30luger", "pistolenpatrone 7.65"]),
        straight(".32 S&W Long", RIMMED, 9.5, 8.6, 8.5, 23.4, 32.5, 7.9, ROUND, ["32s&w", "32swl", "32long"]),
        # Target load for ISSF 25 m centre-fire pistols, its own C.I.P. cartridge ("32 S&W Long Wad Cut.",
        # tab-iv/tabivcal-en-page46.pdf, sheet 1984-06-14, origin DE/FI): higher pressure (Pmax 1550 bar against 1000) and a
        # chamber with a 3 mm instead of 11 mm throat, so C.I.P. treats it as its own cartridge on the same
        # case. Maximum cartridge R1/P1/H2/G1/L3 from the sheet. Drawn with the wadcutter seated flush with
        # the case mouth, as it is usually loaded (https://bullseyeforum.net/t16197-32-sw-long-wadcutter-oal),
        # so the length is L3 (L6 allows up to 25.40) and no bullet shows from the side.
        straight(".32 S&W Long Wadcutter", RIMMED, 9.53, 8.56, 8.56, 23.27, 23.27, 8.0, FLAT,
                 ["32wc", "32swlwc", "32longwc", "32 s&w long wc", "32 s&w lwc"]),
        straight(".32 H&R Magnum", RIMMED, 9.5, 8.6, 8.5, 27.4, 34.3, 7.9, FLAT),
        c("7.62x25 mm Tokarev", RIMLESS, 9.9, 9.9, 9.6, 8.5, 24.7, 19.6, 34.9, 7.85, ROUND, ["tokarev", "7.62tok"]),
        straight("9 mm Browning kurz (.380 ACP)", RIMLESS, 9.5, 9.5, 9.4, 17.3, 25.0, 9.0, ROUND, ["380acp", "380auto", "9kurz", "9mmkurz"]),
        straight("9x18 mm Makarov", RIMLESS, 9.9, 9.9, 9.7, 18.1, 25.0, 9.27, ROUND, ["makarov"]),
        # Swiss Army name «9 mm Pistolenpatrone 41», short «9 mm Pist Pat 41» (Raven's 1955 Thun box «scharfe
        # Pistolenpatronen 41 9 mm»; sigforum.com thread "PISTOLENPATRONE 41 9mm ammo").
        straight("9x19 mm", RIMLESS, 9.96, 9.96, 9.65, 19.15, 29.7, 9.01, ROUND, ["9x19", "9mm", "9mmpara", "9para", "9mmluger", "9luger", "9x19para", "parabellum",
                 "pist pat 41", "pistolenpatrone 41", "9 mm pist pat 41"]),
        straight("9x21 mm IMI", RIMLESS, 9.96, 9.96, 9.65, 21.15, 29.7, 9.01, ROUND, ["9x21"]),
        c(".357 SIG", RIMLESS, 10.77, 10.77, 10.7, 9.68, 21.97, 16.48, 28.96, 9.02, ROUND, ["357sig"]),
        straight(".38 Special", RIMMED, 11.2, 9.6, 9.6, 29.3, 39.4, 9.07, ROUND, ["38spl", "38special", "38"]),
        straight(".357 Magnum", RIMMED, 11.2, 9.6, 9.6, 32.8, 40.6, 9.07, FLAT, ["357mag", "357", "357magnum"]),
        straight(".38 Super", RIMLESS, 10.2, 9.7, 9.6, 22.9, 32.5, 9.03, ROUND, ["38super"]),
        straight("10 mm Auto", RIMLESS, 10.8, 10.8, 10.7, 25.2, 32.0, 10.17, FLAT, ["10mm", "10auto"]),
        straight(".40 S&W", RIMLESS, 10.8, 10.8, 10.7, 21.6, 28.8, 10.17, FLAT, ["40s&w", "40sw", "40"]),
        # Mixed batch 4 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated; 7x65 R and 8x57 IRS rims estimated like 9.3x74 R.
        c(".400 Cor-Bon", RIMLESS, 12.0, 11.9, 11.85, 10.7, 22.8, 17.21, 30.0, 10.2, FLAT, ["400corbon"]),
        straight("9x23 mm Winchester", RIMLESS, 10.01, 9.93, 9.68, 22.86, 33.02, 9.04, ROUND, ["9x23win"]),
        straight(".356 TSW", RIMLESS, 10.0, 9.92, 9.7, 21.6, 29.5, 9.0, ROUND, ["356tsw"]),
        # Batch 6 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".22 Remington Jet", RIMMED, 11.2, 9.6, 8.9, 6.3, 33.0, 15.19, 40.0, 5.6, SPITZER, ["22jet"]),
        c(".256 Winchester Magnum", RIMMED, 11.2, 9.7, 9.3, 7.2, 32.5, 24.77, 40.4, 6.5, FLAT, ["256win"]),
        straight(".41 Magnum", RIMMED, 12.5, 11.0, 11.0, 32.8, 40.4, 10.4, FLAT, ["41mag"]),
        straight(".44 Special", RIMMED, 13.1, 11.6, 11.6, 29.5, 37.0, 10.9, FLAT, ["44spl", "44special"]),
        straight(".44 Magnum", RIMMED, 13.1, 11.6, 11.6, 32.6, 40.9, 10.9, FLAT, ["44mag", "44magnum"]),
        straight(".45 ACP", RIMLESS, 12.0, 12.0, 12.0, 22.8, 32.4, 11.5, ROUND, ["45acp", "45auto", "45", "11.43"]),
        # Batch 14 (2026-11): .378 Weatherby, 7.5 FK and 6 mm GT (SAAMI drawing; neck estimated); dimensions from the page named in INTRODUCED, rounded.
        c("7.5 FK", RIMLESS, 10.8, 10.8, 10.8, 8.5, 27.0, 20.85, 35.0, 7.8, ROUND, ["7.5fk", "fk brno"]),
        # Batch 11 (2026-11): old rimfire, black-powder and British rounds plus 9x25 Dillon and .300 Lapua; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c("9x25 mm Dillon", RIMLESS, 10.8, 10.8, 10.7, 9.7, 25.1, 19.9, 31.8, 9.0, ROUND, ["9x25", "9x25dillon"]),
        # Round nose with a small flat, as factory lead loads come (Winchester X45CP2 "255 gr Lead Round
        # Nose", Raven's W-W round photographed 2026-11-08), not the wide flat point; the 1873 original
        # was an "ogival & flat nosed" 255 gr bullet (Wikipedia).
        straight(".45 Colt", RIMMED, 12.9, 12.2, 12.2, 32.6, 40.6, 11.5, ROUND, ["45colt", "45lc", "45longcolt"]),
        straight(".45 GAP", RIMLESS, 12.0, 12.0, 12.0, 19.2, 27.3, 11.5, ROUND, ["45gap"]),
        straight(".454 Casull", RIMMED, 13.1, 12.1, 12.1, 35.1, 45.0, 11.5, FLAT, ["454casull"]),
        straight(".460 S&W Magnum", RIMMED, 13.2, 12.2, 12.2, 45.7, 58.0, 11.5, FLAT, ["460s&w"]),
        straight(".500 S&W Magnum", RIMMED, 14.2, 13.4, 13.4, 41.3, 57.2, 12.7, FLAT, ["500s&w"]),
        c("5.7x28 mm", RIMLESS, 7.9, 7.9, 7.8, 6.4, 28.9, 23.15, 40.5, 5.7, SPITZER, ["5.7x28", "57x28"]),
        c("4.6x30 mm", RIMLESS, 8.0, 8.0, 7.8, 5.3, 30.5, 23.02, 38.7, 4.65, SPITZER, ["4.6x30"]),
        # Added 2026-11: further mass-produced handgun rounds, current and obsolete. Dimensions from
        # the page named in INTRODUCED (mostly the Wikipedia infobox, which quotes C.I.P./SAAMI),
        # rounded; shoulder heights of bottleneck cases are estimated for drawing.
        c("7.63x25 mm Mauser", RIMLESS, 9.98, 9.86, 9.6, 8.46, 25.15, 19.28, 34.8, 7.86, ROUND, ["7.63mauser", "30mauser"]),
        straight("7.62x38 mm R Nagant", RIMMED, 9.86, 8.94, 7.26, 38.86, 38.86, 7.82, ROUND, ["nagant", "7.62nagant"]),
        straight("7.5 mm Swiss Ordnance 1882", RIMMED, 10.4, 8.4, 8.4, 22.8, 34.6, 8.0, ROUND, ["7.5ord", "7.5revolver", "revolver82"]),
        straight("7.65 mm Longue", RIMLESS, 8.5, 8.53, 8.5, 19.7, 30.24, 7.85, ROUND, ["7.65longue", "7.65mas", "30pedersen"]),
        straight(".30 Super Carry", RIMLESS, 8.74, 8.7, 8.56, 21.0, 29.7, 7.93, ROUND, ["30sc", "30supercarry"]),
        straight(".32 S&W", RIMMED, 9.5, 8.5, 8.5, 15.0, 23.0, 7.9, ROUND, ["32s&wshort", "32sws"]),
        # Webley's 1868 Bull Dog round, C.I.P. «320 Short» (tab-iv/tabivcal-en-page48.pdf, sheet 1984-06-14,
        # origin GB), maximum cartridge R1/P1/H2/G1/L3/L6. Raven's G.F.L. (Fiocchi) round measured rim 9.5,
        # base 8.0, case 16.4, length 24.9 (2026-11-08).
        straight(".320 Revolver", RIMMED, 9.55, 8.12, 8.12, 16.6, 26.7, 8.0, ROUND,
                 ["320rev", "320revolver", "320short", "320 short", "320bulldog", "320 bulldog"]),
        straight(".327 Federal Magnum", RIMMED, 9.5, 8.6, 8.6, 30.0, 37.0, 7.9, FLAT, ["327fed", "327federal"]),
        c(".32-20 Winchester", RIMMED, 10.4, 9.0, 8.7, 8.3, 33.4, 22.35, 40.4, 7.94, FLAT, ["32-20", "32wcf"]),
        c("5.45x18 mm", RIMLESS, 7.64, 7.64, 7.4, 6.26, 18.03, 12.07, 25.0, 5.63, SPITZER, ["5.45x18", "psm"]),
        c(".22 TCM", RIMLESS, 9.6, 9.55, 9.19, 6.48, 25.96, 17.72, 32.13, 5.7, SPITZER, ["22tcm"]),
        c("8 mm Nambu", RIMLESS, 10.5, 10.23, 10.0, 8.71, 21.43, 15.35, 31.56, 8.13, ROUND, ["nambu", "8nambu"]),
        straight("8 mm Lebel revolver", RIMMED, 10.43, 8.96, 8.83, 27.5, 36.7, 8.35, ROUND, ["8lebelrev", "8mm1892"]),
        straight("8 mm Roth-Steyr", RIMLESS, 8.85, 8.85, 8.8, 18.65, 29.0, 8.16, ROUND, ["rothsteyr", "8steyr"]),
        straight("9 mm Glisenti", RIMLESS, 9.98, 9.96, 9.65, 19.15, 29.21, 9.02, ROUND, ["glisenti"]),
        straight("9 mm Browning Long", RIMLESS, 10.2, 9.72, 9.68, 20.2, 28.0, 9.09, ROUND, ["9browninglong", "9x20sr"]),
        straight("9x23 mm Steyr", RIMLESS, 9.7, 9.7, 9.62, 23.2, 32.99, 9.03, ROUND, ["9steyr"]),
        straight("9x23 mm Largo", RIMLESS, 9.9, 9.91, 9.7, 23.1, 33.53, 9.0, ROUND, ["9largo", "bergmann-bayard"]),
        straight(".38 S&W", RIMMED, 11.2, 9.82, 9.79, 19.7, 31.5, 9.2, ROUND, ["38s&w", "38sw", "380-200"]),
        straight(".38 Short Colt", RIMMED, 11.3, 9.6, 9.6, 19.4, 30.48, 9.1, ROUND, ["38shortcolt"]),
        straight(".38 Long Colt", RIMMED, 11.3, 9.7, 9.7, 26.2, 34.54, 9.1, ROUND, ["38longcolt", "38lc"]),
        c(".38-40 Winchester", RIMMED, 13.3, 11.93, 11.54, 10.58, 33.1, 23.42, 40.0, 10.17, FLAT, ["38-40", "38wcf"]),
        straight("10.4 mm Swiss Ordnance 1878", RIMMED, 13.3, 11.2, 10.8, 20.0, 32.0, 10.76, ROUND, ["10.4revolver", "revolver78"]),
        straight(".44 S&W Russian", RIMMED, 13.1, 11.6, 11.6, 24.6, 36.3, 10.9, ROUND, ["44russian"]),
        straight("11 mm French Ordnance", RIMMED, 12.5, 11.45, 11.45, 17.0, 30.0, 11.46, ROUND, ["11mmfrench", "11mm1873"]),
        straight(".45 Schofield", RIMMED, 13.2, 12.2, 12.2, 27.9, 36.3, 11.5, FLAT, ["45schofield", "45s&w"]),
        straight(".45 Auto Rim", RIMMED, 13.09, 11.96, 11.9, 22.87, 32.12, 11.5, ROUND, ["45autorim", "45ar"]),
        straight(".455 Webley", RIMMED, 13.5, 12.2, 12.1, 19.6, 31.2, 11.5, ROUND, ["455webley", "455"]),
        straight(".480 Ruger", RIMLESS, 13.7, 12.8, 12.8, 32.6, 41.9, 12.1, FLAT, ["480ruger"]),
        straight(".50 Action Express", RIMLESS, 13.1, 13.8, 13.5, 32.6, 40.9, 12.7, FLAT, ["50ae"]),
        # Handgun batch 2 (2026-11): dimensions from the page named in INTRODUCED, rounded. .45 Super uses the .45 ACP case outside.
        straight("9x18 mm Ultra", RIMLESS, 9.37, 9.81, 9.65, 17.85, 25.27, 9.01, ROUND, ["9ultra", "9police"]),
        straight(".357 Remington Maximum", RIMMED, 11.2, 9.6, 9.6, 40.8, 50.5, 9.1, FLAT, ["357max"]),
        straight(".41 Action Express", RIMLESS, 10.0, 11.0, 11.0, 22.0, 30.0, 10.4, FLAT, ["41ae"]),
        straight(".45 Winchester Magnum", RIMLESS, 12.2, 12.1, 12.0, 30.4, 40.0, 11.5, ROUND, ["45winmag"]),
        straight(".45 Super", RIMLESS, 12.0, 12.0, 12.0, 22.8, 32.4, 11.5, ROUND, ["45super"]),
        straight(".460 Rowland", RIMLESS, 12.2, 12.1, 12.0, 24.3, 32.4, 11.5, ROUND, ["460rowland"]),
        straight(".475 Linebaugh", RIMLESS, 13.7, 12.8, 12.8, 36.0, 45.0, 12.1, FLAT, ["475linebaugh"]),
        c(".221 Remington Fireball", RIMLESS, 9.6, 9.6, 9.2, 6.4, 35.6, 27.2, 46.5, 5.7, SPITZER, ["221fireball"]),
        c(".25 NAA", RIMLESS, 8.6, 8.6, 8.5, 7.0, 18.9, 13.79, 24.4, 6.4, ROUND, ["25naa"]),
        c(".32 NAA", RIMLESS, 9.5, 9.5, 9.47, 8.55, 17.3, 13.69, 25.0, 7.95, ROUND, ["32naa"]),
        straight(".32 Long Colt", RIMMED, 9.5, 8.1, 8.0, 23.0, 32.0, 7.9, ROUND, ["32longcolt"]),
        # Measured specimens on municion.org (AECC drawings 06-029-CBC-010, 13-035-CGC-010).
        straight("5.75 mm Velo-Dog", RIMMED, 7.78, 6.37, 6.25, 29.41, 35.24, 5.65, ROUND, ["velodog", "5.75velodog", "5.5velodog", "5.5x30r"]),
        straight(".500 JRH", RIMLESS, 13.83, 13.38, 13.38, 35.36, 47.2, 12.72, FLAT, ["500jrh"]),
        straight(".35 S&W Auto", RIMLESS, 8.85, 8.83, 8.82, 17.21, 24.16, 7.92, ROUND, ["35s&w", "35auto"]),
        straight(".38 ACP", RIMLESS, 10.3, 9.8, 9.8, 22.9, 33.0, 9.0, ROUND, ["38acp", "38auto"]),
        straight(".41 Long Colt", RIMMED, 11.0, 10.3, 10.2, 28.6, 35.5, 9.8, ROUND, ["41longcolt", "41lc"]),
        straight(".44 Colt", RIMMED, 12.3, 11.6, 11.6, 28.0, 38.0, 11.5, FLAT, ["44colt"]),
        straight(".442 Webley", RIMMED, 12.8, 12.0, 12.0, 18.0, 28.0, 11.1, ROUND, ["442webley", "442ric"]),
        straight(".450 Adams", RIMMED, 13.0, 12.1, 12.1, 18.0, 28.0, 11.6, ROUND, ["450adams", "450revolver"]),
        straight(".476 Enfield", RIMMED, 13.5, 12.1, 12.0, 22.0, 34.0, 11.6, ROUND, ["476enfield", "476eley"]),
    ]),
    ("Langwaffe", [
        c(".204 Ruger", RIMLESS, 9.6, 9.6, 9.3, 6.0, 47.0, 39.08, 57.4, 5.2, SPITZER),
        c(".222 Remington", RIMLESS, 9.6, 9.6, 9.1, 6.4, 43.2, 32.13, 54.0, 5.7, SPITZER, ["222rem"]),
        c(".223 Remington", RIMLESS, 9.6, 9.6, 9.0, 6.4, 44.7, 35.02, 57.4, 5.7, SPITZER, ["223", "223rem"]),
        c("5.56x45 mm NATO", RIMLESS, 9.6, 9.6, 9.0, 6.4, 44.7, 35.02, 57.4, 5.7, SPITZER, ["5.56", "556", "5.56x45", "5.56nato"]),
        # Official name «5,6 mm Gewehrpatrone 90», short «5,6 mm GP 90» (Stgw 90, from 1990).
        c("5.6 mm GP 90", RIMLESS, 9.6, 9.6, 9.0, 6.4, 44.7, 35.02, 57.4, 5.7, SPITZER, ["gp90", "gp 90", "5.6", "5.6mm", "5.6gp90", "stgw90", "gewehrpatrone 90", "gwpat90"]),
        c(".22-250 Remington", RIMLESS, 12.0, 12.0, 10.5, 6.6, 48.6, 38.48, 60.3, 5.7, SPITZER, ["22-250"]),
        c(".243 Winchester", RIMLESS, 12.0, 12.0, 11.5, 7.0, 51.9, 39.62, 68.8, 6.2, SPITZER, ["243", "243win"]),
        c("6 mm BR Norma", RIMLESS, 12.0, 12.0, 11.6, 6.9, 39.6, 27.3, 58.0, 6.2, SPITZER, ["6br", "6mmbr"]),
        c("6 mm ARC", RIMLESS, 11.2, 11.2, 10.9, 6.9, 38.6, 31.54, 57.4, 6.2, SPITZER, ["6arc"]),
        # Batch 13 (2026-11): .22 Creedmoor, 7 mm Backcountry, .338 ARC (SAAMI drawing; shoulder estimated from 6 mm ARC), 6 mm PPC and 9x39; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".338 ARC", RIMLESS, 11.2, 10.97, 10.9, 9.55, 33.02, 23.83, 57.4, 8.59, SPITZER, ["338arc"]),
        c("6 mm PPC", RIMLESS, 11.3, 11.2, 10.9, 6.7, 38.5, 27.3, 53.3, 6.17, SPITZER, ["6ppc", "6mmppc"]),
        c("9x39 mm", RIMLESS, 11.35, 11.35, 10.36, 9.98, 38.77, 32.3, 56.0, 9.25, SPITZER, ["9x39", "sp-5", "sp-6"]),
        c("6.5 mm Creedmoor", RIMLESS, 12.0, 12.0, 11.7, 7.5, 48.8, 37.84, 71.8, 6.7, SPITZER, ["6.5cm", "6.5creedmoor", "65cm", "creedmoor"]),
        # Batch 14 (2026-11): .378 Weatherby, 7.5 FK and 6 mm GT (SAAMI drawing; neck estimated); dimensions from the page named in INTRODUCED, rounded.
        c("6 mm GT", RIMLESS, 11.96, 11.95, 11.66, 6.95, 43.82, 33.12, 67.06, 6.17, SPITZER, ["6gt", "6mmgt"]),
        # Batch 13 (2026-11): .22 Creedmoor, 7 mm Backcountry, .338 ARC (SAAMI drawing; shoulder estimated from 6 mm ARC), 6 mm PPC and 9x39; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".22 Creedmoor", RIMLESS, 11.99, 11.95, 11.76, 6.53, 48.77, 37.85, 68.58, 5.7, SPITZER, ["22cm", "22creedmoor"]),
        c("7 mm Backcountry", RIMLESS, 11.99, 11.93, 11.65, 8.05, 61.39, 51.35, 84.84, 7.22, SPITZER, ["7bc", "7mmbackcountry", "7backcountry"]),
        # Batch 10 (2026-11): recent American rounds; dimensions from the page named in INTRODUCED, rounded; .25 Creedmoor and 8.6 Blackout from their SAAMI drawings, 6 mm Creedmoor from the Sierra load-data drawing; other shoulder heights estimated.
        c("6 mm Creedmoor", RIMLESS, 12.01, 11.94, 11.73, 6.99, 48.8, 37.49, 71.1, 6.2, SPITZER, ["6cm", "6creedmoor", "6mmcm"]),
        c(".25 Creedmoor", RIMLESS, 12.0, 11.95, 11.76, 7.32, 48.8, 37.85, 71.8, 6.54, SPITZER, ["25cm", "25creedmoor"]),
        c("8.6 Blackout", RIMLESS, 11.99, 11.95, 11.78, 9.3, 42.8, 32.26, 71.4, 8.61, SPITZER, ["8.6blk", "86blk", "8.6blackout"]),
        c(".22 ARC", RIMLESS, 11.2, 11.2, 10.915, 6.43, 38.74, 29.235, 57.4, 5.7, SPITZER, ["22arc"]),
        c(".338 Ruger Compact Magnum", RIMLESS, 13.5, 13.5, 13.1, 9.4, 51.2, 40.34, 72.1, 8.6, SPITZER, ["338rcm"]),
        c(".408 CheyTac", RIMLESS, 16.25, 16.18, 15.24, 11.12, 77.21, 62.02, 115.5, 10.36, SPITZER, ["408cheytac", "408ct", "10.36x77"]),
        straight(".360 Buckhammer", RIMMED, 12.9, 10.66, 9.65, 46.0, 63.5, 9.1, FLAT, ["360buckhammer", "360bh"]),
        straight(".400 Legend", RIMLESS, 10.7, 11.2, 10.84, 42.0, 57.0, 10.17, ROUND, ["400legend"]),
        c("6.5x55 mm Swedish", RIMLESS, 12.2, 12.2, 11.0, 7.6, 55.0, 43.49, 80.0, 6.7, SPITZER, ["6.5x55", "6.5x55se"]),
        c("6.5x47 mm Lapua", RIMLESS, 12.0, 12.0, 11.6, 7.5, 47.0, 35.68, 72.0, 6.7, SPITZER, ["6.5x47"]),
        c("6.5 PRC", RIMLESS, 13.0, 13.0, 12.8, 7.5, 51.2, 39.75, 84.8, 6.7, SPITZER, ["6.5prc"]),
        c(".260 Remington", RIMLESS, 12.0, 12.0, 11.5, 7.5, 51.7, 39.62, 71.1, 6.7, SPITZER),
        c(".270 Winchester", RIMLESS, 12.0, 12.0, 11.2, 7.8, 64.5, 49.49, 84.8, 7.0, SPITZER, ["270", "270win"]),
        c("7 mm-08 Remington", RIMLESS, 12.0, 12.0, 11.5, 8.0, 51.7, 39.62, 71.1, 7.2, SPITZER, ["7mm-08", "7-08"]),
        c("7x57 mm Mauser", RIMLESS, 12.0, 12.0, 10.9, 8.2, 57.0, 43.84, 78.0, 7.24, SPITZER, ["7x57"]),
        c("7x64 mm", RIMLESS, 12.0, 12.0, 11.3, 8.0, 64.0, 51.5, 84.0, 7.24, SPITZER, ["7x64"]),
        c("7 mm Remington Magnum", BELTED, 13.5, 13.0, 12.4, 8.0, 63.5, 51.82, 82.6, 7.2, SPITZER, ["7mmremmag", "7rm"]),
        c("7 mm PRC", RIMLESS, 13.4, 13.4, 13.0, 8.0, 63.5, 53.67, 90.3, 7.2, SPITZER, ["7prc"]),
        c("7.5x55 mm Swiss (GP 11)", RIMLESS, 12.6, 12.6, 11.6, 8.5, 55.6, 44.58, 77.5, 7.77, SPITZER, ["gp11", "gp 11", "7.5x55", "7.5", "7.5mm", "7.5swiss", "k31"]),
        # GP 1890 ("Patrone, Modell 1890", later "Scharfe Patrone 90/23", from about 1960 "7,5 mm GP 90/23"):
        # the original Schmidt-Rubin round of the IG 89/96, KarK 93/05, KG 97 and KG 00. Its bullet is
        # unusual: a lead body wrapped in two turns of paper (the white band above the case mouth) and a
        # long, blunt round nose under a steel cap (13.7 g, 29 mm long, 7.8 mm over the paper). Shorter case
        # than GP 11. Not to be confused with the 5.6 mm GP 90 of the Stgw 90.
        c("7.5x53.5 mm Swiss (GP 1890)", RIMLESS, 12.5, 12.4, 11.5, 8.6, 53.5, 44.24, 77.0, 7.8, PATCHED,
          ["gp1890", "gp 1890", "gp1890/03", "gp90/03", "gp90/23", "7.5 mm gp 90", "patrone 1890", "patrone 90/23",
           "7.5x53.5", "7.5x53", "schmidt-rubin", "ig89"]),
        # Kadettenpatrone («7,5 mm Kadetten-Pat.», «Cart. 7,5 mm cadets/cadetti» on the box): the reduced
        # load for the single-shot Kadettengewehr 1897, "a reduced-power GP90 7.5×53.5mm cartridge"
        # (Wikipedia, Schmidt–Rubin). Measured by Raven with a caliper on one round (2026-11-08, headstamp
        # «12 D T 64»: Thun, December 1964, Dornach brass): length 77.5, case 54.8, rim 12.7, base 12.6,
        # shoulder 11.5, neck 8.6, bullet 7.8, head to shoulder 45.0, primer 5.4. The case is longer than the
        # GP 1890's (53.5), so the two are not one chamber. Jacketed round-nose bullet with a silver-coloured
        # jacket on Raven's round, drawn like any jacket. Kaliberfinder's LiDAR captures of the same round
        # (training package of 2026-11-07, filed under GP 1890 with the note "Kadettenpatrone") gave 79.0.
        c("7.5 mm Kadettenpatrone", RIMLESS, 12.7, 12.6, 11.5, 8.6, 54.8, 45.0, 77.5, 7.8, ROUND,
          ["kadettenpatrone", "kadetten-pat", "kadettenpat", "7.5 mm kadettenpatrone", "7.5 mm kadetten-pat",
           "cadets", "cadetti", "kg97", "kadettengewehr"]),
        c("7.5x54 mm French", RIMLESS, 12.25, 12.25, 11.2, 8.6, 54.0, 42.79, 76.0, 7.8, SPITZER, ["7.5x54"]),
        c("7.62x39 mm", RIMLESS, 11.35, 11.35, 10.07, 8.6, 38.7, 30.5, 56.0, 7.9, SPITZER, ["7.62x39", "762x39"]),
        c(".300 AAC Blackout", RIMLESS, 9.6, 9.6, 9.1, 8.4, 34.7, 27.2, 57.0, 7.8, SPITZER, ["300blk", "300blackout", "300aac"]),
        # SAAMI drawing (Wilson Combat copy, rev. 2022-04-11); case length after the SAAMI datasheet.
        c(".300 HAM'R", RIMLESS, 9.6, 9.55, 9.3, 8.43, 41.02, 34.27, 57.4, 7.82, SPITZER, ["300hamr", "hamr"]),
        c("7.62x51 mm NATO", RIMLESS, 11.9, 11.9, 11.5, 8.7, 51.2, 39.62, 71.1, 7.82, SPITZER, ["7.62x51", "7.62nato", "762"]),
        c(".308 Winchester", RIMLESS, 11.9, 11.9, 11.5, 8.7, 51.2, 39.62, 71.1, 7.82, SPITZER, ["308", "308win"]),
        c(".30-06 Springfield", RIMLESS, 12.0, 12.0, 11.2, 8.6, 63.3, 49.49, 84.8, 7.82, SPITZER, ["30-06", "3006"]),
        c(".30-30 Winchester", RIMMED, 12.8, 10.7, 10.2, 8.5, 51.8, 36.6, 64.8, 7.82, FLAT, ["30-30", "3030"]),
        c(".300 Winchester Magnum", BELTED, 13.0, 13.0, 12.4, 8.6, 66.7, 55.78, 84.8, 7.82, SPITZER, ["300winmag", "300wm"]),
        c(".300 PRC", RIMLESS, 13.4, 13.4, 13.0, 8.6, 65.5, 54.6, 94.5, 7.82, SPITZER, ["300prc"]),
        c(".300 Norma Magnum", RIMLESS, 14.9, 14.9, 14.4, 8.6, 63.3, 48.06, 91.4, 7.82, SPITZER, ["300norma", "300nm"]),
        # Batch 12 (2026-11): British Nitro and Rigby rounds, .310 Cadet, Portuguese 6.5x58, .30 R Blaser, .22 Rem Auto; dimensions from the page named in INTRODUCED (.475 No. 2 from its Wikipedia page), rounded; shoulder heights estimated.
        c("6.5x58 mm Vergueiro", RIMLESS, 11.78, 11.88, 10.94, 7.56, 57.85, 41.0, 81.5, 6.65, SPITZER, ["6.5x58", "6.5vergueiro", "6.5portuguese"]),
        c(".30 R Blaser", RIMMED, 13.5, 12.2, 11.2, 8.73, 68.0, 57.77, 95.0, 7.82, SPITZER, ["30rblaser", "30r"]),
        # Batch 11 (2026-11): old rimfire, black-powder and British rounds plus 9x25 Dillon and .300 Lapua; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".300 Lapua Magnum", RIMLESS, 14.93, 14.91, 13.82, 8.73, 69.73, 54.9, 94.5, 7.82, SPITZER, ["300lapua", "300lm"]),
        c(".35 Winchester", RIMMED, 13.7, 11.6, 10.5, 9.6, 61.0, 51.4, 80.0, 9.1, ROUND, ["35win"]),
        straight(".50-110 Winchester", RIMMED, 15.4, 14.0, 13.6, 61.0, 70.0, 13.0, FLAT, ["50-110"]),
        c(".303 British", RIMMED, 13.5, 11.7, 10.2, 8.6, 56.4, 45.47, 78.1, 7.92, SPITZER, ["303", "303brit"]),
        c("7.62x54 mm R", RIMMED, 14.5, 12.4, 11.6, 8.5, 53.6, 39.7, 77.2, 7.92, SPITZER, ["7.62x54r", "762x54r"]),
        c("8x57 mm IS", RIMLESS, 11.95, 11.95, 11.0, 9.1, 57.0, 46.2, 82.0, 8.2, SPITZER, ["8x57", "8x57is", "8mmmauser"]),
        c("8x68 mm S", RIMLESS, 13.3, 13.3, 12.4, 9.2, 67.5, 53.2, 87.5, 8.2, SPITZER, ["8x68"]),
        c("9.3x62 mm", RIMLESS, 12.0, 12.0, 11.5, 10.0, 62.0, 51.79, 83.6, 9.3, ROUND, ["9.3x62"]),
        c("9.3x74 mm R", RIMMED, 13.0, 11.9, 10.8, 10.0, 74.0, 59, 94.5, 9.3, ROUND, ["9.3x74r"]),
        c(".338 Lapua Magnum", RIMLESS, 14.9, 14.9, 13.82, 9.3, 69.2, 54.9, 93.5, 8.6, SPITZER, ["338lm", "338lapua", "338"]),
        c(".375 H&H Magnum", BELTED, 13.0, 13.0, 11.6, 10.3, 72.4, 61.27, 91.4, 9.5, ROUND, ["375h&h", "375hh"]),
        # Batch 14 (2026-11): .378 Weatherby, 7.5 FK and 6 mm GT (SAAMI drawing; neck estimated); dimensions from the page named in INTRODUCED, rounded.
        c(".378 Weatherby Magnum", BELTED, 14.7, 14.8, 14.2, 10.1, 74.0, 60.9, 93.0, 9.5, ROUND, ["378wby"]),
        # Batch 12 (2026-11): British Nitro and Rigby rounds, .310 Cadet, Portuguese 6.5x58, .30 R Blaser, .22 Rem Auto; dimensions from the page named in INTRODUCED (.475 No. 2 from its Wikipedia page), rounded; shoulder heights estimated.
        c(".465 H&H Magnum", BELTED, 14.7, 14.8, 13.5, 12.5, 73.5, 53.5, 90.2, 11.9, ROUND, ["465hh", "465h&h"]),
        c(".475 No. 2 Nitro Express", RIMMED, 16.9, 14.6, 13.9, 13.0, 89.0, 69.21, 108.0, 12.3, ROUND, ["475no2", "475ne"]),
        c(".400/350 Nitro Express", RIMMED, 13.2, 11.9, 10.5, 9.7, 70.0, 53.34, 93.6, 9.1, ROUND, ["400/350", "350rigbyflanged"]),
        c(".350 Rigby Magnum", RIMLESS, 13.1, 13.1, 11.6, 9.7, 69.6, 57.15, 87.0, 9.1, ROUND, ["350rigby"]),
        straight(".310 Cadet", RIMMED, 10.4, 9.0, 8.3, 28.0, 41.0, 8.2, ROUND, ["310cadet", "310greener"]),
        # Batch 11 (2026-11): old rimfire, black-powder and British rounds plus 9x25 Dillon and .300 Lapua; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".400 H&H Magnum", BELTED, 13.5, 13.0, 12.5, 11.2, 72.3, 50.4, 90.2, 10.4, ROUND, ["400hh", "400h&h"]),
        c(".244 H&H Magnum", BELTED, 13.5, 12.9, 11.3, 6.7, 71.0, 59.18, 91.0, 6.2, SPITZER, ["244hh", "244h&h"]),
        c(".416 Rigby", RIMLESS, 14.9, 14.9, 13.6, 11.6, 73.7, 59.77, 95.3, 10.6, ROUND, ["416rigby"]),
        # Sourced 2026-11-04 from the C.I.P. TDCC sheet (maximum cartridge), rounded to 0.01 mm:
        # sh_at = L1, shoulder = P2, neck = H2, oal = L6. Wikipedia's .450 Rigby infobox gives
        # H1 as the shoulder (12.5 mm), which is why it was left out before.
        c(".450 Rigby", RIMLESS, 14.99, 14.96, 14.5, 12.38, 73.5, 59.5, 95.25, 11.66, ROUND, ["450rigby"]),
        c(".375 CheyTac", RIMLESS, 16.25, 16.18, 15.22, 10.31, 76.91, 62.28, 113.4, 9.52, SPITZER, ["375cheytac", "375ct"]),
        straight(".45-70 Government", RIMMED, 15.2, 12.7, 12.2, 53.5, 64.8, 11.6, FLAT, ["45-70", "4570"]),
        c(".50 BMG", RIMLESS, 20.4, 20.4, 18.3, 14.0, 99.0, 76.34, 138.0, 12.98, SPITZER, ["50bmg", "12.7x99"]),
        # Added 2026-11, rifle batch 1: dimensions from the page named in INTRODUCED, rounded;
        # shoulder heights estimated for drawing.
        c("6.5x52 mm Carcano", RIMLESS, 11.45, 11.41, 10.94, 7.55, 52.5, 41.2, 76.5, 6.8, ROUND, ["6.5carcano", "6.5x52"]),
        c("6.5x50 mm SR Arisaka", RIMLESS, 12.08, 11.45, 10.4, 7.37, 51.0, 38.92, 76.0, 6.63, SPITZER, ["6.5arisaka", "6.5x50"]),
        c("7.7x58 mm Arisaka", RIMLESS, 12.07, 12.02, 11.0, 8.58, 57.8, 47.34, 79.6, 7.92, SPITZER, ["7.7arisaka", "7.7x58"]),
        c("8x50 mm R Lebel", RIMMED, 16.0, 13.77, 11.42, 8.85, 50.5, 37.22, 75.0, 8.3, SPITZER, ["8lebel", "8x50rlebel"]),
        c("8x56 mm R Mannlicher", RIMMED, 14.05, 12.47, 12.0, 9.2, 55.63, 37.03, 75.91, 8.35, SPITZER, ["8x56r"]),
        c("8x50 mm R Mannlicher", RIMMED, 14.11, 12.48, 12.01, 9.03, 50.38, 38.29, 76.21, 8.22, ROUND, ["8x50rmannlicher", "8x50r"]),
        c("7.35x51 mm Carcano", RIMLESS, 11.4, 11.4, 10.85, 8.32, 51.5, 41.73, 73.5, 7.57, SPITZER, ["7.35carcano", "7.35x51"]),
        c("6.5x54 mm Mannlicher-Schönauer", RIMLESS, 11.52, 11.47, 10.87, 7.56, 53.6, 41.82, 77.8, 6.7, ROUND, ["6.5x54ms", "6.5x54"]),
        c(".30-40 Krag", RIMMED, 13.8, 11.6, 10.7, 8.6, 58.8, 43.82, 78.5, 7.8, ROUND, ["30-40", "30-40krag", "30army"]),
        c("7.92x33 mm Kurz", RIMLESS, 11.95, 11.94, 11.4, 9.1, 33.0, 24.38, 48.0, 8.22, SPITZER, ["7.92kurz", "8mmkurz", "7.92x33"]),
        c("5.45x39 mm", RIMLESS, 10.0, 10.0, 9.25, 6.29, 39.82, 30, 57.0, 5.6, SPITZER, ["5.45x39", "545x39"]),
        # Sourced 2026-11-04 from the Wikipedia infoboxes (.277 SIG Fury after the 2020 SAAMI drawing);
        # shoulder heights estimated (.277 Fury like the .308 parent).
        c(".277 SIG Fury", RIMLESS, 11.99, 11.95, 11.71, 7.87, 51.18, 41.43, 71.76, 7.06, SPITZER, ["277fury", "277sigfury", "6.8x51"]),
        c("5.8x42 mm", RIMLESS, 10.42, 10.4, 9.35, 6.65, 42.2, 34.0, 58.0, 6.0, SPITZER, ["5.8x42", "dbp87", "dbp10"]),
        c(".22 Hornet", RIMMED, 8.89, 7.57, 7.01, 6.17, 35.64, 21.64, 43.76, 5.69, SPITZER, ["22hornet", "5.6x35r"]),
        c(".25-06 Remington", RIMLESS, 12.0, 11.9, 11.2, 7.4, 63.3, 49.48, 82.6, 6.5, SPITZER, ["25-06"]),
        c(".257 Roberts", RIMLESS, 12.0, 12.0, 10.9, 7.4, 56.7, 43.88, 70.5, 6.5, SPITZER, ["257roberts"]),
        c(".280 Remington", RIMLESS, 12.0, 11.9, 11.2, 8.0, 64.5, 50.78, 84.6, 7.2, SPITZER, ["280rem"]),
        c(".35 Whelen", RIMLESS, 12.0, 12.0, 11.2, 9.8, 63.3, 49.48, 84.8, 9.1, ROUND, ["35whelen"]),
        c(".300 H&H Magnum", BELTED, 13.5, 13.0, 11.4, 8.6, 72.4, 53.46, 91.4, 7.8, SPITZER, ["300h&h", "300hh"]),
        c(".338 Winchester Magnum", BELTED, 13.5, 13.0, 12.5, 9.4, 63.5, 51.82, 84.8, 8.6, SPITZER, ["338winmag", "338wm"]),
        straight(".444 Marlin", RIMMED, 13.1, 11.95, 11.5, 56.5, 65.0, 10.9, FLAT, ["444marlin"]),
        straight(".458 Winchester Magnum", BELTED, 13.5, 13.0, 12.2, 63.5, 84.8, 11.63, ROUND, ["458winmag", "458wm"]),
        straight(".350 Legend", RIMLESS, 9.6, 9.9, 9.6, 43.0, 57.0, 9.07, SPITZER, ["350legend"]),
        # Rifle batch 2 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c("5.6x50 mm Magnum", RIMLESS, 9.6, 9.56, 9.0, 6.48, 50.0, 40.26, 61.3, 5.7, SPITZER, ["5.6x50", "5.6x50mag"]),
        c("6.5x57 mm Mauser", RIMLESS, 11.95, 11.9, 10.94, 7.65, 56.7, 44.5, 82.0, 6.7, SPITZER, ["6.5x57"]),
        c("6.5x68 mm", RIMLESS, 13.0, 13.3, 12.18, 7.6, 67.5, 51.75, 86.5, 6.7, SPITZER, ["6.5x68"]),
        c("8x64 mm S", RIMLESS, 12.0, 11.95, 10.85, 8.96, 64.0, 51.8, 87.5, 8.22, SPITZER, ["8x64s", "8x64"]),
        c("8x60 mm S", RIMLESS, 11.95, 11.98, 10.95, 9.08, 60.0, 48.2, 83.6, 8.22, SPITZER, ["8x60s", "8x60"]),
        c("9.5x57 mm Mannlicher-Schönauer", RIMLESS, 11.89, 11.89, 11.55, 10.16, 57.15, 46.5, 74.9, 9.55, ROUND, ["9.5x57", "375rimless"]),
        c(".375 Ruger", RIMLESS, 13.5, 13.5, 13.1, 10.3, 65.5, 55.36, 84.8, 9.5, ROUND, ["375ruger"]),
        straight(".450 Bushmaster", RIMLESS, 12.01, 12.7, 12.19, 43.2, 57.4, 11.48, SPITZER, ["450bm", "450bushmaster"]),
        c("6.8 mm Remington SPC", RIMLESS, 10.7, 10.7, 10.2, 7.8, 42.8, 33.05, 57.4, 7.0, SPITZER, ["6.8spc", "68spc"]),
        c(".300 Winchester Short Magnum", RIMLESS, 13.6, 14.1, 13.7, 8.7, 53.3, 42.25, 72.6, 7.8, SPITZER, ["300wsm"]),
        c(".17 Remington", RIMLESS, 9.6, 9.6, 9.0, 5.1, 45.6, 34.31, 54.6, 4.4, SPITZER, ["17rem"]),
        c(".218 Bee", RIMMED, 10.4, 8.9, 8.4, 6.1, 34.2, 23.45, 42.7, 5.7, FLAT, ["218bee"]),
        c(".25-35 Winchester", RIMMED, 12.9, 10.7, 9.3, 7.2, 51.9, 34.1, 65.0, 6.6, FLAT, ["25-35", "25-35wcf"]),
        c(".32 Winchester Special", RIMMED, 12.9, 10.7, 10.2, 8.7, 51.8, 36.72, 65.2, 8.2, FLAT, ["32winspecial", "32ws"]),
        c(".35 Remington", RIMLESS, 11.7, 11.6, 10.3, 9.8, 48.8, 39.1, 64.1, 9.1, ROUND, ["35rem"]),
        straight(".38-55 Winchester", RIMMED, 12.9, 10.7, 10.0, 53.0, 64.8, 9.6, FLAT, ["38-55"]),
        c(".348 Winchester", RIMMED, 15.5, 14.0, 12.3, 9.61, 57.3, 41.91, 71.0, 8.8, FLAT, ["348win"]),
        c(".358 Winchester", RIMLESS, 12.0, 11.9, 11.5, 9.9, 51.2, 39.62, 70.6, 9.1, ROUND, ["358win"]),
        c(".264 Winchester Magnum", BELTED, 13.5, 13.1, 12.5, 7.6, 64.0, 51.82, 85.0, 6.7, SPITZER, ["264winmag"]),
        c(".300 Weatherby Magnum", BELTED, 13.5, 13.0, 12.5, 8.5, 71.8, 59.62, 90.5, 7.8, SPITZER, ["300wby", "300weatherby"]),
        c(".416 Remington Magnum", BELTED, 13.5, 13.0, 12.4, 11.4, 72.4, 60.69, 91.4, 10.6, ROUND, ["416rem"]),
        c(".470 Nitro Express", RIMMED, 16.6, 14.6, 13.5, 12.8, 83.0, 60.96, 101.0, 12.0, ROUND, ["470ne"]),
        # Sourced 2026-11-04 (batch 12 leftovers): C.I.P. TDCC maximum cartridge (shoulder = P2,
        # neck = H2, sh_at = L1, oal = L6); .360 No. 5 Rook from the Wikipedia infobox (Barnes).
        c(".450 No. 2 Nitro Express", RIMMED, 16.76, 14.35, 13.97, 12.24, 88.9, 72.39, 109.98, 11.63, ROUND, ["450no2"]),
        c(".500/416 Nitro Express", RIMMED, 16.64, 14.55, 13.49, 11.33, 82.55, 60.96, 101.09, 10.57, ROUND, ["500/416"]),
        c(".375 Flanged Magnum Nitro Express", RIMMED, 14.35, 13.13, 11.43, 10.29, 74.68, 60.96, 96.52, 9.52, ROUND, ["375flmag"]),
        # .375 Flanged NE (1899, 2.5 in, straight taper) and .55 Boys: measured specimens on municion.org
        # (AECC 10-063-TBC-020, 14-099-BFC-020; Boys belt 21.59 matches antitank.co.uk's 0.850 in).
        # .45-90 WCF: C.I.P. Tab. II "45-90 WM" maximum cartridge, checked against AECC 11-061-BBC-020.
        straight(".375 Flanged Nitro Express", RIMMED, 13.31, 11.52, 10.08, 63.13, 77.58, 9.48, ROUND, ["375flne", "370flanged"]),
        c(".55 Boys", BELTED, 20.3, 20.14, 18.03, 15.51, 99.11, 75.0, 133.64, 14.36, SPITZER, ["55boys", "13.9x99b", "boys"]),
        straight(".45-90 WCF", RIMMED, 15.44, 12.82, 12.22, 60.96, 82.0, 11.63, FLAT, ["45-90", "4590", "45-90wcf"]),
        c("9.3x53 mm R Finnish", RIMMED, 14.4, 12.42, 11.61, 9.9, 53.3, 39.61, 76.0, 9.3, ROUND, ["9.3x53r"]),
        c("10.3x60 mm R", RIMMED, 15.7, 13.85, 12.5, 11.26, 60.8, 40.8, 78.9, 10.54, ROUND, ["10.3x60r"]),
        c("7x61 mm Sharpe & Hart", BELTED, 13.5, 13.05, 11.91, 8.06, 61.0, 50.8, 83.0, 7.2, SPITZER, ["7x61", "7x61sh", "7x61super"]),
        straight(".360 No. 5 Rook", RIMMED, 10.97, 9.65, 9.53, 26.67, 36.83, 9.19, ROUND, ["360rook"]),
        # Batch 9 (2026-11): Nitro Express and small Weatherby rounds; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        straight(".450 Nitro Express", RIMMED, 15.8, 13.8, 12.2, 83.0, 100.0, 11.6, ROUND, ["450ne"]),
        straight(".500 Nitro Express", RIMMED, 16.6, 14.6, 13.5, 76.0, 95.0, 13.0, ROUND, ["500ne"]),
        straight(".577 Nitro Express", RIMMED, 19.0, 16.8, 15.5, 76.0, 94.0, 14.9, ROUND, ["577ne"]),
        straight(".600 Nitro Express", RIMMED, 20.6, 17.8, 16.5, 76.0, 94.0, 15.7, ROUND, ["600ne"]),
        straight(".700 Nitro Express", RIMMED, 22.6, 19.8, 18.5, 89.0, 107.0, 17.8, ROUND, ["700ne"]),
        c(".500/465 Nitro Express", RIMMED, 16.4, 14.5, 13.4, 12.4, 83.0, 55.88, 99.0, 11.9, ROUND, ["500/465", "465ne"]),
        c(".318 Westley Richards", RIMLESS, 11.8, 11.8, 11.1, 9.1, 60.1, 49.63, 85.1, 8.4, ROUND, ["318wr", "318rne"]),
        c(".240 Weatherby Magnum", BELTED, 12.0, 11.5, 10.9, 6.9, 63.4, 51.91, 78.7, 6.2, SPITZER, ["240wby"]),
        c(".224 Weatherby Magnum", BELTED, 10.9, 10.5, 10.0, 6.4, 48.8, 39.01, 59.2, 5.7, SPITZER, ["224wby"]),
        c("6.5 mm Remington Magnum", BELTED, 13.5, 13.51, 12.6, 7.6, 55.1, 43.18, 71.1, 6.7, SPITZER, ["6.5remmag"]),
        # Rifle batch 3 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".220 Swift", RIMLESS, 12.0, 11.3, 10.2, 6.6, 56.0, 43.76, 68.1, 5.7, SPITZER, ["220swift"]),
        c(".25-20 Winchester", RIMMED, 10.4, 8.9, 8.5, 7.0, 33.8, 21.77, 40.4, 6.6, FLAT, ["25-20", "25wcf"]),
        c(".250 Savage", RIMLESS, 12.01, 11.86, 10.25, 7.25, 48.56, 38.4, 63.88, 6.55, SPITZER, ["250savage", "250-3000"]),
        c(".257 Weatherby Magnum", BELTED, 13.5, 13.0, 12.5, 7.2, 64.6, 52.68, 81.5, 6.5, SPITZER, ["257wby"]),
        c(".270 Weatherby Magnum", BELTED, 13.5, 13.0, 12.5, 7.7, 65.0, 52.57, 83.0, 7.0, SPITZER, ["270wby"]),
        c("7 mm Weatherby Magnum", BELTED, 13.5, 13.0, 12.4, 7.9, 64.7, 52.55, 83.8, 7.2, SPITZER, ["7mmwby"]),
        c(".340 Weatherby Magnum", BELTED, 13.5, 13.0, 12.6, 9.3, 72.0, 59.49, 91.0, 8.6, SPITZER, ["340wby"]),
        c(".284 Winchester", RIMLESS, 12.01, 12.72, 12.06, 8.13, 55.12, 45.08, 71.12, 7.21, SPITZER, ["284win"]),
        c(".300 Savage", RIMLESS, 12.0, 12.0, 11.3, 8.6, 47.5, 39.59, 66.0, 7.8, SPITZER, ["300savage"]),
        # Batch 8 (2026-11): old American sporting rounds; dimensions from the page named in INTRODUCED, rounded (.32 Remington from the .25 Remington family); shoulder heights estimated.
        c(".33 Winchester", RIMMED, 15.5, 12.9, 11.3, 9.3, 54.0, 40.96, 71.0, 8.6, FLAT, ["33win", "33wcf"]),
        c(".25 Remington", RIMLESS, 10.6, 10.6, 10.1, 7.3, 52.0, 38.05, 64.0, 6.54, ROUND, ["25rem"]),
        c(".32 Remington", RIMLESS, 10.7, 10.7, 10.06, 8.74, 52.1, 38.05, 64.1, 8.13, ROUND, ["32rem"]),
        straight(".35 Winchester Self-Loading", RIMLESS, 10.3, 9.7, 9.6, 29.3, 42.0, 8.9, ROUND, ["35wsl"]),
        straight(".351 Winchester Self-Loading", RIMLESS, 10.4, 9.7, 9.5, 35.1, 48.4, 8.9, ROUND, ["351wsl"]),
        straight(".401 Winchester Self-Loading", RIMLESS, 11.6, 10.9, 10.9, 38.0, 50.9, 10.33, ROUND, ["401wsl"]),
        straight(".40-65 Winchester", RIMMED, 15.3, 12.8, 10.7, 53.0, 63.0, 10.3, FLAT, ["40-65"]),
        # Sourced 2026-11-04: C.I.P. TDCC maximum cartridge (shoulder = P2, neck = H2, sh_at = L1,
        # oal = L6), except .22 Nosler (Sierra load-data drawing), 6.5-300 Wby (SAAMI drawing; base
        # from Wikipedia) and .38-56 WCF (Wikipedia inch values, its mm column is off by 1000;
        # shoulder start estimated). 9.3x72 R has no shoulder on its C.I.P. sheet.
        straight("9.3x72 mm R", RIMMED, 12.35, 10.91, 9.82, 72.0, 86.0, 9.57, ROUND, ["9.3x72r"]),
        c("8x75 mm RS", RIMMED, 13.35, 11.9, 10.4, 9.08, 74.6, 66.2, 96.0, 8.22, SPITZER, ["8x75rs"]),
        c("6.5x65 mm RWS", RIMLESS, 11.95, 12.04, 10.97, 7.57, 65.0, 53.85, 85.0, 6.7, SPITZER, ["6.5x65", "6.5x65rws"]),
        c("9.3x66 mm Sako (.370 Sako Magnum)", RIMLESS, 11.95, 12.13, 11.43, 9.92, 66.0, 55.8, 85.0, 9.3, ROUND, ["9.3x66", "370sako"]),
        c(".300 Blaser Magnum", RIMLESS, 13.59, 13.84, 13.0, 8.61, 64.2, 52.12, 84.84, 7.83, SPITZER, ["300blaser"]),
        c(".375 Blaser Magnum", RIMLESS, 13.59, 13.84, 12.9, 10.31, 71.7, 59.13, 92.0, 9.53, ROUND, ["375blaser"]),
        # C.I.P. TDCC maximum cartridge (8.5x55 from the 2021 C.I.P. bulletin, sheet 2019-05-22).
        c("7 mm Blaser Magnum", RIMLESS, 13.59, 13.84, 13.09, 8.0, 59.7, 47.24, 80.0, 7.22, SPITZER, ["7mmblaser", "7blaser"]),
        c(".338 Blaser Magnum", RIMLESS, 13.59, 13.84, 13.02, 9.36, 63.7, 51.51, 84.84, 8.59, SPITZER, ["338blaser"]),
        c("8.5x55 mm Blaser", RIMLESS, 13.59, 13.84, 13.17, 9.36, 54.7, 42.38, 75.84, 8.59, SPITZER, ["8.5x55", "8.5x55blaser", "85x55"]),
        c(".450/400 Nitro Express 3 inch", RIMMED, 15.87, 13.92, 13.21, 11.18, 76.2, 55.26, 95.25, 10.41, ROUND, ["450/400", "450/400ne"]),
        c(".40-82 WCF", RIMMED, 15.49, 12.92, 11.54, 10.85, 60.71, 44.91, 70.23, 10.35, FLAT, ["40-82"]),
        c(".50-95 WCF", RIMMED, 15.93, 14.27, 14.05, 13.62, 49.28, 36.63, 57.4, 13.03, FLAT, ["50-95"]),
        c(".38-56 WCF", RIMMED, 15.37, 12.83, 11.3, 10.16, 53.34, 30.64, 63.5, 9.59, FLAT, ["38-56"]),
        c(".30 Remington", RIMLESS, 10.72, 10.71, 10.19, 8.43, 52.07, 38.05, 64.14, 7.8, FLAT, ["30rem"]),
        c(".17 Remington Fireball", RIMLESS, 9.6, 9.57, 9.28, 5.18, 35.81, 27.05, 46.48, 4.38, SPITZER, ["17fireball"]),
        c(".338 Marlin Express", RIMMED, 14.05, 12.89, 12.52, 9.35, 48.01, 37.03, 62.23, 8.6, FLAT, ["338me"]),
        c(".22 Nosler", RIMLESS, 9.6, 10.67, 10.16, 6.48, 44.7, 35.28, 57.4, 5.69, SPITZER, ["22nosler"]),
        c("6.5-300 Weatherby Magnum", BELTED, 13.5, 13.0, 12.57, 7.49, 71.76, 58.35, 91.44, 6.72, SPITZER, ["6.5-300", "6.5-300wby"]),
        c(".303 Savage", RIMMED, 12.8, 11.2, 10.5, 8.5, 51.2, 34.33, 64.0, 7.8, ROUND, ["303savage"]),
        c(".219 Zipper", RIMMED, 12.9, 10.7, 9.3, 6.4, 49.2, 34.55, 57.4, 5.7, FLAT, ["219zipper"]),
        c(".300 Remington Ultra Magnum", RIMLESS, 13.6, 14.0, 13.3, 8.7, 72.4, 60.64, 91.4, 7.8, SPITZER, ["300rum"]),
        c(".270 Winchester Short Magnum", RIMLESS, 13.6, 14.1, 13.67, 7.98, 53.3, 42.25, 72.6, 7.0, SPITZER, ["270wsm"]),
        c("7 mm Winchester Short Magnum", RIMLESS, 13.6, 14.1, 13.7, 8.2, 53.3, 43.23, 72.6, 7.2, SPITZER, ["7mmwsm", "7wsm"]),
        c(".338 Federal", RIMLESS, 12.0, 11.9, 11.5, 9.4, 51.0, 39.62, 70.0, 8.6, SPITZER, ["338fed"]),
        c("8 mm Remington Magnum", BELTED, 13.5, 13.0, 12.4, 9.0, 72.4, 60.69, 91.4, 8.2, SPITZER, ["8mmremmag"]),
        c(".376 Steyr", RIMLESS, 12.55, 12.73, 12.02, 10.11, 59.69, 48.09, 79.0, 9.5, ROUND, ["376steyr"]),
        c("6.5 mm Grendel", RIMLESS, 11.2, 11.15, 10.87, 7.44, 38.7, 29.07, 57.5, 6.71, SPITZER, ["6.5grendel", "grendel"]),
        c("6 mm Remington", RIMLESS, 12.0, 12.0, 10.9, 7.0, 56.7, 43.81, 71.8, 6.18, SPITZER, ["6mmrem", "244rem"]),
        c("7-30 Waters", RIMMED, 12.9, 10.7, 10.2, 7.8, 52.0, 40.29, 64.0, 7.2, FLAT, ["7-30waters"]),
        c(".17 Hornet", RIMMED, 8.9, 7.6, 7.3, 4.9, 34.3, 26.83, 43.8, 4.4, SPITZER, ["17hornet"]),
        straight(".375 Winchester", RIMMED, 12.9, 10.7, 10.2, 51.3, 65.0, 9.5, FLAT, ["375win"]),
        straight(".405 Winchester", RIMMED, 13.8, 11.7, 11.1, 65.6, 80.6, 10.45, FLAT, ["405win"]),
        straight(".450 Marlin", BELTED, 13.4, 13.01, 12.2, 53.0, 65.0, 11.6, FLAT, ["450marlin"]),
        straight(".458 Lott", BELTED, 13.5, 13.0, 12.2, 71.1, 91.4, 11.6, ROUND, ["458lott"]),
        # Mixed batch 4 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated; 7x65 R and 8x57 IRS rims estimated like 9.3x74 R.
        straight(".30 Carbine", RIMLESS, 9.1, 9.2, 8.4, 32.8, 42.0, 7.82, ROUND, ["30carbine", "7.62x33"]),
        c("7x65 mm R", RIMMED, 13.0, 11.89, 10.8, 7.95, 65.0, 51.5, 84.0, 7.25, SPITZER, ["7x65r"]),
        c(".22 Savage Hi-Power", RIMMED, 12.85, 10.7, 9.2, 6.4, 52.0, 35.52, 63.5, 5.79, ROUND, ["22savage", "5.6x52r", "22hp"]),
        c("8x57 mm IRS", RIMMED, 13.0, 11.95, 11.0, 9.1, 57.0, 46, 80.0, 8.2, ROUND, ["8x57irs", "8x57jrs"]),
        c(".280 Ackley Improved", RIMLESS, 12.0, 12.0, 11.7, 8.0, 64.1, 54.96, 84.6, 7.2, SPITZER, ["280ai"]),
        c(".356 Winchester", RIMLESS, 12.9, 11.95, 11.5, 9.9, 51.2, 39.62, 65.0, 9.1, FLAT, ["356win"]),
        c(".307 Winchester", RIMLESS, 12.9, 12.0, 11.5, 8.7, 51.2, 39.62, 65.0, 7.8, FLAT, ["307win"]),
        c(".416 Ruger", RIMLESS, 13.5, 13.5, 13.0, 11.3, 65.3, 55.37, 84.8, 10.6, ROUND, ["416ruger"]),
        c(".416 Weatherby Magnum", BELTED, 13.5, 14.8, 14.2, 11.3, 74.0, 60.66, 95.3, 10.6, ROUND, ["416wby"]),
        c(".375 Remington Ultra Magnum", RIMLESS, 13.6, 13.97, 13.34, 10.29, 72.4, 60.64, 91.4, 9.5, SPITZER, ["375rum"]),
        c("7 mm STW", BELTED, 13.0, 13.0, 12.4, 8.0, 72.4, 60.69, 91.4, 7.2, SPITZER, ["7stw"]),
        c(".225 Winchester", RIMMED, 12.0, 10.7, 10.3, 6.6, 49.0, 38.86, 64.0, 5.7, SPITZER, ["225win"]),
        c(".223 WSSM", RIMLESS, 13.6, 14.1, 13.8, 6.9, 42.4, 29.2, 60.0, 5.7, SPITZER, ["223wssm"]),
        c(".243 WSSM", RIMLESS, 13.6, 14.1, 13.8, 7.4, 42.4, 29.21, 60.0, 6.2, SPITZER, ["243wssm"]),
        c(".25 WSSM", RIMLESS, 13.6, 14.1, 13.8, 7.2, 42.4, 29.4, 60.0, 6.53, SPITZER, ["25wssm"]),
        c(".350 Remington Magnum", BELTED, 13.5, 13.51, 12.6, 9.9, 55.1, 43.18, 71.1, 9.1, ROUND, ["350remmag"]),
        # Batch 6 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".338-378 Weatherby Magnum", BELTED, 14.7, 14.8, 14.2, 9.2, 73.8, 61.05, 93.0, 8.6, SPITZER, ["338-378"]),
        c("6.8 Western", RIMLESS, 13.6, 14.1, 13.7, 8.0, 51.3, 40.21, 75.1, 7.04, SPITZER, ["6.8western", "68western"]),
        c("7 mm Remington SAUM", RIMLESS, 13.6, 13.61, 13.58, 8.1, 51.7, 39.07, 71.8, 7.2, SPITZER, ["7saum"]),
        # Rifle batch 5 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated; the Nosler line shares the .28 Nosler case outside.
        c(".26 Nosler", RIMLESS, 13.6, 14.0, 13.6, 7.6, 65.8, 55.58, 84.8, 6.7, SPITZER, ["26nosler"]),
        c(".27 Nosler", RIMLESS, 13.6, 14.0, 13.6, 7.8, 65.8, 53.57, 84.8, 7.04, SPITZER, ["27nosler"]),
        c(".28 Nosler", RIMLESS, 13.6, 14.0, 13.6, 8.0, 65.8, 56.38, 84.8, 7.2, SPITZER, ["28nosler"]),
        c(".30 Nosler", RIMLESS, 13.56, 13.97, 13.41, 8.74, 64.92, 53.72, 84.84, 7.82, SPITZER, ["30nosler"]),
        c(".33 Nosler", RIMLESS, 13.6, 14.0, 13.6, 9.4, 65.8, 54.32, 84.8, 8.6, SPITZER, ["33nosler"]),
        c(".300 Ruger Compact Magnum", RIMLESS, 13.5, 13.5, 13.1, 8.6, 53.0, 42.44, 71.8, 7.82, SPITZER, ["300rcm"]),
        c(".30 Thompson/Center", RIMLESS, 12.01, 11.95, 11.78, 8.56, 48.77, 38.4, 67.56, 7.82, SPITZER, ["30tc"]),
        c(".30 Remington AR", RIMLESS, 12.5, 12.7, 12.4, 8.6, 39.0, 27.37, 57.0, 7.82, SPITZER, ["30remar"]),
        c(".308 Marlin Express", RIMLESS, 12.9, 11.9, 11.5, 8.7, 48.5, 37.08, 66.0, 7.82, SPITZER, ["308me"]),
        c(".300 Remington SAUM", RIMLESS, 13.6, 14.0, 13.6, 8.7, 51.2, 39.07, 71.8, 7.82, SPITZER, ["300saum"]),
        c(".224 Valkyrie", RIMLESS, 10.7, 10.69, 10.24, 6.5, 41.0, 31.5, 57.4, 5.7, SPITZER, ["224valk"]),
        c(".458 SOCOM", RIMLESS, 12.01, 13.74, 13.49, 12.32, 40.0, 30.0, 57.4, 11.63, ROUND, ["458socom"]),
        straight(".50 Beowulf", RIMLESS, 11.3, 13.6, 13.3, 42.0, 54.0, 12.7, FLAT, ["50beowulf"]),
        c(".222 Remington Magnum", RIMLESS, 9.6, 9.6, 9.1, 6.4, 47.0, 37.18, 57.9, 5.7, SPITZER, ["222remmag"]),
        c("6.5-284 Norma", RIMLESS, 12.0, 12.7, 12.1, 7.5, 55.1, 44.98, 82.0, 6.7, SPITZER, ["6.5-284"]),
        # Weatherby RPM family (rebated rim, 6.5-284 body lengthened). The .25 is from the 2026 SAAMI drawing;
        # the 6.5 and .338 share its rim, head and shoulder diameter, with neck and shoulder height estimated.
        c(".25 Weatherby RPM", RIMLESS, 12.01, 12.7, 12.14, 7.37, 60.96, 50.48, 84.84, 6.53, SPITZER, ["25rpm", "25wbyrpm"]),
        c("6.5 Weatherby RPM", RIMLESS, 12.01, 12.7, 12.14, 7.54, 65.28, 54.80, 84.84, 6.71, SPITZER, ["6.5rpm", "6.5wbyrpm", "65rpm"]),
        c(".338 Weatherby RPM", RIMLESS, 12.01, 12.7, 12.04, 9.25, 64.77, 54.85, 82.55, 8.59, SPITZER, ["338rpm", "338wbyrpm"]),
        c(".30-378 Weatherby Magnum", BELTED, 14.7, 14.8, 14.2, 8.6, 74.0, 61.2, 93.7, 7.82, SPITZER, ["30-378"]),
        c("5.6x57 mm", RIMLESS, 11.95, 11.9, 10.94, 7.1, 56.7, 44.51, 69.0, 5.7, SPITZER, ["5.6x57"]),
        # Smokeless rounds from batches 6 and 7, first misplaced under Schwarzpulver.
        c("6.5x53 mm R Mannlicher", RIMMED, 13.4, 11.48, 10.75, 7.55, 53.5, 43.33, 77.47, 6.65, ROUND, ["6.5x53r", "6.5dutch"]),
        c("8x58 mm R Danish Krag", RIMMED, 14.65, 12.75, 11.95, 8.98, 58.0, 41.96, 78.0, 8.2, ROUND, ["8x58r", "danishkrag"]),
        c("7.62x45 mm vz. 52", RIMLESS, 11.3, 11.3, 10.56, 8.66, 45.0, 36.2, 60.0, 7.83, SPITZER, ["7.62x45", "vz52"]),
        c("7.92x107 mm DS", RIMLESS, 16.36, 16.39, 13.15, 9.23, 107.18, 95.28, 132.0, 8.18, SPITZER, ["7.92x107", "7.92ds"]),
        c("7.65x53 mm Argentine", RIMLESS, 11.96, 12.01, 11.0, 8.73, 53.6, 44.6, 76.0, 7.92, SPITZER, ["7.65x53", "7.65argentine", "7.65belgian"]),
        # Batch 7 (2026-11): dimensions from the page named in INTRODUCED (or the parent page), rounded; shoulder heights estimated; rims of the R variants estimated.
        c(".338 Norma Magnum", RIMLESS, 14.93, 14.87, 14.5, 9.4, 63.3, 47.78, 93.5, 8.6, SPITZER, ["338nm"]),
        c(".308 Norma Magnum", BELTED, 13.5, 13.0, 12.5, 8.1, 65.0, 53.05, 85.0, 7.82, SPITZER, ["308nm"]),
        c(".358 Norma Magnum", BELTED, 13.5, 13.03, 12.45, 9.85, 64.0, 52.94, 85.0, 9.12, ROUND, ["358nm"]),
        c("9.3x64 mm Brenneke", RIMLESS, 12.6, 12.88, 12.05, 10.04, 64.0, 52.09, 85.6, 9.3, ROUND, ["9.3x64"]),
        c("9.3x57 mm Mauser", RIMLESS, 11.95, 11.95, 10.95, 10.0, 56.5, 45.86, 81.0, 9.3, ROUND, ["9.3x57"]),
        c("9x57 mm Mauser", RIMLESS, 11.9, 11.9, 10.9, 9.8, 56.8, 46.2, 81.0, 9.1, ROUND, ["9x57"]),
        c("7x57 mm R", RIMMED, 13.0, 12.05, 10.92, 8.25, 57.0, 43.8, 80.0, 7.25, SPITZER, ["7x57r"]),
        c("6.5x57 mm R", RIMMED, 13.0, 11.9, 10.94, 7.65, 56.7, 44.5, 82.0, 6.7, SPITZER, ["6.5x57r"]),
        c(".338 Remington Ultra Magnum", RIMLESS, 13.6, 14.0, 13.4, 9.4, 70.1, 58.32, 91.4, 8.6, SPITZER, ["338rum"]),
        c("7 mm Remington Ultra Magnum", RIMLESS, 13.5, 13.97, 13.34, 8.1, 72.4, 60.64, 91.4, 7.2, SPITZER, ["7rum"]),
        c(".325 Winchester Short Magnum", RIMLESS, 13.6, 14.1, 13.7, 8.9, 53.3, 42.25, 72.6, 8.2, SPITZER, ["325wsm"]),
        c(".375 Weatherby Magnum", BELTED, 13.5, 13.0, 12.5, 10.2, 72.6, 61.75, 91.4, 9.5, ROUND, ["375wby"]),
        c(".460 Weatherby Magnum", BELTED, 14.7, 14.8, 14.2, 12.2, 74.0, 60.39, 93.0, 11.6, ROUND, ["460wby"]),
        c(".404 Jeffery", RIMLESS, 13.79, 13.84, 13.46, 11.48, 73.02, 50.82, 89.66, 10.72, ROUND, ["404jeffery", "10.75x73"]),
        c(".505 Gibbs", RIMLESS, 16.3, 16.3, 15.2, 13.6, 80.0, 62.43, 97.8, 12.8, ROUND, ["505gibbs"]),
        c(".500 Jeffery", RIMLESS, 14.6, 15.7, 15.4, 13.7, 70.0, 57.61, 88.0, 13.0, ROUND, ["500jeffery", "12.7x70"]),
        c(".416 Barrett", RIMLESS, 20.4, 20.4, 18.5, 11.6, 83.0, 63.55, 118.0, 10.6, SPITZER, ["416barrett"]),
        c("12.7x108 mm", RIMLESS, 21.7, 21.75, 18.9, 13.95, 108.0, 88.13, 147.5, 12.98, SPITZER, ["12.7x108", "dshk"]),
    ]),
    ("Schwarzpulver", [
        ball(".36 Rundkugel (.375)", 9.5, ["36", "36navy", ".375ball"]),
        ball(".44 Rundkugel (.454)", 11.5, ["44", "44ball", ".454", "454ball"]),
        ball(".45 Rundkugel (.440)", 11.2, ["45ball", ".440"]),
        ball(".50 Rundkugel (.490)", 12.4, ["50", "50ball", ".490"]),
        ball(".54 Rundkugel (.530)", 13.5, ["54", "54ball", ".530"]),
        minie(".58 Minié", 14.6, 25.0, ["58", "58minie"]),
        minie(".69 Minié", 17.3, 27.0, ["69", "69minie"]),
        c("10.4x38 mm R Vetterli", RIMMED, 15.7, 13.62, 13.1, 11.43, 38.21, 26.11, 56.22, 10.92, ROUND, ["vetterli", "10.4", "10.4vetterli", "10.4x38"]),
        # Swiss rimfire for the Milbank-Amsler conversion of the 18 mm Infanteriegewehr 1842/1859 (Thun).
        # Drawing on municion.org (AECC ref. 18-026-CBR-010): rim 20.72 (1.74 thick), head 18.58, mouth 18.27,
        # bullet 18.15, case 25.54, overall 39.92. AECC 18-025-BBR-010 (labelled for the converted French
        # 1864 rifle) is a close variant: rim 20.50, head 18.62, mouth 17.96, case 25.45, overall 40.40.
        straight("18 mm Milbank-Amsler", RIMFIRE, 20.72, 18.58, 18.27, 25.54, 39.92, 18.15, ROUND,
                 ["milbankamsler", "milbank-amsler", "milbank", "18x25r", "18x25.7r"]),
        # Rimfire of the Ordonnanzrevolver 1872 (Thun), before the 1878 centrefire change. Drawing on municion.org
        # (AECC ref. 11-018-CBR-010): rim 12.70 (1.50 thick), head 10.95, mouth 10.85, bullet 10.85, case 18.23, overall 30.52.
        straight("10.4 mm Swiss Ordnance 1872 Rimfire", RIMFIRE, 12.7, 10.95, 10.85, 18.23, 30.52, 10.85, ROUND,
                 ["10.4rf", "revolver72", "10.4x18", "10.4mmrf"]),
        straight(".577 Snider", RIMMED, 19.2, 17.0, 16.4, 50.8, 62.0, 14.6, ROUND, ["577snider"]),
        c(".577/450 Martini-Henry", RIMMED, 19.0, 17.0, 16.0, 12.3, 59.7, 35.71, 79.0, 11.6, ROUND, ["martini-henry", "577/450"]),
        straight(".50-70 Government", RIMMED, 16.9, 14.2, 13.4, 44.5, 57.0, 13.0, ROUND, ["50-70"]),
        c(".44-40 WCF", RIMMED, 13.1, 11.9, 11.5, 11.1, 33.2, 23.58, 40.6, 10.8, FLAT, ["44-40", "4440"]),
        # Added 2026-11: dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c("11x59 mm R Gras", RIMMED, 16.9, 13.8, 13.5, 11.9, 59.0, 38.55, 76.0, 11.3, ROUND, ["11gras", "gras"]),
        # Batch 6 (2026-11): dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c("11x60 mm R Mauser", RIMMED, 14.9, 13.1, 13.0, 11.8, 60.0, 36.4, 71.1, 11.3, ROUND, ["11mauser", "11x60r"]),
        straight(".32-40 Ballard", RIMMED, 12.9, 10.8, 8.6, 54.0, 66.0, 8.1, FLAT, ["32-40"]),
        straight(".50-90 Sharps", RIMMED, 16.8, 14.9, 13.4, 64.0, 81.0, 13.0, ROUND, ["50-90", "50sharps"]),
        # Batch 11 (2026-11): old rimfire, black-powder and British rounds plus 9x25 Dillon and .300 Lapua; dimensions from the page named in INTRODUCED, rounded; shoulder heights estimated.
        c(".45-75 Winchester", RIMMED, 15.81, 14.24, 13.87, 12.2, 47.86, 26, 56.52, 11.39, FLAT, ["45-75"]),
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
        # BBs: loose balls, not cartridges. Steel BBs (zinc or copper plated) measure 4.3-4.4 mm and
        # are fired from smoothbore .177 BB guns; airsoft BBs are plastic, 6 mm, a few guns take 8 mm.
        ball("4.4 mm Stahl-BB (.177 BB)", 4.35, ["bb", "steelbb", "stahlbb", "4.4mm"]),
        ball("6 mm Airsoft-BB", 6.0, ["airsoft", "6mmbb", "6mmairsoft"]),
        ball("8 mm Airsoft-BB", 8.0, ["8mmbb", "8mmairsoft"]),
    ]),
]

# Printable alternative names (max 2), shown in the app's calibre lists and search,
# and on the calibre poster. Never alias calibres that are separate cartridges:
# .223 Rem / 5.56 NATO / GP 90 and .308 Win / 7.62 NATO differ in loading and are
# not necessarily interchangeable, so each stays its own entry.
DISPLAY_ALIASES = {
    ".22 LR": [".22 Long Rifle", "KK"],
    ".22 Blank (6.8/11)": [".22 Platzpatrone", "Setzkartusche 6.8/11"],
    "9 mm P.A.K.": ["9 mm P.A. Knall", "9 mm PA Blanc"],
    "8 mm Knall": ["8 mm P.A.K.", "8 mm Blanc"],
    "9 mm R Knall": ["9 mm R.K.", ".380 R Blanc"],
    ".22 Long Knall": [".22 lang Knall", "Setzkartusche 5.6/16"],
    ".22 WMR": [".22 Magnum"],
    "7.65 mm Browning (.32 ACP)": [".32 ACP", ".32 Auto"],
    "7.65 mm Parabellum": [".30 Luger"],
    ".32 S&W Long Wadcutter": [".32 S&W Long WC"],
    "9 mm Browning kurz (.380 ACP)": [".380 ACP", ".380 Auto"],
    "9x19 mm": ["9 mm Luger", "9 mm Para"],
    ".38 Special": [".38 Spl"],
    ".45 ACP": [".45 Auto", "11,43 mm"],
    ".45 Colt": [".45 Long Colt"],
    ".320 Revolver": [".320 Short"],
    "9 mm Flobert Bosquette": ["9 mm Flobert Kugel"],
    ".30-06 Springfield": ["7.62x63 mm"],
    ".300 AAC Blackout": [".300 BLK", "7.62x35 mm"],
    "7.5x55 mm Swiss (GP 11)": ["GP 11", "7.5 mm Swiss"],
    "7.5x53.5 mm Swiss (GP 1890)": ["GP 1890", "GP 90/23"],
    "7.5 mm Kadettenpatrone": ["Cart. 7,5 mm cadets", "Cart. 7,5 mm cadetti"],
    "8x57 mm IS": ["8 mm Mauser"],
    ".50 BMG": ["12,7x99 mm NATO"],
}

# Primer per calibre: the primer of the original factory ammunition, which is today's Boxer size
# for calibres still loaded. Primers sit in the centre of the case head. Old British Nitro
# Expresses and some old European rounds came with the large .254" Berdan "Nitro" primer
# (Kynoch #40, today RWS 6507), measured on headstamp photos (see PRIMER_SOURCES). Other Berdan
# primers (4.5 and 5.5 mm, e.g. 7.62x39, 7.62x54R surplus) are within 0.2 mm of a Boxer size and
# keep that kind; rimfire and caseless entries have none.
SMALL_PISTOL, LARGE_PISTOL, SMALL_RIFLE, LARGE_RIFLE, SHOTSHELL_209, BMG_35, BERDAN_NITRO = (
    "small-pistol", "large-pistol", "small-rifle", "large-rifle", "shotshell-209", "bmg-35",
    "berdan-nitro")
PRIMER_DIAMETERS = {  # mm, nominal primer cup diameter
    SMALL_PISTOL: 4.45, SMALL_RIFLE: 4.45,     # .175"
    LARGE_PISTOL: 5.33, LARGE_RIFLE: 5.33,     # .210"
    SHOTSHELL_209: 6.15,                       # .242"
    BMG_35: 8.03,                              # .316", CCI #35
    BERDAN_NITRO: 6.45,                        # .254", Kynoch #40 / RWS 6507
}
PRIMERS = {
    ".450 No. 2 Nitro Express": LARGE_RIFLE,
    ".500/416 Nitro Express": LARGE_RIFLE,
    ".375 Flanged Magnum Nitro Express": LARGE_RIFLE,
    "9.3x53 mm R Finnish": LARGE_RIFLE,
    "10.3x60 mm R": BERDAN_NITRO,
    "7x61 mm Sharpe & Hart": LARGE_RIFLE,
    ".360 No. 5 Rook": SMALL_PISTOL,
    "6.35 mm Browning (.25 ACP)": SMALL_PISTOL, "7.65 mm Browning (.32 ACP)": SMALL_PISTOL,
    "7.65 mm Parabellum": SMALL_PISTOL, ".32 S&W Long": SMALL_PISTOL, ".32 H&R Magnum": SMALL_PISTOL,
    ".32 S&W Long Wadcutter": SMALL_PISTOL,
    "7.62x25 mm Tokarev": SMALL_PISTOL, "9 mm Browning kurz (.380 ACP)": SMALL_PISTOL,
    "7.63x25 mm Mauser": SMALL_PISTOL, "7.62x38 mm R Nagant": SMALL_PISTOL, "7.5 mm Swiss Ordnance 1882": SMALL_PISTOL,
    "7.65 mm Longue": SMALL_PISTOL, ".30 Super Carry": SMALL_PISTOL, ".32 S&W": SMALL_PISTOL, ".320 Revolver": SMALL_PISTOL,
    ".327 Federal Magnum": SMALL_PISTOL, ".32-20 Winchester": SMALL_PISTOL, "5.45x18 mm": SMALL_PISTOL,
    ".22 TCM": SMALL_PISTOL, "8 mm Nambu": SMALL_PISTOL, "8 mm Lebel revolver": SMALL_PISTOL,
    "8 mm Roth-Steyr": SMALL_PISTOL, "9 mm Glisenti": SMALL_PISTOL, "9 mm Browning Long": SMALL_PISTOL,
    "9x23 mm Steyr": SMALL_PISTOL, "9x23 mm Largo": SMALL_PISTOL, ".38 S&W": SMALL_PISTOL,
    ".38 Short Colt": SMALL_PISTOL, ".38 Long Colt": SMALL_PISTOL, ".38-40 Winchester": LARGE_PISTOL,
    "10.4 mm Swiss Ordnance 1878": LARGE_PISTOL, ".44 S&W Russian": LARGE_PISTOL, "11 mm French Ordnance": LARGE_PISTOL,
    ".45 Schofield": LARGE_PISTOL, ".45 Auto Rim": LARGE_PISTOL, ".455 Webley": LARGE_PISTOL,
    ".480 Ruger": LARGE_PISTOL, ".50 Action Express": LARGE_PISTOL,
    "9x18 mm Makarov": SMALL_PISTOL, "9x19 mm": SMALL_PISTOL, "9 mm P.A.K.": SMALL_PISTOL, "9x21 mm IMI": SMALL_PISTOL,
    # Alarm blanks: not reloadable, primed with small pistol size caps.
    "8 mm Knall": SMALL_PISTOL, ".315 Knall": SMALL_PISTOL, "9 mm R Knall": SMALL_PISTOL,
    ".320 Knall": SMALL_PISTOL, ".45 Knall": SMALL_PISTOL,
    ".357 SIG": SMALL_PISTOL, ".38 Special": SMALL_PISTOL, ".357 Magnum": SMALL_PISTOL,
    ".38 Super": SMALL_PISTOL, "10 mm Auto": LARGE_PISTOL, ".40 S&W": SMALL_PISTOL,
    ".41 Magnum": LARGE_PISTOL, ".44 Special": LARGE_PISTOL, ".44 Magnum": LARGE_PISTOL,
    ".45 ACP": LARGE_PISTOL, ".45 Colt": LARGE_PISTOL, ".45 GAP": SMALL_PISTOL,
    ".454 Casull": SMALL_RIFLE, ".460 S&W Magnum": LARGE_RIFLE, ".500 S&W Magnum": LARGE_RIFLE,
    "5.7x28 mm": SMALL_RIFLE, "4.6x30 mm": SMALL_RIFLE,
    ".204 Ruger": SMALL_RIFLE, ".222 Remington": SMALL_RIFLE, ".223 Remington": SMALL_RIFLE,
    "5.56x45 mm NATO": SMALL_RIFLE, "5.6 mm GP 90": SMALL_RIFLE, ".22-250 Remington": LARGE_RIFLE,
    ".243 Winchester": LARGE_RIFLE, "6 mm BR Norma": SMALL_RIFLE, "6 mm ARC": SMALL_RIFLE,
    "6.5 mm Creedmoor": LARGE_RIFLE, "6.5x55 mm Swedish": LARGE_RIFLE, "6.5x47 mm Lapua": SMALL_RIFLE,
    "6.5 PRC": LARGE_RIFLE, ".260 Remington": LARGE_RIFLE, ".270 Winchester": LARGE_RIFLE,
    "7 mm-08 Remington": LARGE_RIFLE, "7x57 mm Mauser": LARGE_RIFLE, "7x64 mm": LARGE_RIFLE,
    "7 mm Remington Magnum": LARGE_RIFLE, "7 mm PRC": LARGE_RIFLE, "7.5x55 mm Swiss (GP 11)": LARGE_RIFLE,
    "7.5x53.5 mm Swiss (GP 1890)": LARGE_RIFLE,
    "7.5 mm Kadettenpatrone": LARGE_RIFLE,
    "7.5x54 mm French": LARGE_RIFLE, "7.62x39 mm": LARGE_RIFLE, ".300 AAC Blackout": SMALL_RIFLE, ".300 HAM'R": SMALL_RIFLE,
    "7.62x51 mm NATO": LARGE_RIFLE, ".308 Winchester": LARGE_RIFLE, ".30-06 Springfield": LARGE_RIFLE,
    ".30-30 Winchester": LARGE_RIFLE, ".300 Winchester Magnum": LARGE_RIFLE, ".300 PRC": LARGE_RIFLE,
    ".300 Norma Magnum": LARGE_RIFLE, ".303 British": LARGE_RIFLE, "7.62x54 mm R": LARGE_RIFLE,
    "8x57 mm IS": LARGE_RIFLE, "8x68 mm S": LARGE_RIFLE, "9.3x62 mm": LARGE_RIFLE, "9.3x74 mm R": LARGE_RIFLE,
    ".338 Lapua Magnum": LARGE_RIFLE, ".375 H&H Magnum": LARGE_RIFLE, ".416 Rigby": LARGE_RIFLE,
    ".450 Rigby": LARGE_RIFLE, ".375 CheyTac": LARGE_RIFLE,
    ".45-70 Government": LARGE_RIFLE, ".50 BMG": BMG_35,
    "6.5x52 mm Carcano": LARGE_RIFLE, "6.5x50 mm SR Arisaka": LARGE_RIFLE, "7.7x58 mm Arisaka": LARGE_RIFLE,
    "8x50 mm R Lebel": LARGE_RIFLE, "8x56 mm R Mannlicher": LARGE_RIFLE, "8x50 mm R Mannlicher": LARGE_RIFLE,
    "7.35x51 mm Carcano": LARGE_RIFLE, "6.5x54 mm Mannlicher-Schönauer": LARGE_RIFLE,
    ".30-40 Krag": LARGE_RIFLE, "7.92x33 mm Kurz": LARGE_RIFLE, "5.45x39 mm": SMALL_RIFLE,
    ".277 SIG Fury": LARGE_RIFLE, "5.8x42 mm": SMALL_RIFLE,
    ".22 Hornet": SMALL_RIFLE, ".25-06 Remington": LARGE_RIFLE, ".257 Roberts": LARGE_RIFLE,
    ".280 Remington": LARGE_RIFLE, ".35 Whelen": LARGE_RIFLE, ".300 H&H Magnum": LARGE_RIFLE,
    ".338 Winchester Magnum": LARGE_RIFLE, ".444 Marlin": LARGE_RIFLE, ".458 Winchester Magnum": LARGE_RIFLE,
    ".350 Legend": SMALL_RIFLE,
    # Vetterli: the original Swiss service round is rimfire; modern centrefire cases take large rifle.
    "10.4x38 mm R Vetterli": LARGE_RIFLE, ".577 Snider": LARGE_RIFLE, ".577/450 Martini-Henry": LARGE_RIFLE,
    ".50-70 Government": LARGE_RIFLE, ".44-40 WCF": LARGE_PISTOL,
    "12/70": SHOTSHELL_209, "12/76": SHOTSHELL_209, "12/89": SHOTSHELL_209, "16/70": SHOTSHELL_209,
    "20/70": SHOTSHELL_209, "20/76": SHOTSHELL_209, "28/70": SHOTSHELL_209, ".410/76": SHOTSHELL_209,
    "5.6x50 mm Magnum": SMALL_RIFLE,
    "6.5x57 mm Mauser": LARGE_RIFLE,
    "6.5x68 mm": LARGE_RIFLE,
    "8x64 mm S": LARGE_RIFLE,
    "8x60 mm S": LARGE_RIFLE,
    "9.5x57 mm Mannlicher-Schönauer": LARGE_RIFLE,
    ".375 Ruger": LARGE_RIFLE,
    ".450 Bushmaster": SMALL_RIFLE,
    "6.8 mm Remington SPC": LARGE_RIFLE,
    ".300 Winchester Short Magnum": LARGE_RIFLE,
    ".17 Remington": SMALL_RIFLE,
    ".218 Bee": SMALL_RIFLE,
    ".25-35 Winchester": LARGE_RIFLE,
    ".32 Winchester Special": LARGE_RIFLE,
    ".35 Remington": LARGE_RIFLE,
    ".38-55 Winchester": LARGE_RIFLE,
    ".348 Winchester": LARGE_RIFLE,
    ".358 Winchester": LARGE_RIFLE,
    ".264 Winchester Magnum": LARGE_RIFLE,
    ".300 Weatherby Magnum": LARGE_RIFLE,
    ".416 Remington Magnum": LARGE_RIFLE,
    ".470 Nitro Express": LARGE_RIFLE,
    "9x18 mm Ultra": SMALL_PISTOL,
    ".357 Remington Maximum": SMALL_RIFLE,
    ".41 Action Express": SMALL_PISTOL,
    ".45 Winchester Magnum": LARGE_PISTOL,
    ".45 Super": LARGE_PISTOL,
    ".460 Rowland": LARGE_PISTOL,
    ".475 Linebaugh": LARGE_PISTOL,
    ".221 Remington Fireball": SMALL_RIFLE,
    ".25 NAA": SMALL_PISTOL,
    ".32 NAA": SMALL_PISTOL,
    ".32 Long Colt": SMALL_PISTOL,
    "5.75 mm Velo-Dog": SMALL_PISTOL, ".500 JRH": LARGE_PISTOL,
    ".375 Flanged Nitro Express": BERDAN_NITRO, ".45-90 WCF": LARGE_RIFLE,
    ".55 Boys": BMG_35,
    ".35 S&W Auto": SMALL_PISTOL,
    ".38 ACP": SMALL_PISTOL,
    ".41 Long Colt": SMALL_PISTOL,
    ".44 Colt": LARGE_PISTOL,
    ".442 Webley": LARGE_PISTOL,
    ".450 Adams": SMALL_PISTOL,
    ".476 Enfield": SMALL_PISTOL,
    "11x59 mm R Gras": BERDAN_NITRO,
    ".32-40 Ballard": LARGE_RIFLE,
    ".50-90 Sharps": LARGE_RIFLE,
    ".220 Swift": LARGE_RIFLE,
    ".25-20 Winchester": SMALL_RIFLE,
    ".250 Savage": LARGE_RIFLE,
    ".257 Weatherby Magnum": LARGE_RIFLE,
    ".270 Weatherby Magnum": LARGE_RIFLE,
    "7 mm Weatherby Magnum": LARGE_RIFLE,
    ".340 Weatherby Magnum": LARGE_RIFLE,
    ".284 Winchester": LARGE_RIFLE,
    ".300 Savage": LARGE_RIFLE,
    ".300 Remington Ultra Magnum": LARGE_RIFLE,
    ".270 Winchester Short Magnum": LARGE_RIFLE,
    "7 mm Winchester Short Magnum": LARGE_RIFLE,
    ".338 Federal": LARGE_RIFLE,
    "8 mm Remington Magnum": LARGE_RIFLE,
    ".376 Steyr": LARGE_RIFLE,
    "6.5 mm Grendel": SMALL_RIFLE,
    "6 mm Remington": LARGE_RIFLE,
    "7-30 Waters": LARGE_RIFLE,
    ".17 Hornet": SMALL_RIFLE,
    ".375 Winchester": LARGE_RIFLE,
    ".405 Winchester": LARGE_RIFLE,
    ".450 Marlin": LARGE_RIFLE,
    ".458 Lott": LARGE_RIFLE,
    ".30 Carbine": SMALL_RIFLE,
    "7x65 mm R": LARGE_RIFLE,
    ".22 Savage Hi-Power": LARGE_RIFLE,
    "8x57 mm IRS": LARGE_RIFLE,
    ".280 Ackley Improved": LARGE_RIFLE,
    ".356 Winchester": LARGE_RIFLE,
    ".307 Winchester": LARGE_RIFLE,
    ".416 Ruger": LARGE_RIFLE,
    ".416 Weatherby Magnum": LARGE_RIFLE,
    ".375 Remington Ultra Magnum": LARGE_RIFLE,
    "7 mm STW": LARGE_RIFLE,
    ".225 Winchester": LARGE_RIFLE,
    ".223 WSSM": LARGE_RIFLE,
    ".243 WSSM": LARGE_RIFLE,
    ".25 WSSM": LARGE_RIFLE,
    ".350 Remington Magnum": LARGE_RIFLE,
    ".400 Cor-Bon": SMALL_PISTOL,
    "9x23 mm Winchester": SMALL_PISTOL,
    ".356 TSW": SMALL_PISTOL,
    ".26 Nosler": LARGE_RIFLE,
    ".27 Nosler": LARGE_RIFLE,
    ".28 Nosler": LARGE_RIFLE,
    ".30 Nosler": LARGE_RIFLE,
    ".33 Nosler": LARGE_RIFLE,
    ".300 Ruger Compact Magnum": LARGE_RIFLE,
    ".30 Thompson/Center": LARGE_RIFLE,
    ".30 Remington AR": SMALL_RIFLE,
    ".308 Marlin Express": LARGE_RIFLE,
    ".300 Remington SAUM": LARGE_RIFLE,
    ".224 Valkyrie": SMALL_RIFLE,
    ".458 SOCOM": LARGE_PISTOL,
    ".50 Beowulf": LARGE_PISTOL,
    ".222 Remington Magnum": SMALL_RIFLE,
    "6.5-284 Norma": LARGE_RIFLE, ".25 Weatherby RPM": LARGE_RIFLE, "6.5 Weatherby RPM": LARGE_RIFLE, ".338 Weatherby RPM": LARGE_RIFLE,
    ".30-378 Weatherby Magnum": LARGE_RIFLE,
    "5.6x57 mm": LARGE_RIFLE,
    "11x60 mm R Mauser": LARGE_RIFLE,
    "6.5x53 mm R Mannlicher": LARGE_RIFLE,
    "8x58 mm R Danish Krag": LARGE_RIFLE,
    "7.62x45 mm vz. 52": LARGE_RIFLE,
    "7.92x107 mm DS": LARGE_RIFLE,
    "7.65x53 mm Argentine": LARGE_RIFLE,
    ".338-378 Weatherby Magnum": LARGE_RIFLE,
    "6.8 Western": LARGE_RIFLE,
    "7 mm Remington SAUM": LARGE_RIFLE,
    ".22 Remington Jet": SMALL_PISTOL,
    ".256 Winchester Magnum": SMALL_PISTOL,
    ".338 Norma Magnum": LARGE_RIFLE,
    ".308 Norma Magnum": LARGE_RIFLE,
    ".358 Norma Magnum": LARGE_RIFLE,
    "9.3x64 mm Brenneke": LARGE_RIFLE,
    "9.3x57 mm Mauser": LARGE_RIFLE,
    "9x57 mm Mauser": LARGE_RIFLE,
    "7x57 mm R": LARGE_RIFLE,
    "6.5x57 mm R": LARGE_RIFLE,
    ".338 Remington Ultra Magnum": LARGE_RIFLE,
    "7 mm Remington Ultra Magnum": LARGE_RIFLE,
    ".325 Winchester Short Magnum": LARGE_RIFLE,
    ".375 Weatherby Magnum": LARGE_RIFLE,
    ".460 Weatherby Magnum": LARGE_RIFLE,
    ".404 Jeffery": LARGE_RIFLE,
    ".505 Gibbs": LARGE_RIFLE,
    ".500 Jeffery": LARGE_RIFLE,
    ".416 Barrett": BMG_35,
    "12.7x108 mm": BMG_35,
    ".33 Winchester": LARGE_RIFLE,
    ".25 Remington": LARGE_RIFLE,
    ".32 Remington": LARGE_RIFLE,
    ".35 Winchester Self-Loading": SMALL_RIFLE,
    ".351 Winchester Self-Loading": SMALL_RIFLE,
    ".401 Winchester Self-Loading": LARGE_RIFLE,
    ".40-65 Winchester": LARGE_RIFLE,
    ".303 Savage": LARGE_RIFLE,
    ".219 Zipper": LARGE_RIFLE,
    ".450 Nitro Express": LARGE_RIFLE,
    ".500 Nitro Express": LARGE_RIFLE,
    ".577 Nitro Express": LARGE_RIFLE,
    ".600 Nitro Express": LARGE_RIFLE,
    ".700 Nitro Express": LARGE_RIFLE,
    ".500/465 Nitro Express": BERDAN_NITRO,
    ".318 Westley Richards": LARGE_RIFLE,
    ".240 Weatherby Magnum": LARGE_RIFLE,
    ".224 Weatherby Magnum": LARGE_RIFLE,
    "6.5 mm Remington Magnum": LARGE_RIFLE,
    "6 mm Creedmoor": LARGE_RIFLE,
    ".25 Creedmoor": LARGE_RIFLE,
    "8.6 Blackout": LARGE_RIFLE,
    ".22 ARC": SMALL_RIFLE,
    ".338 Ruger Compact Magnum": LARGE_RIFLE,
    ".408 CheyTac": LARGE_RIFLE,
    ".360 Buckhammer": LARGE_RIFLE,
    ".400 Legend": SMALL_RIFLE,
    "9.3x72 mm R": BERDAN_NITRO,
    "8x75 mm RS": LARGE_RIFLE,
    "6.5x65 mm RWS": LARGE_RIFLE,
    "9.3x66 mm Sako (.370 Sako Magnum)": LARGE_RIFLE,
    ".300 Blaser Magnum": LARGE_RIFLE,
    ".375 Blaser Magnum": LARGE_RIFLE,
    "7 mm Blaser Magnum": LARGE_RIFLE,
    ".338 Blaser Magnum": LARGE_RIFLE,
    "8.5x55 mm Blaser": LARGE_RIFLE,
    ".450/400 Nitro Express 3 inch": LARGE_RIFLE,
    ".40-82 WCF": LARGE_RIFLE,
    ".50-95 WCF": LARGE_RIFLE,
    ".38-56 WCF": LARGE_RIFLE,
    ".30 Remington": LARGE_RIFLE,
    ".17 Remington Fireball": SMALL_RIFLE,
    ".338 Marlin Express": LARGE_RIFLE,
    ".22 Nosler": SMALL_RIFLE,
    "6.5-300 Weatherby Magnum": LARGE_RIFLE,
    "9x25 mm Dillon": LARGE_PISTOL,
    ".300 Lapua Magnum": LARGE_RIFLE,
    ".35 Winchester": LARGE_RIFLE,
    ".50-110 Winchester": LARGE_RIFLE,
    ".400 H&H Magnum": LARGE_RIFLE,
    ".244 H&H Magnum": LARGE_RIFLE,
    ".45-75 Winchester": LARGE_RIFLE,
    ".465 H&H Magnum": LARGE_RIFLE,
    ".475 No. 2 Nitro Express": BERDAN_NITRO,
    ".400/350 Nitro Express": LARGE_RIFLE,
    ".350 Rigby Magnum": LARGE_RIFLE,
    ".310 Cadet": SMALL_RIFLE,
    "6.5x58 mm Vergueiro": LARGE_RIFLE,
    ".30 R Blaser": LARGE_RIFLE,
    ".378 Weatherby Magnum": LARGE_RIFLE,
    "7.5 FK": SMALL_PISTOL,
    "6 mm GT": SMALL_RIFLE,
    ".22 Creedmoor": LARGE_RIFLE,
    "7 mm Backcountry": LARGE_RIFLE,
    ".338 ARC": SMALL_RIFLE,
    "6 mm PPC": SMALL_RIFLE,
    "9x39 mm": LARGE_RIFLE,
}

# Year each calibre was first introduced: released as factory ammunition or adopted for
# service (for a wildcat, the year it became a factory round; for a military round, the year
# of adoption). Each entry names the page the year was checked against. Calibres without a
# introduction year (shot shells, loose balls, pellets) are listed in INTRODUCED_UNKNOWN with
# the reason, so a new calibre has to be put in one of the two. Where sources disagree or give
# only a period, the earliest probable year is used.
_WP = "https://en.wikipedia.org/wiki/"
INTRODUCED = {
    ".450 No. 2 Nitro Express": (1903, _WP + ".450_No_2_Nitro_Express"),
    "7x61 mm Sharpe & Hart": (1953, _WP + "7%C3%9761mm_Sharpe_%26_Hart"),  # developed on a 1953 trip
    ".360 No. 5 Rook": (1875, _WP + ".360_No._5_Rook"),  # introduced 1875-1880
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
    "9 mm P.A.K.": (1991, "https://360.lexisnexis.at/media/attachment/2019_ii_435-coo_2026_100_2_1703759-anlage11/pdf"),  # C.I.P. sheet 1991-07-30, no earlier source
    # C.I.P. Tab. VIII sheet dates (1991-07-29 to 1991-08-02); no earlier source found for these blanks.
    **{n: (1991, "https://360.lexisnexis.at/media/attachment/2019_ii_435-coo_2026_100_2_1703759-anlage11/pdf") for n in (
        "8 mm Knall", ".315 Knall", "9 mm R Knall", ".320 Knall", ".45 Knall", ".22 Long Knall", "6 mm Flobert Knall")},
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
    "5.6 mm GP 90": (1990, _WP + "SIG_SG_550"),  # adopted with the Stgw 90
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
    ".300 HAM'R": (2018, "https://athlonoutdoors.com/article/wilson-combat-300-hamr-cartridge/"),
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
    ".450 Rigby": (1994, _WP + ".450_Rigby"),           # named 1994, produced from 1995
    ".375 CheyTac": (2007, _WP + ".408_Cheyenne_Tactical"),  # infobox says 2009, text has .375 variants by 2007; C.I.P. 2017
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
    ".277 SIG Fury": (2019, _WP + ".277_Fury"),
    "5.8x42 mm": (1987, _WP + "5.8×42mm"),
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
    ".320 Revolver": (1868, _WP + ".320_Revolver"),  # Webley Bull Dog
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
    "18 mm Milbank-Amsler": (1867, "https://municion.org/producto/18-x-257-r-rf-milbank-amsler/"),
    "10.4 mm Swiss Ordnance 1872 Rimfire": (1872, "https://municion.org/producto/104-mm-swiss-rf-m-1872/"),
    "9.3x74 mm R": (1900, _WP + "9.3×74mmR"),                       # "c. 1900"
    "5.6x50 mm Magnum": (1970, _WP + "5.6×50mm_Magnum"),
    "6.5x57 mm Mauser": (1893, _WP + "6.5×57mm_Mauser"),
    "6.5x68 mm": (1939, _WP + "6.5×68mm"),
    "8x64 mm S": (1912, _WP + "8×64mm_S"),
    "9.5x57 mm Mannlicher-Schönauer": (1910, _WP + "9.5×57mm_Mannlicher–Schönauer"),
    ".375 Ruger": (2007, _WP + ".375_Ruger"),
    ".450 Bushmaster": (2007, _WP + ".450_Bushmaster"),
    "6.8 mm Remington SPC": (2002, _WP + "6.8mm_Remington_SPC"),
    ".300 Winchester Short Magnum": (2001, _WP + ".300_Winchester_Short_Magnum"),
    ".17 Remington": (1971, _WP + ".17_Remington"),
    ".218 Bee": (1937, _WP + ".218_Bee"),
    ".25-35 Winchester": (1895, _WP + ".25-35_Winchester"),
    ".32 Winchester Special": (1899, _WP + ".32_Winchester_Special"),
    ".35 Remington": (1906, _WP + ".35_Remington"),
    ".38-55 Winchester": (1884, _WP + ".38-55_Winchester"),
    ".348 Winchester": (1936, _WP + ".348_Winchester"),
    ".358 Winchester": (1955, _WP + ".358_Winchester"),
    ".264 Winchester Magnum": (1959, _WP + ".264_Winchester_Magnum"),
    ".300 Weatherby Magnum": (1944, _WP + ".300_Weatherby_Magnum"),
    ".416 Remington Magnum": (1989, _WP + ".416_Remington_Magnum"),
    ".470 Nitro Express": (1907, _WP + ".470_Nitro_Express"),
    "9x18 mm Ultra": (1936, _WP + "9×18mm_Ultra"),
    ".357 Remington Maximum": (1983, _WP + ".357_Remington_Maximum"),
    ".41 Action Express": (1986, _WP + ".41_Action_Express"),
    ".45 Winchester Magnum": (1979, _WP + ".45_Winchester_Magnum"),
    ".45 Super": (1988, _WP + ".45_Super"),
    ".460 Rowland": (1997, _WP + ".460_Rowland"),
    ".475 Linebaugh": (1988, _WP + ".475_Linebaugh"),
    ".221 Remington Fireball": (1963, _WP + ".221_Remington_Fireball"),
    ".25 NAA": (2002, _WP + ".25_NAA"),
    ".32 NAA": (2002, _WP + ".32_NAA"),
    ".32 Long Colt": (1873, _WP + ".32_Long_Colt"),
    ".22 Extra Long": (1878, "https://municion.org/producto/22-extra-long-rf-us/"),
    ".32 Short Rimfire": (1865, "https://municion.org/producto/32-short-rf/"),  # "c1865"
    ".32 Long Rimfire": (1861, "https://municion.org/producto/32-long-rf/"),
    "5.75 mm Velo-Dog": (1894, "https://municion.org/producto/56-mm-velo-dog/"),
    ".500 JRH": (1993, "https://municion.org/producto/500-jrh/"),
    ".375 Flanged Nitro Express": (1899, "https://municion.org/producto/375-flanged-nitro-express/"),
    ".55 Boys": (1936, "https://municion.org/producto/55-boys/"),
    ".45-90 WCF": (1886, "https://municion.org/producto/45-90-300-winchester-cf/"),
    ".35 S&W Auto": (1912, _WP + ".35_S%26W_Auto"),
    ".38 ACP": (1900, _WP + ".38_ACP"),
    ".41 Long Colt": (1877, _WP + ".41_Long_Colt"),
    ".44 Colt": (1871, _WP + ".44_Colt"),
    ".442 Webley": (1868, _WP + ".442_Webley"),
    ".450 Adams": (1868, _WP + ".450_Adams"),
    ".476 Enfield": (1881, _WP + ".476_Enfield"),
    ".22 Long": (1871, _WP + ".22_Long"),
    ".22 BB Cap": (1845, _WP + ".22_BB"),
    "9 mm Flobert Bosquette": (1845, _WP + "9_mm_Flobert_Bosquette"),  # "Designed in 1845 by Nicolas Flobert"
    "5 mm Remington Rimfire Magnum": (1969, _WP + "5mm_Remington_Rimfire_Magnum"),
    ".17 Winchester Super Magnum": (2013, _WP + ".17_Winchester_Super_Magnum"),
    ".44 Henry": (1860, _WP + ".44_Henry"),
    "11x59 mm R Gras": (1874, _WP + "11×59mmR_Gras"),
    ".32-40 Ballard": (1884, _WP + ".32-40_Ballard"),
    ".50-90 Sharps": (1872, _WP + ".50-90_Sharps"),
    ".220 Swift": (1935, _WP + ".220_Swift"),
    ".25-20 Winchester": (1895, _WP + ".25-20_Winchester"),
    ".250 Savage": (1915, _WP + ".250-3000_Savage"),
    ".257 Weatherby Magnum": (1945, _WP + ".257_Weatherby_Magnum"),
    ".270 Weatherby Magnum": (1943, _WP + ".270_Weatherby_Magnum"),
    "7 mm Weatherby Magnum": (1940, _WP + "7mm_Weatherby_Magnum"),
    ".340 Weatherby Magnum": (1962, _WP + ".340_Weatherby_Magnum"),
    ".284 Winchester": (1963, _WP + ".284_Winchester"),
    ".300 Savage": (1920, _WP + ".300_Savage"),
    ".300 Remington Ultra Magnum": (1999, _WP + ".300_Remington_Ultra_Magnum"),
    ".270 Winchester Short Magnum": (2002, _WP + ".270_Winchester_Short_Magnum"),
    "7 mm Winchester Short Magnum": (2001, _WP + "7mm_Winchester_Short_Magnum"),
    ".338 Federal": (2006, _WP + ".338_Federal"),
    "8 mm Remington Magnum": (1978, _WP + "8mm_Remington_Magnum"),
    ".376 Steyr": (1999, _WP + ".376_Steyr"),
    "6.5 mm Grendel": (2003, _WP + "6.5mm_Grendel"),
    "6 mm Remington": (1955, _WP + "6mm_Remington"),
    "7-30 Waters": (1984, _WP + "7-30_Waters"),
    ".375 Winchester": (1978, _WP + ".375_Winchester"),
    ".405 Winchester": (1904, _WP + ".405_Winchester"),
    ".450 Marlin": (2000, _WP + ".450_Marlin"),
    ".458 Lott": (1989, _WP + ".458_Lott"),
    ".30 Carbine": (1941, _WP + "M1_carbine"),
    "7x65 mm R": (1917, _WP + "7×64mm"),
    ".22 Savage Hi-Power": (1912, _WP + ".22_Savage_Hi-Power"),
    ".356 Winchester": (1982, _WP + ".356_Winchester"),
    ".307 Winchester": (1982, _WP + ".307_Winchester"),
    ".416 Ruger": (2008, _WP + ".416_Ruger"),
    ".416 Weatherby Magnum": (1989, _WP + ".416_Weatherby_Magnum"),
    ".375 Remington Ultra Magnum": (2000, _WP + ".375_Remington_Ultra_Magnum"),
    "7 mm STW": (1979, _WP + "7mm_STW"),
    ".225 Winchester": (1964, _WP + ".225_Winchester"),
    ".223 WSSM": (2002, _WP + ".223_Winchester_Super_Short_Magnum"),
    ".243 WSSM": (2003, _WP + ".243_Winchester_Super_Short_Magnum"),
    ".25 WSSM": (2004, _WP + "Winchester_Super_Short_Magnum"),
    ".350 Remington Magnum": (1965, _WP + ".350_Remington_Magnum"),
    ".400 Cor-Bon": (1997, _WP + ".400_Cor-Bon"),
    "9x23 mm Winchester": (1992, _WP + "9×23mm_Winchester"),
    ".356 TSW": (1994, _WP + ".356_TSW"),
    ".26 Nosler": (2013, _WP + ".28_Nosler"),
    ".27 Nosler": (2020, _WP + ".28_Nosler"),
    ".28 Nosler": (2015, _WP + ".28_Nosler"),
    ".30 Nosler": (2016, _WP + ".28_Nosler"),
    ".33 Nosler": (2016, _WP + ".28_Nosler"),
    ".300 Ruger Compact Magnum": (2007, _WP + ".300_Ruger_Compact_Magnum"),
    ".30 Thompson/Center": (2007, _WP + ".30_Thompson_Center"),
    ".30 Remington AR": (2008, _WP + ".30_Remington_AR"),
    ".308 Marlin Express": (2007, _WP + ".308_Marlin_Express"),
    ".300 Remington SAUM": (2001, _WP + ".300_Remington_Short_Action_Ultra_Magnum"),
    ".224 Valkyrie": (2017, _WP + ".224_Valkyrie"),
    ".458 SOCOM": (2000, _WP + ".458_SOCOM"),
    ".50 Beowulf": (2001, _WP + ".50_Beowulf"),
    ".222 Remington Magnum": (1957, _WP + ".222_Remington_Magnum"),
    "6.5-284 Norma": (1999, _WP + "6.5-284_Norma"),
    ".25 Weatherby RPM": (2026, "https://saami.org/wp-content/uploads/2026/01/Public-Introduction-25-Weatherby-RPM-2026-01-19.pdf"),
    "6.5 Weatherby RPM": (2019, "https://hodgdonpowderco.com/articles/loading-the-6-5-weatherby-rpm/"),
    ".338 Weatherby RPM": (2022, "https://www.thefirearmblog.com/blog/2022/08/02/weatherby-338-wby-rpm-cartridge/"),
    ".30-378 Weatherby Magnum": (1959, _WP + ".30-378_Weatherby_Magnum"),
    "5.6x57 mm": (1964, _WP + "5.6×57mm"),
    "11x60 mm R Mauser": (1871, _WP + "11×60mm_Mauser"),
    "6.5x53 mm R Mannlicher": (1892, _WP + "6.5×53mmR"),
    "8x58 mm R Danish Krag": (1888, _WP + "8×58mmR_Danish_Krag"),
    "7.62x45 mm vz. 52": (1952, _WP + "7.62×45mm"),
    "7.92x107 mm DS": (1931, _WP + "7.92×107mm_DS"),
    "7.65x53 mm Argentine": (1889, _WP + "7.65×53mm_Mauser"),
    ".338-378 Weatherby Magnum": (1963, _WP + ".338-378_Weatherby_Magnum"),
    "6.8 Western": (2021, _WP + "6.8_Western"),
    "7 mm Remington SAUM": (2002, _WP + "7mm_Remington_Short_Action_Ultra_Magnum"),
    ".22 Remington Jet": (1961, _WP + ".22_Remington_Jet"),
    ".256 Winchester Magnum": (1960, _WP + ".256_Winchester_Magnum"),
    ".338 Norma Magnum": (2008, _WP + ".338_Norma_Magnum"),
    ".308 Norma Magnum": (1960, _WP + ".308_Norma_Magnum"),
    "9.3x64 mm Brenneke": (1927, _WP + "9.3×64mm_Brenneke"),
    "9.3x57 mm Mauser": (1900, _WP + "9.3×57mm_Mauser"),
    ".338 Remington Ultra Magnum": (2000, _WP + ".338_Remington_Ultra_Magnum"),
    "7 mm Remington Ultra Magnum": (2002, _WP + "7mm_Remington_Ultra_Magnum"),
    ".325 Winchester Short Magnum": (2005, _WP + ".325_WSM"),
    ".375 Weatherby Magnum": (1944, _WP + ".375_Weatherby_Magnum"),
    ".460 Weatherby Magnum": (1957, _WP + ".460_Weatherby_Magnum"),
    ".404 Jeffery": (1905, _WP + ".404_Jeffery"),
    ".505 Gibbs": (1910, _WP + ".505_Gibbs"),
    ".500 Jeffery": (1920, _WP + ".500_Jeffery"),
    ".416 Barrett": (2005, _WP + ".416_Barrett"),
    "12.7x108 mm": (1934, _WP + "12.7×108mm"),
    ".33 Winchester": (1902, _WP + ".33_Winchester"),
    ".25 Remington": (1906, _WP + ".25_Remington"),
    ".32 Remington": (1906, _WP + ".32_Remington"),
    ".351 Winchester Self-Loading": (1906, _WP + ".351_Winchester_Self-Loading"),
    ".40-65 Winchester": (1887, _WP + ".40-65_Winchester"),
    ".303 Savage": (1894, _WP + ".303_Savage"),
    ".219 Zipper": (1937, _WP + ".219_Zipper"),
    ".22 Winchester Rimfire": (1890, _WP + ".22_Winchester_Rimfire"),
    ".450 Nitro Express": (1898, _WP + ".450_Nitro_Express"),
    ".500 Nitro Express": (1890, _WP + ".500_Nitro_Express"),
    ".600 Nitro Express": (1899, _WP + ".600_Nitro_Express"),
    ".700 Nitro Express": (1988, _WP + ".700_Nitro_Express"),
    ".500/465 Nitro Express": (1907, _WP + ".500/465_Nitro_Express"),
    ".318 Westley Richards": (1906, _WP + ".318_Westley_Richards"),
    ".240 Weatherby Magnum": (1968, _WP + ".240_Weatherby_Magnum"),
    ".224 Weatherby Magnum": (1963, _WP + ".224_Weatherby_Magnum"),
    "6.5 mm Remington Magnum": (1966, _WP + "6.5mm_Remington_Magnum"),
    "6 mm Creedmoor": (2009, _WP + "6.5mm_Creedmoor"),
    ".25 Creedmoor": (2025, "https://saami.org/wp-content/uploads/2025/01/Public-Introduction-25-Creedmoor-2025-01-27.pdf"),
    ".22 ARC": (2023, _WP + ".22_ARC"),
    ".338 Ruger Compact Magnum": (2008, _WP + ".338_Ruger_Compact_Magnum"),
    ".408 CheyTac": (2001, _WP + ".408_Cheyenne_Tactical"),
    ".360 Buckhammer": (2022, _WP + ".360_Buckhammer"),
    ".400 Legend": (2023, _WP + ".400_Legend"),
    ".30 Remington": (1906, _WP + ".30_Remington"),
    ".17 Remington Fireball": (2006, _WP + ".17_Remington_Fireball"),  # designed 2006, made from 2007
    ".338 Marlin Express": (2009, _WP + ".338_Marlin_Express"),
    ".38-56 WCF": (1887, _WP + ".38-56_WCF"),
    ".22 Nosler": (2017, "https://bulletin.accurateshooter.com/2017/01/22-nosler-more-details-load-data-and-a-bit-of-history"),
    "9.3x66 mm Sako (.370 Sako Magnum)": (2002, "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page71.pdf"),  # C.I.P. sheet 2002-01-22, Sako launch 2003
    ".300 Blaser Magnum": (2009, "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page114.pdf"),  # C.I.P. sheet 2009-05-05, no earlier source
    ".375 Blaser Magnum": (2009, "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page140.pdf"),  # C.I.P. sheet 2009-05-05, no earlier source
    "7 mm Blaser Magnum": (2009, "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page36.pdf"),  # C.I.P. sheet 2009-05-05, no earlier source
    ".338 Blaser Magnum": (2009, "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page130.pdf"),  # C.I.P. sheet 2009-05-05, no earlier source
    "8.5x55 mm Blaser": (2019, "https://cuzzs.gov.cz/userfiles/documents/CIP/02092021/Mimoradny_Vestnik_%202021_DEF.pdf"),  # C.I.P. sheet 2019-05-22
    ".25 Stevens": (1898, _WP + ".25_Stevens"),
    ".41 Short": (1863, _WP + ".41_Short"),
    ".56-56 Spencer": (1860, _WP + ".56-56_Spencer"),
    "9x25 mm Dillon": (1988, _WP + "9×25mm_Dillon"),
    ".300 Lapua Magnum": (1989, _WP + ".300_Lapua_Magnum"),
    ".35 Winchester": (1903, _WP + ".35_Winchester"),
    ".50-110 Winchester": (1898, _WP + ".50-110_Winchester"),
    ".400 H&H Magnum": (2003, _WP + ".400_H%26H_Magnum"),
    ".244 H&H Magnum": (1955, _WP + ".244_H%26H_Magnum"),
    ".45-75 Winchester": (1876, _WP + ".45-75_Winchester"),
    ".22 Remington Automatic": (1916, _WP + ".22_Remington_Automatic"),
    ".465 H&H Magnum": (2003, _WP + ".465_H%26H_Magnum"),
    ".400/350 Nitro Express": (1899, _WP + ".400/350_Nitro_Express"),
    ".350 Rigby Magnum": (1908, _WP + ".350_Rigby"),
    ".310 Cadet": (1900, _WP + ".310_Cadet"),
    "6.5x58 mm Vergueiro": (1904, _WP + "6.5×58mm_Vergueiro"),
    ".30 R Blaser": (1991, _WP + ".30_R_Blaser"),
    ".378 Weatherby Magnum": (1953, _WP + ".378_Weatherby_Magnum"),
    "7.5 FK": (2009, _WP + "7.5_FK"),
    ".22 Creedmoor": (2023, _WP + ".22_Creedmoor"),
    "7 mm Backcountry": (2024, _WP + "7mm_Backcountry"),
    ".338 ARC": (2025, "https://saami.org/wp-content/uploads/2025/03/Public-Introduction-338-ARC-2025-01-27.pdf"),
    "6 mm PPC": (1975, _WP + "6mm_PPC"),
    # Year of production on the municion.org product pages (AECC).
    ".17 Hornet": (2012, "https://municion.org/producto/17-hornet/"),
    ".22 TCM": (2008, "https://municion.org/producto/22-tuason-craig-micromagnum/"),  # as the Tuason Craig Micromagnum, ca. 2008
    ".280 Ackley Improved": (2006, "https://municion.org/producto/280-ackley-improved/"),  # earlier than the 2008 SAAMI acceptance
    ".35 Winchester Self-Loading": (1905, "https://municion.org/producto/35-winchester-self-loading/"),
    ".358 Norma Magnum": (1959, "https://municion.org/producto/358-norma-magnum-belted/"),
    ".375 Flanged Magnum Nitro Express": (1912, "https://municion.org/producto/375-holland-holland-flanged-magnum-ne/"),
    ".38 Short Colt": (1874, "https://municion.org/producto/38-short-colt-long-case/"),
    ".40-82 WCF": (1885, "https://municion.org/producto/40-82-260-winchester-cf-marlin/"),
    ".401 Winchester Self-Loading": (1910, "https://municion.org/producto/401-winchester-self-loading/"),
    ".50-95 WCF": (1876, "https://municion.org/producto/50-95-300-winchester/"),
    "6.5x57 mm R": (1910, "https://municion.org/producto/65-x-57-r-mauser-m88/"),  # ca. 1910
    "6.5x65 mm RWS": (1988, "https://municion.org/producto/65-x-65-rws/"),
    "7x57 mm R": (1893, "https://municion.org/producto/7-x-57-r-mauser/"),
    "8x57 mm IRS": (1905, "https://municion.org/producto/8-x-57-r-jrs-mauser/"),  # ca. 1905
    "8x60 mm S": (1919, "https://municion.org/producto/8-x-60-s/"),
    "8x75 mm RS": (1909, "https://municion.org/producto/8-x-75-r-behr/"),  # ca. 1909
    "9.3x53 mm R Finnish": (1946, "https://municion.org/producto/93-x-53-r-finnish/"),  # ca. 1946
    "9.3x72 mm R": (1892, "https://municion.org/producto/93-x-72-r/"),
    "9x39 mm": (1980, "https://municion.org/producto/9-x-39-russian/"),  # "1980s"; the other source says early 1980s
    "9x57 mm Mauser": (1890, "https://municion.org/producto/9-x-57-mauser/"),  # municion says ca. 1904, the other source the 1890s: earliest wins
    "10.3x60 mm R": (1919, "https://municion.org/producto/103-x-60-r/"),
    # Swiss cadet round for the Kadettengewehr 1897.
    "7.5 mm Kadettenpatrone": (1897, "https://swisswaffen.com/75mm-cadet-cartridge/gp90kp/wjpaihuqy7ys"),  # "First Issued: 1897"
}

INTRODUCED_UNKNOWN = {
    ".500/416 Nitro Express": "no introduction year in the sources checked",
    "6 mm GT": "sources give only the 2024 SAAMI acceptance",
    ".475 No. 2 Nitro Express": "the source gives only the early 1900s",
    ".577 Nitro Express": "the source gives only the 1890s",
    "8.6 Blackout": "sources give only the 2026 SAAMI acceptance, not when Q introduced it",
    ".22 Blank (6.8/11)": "a family of blanks and power-tool loads with no single launch",
    ".32 S&W Long Wadcutter": "C.I.P. sheet dated 1984-06-14 like the .32 S&W Long's; no launch year found",
    # Not one cartridge with one launch: shot shell sizes, loose balls and air gun pellets.
    **{n: "not a single cartridge" for n in (
        "12/70", "12/76", "12/89", "16/70", "20/70", "20/76", "28/70", ".410/76",
        ".36 Rundkugel (.375)", ".44 Rundkugel (.454)", ".45 Rundkugel (.440)", ".50 Rundkugel (.490)",
        ".54 Rundkugel (.530)", ".58 Minié", ".69 Minié", "4.5 mm Diabolo (.177)", "5.5 mm Diabolo (.22)",
        "4.4 mm Stahl-BB (.177 BB)", "6 mm Airsoft-BB", "8 mm Airsoft-BB")},
    ".450/400 Nitro Express 3 inch": "sources give 1899 for the 3 1/4 inch parent only",
    "6.5-300 Weatherby Magnum": "sources give only the 2017 SAAMI drawing",
}

# Shoulder angle of each bottleneck case: the angle between the shoulder and the case axis in
# degrees (the American convention, alpha/2), with the page it was read from. C.I.P. sheets
# print the full cone angle alpha, so their value is halved here; for those calibres `sh_at`
# is the sheet's L1 (where the body meets the shoulder). Bottleneck cases not listed are drawn
# with DEFAULT_SHOULDER_ANGLE until a source is found (SHOULDER_UNSOURCED in the tests).
_CIP = "https://bobp.cip-bobp.org/uploads/tdcc/"
SHOULDER_ANGLES = {
    ".17 HMR": (25, _CIP + "tab-v/tabvcal-en-page26.pdf"),  # C.I.P. 17 HMR
    ".17 Mach 2": (20, _CIP + "tab-v/tabvcal-en-page27.pdf"),  # C.I.P. 17 Mach 2
    "5 mm Remington Rimfire Magnum": (25, _CIP + "tab-v/tabvcal-en-page3.pdf"),  # C.I.P. 5 mm Rem. Mag.
    "7.65 mm Parabellum": (15.5, _CIP + "tab-iv/tabivcal-en-page14.pdf"),  # C.I.P. 7,65 Parabellum
    "7.62x25 mm Tokarev": (19, _CIP + "tab-iv/tabivcal-en-page9.pdf"),  # C.I.P. 7,62 x 25 Tokarev
    ".357 SIG": (18, _CIP + "tab-iv/tabivcal-en-page53.pdf"),  # C.I.P. 357 SIG
    ".22 Remington Jet": (6.7, _CIP + "tab-iv/tabivcal-en-page36.pdf"),  # C.I.P. 22 Rem. Jet Mag.
    "5.7x28 mm": (35, _CIP + "tab-i/tabical-en-page7.pdf"),  # C.I.P. 5,7 x 28
    "4.6x30 mm": (22.1, _CIP + "tab-iv/tabivcal-en-page1.pdf"),  # C.I.P. 4,6 x 30
    "7.63x25 mm Mauser": (17.4, _CIP + "tab-iv/tabivcal-en-page11.pdf"),  # C.I.P. 7,63 Mauser
    ".32-20 Winchester": (5.7, _CIP + "tab-ii/tabiical-en-page81.pdf"),  # C.I.P. 32-20 Win.
    "5.45x18 mm": (16.5, _CIP + "tab-iv/tabivcal-en-page2.pdf"),  # C.I.P. 5,45x18
    ".38-40 Winchester": (6.8, _CIP + "tab-ii/tabiical-en-page98.pdf"),  # C.I.P. 38-40 Win.
    ".221 Remington Fireball": (23, _CIP + "tab-iv/tabivcal-en-page37.pdf"),  # C.I.P. 221 Rem. Fireball
    ".204 Ruger": (30, _CIP + "tab-i/tabical-en-page79.pdf"),  # C.I.P. 204 Ruger
    ".222 Remington": (23, _CIP + "tab-i/tabical-en-page84.pdf"),  # C.I.P. 222 Rem.
    ".22-250 Remington": (28, _CIP + "tab-i/tabical-en-page82.pdf"),  # C.I.P. 22-250 Rem
    ".243 Winchester": (20, _CIP + "tab-i/tabical-en-page88.pdf"),  # C.I.P. 243 Win.
    "6 mm BR Norma": (30, _CIP + "tab-i/tabical-en-page12.pdf"),  # C.I.P. 6mm BR Norma
    "6 mm PPC": (30, _CIP + "tab-i/tabical-en-page14.pdf"),  # C.I.P. 6 mm PPC
    "6.5 mm Creedmoor": (30, "https://bobp.expert-it.com/uploads/tdcc/tab-i/6-5-creedmoor-fr.pdf"),  # C.I.P. 6,5 Creedmoor
    "6.5x55 mm Swedish": (25.3, _CIP + "tab-i/tabical-en-page23.pdf"),  # C.I.P. 6,5 x 55 SE.
    "6.5x47 mm Lapua": (30, _CIP + "tab-i/tabical-en-page19.pdf"),  # C.I.P. 6,5 x 47 Lapua
    ".260 Remington": (20, _CIP + "tab-i/tabical-en-page97.pdf"),  # C.I.P. 260 Rem.
    ".270 Winchester": (17.5, _CIP + "tab-i/tabical-en-page99.pdf"),  # C.I.P. 270 Win.
    "7 mm-08 Remington": (20, _CIP + "tab-i/tabical-en-page35.pdf"),  # C.I.P. 7 mm - 08 Rem.
    "7x57 mm Mauser": (20.5, _CIP + "tab-i/tabical-en-page33.pdf"),  # C.I.P. 7 x 57
    "7x64 mm": (20.2, _CIP + "tab-i/tabical-en-page34.pdf"),  # C.I.P. 7 x 64
    "7 mm Remington Magnum": (25, _CIP + "tab-iii/tabiiical-en-page3.pdf"),  # C.I.P. 7 mm Rem. Mag.
    "7.5x55 mm Swiss (GP 11)": (30.5, _CIP + "tab-i/tabical-en-page46.pdf"),  # C.I.P. 7,5 x 55 Suisse
    "7.5x54 mm French": (20, _CIP + "tab-i/tabical-en-page45.pdf"),  # C.I.P. 7,5 x 54 MAS
    "7.62x39 mm": (16.4, _CIP + "tab-i/tabical-en-page47.pdf"),  # C.I.P. 7,62 x 39
    ".308 Winchester": (20, _CIP + "tab-i/tabical-en-page125.pdf"),  # C.I.P. 308 Win.
    ".30-06 Springfield": (17.5, _CIP + "tab-i/tabical-en-page111.pdf"),  # C.I.P. 30-06 Spring
    ".30-30 Winchester": (15.7, _CIP + "tab-ii/tabiical-en-page70.pdf"),  # C.I.P. 30-30 Win.
    ".300 Winchester Magnum": (25, _CIP + "tab-iii/tabiiical-en-page20.pdf"),  # C.I.P. 300 Win. Mag.
    ".300 Norma Magnum": (20.5, "https://bobp.expert-it.com/uploads/tdcc/tab-i/300-norma-mag-fr.pdf"),  # C.I.P. 300 Norma Mag
    ".30 R Blaser": (20, _CIP + "tab-ii/tabiical-en-page66.pdf"),  # C.I.P. 30 R Blaser
    ".300 Lapua Magnum": (25, _CIP + "tab-i/tabical-en-page116.pdf"),  # C.I.P. 300 Lapua Mag.
    ".35 Winchester": (15.3, _CIP + "tab-ii/tabiical-en-page86.pdf"),  # C.I.P. 35 Win.
    ".303 British": (17, _CIP + "tab-ii/tabiical-en-page74.pdf"),  # C.I.P. 303 British
    "7.62x54 mm R": (18.5, _CIP + "tab-ii/tabiical-en-page29.pdf"),  # C.I.P. 7,62 x 54 R
    "8x57 mm IS": (19.1, _CIP + "tab-i/tabical-en-page57.pdf"),  # C.I.P. 8 x 57 IS
    "8x68 mm S": (14.5, _CIP + "tab-i/tabical-en-page63.pdf"),  # C.I.P. 8 x 68 S
    "9.3x62 mm": (17.5, _CIP + "tab-i/tabical-en-page69.pdf"),  # C.I.P. 9,3 x 62
    "9.3x74 mm R": (5.5, _CIP + "tab-ii/tabiical-en-page51.pdf"),  # C.I.P. 9,3 x 74 R
    ".338 Lapua Magnum": (20, _CIP + "tab-i/tabical-en-page132.pdf"),  # C.I.P. 338 Lapua Mag.
    ".375 H&H Magnum": (15, _CIP + "tab-iii/tabiiical-en-page27.pdf"),  # C.I.P. 375 H&H Mag.
    ".378 Weatherby Magnum": (43.9, _CIP + "tab-iii/tabiiical-en-page29.pdf"),  # C.I.P. 378 Weath. Mag.
    ".465 H&H Magnum": (5, _CIP + "tab-iii/tabiiical-en-page38.pdf"),  # C.I.P. 465 H&H Belt. Mag.
    ".475 No. 2 Nitro Express": (6.1, _CIP + "tab-ii/tabiical-en-page120.pdf"),  # C.I.P. 475 No 2 N.E. 3''1/2
    ".400/350 Nitro Express": (6.8, _CIP + "tab-ii/tabiical-en-page104.pdf"),  # C.I.P. 400/350 N.E.
    ".350 Rigby Magnum": (45, _CIP + "tab-i/tabical-en-page138.pdf"),  # C.I.P. 350 Mag. Rigby
    ".400 H&H Magnum": (8, _CIP + "tab-iii/tabiiical-en-page30.pdf"),  # C.I.P. 400 H&H Belt. Mag.
    ".244 H&H Magnum": (25, _CIP + "tab-iii/tabiiical-en-page11.pdf"),  # C.I.P. 244 H&H Mag.
    ".450 Rigby": (40, _CIP + "tab-i/tabical-en-page150.pdf"),  # C.I.P. 450 Rigby
    ".50 BMG": (15.7, _CIP + "tab-i/tabical-en-page152.pdf"),  # C.I.P. 50 Browning
    "6.5x52 mm Carcano": (24.3, _CIP + "tab-i/tabical-en-page20.pdf"),  # C.I.P. 6,5 x 52 Carcano
    "6.5x50 mm SR Arisaka": (18.5, _CIP + "tab-ii/tabiical-en-page13.pdf"),  # C.I.P. 6,5 x 51 R (Arisaka)
    "8x56 mm R Mannlicher": (7, _CIP + "tab-ii/tabiical-en-page31.pdf"),  # C.I.P. 8 x 56 R M30S
    "8x50 mm R Mannlicher": (14.5, _CIP + "tab-ii/tabiical-en-page30.pdf"),  # C.I.P. 8 x 50 R
    "6.5x54 mm Mannlicher-Schönauer": (23.6, _CIP + "tab-i/tabical-en-page22.pdf"),  # C.I.P. 6,5 x 54 Mannl. Sch.
    ".30-40 Krag": (21.1, _CIP + "tab-ii/tabiical-en-page71.pdf"),  # C.I.P. 30-40 Krag
    "7.92x33 mm Kurz": (17.5, _CIP + "tab-i/tabical-en-page53.pdf"),  # C.I.P. 7,92 x 33 kurz
    "5.45x39 mm": (20.3, _CIP + "tab-i/tabical-en-page2.pdf"),  # C.I.P. 5,45 x 39
    ".22 Hornet": (5.6, _CIP + "tab-ii/tabiical-en-page56.pdf"),  # C.I.P. 22 Hornet
    ".25-06 Remington": (17.5, _CIP + "tab-i/tabical-en-page92.pdf"),  # C.I.P. 25-06 Rem.
    ".257 Roberts": (20.8, _CIP + "tab-i/tabical-en-page96.pdf"),  # C.I.P. 257 Roberts
    ".280 Remington": (17.5, _CIP + "tab-i/tabical-en-page103.pdf"),  # C.I.P. 280 Rem.
    ".35 Whelen": (17.5, _CIP + "tab-i/tabical-en-page137.pdf"),  # C.I.P. 35 Whelen
    ".300 H&H Magnum": (8.5, _CIP + "tab-iii/tabiiical-en-page18.pdf"),  # C.I.P. 300 H&H Mag.
    ".338 Winchester Magnum": (25, _CIP + "tab-iii/tabiiical-en-page22.pdf"),  # C.I.P. 338 Win. Mag.
    "5.6x50 mm Magnum": (23, _CIP + "tab-i/tabical-en-page4.pdf"),  # C.I.P. 5,6 x 50 Mag.
    "6.5x57 mm Mauser": (18.9, _CIP + "tab-i/tabical-en-page24.pdf"),  # C.I.P. 6,5 x 57
    "6.5x68 mm": (14.7, _CIP + "tab-i/tabical-en-page30.pdf"),  # C.I.P. 6,5 x 68
    "8x64 mm S": (14, _CIP + "tab-i/tabical-en-page62.pdf"),  # C.I.P. 8 x 64 S
    "8x60 mm S": (19.1, _CIP + "tab-i/tabical-en-page60.pdf"),  # C.I.P. 8 x 60 S
    "9.5x57 mm Mannlicher-Schönauer": (21.1, _CIP + "tab-i/tabical-en-page72.pdf"),  # C.I.P. 9,5 x 57 Mannl. Sch.
    ".375 Ruger": (30, _CIP + "tab-i/tabical-en-page143.pdf"),  # C.I.P. 375 Ruger
    "6.8 mm Remington SPC": (23, _CIP + "tab-i/tabical-en-page31.pdf"),  # C.I.P. 6,8 mm Rem. SPC
    ".300 Winchester Short Magnum": (35, _CIP + "tab-i/tabical-en-page122.pdf"),  # C.I.P. 300 Win. Short Mag.
    ".17 Remington": (23, _CIP + "tab-i/tabical-en-page77.pdf"),  # C.I.P. 17 Rem.
    ".218 Bee": (15, _CIP + "tab-ii/tabiical-en-page54.pdf"),  # C.I.P. 218 Bee
    ".35 Remington": (23.4, _CIP + "tab-i/tabical-en-page136.pdf"),  # C.I.P. 35 Rem.
    ".348 Winchester": (19.1, _CIP + "tab-ii/tabiical-en-page85.pdf"),  # C.I.P. 348 Win.
    ".358 Winchester": (20, _CIP + "tab-i/tabical-en-page139.pdf"),  # C.I.P. 358 Win.
    ".300 Weatherby Magnum": (41.3, _CIP + "tab-iii/tabiiical-en-page19.pdf"),  # C.I.P. 300 Weath. Mag.
    ".416 Remington Magnum": (25, _CIP + "tab-iii/tabiiical-en-page31.pdf"),  # C.I.P. 416 Rem. Mag.
    ".470 Nitro Express": (7.2, _CIP + "tab-ii/tabiical-en-page119.pdf"),  # C.I.P. 470 N.E.
    ".450 No. 2 Nitro Express": (9.7, _CIP + "tab-ii/tabiical-en-page116.pdf"),  # C.I.P. 450 No.2 N.E. 3''1/2 Eley
    ".500/416 Nitro Express": (14.8, _CIP + "tab-ii/tabiical-en-page124.pdf"),  # C.I.P. 500/416 N.E. 3"1/4
    ".375 Flanged Magnum Nitro Express": (12.6, _CIP + "tab-ii/tabiical-en-page94.pdf"),  # C.I.P. 375 Fl. Mag. N.E.
    "9.3x53 mm R Finnish": (19.5, _CIP + "tab-ii/tabiical-en-page49.pdf"),  # C.I.P. 9,3 x 53 R Finnish
    "10.3x60 mm R": (5.2, _CIP + "tab-ii/tabiical-en-page52.pdf"),  # C.I.P. 10,3 x 60 R
    "7x61 mm Sharpe & Hart": (42.9, _CIP + "tab-iii/tabiiical-en-page2.pdf"),  # C.I.P. 7 x 61 Super
    ".500/465 Nitro Express": (2.8, _CIP + "tab-ii/tabiical-en-page125.pdf"),  # C.I.P. 500/465 N.E.
    ".318 Westley Richards": (25, _CIP + "tab-i/tabical-en-page126.pdf"),  # C.I.P. 318 Riml. N.E.
    ".240 Weatherby Magnum": (44.5, _CIP + "tab-iii/tabiiical-en-page10.pdf"),  # C.I.P. 240 Weath. Mag.
    ".224 Weatherby Magnum": (41.7, _CIP + "tab-iii/tabiiical-en-page8.pdf"),  # C.I.P. 224 Weath. Mag.
    "6.5 mm Remington Magnum": (25, _CIP + "tab-iii/tabiiical-en-page1.pdf"),  # C.I.P. 6,5 mm Rem. Mag.
    ".220 Swift": (21, _CIP + "tab-i/tabical-en-page83.pdf"),  # C.I.P. 220 Swift
    ".25-20 Winchester": (16.6, _CIP + "tab-ii/tabiical-en-page60.pdf"),  # C.I.P. 25-20 Win.
    ".250 Savage": (26.5, _CIP + "tab-i/tabical-en-page93.pdf"),  # C.I.P. 250 Savage
    ".257 Weatherby Magnum": (50.9, _CIP + "tab-iii/tabiiical-en-page12.pdf"),  # C.I.P. 257 Weath. Mag.
    ".270 Weatherby Magnum": (48.1, _CIP + "tab-iii/tabiiical-en-page14.pdf"),  # C.I.P. 270 Weath. Mag.
    "7 mm Weatherby Magnum": (47.1, _CIP + "tab-iii/tabiiical-en-page5.pdf"),  # C.I.P. 7 mm Weath. Mag.
    ".340 Weatherby Magnum": (37.1, _CIP + "tab-iii/tabiiical-en-page24.pdf"),  # C.I.P. 340 Weath. Mag.
    ".284 Winchester": (35, _CIP + "tab-i/tabical-en-page105.pdf"),  # C.I.P. 284 Win.
    ".300 Savage": (30, _CIP + "tab-i/tabical-en-page120.pdf"),  # C.I.P. 300 Savage
    ".33 Winchester": (16.2, _CIP + "tab-ii/tabiical-en-page83.pdf"),  # C.I.P. 33 Win.
    ".25 Remington": (23, _CIP + "tab-i/tabical-en-page90.pdf"),  # C.I.P. 25 Rem.
    ".32 Remington": (23, _CIP + "tab-i/tabical-en-page127.pdf"),  # C.I.P. 32 Rem.
    "8x75 mm RS": (13, _CIP + "tab-ii/tabiical-en-page42.pdf"),  # C.I.P. 8 x 75 RS
    "6.5x65 mm RWS": (20, _CIP + "tab-i/tabical-en-page29.pdf"),  # C.I.P. 6,5 x 65 RWS
    "9.3x66 mm Sako (.370 Sako Magnum)": (17.5, _CIP + "tab-i/tabical-en-page71.pdf"),  # C.I.P. 9,3 x 66 Sako
    ".300 Blaser Magnum": (30, _CIP + "tab-i/tabical-en-page114.pdf"),  # C.I.P. 300 Blaser Mag.
    ".375 Blaser Magnum": (30, _CIP + "tab-i/tabical-en-page140.pdf"),  # C.I.P. 375 Blaser Mag.
    "7 mm Blaser Magnum": (30, _CIP + "tab-i/tabical-en-page36.pdf"),  # C.I.P. 7 mm Blaser Mag.
    ".338 Blaser Magnum": (30, _CIP + "tab-i/tabical-en-page130.pdf"),  # C.I.P. 338 Blaser Mag.
    ".450/400 Nitro Express 3 inch": (15, _CIP + "tab-ii/tabiical-en-page117.pdf"),  # C.I.P. 450/400 N.E. 3''
    ".40-82 WCF": (4.5, _CIP + "tab-ii/tabiical-en-page102.pdf"),  # C.I.P. 40-82 Win.
    ".50-95 WCF": (6.4, _CIP + "tab-ii/tabiical-en-page122.pdf"),  # C.I.P. 50-95 Win.
    ".30 Remington": (23, _CIP + "tab-i/tabical-en-page108.pdf"),  # C.I.P. 30 Rem.
    ".17 Remington Fireball": (30, _CIP + "tab-i/tabical-en-page78.pdf"),  # C.I.P. 17 Rem. Fireball
    ".338 Marlin Express": (25, _CIP + "tab-ii/tabiical-en-page84.pdf"),  # C.I.P. 338 Marlin Express
    ".303 Savage": (16, _CIP + "tab-ii/tabiical-en-page75.pdf"),  # C.I.P. 303 Savage
    ".219 Zipper": (12, _CIP + "tab-ii/tabiical-en-page55.pdf"),  # C.I.P. 219 Zipper
    ".300 Remington Ultra Magnum": (30, _CIP + "tab-i/tabical-en-page119.pdf"),  # C.I.P. 300 Rem. Ultra Mag.
    ".270 Winchester Short Magnum": (35, _CIP + "tab-i/tabical-en-page100.pdf"),  # C.I.P. 270 Win. Short Mag.
    "7 mm Winchester Short Magnum": (35, _CIP + "tab-i/tabical-en-page43.pdf"),  # C.I.P. 7 mm Win. Short Mag.
    ".338 Federal": (20, _CIP + "tab-i/tabical-en-page131.pdf"),  # C.I.P. 338 Federal
    "8 mm Remington Magnum": (25, _CIP + "tab-iii/tabiiical-en-page6.pdf"),  # C.I.P. 8 mm Rem. Mag.
    ".376 Steyr": (17.5, _CIP + "tab-i/tabical-en-page144.pdf"),  # C.I.P. 376 Steyr
    "6 mm Remington": (26, _CIP + "tab-i/tabical-en-page16.pdf"),  # C.I.P. 6 mm Rem. (244 Rem.)
    "7-30 Waters": (17.2, _CIP + "tab-ii/tabiical-en-page20.pdf"),  # C.I.P. 7-30 Waters
    "7x65 mm R": (20.3, _CIP + "tab-ii/tabiical-en-page24.pdf"),  # C.I.P. 7 x 65 R
    ".22 Savage Hi-Power": (14, _CIP + "tab-ii/tabiical-en-page57.pdf"),  # C.I.P. 22 Savage
    "8x57 mm IRS": (18.2, _CIP + "tab-ii/tabiical-en-page35.pdf"),  # C.I.P. 8 x 57 IRS
    ".356 Winchester": (20, _CIP + "tab-ii/tabiical-en-page90.pdf"),  # C.I.P. 356 Win.
    ".307 Winchester": (20, _CIP + "tab-ii/tabiical-en-page77.pdf"),  # C.I.P. 307 Win.
    ".416 Ruger": (30, _CIP + "tab-i/tabical-en-page147.pdf"),  # C.I.P. 416 Ruger
    ".416 Weatherby Magnum": (36.8, _CIP + "tab-iii/tabiiical-en-page33.pdf"),  # C.I.P. 416 Weath. Mag.
    ".375 Remington Ultra Magnum": (30, _CIP + "tab-i/tabical-en-page142.pdf"),  # C.I.P. 375 Rem. Ultra Mag.
    "7 mm STW": (25, _CIP + "tab-iii/tabiiical-en-page4.pdf"),  # C.I.P. 7 mm STW
    ".225 Winchester": (25, _CIP + "tab-ii/tabiical-en-page58.pdf"),  # C.I.P. 225 Win.
    ".223 WSSM": (28, _CIP + "tab-i/tabical-en-page87.pdf"),  # C.I.P. 223 Win. Super Short Mag.
    ".243 WSSM": (28, _CIP + "tab-i/tabical-en-page89.pdf"),  # C.I.P. 243 Win. Super Short Mag.
    ".25 WSSM": (30, _CIP + "tab-i/tabical-en-page91.pdf"),  # C.I.P. 25 Win. SSM
    ".350 Remington Magnum": (25, _CIP + "tab-iii/tabiiical-en-page25.pdf"),  # C.I.P. 350 Rem. Mag.
    ".338-378 Weatherby Magnum": (48.5, _CIP + "tab-iii/tabiiical-en-page23.pdf"),  # C.I.P. 338-378 Weath. Mag.
    "7 mm Remington SAUM": (30, _CIP + "tab-i/tabical-en-page40.pdf"),  # C.I.P. 7 mm Rem. SA Ultra Mag.
    ".30 Thompson/Center": (30, _CIP + "tab-i/tabical-en-page109.pdf"),  # C.I.P. 30 TC
    ".308 Marlin Express": (20, _CIP + "tab-i/tabical-en-page124.pdf"),  # C.I.P. 308 Marlin Express
    ".300 Remington SAUM": (30, _CIP + "tab-i/tabical-en-page118.pdf"),  # C.I.P. 300 Rem. SA Ultra Mag.
    "6.5-284 Norma": (35.1, _CIP + "tab-i/tabical-en-page18.pdf"),  # C.I.P. 6,5 - 284 Norma
    ".30-378 Weatherby Magnum": (53, _CIP + "tab-iii/tabiiical-en-page17.pdf"),  # C.I.P. 30-378 Weath. Mag.
    "5.6x57 mm": (17.4, _CIP + "tab-i/tabical-en-page5.pdf"),  # C.I.P. 5,6 x 57
    "7.62x45 mm vz. 52": (24.9, _CIP + "tab-i/tabical-en-page48.pdf"),  # C.I.P. 7,62 x 45
    "7.65x53 mm Argentine": (22.2, _CIP + "tab-i/tabical-en-page50.pdf"),  # C.I.P. 7,65 x 53 Arg.
    ".338 Norma Magnum": (20.5, _CIP + "tab-i/tabical-en-page133.pdf"),  # C.I.P. 338 Norma Mag.
    ".358 Norma Magnum": (25.5, _CIP + "tab-iii/tabiiical-en-page26.pdf"),  # C.I.P. 358 Norma Mag.
    "9.3x64 mm Brenneke": (17.5, _CIP + "tab-i/tabical-en-page70.pdf"),  # C.I.P. 9,3 x 64 Brenneke
    "9.3x57 mm Mauser": (17.5, _CIP + "tab-i/tabical-en-page68.pdf"),  # C.I.P. 9,3 x 57
    "9x57 mm Mauser": (19.1, _CIP + "tab-i/tabical-en-page67.pdf"),  # C.I.P. 9 x 57
    "7x57 mm R": (20.5, _CIP + "tab-ii/tabiical-en-page22.pdf"),  # C.I.P. 7 x 57 R
    "6.5x57 mm R": (18.9, _CIP + "tab-ii/tabiical-en-page15.pdf"),  # C.I.P. 6,5 x 57 R
    ".338 Remington Ultra Magnum": (30, _CIP + "tab-i/tabical-en-page134.pdf"),  # C.I.P. 338 Rem. Ultra Mag.
    "7 mm Remington Ultra Magnum": (30, _CIP + "tab-i/tabical-en-page41.pdf"),  # C.I.P. 7 mm Rem. Ultra Mag.
    ".325 Winchester Short Magnum": (35, _CIP + "tab-i/tabical-en-page128.pdf"),  # C.I.P. 325 WSM
    ".375 Weatherby Magnum": (30.9, _CIP + "tab-iii/tabiiical-en-page28.pdf"),  # C.I.P. 375 Weath. Mag.
    ".460 Weatherby Magnum": (28.1, _CIP + "tab-iii/tabiiical-en-page37.pdf"),  # C.I.P. 460 Weath. Mag.
    ".505 Gibbs": (37.6, _CIP + "tab-i/tabical-en-page154.pdf"),  # C.I.P. 505 Mag. Gibbs
    ".500 Jeffery": (12.6, _CIP + "tab-i/tabical-en-page153.pdf"),  # C.I.P. 500 Jeffery
    ".577/450 Martini-Henry": (15.8, _CIP + "tab-ii/tabiical-en-page127.pdf"),  # C.I.P. 577/450 Sld. Mart. H.
    ".44-40 WCF": (4, _CIP + "tab-ii/tabiical-en-page108.pdf"),  # C.I.P. 44-40 Win.
    ".45-75 Winchester": (5.9, _CIP + "tab-ii/tabiical-en-page113.pdf"),  # C.I.P. 45-75 Win.
    ".223 Remington": (23, _WP + ".223_Remington"),  # C.I.P. drawing in the article
    "5.56x45 mm NATO": (23, _WP + ".223_Remington"),  # same case as .223 Rem
    "5.6 mm GP 90": (23, _WP + ".223_Remington"),  # same case as .223 Rem
    "7.62x51 mm NATO": (20, _WP + "7.62%C3%9751mm_NATO"),
    ".408 CheyTac": (22.1, _WP + ".408_Cheyenne_Tactical"),
    "6 mm ARC": (30, "https://bulletin.accurateshooter.com/?p=69700"),  # 30-degree shoulder
    ".28 Nosler": (35, _WP + "Nosler_cartridges"),
    ".280 Ackley Improved": (40, _WP + ".280_Ackley_Improved"),
    ".25 Creedmoor": (35, "https://saami.org/wp-content/uploads/2025/01/Public-Introduction-25-Creedmoor-2025-01-27.pdf"),  # SAAMI drawing
    "8x58 mm R Danish Krag": (16.5, _WP + "8%C3%9758mmR_Danish_Krag"),
    "12.7x108 mm": (18.2, _WP + "12.7%C3%97108mm"),
    "6.5x53 mm R Mannlicher": (25, _WP + "6.5%C3%9753mmR"),
    "7.5 FK": (30, _WP + "7.5_FK"),
    ".30 Remington AR": (25, _WP + ".30_Remington_AR"),
    ".300 AAC Blackout": (23, _CIP + "tab-i/300-aac-blackout-180801-en.pdf"),  # C.I.P. 300 AAC Blackout
    "6 mm Creedmoor": (30, "https://chuckhawks.com/6mm_Creedmoor.html"),
    "6.5 mm Grendel": (30, "https://www.rifleshootermag.com/editorial/6-5-grendel-evolution/84008"),
    "6.5 PRC": (30, "https://bulletin.accurateshooter.com/?p=61574"),
    "7 mm PRC": (30, "https://www.all4shooters.com/en/hunting/ammunition/new-hornady-7mm-prc-cartridge-test-report-background-development-data/"),
    ".300 PRC": (30, "https://www.americanrifleman.org/content/tested-hornady-s-300-prc/"),
    ".222 Remington Magnum": (23, _CIP + "tab-i/tabical-en-page85.pdf"),  # C.I.P. 222 Rem. Mag.
    ".264 Winchester Magnum": (25, _CIP + "tab-iii/tabiiical-en-page13.pdf"),  # C.I.P. 264 Win. Mag.
    ".416 Rigby": (44.9, _CIP + "tab-i/tabical-en-page146.pdf"),  # C.I.P. 416 Rigby
    "11x60 mm R Mauser": (8.95, _CIP + "tab-ii/tabiical-en-page53.pdf"),  # C.I.P. 11,15 x 60 R
    ".32 Winchester Special": (14.5, _CIP + "tab-ii/tabiical-en-page80.pdf"),  # C.I.P. 32 Win. Spec.
    ".22 Nosler": (29.9, "https://municion.org/producto/22-nosler/"),  # AECC drawing 06-045-BRC-050
    ".25 NAA": (29, "https://municion.org/producto/25-naa/"),  # AECC drawing 06-019-BGC-070
    ".22 TCM": (18.8, "https://municion.org/producto/22-tuason-craig-micromagnum/"),  # AECC drawing 06-026-BGC-010
    "9x39 mm": (14.8, "https://municion.org/producto/9-x-39-russian/"),  # AECC drawing 09-039-BGC-010
    ".375 CheyTac": (20, "https://municion.org/producto/375-cheyenne-tactical/"),  # AECC drawing 10-077-BGC-030
    "9x25 mm Dillon": (27.5, "https://municion.org/producto/9-x-25-dillon/"),  # AECC drawing 09-025-BGC-020
    ".17 Winchester Super Magnum": (16.1, "https://municion.org/producto/17-winchester-super-magnum-rf/"),  # AECC drawing 04-029-BBR-010
    ".224 Valkyrie": (29.5, "https://municion.org/producto/224-valkyrie/"),  # AECC drawing 06-042-BGC-090
    "6.5x58 mm Vergueiro": (10.8, "https://municion.org/producto/65-x-58-mauser-vergueiro-m-1904/"),  # AECC drawing 07-058-BGC-030
    ".32 NAA": (18.8, "https://municion.org/producto/32-naa/"),  # AECC drawing 08-017-BGC-040
    ".416 Barrett": (24.7, "https://municion.org/producto/416-barrett-sniper/"),  # AECC drawing 11-083-BGC-010
    ".25-35 Winchester": (11.1, "https://municion.org/producto/25-35-winchester-cf/"),  # AECC drawing 06-052-BBC-050
    ".300 HAM'R": (27.5, "https://municion.org/producto/300-hamr/"),  # AECC drawing 08-041-BGC-001
    ".400 Cor-Bon": (15.4, "https://municion.org/producto/400-cor-bon/"),  # AECC drawing 10-023-BGC-050
    ".26 Nosler": (38.7, "https://municion.org/producto/26-nosler/"),  # AECC drawing 07-066-BRC-040
    ".33 Nosler": (31.9, "https://municion.org/producto/33-nosler/"),  # AECC drawing 09-062-BRC-010
    ".256 Winchester Magnum": (22.3, "https://municion.org/producto/256-winchester-magnum/"),  # AECC drawing 06-033-BBC-040
    "7.92x107 mm DS": (31.2, "https://municion.org/producto/792-x-107-polish-anti-tank-maroszek-ur-wz-35/"),  # AECC drawing 08-107-BGC-020
    ".300 Ruger Compact Magnum": (38, "https://municion.org/producto/300-ruger-compact-magnum/"),  # AECC drawing 08-053-BGC-110
    ".38-56 WCF": (6.5, "https://municion.org/producto/38-56-winchester-cf-marlincolt/"),  # AECC drawing 09-053-BBC-050
    ".338 Ruger Compact Magnum": (27.7, "https://municion.org/producto/338-ruger-compact-magnum/"),  # AECC drawing 09-051-BGC-050
    ".458 SOCOM": (35.2, "https://municion.org/producto/458-socom/"),  # AECC drawing
    "10.4x38 mm R Vetterli": (10.2, "https://municion.org/producto/104-x-38-r-swiss-vetterli-cf-m-1869-81/"),  # AECC drawing 11-038-BBC-011
    ".404 Jeffery": (8.5, _CIP + "tab-i/tabical-en-page145.pdf"),  # C.I.P. 404 Riml. N.E.
    "8.5x55 mm Blaser": (30, "https://cuzzs.gov.cz/userfiles/documents/CIP/02092021/Mimoradny_Vestnik_%202021_DEF.pdf"),  # C.I.P. sheet p7: atan((P2-H2)/2/(L2-L1))
    "11x59 mm R Gras": (8.7, "https://municion.org/producto/11-x-59-r-french-gras-m-1874-79-83/"),  # AECC drawing 11-059-BBC-010
    "7.35x51 mm Carcano": (22.2, "https://municion.org/producto/735-x-51-italian-carcano-m-1938/"),  # AECC drawing 08-051-BGC-010
    "7.7x58 mm Arisaka": (16.1, "https://municion.org/producto/77-x-58-japanese-rimless-arisaka-type-99/"),  # AECC drawing 08-058-BGC-020
    "8 mm Nambu": (15.5, "https://municion.org/producto/8-mm-nambu-m-1914/"),  # AECC drawing 08-022-BGC-040
    ".55 Boys": (10, "https://municion.org/producto/55-boys/"),  # AECC drawing 14-099-BFC-020
    ".308 Norma Magnum": (24.8, "https://municion.org/producto/308-norma-magnum-belted/"),  # AECC drawing 08-065-BFC-010
    "7.5x53.5 mm Swiss (GP 1890)": (27.8, "https://municion.org/producto/75-x-535-swiss-schmidt-rubin-m-1890-1903/"),  # AECC drawing 08-054-BGC-040
    "7.5 mm Kadettenpatrone": (27.8, "https://municion.org/producto/75-x-535-swiss-schmidt-rubin-m-1890-1903/"),  # assumed like the GP 1890 case
    "8x50 mm R Lebel": (17.9, "https://municion.org/producto/8-x-50-r-french-lebel-m-1886-1888-1932/"),  # AECC drawing 08-050-BBC-060
    ".17 Hornet": (21, "https://municion.org/producto/17-hornet/"),  # AECC drawing 04-035-BBC-57W
    "7 mm Backcountry": (30, "https://saami.org/wp-content/uploads/2025/01/Public-Introduction-7mm-Backcountry-2025-01-27.pdf"),  # SAAMI drawing
    "8.6 Blackout": (30, "https://saami.org/wp-content/uploads/2026/04/Public-Introduction-8.6-BLACKOUT-2026-04-07.pdf"),  # SAAMI drawing
    ".338 ARC": (30, "https://saami.org/wp-content/uploads/2025/03/Public-Introduction-338-ARC-2025-01-27.pdf"),  # SAAMI drawing
    ".22 Creedmoor": (30, "https://saami.org/wp-content/uploads/2026/10/Public-Revision-Notice-22-Creedmoor-2026-10-26.pdf"),  # SAAMI drawing
    ".25 Weatherby RPM": (35, "https://saami.org/wp-content/uploads/2026/01/Public-Introduction-25-Weatherby-RPM-2026-01-19.pdf"),  # SAAMI drawing
    "6.5-300 Weatherby Magnum": (46.4, "https://jagdfibel.de/images/0/0e/65300.pdf"),  # SAAMI drawing (double radius; chord through the .4920 datum and neck start)
    ".277 SIG Fury": (30, "https://www.xxlreloading.com/"),  # SAAMI 277 Fury drawing shown with xxlreloading.com load data: 30 deg, shoulder .4611 in at 1.6311 in, neck .310 in at 1.7619 in
    "5.8x42 mm": (24.5, "https://www.small-arms.org/"),  # small-arms.org (QBQ club) 5.8x42 dimension drawing: 49 deg full cone angle, shoulder at 34 mm, neck at 37.2 mm
    "6.8 Western": (35, "https://web.archive.org/web/2022/https://saami.org/wp-content/uploads/2020/11/6.8-Western-Public-Introduction-Orig-2020-11-01.pdf"),  # SAAMI drawing
    "6.5 Weatherby RPM": (35, "https://web.archive.org/web/2022/https://saami.org/wp-content/uploads/2020/10/6.5-WBY-RPM-Public-Introduction-Orig-2020-09-27.pdf"),  # SAAMI drawing
    ".338 Weatherby RPM": (35, "https://www.thefirearmblog.com/"),  # SAAMI 338 WBY RPM drawing (issued 2022-01-16) shown by The Firearm Blog: 35 deg, shoulder .4739 in at 2.1595 in, neck .364 in at 2.2380 in
    ".22 ARC": (30, "https://www.outdoorlife.com/guns/22-arc-review/"),  # SAAMI 22 ARC drawing (issued 2024-01-21) shown by Outdoor Life: 30 deg, shoulder .4297 in at 1.1510 in, neck .253 in at 1.3040 in
    "6 mm GT": (35, "https://www.4dreamerrentals.com/"),  # 4D Reamer Rentals 6mm GT drawing: 35 deg, shoulder at 1.3040 in, neck at 1.4375 in (GA Precision brass photo reads 35-36)
    ".30 Nosler": (35, "https://www.nosler.com/"),  # Nosler's "30 Nosler Rifle Cartridges" drawing: 35 deg, shoulder .528 in at 2.115 in, neck .344 in at 2.246 in, case 2.556 in
    ".27 Nosler": (35, "https://www.nosler.com/"),  # Nosler's "27 Nosler Rifle Cartridge" drawing: 35 deg, shoulder at 2.109 in, neck at 2.262 in
}
DEFAULT_SHOULDER_ANGLE = 32


def shoulder_angle(name):
    """Half cone angle of the shoulder in degrees (sourced, or the default)."""
    entry = SHOULDER_ANGLES.get(name)
    return entry[0] if entry else DEFAULT_SHOULDER_ANGLE


# Case heads of rimless and belted cases, from the C.I.P. sheets (maximum cartridge):
# name: (R, E, E1, delta, url). R = rim thickness; E = head to the top of the extractor-groove ramp
# (belted: head to the front of the belt); E1 = groove diameter; delta = angle of the groove's
# front ramp to the case axis, in degrees. A case made from a parent case without its own sheet
# keeps the parent's head (the note says which). Cases not listed keep a generic head.
CASE_HEADS = {
    "7.65 mm Parabellum": (1.22, 3.69, 8.79, 20.0, _CIP + "tab-iv/tabivcal-en-page14.pdf"),  # C.I.P. 7,65 Parabellum
    "7.62x25 mm Tokarev": (1.32, 3.34, 8.65, 30.0, _CIP + "tab-iv/tabivcal-en-page9.pdf"),  # C.I.P. 7,62 x 25 Tokarev
    ".357 SIG": (1.4, 3.59, 8.81, 43.0, _CIP + "tab-iv/tabivcal-en-page53.pdf"),  # C.I.P. 357 SIG
    "5.7x28 mm": (1.14, 3.38, 6.6, 25.0, _CIP + "tab-i/tabical-en-page7.pdf"),  # C.I.P. 5,7 x 28
    "4.6x30 mm": (1.1, 2.87, 6.8, 31.0, _CIP + "tab-iv/tabivcal-en-page1.pdf"),  # C.I.P. 4,6 x 30
    "7.63x25 mm Mauser": (1.27, 3.72, 8.73, 20.0, _CIP + "tab-iv/tabivcal-en-page11.pdf"),  # C.I.P. 7,63 Mauser
    "5.45x18 mm": (1.13, 2.9, 6.58, 16.7, _CIP + "tab-iv/tabivcal-en-page2.pdf"),  # C.I.P. 5,45x18
    ".221 Remington Fireball": (1.14, 3.13, 8.43, 25.0, _CIP + "tab-iv/tabivcal-en-page37.pdf"),  # C.I.P. 221 Rem. Fireball
    ".204 Ruger": (1.14, 3.11, 8.43, 25.0, _CIP + "tab-i/tabical-en-page79.pdf"),  # C.I.P. 204 Ruger
    ".222 Remington": (1.14, 3.01, 8.43, 25.0, _CIP + "tab-i/tabical-en-page84.pdf"),  # C.I.P. 221 Rem. Fireball?
    ".22-250 Remington": (1.24, 3.22, 10.39, 34.0, _CIP + "tab-i/tabical-en-page82.pdf"),  # C.I.P. 22-250 Rem
    ".243 Winchester": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page88.pdf"),  # C.I.P. 243 Win.
    "6 mm BR Norma": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page12.pdf"),  # C.I.P. 6mm BR Norma
    "6 mm PPC": (1.5, 3.5, 9.6, 43.7, _CIP + "tab-i/tabical-en-page14.pdf"),  # C.I.P. 6 mm PPC
    "6.5x55 mm Swedish": (1.5, 3.25, 10.5, 45.0, _CIP + "tab-i/tabical-en-page23.pdf"),  # C.I.P. 6,5 x 55 SE
    "6.5x47 mm Lapua": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page19.pdf"),  # C.I.P. 6,5 x 47 Lapua
    ".260 Remington": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page97.pdf"),  # C.I.P. 260 Rem.
    ".270 Winchester": (1.24, 3.16, 10.39, 36.0, _CIP + "tab-i/tabical-en-page99.pdf"),  # C.I.P. 270 Win.
    "7 mm-08 Remington": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page35.pdf"),  # C.I.P. 7 mm - 08 Rem.
    "7x57 mm Mauser": (1.15, 3.04, 10.7, 32.0, _CIP + "tab-i/tabical-en-page33.pdf"),  # C.I.P. 7 x 57
    "7x64 mm": (1.3, 3.2, 10.5, 36.9, _CIP + "tab-i/tabical-en-page34.pdf"),  # C.I.P. 7 x 64
    "7 mm Remington Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page3.pdf"),  # C.I.P. 7 mm Rem. Mag.
    "7.5x55 mm Swiss (GP 11)": (1.65, 3.46, 10.3, 51.8, _CIP + "tab-i/tabical-en-page46.pdf"),  # C.I.P. 7,5 x 55 Suisse
    "7.5x54 mm French": (1.4, 3.2, 10.5, 41.2, _CIP + "tab-i/tabical-en-page45.pdf"),  # C.I.P. 7,5 x 54 MAS
    "7.62x39 mm": (1.5, 3.2, 9.56, 52.0, _CIP + "tab-i/tabical-en-page47.pdf"),  # C.I.P. 7,62 x 39
    ".308 Winchester": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page125.pdf"),  # C.I.P. 308 Win.
    ".30-06 Springfield": (1.24, 3.16, 10.39, 36.0, _CIP + "tab-i/tabical-en-page111.pdf"),  # C.I.P. 30-06 Spring.
    ".300 Winchester Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page20.pdf"),  # C.I.P. 300 Win. Mag.
    ".300 Lapua Magnum": (1.52, 3.12, 13.24, 50.0, _CIP + "tab-i/tabical-en-page116.pdf"),  # C.I.P. 300 Lapua Mag.
    "8x57 mm IS": (1.3, 3.19, 10.5, 36.0, _CIP + "tab-i/tabical-en-page57.pdf"),  # C.I.P. 8 x 57 IS
    "8x68 mm S": (1.4, 3.5, 11.2, 43.7, _CIP + "tab-i/tabical-en-page63.pdf"),  # C.I.P. 8 x 68 S
    "9.3x62 mm": (1.3, 3.2, 10.5, 41.6, _CIP + "tab-i/tabical-en-page69.pdf"),  # C.I.P. 9,3 x 62
    ".338 Lapua Magnum": (1.52, 3.12, 13.24, 50.1, _CIP + "tab-i/tabical-en-page132.pdf"),  # C.I.P. 338 Lapua Mag.
    ".375 H&H Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page27.pdf"),  # C.I.P. 375 H&H Mag.
    ".378 Weatherby Magnum": (1.6, 6.4, 12.57, 45.0, _CIP + "tab-iii/tabiiical-en-page29.pdf"),  # C.I.P. ?
    ".465 H&H Magnum": (1.6, 6.4, 12.57, 45.0, _CIP + "tab-iii/tabiiical-en-page38.pdf"),  # C.I.P. ?
    ".350 Rigby Magnum": (1.52, 3.81, 11.61, 26.9, _CIP + "tab-i/tabical-en-page138.pdf"),  # C.I.P. 350 Mag. Rigby
    ".400 H&H Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page30.pdf"),  # C.I.P. 400 H&H Belt. Mag.
    ".244 H&H Magnum": (1.27, 5.56, 11.94, 45.0, _CIP + "tab-iii/tabiiical-en-page11.pdf"),  # C.I.P. 244 H&H Mag.
    ".450 Rigby": (1.65, 3.81, 12.7, 39.9, _CIP + "tab-i/tabical-en-page150.pdf"),  # C.I.P. 450 Rigby
    ".50 BMG": (2.26, 6.23, 17.27, 36.0, _CIP + "tab-i/tabical-en-page152.pdf"),  # C.I.P. 50 Browning
    "6.5x52 mm Carcano": (1.3, 3.2, 9.95, 74.7, _CIP + "tab-i/tabical-en-page20.pdf"),  # C.I.P. 6,5 x 52 Carcano
    "6.5x54 mm Mannlicher-Schönauer": (1.05, 3.4, 9.7, 33.2, _CIP + "tab-i/tabical-en-page22.pdf"),  # C.I.P. 6,5 x 54 Mannl. Sch.
    "7.92x33 mm Kurz": (1.3, 3.5, 10.5, 31.0, _CIP + "tab-i/tabical-en-page53.pdf"),  # C.I.P. 7,92 x 33 kurz
    "5.45x39 mm": (1.5, 3.2, 8.6, 45.0, _CIP + "tab-i/tabical-en-page2.pdf"),  # C.I.P. 5,45 x 39
    ".25-06 Remington": (1.24, 3.16, 10.39, 36.0, _CIP + "tab-i/tabical-en-page92.pdf"),  # C.I.P. 25-06 Rem.?
    ".257 Roberts": (1.24, 3.2, 10.39, 36.0, _CIP + "tab-i/tabical-en-page96.pdf"),  # C.I.P. 257 Roberts
    ".280 Remington": (1.24, 3.17, 10.39, 36.0, _CIP + "tab-i/tabical-en-page103.pdf"),  # C.I.P. 280 Rem.
    ".35 Whelen": (1.24, 3.16, 10.39, 36.0, _CIP + "tab-i/tabical-en-page137.pdf"),  # C.I.P. 35 Whelen
    ".300 H&H Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page18.pdf"),  # C.I.P. 300 H&H Mag.
    ".338 Winchester Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page22.pdf"),  # C.I.P. 338 Win. Mag.
    "5.6x50 mm Magnum": (1.14, 3.1, 8.44, 25.8, _CIP + "tab-i/tabical-en-page4.pdf"),  # C.I.P. 5,6 x 50 Mag.
    "6.5x57 mm Mauser": (1.3, 3.2, 10.5, 37.9, _CIP + "tab-i/tabical-en-page24.pdf"),  # C.I.P. 6,5 x 57
    "6.5x68 mm": (1.4, 3.5, 11.2, 43.7, _CIP + "tab-i/tabical-en-page30.pdf"),  # C.I.P. 6,5 x 68
    "8x64 mm S": (1.3, 3.2, 10.6, 36.8, _CIP + "tab-i/tabical-en-page62.pdf"),  # C.I.P. 8 x 64 S
    "8x60 mm S": (1.3, 3.2, 10.5, 39.4, _CIP + "tab-i/tabical-en-page60.pdf"),  # C.I.P. 8 x 60 S
    "9.5x57 mm Mannlicher-Schönauer": (1.2, 3.2, 10.3, 38.7, _CIP + "tab-i/tabical-en-page72.pdf"),  # C.I.P. 9,5 x 57 Mannl. Sch.
    ".375 Ruger": (1.27, 3.24, 12.07, 35.0, _CIP + "tab-i/tabical-en-page143.pdf"),  # C.I.P. 375 Ruger
    "6.8 mm Remington SPC": (1.24, 3.2, 9.09, 36.0, _CIP + "tab-i/tabical-en-page31.pdf"),  # C.I.P. 6,8 mm Rem. SPC
    ".300 Winchester Short Magnum": (1.37, 3.35, 12.19, 45.0, _CIP + "tab-i/tabical-en-page122.pdf"),  # C.I.P. 300 Win. Short Mag.
    ".17 Remington": (1.14, 3.13, 8.43, 25.0, _CIP + "tab-i/tabical-en-page77.pdf"),  # C.I.P. 17 Rem.
    ".35 Remington": (1.24, 3.14, 10.16, 34.0, _CIP + "tab-i/tabical-en-page136.pdf"),  # C.I.P. 35 Rem.
    ".358 Winchester": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page139.pdf"),  # C.I.P. 358 Win.
    ".300 Weatherby Magnum": (1.3, 5.56, 11.61, 45.0, _CIP + "tab-iii/tabiiical-en-page19.pdf"),  # C.I.P. ?
    ".416 Remington Magnum": (1.27, 5.59, 12.06, 35.0, _CIP + "tab-iii/tabiiical-en-page31.pdf"),  # C.I.P. 416 Rem. Mag.
    "7x61 mm Sharpe & Hart": (1.3, 5.6, 12.2, 35.0, _CIP + "tab-iii/tabiiical-en-page2.pdf"),  # C.I.P. 7 x 61 Super
    ".318 Westley Richards": (1.27, 3.51, 10.52, 25.6, _CIP + "tab-i/tabical-en-page126.pdf"),  # C.I.P. 318 Riml. N.E.
    ".240 Weatherby Magnum": (1.27, 5.56, 10.39, 45.0, _CIP + "tab-iii/tabiiical-en-page10.pdf"),  # C.I.P. ?
    ".224 Weatherby Magnum": (1.27, 5.03, 9.37, 45.0, _CIP + "tab-iii/tabiiical-en-page8.pdf"),  # C.I.P. ?
    "6.5 mm Remington Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page1.pdf"),  # C.I.P. 6,5 mm Rem. Mag.
    ".220 Swift": (1.24, 2.89, 10.82, 15.0, _CIP + "tab-i/tabical-en-page83.pdf"),  # C.I.P. 220 Swift
    ".250 Savage": (1.24, 3.14, 10.39, 36.0, _CIP + "tab-i/tabical-en-page93.pdf"),  # C.I.P. 250 Savage
    ".257 Weatherby Magnum": (1.3, 5.56, 11.61, 45.0, _CIP + "tab-iii/tabiiical-en-page12.pdf"),  # C.I.P. ?
    ".270 Weatherby Magnum": (1.3, 5.56, 11.61, 45.0, _CIP + "tab-iii/tabiiical-en-page14.pdf"),  # C.I.P. ?
    "7 mm Weatherby Magnum": (1.3, 5.56, 11.61, 45.0, _CIP + "tab-iii/tabiiical-en-page5.pdf"),  # C.I.P. 7 mm Weath. Mag.
    ".340 Weatherby Magnum": (1.3, 5.56, 11.61, 45.0, _CIP + "tab-iii/tabiiical-en-page24.pdf"),  # C.I.P. ?
    ".284 Winchester": (1.37, 3.78, 10.39, 40.0, _CIP + "tab-i/tabical-en-page105.pdf"),  # C.I.P. 284 Win.?
    ".300 Savage": (1.24, 3.18, 10.39, 36.0, _CIP + "tab-i/tabical-en-page120.pdf"),  # C.I.P. 300 Savage
    ".25 Remington": (1.24, 3.2, 9.09, 36.0, _CIP + "tab-i/tabical-en-page90.pdf"),  # C.I.P. 25 Rem.
    ".32 Remington": (1.24, 3.19, 9.09, 36.0, _CIP + "tab-i/tabical-en-page127.pdf"),  # C.I.P. 32 Rem.
    "6.5x65 mm RWS": (1.3, 3.2, 10.5, 40.5, _CIP + "tab-i/tabical-en-page29.pdf"),  # C.I.P. 6,5 x 65 RWS
    "9.3x66 mm Sako (.370 Sako Magnum)": (1.3, 3.24, 10.5, 41.0, _CIP + "tab-i/tabical-en-page71.pdf"),  # C.I.P. 9,3 x 66 Sako
    ".300 Blaser Magnum": (1.37, 3.61, 12.19, 45.0, _CIP + "tab-i/tabical-en-page114.pdf"),  # C.I.P. 300 Blaser Mag.
    ".375 Blaser Magnum": (1.37, 3.61, 12.19, 45.0, _CIP + "tab-i/tabical-en-page140.pdf"),  # C.I.P. 375 Blaser Mag.
    "7 mm Blaser Magnum": (1.37, 3.61, 12.19, 45.0, _CIP + "tab-i/tabical-en-page36.pdf"),  # C.I.P. 7 mm Blaser Mag.
    ".338 Blaser Magnum": (1.37, 3.61, 12.19, 45.0, _CIP + "tab-i/tabical-en-page130.pdf"),  # C.I.P. 338 Blaser Mag.
    ".30 Remington": (1.24, 3.19, 9.09, 36.0, _CIP + "tab-i/tabical-en-page108.pdf"),  # C.I.P. 30 Rem.
    ".17 Remington Fireball": (1.14, 3.12, 8.43, 25.0, _CIP + "tab-i/tabical-en-page78.pdf"),  # C.I.P. 17 Rem. Fireball
    ".300 Remington Ultra Magnum": (1.27, 3.75, 12.07, 32.0, _CIP + "tab-i/tabical-en-page119.pdf"),  # C.I.P. 300 Rem. Ultra Mag.
    ".270 Winchester Short Magnum": (1.37, 3.35, 12.19, 45.0, _CIP + "tab-i/tabical-en-page100.pdf"),  # C.I.P. 270 Win. Short Mag.
    "7 mm Winchester Short Magnum": (1.37, 3.35, 12.19, 45.0, _CIP + "tab-i/tabical-en-page43.pdf"),  # C.I.P. 7 mm Win. Short Mag.
    ".338 Federal": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page131.pdf"),  # C.I.P. 338 Federal
    "8 mm Remington Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page6.pdf"),  # C.I.P. 8 mm Rem. Mag.
    ".376 Steyr": (1.3, 3.2, 11.2, 43.0, _CIP + "tab-i/tabical-en-page144.pdf"),  # C.I.P. 376 Steyr
    "6 mm Remington": (1.24, 3.4, 10.36, 34.0, _CIP + "tab-i/tabical-en-page16.pdf"),  # C.I.P. 6 mm Rem. (244 Rem.)
    ".416 Ruger": (1.27, 3.25, 12.07, 35.0, _CIP + "tab-i/tabical-en-page147.pdf"),  # C.I.P. 416 Ruger
    ".416 Weatherby Magnum": (1.6, 6.4, 12.57, 45.0, _CIP + "tab-iii/tabiiical-en-page33.pdf"),  # C.I.P. ?
    ".375 Remington Ultra Magnum": (1.27, 3.75, 12.07, 32.0, _CIP + "tab-i/tabical-en-page142.pdf"),  # C.I.P. 375 Rem. Ultra Mag.
    "7 mm STW": (1.27, 5.58, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page4.pdf"),  # C.I.P. 7 mm STW
    ".223 WSSM": (1.37, 3.35, 12.19, 45.0, _CIP + "tab-i/tabical-en-page87.pdf"),  # C.I.P. 223 Win. Super Short Mag.
    ".243 WSSM": (1.37, 3.35, 12.19, 45.0, _CIP + "tab-i/tabical-en-page89.pdf"),  # C.I.P. 243 Win. Super Short Mag.
    ".25 WSSM": (1.37, 3.36, 12.19, 45.0, _CIP + "tab-i/tabical-en-page91.pdf"),  # C.I.P. 25 Win. SSM
    ".350 Remington Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page25.pdf"),  # C.I.P. 350 Rem. Mag.
    ".338-378 Weatherby Magnum": (1.6, 6.4, 12.57, 45.0, _CIP + "tab-iii/tabiiical-en-page23.pdf"),  # C.I.P. ?
    "7 mm Remington SAUM": (1.27, 3.75, 12.07, 32.0, _CIP + "tab-i/tabical-en-page40.pdf"),  # C.I.P. 7 mm Rem. SA Ultra Mag.
    ".30 Thompson/Center": (1.37, 3.88, 10.39, 35.0, _CIP + "tab-i/tabical-en-page109.pdf"),  # C.I.P. ?
    ".308 Marlin Express": (1.6, 3.72, 10.41, 25.0, _CIP + "tab-i/tabical-en-page124.pdf"),  # C.I.P. 308 Marlin Express
    ".300 Remington SAUM": (1.27, 3.75, 12.07, 32.0, _CIP + "tab-i/tabical-en-page118.pdf"),  # C.I.P. 300 Rem. SA Ultra Mag.
    "6.5-284 Norma": (1.37, 3.78, 10.39, 40.0, _CIP + "tab-i/tabical-en-page18.pdf"),  # C.I.P. 6,5 - 284 Norma
    ".30-378 Weatherby Magnum": (1.6, 6.4, 12.57, 45.0, _CIP + "tab-iii/tabiiical-en-page17.pdf"),  # C.I.P. ?
    "5.6x57 mm": (1.3, 3.2, 10.5, 37.9, _CIP + "tab-i/tabical-en-page5.pdf"),  # C.I.P. 5,6 x 57
    "7.62x45 mm vz. 52": (1.5, 3.99, 9.7, 30.0, _CIP + "tab-i/tabical-en-page48.pdf"),  # C.I.P. 7,62 x 45
    "7.65x53 mm Argentine": (1.0, 3.2, 10.4, 35.7, _CIP + "tab-i/tabical-en-page50.pdf"),  # C.I.P. 7,65 x 53 Arg.
    ".338 Norma Magnum": (1.52, 3.15, 13.24, 50.0, _CIP + "tab-i/tabical-en-page133.pdf"),  # C.I.P. 338 Norma Mag.
    ".358 Norma Magnum": (1.25, 5.56, 11.6, 45.0, _CIP + "tab-iii/tabiiical-en-page26.pdf"),  # C.I.P. ? Norma Mag.
    "9.3x64 mm Brenneke": (1.3, 3.2, 11.2, 43.0, _CIP + "tab-i/tabical-en-page70.pdf"),  # C.I.P. 9,3 x 64 Brenneke
    "9.3x57 mm Mauser": (1.3, 3.2, 10.5, 38.7, _CIP + "tab-i/tabical-en-page68.pdf"),  # C.I.P. 9,3 x 57
    "9x57 mm Mauser": (1.3, 3.2, 10.5, 38.7, _CIP + "tab-i/tabical-en-page67.pdf"),  # C.I.P. 9 x 57
    ".338 Remington Ultra Magnum": (1.27, 3.75, 12.06, 32.0, _CIP + "tab-i/tabical-en-page134.pdf"),  # C.I.P. 338 Rem. Ultra Mag.
    "7 mm Remington Ultra Magnum": (1.27, 3.75, 12.07, 32.0, _CIP + "tab-i/tabical-en-page41.pdf"),  # C.I.P. 7 mm Rem. Ultra Mag.
    ".325 Winchester Short Magnum": (1.37, 3.35, 12.19, 45.0, _CIP + "tab-i/tabical-en-page128.pdf"),  # C.I.P. 325 WSM
    ".375 Weatherby Magnum": (1.3, 5.56, 11.61, 45.0, _CIP + "tab-iii/tabiiical-en-page28.pdf"),  # C.I.P. 375 Weath. Mag.
    ".460 Weatherby Magnum": (1.6, 6.4, 12.57, 45.0, _CIP + "tab-iii/tabiiical-en-page37.pdf"),  # C.I.P. ?
    ".505 Gibbs": (1.65, 4.06, 14.22, 36.3, _CIP + "tab-i/tabical-en-page154.pdf"),  # C.I.P. 505 Mag. Gibbs
    ".500 Jeffery": (1.32, 3.73, 13.77, 34.7, _CIP + "tab-i/tabical-en-page153.pdf"),  # C.I.P. ?
    "6.5 mm Creedmoor": (1.37, 3.84, 10.39, 36.0, "https://bobp.expert-it.com/uploads/tdcc/tab-i/6-5-creedmoor-fr.pdf"),  # C.I.P. 6,5 Creedmoor
    ".300 Norma Magnum": (1.52, 3.15, 13.24, 50.0, "https://bobp.expert-it.com/uploads/tdcc/tab-i/300-norma-mag-fr.pdf"),  # C.I.P. 300 Norma Mag
    ".300 AAC Blackout": (1.14, 3.15, 8.43, 25.0, _CIP + "tab-i/300-aac-blackout-180801-en.pdf"),  # C.I.P. 300 AAC Blackout
    "6.35 mm Browning (.25 ACP)": (1.1, 2.77, 6.35, 20.0, _CIP + "tab-iv/tabivcal-en-page4.pdf"),  # C.I.P. 6,35 Browning
    "7.65 mm Browning (.32 ACP)": (1.25, 3.01, 7.85, 20.0, _CIP + "tab-iv/tabivcal-en-page12.pdf"),  # C.I.P. 7,65 mm Browning
    "9 mm Browning kurz (.380 ACP)": (1.3, 2.84, 8.25, 40.0, _CIP + "tab-iv/tabivcal-en-page24.pdf"),  # C.I.P. 9 mm Browning court
    "9x18 mm Makarov": (1.25, 3.5, 8.55, 29.2, _CIP + "tab-iv/tabivcal-en-page23.pdf"),  # C.I.P. 9 mm Makarov
    "9x19 mm": (1.27, 2.98, 8.79, 35.0, _CIP + "tab-iv/tabivcal-en-page28.pdf"),  # C.I.P. 9 mm Luger
    "9x21 mm IMI": (1.27, 2.98, 8.79, 35.0, _CIP + "tab-iv/tabivcal-en-page20.pdf"),  # C.I.P. 9 x 21
    ".38 Super": (1.27, 3.65, 8.76, 20.0, _CIP + "tab-iv/tabivcal-en-page61.pdf"),  # C.I.P. 38 Super Auto
    "10 mm Auto": (1.4, 3.63, 8.85, 45.0, _CIP + "tab-iv/tabivcal-en-page31.pdf"),  # C.I.P. 10 mm Auto
    ".40 S&W": (1.4, 3.52, 8.81, 45.0, _CIP + "tab-iv/tabivcal-en-page66.pdf"),  # C.I.P. 40 S.& W. (title confirmed)
    ".45 ACP": (1.24, 4.11, 10.16, 26.0, _CIP + "tab-iv/tabivcal-en-page76.pdf"),  # C.I.P. 45 Auto
    ".45 GAP": (1.24, 4.11, 10.16, 26.0, _CIP + "tab-iv/tabivcal-en-page80.pdf"),  # C.I.P. 45 GAP
    "7.65 mm Longue": (1.05, 3.5, 7.5, 21.3, _CIP + "tab-iv/tabivcal-en-page13.pdf"),  # C.I.P. 7,65 Long
    "8 mm Roth-Steyr": (1.1, 3.3, 7.85, 24.4, _CIP + "tab-iv/tabivcal-en-page17.pdf"),  # C.I.P. 8 mm Steyr
    "9 mm Browning Long": (1.25, 2.96, 8.5, 45.0, _CIP + "tab-iv/tabivcal-en-page25.pdf"),  # C.I.P. 9 mm Browning long
    "9x23 mm Steyr": (1.25, 3.5, 8.7, 27.8, _CIP + "tab-iv/tabivcal-en-page29.pdf"),  # C.I.P. 9 mm Steyr
    "9x18 mm Ultra": (1.25, 2.93, 8.25, 50.0, _CIP + "tab-iv/tabivcal-en-page18.pdf"),  # C.I.P. 9 x 18
    ".41 Action Express": (1.27, 3.77, 8.79, 35.0, _CIP + "tab-iv/tabivcal-en-page67.pdf"),  # C.I.P. 41 Act Exp
    ".45 Winchester Magnum": (1.24, 3.38, 10.54, 32.0, _CIP + "tab-iv/tabivcal-en-page84.pdf"),  # C.I.P. 45 Win. Mag.
    ".50 Action Express": (1.5, 3.94, 11.7, 35.0, _CIP + "tab-iv/tabivcal-en-page91.pdf"),  # C.I.P. ?(50 AE: rim 13.06, body 13.79)
    ".416 Rigby": (1.65, 3.81, 12.7, 39.9, _CIP + "tab-i/tabical-en-page146.pdf"),  # C.I.P. 416 Rigby
    ".222 Remington Magnum": (1.14, 3.11, 8.43, 25.0, _CIP + "tab-i/tabical-en-page85.pdf"),  # C.I.P. 222 Rem. Mag.
    ".264 Winchester Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page13.pdf"),  # C.I.P. 264 Win. Mag.
    ".458 Winchester Magnum": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page36.pdf"),  # C.I.P. 458 Win. Mag.
    ".458 Lott": (1.27, 5.59, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page35.pdf"),  # C.I.P. 458 Lott
    ".450 Marlin": (1.27, 6.4, 12.07, 35.0, _CIP + "tab-iii/tabiiical-en-page34.pdf"),  # C.I.P. 450 Marlin
    ".223 Remington": (1.14, 3.15, 8.43, 25.0, _CIP + "tab-i/300-aac-blackout-180801-en.pdf"),  # the .300 BLK is made from .223 Rem. cases; C.I.P. 300 AAC Blackout
    "5.56x45 mm NATO": (1.14, 3.15, 8.43, 25.0, _CIP + "tab-i/300-aac-blackout-180801-en.pdf"),  # same case as the .223 Rem.; C.I.P. 300 AAC Blackout
    "5.6 mm GP 90": (1.14, 3.15, 8.43, 25.0, _CIP + "tab-i/300-aac-blackout-180801-en.pdf"),  # same case as the .223 Rem.; C.I.P. 300 AAC Blackout
    ".300 HAM'R": (1.14, 3.15, 8.43, 25.0, _CIP + "tab-i/300-aac-blackout-180801-en.pdf"),  # made from .223 Rem. cases; C.I.P. 300 AAC Blackout
    "7.62x51 mm NATO": (1.37, 3.85, 10.39, 36.0, _CIP + "tab-i/tabical-en-page125.pdf"),  # same case as the .308 Win.; C.I.P. 308 Win.
    "6 mm Creedmoor": (1.37, 3.84, 10.39, 36.0, "https://bobp.expert-it.com/uploads/tdcc/tab-i/6-5-creedmoor-fr.pdf"),  # 6.5 Creedmoor case necked down; C.I.P. 6,5 Creedmoor
    ".25 Creedmoor": (1.37, 3.84, 10.39, 36.0, "https://bobp.expert-it.com/uploads/tdcc/tab-i/6-5-creedmoor-fr.pdf"),  # 6.5 Creedmoor case necked down; C.I.P. 6,5 Creedmoor
    ".22 Creedmoor": (1.37, 3.84, 10.39, 36.0, "https://bobp.expert-it.com/uploads/tdcc/tab-i/6-5-creedmoor-fr.pdf"),  # 6.5 Creedmoor case necked down; C.I.P. 6,5 Creedmoor
    ".280 Ackley Improved": (1.24, 3.17, 10.39, 36.0, _CIP + "tab-i/tabical-en-page103.pdf"),  # fire-formed .280 Rem.; C.I.P. 280 Rem.
    ".45 Super": (1.24, 4.11, 10.16, 26.0, _CIP + "tab-iv/tabivcal-en-page76.pdf"),  # same case as the .45 ACP, thicker walls; C.I.P. 45 Auto
    ".460 Rowland": (1.24, 4.11, 10.16, 26.0, _CIP + "tab-iv/tabivcal-en-page76.pdf"),  # lengthened .45 ACP case; C.I.P. 45 Auto
    ".400 Cor-Bon": (1.24, 4.11, 10.16, 26.0, _CIP + "tab-iv/tabivcal-en-page76.pdf"),  # .45 ACP case necked down; C.I.P. 45 Auto
    "9x25 mm Dillon": (1.4, 3.63, 8.85, 45.0, _CIP + "tab-iv/tabivcal-en-page31.pdf"),  # 10 mm Auto case necked down; C.I.P. 10 mm Auto
    ".38 ACP": (1.27, 3.65, 8.76, 20.0, _CIP + "tab-iv/tabivcal-en-page61.pdf"),  # same case as the .38 Super; C.I.P. 38 Super Auto
    "9 mm Glisenti": (1.27, 2.98, 8.79, 35.0, _CIP + "tab-iv/tabivcal-en-page28.pdf"),  # same case as the 9x19; C.I.P. 9 mm Luger
    ".356 TSW": (1.27, 2.98, 8.79, 35.0, _CIP + "tab-iv/tabivcal-en-page20.pdf"),  # 9x19-based like the 9x21; C.I.P. 9 x 21
    ".25 NAA": (1.25, 3.01, 7.85, 20.0, _CIP + "tab-iv/tabivcal-en-page12.pdf"),  # .32 ACP case necked down; C.I.P. 7,65 mm Browning
    ".32 NAA": (1.3, 2.84, 8.25, 40.0, _CIP + "tab-iv/tabivcal-en-page24.pdf"),  # .380 ACP case necked down; C.I.P. 9 mm Browning court
    ".224 Valkyrie": (1.24, 3.2, 9.09, 36.0, _CIP + "tab-i/tabical-en-page31.pdf"),  # 6.8 SPC case necked down; C.I.P. 6,8 mm Rem. SPC
    "9x39 mm": (1.5, 3.2, 9.56, 52.0, _CIP + "tab-i/tabical-en-page47.pdf"),  # 7.62x39 case necked up; C.I.P. 7,62 x 39
    "7.35x51 mm Carcano": (1.3, 3.2, 9.95, 74.7, _CIP + "tab-i/tabical-en-page20.pdf"),  # 6.5 Carcano case necked up; C.I.P. 6,5 x 52 Carcano
    "6.5-300 Weatherby Magnum": (1.3, 5.56, 11.61, 45.0, _CIP + "tab-iii/tabiiical-en-page19.pdf"),  # .300 Wby case necked down; C.I.P. ?
    ".300 PRC": (1.27, 3.24, 12.07, 35.0, _CIP + "tab-i/tabical-en-page143.pdf"),  # from the .375 Ruger case; C.I.P. 375 Ruger
    "6.5 PRC": (1.27, 3.24, 12.07, 35.0, _CIP + "tab-i/tabical-en-page143.pdf"),  # from the .375 Ruger case family; C.I.P. 375 Ruger
    "7 mm PRC": (1.27, 3.24, 12.07, 35.0, _CIP + "tab-i/tabical-en-page143.pdf"),  # from the .375 Ruger case family; C.I.P. 375 Ruger
    ".300 Ruger Compact Magnum": (1.27, 3.24, 12.07, 35.0, _CIP + "tab-i/tabical-en-page143.pdf"),  # shortened .375 Ruger case; C.I.P. 375 Ruger
    ".338 Ruger Compact Magnum": (1.27, 3.24, 12.07, 35.0, _CIP + "tab-i/tabical-en-page143.pdf"),  # shortened .375 Ruger case; C.I.P. 375 Ruger
    "6.8 Western": (1.37, 3.35, 12.19, 45.0, _CIP + "tab-i/tabical-en-page100.pdf"),  # .270 WSM case; C.I.P. 270 Win. Short Mag.
    ".404 Jeffery": (1.27, 3.3, 12.37, 36.04, _CIP + "tab-i/tabical-en-page145.pdf"),  # C.I.P. 404 Riml. N.E.
    "8.5x55 mm Blaser": (1.37, 3.62, 12.19, 45.0, "https://cuzzs.gov.cz/userfiles/documents/CIP/02092021/Mimoradny_Vestnik_%202021_DEF.pdf"),  # C.I.P. sheet p7
}


def case_head(name):
    """(rim thickness, ramp top or belt front, groove diameter, ramp angle) or None."""
    entry = CASE_HEADS.get(name)
    return entry[:4] if entry else None


# Where each primer size in PRIMERS was checked. Wikipedia pages are the cartridge infobox
# ("Primer type"); Hodgdon, Vihtavuori and Sierra are the primers used in their published
# reloading data; Starline is the primer named on its brass page. Shot shells: Hodgdon's
# shotshell data uses 209-size primers for every gauge and length listed. municion.org: the
# primer diameter measured on its headstamp photos (median over the specimens, scaled by the rim
# diameter; checked on 9 mm, .38 Special and .308 to within 2 %). It gives the original primer:
# about 6.1-6.7 mm is the .254" Berdan Nitro primer, under 4.5 mm a small one. Readings between two
# sizes (4.8-5.0 mm, about 6.0 mm) stay unverified. Calibres not yet checked against a source are
# in PRIMER_UNVERIFIED, so a new calibre has to go in one of the two.
_HODGDON = "https://hodgdonreloading.com/rldc/"
_VIHTAVUORI = "https://vihtavuori.com/reloading-data/reloading-data-tool/"
_STARLINE = "https://www.starlinebrass.com/"
_MUNICION = "https://municion.org/producto/"
PRIMER_SOURCES = {
    ".25 Remington": _MUNICION + "25-remington-auto/",  # 5.30 mm, 6 specimens
    ".32 Remington": _MUNICION + "32-remington/",  # 5.11 mm, 4 specimens
    ".30 Remington": _MUNICION + "30-remington/",  # 5.33 mm, 3 specimens
    ".35 Winchester Self-Loading": _MUNICION + "35-winchester-self-loading/",  # 4.44 mm, 3 specimens
    ".401 Winchester Self-Loading": _MUNICION + "401-winchester-self-loading/",  # 5.34 mm, 8 specimens
    ".40-82 WCF": _MUNICION + "40-82-260-winchester-cf-marlin/",  # 5.05 mm, 8 specimens
    ".50-95 WCF": _MUNICION + "50-95-300-winchester/",  # 5.16 mm, 6 specimens
    ".45-75 Winchester": _MUNICION + "45-75-winchester-centennial/",  # 5.23 mm, 5 specimens
    ".35 S&W Auto": _MUNICION + "35-smith-wesson-automatic/",  # 4.34 mm, 4 specimens
    "10.3x60 mm R": _MUNICION + "103-x-60-r/",  # 6.14 mm, 4 specimens
    "11x59 mm R Gras": _MUNICION + "11-x-59-r-french-gras-m-1874-79-83/",  # 6.10 mm, 8 specimens
    ".500/465 Nitro Express": _MUNICION + "500-465-holland-holland-flanged-ne-3-1-4/",  # 6.13 mm, 3 specimens
    ".475 No. 2 Nitro Express": _MUNICION + "475-n2-nitro-express-jeffery-3-1-2/",  # 6.69 mm, 5 specimens
    ".375 Flanged Nitro Express": _MUNICION + "375-flanged-nitro-express/",  # 6.22 mm, 2 specimens
    "9.3x72 mm R": _MUNICION + "93-x-72-r-d-express/",  # 6.47 mm, 2 specimens
    ".450 Adams": _MUNICION + "450-adams-mk-ii-brass-base-disk/",  # 4.23 mm, 6 specimens
    ".476 Enfield": _MUNICION + "476-enfield-revolver-mk-iii/",  # 4.41 mm, 3 specimens
    ".360 No. 5 Rook": _MUNICION + "360-n-5-revolver-rifle/",  # 4.40 mm, 8 specimens
    "8 mm Roth-Steyr": _MUNICION + "8-mm-roth-steyr/",  # 4.32 mm, 8 specimens
    "9 mm Glisenti": _MUNICION + "9-mm-glisenti-m-1910/",  # 4.34 mm, 7 specimens
    "7.35x51 mm Carcano": _MUNICION + "735-x-51-italian-carcano-m-1938/",  # 5.11 mm, 4 specimens
    "8x60 mm S": _MUNICION + "8-x-60-s-mauser/",  # 5.11 mm, 5 specimens
    "5.75 mm Velo-Dog": _MUNICION + "56-mm-velo-dog/",  # 4.15 mm, 8 specimens
    ".55 Boys": _MUNICION + "55-boys/",  # 7.61 mm, 7 specimens
    "8x58 mm R Danish Krag": _MUNICION + "8-x-58-r-danish-krag-jorgensen-m-1889/",  # 5.42 mm, 8 specimens
    "7.92x107 mm DS": _MUNICION + "792-x-107-polish-anti-tank-maroszek-ur-wz-35/",  # 5.64 mm, 4 specimens
    "9x57 mm Mauser": _MUNICION + "9-x-57-mauser/",  # 5.36 mm, 8 specimens
    "6.5x57 mm R": _MUNICION + "65-x-57-r-mauser-m88/",  # 5.11 mm, 4 specimens
    ".416 Barrett": _MUNICION + "416-barrett-sniper/",  # 7.77 mm, 2 specimens
    "12.7x108 mm": _MUNICION + "127-x-108-russian-dshk-rimless/",  # 8.70 mm, 8 specimens
    ".600 Nitro Express": _MUNICION + "600-nitro-express-3/",  # 5.52 mm, 8 specimens
    "6.5x65 mm RWS": _MUNICION + "65-x-65-rws/",  # 5.38 mm, 2 specimens
    "8x75 mm RS": _MUNICION + "8-x-75-r-s-behr/",  # 5.10 mm, 6 specimens
    ".450/400 Nitro Express 3 inch": _MUNICION + "450-400-express-2-3-8/",  # 5.16 mm, 6 specimens
    ".400/350 Nitro Express": _MUNICION + "400-350-rigby-flanged-nitro-express/",  # 5.53 mm, 3 specimens
    "6.5x58 mm Vergueiro": _MUNICION + "65-x-58-mauser-vergueiro-m-1904/",  # 5.28 mm, 8 specimens
    "7x61 mm Sharpe & Hart": "https://sierrabullets.com/content/load-data/legacy/284-7mm/7x61mm-sharpe-hart.pdf",  # Rem 9 1/2M
    "6.35 mm Browning (.25 ACP)": _WP + ".25_ACP",
    "7.65 mm Browning (.32 ACP)": _WP + ".32_ACP",
    "7.65 mm Parabellum": _WP + "7.65×21mm_Parabellum",
    ".32 S&W Long": _WP + ".32_S%26W_Long",
    ".32 S&W Long Wadcutter": _WP + ".32_S%26W_Long",  # the same case
    ".32 H&R Magnum": _WP + ".32_H%26R_Magnum",
    "7.62x25 mm Tokarev": _WP + "7.62×25mm_Tokarev",
    "9 mm Browning kurz (.380 ACP)": _WP + ".380_ACP",
    "7.63x25 mm Mauser": _STARLINE + "30-mauser-brass",
    "7.62x38 mm R Nagant": _WP + "7.62×38mmR",
    "7.5 mm Swiss Ordnance 1882": _WP + "7.5mm_1882_Ordnance",
    "7.65 mm Longue": _WP + "7.65×20mm_Long",
    ".32 S&W": _WP + ".32_S%26W",
    ".327 Federal Magnum": _WP + ".327_Federal_Magnum",
    ".32-20 Winchester": _WP + ".32-20_Winchester",
    "5.45x18 mm": _WP + "5.45×18mm",
    ".22 TCM": _HODGDON,
    "8 mm Nambu": _WP + "8×22mm_Nambu",
    "9 mm Browning Long": _WP + "9mm_Browning_Long",
    "9x23 mm Steyr": _WP + "9×23mm_Steyr",
    "9x23 mm Largo": _WP + "9×23mm_Largo",
    ".38 S&W": _WP + ".38_S%26W",
    ".38 Short Colt": _STARLINE + "38-short-colt-brass",
    ".38 Long Colt": _STARLINE + "38-long-colt-brass",
    ".38-40 Winchester": _STARLINE + "38-40-brass",
    ".44 S&W Russian": _WP + ".44_S%26W_Russian",
    ".45 Schofield": _WP + ".45_Schofield",
    ".45 Auto Rim": _WP + ".45_Auto_Rim",
    ".455 Webley": _WP + ".455_Webley",
    ".480 Ruger": _WP + ".480_Ruger",
    ".50 Action Express": _WP + ".50_Action_Express",
    "9x18 mm Makarov": _WP + "9×18mm_Makarov",
    "9x19 mm": _WP + "9×19mm_Parabellum",
    "9x21 mm IMI": _WP + "9×21mm",
    ".357 SIG": _WP + ".357_SIG",
    ".38 Special": _WP + ".38_Special",
    ".357 Magnum": _WP + ".357_Magnum",
    ".38 Super": _WP + ".38_Super",
    "10 mm Auto": _WP + "10mm_Auto",
    ".40 S&W": _WP + ".40_S%26W",
    ".41 Magnum": _WP + ".41_Remington_Magnum",
    ".44 Special": _WP + ".44_Special",
    ".44 Magnum": _WP + ".44_Magnum",
    ".45 ACP": _WP + ".45_ACP",
    ".45 Colt": _WP + ".45_Colt",
    ".45 GAP": _WP + ".45_GAP",
    ".454 Casull": _WP + ".454_Casull",
    ".460 S&W Magnum": _WP + ".460_S%26W_Magnum",
    ".500 S&W Magnum": _WP + ".500_S%26W_Magnum",
    "5.7x28 mm": _WP + "FN_5.7×28mm",
    "4.6x30 mm": _WP + "HK_4.6×30mm",
    ".204 Ruger": _WP + ".204_Ruger",
    ".222 Remington": _WP + ".222_Remington",
    ".223 Remington": _WP + ".223_Remington",
    "5.56x45 mm NATO": _WP + "5.56×45mm_NATO",
    ".22-250 Remington": _WP + ".22-250_Remington",
    ".243 Winchester": _WP + ".243_Winchester",
    "6 mm BR Norma": _WP + "6mm_BR",
    "6 mm ARC": _WP + "6mm_ARC",
    "6.5 mm Creedmoor": _WP + "6.5mm_Creedmoor",
    "6.5x55 mm Swedish": _WP + "6.5×55mm_Swedish",
    "6.5x47 mm Lapua": _WP + "6.5×47mm_Lapua",
    "6.5 PRC": _HODGDON,
    ".260 Remington": _WP + ".260_Remington",
    ".270 Winchester": _WP + ".270_Winchester",
    "7 mm-08 Remington": _WP + "7mm-08_Remington",
    "7x57 mm Mauser": _WP + "7×57mm_Mauser",
    "7x64 mm": _WP + "7×64mm",
    "7 mm Remington Magnum": _WP + "7mm_Remington_Magnum",
    "7 mm PRC": _HODGDON,
    "7.5x55 mm Swiss (GP 11)": _WP + "7.5×55mm_Swiss",
    "7.5x53.5 mm Swiss (GP 1890)": _WP + "7.5×55mm_Swiss",
    "7.5 mm Kadettenpatrone": _WP + "7.5×55mm_Swiss",  # GP 90 family; Raven measured a 5.4 mm primer
    "7.5x54 mm French": _WP + "7.5×54mm_French",
    "7.62x39 mm": _VIHTAVUORI,
    ".300 AAC Blackout": _WP + ".300_AAC_Blackout",
    ".300 HAM'R": _STARLINE + "300-hamr-brass",
    "7.62x51 mm NATO": _WP + "7.62×51mm_NATO",
    ".308 Winchester": _WP + ".308_Winchester",
    ".30-06 Springfield": _WP + ".30-06_Springfield",
    ".30-30 Winchester": _WP + ".30-30_Winchester",
    ".300 Winchester Magnum": _WP + ".300_Winchester_Magnum",
    ".300 PRC": _HODGDON,
    ".300 Norma Magnum": _WP + ".300_Norma_Magnum",
    ".303 British": _WP + ".303_British",
    "7.62x54 mm R": _WP + "7.62×54mmR",
    "8x57 mm IS": _WP + "7.92×57mm_Mauser",
    "8x68 mm S": _WP + "8×68mm_S",
    "9.3x62 mm": _WP + "9.3×62mm",
    "9.3x74 mm R": _WP + "9.3×74mmR",
    ".338 Lapua Magnum": _WP + ".338_Lapua_Magnum",
    ".375 H&H Magnum": _WP + ".375_H%26H_Magnum",
    ".416 Rigby": _WP + ".416_Rigby",
    ".450 Rigby": _WP + ".450_Rigby",
    ".375 CheyTac": _WP + ".408_Cheyenne_Tactical",
    ".45-70 Government": _WP + ".45-70",
    ".50 BMG": _WP + ".50_BMG",
    "6.5x52 mm Carcano": _HODGDON,
    "6.5x50 mm SR Arisaka": _WP + "6.5×50mmSR_Arisaka",
    "7.7x58 mm Arisaka": _WP + "7.7×58mm_Arisaka",
    "8x50 mm R Lebel": _WP + "8×50mmR_Lebel",
    "8x56 mm R Mannlicher": _WP + "8×56mmR",
    "6.5x54 mm Mannlicher-Schönauer": _WP + "6.5×54mm_Mannlicher–Schönauer",
    ".30-40 Krag": _HODGDON,
    "7.92x33 mm Kurz": _WP + "7.92×33mm_Kurz",
    "5.45x39 mm": _WP + "5.45×39mm",
    ".277 SIG Fury": _VIHTAVUORI,
    ".22 Hornet": _WP + ".22_Hornet",
    ".25-06 Remington": _WP + ".25-06_Remington",
    ".257 Roberts": _WP + ".257_Roberts",
    ".280 Remington": _WP + ".280_Remington",
    ".35 Whelen": _WP + ".35_Whelen",
    ".300 H&H Magnum": _WP + ".300_H%26H_Magnum",
    ".338 Winchester Magnum": _WP + ".338_Winchester_Magnum",
    ".444 Marlin": _WP + ".444_Marlin",
    ".458 Winchester Magnum": _WP + ".458_Winchester_Magnum",
    ".350 Legend": _WP + ".350_Legend",
    ".50-70 Government": _STARLINE + "50-70-govt-brass",
    ".44-40 WCF": _WP + ".44-40_Winchester",
    "12/70": _HODGDON,
    "12/76": _HODGDON,
    "12/89": _HODGDON,
    "16/70": _HODGDON,
    "20/70": _HODGDON,
    "20/76": _HODGDON,
    "28/70": _HODGDON,
    ".410/76": _HODGDON,
    "5.6x50 mm Magnum": _WP + "5.6×50mm_Magnum",
    "6.5x57 mm Mauser": _WP + "6.5×57mm_Mauser",
    "6.5x68 mm": _WP + "6.5×68mm",
    "8x64 mm S": _WP + "8×64mm_S",
    ".375 Ruger": _WP + ".375_Ruger",
    ".450 Bushmaster": _HODGDON,
    "6.8 mm Remington SPC": _WP + "6.8mm_Remington_SPC",
    ".300 Winchester Short Magnum": _WP + ".300_Winchester_Short_Magnum",
    ".17 Remington": _WP + ".17_Remington",
    ".218 Bee": _WP + ".218_Bee",
    ".25-35 Winchester": _WP + ".25-35_Winchester",
    ".32 Winchester Special": _WP + ".32_Winchester_Special",
    ".35 Remington": _WP + ".35_Remington",
    ".38-55 Winchester": _STARLINE + "38-55-brass-2080",
    ".348 Winchester": _WP + ".348_Winchester",
    ".358 Winchester": _WP + ".358_Winchester",
    ".264 Winchester Magnum": _WP + ".264_Winchester_Magnum",
    ".300 Weatherby Magnum": _WP + ".300_Weatherby_Magnum",
    ".416 Remington Magnum": _WP + ".416_Remington_Magnum",
    ".470 Nitro Express": _HODGDON,
    "9x18 mm Ultra": _WP + "9×18mm_Ultra",
    ".357 Remington Maximum": _HODGDON,
    ".41 Action Express": _WP + ".41_Action_Express",
    ".45 Winchester Magnum": _WP + ".45_Winchester_Magnum",
    ".45 Super": _WP + ".45_Super",
    ".460 Rowland": _STARLINE + "460-rowland-brass",
    ".475 Linebaugh": _WP + ".475_Linebaugh",
    ".221 Remington Fireball": _WP + ".221_Remington_Fireball",
    ".25 NAA": _WP + ".25_NAA",
    ".32 NAA": _WP + ".32_NAA",
    ".32 Long Colt": _WP + ".32_Long_Colt",
    ".45-90 WCF": _STARLINE + "45-90-brass-45-24",
    ".38 ACP": _WP + ".38_ACP",
    ".41 Long Colt": _STARLINE + "41-colt-brass",
    ".44 Colt": _WP + ".44_Colt",
    ".32-40 Ballard": _WP + ".32-40_Ballard",
    ".50-90 Sharps": _WP + ".50-90_Sharps",
    ".220 Swift": _WP + ".220_Swift",
    ".25-20 Winchester": _WP + ".25-20_Winchester",
    ".250 Savage": _WP + ".250-3000_Savage",
    ".257 Weatherby Magnum": _WP + ".257_Weatherby_Magnum",
    ".270 Weatherby Magnum": _WP + ".270_Weatherby_Magnum",
    "7 mm Weatherby Magnum": _WP + "7mm_Weatherby_Magnum",
    ".340 Weatherby Magnum": _WP + ".340_Weatherby_Magnum",
    ".284 Winchester": _WP + ".284_Winchester",
    ".300 Savage": _WP + ".300_Savage",
    ".300 Remington Ultra Magnum": _WP + ".300_Remington_Ultra_Magnum",
    ".270 Winchester Short Magnum": _WP + ".270_Winchester_Short_Magnum",
    "7 mm Winchester Short Magnum": _WP + "7mm_Winchester_Short_Magnum",
    ".338 Federal": _WP + ".338_Federal",
    "8 mm Remington Magnum": _WP + "8mm_Remington_Magnum",
    ".376 Steyr": _WP + ".376_Steyr",
    "6.5 mm Grendel": _WP + "6.5mm_Grendel",
    "6 mm Remington": _WP + "6mm_Remington",
    "7-30 Waters": _WP + "7-30_Waters",
    ".17 Hornet": _HODGDON,
    ".375 Winchester": _HODGDON,
    ".405 Winchester": _WP + ".405_Winchester",
    ".450 Marlin": _WP + ".450_Marlin",
    ".458 Lott": _WP + ".458_Lott",
    ".30 Carbine": _HODGDON,
    "7x65 mm R": _WP + "7×64mm",
    ".22 Savage Hi-Power": _WP + ".22_Savage_Hi-Power",
    "8x57 mm IRS": _VIHTAVUORI,
    ".280 Ackley Improved": _HODGDON,
    ".356 Winchester": _HODGDON,
    ".307 Winchester": _HODGDON,
    ".416 Ruger": _WP + ".416_Ruger",
    ".416 Weatherby Magnum": _WP + ".416_Weatherby_Magnum",
    ".375 Remington Ultra Magnum": _WP + ".375_Remington_Ultra_Magnum",
    "7 mm STW": _WP + "7mm_STW",
    ".225 Winchester": _WP + ".225_Winchester",
    ".223 WSSM": _WP + ".223_Winchester_Super_Short_Magnum",
    ".243 WSSM": _WP + ".243_Winchester_Super_Short_Magnum",
    ".25 WSSM": _HODGDON,
    ".350 Remington Magnum": _WP + ".350_Remington_Magnum",
    ".400 Cor-Bon": _STARLINE + "400-cor-bon-brass",
    "9x23 mm Winchester": _WP + "9×23mm_Winchester",
    ".26 Nosler": _WP + ".28_Nosler",
    ".27 Nosler": _WP + ".28_Nosler",
    ".28 Nosler": _WP + ".28_Nosler",
    ".30 Nosler": _WP + ".28_Nosler",
    ".33 Nosler": _WP + ".28_Nosler",
    ".300 Ruger Compact Magnum": _WP + ".300_Ruger_Compact_Magnum",
    ".30 Thompson/Center": _HODGDON,
    ".30 Remington AR": _HODGDON,
    ".308 Marlin Express": _WP + ".308_Marlin_Express",
    ".300 Remington SAUM": _WP + ".300_Remington_Short_Action_Ultra_Magnum",
    ".224 Valkyrie": _WP + ".224_Valkyrie",
    ".458 SOCOM": _WP + ".458_SOCOM",
    ".50 Beowulf": _WP + ".50_Beowulf",
    ".222 Remington Magnum": _WP + ".222_Remington_Magnum",
    "6.5-284 Norma": _HODGDON,
    ".25 Weatherby RPM": _HODGDON,
    "6.5 Weatherby RPM": _HODGDON,
    ".338 Weatherby RPM": _HODGDON,
    ".30-378 Weatherby Magnum": _WP + ".30-378_Weatherby_Magnum",
    "5.6x57 mm": _WP + "5.6×57mm",
    "11x60 mm R Mauser": _WP + "11×60mm_Mauser",
    "7.62x45 mm vz. 52": _WP + "7.62×45mm",
    "7.65x53 mm Argentine": _WP + "7.65×53mm_Mauser",
    ".338-378 Weatherby Magnum": _WP + ".338-378_Weatherby_Magnum",
    "6.8 Western": _WP + "6.8_Western",
    "7 mm Remington SAUM": _WP + "7mm_Remington_Short_Action_Ultra_Magnum",
    ".22 Remington Jet": _WP + ".22_Remington_Jet",
    ".256 Winchester Magnum": _WP + ".256_Winchester_Magnum",
    ".338 Norma Magnum": _WP + ".338_Norma_Magnum",
    ".308 Norma Magnum": _WP + ".308_Norma_Magnum",
    ".358 Norma Magnum": _HODGDON,
    "9.3x64 mm Brenneke": _WP + "9.3×64mm_Brenneke",
    "9.3x57 mm Mauser": _WP + "9.3×57mm_Mauser",
    "7x57 mm R": _VIHTAVUORI,
    ".338 Remington Ultra Magnum": _WP + ".338_Remington_Ultra_Magnum",
    "7 mm Remington Ultra Magnum": _WP + "7mm_Remington_Ultra_Magnum",
    ".325 Winchester Short Magnum": _WP + ".325_WSM",
    ".375 Weatherby Magnum": _WP + ".375_Weatherby_Magnum",
    ".460 Weatherby Magnum": _WP + ".460_Weatherby_Magnum",
    ".404 Jeffery": _WP + ".404_Jeffery",
    ".505 Gibbs": _WP + ".505_Gibbs",
    ".500 Jeffery": _WP + ".500_Jeffery",
    ".33 Winchester": _WP + ".33_Winchester",
    ".351 Winchester Self-Loading": _WP + ".351_Winchester_Self-Loading",
    ".40-65 Winchester": _WP + ".40-65_Winchester",
    ".303 Savage": _WP + ".303_Savage",
    ".219 Zipper": _WP + ".219_Zipper",
    ".500 Nitro Express": _HODGDON,
    ".700 Nitro Express": _WP + ".700_Nitro_Express",
    ".240 Weatherby Magnum": _WP + ".240_Weatherby_Magnum",
    ".224 Weatherby Magnum": _WP + ".224_Weatherby_Magnum",
    "6.5 mm Remington Magnum": _WP + "6.5mm_Remington_Magnum",
    "6 mm Creedmoor": _WP + "6.5mm_Creedmoor",
    ".25 Creedmoor": _HODGDON,
    "8.6 Blackout": _STARLINE + "86-blackout-brass",
    ".22 ARC": _HODGDON,
    ".338 Ruger Compact Magnum": _WP + ".338_Ruger_Compact_Magnum",
    ".408 CheyTac": _WP + ".408_Cheyenne_Tactical",
    ".360 Buckhammer": _HODGDON,
    ".400 Legend": _WP + ".400_Legend",
    "9.3x66 mm Sako (.370 Sako Magnum)": _VIHTAVUORI,
    ".38-56 WCF": _WP + ".38-56_WCF",
    ".17 Remington Fireball": _WP + ".17_Remington_Fireball",
    ".338 Marlin Express": _HODGDON,
    ".22 Nosler": _HODGDON,
    "6.5-300 Weatherby Magnum": _HODGDON,
    "9x25 mm Dillon": _WP + "9×25mm_Dillon",
    ".300 Lapua Magnum": _WP + ".300_Lapua_Magnum",
    ".35 Winchester": _WP + ".35_Winchester",
    ".50-110 Winchester": _WP + ".50-110_Winchester",
    ".400 H&H Magnum": _WP + ".400_H%26H_Magnum",
    ".465 H&H Magnum": _WP + ".465_H%26H_Magnum",
    ".310 Cadet": _WP + ".310_Cadet",
    ".30 R Blaser": _WP + ".30_R_Blaser",
    ".378 Weatherby Magnum": _WP + ".378_Weatherby_Magnum",
    "7.5 FK": _WP + "7.5_FK",
    "6 mm GT": _HODGDON,
    ".22 Creedmoor": _VIHTAVUORI,
    "7 mm Backcountry": _WP + "7mm_Backcountry",
    ".338 ARC": _HODGDON,
    "6 mm PPC": _WP + "6mm_PPC",
    "9x39 mm": _STARLINE + "9x39-brass",
    ".320 Revolver": _WP + ".320_Revolver",  # Berdan; Raven's Fiocchi round measures 4.7 mm (2026-11-08)
}

# Primer sizes still unchecked: no reloading data, brass maker page or clear headstamp photo
# found yet (old military rounds, Nitro Expresses, European hunting rounds). Hodgdon loads .30 Super Carry with small
# rifle primers; Federal's ammunition uses small pistol, so it stays small pistol until checked.
PRIMER_UNVERIFIED = {
    ".450 No. 2 Nitro Express", ".500/416 Nitro Express", ".375 Flanged Magnum Nitro Express",
    "9.3x53 mm R Finnish", ".30 Super Carry", "8 mm Lebel revolver", "10.4 mm Swiss Ordnance 1878",
    "11 mm French Ordnance", "9 mm P.A.K.", "8 mm Knall", ".315 Knall", "9 mm R Knall", ".320 Knall",
    ".45 Knall", "5.6 mm GP 90", "8x50 mm R Mannlicher", "5.8x42 mm",
    "10.4x38 mm R Vetterli", ".577 Snider", ".577/450 Martini-Henry",
    "9.5x57 mm Mannlicher-Schönauer", ".500 JRH", ".442 Webley", ".356 TSW",
    "6.5x53 mm R Mannlicher", ".450 Nitro Express", ".577 Nitro Express", ".318 Westley Richards",
    ".300 Blaser Magnum", ".375 Blaser Magnum", "7 mm Blaser Magnum", ".338 Blaser Magnum",
    "8.5x55 mm Blaser", ".244 H&H Magnum", ".350 Rigby Magnum",
}


# Calibres no longer in regular factory production (only surplus, boutique loads or reloading).
# Everything else is current. The apps can hide these by default; the poster can mark them.
OBSOLETE = {
    "7x61 mm Sharpe & Hart", ".360 No. 5 Rook",
    ".320 Revolver",  # 2026-11-08: "an obsolete revolver cartridge" (Wikipedia)
    "7.5x53.5 mm Swiss (GP 1890)", "7.5 mm Kadettenpatrone", "10.4x38 mm R Vetterli", "18 mm Milbank-Amsler", ".577 Snider", "10.4 mm Swiss Ordnance 1872 Rimfire", ".577/450 Martini-Henry",
    ".50-70 Government", ".58 Minié", ".69 Minié",
    "7.5 mm Swiss Ordnance 1882", "7.65 mm Longue", "8 mm Nambu", "8 mm Lebel revolver", "8 mm Roth-Steyr",
    "9 mm Glisenti", "9x23 mm Steyr", "9x23 mm Largo", ".38 Long Colt", "10.4 mm Swiss Ordnance 1878",
    "11 mm French Ordnance",
    "8x50 mm R Mannlicher", "7.35x51 mm Carcano",
    "9.5x57 mm Mannlicher-Schönauer",
    "9x18 mm Ultra",
    ".357 Remington Maximum",
    ".41 Action Express",
    ".32 Long Colt",
    ".22 Extra Long", ".32 Short Rimfire", ".32 Long Rimfire", ".55 Boys",
    ".35 S&W Auto",
    ".38 ACP",
    ".41 Long Colt",
    ".442 Webley",
    ".450 Adams",
    ".476 Enfield",
    ".44 Henry",
    "11x59 mm R Gras",
    ".32-40 Ballard",
    ".50-90 Sharps",
    ".225 Winchester",
    ".223 WSSM",
    ".243 WSSM",
    ".25 WSSM",
    ".356 TSW",
    ".30 Remington AR",
    ".308 Marlin Express",
    ".222 Remington Magnum",
    "11x60 mm R Mauser",
    "6.5x53 mm R Mannlicher",
    "8x58 mm R Danish Krag",
    "7.62x45 mm vz. 52",
    "7.92x107 mm DS",
    ".22 Remington Jet",
    ".256 Winchester Magnum",
    "9x57 mm Mauser",
    ".33 Winchester",
    ".25 Remington",
    ".32 Remington",
    ".35 Winchester Self-Loading",
    ".351 Winchester Self-Loading",
    ".401 Winchester Self-Loading",
    ".303 Savage",
    ".219 Zipper",
    ".224 Weatherby Magnum",
    "6.5 mm Remington Magnum",
    ".30 Remington", ".338 Marlin Express", ".38-56 WCF", ".40-82 WCF", ".50-95 WCF",
    ".25 Stevens",
    ".41 Short",
    ".56-56 Spencer",
    ".35 Winchester",
    ".50-110 Winchester",
    ".244 H&H Magnum",
    ".45-75 Winchester",
    ".22 Remington Automatic",
    ".400/350 Nitro Express",
    ".310 Cadet",
    "6.5x58 mm Vergueiro",
}


def is_obsolete(name):
    return name in OBSOLETE


# Calibres you are unlikely to find, so a photo or measurement that matches one is far more
# likely a false positive than the real thing. Independent of OBSOLETE: most rare calibres are
# obsolete collector rounds, but some are still made in small numbers (big Nitro and African
# rounds, short-lived magnums, niche handgun rounds). Checked on 2026-11-04 against the share of
# each site's listings a calibre has (waffenbörse.ch, swisswaffen.com, GunBroker, TownPost,
# Frankonia, usedguns.com.au, zbrane.cz and others), so a big site counts for more than a small one:
# a calibre with at least 0.5 per mille and at least 3 listings on any site is not rare, unless
# it is obsolete (the guns outlive the ammunition). Under 0.05 per mille on GunBroker and at most
# 2 listings elsewhere counts as rare.
RARE = {
    ".320 Revolver", "9 mm Flobert Bosquette",  # 2026-11-08: from Raven's bag of old rounds
    ".450 No. 2 Nitro Express", ".500/416 Nitro Express", ".375 Flanged Magnum Nitro Express", ".22 Extra Long", ".32 Short Rimfire", ".32 Long Rimfire", "5.75 mm Velo-Dog", ".500 JRH", ".375 Flanged Nitro Express", ".55 Boys", ".45-90 WCF",
    "9.3x53 mm R Finnish", "7x61 mm Sharpe & Hart", ".360 No. 5 Rook",
    ".219 Zipper", ".22 Remington Jet", ".223 WSSM", ".225 Winchester",
    ".25 Remington", ".25 WSSM", ".256 Winchester Magnum", ".30 Remington AR", ".303 Savage",
    ".32 Remington", ".33 Winchester", ".35 S&W Auto", ".35 Winchester Self-Loading",
    ".351 Winchester Self-Loading", ".356 TSW", ".401 Winchester Self-Loading",
    ".41 Action Express", ".44 Henry", ".442 Webley", ".450 Adams", ".476 Enfield", ".577 Snider",
    "11 mm French Ordnance", "18 mm Milbank-Amsler", "10.4 mm Swiss Ordnance 1872 Rimfire",
    "7.5 mm Kadettenpatrone",  # 2026-11-08: made only for the Kadettengewehr 1897 (about 7,900 made); collectors' item
    "11x59 mm R Gras", "11x60 mm R Mauser", "6.5x53 mm R Mannlicher", "7.35x51 mm Carcano",
    "7.62x45 mm vz. 52", "7.92x107 mm DS",
    "8 mm Nambu", "8 mm Roth-Steyr", "8x50 mm R Mannlicher", "8x58 mm R Danish Krag",
    "9.5x57 mm Mannlicher-Schönauer", "9x57 mm Mauser",
    "8 mm Lebel revolver", "9 mm Glisenti", ".32 Long Colt", ".38 Long Colt", ".41 Long Colt",
    ".38 ACP", ".357 Remington Maximum", ".222 Remington Magnum", ".243 WSSM",
    ".308 Marlin Express", ".577/450 Martini-Henry", ".50-70 Government", ".50-90 Sharps", ".69 Minié",
    # Still made, but hardly ever found:
    ".450 Rigby", ".375 CheyTac", ".505 Gibbs", ".277 SIG Fury", "5.8x42 mm", ".25 Weatherby RPM", 
    ".338 Weatherby RPM", ".300 HAM'R", ".500 Jeffery", "12.7x108 mm", ".460 Weatherby Magnum",
    ".338-378 Weatherby Magnum", ".30-378 Weatherby Magnum", "7 mm STW", ".22 Savage Hi-Power",
    ".307 Winchester", ".356 Winchester", ".458 SOCOM", ".50 Beowulf",
    ".30 Thompson/Center", ".300 Ruger Compact Magnum", ".300 Remington SAUM",
    ".325 Winchester Short Magnum", ".27 Nosler", ".33 Nosler",
    ".460 Rowland", ".475 Linebaugh", ".22 TCM", ".25 NAA", ".32 NAA", ".45 Super",
    ".45 Winchester Magnum", "9x23 mm Winchester", ".400 Cor-Bon",
    ".577 Nitro Express", ".600 Nitro Express", ".700 Nitro Express", ".500/465 Nitro Express",
    ".224 Weatherby Magnum",
    ".408 CheyTac", ".338 Ruger Compact Magnum",
    ".45 GAP", "5 mm Remington Rimfire Magnum", ".221 Remington Fireball",
    ".224 Valkyrie", ".376 Steyr", "8 mm Remington Magnum", 
    ".358 Norma Magnum", ".416 Weatherby Magnum", "7 mm Remington Ultra Magnum",
    ".338 Remington Ultra Magnum", ".375 Remington Ultra Magnum",
    # Sourced 2026-11-04 (C.I.P. etc.), all hardly ever found:
    "9.3x72 mm R", "8x75 mm RS", "6.5x65 mm RWS", "9.3x66 mm Sako (.370 Sako Magnum)", ".300 Blaser Magnum", ".375 Blaser Magnum", ".338 Blaser Magnum", ".450/400 Nitro Express 3 inch", ".40-82 WCF", ".50-95 WCF", ".38-56 WCF", ".30 Remington", ".17 Remington Fireball", ".338 Marlin Express", ".22 Nosler", 
    ".25 Stevens", ".41 Short", ".56-56 Spencer", "9x25 mm Dillon", ".300 Lapua Magnum",
    ".35 Winchester", ".50-110 Winchester", ".400 H&H Magnum", ".244 H&H Magnum", ".45-75 Winchester",
    ".22 Remington Automatic", ".465 H&H Magnum", ".475 No. 2 Nitro Express", ".400/350 Nitro Express",
    ".350 Rigby Magnum", ".310 Cadet", "6.5x58 mm Vergueiro",
    ".378 Weatherby Magnum", "7.5 FK", "6 mm GT",
    "6 mm PPC", "9x39 mm",
    # Share of listings (2026-11-04): under 0.05 per mille on GunBroker (1.2 million guns)
    # and at most 2 listings on any other site:
    ".22 BB Cap", ".22 Long", ".318 Westley Richards", ".38 Short Colt", ".40-65 Winchester",
    ".405 Winchester", ".44 Colt", ".45 Auto Rim", ".458 Lott", ".480 Ruger", ".470 Nitro Express",
    ".450 Nitro Express", ".500 Nitro Express", "6.5 mm Remington Magnum", "7-30 Waters",
    "7.92x33 mm Kurz", "8x64 mm S", "9.3x57 mm Mauser", "9.3x64 mm Brenneke", "5.6x57 mm",
    ".375 Weatherby Magnum", ".404 Jeffery", ".416 Ruger",
}


def is_rare(name):
    return name in RARE


def tags(name):
    """The status tags of a calibre: [], ["obsolete"], ["rare"] or ["obsolete", "rare"]."""
    return [t for t, s in (("obsolete", OBSOLETE), ("rare", RARE)) if name in s]

# The state that introduced each calibre (Raven 2026-11-06: every calibre whose origin the sources
# agree on, sporting rounds included; before that only service and regional rounds). A round keeps
# its country when it spread worldwide (9x19 mm stays German, 7.62x39 mm Soviet); the calibres in
# common use worldwide are listed separately in WORLDWIDE, so apps can show the flag, a globe or
# both. No entry means the entry is not a single cartridge, or the origin is open and listed in
# ORIGIN_UNDECIDED with its candidate states. Historical states keep their
# own code (ISO 3166-3 SU/CS where one exists, else a made-up AH/RUE that no ISO code uses, so
# RU stays today's Russia); they have no flag emoji, so apps draw their own.
COUNTRIES = {  # code: (English name, flag emoji or None)
    "CH": ("Switzerland", "🇨🇭"), "DE": ("Germany", "🇩🇪"), "AH": ("Austria-Hungary", None),
    "AT": ("Austria", "🇦🇹"), "FR": ("France", "🇫🇷"), "IT": ("Italy", "🇮🇹"),
    "GB": ("United Kingdom", "🇬🇧"), "US": ("United States", "🇺🇸"), "SE": ("Sweden", "🇸🇪"),
    "DK": ("Denmark", "🇩🇰"), "BE": ("Belgium", "🇧🇪"), "ES": ("Spain", "🇪🇸"), "PT": ("Portugal", "🇵🇹"), "CZ": ("Czechia", "🇨🇿"),
    "JP": ("Japan", "🇯🇵"), "PL": ("Poland", "🇵🇱"), "IL": ("Israel", "🇮🇱"), "FI": ("Finland", "🇫🇮"),
    "RUE": ("Russian Empire", None), "SU": ("Soviet Union", None), "CS": ("Czechoslovakia", None),
    "CN": ("China", "🇨🇳"), "PH": ("Philippines", "🇵🇭"),
}

ORIGIN = {
    ".450 No. 2 Nitro Express": "GB", ".375 Flanged Magnum Nitro Express": "GB", ".375 Flanged Nitro Express": "GB", ".55 Boys": "GB",
    "5.75 mm Velo-Dog": "FR", ".500 JRH": "US", ".45-90 WCF": "US", ".22 Extra Long": "US", ".32 Short Rimfire": "US", ".32 Long Rimfire": "US", ".360 No. 5 Rook": "GB",
    "10.3x60 mm R": "CH", "7x61 mm Sharpe & Hart": "US",
    # In common use worldwide (also in WORLDWIDE); the state that introduced them:
    ".22 Short": "US", ".22 LR": "US", ".22 WMR": "US", ".17 HMR": "US",
    "9 mm Browning kurz (.380 ACP)": "US", "9x19 mm": "DE", ".38 Special": "US",
    ".357 Magnum": "US", ".40 S&W": "US", ".44 Magnum": "US", ".45 ACP": "US",
    "5.7x28 mm": "BE", ".222 Remington": "US", ".223 Remington": "US",
    ".22-250 Remington": "US", ".22 Hornet": "US",
    ".243 Winchester": "US", "6.5 mm Creedmoor": "US", ".270 Winchester": "US",
    "7 mm Remington Magnum": "US", ".300 AAC Blackout": "US",
    "7.62x51 mm NATO": "US", ".308 Winchester": "US", ".30-06 Springfield": "US",
    ".300 Winchester Magnum": "US", ".338 Lapua Magnum": "FI",
    ".375 H&H Magnum": "GB", ".50 BMG": "US",
    # Blanks: the market whose makers standardised each; only municion.org names a country for them
    # (8 mm Knall DE, 6 mm Flobert Knall FR, 9 mm P.A.K. IT 1985), so whether blanks keep a country
    # at all is still open for Raven (thread "Verify country per cartridge", 2026-11-06).
    "9 mm P.A.K.": "DE", "8 mm Knall": "DE", ".315 Knall": "DE", "9 mm R Knall": "DE", ".320 Knall": "DE", ".45 Knall": "DE",
    ".22 Long Knall": "IT", "6 mm Flobert Knall": "FR",
    # Switzerland
    "5.6 mm GP 90": "CH", "7.5x55 mm Swiss (GP 11)": "CH", "7.5x53.5 mm Swiss (GP 1890)": "CH",
    "7.5 mm Kadettenpatrone": "CH",
    "7.5 mm Swiss Ordnance 1882": "CH", "10.4 mm Swiss Ordnance 1878": "CH",
    "10.4x38 mm R Vetterli": "CH", "18 mm Milbank-Amsler": "CH", "10.4 mm Swiss Ordnance 1872 Rimfire": "CH",
    "7.65 mm Parabellum": "CH",  # first adopted by the Swiss Army (Ordonnanzpistole 1900)
    # Soviet Union and Russian Empire
    "7.62x39 mm": "SU", "5.45x39 mm": "SU", "9x18 mm Makarov": "SU", "7.62x25 mm Tokarev": "SU",
    "5.45x18 mm": "SU", "12.7x108 mm": "SU",
    "5.8x42 mm": "CN", ".277 SIG Fury": "US",
    "7.62x54 mm R": "RUE", "7.62x38 mm R Nagant": "RUE",
    # Germany: service rounds and German hunting rounds
    "8x57 mm IS": "DE", "8x57 mm IRS": "DE", "7.92x33 mm Kurz": "DE", "7.63x25 mm Mauser": "DE",
    "11x60 mm R Mauser": "DE", "7x57 mm Mauser": "DE", "7x57 mm R": "DE", "6.5x57 mm Mauser": "DE",
    "6.5x57 mm R": "DE", "9x57 mm Mauser": "DE", "9.3x57 mm Mauser": "DE", "7x64 mm": "DE",
    "7x65 mm R": "DE", "8x64 mm S": "DE", "8x60 mm S": "DE", "8x68 mm S": "DE", "6.5x68 mm": "DE",
    "9.3x62 mm": "DE", "9.3x64 mm Brenneke": "DE", "9.3x74 mm R": "DE", "5.6x57 mm": "DE",
    "5.6x50 mm Magnum": "DE", "4.6x30 mm": "DE", ".500 Jeffery": "DE",
    # Austria-Hungary and Austria
    "8x50 mm R Mannlicher": "AH", "8 mm Roth-Steyr": "AH", "9x23 mm Steyr": "AH",
    "6.5x54 mm Mannlicher-Schönauer": "AH", "9.5x57 mm Mannlicher-Schönauer": "AH",
    "8x56 mm R Mannlicher": "AT", ".376 Steyr": "AT",
    # France
    "8x50 mm R Lebel": "FR", "7.5x54 mm French": "FR", "11x59 mm R Gras": "FR",
    "11 mm French Ordnance": "FR", "8 mm Lebel revolver": "FR", "7.65 mm Longue": "FR",
    # Italy
    "6.5x52 mm Carcano": "IT", "7.35x51 mm Carcano": "IT", "9 mm Glisenti": "IT",
    # United Kingdom: service rounds and the British African rounds
    ".303 British": "GB", ".577 Snider": "GB", ".577/450 Martini-Henry": "GB", ".455 Webley": "GB",
    ".450 Adams": "GB", ".476 Enfield": "GB", ".442 Webley": "GB", ".470 Nitro Express": "GB",
    ".416 Rigby": "GB", ".404 Jeffery": "GB", ".505 Gibbs": "GB",
    ".450 Nitro Express": "GB", ".500 Nitro Express": "GB", ".577 Nitro Express": "GB",
    ".600 Nitro Express": "GB", ".700 Nitro Express": "GB", ".500/465 Nitro Express": "GB",
    ".318 Westley Richards": "GB",
    # Others
    "6.5x55 mm Swedish": "SE", "8x58 mm R Danish Krag": "DK", "7.65x53 mm Argentine": "BE",
    "9 mm Browning Long": "BE", "9x23 mm Largo": "ES", "6.5x50 mm SR Arisaka": "JP",
    "7.7x58 mm Arisaka": "JP", "8 mm Nambu": "JP", "7.92x107 mm DS": "PL",
    "7.62x45 mm vz. 52": "CS", "9x21 mm IMI": "IL",
    "9.3x72 mm R": "DE", "8x75 mm RS": "DE", "6.5x65 mm RWS": "DE",
    ".450 Rigby": "GB", ".450/400 Nitro Express 3 inch": "GB", ".375 CheyTac": "US",
    ".40-82 WCF": "US", ".50-95 WCF": "US", ".38-56 WCF": "US", ".30 Remington": "US",
    ".17 Remington Fireball": "US", ".338 Marlin Express": "US", ".22 Nosler": "US",
    "6.5-300 Weatherby Magnum": "US",
    ".400 H&H Magnum": "GB",
    ".244 H&H Magnum": "GB",
    ".465 H&H Magnum": "GB",
    ".475 No. 2 Nitro Express": "GB",
    ".400/350 Nitro Express": "GB",
    ".350 Rigby Magnum": "GB",
    ".310 Cadet": "GB",
    "6.5x58 mm Vergueiro": "PT",
    ".30 R Blaser": "DE",
    "7.5 FK": "CZ",
    "9x39 mm": "SU",
    # United States: service rounds, then sporting, target and revolver rounds (Raven 2026-11-06)
    ".30-40 Krag": "US", ".30 Carbine": "US", ".45-70 Government": "US", ".50-70 Government": "US",
    ".17 Mach 2": "US", ".22 Long": "US", "5 mm Remington Rimfire Magnum": "US",
    ".17 Winchester Super Magnum": "US", ".22 Winchester Rimfire": "US", ".44 Henry": "US",
    ".22 Remington Automatic": "US", ".25 Stevens": "US", ".41 Short": "US", ".56-56 Spencer": "US",
    ".32 S&W Long": "US", ".32 H&R Magnum": "US", ".38 Super": "US", ".400 Cor-Bon": "US",
    "9x23 mm Winchester": "US", ".356 TSW": "US", ".22 Remington Jet": "US",
    ".256 Winchester Magnum": "US", ".41 Magnum": "US", ".44 Special": "US", "9x25 mm Dillon": "US",
    ".45 Colt": "US", ".454 Casull": "US", ".460 S&W Magnum": "US", ".500 S&W Magnum": "US",
    ".30 Super Carry": "US", ".32 S&W": "US", ".327 Federal Magnum": "US",
    ".32-20 Winchester": "US", ".38 S&W": "US", ".38 Short Colt": "US", ".38 Long Colt": "US",
    ".38-40 Winchester": "US", ".44 S&W Russian": "US", ".45 Schofield": "US", ".45 Auto Rim": "US",
    ".480 Ruger": "US", ".50 Action Express": "US", ".357 Remington Maximum": "US",
    ".41 Action Express": "US", ".45 Winchester Magnum": "US", ".45 Super": "US",
    ".460 Rowland": "US", ".475 Linebaugh": "US", ".221 Remington Fireball": "US", ".25 NAA": "US",
    ".32 NAA": "US", ".32 Long Colt": "US", ".35 S&W Auto": "US", ".38 ACP": "US",
    ".41 Long Colt": "US", ".44 Colt": "US", ".204 Ruger": "US", "6 mm ARC": "US", ".338 ARC": "US",
    "6 mm PPC": "US", "6 mm GT": "US", ".22 Creedmoor": "US", "7 mm Backcountry": "US",
    "6 mm Creedmoor": "US", ".25 Creedmoor": "US", "8.6 Blackout": "US", ".22 ARC": "US",
    ".338 Ruger Compact Magnum": "US", ".408 CheyTac": "US", ".360 Buckhammer": "US",
    ".400 Legend": "US", "6.5 PRC": "US", ".260 Remington": "US", "7 mm-08 Remington": "US",
    "7 mm PRC": "US", ".30-30 Winchester": "US", ".300 PRC": "US", ".35 Winchester": "US",
    ".50-110 Winchester": "US", ".378 Weatherby Magnum": "US", ".25-06 Remington": "US",
    ".257 Roberts": "US", ".280 Remington": "US", ".35 Whelen": "US",
    ".338 Winchester Magnum": "US", ".444 Marlin": "US", ".458 Winchester Magnum": "US",
    ".350 Legend": "US", ".375 Ruger": "US", ".450 Bushmaster": "US", "6.8 mm Remington SPC": "US",
    ".300 Winchester Short Magnum": "US", ".17 Remington": "US", ".218 Bee": "US",
    ".25-35 Winchester": "US", ".32 Winchester Special": "US", ".35 Remington": "US",
    ".38-55 Winchester": "US", ".348 Winchester": "US", ".358 Winchester": "US",
    ".264 Winchester Magnum": "US", ".300 Weatherby Magnum": "US", ".416 Remington Magnum": "US",
    ".240 Weatherby Magnum": "US", ".224 Weatherby Magnum": "US", "6.5 mm Remington Magnum": "US",
    ".220 Swift": "US", ".25-20 Winchester": "US", ".250 Savage": "US",
    ".257 Weatherby Magnum": "US", ".270 Weatherby Magnum": "US", "7 mm Weatherby Magnum": "US",
    ".340 Weatherby Magnum": "US", ".284 Winchester": "US", ".300 Savage": "US",
    ".33 Winchester": "US", ".25 Remington": "US", ".32 Remington": "US",
    ".35 Winchester Self-Loading": "US", ".351 Winchester Self-Loading": "US",
    ".401 Winchester Self-Loading": "US", ".40-65 Winchester": "US", ".303 Savage": "US",
    ".219 Zipper": "US", ".300 Remington Ultra Magnum": "US", ".270 Winchester Short Magnum": "US",
    "7 mm Winchester Short Magnum": "US", ".338 Federal": "US", "8 mm Remington Magnum": "US",
    "6.5 mm Grendel": "US", "6 mm Remington": "US", "7-30 Waters": "US", ".17 Hornet": "US",
    ".375 Winchester": "US", ".405 Winchester": "US", ".450 Marlin": "US", ".458 Lott": "US",
    ".22 Savage Hi-Power": "US", ".280 Ackley Improved": "US", ".356 Winchester": "US",
    ".307 Winchester": "US", ".416 Ruger": "US", ".416 Weatherby Magnum": "US",
    ".375 Remington Ultra Magnum": "US", "7 mm STW": "US", ".225 Winchester": "US",
    ".223 WSSM": "US", ".243 WSSM": "US", ".25 WSSM": "US", ".350 Remington Magnum": "US",
    ".338-378 Weatherby Magnum": "US", "6.8 Western": "US", "7 mm Remington SAUM": "US",
    ".26 Nosler": "US", ".27 Nosler": "US", ".28 Nosler": "US", ".30 Nosler": "US",
    ".33 Nosler": "US", ".300 Ruger Compact Magnum": "US", ".30 Thompson/Center": "US",
    ".30 Remington AR": "US", ".308 Marlin Express": "US", ".300 Remington SAUM": "US",
    ".224 Valkyrie": "US", ".458 SOCOM": "US", ".50 Beowulf": "US", ".222 Remington Magnum": "US",
    ".30-378 Weatherby Magnum": "US", ".338 Remington Ultra Magnum": "US",
    "7 mm Remington Ultra Magnum": "US", ".325 Winchester Short Magnum": "US",
    ".375 Weatherby Magnum": "US", ".460 Weatherby Magnum": "US", ".416 Barrett": "US",
    ".44-40 WCF": "US", ".32-40 Ballard": "US", ".50-90 Sharps": "US", ".45-75 Winchester": "US",
    ".300 HAM'R": "US", ".25 Weatherby RPM": "US", "6.5 Weatherby RPM": "US", ".338 Weatherby RPM": "US",
    # France
    ".22 BB Cap": "FR", "9 mm Flobert Bosquette": "FR",
    # Germany
    # Genschow (Durlach) designed it in 1936 for the Luftwaffe, the year INTRODUCED gives, and Wikipedia says
    # Germany; Hirtenberger (AT) only revived it in 1972 for the Walther PP Super, so AT is not a candidate.
    "9x18 mm Ultra": "DE",
    ".300 Blaser Magnum": "DE", ".375 Blaser Magnum": "DE",
    "7 mm Blaser Magnum": "DE", ".338 Blaser Magnum": "DE", "8.5x55 mm Blaser": "DE",
    # Austria-Hungary
    "6.5x53 mm R Mannlicher": "AH",
    # United Kingdom
    ".320 Revolver": "GB",
    ".300 H&H Magnum": "GB",
    # Finland
    "6.5x47 mm Lapua": "FI", ".300 Lapua Magnum": "FI", "9.3x53 mm R Finnish": "FI",
    "9.3x66 mm Sako (.370 Sako Magnum)": "FI",
    # Sweden
    ".300 Norma Magnum": "SE", ".308 Norma Magnum": "SE",
    ".338 Norma Magnum": "SE",  # developed by Norma with Jimmie Sloan (US) as a new round; both sources say Sweden
    ".358 Norma Magnum": "SE",
}

# Calibres two states can claim; neither is in ORIGIN until Raven decides (thread "Verify country per
# cartridge", 2026-11-06). The tuple lists the candidates, the likelier one first.
ORIGIN_UNDECIDED = {
    "6.35 mm Browning (.25 ACP)": ("BE", "US"),  # Browning design, first made and sold by FN Herstal 1905/06, Colt 1908
    "7.65 mm Browning (.32 ACP)": ("BE", "US"),  # Browning design, introduced by FN Herstal 1899 for the FN M1900
    "5.56x45 mm NATO": ("US", "BE"),  # US .223/M193 of 1963 became the NATO round; the NATO SS109 load of 1980 is Belgian (FN)
    "10 mm Auto": ("US", "SE"),  # designed in the US (Cooper, Dornaus & Dixon) 1983, first loaded by Norma
    ".357 SIG": ("US", "CH"),  # SIGARMS (Exeter NH) with Federal 1994
    ".45 GAP": ("US", "AT"),  # CCI/Speer design 2003 at Glock's request
    ".22 TCM": ("PH", "US"),  # Armscor (Philippines) with Fred Craig (US)
    "6 mm BR Norma": ("SE", "US"),  # Norma standardised the US 6mm BR Remington wildcat 1996
    "6.5-284 Norma": ("SE", "US"),  # Norma standardised the US 6.5-284 wildcat
    ".500/416 Nitro Express": ("DE", "US"),  # Krieghoff (Ulm) with Hornady, 2000s; only municion.org names a country
    ".32 S&W Long Wadcutter": ("DE", "FI"),  # the C.I.P. sheet gives "DE/FI"
}

# Calibres in common use worldwide (Raven 2026-11-04); independent of ORIGIN (Raven 2026-11-07: show the
# country as well, so 9x19 mm is German and worldwide). Includes the generic gauges and pellet sizes.
WORLDWIDE = frozenset({
    ".22 Short", ".22 LR", ".22 WMR", ".17 HMR", "6.35 mm Browning (.25 ACP)", "7.65 mm Browning (.32 ACP)",
    "9 mm Browning kurz (.380 ACP)", "9x19 mm", ".38 Special", ".357 Magnum", ".40 S&W", ".44 Magnum", ".45 ACP",
    "5.7x28 mm", ".222 Remington", ".223 Remington", "5.56x45 mm NATO", ".22-250 Remington", ".22 Hornet",
    ".243 Winchester", "6.5 mm Creedmoor", ".270 Winchester", "7 mm Remington Magnum", ".300 AAC Blackout",
    "7.62x51 mm NATO", ".308 Winchester", ".30-06 Springfield", ".300 Winchester Magnum", ".338 Lapua Magnum",
    ".375 H&H Magnum", ".50 BMG", "12/70", "12/76", "20/70", "20/76", "4.5 mm Diabolo (.177)", "5.5 mm Diabolo (.22)",
    "4.4 mm Stahl-BB (.177 BB)", "6 mm Airsoft-BB", "8 mm Airsoft-BB",
})


def origin(name):
    """(code, English name, flag emoji or None) of the state that introduced a calibre, or None (not a
    single cartridge, or still open in ORIGIN_UNDECIDED, see origin_candidates). Worldwide use is
    separate: is_worldwide."""
    code = ORIGIN.get(name)
    return (code, *COUNTRIES[code]) if code else None


def origin_candidates(name):
    """The states that can claim a calibre whose origin is still open, likelier first, as
    (code, English name, flag emoji or None) tuples; () when origin() answers or nothing is known."""
    return tuple((code, *COUNTRIES[code]) for code in ORIGIN_UNDECIDED.get(name, ()))


def is_worldwide(name):
    """True for a calibre in common use worldwide (WORLDWIDE); independent of origin()."""
    return name in WORLDWIDE


# Bullet the cartridge was first sold with (Raven 2026-11-05: draw the original bullet, soft points
# with their lead tip). Calibres not listed here had a full metal jacket (or another all-copper bullet).
# LEAD: bare lead, also lubricated or wax coated. PAPER_PATCHED: lead bullet wrapped in paper below
# the nose. SOFT_POINT: copper jacket with the lead core showing at the tip (hunting rounds).
# POLYMER_TIP: copper jacket with a plastic tip (V-Max, ELD, FTX, SST, AccuBond; Raven 2026-11-05).
# The GP 1890 steel cap is its own profile (PATCHED) and not listed.
JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP = "jacketed", "lead", "paper", "softpoint", "polymer"
BULLETS = {  # name: (bullet, source that names the original or factory bullet)
    ".22 Short": (LEAD, "https://en.wikipedia.org/wiki/.22_Short"),
    ".22 LR": (LEAD, "https://en.wikipedia.org/wiki/.22_Long_Rifle"),
    ".22 Long": (LEAD, "https://en.wikipedia.org/wiki/.22_Long"),
    ".22 Extra Long": (LEAD, "https://municion.org/producto/22-extra-long-rf-us/"),
    ".32 Short Rimfire": (LEAD, "https://municion.org/producto/32-short-rf/"),
    ".32 Long Rimfire": (LEAD, "https://municion.org/producto/32-long-rf/"),
    ".22 BB Cap": (LEAD, "https://en.wikipedia.org/wiki/.22_BB"),
    "9 mm Flobert Bosquette": (LEAD, "https://en.wikipedia.org/wiki/9_mm_Flobert_Bosquette"),  # a 00 buckshot ball
    ".320 Revolver": (LEAD, "https://en.wikipedia.org/wiki/.320_Revolver"),  # "80 gr (5 g) Lead"
    ".22 Winchester Rimfire": (LEAD, "https://en.wikipedia.org/wiki/.22_Winchester_Rimfire"),
    ".44 Henry": (LEAD, "https://en.wikipedia.org/wiki/.44_Henry"),
    ".25 Stevens": (LEAD, "https://municion.org/producto/25-stevens-short-rf/"),
    ".41 Short": (LEAD, "https://en.wikipedia.org/wiki/.41_Short"),
    ".56-56 Spencer": (LEAD, "https://municion.org/producto/56-56-spencer-rf/"),
    "10.4 mm Swiss Ordnance 1872 Rimfire": (LEAD, "https://municion.org/producto/104-mm-swiss-rf-m-1872/"),
    "18 mm Milbank-Amsler": (LEAD, "https://municion.org/producto/18-x-257-r-rf-milbank-amsler/"),
    ".22 Remington Automatic": (LEAD, "https://en.wikipedia.org/wiki/.22_Remington_Automatic"),
    ".32 S&W": (LEAD, "https://en.wikipedia.org/wiki/.32_S%26W"),
    ".32 S&W Long": (LEAD, "https://en.wikipedia.org/wiki/.32_S%26W_Long"),
    ".32 S&W Long Wadcutter": (LEAD, "https://www.lapua.com/product/32-sw-lapua-wadcutter-bullet-c427-535-g-83-gr/"),
    ".32 Long Colt": (LEAD, "https://en.wikipedia.org/wiki/.32_Long_Colt"),
    ".38 S&W": (LEAD, "https://en.wikipedia.org/wiki/.38_S%26W"),
    ".38 Short Colt": (LEAD, "https://municion.org/producto/38-short-colt-long-case/"),
    ".38 Long Colt": (LEAD, "https://en.wikipedia.org/wiki/.38_Long_Colt"),
    ".38 Special": (LEAD, "https://en.wikipedia.org/wiki/.38_Special"),
    ".38-40 Winchester": (LEAD, "https://en.wikipedia.org/wiki/.38-40_Winchester"),
    ".41 Long Colt": (LEAD, "https://en.wikipedia.org/wiki/.41_Long_Colt"),
    ".44 S&W Russian": (LEAD, "https://en.wikipedia.org/wiki/.44_S%26W_Russian"),
    ".44 Colt": (LEAD, "https://municion.org/producto/44-colt-remington-army-revolver/"),
    ".44 Special": (LEAD, "https://en.wikipedia.org/wiki/.44_Special"),
    ".44 Magnum": (LEAD, "https://en.wikipedia.org/wiki/.44_Magnum"),
    ".45 Colt": (LEAD, "https://en.wikipedia.org/wiki/.45_Colt"),
    ".45 Schofield": (LEAD, "https://municion.org/producto/45-smith-wesson-schofield/"),
    ".45 Auto Rim": (LEAD, "https://en.wikipedia.org/wiki/.45_Auto_Rim"),
    ".442 Webley": (LEAD, "https://en.wikipedia.org/wiki/.442_Webley"),
    ".450 Adams": (LEAD, "https://en.wikipedia.org/wiki/.450_Adams"),
    ".455 Webley": (LEAD, "https://en.wikipedia.org/wiki/.455_Webley"),
    ".476 Enfield": (LEAD, "https://en.wikipedia.org/wiki/.476_Enfield"),
    "11 mm French Ordnance": (LEAD, "https://en.wikipedia.org/wiki/11mm_French_Ordnance"),
    "10.4 mm Swiss Ordnance 1878": (LEAD, "https://en.wikipedia.org/wiki/10.4mm_Swiss_Centerfire"),
    ".357 Magnum": (LEAD, "https://en.wikipedia.org/wiki/.357_Magnum"),
    ".32-20 Winchester": (LEAD, "https://en.wikipedia.org/wiki/.32-20_Winchester"),
    ".577 Snider": (LEAD, "https://en.wikipedia.org/wiki/.577_Snider"),
    ".50-70 Government": (LEAD, "https://en.wikipedia.org/wiki/.50-70_Government"),
    ".45-70 Government": (LEAD, "https://en.wikipedia.org/wiki/.45-70"),
    ".50-90 Sharps": (LEAD, "https://en.wikipedia.org/wiki/.50-90_Sharps"),
    ".45-75 Winchester": (LEAD, "https://en.wikipedia.org/wiki/.45-75_Winchester"),
    ".44-40 WCF": (LEAD, "https://en.wikipedia.org/wiki/.44-40_Winchester"),
    ".32-40 Ballard": (LEAD, "https://en.wikipedia.org/wiki/.32-40_Ballard"),
    ".40-65 Winchester": (LEAD, "https://municion.org/producto/40-65-winchester-cf/"),
    ".40-82 WCF": (LEAD, "https://municion.org/producto/40-82-260-winchester-cf-marlin/"),
    ".38-55 Winchester": (LEAD, "https://en.wikipedia.org/wiki/.38-55_Winchester"),
    ".38-56 WCF": (LEAD, "https://en.wikipedia.org/wiki/.38-56_WCF"),
    ".45-90 WCF": (LEAD, "https://municion.org/producto/45-90-300-winchester-cf/"),
    ".50-95 WCF": (LEAD, "https://municion.org/producto/50-95-300-winchester/"),
    ".50-110 Winchester": (LEAD, "https://municion.org/producto/50-110-300-winchester-express/"),
    ".25-20 Winchester": (LEAD, "https://en.wikipedia.org/wiki/.25-20_Winchester"),
    ".310 Cadet": (LEAD, "https://municion.org/producto/310-cadet-single-shot/"),
    ".360 No. 5 Rook": (LEAD, "https://en.wikipedia.org/wiki/.360_No._5_Rook"),
    ".577/450 Martini-Henry": (PAPER_PATCHED, "https://en.wikipedia.org/wiki/.577/450_Martini–Henry"),
    "11x59 mm R Gras": (PAPER_PATCHED, "https://en.wikipedia.org/wiki/11×59mmR_Gras"),
    "11x60 mm R Mauser": (PAPER_PATCHED, "https://en.wikipedia.org/wiki/11×60mm_Mauser"),
    "10.4x38 mm R Vetterli": (PAPER_PATCHED, "https://en.wikipedia.org/wiki/.41_Swiss"),
    ".22 Hornet": (SOFT_POINT, "https://en.wikipedia.org/wiki/.22_Hornet"),
    ".218 Bee": (SOFT_POINT, "https://en.wikipedia.org/wiki/.218_Bee"),
    ".219 Zipper": (SOFT_POINT, "https://en.wikipedia.org/wiki/.219_Zipper"),
    ".220 Swift": (SOFT_POINT, "https://en.wikipedia.org/wiki/.220_Swift"),
    ".222 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/.222_Remington"),
    ".222 Remington Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.222_Remington_Magnum"),
    ".225 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.225_Winchester"),
    ".22-250 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/.22-250_Remington"),
    ".224 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.224_Weatherby_Magnum"),
    ".22 Savage Hi-Power": (SOFT_POINT, "https://municion.org/producto/22-savage-hi-power/"),
    ".221 Remington Fireball": (SOFT_POINT, "https://en.wikipedia.org/wiki/.221_Remington_Fireball"),
    ".22 Remington Jet": (SOFT_POINT, "https://en.wikipedia.org/wiki/.22_Remington_Jet"),
    ".243 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.243_Winchester"),
    "6 mm Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/6mm_Remington"),
    ".240 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.240_Weatherby_Magnum"),
    ".223 WSSM": (SOFT_POINT, "https://en.wikipedia.org/wiki/.223_Winchester_Super_Short_Magnum"),
    ".243 WSSM": (SOFT_POINT, "https://en.wikipedia.org/wiki/.243_Winchester_Super_Short_Magnum"),
    ".25 WSSM": (SOFT_POINT, "https://en.wikipedia.org/wiki/Winchester_Super_Short_Magnum"),
    ".250 Savage": (SOFT_POINT, "https://en.wikipedia.org/wiki/.250-3000_Savage"),
    ".257 Roberts": (SOFT_POINT, "https://en.wikipedia.org/wiki/.257_Roberts"),
    ".25-06 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/.25-06_Remington"),
    ".257 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.257_Weatherby_Magnum"),
    ".25-35 Winchester": (SOFT_POINT, "https://municion.org/producto/25-35-winchester-cf/"),
    ".25 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/.25_Remington"),
    ".264 Winchester Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.264_Winchester_Magnum"),
    "5.6x50 mm Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/5.6×50mm_Magnum"),
    "5.6x57 mm": (SOFT_POINT, "https://en.wikipedia.org/wiki/5.6×57mm"),
    "6.5x57 mm Mauser": (SOFT_POINT, "https://en.wikipedia.org/wiki/6.5×57mm_Mauser"),
    "6.5x57 mm R": (SOFT_POINT, "https://municion.org/producto/65-x-57-r-mauser-m88/"),
    "6.5x65 mm RWS": (SOFT_POINT, "https://municion.org/producto/65-x-65-rws/"),
    "6.5x68 mm": (SOFT_POINT, "https://en.wikipedia.org/wiki/6.5×68mm"),
    "6.5 mm Remington Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/6.5mm_Remington_Magnum"),
    ".260 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/.260_Remington"),
    "6.5-300 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/6.5-300_Weatherby_Magnum"),
    ".270 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.270_Winchester"),
    ".270 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.270_Weatherby_Magnum"),
    ".270 Winchester Short Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.270_Winchester_Short_Magnum"),
    "7x64 mm": (SOFT_POINT, "https://en.wikipedia.org/wiki/7×64mm"),
    "7x65 mm R": (SOFT_POINT, "https://en.wikipedia.org/wiki/7×64mm"),
    "7x57 mm R": (SOFT_POINT, "https://municion.org/producto/7-x-57-r-mauser/"),
    "7x61 mm Sharpe & Hart": (SOFT_POINT, "https://en.wikipedia.org/wiki/7%C3%9761mm_Sharpe_%26_Hart"),
    "7 mm Remington Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/7mm_Remington_Magnum"),
    "7 mm Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/7mm_Weatherby_Magnum"),
    "7 mm-08 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/7mm-08_Remington"),
    ".280 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/.280_Remington"),
    ".284 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.284_Winchester"),
    "7 mm STW": (SOFT_POINT, "https://en.wikipedia.org/wiki/7mm_STW"),
    "7 mm Winchester Short Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/7mm_Winchester_Short_Magnum"),
    "7 mm Remington SAUM": (SOFT_POINT, "https://en.wikipedia.org/wiki/7mm_Remington_Short_Action_Ultra_Magnum"),
    "7 mm Remington Ultra Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/7mm_Remington_Ultra_Magnum"),
    "7-30 Waters": (SOFT_POINT, "https://en.wikipedia.org/wiki/7-30_Waters"),
    ".30-30 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.30-30_Winchester"),
    ".30 Remington": (SOFT_POINT, "https://municion.org/producto/30-remington/"),
    ".30 Remington AR": (SOFT_POINT, "https://en.wikipedia.org/wiki/.30_Remington_AR"),
    ".32 Winchester Special": (SOFT_POINT, "https://municion.org/producto/32-winchester-cf-special/"),
    ".32 Remington": (SOFT_POINT, "https://municion.org/producto/32-remington/"),
    ".300 Savage": (SOFT_POINT, "https://en.wikipedia.org/wiki/.300_Savage"),
    ".303 Savage": (SOFT_POINT, "https://municion.org/producto/303-savage/"),
    ".307 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.307_Winchester"),
    ".308 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.308_Winchester"),
    ".300 H&H Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.300_H%26H_Magnum"),
    ".300 Winchester Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.300_Winchester_Magnum"),
    ".300 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.300_Weatherby_Magnum"),
    ".308 Norma Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.308_Norma_Magnum"),
    ".30-378 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.30-378_Weatherby_Magnum"),
    ".300 Winchester Short Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.300_Winchester_Short_Magnum"),
    ".300 Remington Ultra Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.300_Remington_Ultra_Magnum"),
    ".300 Remington SAUM": (SOFT_POINT, "https://en.wikipedia.org/wiki/.300_Remington_Short_Action_Ultra_Magnum"),
    ".30 R Blaser": (SOFT_POINT, "https://en.wikipedia.org/wiki/.30_R_Blaser"),
    "8x57 mm IRS": (SOFT_POINT, "https://municion.org/producto/8-x-57-r-jrs-mauser/"),
    "8x60 mm S": (SOFT_POINT, "https://municion.org/producto/8-x-60-s/"),
    "8x64 mm S": (SOFT_POINT, "https://en.wikipedia.org/wiki/8×64mm_S"),
    "8x68 mm S": (SOFT_POINT, "https://en.wikipedia.org/wiki/8×68mm_S"),
    "8x75 mm RS": (SOFT_POINT, "https://municion.org/producto/8-x-75-r-behr/"),
    "8 mm Remington Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/8mm_Remington_Magnum"),
    ".318 Westley Richards": (SOFT_POINT, "https://municion.org/producto/318-westley-richards-rimless-nitro-express/"),
    ".33 Winchester": (SOFT_POINT, "https://municion.org/producto/33-winchester-cf/"),
    ".338 Winchester Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.338_Winchester_Magnum"),
    ".340 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.340_Weatherby_Magnum"),
    ".338-378 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.338-378_Weatherby_Magnum"),
    ".338 Remington Ultra Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.338_Remington_Ultra_Magnum"),
    ".348 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.348_Winchester"),
    ".35 Remington": (SOFT_POINT, "https://en.wikipedia.org/wiki/.35_Remington"),
    ".35 Whelen": (SOFT_POINT, "https://en.wikipedia.org/wiki/.35_Whelen"),
    ".358 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.358_Winchester"),
    ".356 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.356_Winchester"),
    ".35 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.35_Winchester"),
    ".350 Remington Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.350_Remington_Magnum"),
    ".358 Norma Magnum": (SOFT_POINT, "https://municion.org/producto/358-norma-magnum-belted/"),
    ".350 Rigby Magnum": (SOFT_POINT, "https://municion.org/producto/350-rigby-magnum-ne/"),
    ".350 Legend": (SOFT_POINT, "https://en.wikipedia.org/wiki/.350_Legend"),
    ".360 Buckhammer": (SOFT_POINT, "https://en.wikipedia.org/wiki/.360_Buckhammer"),
    ".35 Winchester Self-Loading": (SOFT_POINT, "https://municion.org/producto/35-winchester-self-loading/"),
    ".351 Winchester Self-Loading": (SOFT_POINT, "https://municion.org/producto/351-winchester-semi-rimmed-self-loading/"),
    ".401 Winchester Self-Loading": (SOFT_POINT, "https://municion.org/producto/401-winchester-self-loading/"),
    ".375 H&H Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.375_H%26H_Magnum"),
    ".375 Flanged Magnum Nitro Express": (SOFT_POINT, "https://municion.org/producto/375-holland-holland-flanged-magnum-ne/"),
    ".375 Flanged Nitro Express": (SOFT_POINT, "https://municion.org/producto/375-flanged-nitro-express/"),
    ".375 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.375_Winchester"),
    ".375 Ruger": (SOFT_POINT, "https://en.wikipedia.org/wiki/.375_Ruger"),
    ".375 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.375_Weatherby_Magnum"),
    ".375 Remington Ultra Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.375_Remington_Ultra_Magnum"),
    ".376 Steyr": (SOFT_POINT, "https://en.wikipedia.org/wiki/.376_Steyr"),
    ".378 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.378_Weatherby_Magnum"),
    "9.3x57 mm Mauser": (SOFT_POINT, "https://en.wikipedia.org/wiki/9.3×57mm_Mauser"),
    "9.3x62 mm": (SOFT_POINT, "https://en.wikipedia.org/wiki/9.3×62mm"),
    "9.3x64 mm Brenneke": (SOFT_POINT, "https://en.wikipedia.org/wiki/9.3×64mm_Brenneke"),
    "9.3x72 mm R": (SOFT_POINT, "https://municion.org/producto/93-x-72-r/"),
    "9.3x74 mm R": (SOFT_POINT, "https://en.wikipedia.org/wiki/9.3×74mmR"),
    "9.3x53 mm R Finnish": (SOFT_POINT, "https://municion.org/producto/93-x-53-r-finnish/"),
    "9x57 mm Mauser": (SOFT_POINT, "https://municion.org/producto/9-x-57-mauser/"),
    "9.5x57 mm Mannlicher-Schönauer": (SOFT_POINT, "https://en.wikipedia.org/wiki/9.5×57mm_Mannlicher–Schönauer"),
    "10.3x60 mm R": (SOFT_POINT, "https://municion.org/producto/103-x-60-r/"),
    ".400/350 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.400/350_Nitro_Express"),
    ".400 H&H Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.400_H%26H_Magnum"),
    ".400 Legend": (SOFT_POINT, "https://en.wikipedia.org/wiki/.400_Legend"),
    ".404 Jeffery": (SOFT_POINT, "https://en.wikipedia.org/wiki/.404_Jeffery"),
    ".405 Winchester": (SOFT_POINT, "https://en.wikipedia.org/wiki/.405_Winchester"),
    ".416 Rigby": (SOFT_POINT, "https://municion.org/producto/416-rigby-magnum-nitro-express-2-7-8/"),
    ".416 Remington Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.416_Remington_Magnum"),
    ".416 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.416_Weatherby_Magnum"),
    ".416 Ruger": (SOFT_POINT, "https://en.wikipedia.org/wiki/.416_Ruger"),
    ".444 Marlin": (SOFT_POINT, "https://en.wikipedia.org/wiki/.444_Marlin"),
    ".450 Marlin": (SOFT_POINT, "https://en.wikipedia.org/wiki/.450_Marlin"),
    ".458 Winchester Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.458_Winchester_Magnum"),
    ".458 Lott": (SOFT_POINT, "https://en.wikipedia.org/wiki/.458_Lott"),
    ".460 Weatherby Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.460_Weatherby_Magnum"),
    ".465 H&H Magnum": (SOFT_POINT, "https://en.wikipedia.org/wiki/.465_H%26H_Magnum"),
    ".450 Rigby": (SOFT_POINT, "https://en.wikipedia.org/wiki/.450_Rigby"),
    ".450 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.450_Nitro_Express"),
    ".450 No. 2 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.450_No_2_Nitro_Express"),
    ".450/400 Nitro Express 3 inch": (SOFT_POINT, "https://en.wikipedia.org/wiki/.450/400_Nitro_Express"),
    ".470 Nitro Express": (SOFT_POINT, "https://municion.org/producto/470-nitro-express/"),
    ".475 No. 2 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.475_No._2_Nitro_Express"),
    ".500/465 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.500/465_Nitro_Express"),
    ".500/416 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.500/416_Nitro_Express"),
    ".500 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.500_Nitro_Express"),
    ".505 Gibbs": (SOFT_POINT, "https://en.wikipedia.org/wiki/.505_Gibbs"),
    ".500 Jeffery": (SOFT_POINT, "https://en.wikipedia.org/wiki/.500_Jeffery"),
    ".577 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.577_Nitro_Express"),
    ".600 Nitro Express": (SOFT_POINT, "https://municion.org/producto/600-nitro-express-3/"),
    ".700 Nitro Express": (SOFT_POINT, "https://en.wikipedia.org/wiki/.700_Nitro_Express"),
    ".17 HMR": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.17_Hornady_Magnum_Rimfire"),
    ".17 Mach 2": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.17_Hornady_Mach_2"),
    ".17 Winchester Super Magnum": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.17_Winchester_Super_Magnum"),
    ".204 Ruger": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.204_Ruger"),
    ".17 Remington Fireball": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.17_Remington_Fireball"),
    ".17 Hornet": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.17_Hornet"),
    "6.5 mm Creedmoor": (POLYMER_TIP, "https://en.wikipedia.org/wiki/6.5mm_Creedmoor"),
    "6.5 PRC": (POLYMER_TIP, "https://en.wikipedia.org/wiki/6.5_PRC"),
    "7 mm PRC": (POLYMER_TIP, "https://en.wikipedia.org/wiki/7mm_PRC"),
    ".300 PRC": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.300_PRC"),
    ".22 ARC": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.22_ARC"),
    "6 mm ARC": (POLYMER_TIP, "https://en.wikipedia.org/wiki/6mm_ARC"),
    ".22 Creedmoor": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.22_Creedmoor"),
    ".308 Marlin Express": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.308_Marlin_Express"),
    ".338 Marlin Express": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.338_Marlin_Express"),
    ".30 Thompson/Center": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.30_Thompson_Center"),
    ".338 Ruger Compact Magnum": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.338_Ruger_Compact_Magnum"),
    ".325 Winchester Short Magnum": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.325_WSM"),
    ".26 Nosler": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.26_Nosler"),
    ".27 Nosler": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.28_Nosler"),
    ".28 Nosler": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.28_Nosler"),
    ".30 Nosler": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.30_Nosler"),
    ".33 Nosler": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.28_Nosler"),
    "6.8 Western": (POLYMER_TIP, "https://en.wikipedia.org/wiki/6.8_Western"),
    ".450 Bushmaster": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.450_Bushmaster"),
    "7 mm Backcountry": (POLYMER_TIP, "https://en.wikipedia.org/wiki/7mm_Backcountry"),
    ".338 Federal": (POLYMER_TIP, "https://en.wikipedia.org/wiki/.338_Federal"),
    "7 mm Blaser Magnum": (SOFT_POINT, None),
    ".300 Blaser Magnum": (SOFT_POINT, None),
    "8.5x55 mm Blaser": (SOFT_POINT, None),
    ".338 Blaser Magnum": (SOFT_POINT, None),
    ".375 Blaser Magnum": (SOFT_POINT, None),
    "9.3x66 mm Sako (.370 Sako Magnum)": (SOFT_POINT, None),
}
# Hunting rounds whose sources (C.I.P. sheets) give no bullet: soft point from their use, not checked.
BULLET_INFERRED = {name for name, (_, url) in BULLETS.items() if url is None}


def bullet(name):
    """The original bullet of a calibre: JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT or POLYMER_TIP."""
    return BULLETS.get(name, (JACKETED, None))[0]


# Case material of the original cartridge where it was not brass (Raven 2026-11-05).
# PAPER: brass foil covered in paper, on a brass head (Boxer's Snider case). HYBRID: brass body on a steel head.
BRASS, COPPER, STEEL, NICKEL, PAPER, HYBRID = "brass", "copper", "steel", "nickel", "paper", "hybrid"
CASES = {  # name: (material, source)
    ".44 Henry": (COPPER, "https://en.wikipedia.org/wiki/.44_Henry"),
    ".56-56 Spencer": (COPPER, "https://municion.org/producto/56-56-spencer-rf/"),
    "10.4 mm Swiss Ordnance 1872 Rimfire": (COPPER, "https://municion.org/producto/104-mm-swiss-rf-m-1872/"),
    "10.4x38 mm R Vetterli": (COPPER, "https://en.wikipedia.org/wiki/.41_Swiss"),
    ".45-70 Government": (COPPER, "https://en.wikipedia.org/wiki/.45-70"),
    ".50-70 Government": (COPPER, "https://en.wikipedia.org/wiki/.45-70"),
    ".45 Schofield": (COPPER, "https://municion.org/producto/45-smith-wesson-schofield/"),
    ".577 Snider": (PAPER, "https://en.wikipedia.org/wiki/.577_Snider"),
    # Lacquered steel: 5.45x39 from the start; 7.62x39 since the early 1960s (bimetal before).
    "5.45x39 mm": (STEEL, "https://en.wikipedia.org/wiki/5.45%C3%9739mm"),
    "7.62x39 mm": (STEEL, "https://en.wikipedia.org/wiki/7.62%C3%9739mm"),
    # Brass body on a stainless steel head, held by an aluminium washer.
    ".277 SIG Fury": (HYBRID, "https://en.wikipedia.org/wiki/.277_Fury"),
    # Nickel-plated steel case (Federal).
    "7 mm Backcountry": (NICKEL, "https://en.wikipedia.org/wiki/7mm_Backcountry"),
}


def case_material(name):
    """What the case is made of: BRASS, COPPER, STEEL, NICKEL, PAPER or HYBRID."""
    return CASES.get(name, (BRASS, None))[0]


_STARLINE = "https://www.starlinebrass.com/"
_BARNAUL = "https://en.wikipedia.org/wiki/Barnaul_Cartridge_Plant"
CURRENT_CASES = {  # name: (other case materials made today, source); the original in CASES stays the drawn one
    ".45-70 Government": ((BRASS,), _STARLINE + "45-70-govt-brass"),
    ".50-70 Government": ((BRASS,), _STARLINE + "50-70-govt-brass"),
    ".45 Schofield": ((BRASS,), _STARLINE + "45-sw-schofield-brass"),
    ".577 Snider": ((BRASS,), "https://en.wikipedia.org/wiki/.577_Snider"),  # Kynamco, Bertram
    "7.62x39 mm": ((BRASS,), _STARLINE + "762x39mm-russian"),
    ".277 SIG Fury": ((BRASS,), "https://en.wikipedia.org/wiki/.277_Fury"),  # brass "practice" loads
    # Barnaul's lacquered, zinc- or polymer-coated steel cases.
    "9x19 mm": ((STEEL,), _BARNAUL),
    "9x18 mm Makarov": ((STEEL,), _BARNAUL),
    ".45 ACP": ((STEEL,), _BARNAUL),
    "5.56x45 mm NATO": ((STEEL,), _BARNAUL),
    ".223 Remington": ((STEEL,), _BARNAUL),
    "6.5 mm Grendel": ((STEEL,), _BARNAUL),
    ".243 Winchester": ((STEEL,), _BARNAUL),
    "7.62x51 mm NATO": ((STEEL,), _BARNAUL),
    ".308 Winchester": ((STEEL,), _BARNAUL),
    "7.62x54 mm R": ((STEEL,), _BARNAUL),
    ".30-06 Springfield": ((STEEL,), _BARNAUL),
    "9.3x64 mm Brenneke": ((STEEL,), _BARNAUL),
}


def current_case_materials(name):
    """Case materials made today besides the original one, e.g. (BRASS,) for the .45-70."""
    return CURRENT_CASES.get(name, ((), None))[0]


# Loose projectiles (balls, Minié bullets, pellets) not made of lead (Raven 2026-11-05: steel BBs
# and airsoft BBs). Not listed means lead.
PLASTIC = "plastic"
_BB = "https://en.wikipedia.org/wiki/BB_gun"
_AIRSOFT = "https://en.wikipedia.org/wiki/Airsoft_pellets"
LOOSE_MATERIALS = {  # name: (material, source)
    "4.4 mm Stahl-BB (.177 BB)": (STEEL, _BB),  # 0.171-0.173 in, zinc or copper plated
    "6 mm Airsoft-BB": (PLASTIC, _AIRSOFT),
    "8 mm Airsoft-BB": (PLASTIC, _AIRSOFT),
}


def loose_material(name):
    """What a ball, Minié bullet or pellet is made of: LEAD, STEEL or PLASTIC."""
    return LOOSE_MATERIALS.get(name, (LEAD, None))[0]
