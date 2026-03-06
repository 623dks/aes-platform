import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

BASE_MODEL_ID = "unsloth/meta-llama-3.1-8b-bnb-4bit"
ADAPTERS_ROOT  = "/home/g623dks/outputs/adapters"

ADAPTER_MAP = {
    "exam_1": "exam_1",
    "exam_2": "exam_2",
    "exam_3": "exam_3",
    "exam_4": "exam_4",
    "exam_5": "exam_5",
    "exam_6": "exam_6",
    "exam_7": "exam_7",
}

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

print(f"Loading base model: {BASE_MODEL_ID}")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, trust_remote_code=True)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Base model loaded.")

def load_adapter(exam_key):
    adapter_dir = os.path.join(ADAPTERS_ROOT, ADAPTER_MAP[exam_key])
    cfg_path = os.path.join(adapter_dir, "adapter_config.json")
    old_cfg  = os.path.join(adapter_dir, "config.json")
    if not os.path.exists(cfg_path) and os.path.exists(old_cfg):
        os.rename(old_cfg, cfg_path)
        print(f"  Renamed config.json -> adapter_config.json in {adapter_dir}")
    print(f"Loading adapter for {exam_key} from {adapter_dir}")
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()
    return model

def score_essay(essay_text, exam_key):
    if exam_key not in ADAPTER_MAP:
        raise ValueError(f"Unknown exam_key: {exam_key}")
    model = load_adapter(exam_key)
    prompt = f"Score the following essay on a scale of 0-10 and briefly justify your score.\n\nEssay:\n{essay_text}\n\nScore:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
            temperature=1.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = output_ids[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--exam",  required=True)
    parser.add_argument("--essay", required=True)
    args = parser.parse_args()
    if os.path.isfile(args.essay):
        with open(args.essay, "r", encoding="utf-8") as f:
            essay_text = f.read()
    else:
        essay_text = args.essay
    score = score_essay(essay_text, args.exam)
    print(f"\n=== Score for {args.exam} ===\n{score}\n")
