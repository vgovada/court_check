"""CourtCheck website. Run from the repo root:

    streamlit run app/app.py

Python loads the data and photos, then hands them to site.html,
which runs the whole interactive page.
"""

import base64
import json
from pathlib import Path

import cv2
import streamlit as st
import streamlit.components.v1 as components

from data import DATA_DIR, load_courts

st.set_page_config(page_title="CourtCheck", page_icon="🏀", layout="wide",
                   initial_sidebar_state="collapsed")

# Make the page fill the whole browser window
st.markdown(
    """
    <style>
    header[data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { overflow: hidden !important; background: #2b0000; }
    .block-container, [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
    iframe { height: 100vh !important; width: 100vw !important; display: block; border: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

PHOTO_NAMES = {
    "basketball_cloth_A": "Basketball A",
    "basketball_court_B": "Basketball B",
    "volleyball_cloth": "Volleyball",
    "pickleball_cloth": "Pickleball",
    "badminton_cloth": "Badminton",
    "soccer_cloth": "Soccer",
}


@st.cache_data
def load_photos():
    """Shrink each cloth photo and turn it into text the page can display."""
    photos = []
    for path in sorted((DATA_DIR / "photos").glob("*.jpg")):
        img = cv2.imread(str(path))
        if img is None:
            continue
        scale = 360 / max(img.shape[:2])
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            photos.append({
                "name": PHOTO_NAMES.get(path.stem, path.stem.replace("_", " ").title()),
                "src": "data:image/jpeg;base64," + base64.b64encode(buf).decode(),
            })
    return photos


# Put photos in app/images/ with these names (jpg or png). Missing ones show a placeholder.
TEAM_IMAGES = {
    "joseph": "Joseph Gwak", "william": "William Lee", "vidhur": "Vidhur Govada",
    "gallery1": "The CourtCheck team at TAMU Datathon", "gallery2": "Spring-scale pull test with a weighted shoe", "gallery3": "Wiping a court with a white cloth",
}


@st.cache_data
def load_team_images():
    out = {}
    for key, alt in TEAM_IMAGES.items():
        for ext in ("jpg", "jpeg", "png"):
            path = Path(__file__).parent / "images" / f"{key}.{ext}"
            if not path.exists():
                continue
            img = cv2.imread(str(path))
            if img is None:
                break
            scale = min(1.0, 900 / max(img.shape[:2]))
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if ok:
                out[key] = {"src": "data:image/jpeg;base64," + base64.b64encode(buf).decode(), "alt": alt}
            break
    return out


def font_b64(name):
    """Bundle the handwriting font into the page so it always shows."""
    return base64.b64encode((Path(__file__).parent / "fonts" / name).read_bytes()).decode()


data = load_courts()
measured = [t["dustiness"] for c in data["courts"] for t in c["times"].values() if t["measured"]]

html = (Path(__file__).parent / "site.html").read_text(encoding="utf-8")
for key, value in {
    "__DATA__": json.dumps(data),
    "__IMAGES__": json.dumps(load_team_images()),
    "__PHOTOS__": json.dumps(load_photos()),
    "__SAMPLES__": str(sum(c["samples"] for c in data["courts"])),
    "__GROUPS__": str(len(data["courts"])),
    "__COURTS__": str(sum(len(c["courts"]) for c in data["courts"])),
    "__MAXDUST__": str(max(measured)),
    "__CLEAN__": f"{data['clean_friction']:g}",
    "__SHOE__": f"{data['shoe_weight']:g}",
    "__CAVEAT_500__": font_b64("caveat-latin-500-normal.woff2"),
    "__CAVEAT_700__": font_b64("caveat-latin-700-normal.woff2"),
}.items():
    html = html.replace(key, value)

components.html(html, height=900, scrolling=True)
