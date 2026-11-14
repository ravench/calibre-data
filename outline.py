"""Side-view outlines of the catalogue cartridges, shared by both apps and the poster.

outline(spec) returns {"width", "height", "case"?, "head"?, "bullet"?, "patch"?, "tip"?, "bulletMaterial"?,
"tipMaterial"?, "caseMaterial"?, "headMaterial"?, "currentCaseMaterials"?}:
millimetres, SVG path data (M/L/Z only), tip at the top (y = 0), base at the bottom
(y = overall length), centred in `width`.
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cartridges import CATALOGUE, shoulder_angle, case_head, rim_thickness, unsourced, SHOULDER_ANGLES, RIMLESS, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET, SPITZER, ROUND, FLAT, PATCHED, CRIMPED, BALL_NOSE  # noqa: E402
from cartridges import LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, HOLLOW_POINT, STEEL, BRASS, COPPER, HYBRID, PAPER, bullet, jacket, patch_length, case_material, current_case_materials, loose_material  # noqa: E402

N = 14  # samples per curve
# mm, groove floor where no source gives its length: belted cases (as drawn on the C.I.P. sheets) and
# generic heads (the sourced rimless floors: median 0.95)
GROOVE_FLOOR = 1.0
# mm, rim thickness of a case whose [case_head] gives none: rimmed, rimfire, rimless, semi-rimmed or belted
RIMMED_RIM, RIMFIRE_RIM, RIMLESS_RIM = 1.5, 1.1, 1.3
# Head of a rimless, semi-rimmed or belted case whose [case_head] gives no groove, fitted to the sourced ones
# (generic_head). The groove's diameter is a share of the rim's (their median: 0.869; half of them lie between
# 0.86 and 0.89): the extractor grips the rim, so the groove stays below a rebated rim too. It is at most a
# share of the base's, which keeps it below the body of a semi-rimmed case (their median: 0.898).
GENERIC_GROOVE, GENERIC_GROOVE_OF_BASE = 0.87, 0.9
# The ramp's angle to the case axis in degrees: one for every size and kind (their median: 36; behind the
# 1 mm floor, 40 puts the ramp's top closest to theirs, and angles by size or kind come no closer). On a
# belted case, the distance from the rim's front to the belt's front (their median: 4.32 mm, the H&H belt).
GENERIC_RAMP, GENERIC_BELT = 40.0, 4.3


def ramp_run(groove, outer, angle):
    """Length along the axis of the ramp from a groove out to `outer` (diameters), `angle` degrees to the axis."""
    return (outer - groove) / 2 / math.tan(math.radians(angle))


def generic_head(s):
    """(rim thickness, ramp top or belt front, groove diameter, ramp angle) like cartridges.case_head, for a
    rimless, semi-rimmed or belted case without one: the calibre's own rim thickness where a source gives it,
    and a ramp top that leaves the groove a GROOVE_FLOOR long floor, however far a rebated rim leaves the
    ramp to climb."""
    thick = rim_thickness(s["name"]) or RIMLESS_RIM
    groove = min(s["rim"] * GENERIC_GROOVE, s["base"] * GENERIC_GROOVE_OF_BASE)
    if s["kind"] == BELTED:
        return thick, thick + GENERIC_BELT, groove, GENERIC_RAMP
    return thick, thick + GROOVE_FLOOR + ramp_run(groove, s["base"], GENERIC_RAMP), groove, GENERIC_RAMP


def rim_and_groove(s):
    """Right half of the case's head, from the base to where the body starts, as (radius, height): the rim and,
    on a rimless, semi-rimmed or belted case, the extractor groove with its ramp (and the belt)."""
    rim, base, k = s["rim"] / 2, s["base"] / 2, s["kind"]
    if k in (RIMMED, RIMFIRE):
        h = rim_thickness(s["name"]) or (RIMFIRE_RIM if k == RIMFIRE else RIMMED_RIM)
        return [(rim, 0), (rim, h), (base, h)]
    # Rim, extractor groove and its front ramp at the calibre's own values (cartridges.CASE_HEADS), or at
    # the generic ones where no source gives them.
    thick, top_at, groove_dia, ramp_angle = case_head(s["name"]) or generic_head(s)
    groove = groove_dia / 2
    if k == BELTED:
        # The ramp climbs to the belt, which ends at E; the sheets give no groove width, so the groove floor
        # is drawn GROOVE_FLOOR long. The belt is as wide as the rim unless the calibre gives its own diameter
        # (.378 Weatherby Magnum: a belt of 15.33 mm in front of a 14.71 mm rim). In front of the belt the body
        # starts at the base diameter, which a belted case's sheet gives there (P1).
        belt_dia = s["belt"] or s["rim"]
        # A long ramp (a wide belt, or a big case on the generic head) stops at the front of the belt.
        ramp_end = min(top_at, thick + GROOVE_FLOOR + ramp_run(groove_dia, belt_dia, ramp_angle))
        return [(rim, 0), (rim, thick), (groove, thick), (groove, thick + GROOVE_FLOOR),
                (belt_dia / 2, ramp_end), (belt_dia / 2, top_at), (base, top_at)]
    ramp_start = max(thick, top_at - ramp_run(groove_dia, s["base"], ramp_angle))
    return [(rim, 0), (rim, thick), (groove, thick), (groove, ramp_start), (base, top_at)]


MIN_NECK = 1.2  # mm of neck a bottleneck case is drawn with at least: a shoulder too far forward moves back


def shoulder_run(s):
    """Length along the axis of a bottleneck case's shoulder, which runs at the calibre's own angle to the
    axis (cartridges.SHOULDER_ANGLES)."""
    return (s["shoulder"] - s["neck"]) / 2 / math.tan(math.radians(shoulder_angle(s["name"])))


# What can keep a drawing from being the calibre's own shape (gaps): a measurement without a source
# ([mm] unsourced, or no [mm] source at all), a bottleneck's shoulder at the default angle, the generic
# extractor groove, a rim of default thickness, and a shoulder the drawing had to move back to leave a neck.
MEASUREMENTS, SHOULDER_ANGLE, GROOVE, RIM_THICKNESS, SHOULDER_MOVED = GAPS = (
    "measurements", "shoulder_angle", "groove", "rim_thickness", "shoulder_moved")


def gaps(s):
    """The GAPS of a calibre's drawing, in their order: () when every drawn dimension comes from a source
    (well_sourced allows a little less). Bullet type, case material and the nose are not counted: they colour the
    drawing or are schematic anyway, like a shot shell's brass head and crimp, which differ from load to load."""
    name, found = s["name"], []
    cartridge = s["kind"] not in (SHOT, BALL, MINIE, PELLET)
    drawn = ("rim", "base", "neck", "case", "oal", "bullet") + (("sh_at",) if s["shoulder"] else ()) if cartridge else ()
    if unsourced(name) or any(s[k] is None for k in drawn):  # a cannon round may leave measurements out
        found.append(MEASUREMENTS)
    if cartridge:
        bottleneck = s["shoulder"] and s["profile"] != CRIMPED
        if bottleneck and name not in SHOULDER_ANGLES:
            found.append(SHOULDER_ANGLE)
        if s["kind"] not in (RIMMED, RIMFIRE) and case_head(name) is None:
            found.append(GROOVE)
        if rim_thickness(name) is None:
            found.append(RIM_THICKNESS)
        if bottleneck and None not in (s["sh_at"], s["neck"]) and s["sh_at"] > s["case"] - shoulder_run(s) - MIN_NECK:
            found.append(SHOULDER_MOVED)
    return tuple(found)


def well_sourced(s):
    """True for a calibre that is well sourced and likely draws correctly: its drawing has no gaps but, at
    most, a rim of default thickness, which is off by about half a millimetre at worst (Raven, 2026-11-14)."""
    return not set(gaps(s)) - {RIM_THICKNESS}


def case_profile(s):
    """Right half of the case, bottom to top, as (radius, height)."""
    base, case = s["base"] / 2, s["case"]
    pts = rim_and_groove(s)
    top = s["neck"] / 2
    if s["profile"] == CRIMPED:
        # Star crimp: the petals bend in over the front 38 % of the case, then turn in at the mouth.
        return pts + [(base, case * (1 - CRIMP_LENGTH)), ((base + top) / 2, case - 0.35), (top, case)]
    if s["shoulder"]:
        sh = s["shoulder"] / 2
        run = shoulder_run(s)
        sh_at = min(s["sh_at"], case - run - MIN_NECK)
        pts += [(sh, sh_at), (top, sh_at + run), (top, case)]
    else:
        pts += [(top, case)]
    return pts


def bullet_profile(r, y0, top, profile):
    """Right half of the exposed bullet from (r, y0) to the tip at `top`."""
    e = top - y0
    if profile == SPITZER:
        cyl, tip, f = 0.32, 0.05, lambda t: (1 - t ** 1.7) ** 0.8
    elif profile == ROUND:
        cyl, tip, f = 0.22, 0.16, lambda t: math.sqrt(max(0, 1 - t * t))
    elif profile == PATCHED:
        # The paper-wrapped body, then the capped nose straight from where the paper ends. The cap
        # sits the paper's thickness (8.15 where the paper ends, 7.95 on the cap) inside the body, so
        # the outline steps in there. The nose is an ogive of radius 22 mm ending in a 2.3 mm round tip.
        band, cap = PATCH_BAND * e, r - CAP_STEP
        start = y0 + band
        return [(r, y0), (r, start), (cap, start)] + ogive_nose(cap, start, top, OGIVE_RADIUS / CAP_RADIUS,
                                                                  TIP_RADIUS / CAP_RADIUS)
    elif profile == BALL_NOSE:
        # A sphere of the bullet's width, its top at the tip: the arc from the case mouth up, by angle
        # so the top is as smooth as the sides.
        centre, a0 = top - r, math.asin(max(-1, min(1, (y0 - (top - r)) / r)))
        angles = (a0 + (math.pi / 2 - a0) * i / (2 * N) for i in range(2 * N))
        return [(r * math.cos(a), centre + r * math.sin(a)) for a in angles] + [(0, top)]
    else:
        cyl, tip, f = 0.30, 0.55, lambda t: math.sqrt(max(0, 1 - t * t))
    start = y0 + cyl * e
    pts = [(r, y0), (r, start)]
    for i in range(1, N + 1):
        t = i / N
        pts.append((max(r * tip, r * f(t)), start + t * (top - start)))
    if pts[-1][0] > 0.001:
        pts.append((0, top))
    return pts


# Share of a crimped blank's case taken up by the star crimp, from the mouth back.
CRIMP_LENGTH = 0.38

# GP 1890 bullet from the army's drawing «Patrone, Modell 1890» (Thun, 1 February 1892): of the
# 23.7 mm out of the case, the paper covers 12.7 mm and the capped nose is the last 11 mm. Where the
# paper ends the bullet is 8.15 across and the cap 7.95: two turns of 0.05 mm paper, 0.1 mm a side
# (at the case mouth the paper is 8.35; drawn parallel at 8.15). The nose is an ogive of radius 22 mm
# with a 2.3 mm round tip; on a 7.95 mm cap that gives a 10.25 mm nose, stretched 7 % to the
# drawing's 11 (toleranced +0/-1).
PATCH_BAND = 12.7 / 23.7
CAP_STEP = 0.1
CAP_RADIUS = 7.95 / 2
OGIVE_RADIUS, TIP_RADIUS = 22.0, 2.3


def ogive_nose(r, start, top, ogive, tip):
    """Right half of a round-tipped tangent ogive from (r, start) to the tip at `top`, its radii given
    in bullet radii (`ogive` for the curve, `tip` for the round tip), stretched to the nose length.
    Needs tip < 1 <= ogive."""
    R, rt = ogive * r, tip * r
    cx = r - R  # the ogive's centre, level with the start of the nose
    ty = math.sqrt((R - rt) ** 2 - cx ** 2)  # the tip circle's centre on the axis, where it touches the ogive
    # Where the two circles touch: on the line from the ogive's centre through the tip's centre.
    k = R / (R - rt)
    jx, jy = cx + k * (0 - cx), k * ty
    length = ty + rt
    pts = []
    for i in range(1, N + 1):
        y = length * math.sin(math.pi / 2 * i / N)  # denser towards the round tip
        if y < jy:
            x = cx + math.sqrt(max(0, R * R - y * y))
        else:
            x = math.sqrt(max(0, rt * rt - (y - ty) ** 2))
        pts.append((x, start + y * (top - start) / length))
    pts[-1] = (0, top)
    return pts


def patch_profile(r, y0, top, band=PATCH_BAND):
    """Right half of the paper band of a patched bullet, drawn over the bullet."""
    return [(r, y0), (r, y0 + band * (top - y0))]


# Share of the exposed bullet wrapped in paper on a PAPER_PATCHED lead bullet (Gras, Martini-Henry):
# the paper covers the body, the lead nose shows. A calibre's [bullet] patch_length replaces it.
PAPER_BAND = 0.5

# Share of the exposed bullet that is the bare lead tip of a SOFT_POINT bullet, or the plastic tip of
# a POLYMER_TIP bullet.
TIP_SHARE = 0.14

# Height of the brass base cup of a PAPER case, from the base (mm): Boxer's Snider case is
# paper-covered brass foil in a brass cup; the paper starts 12.2-12.7 mm up on Raven's photos (2026-11-06).
PAPER_HEAD = 12.7


# Mouth radius and depth of a HOLLOW_POINT bullet's cavity, as shares of the bullet's radius.
HOLLOW_MOUTH, HOLLOW_DEPTH = 0.3, 0.8


def hollow_profile(r, y0, top, profile):
    """Right half of a hollow-point bullet: the round's own nose, cut off where it is as wide as the
    cavity's mouth, with the cavity below the cut (at most 0.3 of the exposed bullet deep)."""
    pts, m = bullet_profile(r, y0, top, profile), HOLLOW_MOUTH * r
    i = next(i for i, (x, _) in enumerate(pts) if x <= m)
    (xa, ya), (xb, yb) = pts[i - 1], pts[i]
    y = ya + (xa - m) / (xa - xb) * (yb - ya)
    return pts[:i] + [(m, y), (0, y - min(HOLLOW_DEPTH * r, 0.3 * (y - y0)))]


def tip_profile(right, top, share=TIP_SHARE):
    """Right half of the front `share` of a bullet profile (bottom to tip), for a soft point's lead tip."""
    cut = top - share * (top - right[0][1])
    pts = []
    for (x0, y0), (x1, y1) in zip(right, right[1:]):
        if y0 < cut < y1:
            pts.append((x0 + (x1 - x0) * (cut - y0) / (y1 - y0), cut))
        if y1 >= cut:
            pts.append((x1, y1))
    return pts


def head_profile(prof, top):
    """Right half of a case profile (bottom to top) from the base up to height `top`."""
    (x0, y0), (x1, y1) = next((a, b) for a, b in zip(prof, prof[1:]) if a[1] < top <= b[1])
    return [(x, y) for x, y in prof if y < top] + [(x0 + (x1 - x0) * (top - y0) / (y1 - y0), top)]


def mirror(right):
    """Closed polygon from a right half profile (x >= 0)."""
    left = [(-x, y) for x, y in reversed(right) if x > 0.0001]
    return right + left


def to_path(poly, height, half_width):
    d = []
    for i, (x, y) in enumerate(poly):
        d.append(f"{'M' if i == 0 else 'L'}{x + half_width:.2f} {height - y:.2f}")
    return " ".join(d) + " Z"


def outline(s):
    k = s["kind"]
    width = max(s["rim"], s["base"], s["bullet"], s["belt"] or 0)
    hw = width / 2
    H = s["oal"]
    paths = {}
    if k == SHOT:
        r, rim, L = s["base"] / 2, s["rim"] / 2, s["oal"]  # the loaded shell as crimped, not the opened hull
        head = 0.2 * L
        hull = [(r * 0.98, 1.5), (r * 0.98, L - 2.2), (r * 0.8, L - 0.6), (r * 0.35, L)]
        paths["case"] = to_path(mirror(hull), H, hw)
        paths["head"] = to_path(mirror([(rim, 0), (rim, 1.5), (r, 1.5), (r, head)]), H, hw)
    elif k == BALL:
        r = s["bullet"] / 2
        circ = [(r * math.sin(math.pi * i / (2 * N)), r - r * math.cos(math.pi * i / (2 * N))) for i in range(0, 2 * N + 1)]
        circ[0] = (0.0001, 0)
        paths["bullet"] = to_path(mirror(circ), H, hw)
    elif k == MINIE:
        r, L = s["bullet"] / 2, s["oal"]
        right = [(r * 0.94, 0), (r, 1.0)] + bullet_profile(r, 0.45 * L, L, ROUND)[0:]
        paths["bullet"] = to_path(mirror(right), H, hw)
    elif k == PELLET:
        r, L = s["bullet"] / 2, s["oal"]
        right = [(r, 0), (r * 0.9, 0.18 * L), (r * 0.6, 0.5 * L), (r * 0.62, 0.58 * L), (r, 0.66 * L)]
        right += [(max(0.15 * r, r * math.cos(math.pi / 2 * i / N)), 0.66 * L + 0.34 * L * math.sin(math.pi / 2 * i / N)) for i in range(1, N + 1)]
        right.append((0, L))
        paths["bullet"] = to_path(mirror(right), H, hw)
    else:
        prof = case_profile(s)
        paths["case"] = to_path(mirror(prof), H, hw)
        if s["oal"] > s["case"] + 0.1:
            kind = bullet(s["name"])
            r, y0, top = s["bullet"] / 2, s["case"], s["oal"]
            right = hollow_profile(r, y0, top, s["profile"]) if kind == HOLLOW_POINT else bullet_profile(r, y0, top, s["profile"])
            paths["bullet"] = to_path(mirror(right), H, hw)
            if s["profile"] == PATCHED:
                # The bullet path is the whole silhouette (steel cap colour); the paper band goes on top.
                paths["patch"] = to_path(mirror(patch_profile(s["bullet"] / 2, s["case"], s["oal"])), H, hw)
                paths["bulletMaterial"] = "steel"
            elif kind == PAPER_PATCHED:
                patch = patch_length(s["name"])
                band = patch / (s["oal"] - s["case"]) if patch else PAPER_BAND
                paths["patch"] = to_path(mirror(patch_profile(s["bullet"] / 2, s["case"], s["oal"], band)), H, hw)
                paths["bulletMaterial"] = "lead"
            elif kind == LEAD:
                paths["bulletMaterial"] = "lead"
            elif kind == STEEL:  # the MPS underwater dart
                paths["bulletMaterial"] = "steel"
            elif kind in (SOFT_POINT, POLYMER_TIP):
                paths["tip"] = to_path(mirror(tip_profile(right, top)), H, hw)
                if kind == POLYMER_TIP:
                    paths["tipMaterial"] = "polymer"
            if jacket(s["name"]) not in (None, COPPER):
                paths["bulletMaterial"] = jacket(s["name"])  # "cupronickel" or "steel"; copper is not named
        if case_material(s["name"]) == HYBRID:
            # The steel head holds the rim and the extractor groove, up to where the body starts (.277 Fury).
            paths["head"] = to_path(mirror(head_profile(prof, rim_and_groove(s)[-1][1])), H, hw)
            paths["headMaterial"] = "steel"
        elif case_material(s["name"]) == PAPER:  # brass head, no headMaterial
            paths["head"] = to_path(mirror(head_profile(prof, PAPER_HEAD)), H, hw)
        if case_material(s["name"]) != BRASS:
            paths["caseMaterial"] = case_material(s["name"])
        if current_case_materials(s["name"]):
            paths["currentCaseMaterials"] = list(current_case_materials(s["name"]))
    if k in (BALL, MINIE, PELLET) and loose_material(s["name"]) != LEAD:
        paths["bulletMaterial"] = loose_material(s["name"])  # "steel" or "plastic"; lead is not named
    return {"width": round(width, 2), "height": round(H, 2), **paths}


def specs():
    """Every catalogue entry as (category, spec), in catalogue order."""
    return [(category, s) for category, items in CATALOGUE for s in items]


def identical_groups():
    """Lists of calibre names whose outlines are identical (e.g. .308 Win / 7.62 NATO), in catalogue order.
    These cartridges cannot be told apart from the side."""
    groups = {}
    for _, s in specs():
        # Only the shape counts: twins may differ in bullet (.308 Win soft point, 7.62 NATO jacketed).
        o = {k: v for k, v in outline(s).items() if k in ("width", "height", "case", "head", "bullet")}
        key = (s["kind"], tuple(sorted(o.items())))
        groups.setdefault(key, []).append(s["name"])
    return [names for names in groups.values() if len(names) > 1]
