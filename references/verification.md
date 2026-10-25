# Native verification and the junction checker

## Step 0 completion

When symbol compaction is authorised, verify both the local-library change and its placed-instance update before Step 1. Check pin semantics, original pin-to-wire/label/NC identity, cached-library consistency and rendered support circuits in addition to the native comparisons below. A library preview alone does not complete Step 0. Read [the symbol-compaction reference](symbol-compaction.md#placed-instance-completion-and-verification) for the specific checks and accepted examples. Normalise coordinate-dependent native unit-pin element order and insignificant XML whitespace only; preserve exact pin membership and component metadata.

## Baseline and candidate evidence

Use the actual root schematic so repeated sheets retain their instance references. Capture native component XML, complete net pin memberships and ERC before and after the layout pass. Preserve source hashes and recovery files. Compare component records and pin partitions rather than net counts alone. When deliberately renaming an unnamed net, require the same exact membership and report the rename separately.

Keep existing errors, warnings, excluded findings and ignored check categories visible. An unchanged failure is still unresolved. Do not repair an electrical fault as a side effect of tidying. New electrical differences require explanation and appropriate user scope before application.

Measure transformed electrical pin endpoints on the actual symbol units, not just symbol origins. Check the 50 mil grid and orthogonal wires. Record each lead longer than 100 mil with its actual nearby blocker and the smallest workable increment. Render the sheet and close-ups; native ERC does not catch all text/wire/body collisions or establish the intended visual compactness.

## Sheet-organisation measurements

Read the actual drawing-sheet border and title-block extents from the native drawing or a fresh export. Do not assume that the physical A4 page edge or a hardcoded border inset is the reference. Check A4 unless the user explicitly requested a larger page.

Measure each group's visible bounds, including symbol/pin strokes, visible fields, wires, labels and power symbols. Native plotted glyph geometry avoids guessing text width from character count. Exclude hidden properties, box headings and separate engineering notes from circuit bounds; inspect headings and notes separately for fit and collisions. Measure padding and box gaps to the blue box edge centrelines.

Verify 300 mil minimum internal clearance on every edge. Where exact box packing conflicts with the absolute 50 mil electrical grid, retain only the smallest extra padding needed, less than 50 mil per edge, and report the measured allowance. Moving a group off-grid to make its padding exactly 300 mil is not an acceptable shortcut.

Verify the first row starts 100 mil below the inner border and every row starts 100 mil to its right. Check exactly 200 mil horizontal gaps and top alignment within a row. Each following row starts 200 mil below the preceding row's tallest box. Right/bottom border and title-block clearance must remain at least 100 mil; unused page area need not be filled. Confirm reading order and whole-box fit when wrapping.

For a rigid group move, compare every electrical object, symbol and attached field against the same grid-aligned translation. Recheck transformed pin endpoints, wire endpoints, lead lengths and native connectivity. A clean netlist/ERC or junction audit does not establish correct box measurements, text fit or visual layout.

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
