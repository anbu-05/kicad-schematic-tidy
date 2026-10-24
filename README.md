# KiCad Schematic Tidy

A Codex skill for tidying existing KiCad schematic sheets with six presentation and connectivity rules. It helps compact local circuits, improve spacing and field placement, and replace long wiring detours with matching net labels while preserving the circuit's connections and component data.

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

The skill can also be selected automatically when a request matches its description. It reads the project's constraints, works on an isolated candidate, and checks the result before applying the requested changes.

## The six rules

1. **Compact complete local circuits.** Move support components and reshape their wiring together; remove unnecessary empty space and large loops.
2. **Target 100 mil pin leads.** Measure from the electrical pin endpoint to the first bend, junction, label or connected pin. Use at least 100 mil; extend in 50 mil steps only for a specific nearby pin or routing conflict.
3. **Use comfortable passive-branch spacing.** Target 300 mil between centre columns of comparable ordinary parallel passive branches. Increase when actual symbol or pin geometry requires it.
4. **Move fields into free space.** Keep references and values outside narrow gaps, clearly associated with their components, preserving their content, fonts and visibility.
5. **Separate groups before routing between them.** Keep local wires short. Replace long inter-group detours with matching net labels and verify that connected pin sets stay unchanged.
6. **Verify geometry and native connectivity.** Keep local wiring on the 50 mil grid. Compare component data and complete pin partitions, run ERC, inspect renders, and require explicit dots at wire branches.

The full measurements, exceptions and workflow are in [SKILL.md](SKILL.md). The 300 mil branch target is not a universal component pitch; the examples distinguish general rules from arrangement-specific dimensions.

## Examples

The [reviewed examples](references/examples.md) cover a compact input/enable/bypass group, accepted passive-branch spacing, USB CC detour separation, and missing versus corrected junction dots.

![Accepted passive-branch spacing with outward field placement](references/images/passive-branches-300mil.png)

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

These checks support the presentation workflow; they do not establish electrical qualification or fabrication readiness. Existing faults remain reported rather than silently repaired by a tidying task.

## Repository contents

- `SKILL.md`: skill instructions and the six rules.
- `agents/openai.yaml`: Codex display metadata.
- `references/`: examples, reference images and verification guidance.
- `scripts/`: read-only junction checker and behavior tests.
