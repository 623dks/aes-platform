import torch, gc
import pandas as pd
from unsloth import FastLanguageModel
from tqdm import tqdm

# 1. Load the test data
test_df = pd.read_csv('/home/g623dks/data/raw/test.csv') 

# Dictionary to hold the 7 different scores for each essay
# Format: { 'essay_id_1': [score1, score2...], 'essay_id_2': [...] }
essay_scores = {row['essay_id']: [] for _, row in test_df.iterrows()}

# 2. Loop through all 7 adapters
for set_id in range(1, 8):
    print(f"\n🚀 LOADING ADAPTER FOR EXAM {set_id}...")
    
    adapter_path = f"/home/g623dks/outputs/adapters/exam_{set_id}"
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = adapter_path,
        max_seq_length = 1024,
        load_in_4bit = True,
    )
    
    FastLanguageModel.for_inference(model)
    
    print(f"Having Expert {set_id} grade all {len(test_df)} test essays...")
    
    # 3. Have the current adapter score EVERY essay
    for index, row in tqdm(test_df.iterrows(), total=len(test_df)):
        essay_text = row['full_text']
        essay_id = row['essay_id']
        
        # We prompt it using the format it learned in training
        prompt = f"### Instruction: Score this essay for Exam {set_id}.\n### Essay: {essay_text}\n### Score: "
        
        inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
        
        # FIX: Removed temperature=0.0
        outputs = model.generate(**inputs, max_new_tokens=5, use_cache=True)
        
        full_response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        generated_score = full_response.split("### Score: ")[-1].strip()
        
        # Clean up the AI's output to make sure it's just a number
        try:
            # Filters out any accidental punctuation like "4." or " 4"
            score_val = float(''.join(filter(str.isdigit, generated_score)) or 0)
        except:
            score_val = 3.0 # Fallback in case of a weird AI hallucination
            
        # Add this expert's score to the essay's record
        essay_scores[essay_id].append(score_val)
        
    # 4. Clean up the GPU before loading the next expert
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()

# 5. Calculate the final average scores!
print("\n📊 Calculating final Ensemble scores...")
final_predictions = []

for essay_id, scores in essay_scores.items():
    # Calculate the average of the 7 experts
    avg_score = sum(scores) / len(scores)
    # Round to the nearest whole number (since grades are integers)
    final_score = int(round(avg_score))
    
    final_predictions.append({
        'essay_id': essay_id,
        'score': final_score
    })

# 6. Save exactly how Kaggle wants it
results_df = pd.DataFrame(final_predictions)
results_df.to_csv('/home/g623dks/submission.csv', index=False)
print("\n✅ All scoring complete! Your Kaggle-ready file is saved at /home/g623dks/submission.csv")
