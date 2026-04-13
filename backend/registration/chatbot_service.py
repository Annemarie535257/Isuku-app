"""
Chatbot service for loading and using the trained Llama model
"""
import os
import logging
from pathlib import Path
import unicodedata
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

# Path to the trained model (repo_root/AI_Chatbot/models/isuku_chatbot_llama)
REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = str(REPO_ROOT / 'AI_Chatbot' / 'models' / 'isuku_chatbot_llama')
BASE_MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Global variables to cache the model and tokenizer
_model = None
_tokenizer = None


def normalize_text(text):
    """Lowercase text and remove accents for keyword matching."""
    normalized = unicodedata.normalize('NFKD', text or '')
    return ''.join(char for char in normalized if not unicodedata.combining(char)).lower().strip()


def normalize_language(language, question=''):
    """Resolve the chatbot language to en, rw, or fr."""
    value = normalize_text(language)
    if value in {'en', 'english'}:
        return 'en'
    if value in {'rw', 'kinyarwanda', 'kinya', 'rwanda'}:
        return 'rw'
    if value in {'fr', 'french', 'francais', 'français'}:
        return 'fr'

    question_text = normalize_text(question)
    french_markers = {
        'bonjour', 'salut', 'collecte', 'dechets', 'dechet', 'demander', 'tri',
        'plastique', 'papier', 'verre', 'metal', 'compte', 'mot de passe', 'proche'
    }
    kinyarwanda_markers = {
        'muraho', 'imyanda', 'gusaba', 'gukusanya', 'gutondeka', 'plastike',
        'impapuro', 'ikirahure', 'icyuma', 'konti', 'ijambobanga', 'hafi'
    }

    if any(marker in question_text for marker in french_markers):
        return 'fr'
    if any(marker in question_text for marker in kinyarwanda_markers):
        return 'rw'
    return 'en'


def detect_intent(question):
    """Detect the main chatbot topic so localized answers stay useful."""
    question_text = normalize_text(question)

    intent_keywords = {
        'pickup_request': {
            'pickup', 'collect', 'collection', 'request', 'demander', 'collecte',
            'saba', 'gusaba', 'gukusanya', 'request pickup'
        },
        'sorting': {
            'sort', 'sorting', 'tri', 'tondeka', 'separate', 'classification',
            'gutondeka', 'waste type'
        },
        'plastic': {'plastic', 'plastique', 'plastike', 'bottle', 'wrapper'},
        'organic': {'organic', 'organique', 'ibinyabuzima', 'food', 'compost'},
        'paper': {'paper', 'papier', 'impapuro', 'cardboard'},
        'glass': {'glass', 'verre', 'ikirahure', 'jar'},
        'metal': {'metal', 'metallic', 'metaux', 'icyuma', 'can', 'aluminium', 'aluminum'},
        'collectors': {'collector', 'collecteurs', 'abakusanya', 'nearby', 'proche', 'hafi', 'map', 'carte'},
        'login': {'login', 'account', 'password', 'connexion', 'compte', 'ijambobanga', 'kwinjira'},
    }

    for intent, keywords in intent_keywords.items():
        if any(keyword in question_text for keyword in keywords):
            return intent

    return 'general'


LOCALIZED_RESPONSES = {
    'en': {
        'pickup_request': "To request a pickup, open your Household Dashboard, click Request Pickup, choose the waste category and quantity, then submit the form.",
        'sorting': "Sort waste into Organic, Plastic, Paper, Glass, Metal, and General Waste. Keep recyclables clean and dry.",
        'plastic': "Rinse plastic items when possible and place them in the plastic recycling stream.",
        'organic': "Organic waste can go in compost or the organic bin.",
        'paper': "Keep paper and cardboard dry before placing them in paper recycling.",
        'glass': "Handle glass carefully and place it in the glass recycling stream.",
        'metal': "Empty metal cans and place them in metal recycling where available.",
        'collectors': "Use the service area map and update your location to see nearby collectors and pickups.",
        'login': "You can log in with your registered account. If needed, use the password reset link from the login page.",
        'general': "I can help with pickup requests, sorting advice, nearby collectors, and account help. Ask me in English, Kinyarwanda, or French.",
    },
    'fr': {
        'pickup_request': "Pour demander une collecte, ouvrez votre tableau de bord ménage, cliquez sur Demander une collecte, choisissez la catégorie et la quantité, puis envoyez le formulaire.",
        'sorting': "Triez les déchets en organiques, plastique, papier, verre, métal et déchets généraux. Gardez les matières recyclables propres et sèches.",
        'plastic': "Rincez les objets en plastique quand c'est possible et placez-les dans la filière de recyclage du plastique.",
        'organic': "Les déchets organiques peuvent aller au compost ou dans la poubelle organique.",
        'paper': "Gardez le papier et le carton au sec avant de les déposer dans le recyclage du papier.",
        'glass': "Manipulez le verre avec précaution et placez-le dans la filière de recyclage du verre.",
        'metal': "Videz les boîtes métalliques et placez-les dans le recyclage du métal quand il est disponible.",
        'collectors': "Utilisez la carte de la zone de service et mettez à jour votre position pour voir les collecteurs et collectes proches.",
        'login': "Vous pouvez vous connecter avec votre compte enregistré. Si nécessaire, utilisez le lien de réinitialisation du mot de passe.",
        'general': "Je peux vous aider avec les demandes de collecte, les conseils de tri, les collecteurs proches et l'aide au compte. Vous pouvez me parler en anglais, en kinyarwanda ou en français.",
    },
    'rw': {
        'pickup_request': "Kugira ngo usabe gukusanya imyanda, fungura Dashboard y'Urugo, kanda Saba Gukusanya, uhitemo icyiciro n'ubunini, hanyuma wohereze ifishi.",
        'sorting': "Tondeka imyanda mu byiciro bya Organic, Plastic, Paper, Glass, Metal, n'Imyanda Rusange. Recyclables zigomba kuba zisukuye kandi zumye.",
        'plastic': "Niba bishoboka, koza ibintu bya plastike hanyuma ubishyire mu cyiciro cyo gusubiramo plastike.",
        'organic': "Imyanda y'ibinyabuzima ishobora kujya mu ifumbire cyangwa mu gatebo k'ibinyabuzima.",
        'paper': "Impapuro na karito bigomba kuguma byumye mbere yo kujya mu gusubiramo impapuro.",
        'glass': "Fata ibirahure witonze hanyuma ubishyire mu gusubiramo ibirahure.",
        'metal': "Sukuramo ibintu byo mu byuma maze ubishyire mu gusubiramo ibyuma aho biboneka.",
        'collectors': "Koresha ikarita y'akarere ka serivisi kandi uvugurure aho uherereye kugira ngo ubone abakusanya n'ibisabwa biri hafi yawe.",
        'login': "Urashobora kwinjira ukoresheje konti yawe wiyandikishije. Niba bikenewe, koresha umurongo wo gusubizaho ijambobanga ku rupapuro rwo kwinjira.",
        'general': "Nshobora kugufasha ku gusaba gukusanya imyanda, inama zo gutondeka, abakusanya bari hafi, n'ubufasha bwa konti. Urashobora kumbaza mu Cyongereza, Ikinyarwanda, cyangwa Igifaransa.",
    },
}


def generate_localized_response(question, language):
    """Generate a deterministic localized response for supported languages."""
    resolved_language = normalize_language(language, question)
    intent = detect_intent(question)
    language_responses = LOCALIZED_RESPONSES.get(resolved_language, LOCALIZED_RESPONSES['en'])
    return language_responses.get(intent, language_responses['general'])


def generate_fallback_response(question):
    """Return a useful deterministic response when the ML model is unavailable."""
    q = (question or '').lower()

    fallback_knowledge = [
        (
            ['pickup', 'collect', 'request', 'trash collection'],
            "To request pickup, log in as Household, open Dashboard, click 'Request Pickup', choose waste category, quantity, and submit."
        ),
        (
            ['sort', 'classification', 'separate', 'waste type'],
            "Sort waste into Organic, Plastic, Paper, Glass, Metal, and General Waste. Keep recyclables clean and dry before disposal."
        ),
        (
            ['plastic', 'bottle', 'wrapper'],
            "Plastic waste should be rinsed and placed in the plastic recycling stream where available."
        ),
        (
            ['organic', 'food', 'banana', 'compost'],
            "Organic waste can be composted or placed in the organic bin for proper treatment."
        ),
        (
            ['paper', 'cardboard'],
            "Paper and cardboard should be kept dry and placed in paper recycling."
        ),
        (
            ['glass', 'jar'],
            "Glass should be handled safely and placed in designated glass recycling."
        ),
        (
            ['metal', 'can', 'aluminium', 'aluminum'],
            "Metal cans should be emptied and placed in metal recycling where available."
        ),
        (
            ['collector', 'nearby', 'distance', 'map'],
            "Use the Service Area Map and 'Update My Location' to refresh nearby collectors and pickup routing."
        ),
        (
            ['login', 'account', 'password'],
            "You can log in using your registered account. If needed, use Password Reset from the login page."
        ),
    ]

    for keywords, response in fallback_knowledge:
        if any(keyword in q for keyword in keywords):
            return response

    return (
        "I can help with waste pickup requests, sorting guidance, collector routing, and account help. "
        "Try asking: 'How do I request pickup?' or 'How do I sort plastic waste?'"
    )


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


def generate_response(question, max_length=256, temperature=0.7, language='auto'):
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

    resolved_language = normalize_language(language, question)

    if resolved_language != 'en':
        return generate_localized_response(question, resolved_language)
    
    # Check if ML libraries are available
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
        return generate_fallback_response(question)
    
    # Load model if not already loaded
    if _model is None or _tokenizer is None:
        try:
            _model, _tokenizer = load_model()
            # Check if model loaded successfully
            if _model is None or _tokenizer is None:
                logger.warning("Chatbot model not available - returning fallback response")
                return generate_fallback_response(question)
        except Exception as e:
            logger.error(f"Error loading chatbot model: {str(e)}", exc_info=True)
            return generate_fallback_response(question)
    
    # Double-check model is available
    if _model is None or _tokenizer is None:
        return generate_fallback_response(question)
    
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
        return generate_fallback_response(question)


def is_model_loaded():
    """Check if model is loaded"""
    return _model is not None and _tokenizer is not None

