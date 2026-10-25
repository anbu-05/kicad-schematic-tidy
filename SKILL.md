---
name: kicad-schematic-tidy
description: Tidy existing KiCad schematics with a symbol-outlier scan, optional authorised symbol compaction, connection tidying and A4 circuit-box organisation. Preserve native connectivity; use for schematic presentation edits or reviews, not PCB layout, part selection or circuit redesign.
---

# KiCad schematic tidy

Use **Step 0: symbol compaction**, when needed and authorised, then **Step 1: connection tidying** and **Step 2: sheet organisation**. Whenever this skill is explicitly invoked or selected automatically, start with the Step 0 scan in the requested scope. For a general sheet-tidying request, complete or skip Step 0 before running Steps 1 and 2 once, in order. Requests limited to one step, group or read-only review retain that scope. Work from electrical pin endpoints and connected local groups. Project-specific constraints and explicit user choices take precedence. Keep physical parts, pin identities, values, footprints, purchasing fields, label scope, field content/fonts/visibility, and unrelated project content intact.

Read [the approved examples](references/examples.md) before the first layout pass. They explain the intended compactness and distinguish example dimensions from general rules.

## Step 0: symbol compaction — conditional

1. **Scan for outliers before tidying.** Look for avoidable empty body space, unexplained uneven pin spacing, or disproportionate size compared with symbols of similar pin count, name lengths and functional needs. Inspect distinct placed symbol definitions, including their units/body styles and differing cached geometry, rather than every repeated component. Stop the initial scan at the first clear hit; if none is found in scope, skip Step 0. Use comparative judgment with a concrete reason, not a numerical eligibility threshold. Poor arrangement supports a finding; size, asymmetry or side-mounted grounds alone do not establish one. Leave already reasonable symbols alone.

2. **Ask about permission and exceptions at the first hit.** Show the candidate and why it qualifies, then ask whether schematic symbols may be changed and whether any components, symbols or libraries must be left unchanged. Wait before library or schematic mutations and before starting later steps. If permission is declined, preserve symbols and continue with the requested later steps. Honour existing explicit permission and exceptions without asking again. Once allowed, finish identifying eligible definitions in scope; the early exit is a permission trigger, not a limit of one symbol per run. A review-only request remains read-only.

3. **Analyse the actual circuit first.** Resolve the library actually used, inspect the placed pin connections and support network, and explain the proposed grouping and geometry before applying it. Keep useful associations such as bootstrap pins and their capacitor. Identify affected placed instances and shared-library users; avoid changing out-of-scope instances by using a project-local variant when needed. Preserve global/vendor libraries outside the authorised scope.

4. **Compact for comparable readability.** Remove unexplained gaps, arrange related pins coherently, align useful rows, and fit the body around readable names and practical routing. Use the 50 mil connection grid. Retain text sizes and drawn-pin lengths unless a specific change is justified. Regular spacing and grounds below are useful when suited to the circuit, not mandatory arrangements. Example body dimensions and pin pitches are not universal targets; the external 100 mil wire-interface rule in Step 1 is separate from drawn-pin length.

5. **Preserve electrical meaning and part data.** Keep every pin number, name, electrical type, visibility, unit/body-style assignment and instance identity. Do not remove, merge, stack or hide pins to save space. Preserve physical pad mapping, values, footprints, purchasing fields, property content/fonts/visibility, label scope and NC status. Record any necessary project-local variant identifier change separately from electrical identity.

6. **Finish by updating and verifying placed instances.** Work on an isolated candidate with recovery and source guards. Update the approved local-library geometry and its placed schematic instances within scope; move attached wires, junctions, labels, NC markers and support components by original pin identity, not by old coordinates. Step 0 is not complete at a library-only preview. Verify pin semantics, complete native net-to-pin partitions, component data, ERC including exclusions, library consistency, explicit junctions and rendered appearance before proceeding to the requested later steps. Existing faults remain reported. Compare component unit-pin membership independently of native XML ordering, which can follow drawing position. Read [symbol-compaction examples and completion checks](references/symbol-compaction.md) when a candidate qualifies.

## Step 1: connection tidying — six rules

1. **Compact complete local circuits.** Move support parts and reshape shared wires together. Remove unnecessary empty rail length and large return loops. Reaching a pin-length metric alone does not complete the layout. Keep a readable association between each IC and its support circuit.

2. **Target 100 mil at pin interfaces.** Measure from the electrical pin endpoint to the first bend, real junction, label/power anchor, or connected symbol pin. Target exactly 100 mil (2.54 mm), with no shorter lead. Extend only to clear a specific nearby pin or its routing, using the smallest necessary 50 mil step and recording the blocker. Move the surrounding circuit before retaining a long lead. NC markers and coincident stacked pins internal to a symbol are exempt. Count floating touching stubs separately from real connections.

3. **Give comparable passive branches breathing room.** Use 300 mil (7.62 mm) between centre columns of ordinary parallel passive branches, such as neighboring resistor/capacitor branches sharing a rail. Match comparable pairs; increase in 50 mil steps when actual symbol or pin extents require it. This is independent of the 100 mil lead rule. Do not apply this pitch to every symbol, IC, bank, or different branch orientation.

4. **Move fields into nearby free space.** Put references and values outside narrow branch gaps, clearly associated with their parts. Clear bodies, pins, wires, labels, and other text. Preserve content, font size and visibility; use consistent anchors for comparable parts. No universal numerical text clearance has been agreed.

5. **Choose groups before routing between them.** Keep short, readable direct connections within each local group, using short shared rails and local grounds. Where an inter-group wire wraps around components or forces unnecessary separation/crossings, replace that span with matching net labels and compact the groups independently. Anchor labels exactly at accessible wire endpoints. Preserve existing names and scope; deliberately name previously unnamed nets where needed, documenting the rename and proving that complete pin partitions are unchanged. Do not merge distinct nets or convert local labels into global labels to simplify routing.

6. **Check geometry and native connectivity.** Use the 50 mil (1.27 mm) grid for local wire endpoints and placement. Preserve orthogonal wiring. Compare native component data and complete net-to-pin partitions, run ERC including exclusions, and inspect rendered output. Require an explicit junction dot at a drawn T or other three-or-more-arm wire branch. Verify actual native nets; visual contact is insufficient. Intentional interior crossings remain unconnected without a dot. Report pre-existing junction faults as unresolved failures, even when before/after connectivity is unchanged. Read [verification guidance](references/verification.md) for the checker, evidence requirements and its limitations.

## Step 2: sheet organisation — six rules

1. **Use A4 sheets.** Use A3 or larger only when the user explicitly requests it. If a complete group cannot fit A4 under these rules, report the constraint before enlarging the sheet or splitting the group.

2. **Minimise each circuit box.** Call the blue functional boundary a circuit box. Compact the complete local circuit under the connection-tidying rules, then fit its box to the full visible extent of components, pins, fields, wires, labels and power symbols. Do not retain empty space merely to match the old box size.

3. **Keep 300 mil internal clearance.** Measure from each box edge's centreline to the outermost visible circuit content on that side. Target 300 mil (7.62 mm), never less. Exact outer box placement and the absolute 50 mil electrical grid take priority: add only the smallest necessary padding, less than 50 mil per edge. Keep the heading within the upper margin and separate engineering notes outside the boxes. Hidden properties do not enlarge visible-content bounds.

4. **Keep boxes clear of the drawing border.** Measure from the actual inner drawing border, not the physical paper edge. Start the first row 100 mil (2.54 mm) below it and each row 100 mil to its right. Keep at least 100 mil clear of the right/bottom inner border and title block. Leave unused sheet area rather than stretching circuits to its far edges.

5. **Pack left-to-right, then top-to-bottom.** Retain the existing functional reading order unless directed otherwise. Align box tops within a row and leave exactly 200 mil (5.08 mm) horizontally between adjacent boxes. When the next complete box cannot fit the usable width, start a new row exactly 200 mil below the bottom of the tallest box in the preceding row. Measure gaps between box edge centrelines.

6. **Preserve and verify.** Translate complete electrical groups on the 50 mil grid, preserving their internal geometry unless connection tidying requires further compaction. Keep parts, fields, wires, junctions, labels and NC markers together. Check paper size, visible-content padding, border/title-block clearances, box gaps and row order in addition to the native checks below. Read [the sheet-organisation example](references/examples.md#sheet-organisation--accepted-circuit-box-packing) when judging the intended arrangement.

## Workflow

- Identify the requested root/sheets and current saved state. Preserve manual saves and project/library resolution. Snapshot affected native sources and retain hashes before editing; never replay a historical coordinate editor over a later save.
- Capture fresh baseline netlist/ERC evidence. Existing electrical faults remain visible in the final result. A presentation task does not authorise connecting previously separate nets to repair them.
- Run the Step 0 scan and resolve permission/exceptions before mutations. When authorised and needed, finish symbol compaction through verified placed-instance updates. Then tidy connections within local groups (Step 1) and fit/pack circuit boxes (Step 2), as requested. Do not tidy and pack first and then repeat both because symbols were updated late. Use an isolated candidate throughout; render the whole sheet and useful close-ups. Inspect text, pin/body collisions, junctions, label anchors, box placement and spacing allowances.
- Verify the candidate against its baseline. Explain intentional net renames separately from electrical changes. If source hashes changed while working, preserve the new saves and rebase the candidate rather than overwrite them. Apply only verified edits within the requested scope.
- Report changed groups, measured pin-lead exceptions and box-padding allowances, connectivity/ERC/junction results and remaining faults. Presentation checks do not establish electrical qualification.

Prefer native-file/CLI workflows for deterministic edits and exports. When GUI work is needed, use exact-window background control that preserves the foreground app and input focus; stop and explain if that cannot complete the action. Do not change PCB placement/routing, part choices or circuit architecture under this skill.

The bundled script is a read-only junction check. It does not scan symbol eligibility, compact symbols, edit layouts or automatically implement the three steps. The Step 0 scan uses the qualitative rules above. Dependencies: Python 3 standard library and `kicad-cli` with schematic XML-netlist/JSON-ERC export support.
