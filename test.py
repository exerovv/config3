import unittest
from main import parse_config


class TestParseConfig(unittest.TestCase):

    def setUp(self):
        self.valid_config = """
        (def PI 3.14);
        (def COLORS #("red" "green" "blue"));
        ?{PI}
        ?{COLORS}
        """
        self.invalid_config = """
        (def PI 3.14);
        ?{UNDEFINED_CONST}
        """
        self.empty_config = ""

    def test_parse_invalid_config(self):
        with self.assertRaises(SyntaxError):
            parse_config(self.invalid_config)

    def test_parse_empty_config(self):
        xml_root = parse_config(self.empty_config)
        self.assertEqual(len(xml_root.findall(".//constant")), 0)
        self.assertEqual(len(xml_root.findall(".//array")), 0)
        self.assertEqual(len(xml_root.findall(".//evaluation")), 0)

    def test_parse_number(self):
        config = "42"
        xml_root = parse_config(config)
        number_elem = xml_root.find(".//number")
        self.assertIsNotNone(number_elem)
        self.assertEqual(number_elem.text, "42")

    def test_parse_string(self):
        config = '"Hello World"'
        xml_root = parse_config(config)
        string_elem = xml_root.find(".//string")
        self.assertIsNotNone(string_elem)
        self.assertEqual(string_elem.text, "Hello World")

    def test_parse_array(self):
        config = '#(  "apple" "banana" "cherry" )'
        xml_root = parse_config(config)
        array_elem = xml_root.find(".//array")
        self.assertIsNotNone(array_elem)
        items = array_elem.findall("item")
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].text, "apple")
        self.assertEqual(items[1].text, "banana")
        self.assertEqual(items[2].text, "cherry")

    def test_parse_nested_array(self):
        config = '(def style #("красный" "зеленый" "синий" ?{colors}));'
        xml_root = parse_config(config)
        outer_array_elem = xml_root.find(".//array")
        self.assertIsNotNone(outer_array_elem)
        items = outer_array_elem.findall("item")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].text, "outer")
        self.assertEqual(items[1].text, "outer2")

        inner_array_elem = outer_array_elem.find("array")
        self.assertIsNotNone(inner_array_elem)
        inner_items = inner_array_elem.findall("item")
        self.assertEqual(len(inner_items), 2)
        self.assertEqual(inner_items[0].text, "inner1")
        self.assertEqual(inner_items[1].text, "inner2")

if __name__ == "__main__":
    unittest.main()
