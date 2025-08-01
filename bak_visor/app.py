import json
from dataclasses import asdict

import pandas as pd
import streamlit as st

from visor.constants import IMAGE_FOLDER
from visor.constants import METADATA_FILE
from visor.models import Metadata
from visor.utils import get_visible_images
from visor.utils import save_metadata

# Streamlit configuration
st.set_page_config(layout="wide")

# Load or create metadata
if METADATA_FILE.exists():
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata_list = [Metadata(**item) for item in json.load(f)]
else:
    metadata_list = []

# Create a DataFrame
df = pd.DataFrame([asdict(m) for m in metadata_list])
if df.empty:
    df = pd.DataFrame(columns=list(Metadata.__annotations__.keys()))
df.set_index("filename", inplace=True)

# Session state for navigation
if "image_index" not in st.session_state:
    st.session_state.image_index = 0
if "image_files" not in st.session_state:
    st.session_state.image_files = sorted([f.name for f in IMAGE_FOLDER.iterdir() if f.suffix.lower() in [".jpg", ".png", ".jpeg"]])
if "filter_missing" not in st.session_state:
    st.session_state.filter_missing = False

# UI
st.markdown("<h1 style='text-align: center;'>✨ Aesthetics Catalog ✨</h1>", unsafe_allow_html=True)
st.markdown("</br>", unsafe_allow_html=True)

st.checkbox("Show only images without metadata", key="filter_missing")
completed = len(df.index)
total = len(st.session_state.image_files)
if total > 0:
    st.progress(completed / total)
    st.markdown(f"**{completed} / {total} images have metadata.**")

button_col1, button_col2, button_col3, button_col4 = st.columns([1, 1, 1, 1])
with button_col2:
    if st.button("⬅️ Prev", use_container_width=True):
        visible_images = get_visible_images(df)
        st.session_state.image_index = (st.session_state.image_index - 1) % len(visible_images)
with button_col3:
    if st.button("Next ➡️", use_container_width=True):
        visible_images = get_visible_images(df)
        st.session_state.image_index = (st.session_state.image_index + 1) % len(visible_images)

visible_images = get_visible_images(df)
if not visible_images:
    st.warning("No images to display!")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    selected_image = visible_images[st.session_state.image_index]
    img_path = IMAGE_FOLDER / selected_image
    st.image(str(img_path), use_container_width=True)

    if selected_image not in df.index:
        df.loc[selected_image] = asdict(Metadata())

with col2:
    if st.button("🔍 Buscar con agente"):
        with st.spinner("Consultando agente..."):
            suggestion = None  # run_agent_pipeline(img_path)
            st.session_state.suggested_meta = suggestion
    with st.form(key="edit_form"):
        current_metadata = Metadata(**df.loc[selected_image].fillna("").to_dict())

        st.markdown(f"##### Filename: {selected_image}")
        title = st.text_input("Title", current_metadata.title)
        author = st.text_input("Author", current_metadata.author)
        year = st.text_input("Year", current_metadata.year)
        description = st.text_area("Description", current_metadata.description)
        source = st.text_input("Source", current_metadata.source)
        tags_input = st.text_input("Tags (separated by commas)", value=", ".join(current_metadata.tags))
        museum = st.text_input("Museum", current_metadata.museum)
        material = st.text_input("Material", current_metadata.material)
        style = st.text_input("Style", current_metadata.style)
        dimensions = st.text_input("Dimensions", current_metadata.dimensions)

        submitted = st.form_submit_button("Save changes")
        if submitted:
            updated_metadata = Metadata(
                filename=selected_image,
                title=title,
                author=author,
                year=year,
                tags=[tag.strip() for tag in tags_input.split(",") if tag.strip()],
                description=description,
                museum=museum,
                material=material,
                style=style,
                dimensions=dimensions,
                source=source
            )
            save_metadata(selected_image, updated_metadata, df)
            st.success("Metadata saved!")
        if 'suggested_meta' in st.session_state:
            sugg = st.session_state.suggested_meta
            with st.expander("Proposed metadata", expanded=True):
                st.json(asdict(sugg))
                if st.button("✅ Accept suggestion"):
                    save_metadata(selected_image, sugg, df)
                    st.success("Metadata imported!")
                    del st.session_state['suggested_meta']
