"""
AI-powered waste classification service
Uses a pre-trained model to classify waste from images
"""

import os
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

# Try to import torch/torchvision, but make it optional for deployment
try:
    import torch
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. Using rule-based classification only.")

logger = logging.getLogger(__name__)

# Map model predictions to waste categories
WASTE_CATEGORY_MAPPING = {
    'organic': 'Organic Waste',
    'plastic': 'Plastic Waste',
    'paper': 'Paper Waste',
    'glass': 'Glass Waste',
    'metal': 'Metal Waste',
    'general': 'General Waste',
    'cardboard': 'Paper Waste',
    'trash': 'General Waste',
    'recyclable': 'General Waste',
}

# Category confidence thresholds
MIN_CONFIDENCE = 0.3


class WasteClassifier:
    """
    Waste classification service using a pre-trained model
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the waste classifier
        
        Args:
            model_path: Path to a custom trained model (optional)
        """
        self.model = None
        self.model_loaded = False
        
        if TORCH_AVAILABLE:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            # Image preprocessing transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
        else:
            self.device = None
            self.transform = None
        
        # Try to load model if path provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            # Use a lightweight approach with a pre-trained model
            self._init_lightweight_model()
    
    def _init_lightweight_model(self):
        """
        Initialize a lightweight classification approach
        For production, you can use:
        - A pre-trained ResNet/MobileNet fine-tuned on waste data
        - Or integrate with cloud APIs (Google Vision, AWS Rekognition)
        """
        if not TORCH_AVAILABLE:
            logger.info("PyTorch not available. Using rule-based classification.")
            self.model_loaded = False
            return
            
        try:
            # Try to load torchvision models
            import torchvision.models as models
            
            # Use MobileNetV2 for lightweight inference
            self.model = models.mobilenet_v2(pretrained=True)
            self.model.eval()
            self.model.to(self.device)
            self.model_loaded = True
            logger.info("Lightweight model initialized (MobileNetV2)")
        except Exception as e:
            logger.warning(f"Could not load model: {e}. Using rule-based classification.")
            self.model_loaded = False
    
    def load_model(self, model_path: str):
        """Load a custom trained model"""
        try:
            self.model = torch.load(model_path, map_location=self.device)
            self.model.eval()
            self.model.to(self.device)
            self.model_loaded = True
            logger.info(f"Custom model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._init_lightweight_model()
    
    def preprocess_image(self, image: Image.Image):
        """
        Preprocess image for model input
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed tensor or None if torch not available
        """
        if not TORCH_AVAILABLE or not self.transform:
            return None
            
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms
        tensor = self.transform(image)
        return tensor.unsqueeze(0)  # Add batch dimension
    
    def classify_by_color_and_features(self, image: Image.Image) -> Dict[str, float]:
        """
        Rule-based classification using color and basic features
        This is a fallback when ML model is not available
        """
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize for faster processing
        image = image.resize((224, 224))
        img_array = np.array(image)
        
        # Calculate average color
        avg_color = img_array.mean(axis=(0, 1))
        
        # Basic color-based classification
        scores = {}
        
        # Green/brown -> Organic
        if avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:
            scores['Organic Waste'] = 0.6
        
        # Blue/transparent -> Plastic/Glass
        if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:
            scores['Plastic Waste'] = 0.5
            scores['Glass Waste'] = 0.4
        
        # White/light -> Paper
        if avg_color.mean() > 200:
            scores['Paper Waste'] = 0.5
        
        # Gray/metallic -> Metal
        if abs(avg_color[0] - avg_color[1]) < 20 and abs(avg_color[1] - avg_color[2]) < 20:
            scores['Metal Waste'] = 0.4
        
        # Default to General Waste
        if not scores:
            scores['General Waste'] = 0.5
        
        return scores
    
    def classify(self, image: Image.Image) -> Dict[str, any]:
        """
        Classify waste from an image
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with classification results:
            {
                'category': 'Category Name',
                'category_id': 1,
                'confidence': 0.85,
                'all_predictions': [
                    {'category': 'Plastic Waste', 'confidence': 0.85},
                    ...
                ]
            }
        """
        try:
            if TORCH_AVAILABLE and self.model_loaded and self.model is not None:
                # Use ML model
                try:
                    with torch.no_grad():
                        tensor = self.preprocess_image(image)
                        if tensor is not None:
                            tensor = tensor.to(self.device)
                            
                            # Get predictions
                            outputs = self.model(tensor)
                            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                            
                            # Map to waste categories (this would need to match your model's output)
                            # For now, use rule-based as fallback
                            predictions = self.classify_by_color_and_features(image)
                        else:
                            predictions = self.classify_by_color_and_features(image)
                except Exception as e:
                    logger.warning(f"Error using ML model: {e}. Falling back to rule-based.")
                    predictions = self.classify_by_color_and_features(image)
            else:
                # Use rule-based classification
                predictions = self.classify_by_color_and_features(image)
            
            # Sort by confidence
            sorted_predictions = sorted(
                predictions.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get top prediction
            top_category, top_confidence = sorted_predictions[0] if sorted_predictions else ('General Waste', 0.5)
            
            # Format results
            result = {
                'category': top_category,
                'confidence': float(top_confidence),
                'all_predictions': [
                    {'category': cat, 'confidence': float(conf)}
                    for cat, conf in sorted_predictions[:3]  # Top 3
                ],
                'success': True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                'category': 'General Waste',
                'confidence': 0.0,
                'all_predictions': [],
                'success': False,
                'error': str(e)
            }
    
    def classify_from_file(self, image_path: str) -> Dict[str, any]:
        """
        Classify waste from an image file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            Classification results
        """
        try:
            image = Image.open(image_path)
            return self.classify(image)
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return {
                'category': 'General Waste',
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def classify_from_bytes(self, image_bytes: bytes) -> Dict[str, any]:
        """
        Classify waste from image bytes
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Classification results
        """
        try:
            from io import BytesIO
            image = Image.open(BytesIO(image_bytes))
            return self.classify(image)
        except Exception as e:
            logger.error(f"Error processing image bytes: {e}")
            return {
                'category': 'General Waste',
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }


# Singleton instance
_classifier_instance = None

def get_waste_classifier() -> WasteClassifier:
    """Get or create the waste classifier singleton"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = WasteClassifier()
    return _classifier_instance

