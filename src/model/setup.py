
import torch

import os

import sys

from transformers import (

    AutoModelForCausalLM, 

    AutoModelForSeq2SeqLM,

    AutoTokenizer, 

    BitsAndBytesConfig

)

from peft import (

    LoraConfig, 

    get_peft_model, 

    prepare_model_for_kbit_training,

    TaskType

)



# HF Login

from huggingface_hub import login

login(token=os.environ.get("HF_TOKEN"))





def setup_model_and_tokenizer(config: dict, model_type: str = "llama"):

    """

    Load base model, apply 4-bit quantization, and attach LoRA adapter.

    Handles both Decoder-only (Llama) and Encoder-Decoder (Flan-T5) architectures.

    """

    model_id = config["model"]["name"]

    

    # 1. Load Tokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    

    if model_type == "llama":

        # Llama 3 needs an explicit pad token assigned

        if tokenizer.pad_token is None:

            tokenizer.pad_token = tokenizer.eos_token

        tokenizer.padding_side = "right"  # standard for training causal LMs

    elif model_type == "t5":

        # T5 doesn't need eos as pad, it has its own

        pass

    

    # 2. Configure 4-bit Quantization (QLoRA)

    bnb_config = BitsAndBytesConfig(

        load_in_4bit=True,

        bnb_4bit_quant_type="nf4",

        bnb_4bit_compute_dtype=torch.bfloat16 if config["training"]["bf16"] else torch.float16,

        bnb_4bit_use_double_quant=True,

    )

    

    # 3. Load Base Model

    print(f"Loading base {model_type} model: {model_id} in 4-bit...")

    if model_type == "llama":

        model = AutoModelForCausalLM.from_pretrained(

            model_id,

            quantization_config=bnb_config,

            device_map="auto",

            attn_implementation=config["model"].get("attn_implementation", "sdpa")

        )

        task_type = TaskType.CAUSAL_LM

        # Standard Llama attention targets

        target_modules = config["lora"]["target_modules"]    

    

    elif model_type == "t5":

        model = AutoModelForSeq2SeqLM.from_pretrained(

            model_id,

            quantization_config=bnb_config,

            device_map="auto"

            # T5 doesn't support flash_attention_2 natively out of the box

        )

        task_type = TaskType.SEQ_2_SEQ_LM

        # T5-specific attention projection names

        target_modules = ["q", "k", "v", "o", "wi_0", "wi_1", "wo"]

    

    # Prepare model for standard QLoRA training

    model = prepare_model_for_kbit_training(model)

    

    # 4. Configure and Apply LoRA

    print(f"Applying LoRA adapter (rank {config['lora']['r']})...")

    peft_config = LoraConfig(

        r=config["lora"]["r"],

        lora_alpha=config["lora"]["lora_alpha"],

        target_modules=target_modules,

        lora_dropout=config["lora"]["lora_dropout"],

        bias=config["lora"]["bias"],

        task_type=task_type

    )

    model = get_peft_model(model, peft_config)

    model.print_trainable_parameters()

    

    return model, tokenizer

