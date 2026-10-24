"""Read-only branch/junction audit for existing KiCad schematics.

Scan the active sheet hierarchy, not backup/autosave globs. Check explicit
junction dots against wire contacts, then attach fresh native netlist/ERC
evidence. This checks exact contacts, not near misses or general layout.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


def parse(text):
    """Read the small S-expression subset needed here; retain no edit spans."""
    stack = []
    root = None
    for match in re.finditer(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        token = match.group()
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            else:
                root = node
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if stack or root is None:
        raise ValueError('Incomplete schematic S-expression')
    return root


def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def one(node, key):
    result = children(node, key)
    if len(result) != 1:
        raise ValueError(f'Expected one {key}, got {len(result)}')
    return result[0]


def xy(node):
    # KiCad coordinates have nanometre resolution. Integer coordinates make
    # a real contact distinct from a very small gap; no snapping/tolerance.
    return tuple(round(float(n) * 1_000_000) for n in node[1:3])


def contains(p, a, b):
    return ((p[0]-a[0])*(b[1]-a[1]) == (p[1]-a[1])*(b[0]-a[0])
            and min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def direction(p, q):
    dx, dy = q[0]-p[0], q[1]-p[1]
    divisor = math.gcd(abs(dx), abs(dy))
    return dx//divisor, dy//divisor


def contacts(wires, dots):
    """Return branches, preserving ordinary dotless crossing/bend behavior."""
    candidates = set(dots) | {p for w in wires for p in (w['a'], w['b'])}
    result = []
    for p in sorted(candidates):
        touching = [i for i, w in enumerate(wires) if contains(p, w['a'], w['b'])]
        rays = {direction(p, q) for i in touching for q in (wires[i]['a'], wires[i]['b']) if q != p}
        if len(rays) >= 3:
            result.append({'point': p, 'wires': touching, 'arms': len(rays),
                           'has_dot': p in dots})
    return result


class Groups:
    def __init__(self, count):
        self.parent = list(range(count))

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def join(self, indexes):
        indexes = list(indexes)
        if indexes:
            head = self.find(indexes[0])
            for i in indexes[1:]:
                self.parent[self.find(i)] = head


def wire_groups(wires, dots):
    """Do not infer an endpoint-to-interior join from visual coincidence."""
    groups = Groups(len(wires))
    ends = defaultdict(list)
    for i, wire in enumerate(wires):
        for p in [wire['a'], wire['b']]:
            ends[p].append(i)
    for indexes in ends.values():
        groups.join(indexes)
    for p in dots:
        groups.join(i for i, w in enumerate(wires) if contains(p, w['a'], w['b']))
    return groups


def sheet_data(path):
    tree = parse(path.read_text())
    wires = [{'a': xy(one(w, 'pts')[1]), 'b': xy(one(w, 'pts')[2]),
              'uuid': one(w, 'uuid')[1]} for w in children(tree, 'wire')]
    dots = {xy(one(n, 'at')) for n in children(tree, 'junction')}
    definitions = {s[1]: s for s in children(one(tree, 'lib_symbols'), 'symbol')}
    terminals = []
    for symbol in children(tree, 'symbol'):
        library = one(symbol, 'lib_id')[1]
        if library.startswith('power:'):
            continue  # Native netlists omit virtual power symbols.
        at = one(symbol, 'at')
        origin = xy(at)
        angle = math.radians(float(at[3]))
        props = {p[1]: p[2] for p in children(symbol, 'property')}
        pin_ids = {p[1]: one(p, 'uuid')[1] for p in children(symbol, 'pin')}
        mirrors = children(symbol, 'mirror')
        unit = int(one(symbol, 'unit')[1])
        for shape in children(definitions[library], 'symbol'):
            shape_unit, style = map(int, shape[1].rsplit('_', 2)[1:])
            if shape_unit not in [0, unit] or style not in [0, 1]:
                continue
            for pin in children(shape, 'pin'):
                x, y = xy(one(pin, 'at'))
                dx = x*math.cos(angle)-y*math.sin(angle)
                dy = -(x*math.sin(angle)+y*math.cos(angle))
                if mirrors:
                    if 'x' in mirrors[0][1:]:
                        dy = -dy
                    if 'y' in mirrors[0][1:]:
                        dx = -dx
                number = one(pin, 'number')[1]
                terminals.append({'point': (round(origin[0]+dx), round(origin[1]+dy)),
                                  'symbol_uuid': one(symbol, 'uuid')[1],
                                  'pin': number, 'pin_uuid': pin_ids.get(number),
                                  'default_ref': props['Reference']})
    return tree, wires, dots, terminals


def hierarchy(root):
    """Keep every repeated-sheet instance while reading each file once."""
    sources = {}
    instances = defaultdict(list)

    def visit(path, sheet_path, ancestors):
        path = path.resolve()
        if path in ancestors:
            raise ValueError(f'Recursive sheet hierarchy: {path}')
        if path not in sources:
            sources[path] = sheet_data(path)
        instances[path].append(sheet_path)
        for sheet in children(sources[path][0], 'sheet'):
            props = {p[1]: p[2] for p in children(sheet, 'property')}
            visit(path.parent/props['Sheetfile'], sheet_path+props['Sheetname']+'/', ancestors | {path})

    visit(root, '/', set())
    return sources, instances


def native_maps(netlist):
    tree = ET.parse(netlist)
    references = {}
    for comp in tree.findall('./components/comp'):
        # Multi-unit components export one source UUID per unit, separated by
        # spaces. Any of those units must map to the same physical reference.
        for stamp in (comp.findtext('tstamps') or '').split():
            references[(comp.find('sheetpath').attrib['names'], stamp)] = comp.attrib['ref']
    pins = {}
    for net in tree.findall('./nets/net'):
        for node in net.findall('node'):
            pins[(node.attrib['ref'], node.attrib['pin'])] = {'code': net.attrib['code'], 'name': net.attrib['name']}
    return references, pins


def inspect_sheet(wires, dots, terminals, instances, references, native_pins, erc):
    groups = wire_groups(wires, dots)
    terminals_by_group = defaultdict(list)
    for terminal in terminals:
        roots = {groups.find(i) for i, w in enumerate(wires) if contains(terminal['point'], w['a'], w['b'])}
        for group in roots:
            terminals_by_group[group].append(terminal)
    findings = []
    for contact in contacts(wires, dots):
        relevant_groups = sorted({groups.find(i) for i in contact['wires']})
        evidence = []
        mismatch = False
        for instance in instances:
            branches = []
            all_codes = set()
            for group in relevant_groups:
                members = []
                for terminal in terminals_by_group[group]:
                    reference = references.get((instance, terminal['symbol_uuid']))
                    net = native_pins.get((reference, terminal['pin']))
                    if net is not None:
                        all_codes.add(net['code'])
                        members.append({'reference': reference, 'pin': terminal['pin'],
                                        'pin_uuid': terminal['pin_uuid'], 'native_net': net['name'],
                                        'native_net_code': net['code']})
                branches.append(members)
            mismatch |= len(all_codes) > 1
            pin_ids = {pin['pin_uuid'] for branch in branches for pin in branch}
            erc_matches = [v for sheet in erc['sheets'] if sheet['path'] == instance
                           for v in sheet['violations'] if any(i.get('uuid') in pin_ids for i in v['items'])]
            evidence.append({'sheet_instance': instance, 'wire_groups': branches,
                             'different_native_nets': len(all_codes) > 1,
                             'erc_findings': erc_matches})
        if contact['has_dot'] and not mismatch:
            continue
        p = contact['point']
        findings.append({'rule': 'junction_native_net_mismatch' if contact['has_dot'] else 'branch_missing_junction_dot',
                         'position_mm': [v/1_000_000 for v in p],
                         'position_mil': [v/25_400 for v in p], 'arms': contact['arms'],
                         'has_explicit_junction': contact['has_dot'],
                         'wire_uuids': [wires[i]['uuid'] for i in contact['wires']],
                         'different_native_nets_at_contact': mismatch,
                         'native_instances': evidence})
    return findings


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root, output):
    root = root.resolve()
    output = output.resolve()
    sources, instances = hierarchy(root)
    # Never reuse stale exports or overwrite an earlier audit's evidence.
    output.mkdir(parents=True, exist_ok=False)
    guarded = set(sources)
    project = root.with_suffix('.kicad_pro')
    if project.exists():
        guarded.add(project)
    before = {p: sha(p) for p in guarded}
    try:
        for args in [
            ['export', 'netlist', '--format', 'kicadxml', '-o', str(output/'native-netlist.xml')],
            ['erc', '--severity-all', '--format', 'json', '-o', str(output/'native-erc.json')]]:
            result = subprocess.run(['kicad-cli', 'sch']+args+[str(root)], text=True, capture_output=True)
            if result.returncode:
                raise RuntimeError(result.stderr or result.stdout)
        references, pins = native_maps(output/'native-netlist.xml')
        erc = json.loads((output/'native-erc.json').read_text())
        findings = []
        for path, (_, wires, dots, terminals) in sources.items():
            findings.extend({'source_file': str(path), **finding} for finding in
                            inspect_sheet(wires, dots, terminals, instances[path], references, pins, erc))
        report = {'status': 'FAIL' if findings else 'PASS', 'root': str(root),
                  'source_file_count': len(sources), 'sheet_instance_count': sum(map(len, instances.values())),
                  'finding_count': len(findings),
                  'sheet_instance_contacts': sum(len(f['native_instances']) for f in findings),
                  'findings': findings, 'checked_source_sha256': {str(p): h for p, h in before.items()},
                  'scope': 'Exact branch contacts, junction dots and native net evidence; no near-miss or full layout audit.'}
        (output/'junction-check.json').write_text(json.dumps(report, indent=2)+'\n')
        lines = [f"{report['status']}: {len(findings)} junction discrepancies",
                 f"{len(sources)} source files; {report['sheet_instance_count']} sheet instances.", '']
        for finding in findings:
            lines.append(f"- {Path(finding['source_file']).name} at {finding['position_mm']} mm: {finding['rule']}; "
                         f"different native nets: {finding['different_native_nets_at_contact']}.")
            for instance in finding['native_instances']:
                pins_at_contact = sorted({f"{p['reference']}.{p['pin']} ({p['native_net']})"
                                          for branch in instance['wire_groups'] for p in branch})
                lines.append(f"  - {instance['sheet_instance']}: {', '.join(pins_at_contact)}")
        (output/'junction-check.md').write_text('\n'.join(lines)+'\n')
    finally:
        changed = [str(p) for p, h in before.items() if sha(p) != h]
        if changed:
            raise RuntimeError(f'Source files changed during audit: {changed}')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='Root .kicad_sch of the active project')
    parser.add_argument('--output', required=True, type=Path, help='Directory for audit reports and native exports')
    args = parser.parse_args()
    try:
        report = audit(args.root, args.output)
    except (OSError, ValueError, KeyError, IndexError, ET.ParseError, RuntimeError) as error:
        print(f'ERROR: junction audit incomplete: {error}', file=sys.stderr)
        return 2
    print(f"{report['status']}: {report['finding_count']} junction discrepancies "
          f"({report['sheet_instance_contacts']} sheet-instance contacts). Source hashes unchanged.")
    return 1 if report['findings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
