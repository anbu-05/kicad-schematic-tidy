# KiCad Schematic Tidy

A Codex skill for tidying existing KiCad schematics: **Step 0: symbol compaction**, when needed and authorised; **Step 1: connection tidying**; and **Step 2: sheet organisation**. It corrects symbol outliers, compacts local circuits and arranges their circuit boxes on A4 sheets while preserving connections and component data.

The skill includes reviewed visual examples and a read-only junction checker. It covers schematic presentation; PCB layout, part selection and circuit redesign are outside its scope.

## Install

Clone this repository into your personal Codex skills directory to make it available across projects:

```bash
git clone https://github.com/anbu-05/kicad-schematic-tidy.git ~/.agents/skills/kicad-schematic-tidy
```

If that directory already contains the skill, update the existing installation rather than cloning over it. Codex detects skill changes automatically; restart it if the skill does not appear.

## Use

In Codex, invoke the skill and identify the schematic or sheet:

```text
$kicad-schematic-tidy tidy the override supplies sheet in this project.
```

The skill can also be selected automatically when a request matches its description. Every invocation starts with a symbol-outlier scan in the requested scope. With no hit, Step 0 is skipped. The first clear hit triggers a question about permission to change symbols and any exceptions; declining preserves symbols and continues with the requested later steps. Existing permission is honoured. An authorised Step 0 ends with verified changes to placed schematic instances, then a general tidy runs Steps 1 and 2 once in order. Requests limited to a step, group or review retain that scope. The skill reads project constraints and verifies an isolated candidate before applying changes.

## Step 0: symbol compaction — conditional

1. **Scan for outliers.** Look for avoidable empty body space, unexplained uneven pin spacing or disproportionate size relative to comparable symbols. Inspect distinct definitions, not every repeated component; stop the initial scan at the first clear hit. There is no numerical eligibility threshold.
2. **Resolve permission and exceptions.** Ask whether symbols can be changed and what must be left alone. With permission, finish identifying eligible definitions in scope; without it, skip compaction and continue.
3. **Analyse the circuit.** Inspect the actual library, pin connections and support network; explain the proposed arrangement and account for shared-library users.
4. **Compact for readability.** Group pins coherently and remove unnecessary gaps, retaining text sizes and drawn-pin lengths unless a specific change is justified. Example pitches and body dimensions are not universal targets.
5. **Preserve electrical meaning.** Retain every pin identity, type, visibility and unit assignment, footprint-pad mapping, part data and NC status. Do not hide or combine pins to save space.
6. **Complete the placed-instance update.** Verify approved library geometry and all affected placed instances, including their attached wiring and NC markers, before proceeding to Step 1. A library-only preview is intermediate work.

The [symbol-compaction reference](references/symbol-compaction.md) contains the accepted U303/U301 comparisons, reasonable peers to leave unchanged, and completion checks. The bundled checker does not automate this scan or compaction.

## Step 1: connection tidying

1. **Compact complete local circuits.** Move support components and reshape their wiring together; remove unnecessary empty space and large loops.
2. **Target 100 mil pin leads.** Measure from the electrical pin endpoint to the first bend, junction, label or connected pin. Use at least 100 mil; extend in 50 mil steps only for a specific nearby pin or routing conflict.
3. **Use comfortable passive-branch spacing.** Target 300 mil between centre columns of comparable ordinary parallel passive branches. Increase when actual symbol or pin geometry requires it.
4. **Move fields into free space.** Keep references and values outside narrow gaps, clearly associated with their components, preserving their content, fonts and visibility.
5. **Separate groups before routing between them.** Keep local wires short. Replace long inter-group detours with matching net labels and verify that connected pin sets stay unchanged.
6. **Verify geometry and native connectivity.** Keep local wiring on the 50 mil grid. Compare component data and complete pin partitions, run ERC, inspect renders, and require explicit dots at wire branches.

The 300 mil branch target is not a universal component pitch; the examples distinguish general rules from arrangement-specific dimensions.

## Step 2: sheet organisation

1. **Use A4 sheets.** A3 or larger requires an explicit user request.
2. **Minimise each circuit box.** Fit the blue boundary around the complete visible circuit, including fields, wires, labels and power symbols, while respecting the connection-tidying rules.
3. **Keep 300 mil internal clearance.** Measure to the box edge centreline. Allow only the smallest necessary extra padding, less than 50 mil per edge, to preserve the electrical grid. Keep headings in the upper margin and separate notes outside boxes.
4. **Keep clear of the inner drawing border.** Start the first row 100 mil below it and every row 100 mil from its left edge. Keep at least 100 mil clear of the right/bottom border and title block.
5. **Pack left-to-right, then top-to-bottom.** Align box tops within a row, with exactly 200 mil between adjacent boxes. Wrap when the next complete box cannot fit; start the next row 200 mil below the preceding row's tallest box.
6. **Preserve and verify.** Move complete electrical groups on the 50 mil grid. Verify box measurements and rendered appearance alongside component data, full native connectivity, ERC and junction checks.

The complete rules, measurements, permission flow, exceptions and workflow are in [SKILL.md](SKILL.md).

## Examples

The [reviewed examples](references/examples.md) cover symbol-outlier compaction, a compact input/enable/bypass group, accepted passive-branch spacing, USB CC detour separation, missing versus corrected junction dots, and accepted A4 circuit-box packing.

![Accepted A4 circuit-box arrangement on override supplies](references/images/override-supplies-a4-boxes.png)

The accepted page places the 12 V and 5 V boxes on the first row and the dual-source/3.3 V box below. Internal padding is approximately 300–341 mil where needed to keep pins and wires on-grid. Complete native connections and all 55 physical pin-lead lengths were preserved.

## Junction checker

Requirements:

- Python 3, using only the standard library.
- `kicad-cli` with schematic XML-netlist and JSON-ERC export support.
- The project's root schematic, project file and required libraries.

From the repository directory, run the checker against the actual root schematic. Choose a new output directory for each audit:

```bash
python3 scripts/check_junctions.py /path/to/project/root.kicad_sch --output /path/to/new-audit
```

It follows the active hierarchy, including repeated sheet instances, and writes native netlist/ERC exports plus Markdown and JSON junction reports. It detects missing dots at exact wire branches and attaches native pin/net evidence. Intentional crossings inside both wires and ordinary bends are left alone.

| Exit status | Meaning |
| --- | --- |
| `0` | No junction discrepancies found by this check. |
| `1` | Junction discrepancies remain, including pre-existing ones. |
| `2` | The audit could not complete. |

A junction-check pass is separate from ERC status. The checker does not automatically tidy a schematic or check every layout rule, small gap, bus or possible connection error. See [verification guidance](references/verification.md) for its scope and limits.

## Tests and validation

Run the bundled behavior tests:

```bash
python3 -m unittest discover -s scripts -p 'test_check_junctions.py' -v
```

The initial package passed structural validation and 11 behavior tests. An isolated KiCad project exercise verified a 300-to-100 mil input-group adjustment with identical native component records and complete named pin partitions. Native control cases also verified missing-dot detection both when wires remained electrically joined and when touching stubs were disconnected.

A subsequent [TCAN1044A worked test](references/symbol-compaction.md#additional-applied-test-u1402-tcan1044a) exercised Steps 0–2: compacted a different symbol, updated its placed instance and support circuit, then packed the communications sheet onto A4. All 76 physical pin leads measure 100 mil; exact native component semantics and all named pin memberships remain unchanged. Pre-existing ERC/junction faults elsewhere remain reported. The reference includes the symbol comparison, final sheet and measured packing evidence; it does not claim an automatic symbol-scanner benchmark.

These checks support the presentation workflow; they do not establish electrical qualification or fabrication readiness. Existing faults remain reported rather than silently repaired by a tidying task.

## Repository contents

- `SKILL.md`: the entry scan and conditional Step 0, followed by Steps 1 and 2.
- `agents/openai.yaml`: Codex display metadata.
- `references/`: examples, reference images and verification guidance.
- `scripts/`: read-only junction checker and behavior tests.
