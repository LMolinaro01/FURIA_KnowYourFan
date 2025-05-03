import os
import io
import json
import re
import hashlib

from PIL import Image
import numpy as np
import cv2
import pytesseract
from cryptography.fernet import Fernet

# ————————— Configurações Tesseract —————————
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESS_CONF_FULL   = "--oem 3 --psm 3"
TESS_CONF_DIGITS = "--oem 3 --psm 3 -c tessedit_char_whitelist=0123456789"
TESS_CONF_MRZ    = "--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ<"

DATA_DIR = "form_data"
KEY_FILE = "rg_encryption.key"

# ————————— Carrega chave e dados do JSON mais recente válido —————————
fernet = Fernet(open(KEY_FILE, "rb").read())

# Lista e filtra os JSONs válidos (com estrutura de dicionário)
json_files = sorted(
    [f for f in os.listdir(DATA_DIR) if f.endswith(".json") and f != 'last_user_id.json'],
    key=lambda fn: os.path.getmtime(os.path.join(DATA_DIR, fn)),
    reverse=True
)

valid_json_files = []
for f in json_files:
    path = os.path.join(DATA_DIR, f)
    try:
        with open(path, encoding="utf-8") as j:
            data = json.load(j)
            if isinstance(data, dict):
                valid_json_files.append(f)
    except Exception:
        continue

if not valid_json_files:
    raise FileNotFoundError("Nenhum JSON válido (tipo dicionário) encontrado em 'form_data'.")

latest_json = valid_json_files[0]
user_id = os.path.splitext(latest_json)[0]
form_data = json.load(open(os.path.join(DATA_DIR, latest_json), encoding="utf-8"))
provided_name = form_data.get("nome", "")
cpf_hash = form_data.get("cpf", "")

# ————————— Decrypt + carrega imagem em alta resolução (×2) —————————
encrypted_fn = form_data.get("rgImagem_encrypted")
if encrypted_fn:
    enc_path = os.path.join(DATA_DIR, encrypted_fn)
    try:
        raw_bytes = fernet.decrypt(open(enc_path, "rb").read())
        pil = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        pil = pil.resize((pil.width * 2, pil.height * 2), Image.LANCZOS)
        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Erro ao descriptografar '{encrypted_fn}': {e}")
        img = None
else:
    print("Aviso: 'rgImagem_encrypted' not found in form_data")
    img = None

# ————————— Pré-processamento e OCR —————————
if img is not None:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(gray)
    _, prep = cv2.threshold(cl, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    full_ocr_text = pytesseract.image_to_string(prep, config=TESS_CONF_FULL, lang="por+eng")
else:
    full_ocr_text = ""
    print("Skipping OCR: no image available.")

# ————————— Função de validação de CPF —————————
def valida_cpf(c: str) -> bool:
    if len(c) != 11 or c == c[0]*11:
        return False
    s1 = sum(int(c[i])*(10-i) for i in range(9))
    d1 = ((s1*10) % 11) % 10
    s2 = sum(int(c[i])*(11-i) for i in range(10))
    d2 = ((s2*10) % 11) % 10
    return c[-2:] == f"{d1}{d2}"

# ————————— Extrai Nome via MRZ —————————
name = None
name_ocr_raw = None
mrz_lines = [L.strip() for L in full_ocr_text.splitlines() if "<<" in L]
if mrz_lines:
    mrz = mrz_lines[-1]
    parts = mrz.split("<<")
    if len(parts) >= 2:
        surname = parts[0].title()
        given_list = [p for p in parts[1].split("<") if p]
        given_reversed = list(reversed(given_list))
        name = " ".join(p.title() for p in given_reversed + [surname])
        name_ocr_raw = mrz

# Normalize and compare
def normalize(n: str) -> str:
    t = re.sub(r'\b(?:de|da|dos|das|do)\b','', n, flags=re.IGNORECASE)
    return re.sub(r'\s+','', t).lower()

name_match = bool(name and normalize(name) == normalize(provided_name))
if name_match:
    name = provided_name

# ————————— Extração da Naturalidade —————————
naturalidade = None
naturalidade_match = False
m = re.search(
    r'(?:Naturalidade|Natural de|Natural)\s*[:\-]?\s*([\wÀ-ú\s]+)[-/]?\s*([A-Za-z]{2})',
    full_ocr_text,
    flags=re.IGNORECASE
)
if m:
    cidade = m.group(1).strip().title()
    estado = m.group(2).strip().upper()
    naturalidade = f"{cidade} - {estado}"
else:
    f2 = re.search(r'ESTADO DE\s+([\wÀ-ú]+)\s+([A-Za-z]{2})', full_ocr_text, flags=re.IGNORECASE)
    if f2:
        cidade = f2.group(1).strip().title()
        estado = f2.group(2).strip().upper()
        naturalidade = f"{cidade} - {estado}"

expected_city = form_data.get("endereco", "").strip().lower()
if naturalidade:
    naturalidade_match = (naturalidade.split(" - ")[0].strip().lower() == expected_city)

# ————————— Atualiza e salva o JSON —————————
form_data.update({
    "naturalidade_extraida": naturalidade,
    "naturalidade_match": naturalidade_match,
    "name_match": name_match
})
with open(os.path.join(DATA_DIR, latest_json), "w", encoding="utf-8") as f:
    json.dump(form_data, f, ensure_ascii=False, indent=4)

# ————————— Exibe resultado —————————
result = {
    "full_ocr_text": full_ocr_text,
    "name": name,
    "name_ocr_raw": name_ocr_raw,
    "name_match": name_match,
    "naturalidade": naturalidade,
    "naturalidade_match": naturalidade_match
}
print(json.dumps(result, indent=4, ensure_ascii=False))
