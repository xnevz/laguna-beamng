# Building from source

The complete pipeline is defined in `tools/build_all.py`.

## Requirements

- Windows
- Python 3
- Blender 5.3 or a compatible Blender executable
- BeamNG.drive for final in-game testing

## Configure Blender

The default executable is:

```text
C:\Program Files\Blender Foundation\Blender 5.3\blender.exe
```

Override it in PowerShell:

```powershell
$env:BLENDER="C:\Path\To\Blender\blender.exe"
```

## Run the full pipeline

```bash
python tools/build_all.py
```

The pipeline:

1. Builds the vehicle body in Blender.
2. Creates customization variants.
3. Exports meshes and materials.
4. Generates JBeam parts and configurations.
5. Runs static validation.
6. Generates preview renders.
7. Creates `renault_laguna.zip`.

## Development options

```bash
python tools/build_all.py --no-renders
python tools/build_all.py --draft
python tools/build_all.py --no-renders --draft
```

Use `--no-renders` for rapid JBeam and physics work.

## Individual stages

```bash
python tools/beamng/gen_laguna2.py
python tools/beamng/validate.py
python tools/package_mod.py
```

## JBeam maintenance

Do not edit generated JBeam files directly. Edit:

```text
tools/beamng/gen_laguna2.py
```

Then regenerate and validate:

```bash
python tools/beamng/gen_laguna2.py
python tools/beamng/validate.py
```

## Validation

The validator checks:

- Configuration and slot references
- Required nodes and meshes
- Materials and glow maps
- Engine-to-wheel powertrain connections
- Suspension degrees of freedom

Static validation does not replace testing the mod inside BeamNG.drive.
