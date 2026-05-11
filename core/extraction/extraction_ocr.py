import json
import os
import sys

# Garante que o Python encontre a pasta 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extractor import DiagramExtractor

# Caminho do arquivo conforme sua estrutura local
FILE_PATH = "ArchMind\core\extraction\diagrama.png"

def run_final_extraction_test():
    print(f"--- Iniciando Pipeline de Extração ArchMind ---")
    
    # 1. Instancia o novo Extrator que criamos
    extractor = DiagramExtractor()
    
    try:
        # 2. Executa a extração completa (OpenCV + EasyOCR + Hierarquia + Formatação)
        print(f"Processando arquivo: {FILE_PATH}...")
        final_output = extractor.extract(FILE_PATH)
        
        # 3. Salva o resultado no formato final (igual às imagens do seu colega)
        output_name = "resultado_final_archmind.json"
        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
            
        print(f"--- Sucesso! ---")
        print(f"Arquivo gerado: {output_name}")
        print(f"Blocos de texto encontrados: {len(final_output['text_blocks'])}")
        print(f"Grupos de contexto detectados: {len(final_output['context_groups'])}")
        
    except Exception as e:
        print(f"Erro durante a extração: {e}")

if __name__ == "__main__":
    run_final_extraction_test()