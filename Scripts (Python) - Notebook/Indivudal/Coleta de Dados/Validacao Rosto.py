import json
import io
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import cv2
from PIL import Image
from cryptography.fernet import Fernet

# Constants
DATA_DIR = Path("form_data")
KEY_FILE = Path("rg_encryption.key")
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
FACE_SIZE = (150, 150)
DISTANCE_THRESHOLD = 60.0  # adjustable threshold for face match

def load_fernet_key(key_path: Path) -> Fernet:
    """
    Load Fernet encryption key from file.
    """
    with key_path.open("rb") as f:
        key = f.read()
    return Fernet(key)


def load_latest_form(data_dir: Path) -> tuple[Dict[str, Any], Path]:
    """
    Load the most recent JSON form from data_dir, returning the data and its file path.
    """
    json_files = sorted(data_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {data_dir}")
    latest = json_files[0]
    with latest.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # retornamos também o caminho do arquivo JSON para permitir regravação
    return data, latest


def decrypt_image(encrypted_filename: str, fernet: Fernet, data_dir: Path) -> Image.Image:
    """
    Decrypt an image file and return a PIL Image.
    """
    encrypted_path = data_dir / encrypted_filename
    if not encrypted_path.exists():
        raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
    data = fernet.decrypt(encrypted_path.read_bytes())
    return Image.open(io.BytesIO(data))


def load_plain_image(filename: str, data_dir: Path) -> Image.Image:
    """
    Load a non-encrypted image from disk as PIL Image.
    """
    img_path = data_dir / filename
    if not img_path.exists():
        raise FileNotFoundError(f"Image file not found: {img_path}")
    return Image.open(img_path)


def pil_to_bgr(img: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to OpenCV BGR numpy array.
    """
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def detect_face(image_bgr: np.ndarray, cascade: cv2.CascadeClassifier) -> Optional[np.ndarray]:
    """
    Detect the first face in a BGR image, crop and resize it.
    Returns the grayscale face ROI or None.
    """
    faces = cascade.detectMultiScale(image_bgr, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    face = image_bgr[y:y+h, x:x+w]
    face_resized = cv2.resize(face, FACE_SIZE)
    return cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)


def compare_faces(gray1: np.ndarray, gray2: np.ndarray) -> float:
    """
    Compute mean absolute difference between two grayscale face images.
    """
    diff = cv2.absdiff(gray1, gray2)
    return float(np.mean(diff))


def perform_face_comparison_opencv(
    img1_pil: Image.Image, img2_pil: Image.Image, threshold: float = DISTANCE_THRESHOLD
) -> Dict[str, Any]:
    """
    Compare two PIL images containing faces using OpenCV Haar cascades.
    Returns a dict with match result, distance, and status.
    """
    results: Dict[str, Any] = {
        'face_match': False,
        'distance': None,
        'success': False,
        'message': ''
    }
    try:
        img1_bgr = pil_to_bgr(img1_pil)
        img2_bgr = pil_to_bgr(img2_pil)

        cascade = cv2.CascadeClassifier(CASCADE_PATH)
        if cascade.empty():
            raise RuntimeError(f"Failed to load cascade classifier at {CASCADE_PATH}")

        face1 = detect_face(img1_bgr, cascade)
        face2 = detect_face(img2_bgr, cascade)

        if face1 is None or face2 is None:
            results['message'] = "No face detected in one or both images."
            return results

        distance = compare_faces(face1, face2)
        results['distance'] = float(distance)
        results['face_match'] = bool(distance < threshold)
        results['success'] = True
        results['message'] = "Comparison successful with OpenCV."
    except Exception as e:
        results['message'] = f"Error during face comparison: {e}"
    return results


if __name__ == "__main__":
    # Initialize
    fernet = load_fernet_key(KEY_FILE)
    form_data, form_path = load_latest_form(DATA_DIR)

    # Decrypt RG image
    encrypted_rg = form_data.get("rgImagem_encrypted")
    img_doc = decrypt_image(encrypted_rg, fernet, DATA_DIR)

    # Load selfie (not encrypted)
    selfie_filename = form_data.get("selfieImagem_file")
    img_selfie = load_plain_image(selfie_filename, DATA_DIR)

    # Run comparison
    result = perform_face_comparison_opencv(img_doc, img_selfie)

    # Add result index to form data
    form_data['rosto_correto_indice'] = 1 if result.get('face_match') else 0
    form_data['face_match'] = result.get('face_match')
    form_data['face_distance'] = result.get('distance')

    # Save updated JSON back to file
    with form_path.open('w', encoding='utf-8') as f:
        json.dump(form_data, f, indent=4, ensure_ascii=False)

    # Print JSON-safe result
    print(json.dumps(result, indent=4, ensure_ascii=False))
