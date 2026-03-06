import argparse
import os
import sys

# Add project root to path so we can run scripts from anywhere
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.loader import load_config, load_essays, create_splits
from src.training.trainer import train_adapter

def main():
    parser = argparse.ArgumentParser(description="Train LoRA adapter for a specific essay set.")
    parser.add_argument("--essay_set", type=int, required=True, 
                        help="Prompt ID (essay set) to train on (e.g. 1-8 for ASAP)")
    parser.add_argument("--model_type", type=str, choices=["llama", "t5"], default="llama",
                        help="Which base architecture to train")
    parser.add_argument("--config", type=str, default="config/default.yaml",
                        help="Path to YAML config file")
    
    args = parser.parse_args()
    
    # 1. Load config
    config = load_config(args.config)
    
    # Check if we should override model name via CLI
    if args.model_type == "t5":
        config["model"]["name"] = "google/flan-t5-xl"
        print("Using Flan-T5-XL standard comparison model")
        
    # 2. Setup output dir
    output_dir = os.path.join(config["paths"]["adapters_dir"], f"set_{args.essay_set}_{args.model_type}")
    print(f"\n--- Training {args.model_type.upper()} Adapter for Essay Set {args.essay_set} ---")
    print(f"Outputting to: {output_dir}")
    
    # 3. Load Data
    data_path = os.path.join(config["data"]["raw_dir"], "train.csv")
    print(f"Loading data from {data_path}...")
    try:
        df = load_essays(data_path, prompt_id=args.essay_set)
    except FileNotFoundError:
        print(f"ERROR: Cannot find dataset at {data_path}. Please run `python scripts/download_data.py` first.")
        sys.exit(1)
        
    print(f"Loaded {len(df)} essays for Set {args.essay_set}.")
    
    if len(df) == 0:
        print(f"ERROR: No essays found for Set {args.essay_set}. Exiting.")
        sys.exit(1)
    
    # 4. Create splits
    dataset_dict = create_splits(
        df, 
        val_size=config["data"]["val_split"], 
        test_size=config["data"]["test_split"]
    )
    
    print(f"Splits created: Train({len(dataset_dict['train'])}), Val({len(dataset_dict['validation'])}), Test({len(dataset_dict['test'])})")
    
    # Save the test split for evaluation later
    test_output_path = os.path.join(output_dir, "test_split.jsonl")
    dataset_dict["test"].to_json(test_output_path)
    print(f"Saved test split to {test_output_path} for later evaluation.")

    # 5. Kick off training
    train_adapter(
        model_type=args.model_type,
        dataset_dict=dataset_dict,
        config=config,
        output_dir=output_dir
    )

if __name__ == "__main__":
    main()
