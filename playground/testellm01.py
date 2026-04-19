import os
import anthropic

def main():
    # Inicializa o cliente do Anthropic. 
    # A chave de API será lida automaticamente da variável de ambiente ANTHROPIC_API_KEY
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # Cria a requisição para o Claude
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", # Utilizando o modelo Haiku (mais rápido e barato)
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Quais são as fases do período romano?"}
        ]
    )

    print(response.content[0].text)

if __name__ == "__main__":
    main()