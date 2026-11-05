"""Side-view outlines of the catalogue cartridges, shared by both apps and the poster.

outline(spec) returns {"width", "height", "case"?, "head"?, "bullet"?, "patch"?, "tip"?, "bulletMaterial"?,
"tipMaterial"?, "caseMaterial"?, "headMaterial"?}:
millimetres, SVG path data (M/L/Z only), tip at the top (y = 0), base at the bottom
(y = overall length), centred in `width`.
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cartridges import CATALOGUE, RIMLESS, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET, SPITZER, ROUND, FLAT, PATCHED, CRIMPED  # noqa: E402
from cartridges import LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, BRASS, HYBRID, bullet, case_material  # noqa: E402

N = 14  # samples per curve


def case_profile(s):
    """Right half of the case, bottom to top, as (radius, height)."""
    rim, base, case = s["rim"] / 2, s["base"] / 2, s["case"]
    k = s["kind"]
    if k in (RIMMED, RIMFIRE):
        h = 1.1 if k == RIMFIRE else 1.5
        pts = [(rim, 0), (rim, h), (base, h)]
    else:
        groove = base * 0.82
        pts = [(rim, 0), (rim, 1.3), (groove, 1.3), (groove, 2.6), (base, 3.3)]
        if k == BELTED:
            pts[-1] = (rim, 3.3)
            pts += [(rim, 6.2), (base * 0.985, 6.2)]
    top = s["neck"] / 2
    if s["profile"] == CRIMPED:
        # Star crimp: the petals bend in over the front 38 % of the case, then turn in at the mouth.
        return pts + [(base, case * (1 - CRIMP_LENGTH)), ((base + top) / 2, case - 0.35), (top, case)]
    if s["shoulder"]:
        sh = s["shoulder"] / 2
        run = max(0.8, (sh - top) / math.tan(math.radians(32)))
        sh_at = min(s["sh_at"], case - run - 1.2)
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
        # Long parallel body, then a blunt round nose. The steel cap sits a paper's thickness
        # (about 0.06 mm) inside the patched body, so the outline steps in where the paper ends.
        band, cap = PATCH_BAND * e, r - 0.06
        pts = [(r, y0), (r, y0 + band), (cap, y0 + band)]
        start = y0 + 0.40 * e
        for i in range(1, N + 1):
            t = i / N
            pts.append((max(cap * 0.14, cap * math.sqrt(max(0, 1 - t * t))), start + t * (top - start)))
        return pts + [(0, top)]
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

# Share of the exposed bullet that shows the paper patch (GP 1890), from the case mouth up.
PATCH_BAND = 0.26


def patch_profile(r, y0, top, band=PATCH_BAND):
    """Right half of the paper band of a patched bullet, drawn over the bullet."""
    return [(r, y0), (r, y0 + band * (top - y0))]


# Share of the exposed bullet wrapped in paper on a PAPER_PATCHED lead bullet (Gras, Martini-Henry):
# the paper covers the body, the lead nose shows.
PAPER_BAND = 0.5

# Share of the exposed bullet that is the bare lead tip of a SOFT_POINT bullet, or the plastic tip of
# a POLYMER_TIP bullet.
TIP_SHARE = 0.14

# Height of the steel head of a HYBRID case, from the base (mm): rim, extractor groove and the
# start of the body (.277 Fury).
HYBRID_HEAD = 3.3


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
    width = max(s["rim"], s["base"], s["bullet"])
    hw = width / 2
    H = s["oal"]
    paths = {}
    if k == SHOT:
        r, rim, L = s["base"] / 2, s["rim"] / 2, s["case"]
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
            paths["bullet"] = to_path(mirror(bullet_profile(s["bullet"] / 2, s["case"], s["oal"], s["profile"])), H, hw)
            kind = bullet(s["name"])
            if s["profile"] == PATCHED:
                # The bullet path is the whole silhouette (steel cap colour); the paper band goes on top.
                paths["patch"] = to_path(mirror(patch_profile(s["bullet"] / 2, s["case"], s["oal"])), H, hw)
                paths["bulletMaterial"] = "steel"
            elif kind == PAPER_PATCHED:
                paths["patch"] = to_path(mirror(patch_profile(s["bullet"] / 2, s["case"], s["oal"], PAPER_BAND)), H, hw)
                paths["bulletMaterial"] = "lead"
            elif kind == LEAD:
                paths["bulletMaterial"] = "lead"
            elif kind in (SOFT_POINT, POLYMER_TIP):
                right = bullet_profile(s["bullet"] / 2, s["case"], s["oal"], s["profile"])
                paths["tip"] = to_path(mirror(tip_profile(right, s["oal"])), H, hw)
                if kind == POLYMER_TIP:
                    paths["tipMaterial"] = "polymer"
        if case_material(s["name"]) == HYBRID:
            head = [(x, y) for x, y in prof if y <= HYBRID_HEAD] + [(s["base"] / 2, HYBRID_HEAD)]
            paths["head"] = to_path(mirror(head), H, hw)
            paths["headMaterial"] = "steel"
        if case_material(s["name"]) != BRASS:
            paths["caseMaterial"] = case_material(s["name"])
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
