import os
import glob
import base64
import anthropic
import mimetypes

def main():
    client = anthropic.Anthropic(api_key=os.environ.get("LLM_API_KEY"))

    # Localiza o arquivo de imagem na mesma pasta (suporta .png, .jpg, etc)
    base_path = os.path.join(os.path.dirname(__file__), "diagramateste")
    files = glob.glob(f"{base_path}.*")
    
    if not files:
        print("Arquivo 'diagramateste' não encontrado na pasta playground.")
        return
        
    image_path = files[0]
    media_type, _ = mimetypes.guess_type(image_path)
    if not media_type:
        media_type = "image/png"

    # Codifica a imagem em base64 para envio
    with open(image_path, "rb") as file:
        image_data = base64.b64encode(file.read()).decode("utf-8")
               
    EXTRACTION_PROMPT = """
    You are a multimodal AI specialized in extracting structured information from software architecture diagrams.

    Your task is NOT to analyze or interpret the architecture at a high level.
    Your task is ONLY to extract visible and explicit information from the diagram.

    Given an input diagram (image or PDF), you must extract raw structural elements and return them in a strictly valid JSON format.

    ---

    ## Extraction Rules

    1. Do NOT infer architecture patterns (e.g., microservices, monolith).
    2. Do NOT generate recommendations or analysis.
    3. Only extract what is visually or textually present in the diagram.
    4. If something is uncertain, include it with lower confidence rather than omitting it.
    5. Prefer explicit labels over assumptions.

    ---

    ## Output Format (STRICT JSON)

    You must return ONLY a JSON object with the following structure:

    {
      "text_blocks": [string],
      "grouped_elements": [
        {
          "label": string,
          "texts": [string]
        }
      ],
      "detected_keywords": [
        {
          "text": string,
          "hint": string
        }
      ],
      "relationship_hints": [
        {
          "from": string,
          "to": string,
          "label": string
        }
      ],
      "context_groups": [
        {
          "name": string,
          "contains": [string]
        }
      ]
    }

    ---

    ## Field Definitions

    ### text_blocks
    All distinct text elements found in the diagram (titles, labels, annotations).

    ### grouped_elements
    Logical groupings of text that belong to the same visual block or component.

    ### detected_keywords
    Important keywords with lightweight hints about their possible meaning.
    Examples of hints:
    - "ui"
    - "service"
    - "database"
    - "event_stream"
    - "entrypoint"
    - "external_system"

    ### relationship_hints
    Connections between elements based on arrows or flow indicators.
    - "from": source component label
    - "to": destination component label
    - "label": text describing the connection (if available)

    ### context_groups
    Higher-level visual containers or boundaries.
    Examples:
    - "Kubernetes Cluster"
    - "External Systems"
    - "Cloud Environment"

    ---

    ## Additional Guidelines

    - Merge similar texts when they clearly refer to the same element.
    - Preserve original naming as much as possible.
    - If multiple interpretations exist, choose the most visually supported one.
    - Keep the output concise but complete.

    ---

    ## Output Constraints

    - Return ONLY valid JSON.
    - Do NOT include explanations.
    - Do NOT include markdown.
    - Do NOT include comments.

    ---

    Now analyze the provided diagram and return the structured extraction.
    """

    # Cria a requisição para o Claude com suporte à visão
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10240,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        }
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT
                    }
                ]
            }
        ]
    )

    print(response.content[0].text)

if __name__ == "__main__":
    main()