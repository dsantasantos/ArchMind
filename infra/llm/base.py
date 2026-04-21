class LLMClient:
    def generate(self, prompt: str, image_base64: str = None, media_type: str = "image/jpeg") -> str:
        raise NotImplementedError
