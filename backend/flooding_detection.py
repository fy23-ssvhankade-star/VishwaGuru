from PIL import Image
from hf_service import detect_flooding_clip

def detect_flooding(image: Image.Image):
    """
    Detects flooding in an image.
    Delegates to the Hugging Face service.
    """
    return detect_flooding_clip(image)
