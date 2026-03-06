import os
from trl import SFTTrainer
from transformers import TrainingArguments, DataCollatorForLanguageModeling, DataCollatorForSeq2Seq
from src.model.setup import setup_model_and_tokenizer
from src.data.prompt_templates import format_training_example

def train_adapter(model_type: str, dataset_dict, config: dict, output_dir: str):
    """
    Train a LoRA adapter using SFTTrainer on a specific format.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup model
    model, tokenizer = setup_model_and_tokenizer(config, model_type)
    
    # Training args
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=config["training"]["num_epochs"],
        per_device_train_batch_size=config["training"]["per_device_batch_size"],
        gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
        learning_rate=float(config["training"]["learning_rate"]),
        weight_decay=config["training"]["weight_decay"],
        warmup_ratio=config["training"]["warmup_ratio"],
        lr_scheduler_type=config["training"]["lr_scheduler_type"],
        fp16=config["training"]["fp16"],
        bf16=config["training"]["bf16"],
        logging_steps=config["training"]["logging_steps"],
        save_strategy=config["training"]["save_strategy"],
        evaluation_strategy="epoch", # Validate at end of each epoch
        seed=config["training"]["seed"],
        report_to="none"  # Disable wandb/tensorboard for local dev
    )
    
    print(f"Starting {model_type} training for {len(dataset_dict['train'])} examples...")
    
    if model_type == "llama":
        # Decoder-only SFT Training
        
        # Apply formatting map (creates 'messages' column)
        def process(row): return format_training_example(row, "llama")
        
        train_dataset = dataset_dict["train"].map(process)
        eval_dataset = dataset_dict["validation"].map(process)
        
        # We use a custom formatting function to apply the chat template
        def formatting_func(example):
            return tokenizer.apply_chat_template(example["messages"], tokenize=False)
            
        trainer = SFTTrainer(
            model=model,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            formatting_func=formatting_func,
            max_seq_length=config["model"]["max_seq_length"],
            tokenizer=tokenizer,
            args=training_args,
            packing=False, # Don't pack separate essays into single sequence
        )
        
    elif model_type == "t5":
        # Encoder-Decoder standard training
        
        def process_t5(batch):
            inputs = [format_training_example(row, "t5")["input_text"] for row in batch]
            targets = [format_training_example(row, "t5")["target_text"] for row in batch]
            
            model_inputs = tokenizer(inputs, max_length=config["model"]["max_seq_length"], truncation=True)
            labels = tokenizer(targets, max_length=128, truncation=True)
            model_inputs["labels"] = labels["input_ids"]
            return model_inputs
            
        train_dataset = dataset_dict["train"].map(process_t5, batched=True, remove_columns=dataset_dict["train"].column_names)
        eval_dataset = dataset_dict["validation"].map(process_t5, batched=True, remove_columns=dataset_dict["validation"].column_names)
        
        data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
        
        # We can use standard Trainer for sequence-to-sequence
        from transformers import Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator
        )
        
    trainer.train()
    
    print(f"Training complete. Saving adapter to {output_dir}")
    # Only save the LoRA adapter weights, NOT the base model
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
