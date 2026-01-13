"""
Chatbot service for loading and using the trained Llama model
"""
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import warnings
warnings.filterwarnings('ignore')

# Path to the trained model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'AI_Chatbot', 'models', 'isuku_chatbot_llama')
BASE_MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Global variables to cache the model and tokenizer
_model = None
_tokenizer = None


def load_model():
    """Load the trained model and tokenizer (cached after first load)"""
    global _model, _tokenizer
    
    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer
    
    try:
        print(f"Loading model from: {MODEL_PATH}")
        
        # Check if model directory exists
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        # Load tokenizer
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _tokenizer.pad_token = _tokenizer.eos_token
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_NAME,
            torch_dtype=torch.float32,  # Use float32 for CPU/MPS compatibility
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )
        
        # Load fine-tuned LoRA weights
        if os.path.exists(os.path.join(MODEL_PATH, 'adapter_config.json')):
            try:
                _model = PeftModel.from_pretrained(base_model, MODEL_PATH)
                _model.eval()
            except Exception as e:
                print(f"Warning: Could not load LoRA adapter: {e}")
                print("Using base model instead.")
                _model = base_model
                _model.eval()
        else:
            # If no LoRA adapter, use base model directly
            _model = base_model
            _model.eval()
        
        # Move to device if not using device_map
        if not torch.cuda.is_available() and not torch.backends.mps.is_available():
            _model = _model.to('cpu')
        
        print("Model loaded successfully!")
        return _model, _tokenizer
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise


def generate_response(question, max_length=256, temperature=0.7):
    """
    Generate a response to a given question
    
    Args:
        question: The user's question
        max_length: Maximum length of generated response
        temperature: Sampling temperature (higher = more creative)
    
    Returns:
        Generated response string
    """
    global _model, _tokenizer
    
    # Load model if not already loaded
    if _model is None or _tokenizer is None:
        try:
            _model, _tokenizer = load_model()
        except Exception as e:
            return f"I'm sorry, but I'm currently unavailable. Error: {str(e)}. Please try again later or contact support."
    
    try:
        # Format the prompt
        prompt = f"### Instruction:\n{question}\n\n### Response:\n"
        
        # Tokenize
        inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
        
        # Move to device
        device = next(_model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=_tokenizer.eos_token_id,
                eos_token_id=_tokenizer.eos_token_id,
            )
        
        # Decode response
        full_response = _tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response part
        if "### Response:" in full_response:
            response = full_response.split("### Response:")[-1].strip()
        else:
            response = full_response[len(prompt):].strip()
        
        # Clean up response (remove any remaining prompt artifacts)
        response = response.split("### Instruction:")[0].strip()
        response = response.split("### Response:")[0].strip()
        
        return response if response else "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."


def is_model_loaded():
    """Check if model is loaded"""
    return _model is not None and _tokenizer is not None

