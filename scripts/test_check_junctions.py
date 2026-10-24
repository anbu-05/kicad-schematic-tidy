"""Behavior tests for branch detection; no layout implementation snapshots."""
import unittest
from pathlib import Path
import subprocess
import sys
import tempfile
from check_junctions import contacts, wire_groups, inspect_sheet, native_maps


def wire(a, b):
    return {'a': a, 'b': b, 'uuid': f'{a}:{b}'}


class JunctionChecks(unittest.TestCase):
    def test_branch_to_continuous_wire_needs_dot(self):
        wires = [wire((0, 0), (10, 0)), wire((5, 0), (5, 5))]
        result = contacts(wires, set())
        self.assertEqual([(r['point'], r['arms'], r['has_dot']) for r in result], [((5, 0), 3, False)])
        groups = wire_groups(wires, set())
        self.assertNotEqual(groups.find(0), groups.find(1))

    def test_three_endpoint_branch_still_requires_visible_dot(self):
        result = contacts([wire((0, 0), (5, 0)), wire((5, 0), (10, 0)), wire((5, 0), (5, 5))], set())
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]['has_dot'])

    def test_explicit_dot_joins_and_passes(self):
        wires = [wire((0, 0), (10, 0)), wire((5, 0), (5, 5))]
        groups = wire_groups(wires, {(5, 0)})
        self.assertEqual(groups.find(0), groups.find(1))
        self.assertEqual(inspect_sheet(wires, {(5, 0)}, [], ['/'], {}, {}, {'sheets': []}), [])

    def test_interior_crossing_is_not_reported(self):
        wires = [wire((0, 0), (10, 0)), wire((5, -5), (5, 5))]
        self.assertEqual(contacts(wires, set()), [])

    def test_four_way_contact_with_endpoint_requires_dot(self):
        wires = [wire((0, 0), (10, 0)), wire((5, -5), (5, 0)), wire((5, 0), (5, 5))]
        self.assertEqual(contacts(wires, set())[0]['arms'], 4)

    def test_bend_and_straight_split_are_not_branches(self):
        self.assertEqual(contacts([wire((0, 0), (5, 0)), wire((5, 0), (5, 5))], set()), [])
        self.assertEqual(contacts([wire((0, 0), (5, 0)), wire((5, 0), (10, 0))], set()), [])

    def test_tiny_gap_is_not_snapped_into_a_contact(self):
        self.assertEqual(contacts([wire((0, 0), (10, 0)), wire((5, 1), (5, 5))], set()), [])

    def test_native_different_nets_are_reported_as_evidence(self):
        wires = [wire((0, 0), (10, 0)), wire((5, 0), (5, 5))]
        terminals = [{'point': (0, 0), 'symbol_uuid': 'r', 'pin': '2', 'pin_uuid': 'rp'},
                     {'point': (5, 5), 'symbol_uuid': 'c', 'pin': '1', 'pin_uuid': 'cp'}]
        refs = {('/', 'r'): 'R1', ('/', 'c'): 'C1'}
        nets = {('R1', '2'): {'code': '1', 'name': 'SENSE'},
                ('C1', '1'): {'code': '2', 'name': 'unconnected-C1'}}
        result = inspect_sheet(wires, set(), terminals, ['/'], refs, nets, {'sheets': []})
        self.assertTrue(result[0]['different_native_nets_at_contact'])
        # Even an explicit drawn dot must fail if the native nets disagree.
        result = inspect_sheet(wires, {(5, 0)}, terminals, ['/'], refs, nets, {'sheets': []})
        self.assertEqual(result[0]['rule'], 'junction_native_net_mismatch')

    def test_same_native_net_elsewhere_does_not_excuse_missing_local_dot(self):
        wires = [wire((0, 0), (10, 0)), wire((5, 0), (5, 5))]
        terminals = [{'point': (0, 0), 'symbol_uuid': 'r', 'pin': '2', 'pin_uuid': 'rp'},
                     {'point': (5, 5), 'symbol_uuid': 'c', 'pin': '1', 'pin_uuid': 'cp'}]
        refs = {('/', 'r'): 'R1', ('/', 'c'): 'C1'}
        nets = {('R1', '2'): {'code': '1', 'name': 'SENSE'},
                ('C1', '1'): {'code': '1', 'name': 'SENSE'}}
        result = inspect_sheet(wires, set(), terminals, ['/'], refs, nets, {'sheets': []})
        self.assertEqual(result[0]['rule'], 'branch_missing_junction_dot')
        self.assertFalse(result[0]['different_native_nets_at_contact'])

    def test_multi_unit_native_reference_mapping(self):
        with tempfile.TemporaryDirectory() as folder:
            netlist = Path(folder)/'native.xml'
            netlist.write_text('<export><components><comp ref="U1">'
                               '<sheetpath names="/GROUP/"/><tstamps>unit-a unit-b</tstamps>'
                               '</comp></components><nets/></export>')
            references, _ = native_maps(netlist)
            self.assertEqual(references[('/GROUP/', 'unit-a')], 'U1')
            self.assertEqual(references[('/GROUP/', 'unit-b')], 'U1')

    def test_incomplete_audit_has_distinct_exit_status(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('check_junctions.py')),
                                     str(Path(folder)/'absent.kicad_sch'), '--output', str(Path(folder)/'audit')],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('audit incomplete', result.stderr)


if __name__ == '__main__':
    unittest.main()
