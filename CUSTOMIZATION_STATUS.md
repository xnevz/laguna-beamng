# Laguna II customisation: implementation status

Tracks `BEAMNG_CUSTOMIZATION_OPTIONS.md` section by section. **Wave 1** (this pass) rebuilt the vehicle as a working
BeamNG part tree and implemented the options that could be built properly with the current body model.

Rebuild everything with `python tools/build_all.py` (body → variants → export → jbeam → validate → renders → zip).
All jbeam files are **generated** by `tools/beamng/gen_laguna2.py`: edit the generator, not the .jbeam files.

Legend: ✅ done · 🟡 partly · ❌ not yet (with the reason)

---

## What the parts selector offers now

| Slot | Options | Notes |
|---|---|---|
| Body Style | Liftback | chassis, body meshes, glows for repeaters / 3rd brake light / plate lights |
| Engine | 1.6 16V, 1.8 16V, 2.0 16V, 2.0 Turbo, 3.0 V6, 1.9 dCi, 2.2 dCi, 2.0 dCi | real torque curves, petrol/diesel fuel, 68 L tank, *Starting Fuel* slider |
| Transmission | 5M (JR5), 6M (PK6), 4A Proactive (DP0), 5A Aisin | **only the gearboxes each engine really had** (see below); *Final Drive* slider |
| Front Differential | Open (factory), LSD (aftermarket) | |
| Front / Rear Suspension | Standard, Sport (GT), Lowered (aftermarket) | *Spring Rate*, *Damping*, *Ride Height* sliders per axle |
| Brakes | Standard, Large (V6 / 2.0T / GT) | *Front / Rear Brake Torque*, *Handbrake Torque* sliders |
| Wheels & Tyres | 17" ten-spoke alloys 225/45 R17, 15" steel + Renault hubcap 195/65 R15 | the steel wheel was modelled for this |
| Headlights | Halogen, Xenon | same lamps, xenon low beam glows cold blue-white |
| Tail Lights | Factory, Smoked (aftermarket) | |
| Front Fog Lights | Round, (empty = none) | |
| Side & Rear Glass | Factory tint, Privacy, Dark film | windscreen always factory green |
| Side Mirrors | Body-coloured caps, (empty) | |
| Rear Wiper | Rear wiper, (empty) | |
| Side Mouldings | Black, Body-coloured | |
| Rear Parking Sensors | Sensors, (empty: default) | |
| Front / Rear License Plate | EU (France), (empty) | |
| Rear Badges | "LAGUNA" script, (empty = debadged) | |

Every slot can also be emptied in the parts selector, so "none" exists for all of them.

**Engine → gearbox** (from the spec's engine table): 1.6 → 5M · 1.8 → 5M/4A · 2.0 → 5M/6M/4A ·
2.0T → 6M/5A · 3.0 V6 → 5A/6M · 1.9 dCi → 5M/6M/5A · 2.2 dCi → 6M/5A · 2.0 dCi → 6M/5A.

**Configurations** (`*.pc`): Authentique 1.6 · Expression 1.9 dCi (default) · Privilège 2.2 dCi Auto ·
Dynamique 2.0 Turbo · Initiale 3.0 V6 Auto · 2.0 Turbo Street (aftermarket). Renders: `renders/configs_sheet.png`.

**Paints** (`info.json`): Gris Hologramme, Gris Eclipse, Gris Platine, Noir Nacre, Blanc Glacier, Rouge de Feu,
Rouge Vif, Bleu Iliade, Bleu Nuit, Vert Fougère, Beige Champagne. The body paint follows the paint picker
(`instanceDiffuse`), so any colour works.

**Lights** (`glowMap` + lit materials): sidelights, low beam, high beam, front/rear indicators, side repeaters,
front fog, **rear fog (driver's side only)**, tail, brake, third brake light, reversing, plate lights.
Night renders of every state: `renders/lights_front_sheet.png`, `renders/lights_rear_sheet.png`,
`renders/option_headlights_halogen_vs_xenon.png`.

---

## Spec sections

| § | Topic | Status |
|---|---|---|
| 1 | Configurations | 🟡 6 liftback configs. Estate, Phase 2, police/taxi/rally need those bodies/parts first |
| 2 | Generation & body style | 🟡 Liftback (Phase 1 front, facelift-style tail lamps). ❌ Estate and Phase 2 front need new modelling |
| 3 | Front end | 🟡 ✅ headlights halogen/xenon, ✅ fog lights, ✅ front plate. ❌ Ph1/Ph2/GT bumpers and grilles, headlight washers, tow eye |
| 4 | Sides | 🟡 ✅ mirrors, ✅ mouldings black/body, ✅ "LAGUNA" script. ❌ engine/trim badges, chrome handles, skirts, mud flaps |
| 5 | Rear / tailgate | 🟡 ✅ tail lights factory/smoked, ✅ rear wiper, ✅ parking sensors, ✅ rear plate + plate lights, ✅ 3rd brake light. ❌ opening tailgate, roof-edge spoiler, rear bumper variants, visible exhaust tips |
| 6 | Glass | 🟡 ✅ factory / privacy / dark film. ❌ tint slider, breakable glass |
| 7 | Roof | ❌ sunroof, rails, racks (needs modelling) |
| 8 | Towing & cargo | ❌ tow bar, trailer socket, cargo cover, spare wheel |
| 9 | Lights & electrics | 🟡 ✅ all glows incl. rear fog and repeaters, ✅ xenon vs halogen. ❌ light-casting beams in game (`props`), horn, battery |
| 10 | Wheels, tyres, brakes | 🟡 ✅ 2 wheel designs, ✅ 2 brake sizes + torque sliders. ❌ separate tyre slot, more wheel designs, caliper paint |
| 11 | Suspension & steering | 🟡 ✅ standard/sport/lowered + spring/damping/ride-height sliders. ❌ camber/toe/anti-roll sliders, steering-lock kit |
| 12 | Engines | 🟡 ✅ all 8 engines with real curves and fuel types. ❌ turbo device (boost is in the torque curve), ECU remap, intake/exhaust parts, **engine sounds** |
| 13 | Transmission | 🟡 ✅ 4 gearboxes with per-engine availability, final-drive slider, open/LSD. ❌ shifter and pedal animations |
| 14 | Interior | ❌ only a simple static interior (no dashboard detail, keycard/START, Carminat, animations) |
| 15 | Paint | 🟡 ✅ 11 period colours + free paint. ❌ secondary/accent paint zones, liveries |
| 16 | Plates | 🟡 ✅ EU French plates. ❌ editable plate text (needs BeamNG's dynamic plate parts) |
| 17 | Role packages | 🟡 one aftermarket "street" config |
| 18 | Driver assists | ❌ ABS/ESP controllers |
| 19 | Damage & physics | 🟡 deformable chassis cage with crumple-friendly bumpers. ❌ detachable doors/hood/tailgate/bumpers, glass breaking |

---

## Vehicle physics (new in wave 1)

- **Frame**: BeamNG's own (front towards −Y, +X = left); the Blender scene already uses it, so meshes export unflipped.
- **Chassis**: 10 stations × lower/belt nodes + 3 roof stations + 4 engine nodes, fully braced cage, collision skin.
  Node masses ≈ **1305 kg, 61.6 % front** (1.9 dCi Laguna II ≈ 1370 kg).
- **Suspension**: every corner is a rigid knuckle held by a 2-link lower arm, a 2-link upper/strut link and a tie rod
  (front: steering hydro; rear: fixed toe link) → **exactly one degree of freedom**, carried by a coil-over whose
  preload is computed from the corner load, so the car sits at design height for any spring-rate / ride-height setting.
- **Powertrain**: engine → clutch or torque converter → gearbox → front differential → `wheelaxleFL/FR` (FWD).

## Checked here vs. needs an in-game test

`python tools/beamng/validate.py` checks every configuration: part tree resolves, slot types match, every node,
mesh, material, glowMap entry and variable exists, the powertrain is connected engine-to-wheels, and each
suspension corner has exactly one DOF. **BeamNG is not installed on the build machine**, so these were not
verified in the game and are the first things to check:

1. **Spawns and sits level**: ride height comes from the computed preload (`$=` expressions).
2. **Tyre parameters**: names/values in `TYRE_COMMON` (gen_laguna2.py) follow BeamNG's pressureWheels keys from
   memory; if the tyres look wrong, compare with a vanilla tyre part.
3. **Directions**: `wheelDir` (left −1, right +1) and the steering hydro sign (left +0.22, right −0.22). If the
   wheels spin backwards or the steering is inverted, flip the sign in the generator.
4. **Wheel meshes**: placed by flexbody `pos` / `rot` (right side rotated 180°).
5. **Lights**: electrics names (`lowbeam`, `highbeam`, `brakelights`, `signal_L/R`, `reverse`, `fog`) and the
   on / on_intense thresholds.
6. **No engine sound** and **no interior camera** are configured yet.
