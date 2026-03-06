import argparse
import os
import sys
import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.loader import load_config
from src.inference.scorer import AESScorer
from src.evaluation.qwk import evaluate_predictions

def main():
    parser = argparse.ArgumentParser(description="Evaluate a trained LoRA adapter on test split.")
    parser.add_argument("--adapter_dir", type=str, required=True, 
                        help="Path to trained LoRA adapter")
    parser.add_argument("--model_type", type=str, choices=["llama", "t5"], default="llama")
    parser.add_argument("--essay_set", type=int, required=True)
    parser.add_argument("--config", type=str, default="config/default.yaml")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    if args.model_type == "t5":
        config["model"]["name"] = "google/flan-t5-xl"
        
    print(f"\n--- Evaluating {args.model_type.upper()} Adapter (Set {args.essay_set}) ---")
    
    # 1. Load test data (JSONL created during training setup)
    test_data_path = os.path.join(args.adapter_dir, "test_split.jsonl")
    if not os.path.exists(test_data_path):
        print(f"ERROR: Test split not found at {test_data_path}")
        sys.exit(1)
        
    df = pd.read_json(test_data_path, lines=True)
    print(f"Loaded {len(df)} test essays.")
    
    # Optionally limit for fast dev testing
    if config["evaluation"]["num_samples"] > 0:
        df = df.head(config["evaluation"]["num_samples"])
        print(f"Limiting to first {len(df)} samples per config.")
    
    # 2. Init Scorer
    scorer = AESScorer(
        base_model_id=config["model"]["name"],
        adapter_path=args.adapter_dir,
        model_type=args.model_type
    )
    
    # 3. Predict looping
    results = []
    print("Scoring essays...")
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        essay_text = row["full_text"]
        true_score = row["score"]
        
        parsed_out = scorer.score_essay(essay_text, args.essay_set)
        
        results.append({
            "essay_id": row.get("essay_id", f"idx_{idx}"),
            "true_score": true_score,
            "pred_score": parsed_out["score"],
            "justification": parsed_out["justification"],
            "raw_output": parsed_out.get("raw_output", "")
        })
        
    results_df = pd.DataFrame(results)
    
    # 4. Calculate QWK
    metrics = evaluate_predictions(results_df)
    
    print("\n--- Evaluation Results ---")
    print(f"Total Evaluated: {metrics['total_evaluated']}")
    print(f"Failed JSON Parses: {metrics['failed_parses']}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Quadratic Weighted Kappa (QWK): {metrics['qwk']:.4f}")
    
    # 5. Save results
    os.makedirs(config["paths"]["results_dir"], exist_ok=True)
    out_csv = os.path.join(config["paths"]["results_dir"], f"results_set{args.essay_set}_{args.model_type}.csv")
    results_df.to_csv(out_csv, index=False)
    print(f"Saved detailed predictions to {out_csv}")

if __name__ == "__main__":
    main()
