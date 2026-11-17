# Renault Laguna II: BeamNG Customization Possibilities

A list of everything the Laguna II (X74, 2001–2007) can let the player customize in BeamNG,
adapted to what the real car actually had. Generic BeamNG options that don't fit this car are
listed separately so they can be added on purpose (as aftermarket/fun parts) or skipped.

Legend:
- **[Slot]**: part chosen in the Parts Selector (can be empty / "none")
- **[Var]**: tuning slider (`variables` in jbeam)
- **[Paint]**: paint / material option
- **[Anim]**: prop or flexbody driven by `electrics` (moves in-game)
- **[Factory]**: existed on the real Laguna II
- **[Aftermarket]**: not factory, but believable as an add-on
- **[Verify]**: detail I'm not certain about; check against the reference photos / FBX before building

---

## 0. The car in short (what makes it different)

| Topic | Laguna II reality | Consequence for the mod |
|---|---|---|
| Generations | Phase 1 (2001–2005) and Phase 2 facelift (2005–2007) | Most visible parts need **Ph1 and Ph2 versions** |
| Body styles | 5-door **liftback** (hatchback) and **Estate** (Grandtour / Sport Tourer) | No sedan, no coupe (the coupe is Laguna III) |
| Drive layout | **Front-wheel drive only**, transverse engine | No RWD/AWD, no rear diff, no transfer case |
| Engines | Petrol I4 (1.6, 1.8, 2.0, 2.0 Turbo), **3.0 V6**, diesel dCi (1.9, 2.0, 2.2) | Each engine limits which gearboxes fit |
| Gearboxes | 5- and 6-speed manuals; 4- and 5-speed automatics ("Proactive", with manual +/− mode) | No DCT, no CVT, no sequential |
| Signature features | **Renault keycard + START button** (hands-free card), Carminat pop-up navigation screen, 5-star Euro NCAP (2001) | Unique interior animations and props |
| Trims | Authentique, Expression, Dynamique, Privilège, Initiale (Paris), **GT** (Phase 2) | Trims set wheels, interior, lights, paint options |

---

## 1. Configurations (presets, `.pc` files)

Realistic set:
- **Liftback** × Ph1 / Ph2 × trims (Authentique → Initiale)
- **Estate** × Ph1 / Ph2 × trims
- **2.0 Turbo** (Ph1) and **GT 2.0T** (Ph2, sportier suspension and bodywork)
- **3.0 V6 Initiale** (top luxury, automatic)
- **dCi** diesel family cars (the most common real-world Lagunas)
- Fleet / company car (base spec, plain colors)

Fun / BeamNG-style extras (not factory):
- European police estate, taxi, rally (gravel), drift build, worn "beater"

---

## 2. Generation & Body Style (top-level slots)

- **[Slot] [Factory]** Generation: Laguna II Phase 1 / Phase 2
  (the project already has a `laguna_generation` slot and a `laguna_bodystyle_gen2` slot)
- **[Slot] [Factory]** Body style: liftback / estate
  - Shared: front end, front doors, dashboard, engines, gearboxes, front suspension
  - Different: rear doors (shape of window frame), C/D pillars, roof length, rear glass,
    **tailgate**, tail lights, rear bumper, rear suspension mounting, cargo area
- Not applicable: sedan, coupe, convertible, van, pickup

---

## 3. Front End

- **[Slot] [Factory]** Front bumper: Ph1 / Ph2 / Ph2 GT (sportier lower intake)
- **[Slot] [Factory]** Grille: Ph1 (Renault diamond on body-colored nose, thin grille slots) /
  Ph2 (larger chrome-trimmed grille, redesigned nose) **[Verify]** exact styling per trim
- **[Slot] [Factory]** Headlights:
  - Ph1 halogen
  - Ph1 xenon (high trims, with **headlight washers**)
  - Ph2 halogen / Ph2 xenon (redesigned shape)
  - **[Aftermarket]** smoked / black-housing versions
- **[Slot] [Factory]** Front fog lights: none / round fogs in bumper (depends on trim and phase)
- **[Slot] [Factory]** Headlight washers (only with xenon)
- **[Slot]** Hood: stock only (factory). **[Aftermarket]** vented / carbon hood for race builds
- **[Slot] [Factory]** Front license plate holder (EU long plate)
- **[Slot] [Factory]** Front tow eye (screw-in, stored in the trunk)

---

## 4. Sides

- **[Slot] [Factory]** Front fenders (shared by body styles; Ph1/Ph2 with side repeater)
- **[Slot] [Factory]** Doors: 4 doors, rear doors differ between liftback and estate
- **[Slot] [Factory]** Side mirrors: manual / electric / electric heated / power-folding (higher trims);
  body-colored caps
- **[Slot] [Factory]** Side protection moldings (black / body-colored / chrome strip on Initiale **[Verify]**)
- **[Slot] [Factory]** Door handles: body-colored (chrome accents on some Ph2 trims **[Verify]**)
- **[Slot] [Factory]** Badges: "Laguna", engine badges (e.g. "V6", "dCi"), "Initiale" badge
- **[Slot] [Aftermarket]** Side skirts, mud flaps

---

## 5. Rear End: the Tailgate

The rear opening part is the **tailgate** (also called the **hatch** or **liftgate**).
On the Laguna II the **liftback** tailgate is large and lifts **together with the rear window**;
it's the car's defining shape. The **estate** has a near-vertical tailgate.

- **[Slot] [Factory]** Tailgate: liftback / estate (each with Ph1 / Ph2 trim)
- **[Slot] [Factory]** Tailgate opening: **[Anim]** hinges at the roof, gas struts
- **[Slot] [Factory]** Rear spoiler: none / small roof-edge spoiler (sporty trims, Ph2 GT)
- **[Slot] [Factory]** Rear wiper: standard on estate; liftback **[Verify]** (often absent)
- **[Slot] [Factory]** Tail lights:
  - Liftback Ph1 / Liftback Ph2
  - Estate Ph1 / Estate Ph2
  - **[Aftermarket]** smoked / clear "euro" style
- **[Slot] [Factory]** Third brake light (top of the tailgate)
- **[Slot] [Factory]** Rear bumper: Ph1 / Ph2 / GT, liftback and estate versions
- **[Slot] [Factory]** Exhaust exit: hidden single pipe (most engines) / visible tip(s) on V6 and GT **[Verify]**
- **[Slot] [Factory]** Rear license plate with plate lights (on the tailgate)
- Not applicable: trunk lid, big wing (factory). A big wing would be aftermarket only.

---

## 6. Glass

- **[Factory]** Windshield (green-tinted factory glass, laminated: it cracks but stays in place)
- **[Slot] [Factory]** Side windows: standard light tint
- **[Slot] [Factory]** Rear privacy glass: darker rear side windows + rear window (mainly estate / high trims **[Verify]**)
- **[Slot] [Aftermarket]** Film tint: light / dark / limo
- **[Var]** Tint darkness
- **[Factory]** Rear window with defroster lines (part of the liftback tailgate)
- **[Factory]** Windows on the liftback: frameless? **No**, the Laguna II has framed doors
- Tempered side and rear glass shatters fully; windshield only cracks

---

## 7. Roof

- **[Slot] [Factory]** Plain roof
- **[Slot] [Factory]** Electric sunroof (tilt and slide)
- **[Slot] [Factory]** Roof rails (estate)
- **[Slot] [Aftermarket]** Crossbars, roof box, bike / ski rack
- Not applicable: panoramic roof, convertible top, removable roof

---

## 8. Towing & Cargo

- **[Slot] [Factory accessory]** Tow bar: none / fixed swan-neck / **detachable** (Renault accessory)
- **[Slot]** Trailer socket 7-pin / 13-pin, so trailer lights work
- **[Var]** Realistic towing: estate and diesels were popular tow cars
- **[Slot] [Factory]** Cargo cover: roller blind (estate) / parcel shelf that lifts with the tailgate (liftback)
- **[Slot] [Factory]** Cargo net / dog guard (estate)
- **[Slot] [Factory]** Spare wheel under the trunk floor: space-saver / full size / repair kit
- **[Slot]** Trunk props: jack, warning triangle, toolkit

---

## 9. Lights & Electrics

- **[Anim] [Factory]** Working glows: low / high beam, brake, reverse, indicators, hazards, rear fog
- **[Factory]** Rear fog light (EU requirement; single light, driver's side)
- **[Factory]** Indicator repeaters on the front fenders
- **[Slot] [Factory]** Xenon vs halogen changes light color and intensity
- Not factory: DRLs (Laguna II predates DRL rules), LED lights
- **[Slot] [Aftermarket]** Light pod (rally), lightbar (police)
- **[Slot]** Horn: stock / **[Aftermarket]** air horn
- **[Slot]** Battery: petrol / diesel (bigger) / heavy-duty

---

## 10. Wheels, Tires & Brakes

### Wheels
- **[Slot] [Factory]** Steel wheels with Renault hubcaps (15"), several hubcap designs
- **[Slot] [Factory]** Alloy wheels (16", 17") with designs per trim and phase
- **[Slot] [Factory]** GT / V6 alloys (17", Ph2 GT design **[Verify]**)
- **[Slot] [Aftermarket]** Aftermarket alloys, 18" options
- **[Factory]** 4-stud hubs on small engines vs 5-stud on bigger ones **[Verify]**; this sets which wheels fit
- **[Var]** Offset / spacers
- **[Paint]** Rim finish: silver, anthracite (GT), black (aftermarket)

### Tires
- **[Slot]** Economy / touring (factory) / sport / winter / all-terrain (rally) / semi-slick / drift
- Sizes around 195/65 R15, 205/55 R16, 225/45 R17
- **[Var]** Pressure front/rear

### Brakes
- **[Factory]** Front vented discs; rear solid discs
- **[Slot] [Factory]** Larger front brakes on V6 / 2.0T / GT
- **[Factory]** ABS standard (with brake assist); EBD
- **[Slot] [Aftermarket]** Big brake kit, sport pads
- **[Var]** Brake bias
- **[Paint]** Caliper color (factory: plain; aftermarket: red / yellow / black)
- Handbrake: conventional lever **[Verify]**; **[Aftermarket]** hydraulic drift handbrake

---

## 11. Suspension & Steering

- **[Factory]** Front: MacPherson struts. Rear: torsion beam (different on estate for load capacity)
- **[Slot] [Factory]** Standard / sport (GT, firmer and lower) / estate heavy-load springs
- **[Slot] [Aftermarket]** Lowered springs, coilovers, rally (raised), race
- **[Var]** Ride height, spring rate, damping, anti-roll bars, camber, toe
- **[Factory]** Hydraulic power steering (electro-hydraulic on some engines **[Verify]**)
- **[Factory]** Ph2 GT with stiffer settings and quicker steering **[Verify]**
- **[Var]** Steering lock (drift kit = more lock)
- Rear camber/toe on a torsion beam is mostly fixed in reality; the sliders are a BeamNG convenience
- Not applicable: air suspension, solid axle, rear steering (that came on the Laguna III GT 4Control)

---

## 12. Engines (real Laguna II range)

| Engine | Code | Fuel | Approx. power | Factory gearboxes |
|---|---|---|---|---|
| 1.6 16V | K4M | Petrol | 107–110 hp | 5-speed manual |
| 1.8 16V | F4P | Petrol | 117–120 hp | 5-speed manual / 4-speed auto |
| 2.0 16V | F4R | Petrol | 135–140 hp | 5/6-speed manual / auto |
| 2.0 16V Turbo | F4Rt | Petrol | 165–170 hp (205 hp GT Ph2) | 6-speed manual / 5-speed auto |
| 3.0 V6 24V | L7X | Petrol | ~207–210 hp | 5-speed auto (manual on some markets **[Verify]**) |
| 1.9 dCi | F9Q | Diesel | 100–130 hp | 5/6-speed manual / auto |
| 2.2 dCi | G9T | Diesel | ~150 hp | 6-speed manual / auto |
| 2.0 dCi | M9R | Diesel | 150–175 hp (Ph2) | 6-speed manual / auto |

(Power figures are approximate and vary by year and market.)

Per-engine slots:
- **[Slot] [Factory]** Engine
- **[Slot]** Engine internals (stock / **[Aftermarket]** upgraded)
- **[Slot]** Intake: airbox / **[Aftermarket]** cone filter
- **[Slot] [Factory]** Turbo: only on 2.0T and all dCi engines
- **[Slot] [Factory]** Intercooler: 2.0T and dCi
- **[Var]** Boost pressure (turbo engines only)
- **[Slot]** ECU: stock / **[Aftermarket]** remap (very popular on dCi and 2.0T)
- **[Slot] [Factory]** Diesel particulate filter (later 2.0 dCi) **[Verify]**
- **[Slot]** Radiator, oil cooler
- **[Slot]** Engine cover (Renault plastic cover, differs per engine)
- **[Slot]** Fuel tank (~68 L) **[Verify]**, **[Var]** starting fuel
- Sounds: I4 petrol, turbo I4, V6, diesel (with turbo whistle)
- Not applicable (factory): supercharger, nitrous, carburetors, V8. These are aftermarket fun only.

### Exhaust
- **[Slot] [Factory]** Stock exhaust (per engine)
- **[Slot] [Factory]** Catalytic converter
- **[Slot] [Aftermarket]** Sport muffler / straight pipe / DPF delete (diesel)
- **[Slot]** Tips: hidden stock / visible chrome tip

---

## 13. Transmission & Shifter (with matching interior animation)

### Gearboxes
- **[Slot] [Factory]** 5-speed manual (JR5-type, small engines)
- **[Slot] [Factory]** 6-speed manual (PK6, bigger engines and dCi)
- **[Slot] [Factory]** 4-speed automatic "Proactive" (DP0, smaller petrols)
- **[Slot] [Factory]** 5-speed automatic (Aisin, V6 / 2.0T / dCi) with **manual +/− mode**
- **[Var]** Gear ratios, final drive
- **[Slot]** Clutch: stock / **[Aftermarket]** sport (manual only)
- Not applicable: DCT, CVT, sequential, paddle shifters, AWD transfer case

### Shifter animation (depends on the gearbox chosen)
- **Manual 5-speed**: **[Anim]** H-pattern stick with 5 gates, reverse behind 5th or **[Verify]**
  next to 1st with a lift-ring; moves to the current gear (`gear_M` electrics)
- **Manual 6-speed**: **[Anim]** 6-gate H-pattern, reverse with lift-up collar
- **Automatic**: **[Anim]** lever moves along a gated P-R-N-D path (`gear_A`), and into the
  **side gate for +/−** manual mode, where it tips forward/back on each shift
- **[Anim]** Clutch pedal: present and moving only on manual cars; automatics have a wide brake pedal and no clutch
- **[Anim]** Dashboard gear indicator: automatics show P/R/N/D or the gear number in manual mode
- **[Slot]** Gear knob: stock leather / chrome-ring (GT, Initiale) / **[Aftermarket]** short shifter
- **[Slot]** Center console: manual version vs automatic version (different gate trim)

### Drivetrain
- **[Factory]** FWD only, open front differential
- **[Slot] [Aftermarket]** LSD (clutch / viscous) / welded diff
- **[Slot] [Factory]** Traction control + ESP (standard on bigger engines and later cars **[Verify]**)
- Not applicable: rear diff, center diff, AWD, 4x4

---

## 14. Interior

### Dashboard & instruments
- **[Slot] [Factory]** Dashboard: Ph1 / Ph2 (Ph2 has updated materials and trim) **[Verify]** exact differences
- **[Factory]** Gauge cluster: analog speedometer + tachometer with central digital displays
  (trip computer, fuel, temperature **[Verify]**)
- **[Anim]** Needles: speed, RPM; digital fuel and temperature
- **[Anim]** Warning lights: engine, oil, battery, ABS, handbrake, indicators, high beam, seatbelt, glow plug (diesel)
- **[Slot] [Factory]** Radio: Renault Update List / CD / CD changer, with steering-column satellite remote stalk
- **[Slot] [Factory]** **Carminat navigation**: screen that rises out of the top of the dashboard (Initiale / high trims)
  **[Anim]** screen raises when ignition is on
- **[Slot] [Factory]** Climate: manual / automatic dual-zone
- **[Slot] [Aftermarket]** Extra gauges (boost, oil), dashcam

### Keycard & start button (unique to this car)
- **[Factory]** No traditional key: **Renault card** goes in a **slot on the dashboard**, then press the **START** button
- **[Slot] [Factory]** Card version: insert-card / hands-free card (higher trims)
- **[Anim]** Card visible in the slot when the engine is running; START button light

### Steering wheel
- **[Slot] [Factory]** 4-spoke Renault wheel (airbag), urethane / leather (higher trims)
- **[Slot] [Factory]** GT / Ph2 sport leather wheel **[Verify]**
- **[Factory]** Cruise control / speed limiter buttons on the wheel
- **[Factory]** Radio remote **stalk** behind the wheel (not buttons on the wheel)
- **[Slot] [Aftermarket]** Sport / racing / quick-release wheel
- **[Anim]** Wheel rotates with steering

### Seats & trim
- **[Slot] [Factory]** Front seats: cloth / velour / leather (Initiale) / sport seats (GT)
- **[Factory]** Heated and electric seats on high trims
- **[Slot] [Factory]** Rear bench: 60/40 split folding (estate flat-loading)
- **[Slot] [Aftermarket]** Bucket seats + harnesses, roll cage, stripped interior
- **[Paint] [Factory]** Interior color schemes: dark grey / charcoal, light grey, beige; Initiale two-tone leather **[Verify]**
- **[Slot] [Factory]** Dash/door inserts: plain plastic / aluminium-look / wood-look (Initiale) **[Verify]**
- **[Slot]** Floor mats, sun visors, rear-view mirror (auto-dimming on high trims)
- **[Anim]** Pedals (throttle, brake, clutch on manuals), handbrake lever, indicator/wiper stalks

### Doors & openings
- **[Anim]** 4 doors, hood, tailgate, fuel flap
- **[Factory]** Electric windows front (and rear on most trims); manual rear winders on base trims **[Verify]**

---

## 15. Paint, Trim & Skins

- **[Paint]** Three paint slots: body / secondary (lower trim on some versions) / accents
- **[Paint]** Metallic, clearcoat, roughness
- **[Factory]** Era-appropriate Renault colors: silver, dark grey, black, dark blue, red, white,
  green, champagne/beige metallics **[Verify]** exact names and codes
- **[Factory]** Bumpers fully body-colored on all versions (no unpainted plastic)
- **[Slot]** Trim finish: chrome (Initiale, Ph2) / black
- **[Slot] [Aftermarket]** Liveries: police, taxi, rally, racing stripes, dirty/rusty, sponsor decals

---

## 16. License Plates

- **[Factory]** EU long plates front and rear (French style as default)
- **[Slot]** Other countries' plates (UK, German, etc.)
- **[Slot]** Plate frame (dealer frame)
- Plate text editable

---

## 17. Role & Fun Packages (non-factory, believable for this car)

- **Police (European)**: estate with lightbar, sirens, livery, radio, push bar (use as a fun config)
- **Taxi**: dCi estate/liftback with roof sign and meter
- **Rally (gravel)**: raised suspension, skid plates, mud flaps, light pod, rally tires, bucket seats, cage
- **Track**: lowered, semi-slicks, wing, stripped interior, 2.0T remap
- **Drift**: steering lock kit, welded diff... **note**: the car is FWD, so drift needs an aftermarket
  RWD swap (very unrealistic) or should be skipped
- **Beater**: rust/dirt skin, mismatched panel colors, cracked windshield
- Not useful: off-road 4x4 (no AWD), heavy-duty work trucks

---

## 18. Driver Assists (controllers)

- **[Factory]** ABS + brake assist + EBD
- **[Factory]** ESP / traction control (trim-dependent **[Verify]**)
- **[Factory]** Cruise control and speed limiter
- **[Factory]** Rain-sensing wipers and auto headlights (high trims)
- **[Factory]** Rear parking sensors (option)
- Not applicable: launch control, start-stop, lane assist, adaptive cruise

---

## 19. Damage & Physics (things this car should do right)

- Large liftback tailgate: heavy, lots of glass, struts fail on big rear hits
- Laminated windshield cracks; tempered side/rear glass shatters
- Euro NCAP 5-star structure: strong cabin cell, crumple zones in front
- Doors, hood, tailgate, bumpers, mirrors, hubcaps detach
- FWD engine bay: engine and gearbox move together on crash; radiator damage → overheating
- Weight differences: V6 / diesel nose heavier than 1.6 petrol; estate heavier at the rear

---

## Summary: what does NOT apply to the Laguna II (unless added as aftermarket)

| Generic BeamNG option | Why it doesn't fit |
|---|---|
| Sedan / coupe / convertible / van | Only liftback and estate existed |
| RWD / AWD, rear or center diff | FWD only |
| DCT, CVT, sequential, paddle shifters | Not offered |
| Supercharger, nitrous, V8 | Not offered |
| Panoramic or removable roof | Only a sunroof |
| DRL / LED lights | Too early |
| Air suspension, rear-wheel steering | Not on this generation |
| Launch control, start-stop, lane assist | Not on this generation |
| Off-road 4x4 package | No AWD |
| Traditional key ignition | It uses the keycard + START button instead |

Items marked **[Verify]** should be checked against the reference FBX and photos in
`blender/references/` before modeling them.
