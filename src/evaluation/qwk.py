import numpy as np
from sklearn.metrics import confusion_matrix
import pandas as pd

def quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=6):
    """
    Calculates the Quadratic Weighted Kappa (QWK) metric for essay scoring.
    Formula implemented directly from the AES proposal Equation 2.
    """
    # Ensure inputs are ints
    y_true = np.array(y_true, dtype=int)
    y_pred = np.array(y_pred, dtype=int)

    # 1. Create the confusion matrix O (observed)
    num_ratings = max_rating - min_rating + 1
    O = confusion_matrix(y_true, y_pred, labels=np.arange(min_rating, max_rating + 1))

    # 2. Create the weight matrix W (quadratic penalty)
    W = np.zeros((num_ratings, num_ratings))
    for i in range(num_ratings):
        for j in range(num_ratings):
            W[i, j] = ((i - j) ** 2) / ((num_ratings - 1) ** 2)

    # 3. Create the expected matrix E
    # E is the outer product of the class marginals, normalized by total sum
    hist_true = np.bincount(y_true - min_rating, minlength=num_ratings)
    hist_pred = np.bincount(y_pred - min_rating, minlength=num_ratings)
    
    E = np.outer(hist_true, hist_pred)
    # Normalize E to have the same sum as O (total number of samples)
    if np.sum(E) == 0:
        return 0.0 # avoid division by zero
    E = E / np.sum(E) * np.sum(O)

    # 4. Calculate Kappa
    numerator = np.sum(W * O)
    denominator = np.sum(W * E)

    if denominator == 0:
        return 0.0
        
    kappa = 1.0 - (numerator / denominator)
    return kappa

def evaluate_predictions(results_df: pd.DataFrame):
    """
    Takes a dataframe with 'true_score' and 'pred_score' and returns metrics.
    """
    # Filter out failed parses (-1)
    valid_df = results_df[results_df['pred_score'] != -1]
    failed_count = len(results_df) - len(valid_df)
    
    if len(valid_df) == 0:
        return {"qwk": 0.0, "accuracy": 0.0, "failed_parses": failed_count}
        
    y_true = valid_df['true_score'].values
    y_pred = valid_df['pred_score'].values
    
    qwk = quadratic_weighted_kappa(y_true, y_pred, min_rating=1, max_rating=6)
    acc = np.mean(y_true == y_pred)
    
    return {
        "qwk": float(qwk),
        "accuracy": float(acc),
        "failed_parses": failed_count,
        "total_evaluated": len(valid_df)
    }
