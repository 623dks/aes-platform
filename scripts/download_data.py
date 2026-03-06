import os
import argparse
import subprocess
from pathlib import Path

def download_kaggle_dataset(dataset_name: str, output_dir: str):
    """Download and unzip a Kaggle dataset using the Kaggle API."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Downloading {dataset_name} to {output_dir}...")
    try:
        # Check if kaggle CLI is installed and configured
        subprocess.run(["kaggle", "--version"], check=True, capture_output=True)
        
        # Download
        cmd = ["kaggle", "competitions", "download", "-c", dataset_name, "-p", output_dir]
        subprocess.run(cmd, check=True)
        
        # Unzip
        zip_file = list(Path(output_dir).glob("*.zip"))
        if zip_file:
            print(f"Unzipping {zip_file[0]}...")
            subprocess.run(["unzip", "-o", str(zip_file[0]), "-d", output_dir], check=True)
            os.remove(zip_file[0])
            print("Download and extraction complete.")
        else:
            print("No zip file found after download.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error executing Kaggle command: {e}")
        print("Make sure you have installed kaggle (pip install kaggle) and set up ~/.kaggle/kaggle.json")
    except FileNotFoundError:
        print("Kaggle CLI not found. Please install: pip install kaggle")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download AES Datasets")
    parser.add_argument("--dataset", type=str, default="learning-agency-lab-automated-essay-scoring-2", 
                        help="Kaggle competition or dataset name")
    parser.add_argument("--output", type=str, default="data/raw", 
                        help="Output directory")
    
    args = parser.parse_args()
    download_kaggle_dataset(args.dataset, args.output)
