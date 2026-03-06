import os
import json
from transformers import AutoTokenizer

try:
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest
    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False
    print("WARNING: vllm not installed. Multi-LoRA serving will not work.")

from src.data.prompt_templates import format_scoring_prompt
from src.inference.output_parser import parse_model_output

class MultiLoRAEngine:
    """
    Manages vLLM inference with multiple concurrent LoRA adapters.
    This demonstrates the memory/scaling advantage highlighted in the proposal.
    """
    def __init__(self, base_model_id: str, adapters_config: dict, max_loras: int = 8):
        """
        adapters_config format: { prompt_id: {"name": str, "path": str} }
        """
        if not VLLM_AVAILABLE:
            raise ImportError("vllm package required for MultiLoRAEngine")
            
        print(f"Initializing vLLM Multi-LoRA Engine with base model: {base_model_id}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_id)
        self.adapters = adapters_config
        self.lora_requests = {}
        
        # Initialize vLLM with LoRA enabled
        self.llm = LLM(
            model=base_model_id,
            enable_lora=True,
            max_loras=max_loras,
            max_lora_rank=8,
            max_model_len=4096,
            gpu_memory_utilization=0.90,
            # Use AWQ or GPTQ if specified, else FP16/BF16

        )
        
        # Register adapters
        # vLLM assigns a unique integer ID to each LoRA
        lora_base_id = 1
        for prompt_id, config in self.adapters.items():
            if os.path.exists(config["path"]):
                print(f"Registering LoRA '{config['name']}' at ID {lora_base_id}")
                self.lora_requests[prompt_id] = LoRARequest(
                    lora_name=config["name"],
                    lora_int_id=lora_base_id,
                    lora_path=config["path"]
                )
                lora_base_id += 1
            else:
                print(f"WARNING: Adapter path not found: {config['path']}")

    def generate_batch(self, requests):
        """
        Process a batch of essays that may require DIFFERENT LoRA adapters simultaneously.
        requests format: [{"essay_id": str, "text": str, "prompt_id": int}]
        """
        prompts = []
        lora_requests = []
        
        # 1. Prepare formatting and routing
        for req in requests:
            prompt_id = req["prompt_id"]
            
            # Format chat prompt
            messages = json.loads(format_scoring_prompt(req["text"], prompt_id, "llama"))
            input_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            prompts.append(input_text)
            
            # Route to correct LoRA
            if prompt_id in self.lora_requests:
                lora_requests.append(self.lora_requests[prompt_id])
            else:
                print(f"WARNING: No LoRA registered for prompt_id {prompt_id}. Using base model.")
                lora_requests.append(None)
                
        # 2. Vectorized Generation
        sampling_params = SamplingParams(temperature=0.1, max_tokens=256)
        
        # vLLM handles continuous batching and PagedAttention across the different adapters automatically
        outputs = self.llm.generate(
            prompts,
            sampling_params=sampling_params,
            lora_request=lora_requests
        )
        
        # 3. Parse outputs
        results = []
        for req, output in zip(requests, outputs):
            generated_text = output.outputs[0].text
            parsed = parse_model_output(generated_text)
            
            # Combine with original request data
            res = req.copy()
            res.update(parsed)
            results.append(res)
            
        return results
