"""Light functions of the Laguna II - one table shared by the build, the export and the night renders.

Every lamp element that lights up has its own material.  BeamNG switches it with
the part's "glowMap": the material is swapped for <name>_on / <name>_on_intense
depending on the value of its simpleFunction (electrics weighted and summed):
0 -> off, up to 0.5 -> on, above 0.5 -> on_intense.  The tail lamps use the stock
BeamNG pattern {"lowbeam": 0.49, "highbeam": 0.49, "brakelights": 0.5}, so lights
alone give "on" (tail) and lights + brake give "on_intense" (brake).
"""

WHITE = (1.0, 0.95, 0.86)
HALOGEN = (1.0, 0.86, 0.66)      # warm tungsten-halogen
COOL = (0.92, 0.96, 1.0)
AMBER = (1.0, 0.42, 0.02)
RED = (1.0, 0.02, 0.02)

LIGHTS_ON = {"lowbeam": 1.0, "highbeam": 1.0}
TAIL = {"lowbeam": 0.49, "highbeam": 0.49, "brakelights": 0.5}

# material: (simpleFunction, glow colour, Blender emission strength for "on", for "on_intense")
GLOW = {
    # Front
    "laguna2_hl_low": (LIGHTS_ON, HALOGEN, 6.0, 6.0),           # low-beam reflector bowl
    "laguna2_hl_low_lens": (LIGHTS_ON, HALOGEN, 30.0, 30.0),    # projector lens
    "laguna2_hl_position": (LIGHTS_ON, WHITE, 12.0, 12.0),      # sidelight bulb in the low-beam bowl
    "laguna2_hl_high": ({"highbeam": 1.0}, HALOGEN, 30.0, 30.0),  # high-beam bowl and bulb (halogen on all versions)
    "laguna2_hl_signal_L": ("signal_L", AMBER, 30.0, 30.0),
    "laguna2_hl_signal_R": ("signal_R", AMBER, 30.0, 30.0),
    "laguna2_fog": ({"fog": 1.0}, WHITE, 25.0, 25.0),
    "laguna2_repeater_L": ("signal_L", AMBER, 20.0, 20.0),
    "laguna2_repeater_R": ("signal_R", AMBER, 20.0, 20.0),
    # Rear
    "laguna2_tail_lens_red": (TAIL, RED, 2.5, 10.0),
    "laguna2_tail_lens_smoked": (TAIL, RED, 2.5, 10.0),       # aftermarket smoked lens variant
    "laguna2_tail_fog": ({"fog": 1.0}, RED, 22.0, 22.0),      # rear fog light, driver's (left) side only
    "laguna2_tail_reflector": (TAIL, RED, 2.0, 8.0),
    "laguna2_tail_eye_red": (TAIL, RED, 4.0, 16.0),
    "laguna2_brake3": ({"brakelights": 1.0}, RED, 18.0, 18.0),
    "laguna2_reverse": ("reverse", WHITE, 25.0, 25.0),
    "laguna2_tail_signal_L": ("signal_L", AMBER, 30.0, 30.0),
    "laguna2_tail_signal_R": ("signal_R", AMBER, 30.0, 30.0),
    "laguna2_platelight": (LIGHTS_ON, WHITE, 10.0, 10.0),
}

# Electrics for the preview renders.  "sidelights" is a preview-only state (in
# BeamNG the sidelights come on with the low beam).
STATES = {
    "off": {},
    "sidelights": {"_side": 1.0},
    "lowbeam": {"lowbeam": 1.0},
    "highbeam": {"lowbeam": 1.0, "highbeam": 1.0},
    "signal_left": {"signal_L": 1.0},
    "hazards": {"signal_L": 1.0, "signal_R": 1.0},
    "fog": {"lowbeam": 1.0, "fog": 1.0},
    "brake": {"brakelights": 1.0},
    "lights_and_brake": {"lowbeam": 1.0, "brakelights": 1.0},
    "reverse": {"reverse": 1.0},
}
SIDELIGHT_MATS = {"laguna2_hl_position", "laguna2_tail_lens_red", "laguna2_tail_reflector",
                  "laguna2_tail_eye_red", "laguna2_platelight"}


# Xenon headlights use the same lamp meshes; only the lit colour of the low beam
# changes (cold blue-white instead of warm halogen).  material -> lit colour.
XENON = {
    "laguna2_hl_low": (0.70, 0.82, 1.0),
    "laguna2_hl_low_lens": (0.68, 0.80, 1.0),
}


def level(material, electrics):
    """0 = off, 1 = on, 2 = on_intense, as BeamNG's glowMap would pick."""
    fn = GLOW[material][0]
    if electrics.get("_side") and material in SIDELIGHT_MATS:
        return 1
    if isinstance(fn, str):
        v = electrics.get(fn, 0.0)
    else:
        v = sum(w * electrics.get(k, 0.0) for k, w in fn.items())
    if v <= 0.0:
        return 0
    return 1 if v <= 0.5 else 2


def glow_entry(name, variant=""):
    fn = GLOW[name][0]
    return {"simpleFunction": fn, "off": name, "on": name + "_on" + variant, "on_intense": name + "_on_intense" + variant}


def glow_map(names=None, variant_for=None):
    """A jbeam "glowMap" section for the given light materials (default: all).

    variant_for: {material: suffix} to point a material at a different lit
    version (e.g. the xenon low beam: "_xenon")."""
    variant_for = variant_for or {}
    return {n: glow_entry(n, variant_for.get(n, "")) for n in sorted(names or GLOW)}
