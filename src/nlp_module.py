import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

# Set of known suspicious phrases
SUSPICIOUS_PHRASES = [
    "lost item", "damage occurred", "injured in", "fell and hurt", 
    "car accident", "water leak", "stolen electronics",
    "sudden", "unexplained", "lost completely", "no witnesses"
]

class TextRiskAnalyzer:
    def __init__(self, model_dir='models'):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
        self.model_dir = model_dir
        self.trained = False
        
    def fit(self, texts, labels=None):
        """Fit TF-IDF on training text corpus."""
        self.vectorizer.fit(texts)
        os.makedirs(self.model_dir, exist_ok=True)
        joblib.dump(self.vectorizer, os.path.join(self.model_dir, 'tfidf_vectorizer.pkl'))
        self.trained = True
        return self
        
    def load(self):
        """Load pretrained vectorizer."""
        self.vectorizer = joblib.load(os.path.join(self.model_dir, 'tfidf_vectorizer.pkl'))
        self.trained = True
        return self
        
    def extract_keywords(self, text, top_n=3):
        """Extract top keywords from a single text."""
        if not self.trained:
            self.load()
            
        tfidf_matrix = self.vectorizer.transform([text])
        feature_array = np.array(self.vectorizer.get_feature_names_out())
        tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
        
        return list(feature_array[tfidf_sorting][:top_n])
        
    def calculate_text_risk_score(self, text):
        """
        Calculate a heuristic text-based risk score.
        1. Checks for vague/suspicious phrases.
        2. Rewards detailed descriptions (longer text).
        """
        text_lower = str(text).lower()
        
        # Base score
        score = 0.0
        
        # Penalty for suspicious phrases
        matches = [phrase for phrase in SUSPICIOUS_PHRASES if phrase in text_lower]
        if len(matches) > 0:
            score += 0.5 * min(len(matches), 3) # Max 1.5 penalty
            
        # Penalty for extremely vague descriptions
        word_count = len(text_lower.split())
        if word_count < 5:
            score += 0.6
        elif word_count < 10:
            score += 0.3
        else:
            # Reward for detail
            score -= 0.2
            
        # Normalize between 0 and 1
        return max(0.0, min(1.0, score + 0.1))

def process_nlp_features(df, is_training=True):
    """Add NLP-derived features to dataframe."""
    df = df.copy()
    analyzer = TextRiskAnalyzer()
    
    if is_training:
        analyzer.fit(df['claim_description'])
        
    # Vectorized computation of risk scores and keywords
    df['nlp_risk_score'] = df['claim_description'].apply(analyzer.calculate_text_risk_score)
    df['nlp_keywords'] = df['claim_description'].apply(lambda x: ', '.join(analyzer.extract_keywords(x)))
    
    # Check for suspicious phrases flag
    df['has_suspicious_phrases'] = df['claim_description'].apply(
        lambda x: 1 if any(p in str(x).lower() for p in SUSPICIOUS_PHRASES) else 0
    )
    
    return df, ['nlp_risk_score', 'has_suspicious_phrases']

if __name__ == '__main__':
    # Test block
    print("Testing NLP Module...")
    df = pd.DataFrame({'claim_description': ["Damage occurred to property. Lost item.", 
                                             "Rear-ended on Main St by a blue sedan. Bumper cracked.",
                                             "Fell and hurt myself.",
                                             "Laptop stolen from locked car in mall parking lot. Forced entry visible."]})
    df_out, cols = process_nlp_features(df, is_training=True)
    print(df_out[['claim_description', 'nlp_risk_score', 'nlp_keywords', 'has_suspicious_phrases']])