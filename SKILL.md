---
name: kicad-schematic-tidy
description: Tidy existing KiCad schematic sheets by compacting connected groups, applying 100 mil pin leads and 300 mil passive-branch spacing, repositioning fields, and replacing long detours with net labels. Verify native connectivity and junctions. Use for schematic presentation edits or reviews, not PCB layout, part selection, or circuit redesign.
---

# KiCad schematic tidy

Apply the six rules below to the requested sheets of an existing schematic. Work from electrical pin endpoints and connected local groups. Scope, project-specific constraints, and explicit user choices take precedence. Keep physical parts, pin identities, values, footprints, purchasing fields, label scope, field content/fonts/visibility, and unrelated project content intact.

Read [the approved examples](references/examples.md) before the first layout pass. They explain the intended compactness and distinguish example dimensions from general rules.

## Six rules

1. **Compact complete local circuits.** Move support parts and reshape shared wires together. Remove unnecessary empty rail length and large return loops. Reaching a pin-length metric alone does not complete the layout. Keep a readable association between each IC and its support circuit.

2. **Target 100 mil at pin interfaces.** Measure from the electrical pin endpoint to the first bend, real junction, label/power anchor, or connected symbol pin. Target exactly 100 mil (2.54 mm), with no shorter lead. Extend only to clear a specific nearby pin or its routing, using the smallest necessary 50 mil step and recording the blocker. Move the surrounding circuit before retaining a long lead. NC markers and coincident stacked pins internal to a symbol are exempt. Count floating touching stubs separately from real connections.

3. **Give comparable passive branches breathing room.** Use 300 mil (7.62 mm) between centre columns of ordinary parallel passive branches, such as neighboring resistor/capacitor branches sharing a rail. Match comparable pairs; increase in 50 mil steps when actual symbol or pin extents require it. This is independent of the 100 mil lead rule. Do not apply this pitch to every symbol, IC, bank, or different branch orientation.

4. **Move fields into nearby free space.** Put references and values outside narrow branch gaps, clearly associated with their parts. Clear bodies, pins, wires, labels, and other text. Preserve content, font size and visibility; use consistent anchors for comparable parts. No universal numerical text clearance has been agreed.

5. **Choose groups before routing between them.** Keep short, readable direct connections within each local group, using short shared rails and local grounds. Where an inter-group wire wraps around components or forces unnecessary separation/crossings, replace that span with matching net labels and compact the groups independently. Anchor labels exactly at accessible wire endpoints. Preserve existing names and scope; deliberately name previously unnamed nets where needed, documenting the rename and proving that complete pin partitions are unchanged. Do not merge distinct nets or convert local labels into global labels to simplify routing.

6. **Check geometry and native connectivity.** Use the 50 mil (1.27 mm) grid for local wire endpoints and placement. Preserve orthogonal wiring. Compare native component data and complete net-to-pin partitions, run ERC including exclusions, and inspect rendered output. Require an explicit junction dot at a drawn T or other three-or-more-arm wire branch. Verify actual native nets; visual contact is insufficient. Intentional interior crossings remain unconnected without a dot. Report pre-existing junction faults as unresolved failures, even when before/after connectivity is unchanged. Read [verification guidance](references/verification.md) for the checker, evidence requirements and its limitations.

## Working pass

- Identify the requested root/sheets and current saved state. Preserve manual saves and project/library resolution. Snapshot affected native sources and retain hashes before editing; never replay a historical coordinate editor over a later save.
- Capture fresh baseline netlist/ERC evidence. Existing electrical faults remain visible in the final result. A presentation task does not authorise connecting previously separate nets to repair them.
- Edit an isolated candidate first. Apply rules to local groups, then render the whole sheet and useful close-ups. Inspect text, pin/body collisions, junctions, label anchors and spacing exceptions.
- Verify the candidate against its baseline. Explain intentional net renames separately from electrical changes. If source hashes changed while working, preserve the new saves and rebase the candidate rather than overwrite them. Apply only verified edits within the requested scope.
- Report changed groups, measured exceptions, connectivity/ERC/junction results and remaining faults. Presentation checks do not establish electrical qualification.

Prefer native-file/CLI workflows for deterministic edits and exports. When GUI work is needed, use exact-window background control that preserves the foreground app and input focus; stop and explain if that cannot complete the action. Do not change PCB placement/routing, part choices or circuit architecture under this skill.

The bundled script is a read-only junction check, not a general layout editor or automatic implementation of all six rules. Dependencies: Python 3 standard library and `kicad-cli` with schematic XML-netlist/JSON-ERC export support.
