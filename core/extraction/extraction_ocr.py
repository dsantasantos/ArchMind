import json
import easyocr
from PIL import Image
import numpy as np
from ultralytics import YOLO
import cv2

FILE_PATH = "core\\extraction\\diagrama.png"

# Verifica se box_inner está contido em box_outer
def is_inside(box_inner, box_outer):
    in_x, in_y, in_w, in_h = box_inner
    out_x, out_y, out_w, out_h = box_outer
    
    return (in_x >= out_x and 
            in_y >= out_y and 
            (in_x + in_w) <= (out_x + out_w) and 
            (in_y + in_h) <= (out_y + out_h))

def test_hierarchical_extraction():
    reader = easyocr.Reader(['pt'])
    img = cv2.imread(FILE_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold para detecção de bordas
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    raw_components = []
    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 30 or h < 20 or w > img.shape[1] * 0.95: continue
        
        # Faz o OCR da região
        roi = img[y:y+h, x:x+w]
        ocr_result = reader.readtext(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        text = " ".join([res[1] for res in ocr_result]).strip()
        
        if text:
            raw_components.append({
                "id": f"box_{i}",
                "text": text,
                "bbox": (x, y, w, h)
            })

    # Lógica de Hierarquia
    final_components = []
    for i, comp_a in enumerate(raw_components):
        parent_id = None
        # Compara com todos os outros para ver se está dentro de algum
        for j, comp_b in enumerate(raw_components):
            if i == j: continue
            if is_inside(comp_a["bbox"], comp_b["bbox"]):
                parent_id = comp_b["id"]
                break # Pega o primeiro pai encontrado
        
        x, y, w, h = comp_a["bbox"]
        final_components.append({
            "id": comp_a["id"],
            "parent_id": parent_id,
            "text": comp_a["text"],
            "geometry": {"x": x, "y": y, "w": w, "h": h}
        })

    with open("resultado_hierarquico.json", "w", encoding="utf-8") as f:
        json.dump({"components": final_components}, f, indent=4, ensure_ascii=False)

    print("Extração hierárquica concluída com sucesso!")

if __name__ == "__main__":
    test_hierarchical_extraction()