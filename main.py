import sys
import xml.etree.ElementTree as ET
import re
import xml.dom.minidom

# Определение регулярных выражений
COMMENT_LINE = r"::.*"
COMMENT_BLOCK = r"--\[\[.*?\]\]"
ARRAY = r"#\((.*?)\)"
STRING = r"\"([^\"]*)\""
NUMBER = r"\b\d+\b"
CONST_DECLARATION = r"\(def\s+([_a-zA-Z][_a-zA-Z0-9]*)\s+(.*)\);"
CONST_EVALUATION = r"\?\{([_a-zA-Z][_a-zA-Z0-9]*)\}"

# Словарь для хранения констант
constants = {}


def parse_array(value):
    """Рекурсивный парсинг массива, поддерживающий вложенные структуры."""
    array_elem = ET.Element("array")

    # Удаляем оболочку массива #( ... )
    inner_values = value[2:-1].strip()  # Убираем только внешние символы `#(` и `)`

    # Проход по элементам массива с поддержкой вложенности
    pos = 0
    while pos < len(inner_values):
        match_str = re.match(STRING, inner_values[pos:])
        match_num = re.match(NUMBER, inner_values[pos:])
        match_array = re.match(ARRAY, inner_values[pos:])
        match_nested_array = re.match(r'#\((.*?)', inner_values[pos:])

        if match_str:
            item_elem = ET.SubElement(array_elem, "item")
            item_elem.text = match_str.group().strip('"')
            pos += len(match_str.group())
        elif match_num:
            item_elem = ET.SubElement(array_elem, "item")
            item_elem.text = match_num.group()
            pos += len(match_num.group())
        elif match_array:
            # Рекурсивно парсим вложенный массив
            nested_array = parse_array(match_array.group())
            array_elem.append(nested_array)
            pos += len(match_array.group())
        elif match_nested_array:
            nested_array = parse_array(match_nested_array.group())
            array_elem.append(nested_array)
            pos += len(match_nested_array.group())
        else:
            raise SyntaxError(f"Неизвестный синтаксис в массиве: {inner_values[pos:]}")

        # Пропуск пробелов и запятых
        while pos < len(inner_values) and inner_values[pos] in ' ,':
            pos += 1

    return array_elem


def parse_value(value):
    """Парсит значение, определяя его тип (массив, строка, число)."""
    if re.match(ARRAY, value):
        return parse_array(value)
    elif re.match(STRING, f'"{value}"') or isinstance(value, str):
        str_elem = ET.Element("string")
        str_elem.text = value.strip('"')
        return str_elem
    elif re.match(NUMBER, value):
        num_elem = ET.Element("number")
        num_elem.text = value
        return num_elem
    else:
        raise SyntaxError(f"Unknown syntax or undefined constant: {value}")


def parse_config(input_text):
    xml_root = ET.Element("config")

    # Удаление комментариев
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
            constants[name] = value.strip('"')
            const_elem = ET.SubElement(xml_root, "constant", name=name)
            const_elem.append(parse_value(value))
            continue

        const_eval = re.match(CONST_EVALUATION, line)
        if const_eval:
            name = const_eval.group(1)
            value = constants.get(name, "undefined")
            if value == "undefined":
                raise SyntaxError(f"Constant '{name}' is undefined")
            eval_elem = ET.SubElement(xml_root, "evaluation", name=name)
            eval_elem.append(parse_value(value))
            continue

        array_match = re.match(ARRAY, line)
        if array_match:
            array_elem = parse_array(array_match.group(1))
            xml_root.append(array_elem)
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
