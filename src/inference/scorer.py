import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
from src.data.prompt_templates import format_scoring_prompt
from src.inference.output_parser import parse_model_output

class AESScorer:
    """Scorer utilizing the base model + LoRA adapter for a specific exam type."""
    
    def __init__(self, base_model_id: str, adapter_path: str, model_type: str = "llama"):
        self.model_type = model_type
        print(f"Loading {model_type} tokenizer and base model: {base_model_id}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_id)
        
        if model_type == "llama":
            model_class = AutoModelForCausalLM
        elif model_type == "t5":
            model_class = AutoModelForSeq2SeqLM
        else:
            raise ValueError(f"Unknown model architecture: {model_type}")
            
        # Load base model in 4-bit for memory efficiency during inference too
        base_model = model_class.from_pretrained(
            base_model_id,
            load_in_4bit=True,
            device_map="auto"
        )
        
        print(f"Loading LoRA adapter from {adapter_path}...")
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
        self.model.eval()
        
    def score_essay(self, essay_text: str, prompt_id: int) -> dict:
        """Run single essay through model and return parsed dict."""
        
        if self.model_type == "llama":
            # Chat format
            messages = json.loads(format_scoring_prompt(essay_text, prompt_id, "llama"))
            input_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.1,  # Low temp for deterministic scoring
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
            # Decode just the newly generated tokens
            input_length = inputs.input_ids.shape[1]
            generated_text = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
            
            return parse_model_output(generated_text)
            
        elif self.model_type == "t5":
            # Standard Text2Text formatting
            input_text = format_scoring_prompt(essay_text, prompt_id, "t5")
            inputs = self.tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True).to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=128
                )
                
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # T5 is outputting flat text (Score: X. Justification: Y), parse simply
            import re
            score_match = re.search(r'Score:\s*(\d)', generated_text)
            score = int(score_match.group(1)) if score_match else -1
            
            return {
                "score": score,
                "justification": generated_text,
                "raw_output": generated_text
            }

import json # needed for the llama chat formatting parsing above
