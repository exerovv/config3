import sys
import xml.etree.ElementTree as ET
import re
import xml.dom.minidom

COMMENT_LINE = r"::.*"
COMMENT_BLOCK = r"--\[\[.*?\]\]"
ARRAY = r"#\((.*?)\)"
STRING = r"\"(.*?)\""
NUMBER = r"\b\d+\b"
CONST_DECLARATION = r"\(def\s+([_a-zA-Z][_a-zA-Z0-9]*)\s+(.*?)\);"
CONST_EVALUATION = r"\?\{([_a-zA-Z][_a-zA-Z0-9]*)\}"

constants = {}

def parse_config(input_text):
    xml_root = ET.Element("config")
    input_text = re.sub(COMMENT_LINE, '', input_text)
    input_text = re.sub(COMMENT_BLOCK, '', input_text, flags=re.DOTALL)
    lines = input_text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        const_decl = re.match(CONST_DECLARATION, line)
        if const_decl:
            name, value = const_decl.groups()
            if re.match(ARRAY, value):
                array_elem = ET.SubElement(xml_root, "array", name=name)
                values = re.findall(r'"(.*?)"|(\d+)', value)
                for val in values:
                    item_elem = ET.SubElement(array_elem, "item")
                    item_elem.text = val[0] if val[0] else val[1]
            else:
                constants[name] = value
                const_elem = ET.SubElement(xml_root, "constant", name=name)
                const_elem.text = value.strip('"')
            continue

        const_eval = re.match(CONST_EVALUATION, line)
        if const_eval:
            name = const_eval.group(1)
            value = constants.get(name, "undefined")
            if value == "undefined":
                raise SyntaxError(f"Constant '{name}' is undefined")
            eval_elem = ET.SubElement(xml_root, "evaluation", name=name)
            eval_elem.text = value
            continue

        array_match = re.match(ARRAY, line)
        if array_match:
            values = re.findall(r'"(.*?)"|(\d+)', array_match.group(1))
            array_elem = ET.SubElement(xml_root, "array")
            for val in values:
                item_elem = ET.SubElement(array_elem, "item")
                item_elem.text = val[0] if val[0] else val[1]
            continue

        if re.match(NUMBER, line):
            num_elem = ET.SubElement(xml_root, "number")
            num_elem.text = line
        elif re.match(STRING, line):
            str_elem = ET.SubElement(xml_root, "string")
            str_elem.text = line.strip('"')
        else:
            raise SyntaxError(f"Unknown syntax: {line}")

    return xml_root

def main():
    if len(sys.argv) != 2:
        print("Usage: python config_to_xml.py <path_to_config_file>")
        sys.exit(1)
    file_path = sys.argv[1]

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            input_text = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    try:
        xml_root = parse_config(input_text)
        xml_str = ET.tostring(xml_root, encoding='unicode')
        xml_pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="    ")
        print(xml_pretty)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")

if __name__ == "__main__":
    main()