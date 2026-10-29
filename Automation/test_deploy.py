import unittest

from deploy import CONFIG_DIR, ROOT, build_commands, find_missing, is_present, load_inventory, load_wanted, normalize, parse_entries

WANTED = parse_entries(
    "interface GigabitEthernet0/1\n"
    " ip address 10.10.100.1 255.255.255.252\n"
    " no shutdown\n"
    "router ospf 1\n"
    " router-id 1.1.1.1\n"
    " network 10.10.0.0 0.0.255.255 area 0\n"
    "crypto ikev2 keyring K\n"
    " peer P\n"
    "  address 10.0.2.2\n"
    "  pre-shared-key secret\n"
)


class ParseTests(unittest.TestCase):
    def test_nested_paths(self):
        self.assertIn(("crypto ikev2 keyring K", "peer P", "address 10.0.2.2"), WANTED)
        self.assertIn(("router ospf 1", "router-id 1.1.1.1"), WANTED)

    def test_secret_is_normalized(self):
        self.assertEqual(normalize("pre-shared-key 0 abc"), "pre-shared-key")


class DiffTests(unittest.TestCase):
    def test_full_config_has_nothing_missing(self):
        running = (
            "interface GigabitEthernet0/1\n ip address 10.10.100.1 255.255.255.252\n"
            "router ospf 1\n router-id 1.1.1.1\n network 10.10.0.0 0.0.255.255 area 0\n"
            "crypto ikev2 keyring K\n peer P\n  address 10.0.2.2\n  pre-shared-key 0 other\n"
        )
        self.assertEqual(find_missing(WANTED, running), [])

    def test_shutdown_interface_needs_no_shutdown(self):
        running = "interface GigabitEthernet0/1\n ip address 10.10.100.1 255.255.255.252\n shutdown\n"
        missing = find_missing(WANTED, running)
        self.assertIn(("interface GigabitEthernet0/1", "no shutdown"), missing)

    def test_empty_device_needs_everything(self):
        self.assertEqual(len(find_missing(WANTED, "")), len(WANTED))

    def test_second_run_sends_nothing(self):
        text = (
            "interface GigabitEthernet0/1\n ip address 10.10.100.1 255.255.255.252\n"
            "router ospf 1\n router-id 1.1.1.1\n network 10.10.0.0 0.0.255.255 area 0\n"
            "crypto ikev2 keyring K\n peer P\n  address 10.0.2.2\n  pre-shared-key secret\n"
        )
        self.assertEqual(build_commands(find_missing(WANTED, text)), [])


class RepositoryTests(unittest.TestCase):
    def test_every_inventory_device_with_files_parses(self):
        for device in load_inventory(ROOT / "inventory.yml"):
            files, wanted = load_wanted(device["name"], [])
            if files:
                self.assertTrue(wanted, device["name"])

    def test_ospf_networks_use_passive_default(self):
        for folder in CONFIG_DIR.iterdir():
            text = "\n".join(path.read_text(encoding="utf-8") for path in folder.glob("*.cfg"))
            if "router ospf 1" in text:
                self.assertIn("passive-interface default", text, folder.name)


class CommandTests(unittest.TestCase):
    def test_parents_are_emitted_once(self):
        missing = [("router ospf 1", "router-id 1.1.1.1"), ("router ospf 1", "passive-interface default")]
        self.assertEqual(build_commands(missing), ["router ospf 1", "router-id 1.1.1.1", "passive-interface default"])

    def test_nested_parents(self):
        missing = [("crypto ikev2 keyring K", "peer P", "address 10.0.2.2")]
        self.assertEqual(build_commands(missing), ["crypto ikev2 keyring K", "peer P", "address 10.0.2.2"])

    def test_is_present_requires_parent(self):
        self.assertFalse(is_present(("interface X", "no shutdown"), set()))


if __name__ == "__main__":
    unittest.main()
