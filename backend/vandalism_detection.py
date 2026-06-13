from hf_service import detect_vandalism_clip
from PIL import Image

def detect_vandalism(image: Image.Image):
    """
    Wrapper for vandalism detection using HF Service.
    """
    return detect_vandalism_clip(image)
