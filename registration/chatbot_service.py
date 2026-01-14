"""
Chatbot service for loading and using the trained Llama model
"""
import os
import logging
import warnings
warnings.filterwarnings('ignore')

# Try to import ML libraries - make them optional to prevent crashes
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. Chatbot will use fallback responses.")

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Chatbot will use fallback responses.")

try:
    from peft import PeftModel
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False
    logging.warning("PEFT not available. Chatbot will use fallback responses.")

logger = logging.getLogger(__name__)

# Path to the trained model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'AI_Chatbot', 'models', 'isuku_chatbot_llama')
BASE_MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Global variables to cache the model and tokenizer
_model = None
_tokenizer = None


def load_model():
    """Load the trained model and tokenizer (cached after first load)"""
    global _model, _tokenizer
    
    # Check if required libraries are available
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
        logger.warning("Required ML libraries not available. Chatbot will use fallback responses.")
        _model = None
        _tokenizer = None
        return None, None
    
    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer
    
    try:
        logger.info(f"Loading model from: {MODEL_PATH}")
        
        # Check if model directory exists
        if not os.path.exists(MODEL_PATH):
            logger.warning(f"Model not found at {MODEL_PATH}. Chatbot will return default responses.")
            _model = None
            _tokenizer = None
            return None, None
        
        # Check if adapter config exists
        adapter_config_path = os.path.join(MODEL_PATH, 'adapter_config.json')
        if not os.path.exists(adapter_config_path):
            logger.warning(f"Adapter config not found at {adapter_config_path}. Model may not be properly trained.")
            _model = None
            _tokenizer = None
            return None, None
        
        # Load tokenizer
        try:
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            _tokenizer.pad_token = _tokenizer.eos_token
        except Exception as e:
            logger.error(f"Error loading tokenizer: {e}")
            _model = None
            _tokenizer = None
            return None, None
        
        # Load base model
        try:
            base_model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL_NAME,
                torch_dtype=torch.float32,  # Use float32 for CPU/MPS compatibility
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
        except Exception as e:
            logger.error(f"Error loading base model: {e}")
            _model = None
            _tokenizer = None
            return None, None
        
        # Load fine-tuned LoRA weights
        if PEFT_AVAILABLE and os.path.exists(adapter_config_path):
            try:
                _model = PeftModel.from_pretrained(base_model, MODEL_PATH)
                _model.eval()
            except Exception as e:
                logger.warning(f"Could not load LoRA adapter: {e}. Using base model instead.")
                _model = base_model
                _model.eval()
        else:
            # If no LoRA adapter, use base model directly
            _model = base_model
            _model.eval()
        
        # Move to device if not using device_map
        if not torch.cuda.is_available():
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                try:
                    _model = _model.to('mps')
                except:
                    _model = _model.to('cpu')
            else:
                _model = _model.to('cpu')
        
        logger.info("Model loaded successfully!")
        return _model, _tokenizer
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}", exc_info=True)
        # Return None instead of raising to allow graceful degradation
        _model = None
        _tokenizer = None
        return None, None


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
    
    # Check if ML libraries are available
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
        return "I'm sorry, the AI chatbot is currently unavailable due to missing dependencies. Please contact our support team for assistance with your waste management needs."
    
    # Load model if not already loaded
    if _model is None or _tokenizer is None:
        try:
            _model, _tokenizer = load_model()
            # Check if model loaded successfully
            if _model is None or _tokenizer is None:
                logger.warning("Chatbot model not available - returning fallback response")
                return "I'm sorry, the AI chatbot model is not currently available. The model files may not be deployed yet. Please contact our support team for assistance with your waste management needs."
        except Exception as e:
            logger.error(f"Error loading chatbot model: {str(e)}", exc_info=True)
            return "I'm sorry, but I encountered an error while loading. Please try again later or contact support."
    
    # Double-check model is available
    if _model is None or _tokenizer is None:
        return "I'm sorry, the AI chatbot model is not currently available. Please contact our support team for assistance with your waste management needs."
    
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

