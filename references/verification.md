# Native verification and the junction checker

## Baseline and candidate evidence

Use the actual root schematic so repeated sheets retain their instance references. Capture native component XML, complete net pin memberships and ERC before and after the layout pass. Preserve source hashes and recovery files. Compare component records and pin partitions rather than net counts alone. When deliberately renaming an unnamed net, require the same exact membership and report the rename separately.

Keep existing errors, warnings, excluded findings and ignored check categories visible. An unchanged failure is still unresolved. Do not repair an electrical fault as a side effect of tidying. New electrical differences require explanation and appropriate user scope before application.

Measure transformed electrical pin endpoints on the actual symbol units, not just symbol origins. Check the 50 mil grid and orthogonal wires. Record each lead longer than 100 mil with its actual nearby blocker and the smallest workable increment. Render the sheet and close-ups; native ERC does not catch all text/wire/body collisions or establish the intended visual compactness.

## Run the read-only junction check

Locate the scripts relative to this skill folder, not relative to the project being edited. Run:

```bash
python3 /absolute/path/to/kicad-schematic-tidy/scripts/check_junctions.py /absolute/path/to/root.kicad_sch --output /absolute/path/to/new-audit-folder
```

Requirements: Python 3 standard library and `kicad-cli` supporting schematic `export netlist --format kicadxml` and `erc --severity-all --format json`. Keep the adjacent `.kicad_pro`, project libraries and symbol tables available. Use a fresh output directory for each audit.

The script follows Sheetfile/Sheetname hierarchy entries, reads each unique source once, and reports repeated instances separately. It avoids backup/autosave globs. It writes fresh `native-netlist.xml`, `native-erc.json`, `junction-check.json` and `junction-check.md`. Source/project hashes must remain unchanged during the audit.

- Exit **0**: no discrepancies found by this junction check.
- Exit **1**: branch/junction discrepancies remain, including existing ones.
- Exit **2**: audit could not complete; do not interpret partial outputs as a pass.

The junction status is separate from ERC status. Inspect the exported ERC findings even if the junction check passes.

## Detection and limits

At exact wire contacts, require an explicit dot for three or more distinct wire arms. A missing dot is reported even when a different route or label already joins the same native net. Report attached physical-terminal net disagreements at explicit junctions as well.

Ordinary bends and straight wire splits have two arms and are not branch violations. A crossing strictly inside both wires is left alone without a dot. Coordinates are compared exactly; small gaps are not snapped into contacts.

Native pin evidence is attached where physical terminals map to the exported netlist. Empty evidence is not proof that all intended connections are correct. The helper covers modern text KiCad schematics with embedded library symbols, standard unit/body-style suffixes and native CLI exports. Unsupported input or export failures must fail the audit rather than be described as verified. Legacy `.sch`, buses, arbitrary pin-to-wire contact errors, near misses, layout collisions and full electrical validation are outside this helper's scope. Review those separately where relevant.

## Behavior tests

```bash
python3 -m unittest discover -s /absolute/path/to/kicad-schematic-tidy/scripts -p 'test_check_junctions.py' -v
```

Test native behavior on an isolated project copy as well: a known missing-dot contact must be reported, and its corrected version must agree in the native netlist. Keep test-only electrical changes out of the live project. Do not reuse a snapshot-specific coordinate editor as a general tidying engine.
