---
name: kicad-schematic-tidy
description: Tidy existing KiCad schematic connections and organise A4 sheets with compact circuit boxes while preserving native connectivity. Use for schematic presentation edits or reviews, not PCB layout, part selection, or circuit redesign.
---

# KiCad schematic tidy

Use two passes on the requested sheets of an existing schematic: **connection tidying**, then **sheet organisation**. For a general sheet-tidying request, apply both; for a request limited to one pass or group, keep that scope. Work from electrical pin endpoints and connected local groups. Project-specific constraints and explicit user choices take precedence. Keep physical parts, pin identities, values, footprints, purchasing fields, label scope, field content/fonts/visibility, and unrelated project content intact.

Read [the approved examples](references/examples.md) before the first layout pass. They explain the intended compactness and distinguish example dimensions from general rules.

## Connection tidying — six rules

1. **Compact complete local circuits.** Move support parts and reshape shared wires together. Remove unnecessary empty rail length and large return loops. Reaching a pin-length metric alone does not complete the layout. Keep a readable association between each IC and its support circuit.

2. **Target 100 mil at pin interfaces.** Measure from the electrical pin endpoint to the first bend, real junction, label/power anchor, or connected symbol pin. Target exactly 100 mil (2.54 mm), with no shorter lead. Extend only to clear a specific nearby pin or its routing, using the smallest necessary 50 mil step and recording the blocker. Move the surrounding circuit before retaining a long lead. NC markers and coincident stacked pins internal to a symbol are exempt. Count floating touching stubs separately from real connections.

3. **Give comparable passive branches breathing room.** Use 300 mil (7.62 mm) between centre columns of ordinary parallel passive branches, such as neighboring resistor/capacitor branches sharing a rail. Match comparable pairs; increase in 50 mil steps when actual symbol or pin extents require it. This is independent of the 100 mil lead rule. Do not apply this pitch to every symbol, IC, bank, or different branch orientation.

4. **Move fields into nearby free space.** Put references and values outside narrow branch gaps, clearly associated with their parts. Clear bodies, pins, wires, labels, and other text. Preserve content, font size and visibility; use consistent anchors for comparable parts. No universal numerical text clearance has been agreed.

5. **Choose groups before routing between them.** Keep short, readable direct connections within each local group, using short shared rails and local grounds. Where an inter-group wire wraps around components or forces unnecessary separation/crossings, replace that span with matching net labels and compact the groups independently. Anchor labels exactly at accessible wire endpoints. Preserve existing names and scope; deliberately name previously unnamed nets where needed, documenting the rename and proving that complete pin partitions are unchanged. Do not merge distinct nets or convert local labels into global labels to simplify routing.

6. **Check geometry and native connectivity.** Use the 50 mil (1.27 mm) grid for local wire endpoints and placement. Preserve orthogonal wiring. Compare native component data and complete net-to-pin partitions, run ERC including exclusions, and inspect rendered output. Require an explicit junction dot at a drawn T or other three-or-more-arm wire branch. Verify actual native nets; visual contact is insufficient. Intentional interior crossings remain unconnected without a dot. Report pre-existing junction faults as unresolved failures, even when before/after connectivity is unchanged. Read [verification guidance](references/verification.md) for the checker, evidence requirements and its limitations.

## Sheet organisation — six rules

1. **Use A4 sheets.** Use A3 or larger only when the user explicitly requests it. If a complete group cannot fit A4 under these rules, report the constraint before enlarging the sheet or splitting the group.

2. **Minimise each circuit box.** Call the blue functional boundary a circuit box. Compact the complete local circuit under the connection-tidying rules, then fit its box to the full visible extent of components, pins, fields, wires, labels and power symbols. Do not retain empty space merely to match the old box size.

3. **Keep 300 mil internal clearance.** Measure from each box edge's centreline to the outermost visible circuit content on that side. Target 300 mil (7.62 mm), never less. Exact outer box placement and the absolute 50 mil electrical grid take priority: add only the smallest necessary padding, less than 50 mil per edge. Keep the heading within the upper margin and separate engineering notes outside the boxes. Hidden properties do not enlarge visible-content bounds.

4. **Keep boxes clear of the drawing border.** Measure from the actual inner drawing border, not the physical paper edge. Start the first row 100 mil (2.54 mm) below it and each row 100 mil to its right. Keep at least 100 mil clear of the right/bottom inner border and title block. Leave unused sheet area rather than stretching circuits to its far edges.

5. **Pack left-to-right, then top-to-bottom.** Retain the existing functional reading order unless directed otherwise. Align box tops within a row and leave exactly 200 mil (5.08 mm) horizontally between adjacent boxes. When the next complete box cannot fit the usable width, start a new row exactly 200 mil below the bottom of the tallest box in the preceding row. Measure gaps between box edge centrelines.

6. **Preserve and verify.** Translate complete electrical groups on the 50 mil grid, preserving their internal geometry unless connection tidying requires further compaction. Keep parts, fields, wires, junctions, labels and NC markers together. Check paper size, visible-content padding, border/title-block clearances, box gaps and row order in addition to the native checks below. Read [the sheet-organisation example](references/examples.md#sheet-organisation--accepted-circuit-box-packing) when judging the intended arrangement.

## Workflow

- Identify the requested root/sheets and current saved state. Preserve manual saves and project/library resolution. Snapshot affected native sources and retain hashes before editing; never replay a historical coordinate editor over a later save.
- Capture fresh baseline netlist/ERC evidence. Existing electrical faults remain visible in the final result. A presentation task does not authorise connecting previously separate nets to repair them.
- Edit an isolated candidate first. Tidy connections within local groups, then fit and pack circuit boxes when sheet organisation is in scope. Render the whole sheet and useful close-ups. Inspect text, pin/body collisions, junctions, label anchors, box placement and spacing allowances.
- Verify the candidate against its baseline. Explain intentional net renames separately from electrical changes. If source hashes changed while working, preserve the new saves and rebase the candidate rather than overwrite them. Apply only verified edits within the requested scope.
- Report changed groups, measured pin-lead exceptions and box-padding allowances, connectivity/ERC/junction results and remaining faults. Presentation checks do not establish electrical qualification.

Prefer native-file/CLI workflows for deterministic edits and exports. When GUI work is needed, use exact-window background control that preserves the foreground app and input focus; stop and explain if that cannot complete the action. Do not change PCB placement/routing, part choices or circuit architecture under this skill.

The bundled script is a read-only junction check, not a layout editor or automatic implementation of either pass. Dependencies: Python 3 standard library and `kicad-cli` with schematic XML-netlist/JSON-ERC export support.
