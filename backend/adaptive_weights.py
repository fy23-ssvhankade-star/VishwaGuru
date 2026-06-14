import json
import os
import logging
from typing import Dict, List, Any, Union

logger = logging.getLogger(__name__)

class AdaptiveWeights:
    """
    Manages adaptive weights for the Civic Intelligence Engine.
    Loads and saves configuration from data/modelWeights.json.
    Supports hot-reloading when the file changes on disk.
    """

    # Resolve absolute path to data directory relative to this file
    # This file is in backend/
    # data/ is in root/
    _BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    _ROOT_DIR = os.path.dirname(_BACKEND_DIR)
    DEFAULT_FILE_PATH = os.path.join(_ROOT_DIR, "data", "modelWeights.json")

    def __init__(self, file_path: str = None):
        if file_path is None:
            self.file_path = self.DEFAULT_FILE_PATH
        else:
            self.file_path = file_path

        self._last_mtime = 0.0
        self._weights = self._load_initial()

    def _get_defaults(self) -> Dict[str, Any]:
        """Returns the hardcoded default weights."""
        return {
            "severity_keywords": {
                "critical": [
                    "fire", "explosion", "blood", "death", "collapse", "gas leak",
                    "electric shock", "spark", "electrocution", "drowning",
                    "flood", "landslide", "earthquake", "cyclone", "hurricane",
                    "attack", "assault", "rabid", "deadly", "fatal", "emergency",
                    "blocked road", "ambulance", "hospital", "school", "child",
                    "exposed wire", "transformer", "chemical", "toxic", "poison",
                    "weapon", "gun", "bomb", "terror", "riot", "stampede",
                    "structural failure", "pillar", "bridge", "flyover",
                    "open manhole", "live wire", "gas smell", "open electrical box",
                    "burning", "flame", "smoke", "crack", "fissure"
                ],
                "high": [
                    "accident", "injury", "broken", "bleeding", "hazard", "risk",
                    "dangerous", "unsafe", "threat", "pollution", "smoke",
                    "sewage", "overflow", "contamination", "infection", "disease",
                    "mosquito", "dengue", "malaria", "typhoid", "cholera",
                    "rat", "snake", "stray dog", "bite", "attack", "cattle",
                    "theft", "robbery", "burglary", "harassment", "abuse",
                    "illegal", "crime", "violation", "bribe", "corruption",
                    "traffic jam", "congestion", "gridlock", "delay",
                    "no water", "power cut", "blackout", "load shedding",
                    "pothole", "manhole", "open drain", "water logging",
                    "dead", "animal", "fish", "stuck",
                    "not working", "signal", "traffic light", "fallen tree",
                    "water leakage", "leakage", "burst", "pipe burst", "damage",
                    "leaning", "tilted", "unstable", "waterlogging"
                ],
                "medium": [
                    "garbage", "trash", "waste", "litter", "rubbish", "dustbin",
                    "smell", "odor", "stink", "foul", "dirty", "unclean",
                    "messy", "ugly", "eyesore", "bad", "poor",
                    "leak", "drip", "seepage", "moisture", "damp",
                    "noise", "loud", "sound", "music", "party", "barking",
                    "encroachment", "hawker", "vendor", "stall", "shop",
                    "parking", "parked", "vehicle", "car", "bike", "scooter",
                    "construction", "debris", "material", "sand", "cement",
                    "graffiti", "poster", "banner", "hoarding", "advertisement",
                    "slippery", "muddy", "path", "pavement", "sidewalk",
                    "crowd", "gathering", "tap", "wasting", "running water",
                    "speed breaker", "hump", "bump"
                ],
                "low": [
                    "light", "lamp", "bulb", "flicker", "dim", "dark",
                    "sign", "board", "paint", "color", "faded",
                    "bench", "chair", "seat", "grass", "plant", "tree",
                    "leaf", "branch", "garden", "park", "playground",
                    "cosmetic", "look", "appearance", "aesthetic",
                    "old", "rusty", "dirty", "leaning"
                ]
            },
            "urgency_patterns": [
                [r"\b(now|immediately|urgent|emergency|critical|danger|help)\b", 20],
                [r"\b(today|tonight|morning|evening|afternoon)\b", 10],
                [r"\b(yesterday|last night|week|month)\b", 5],
                [r"\b(blood|bleeding|injury|hurt|pain|dead)\b", 25],
                [r"\b(fire|smoke|flame|burn|gas|leak|explosion)\b", 30],
                [r"\b(blocked|stuck|trapped|jam)\b", 15],
                [r"\b(school|hospital|clinic)\b", 15],
                [r"\b(child|kid|baby|elderly|senior)\b", 10]
            ],
            "categories": {
                "Abandoned Vehicle": ["abandoned", "car", "vehicle", "rust", "parked", "scooter", "bike"],
                "Fire": ["fire", "smoke", "flame", "burn", "explosion", "burning"],
                "Pothole": ["pothole", "hole", "crater", "road damage", "broken road"],
                "Street Light": ["light", "lamp", "bulb", "dark", "street light", "flicker"],
                "Garbage": ["garbage", "trash", "waste", "litter", "rubbish", "dump", "dustbin"],
                "Water Leak": ["water", "leak", "pipe", "burst", "flood", "seepage", "drip", "leakage", "tap", "running"],
                "Stray Animal": ["dog", "cat", "cow", "cattle", "monkey", "bite", "stray", "animal", "rabid", "dead animal"],
                "Construction Safety": ["construction", "debris", "material", "cement", "sand", "building"],
                "Illegal Parking": ["parking", "parked", "blocking", "vehicle", "car", "bike"],
                "Vandalism": ["graffiti", "paint", "broken", "destroy", "damage", "poster"],
                "Infrastructure": ["bridge", "flyover", "pillar", "crack", "collapse", "structure", "manhole", "drain", "wire", "cable", "pole", "electrical box", "electric box", "transformer", "sidewalk", "pavement", "tile", "speed breaker", "road"],
                "Traffic Sign": ["sign", "signal", "light", "traffic", "board", "direction", "stop sign"],
                "Public Facilities": ["toilet", "washroom", "bench", "seat", "park", "garden", "playground", "slide", "swing"],
                "Tree Hazard": ["tree", "branch", "fallen", "root", "leaf"],
                "Accessibility": ["ramp", "wheelchair", "step", "stair", "access", "disability"],
                "Noise Pollution": ["noise", "loud", "sound", "music", "speaker"],
                "Air Pollution": ["smoke", "dust", "fume", "smell", "pollution", "air"],
                "Water Pollution": ["river", "lake", "pond", "chemical", "oil", "poison", "fish"],
                "Health Hazard": ["mosquito", "dengue", "malaria", "rat", "disease", "health"],
                "Crowd": ["crowd", "gathering", "mob", "people", "protest"],
                "Gas Leak": ["gas", "leak", "smell", "cylinder", "pipeline"],
                "Environment": ["tree", "cutting", "deforestation", "forest", "nature"],
                "Flooding": ["flood", "waterlogging", "water logged", "rain", "drainage"]
            },
            "duplicate_search_radius": 50.0
        }

    def _load_initial(self) -> Dict[str, Any]:
        """Loads weights initially, creating file if needed."""
        try:
            if not os.path.exists(self.file_path):
                logger.info(f"Weights file not found at {self.file_path}. Using defaults.")
                defaults = self._get_defaults()
                # Ensure directory exists
                dirname = os.path.dirname(self.file_path)
                if dirname:
                    os.makedirs(dirname, exist_ok=True)
                self._save_weights_to_file(defaults)
                # Track mtime
                try:
                    self._last_mtime = os.path.getmtime(self.file_path)
                except OSError:
                    pass
                return defaults

            self._last_mtime = os.path.getmtime(self.file_path)
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading weights from {self.file_path}: {e}")
            return self._get_defaults()

    def _check_reload(self):
        """Checks if file has changed and reloads if necessary."""
        try:
            # Resolve path absolute to handle cwd differences if needed
            # For now relying on relative path consistency
            if not os.path.exists(self.file_path):
                return

            mtime = os.path.getmtime(self.file_path)
            if mtime > self._last_mtime:
                logger.info(f"Detected change in {self.file_path}, reloading weights...")
                with open(self.file_path, 'r') as f:
                    self._weights = json.load(f)
                self._last_mtime = mtime
        except Exception as e:
            logger.error(f"Error checking reload for {self.file_path}: {e}")

    def _save_weights_to_file(self, weights: Dict[str, Any]):
        """Saves weights to JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(weights, f, indent=4)
            # Update mtime so we don't trigger reload on our own write immediately
            # (though it wouldn't hurt, just redundant)
            self._last_mtime = os.path.getmtime(self.file_path)
        except Exception as e:
            logger.error(f"Error saving weights to {self.file_path}: {e}")

    def get_weights(self) -> Dict[str, Any]:
        """Returns current weights, reloading if file changed."""
        self._check_reload()
        return self._weights

    def update_weights(self, new_weights: Dict[str, Any]):
        """Updates weights and saves to file."""
        self._weights.update(new_weights)
        self._save_weights_to_file(self._weights)

    def get_duplicate_search_radius(self) -> float:
        self._check_reload()
        return self._weights.get("duplicate_search_radius", 50.0)

# Singleton instance
adaptive_weights = AdaptiveWeights()
