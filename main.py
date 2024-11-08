import sys

COMMENT_LINE = r"::.*"
COMMENT_BLOCK = r"--\[\[.*?\]\]"
ARRAY = r"#\((.*?)\)"
STRING = r"\"(.*?)\""
NUMBER = r"\b\d+\b"
CONST_DECLARATION = r"\(def\s+([_a-zA-Z][_a-zA-Z0-9]*)\s+(.*?)\);"
CONST_EVALUATION = r"\?\{([_a-zA-Z][_a-zA-Z0-9]*)\}"

constants = {}

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

if __name__ == "__main__":
    main()