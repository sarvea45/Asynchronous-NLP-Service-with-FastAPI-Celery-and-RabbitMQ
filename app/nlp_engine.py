import spacy
from transformers import pipeline

# Global variables to hold models in memory
NLP_MODELS = {
    "spacy_ner": None,
    "transformers_sentiment": None
}

def load_all_models():
    """
    Loads models into memory. Must be called once when the worker starts.
    """
    print("Loading models into memory...")
    try:
        # Load spaCy for NER
        NLP_MODELS["spacy_ner"] = spacy.load("en_core_web_sm")
    except OSError:
        print("spacy model not found. Downloading...")
        from spacy.cli import download
        download("en_core_web_sm")
        NLP_MODELS["spacy_ner"] = spacy.load("en_core_web_sm")

    # Load HuggingFace pipeline for sentiment analysis
    NLP_MODELS["transformers_sentiment"] = pipeline("sentiment-analysis")
    print("Models loaded successfully.")

def analyze_sentiment(text: str) -> dict:
    """
    Performs sentiment analysis using HuggingFace transformers.
    """
    model = NLP_MODELS.get("transformers_sentiment")
    if not model:
        raise RuntimeError("Sentiment model is not loaded.")
    
    # pipeline returns a list of dicts, e.g., [{'label': 'POSITIVE', 'score': 0.99}]
    result = model(text)
    return {"sentiment": result}

def extract_entities(text: str) -> dict:
    """
    Performs named entity recognition using spaCy.
    """
    model = NLP_MODELS.get("spacy_ner")
    if not model:
        raise RuntimeError("NER model is not loaded.")
    
    doc = model(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    return {"entities": entities}
