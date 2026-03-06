import torch, gc
import pandas as pd
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset

df = pd.read_csv('/home/g623dks/data/raw/train_labeled.csv')

def train_adapter(set_id):
    print(f"\n🚀 STARTING TRAINING: EXAM ADAPTER {set_id}")
    subset = df[df['essay_set'] == set_id]
    
    # LOAD FRESH MODEL FOR EVERY EXAM SO PEFT DOES NOT CRASH
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "unsloth/Meta-Llama-3.1-8B-bnb-4bit",
        max_seq_length = 1024,
        load_in_4bit = True,
    )
    
    peft_model = FastLanguageModel.get_peft_model(
        model, 
        r = 16, 
        lora_alpha = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = "unsloth",
    )

    dataset = Dataset.from_pandas(subset)
    def format_prompt(x):
        return {"text": f"### Instruction: Score this essay for Exam {set_id}.\n### Essay: {x['full_text']}\n### Score: {x['score']} <|end_of_text|>"}
    dataset = dataset.map(format_prompt)

    trainer = SFTTrainer(
        model = peft_model,
        processing_class = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = 1024,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            num_train_epochs = 2,
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 10,
            output_dir = f"outputs/temp_set_{set_id}",
            report_to = "none"
        ),
    )
    
    trainer.train()

    peft_model.save_pretrained(f"/home/g623dks/outputs/adapters/exam_{set_id}")
    
    # Nuke everything from memory before the next loop
    del trainer
    del peft_model
    del model
    gc.collect()
    torch.cuda.empty_cache()
    print(f"✅ Adapter for Exam {set_id} saved.")

for i in range(1, 8):
    train_adapter(i)
