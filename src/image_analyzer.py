"""
Image analysis module for AccessiAI.
Generates alt text for images using the BLIP image captioning model.
"""

import requests
from PIL import Image
from io import BytesIO
from typing import List, Dict, Optional, Tuple
import logging
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = "Salesforce/blip-image-captioning-base"
MAX_ALT_TEXT_LENGTH = 125
IMAGE_DOWNLOAD_TIMEOUT = 10  # seconds
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Global model cache
_model_cache = {
    "processor": None,
    "model": None,
    "device": None
}


def _get_device() -> str:
    """
    Detect available device (GPU or CPU).
    
    Returns:
        Device string ("cuda" or "cpu")
    """
    if torch.cuda.is_available():
        logger.info("GPU detected, using CUDA")
        return "cuda"
    else:
        logger.info("GPU not available, using CPU")
        return "cpu"


def _load_model(device: Optional[str] = None) -> Tuple:
    """
    Load BLIP model and processor with caching.
    
    Args:
        device: Device to load model on ("cuda" or "cpu"). Auto-detected if None.
        
    Returns:
        Tuple of (processor, model, device)
    """
    global _model_cache
    
    # Return cached model if available
    if _model_cache["model"] is not None:
        return _model_cache["processor"], _model_cache["model"], _model_cache["device"]
    
    # Detect device if not specified
    if device is None:
        device = _get_device()
    
    try:
        logger.info(f"Loading BLIP model: {MODEL_NAME}")
        processor = BlipProcessor.from_pretrained(MODEL_NAME)
        model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)
        model.to(device)
        model.eval()
        
        # Cache the model
        _model_cache["processor"] = processor
        _model_cache["model"] = model
        _model_cache["device"] = device
        
        logger.info("BLIP model loaded successfully")
        return processor, model, device
    
    except Exception as e:
        logger.error(f"Failed to load BLIP model: {e}")
        raise RuntimeError(f"Could not load image captioning model: {e}")


def download_image(url: str) -> Optional[Image.Image]:
    """
    Download an image from a URL.
    
    Args:
        url: Image URL
        
    Returns:
        PIL Image object or None if download fails
    """
    if not url:
        logger.warning("Empty image URL provided")
        return None
    
    try:
        # Handle relative URLs
        if url.startswith("/"):
            logger.warning(f"Relative image URL not supported: {url}")
            return None
        
        headers = {"User-Agent": DEFAULT_USER_AGENT}
        response = requests.get(url, timeout=IMAGE_DOWNLOAD_TIMEOUT, headers=headers)
        response.raise_for_status()
        
        # Open image from bytes
        image = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        logger.info(f"Successfully downloaded image: {url}")
        return image
    
    except requests.exceptions.Timeout:
        logger.warning(f"Image download timeout: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error downloading image: {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP error downloading image {url}: {e.response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error downloading image {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Error processing image {url}: {e}")
        return None


def generate_alt_text(image: Image.Image) -> Optional[str]:
    """
    Generate alt text for an image using BLIP model.
    
    Args:
        image: PIL Image object
        
    Returns:
        Generated alt text string or None if generation fails
    """
    if image is None:
        return None
    
    try:
        # Load model
        processor, model, device = _load_model()
        
        # Prepare image
        inputs = processor(image, return_tensors="pt").to(device)
        
        # Generate caption
        with torch.no_grad():
            out = model.generate(**inputs, max_length=50)
        
        # Decode caption
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        # Truncate to max length if needed
        if len(caption) > MAX_ALT_TEXT_LENGTH:
            caption = caption[:MAX_ALT_TEXT_LENGTH].rsplit(" ", 1)[0] + "..."
        
        logger.info(f"Generated alt text: {caption}")
        return caption
    
    except Exception as e:
        logger.error(f"Error generating alt text: {e}")
        return None


def process_images(images: List[Dict]) -> List[Dict]:
    """
    Batch process images to generate alt text for those lacking it.
    
    Args:
        images: List of image dictionaries from parse_images()
                Each should have: url, alt_text, has_alt, element_id
    
    Returns:
        List of image dictionaries with generated_alt_text added
    """
    processed_images = []
    
    for idx, image_data in enumerate(images):
        # Skip images that already have alt text
        if image_data.get("has_alt"):
            image_data["generated_alt_text"] = None
            processed_images.append(image_data)
            continue
        
        # Download image
        image_url = image_data.get("url", "")
        image = download_image(image_url)
        
        if image is None:
            logger.warning(f"Could not download image {idx + 1}/{len(images)}: {image_url}")
            image_data["generated_alt_text"] = None
            processed_images.append(image_data)
            continue
        
        # Generate alt text
        alt_text = generate_alt_text(image)
        
        if alt_text:
            image_data["generated_alt_text"] = alt_text
            logger.info(f"Processed image {idx + 1}/{len(images)}: {image_url}")
        else:
            logger.warning(f"Failed to generate alt text for image {idx + 1}/{len(images)}: {image_url}")
            image_data["generated_alt_text"] = None
        
        processed_images.append(image_data)
    
    return processed_images


def clear_model_cache() -> None:
    """
    Clear the cached model to free memory.
    Useful when processing is complete or memory is needed for other tasks.
    """
    global _model_cache
    
    if _model_cache["model"] is not None:
        try:
            # Move model to CPU and delete
            if _model_cache["device"] == "cuda":
                _model_cache["model"].to("cpu")
            del _model_cache["model"]
            del _model_cache["processor"]
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            logger.info("Model cache cleared")
        except Exception as e:
            logger.warning(f"Error clearing model cache: {e}")
    
    _model_cache["processor"] = None
    _model_cache["model"] = None
    _model_cache["device"] = None
