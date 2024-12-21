from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize the FastAPI app
app = FastAPI()

# 2. Add CORS middleware to the FastAPI app
origins = [
    "http://192.168.0.102:5500",  # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# 3. Load the model and tokenizer at startup so we only do it once.
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# 4. Create a Pydantic model for request data
class TitleRequest(BaseModel):
    title: str

def get_virality_score_transformers(youtube_title: str) -> float:
    """
    Computes a 'virality score' for a YouTube title using a Transformer-based sentiment analysis.
    Returns a value between 0 and 100.
    """
    analysis = sentiment_analyzer(youtube_title)
    if not analysis:
        return 0.0

    label = analysis[0]['label']   # e.g., 'Positive', 'Neutral', or 'Negative'
    confidence = analysis[0]['score']

    # Assign base values: Positive -> 2, Neutral -> 1, Negative -> -2
    if label.lower() == "positive":
        base_score = 2.0
    elif label.lower() == "neutral":
        base_score = 1.0
    else:  # "negative"
        base_score = -2.0  # Negative gets higher penalty to emphasize virality of strong negativity

    # Adjust raw score to amplify strong sentiments
    raw_score = base_score * confidence * 3.0  # Increased amplification

    # Normalize raw_score [-6, 6] into [0, 1]
    normalized_score = (raw_score + 6.0) / 12.0
    normalized_score = max(0.0, min(1.0, normalized_score))

    return normalized_score * 100


# 6. Define an endpoint to compute the virality score
@app.post("/virality-score")
def compute_virality_score(req: TitleRequest):
    """
    Expects JSON: {"title": "some youtube title"}
    Returns: {"virality_score": 0.XX}
    """
    score = get_virality_score_transformers(req.title)
    return {"virality_score": round(score, 3)}
