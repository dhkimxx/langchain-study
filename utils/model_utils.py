def normalize_embedding_model_name(name: str | None) -> str:
    """왜: Google Embeddings API는 모델명을 'models/<id>' 형식으로 기대한다.
    사용자가 'text-embedding-004'로 설정해도 자동 보정해 안전하게 호출한다.
    """
    default = "models/text-embedding-004"
    if not name:
        return default
    return name if name.startswith("models/") else f"models/{name}"
