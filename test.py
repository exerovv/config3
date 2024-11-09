import unittest
import xml.etree.ElementTree as ET
from io import StringIO
import sys
from main import parse_config


class TestParseConfig(unittest.TestCase):

    def setUp(self):
        # Set up necessary resources for tests (like file input or configuration text)
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

    def test_parse_valid_config(self):
        # Test the valid config string
        xml_root = parse_config(self.valid_config)

        # Check the structure of the XML
        self.assertEqual(len(xml_root.findall("constant")), 1)
        self.assertEqual(len(xml_root.findall("array")), 1)
        self.assertEqual(len(xml_root.findall("evaluation")), 2)

        # Check the correct content for constant
        const_elem = xml_root.find(".//constant[@name='PI']")
        self.assertIsNotNone(const_elem)
        self.assertEqual(const_elem.text, "3.14")

        # Check array content
        array_elem = xml_root.find(".//array[@name='COLORS']")
        self.assertIsNotNone(array_elem)
        items = array_elem.findall("item")
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].text, "red")
        self.assertEqual(items[1].text, "green")
        self.assertEqual(items[2].text, "blue")

    def test_parse_invalid_config(self):
        # Test the invalid config string (undefined constant)
        with self.assertRaises(SyntaxError):
            parse_config(self.invalid_config)

    def test_parse_empty_config(self):
        # Test the empty config string (should return an empty XML root)
        xml_root = parse_config(self.empty_config)
        self.assertEqual(len(xml_root.findall(".//constant")), 0)
        self.assertEqual(len(xml_root.findall(".//array")), 0)
        self.assertEqual(len(xml_root.findall(".//evaluation")), 0)

    def test_parse_number(self):
        # Test parsing of numbers
        config = "42"
        xml_root = parse_config(config)
        number_elem = xml_root.find(".//number")
        self.assertIsNotNone(number_elem)
        self.assertEqual(number_elem.text, "42")

    def test_parse_string(self):
        # Test parsing of strings
        config = '"Hello World"'
        xml_root = parse_config(config)
        string_elem = xml_root.find(".//string")
        self.assertIsNotNone(string_elem)
        self.assertEqual(string_elem.text, "Hello World")

    def test_parse_array(self):
        # Test parsing of array
        config = '#("apple" "banana" "cherry")'
        xml_root = parse_config(config)
        array_elem = xml_root.find(".//array")
        self.assertIsNotNone(array_elem)
        items = array_elem.findall("item")
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].text, "apple")
        self.assertEqual(items[1].text, "banana")
        self.assertEqual(items[2].text, "cherry")


if __name__ == "__main__":
    unittest.main()
