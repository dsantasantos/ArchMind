import json
import re
from typing import Any

def safe_parse_json(text: str, expected_type: type = list) -> Any:
    """
    Tenta extrair e parsear JSON de uma string, lidando com markdown e texto extra.
    """
    if not text:
        return [] if expected_type is list else {}

    # 1. Tenta parsear a string direta
    try:
        data = json.loads(text.strip())
        if isinstance(data, expected_type):
            return data
    except json.JSONDecodeError:
        pass

    # 2. Busca por blocos de código markdown ```json ... ```
    md_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if md_match:
        try:
            data = json.loads(md_match.group(1))
            if isinstance(data, expected_type):
                return data
        except json.JSONDecodeError:
            pass

    # 3. Busca pelo padrão mais abrangente [...] ou {...}
    pattern = r"\[.*\]" if expected_type is list else r"\{.*\}"
    json_match = re.search(pattern, text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if isinstance(data, expected_type):
                return data
        except json.JSONDecodeError:
            # Tenta uma versão menos gananciosa se falhar (caso haja texto após o JSON)
            # Isso é útil se o LLM escrever algo depois do array
            inner_match = re.search(pattern.replace(".*", ".*?"), text, re.DOTALL)
            if inner_match:
                try:
                    data = json.loads(inner_match.group())
                    if isinstance(data, expected_type):
                        return data
                except json.JSONDecodeError:
                    pass

    return [] if expected_type is list else {}
