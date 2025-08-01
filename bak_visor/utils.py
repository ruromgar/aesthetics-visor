import json
import shutil
from dataclasses import asdict

import pandas as pd
import streamlit as st

from visor.constants import IMAGE_FOLDER
from visor.constants import METADATA_FILE
from visor.models import Metadata


def save_metadata(selected_image: str, metadata: Metadata, df: pd.DataFrame):
    old_path = IMAGE_FOLDER / selected_image
    base_name = generate_filename(metadata)
    new_filename = base_name + old_path.suffix
    counter = 1
    while (IMAGE_FOLDER / new_filename).exists() and new_filename != selected_image:
        new_filename = f"{base_name} ({counter})" + old_path.suffix
        counter += 1
    if new_filename != selected_image:
        new_path = IMAGE_FOLDER / new_filename
        shutil.move(str(old_path), str(new_path))
        df.rename(index={selected_image: new_filename}, inplace=True)
        st.session_state.image_files[st.session_state.image_index] = new_filename

    df.loc[new_filename] = asdict(metadata)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(df.reset_index().to_dict(orient="records"), f, ensure_ascii=False, indent=2)


def get_visible_images(df: pd.DataFrame):
    if st.session_state.filter_missing:
        return [img for img in st.session_state.image_files if img not in df.index]
    return st.session_state.image_files


def split_author(author: str):
    parts = author.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[1], parts[0]  # Apellido, Nombre
    else:
        return parts[0], ""  # Solo un nombre, sin apellido


def generate_filename(metadata: Metadata):
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_.,()")
    surname, firstname = split_author(metadata.author)

    if metadata.year:
        filename = f"{surname}, {firstname} - {metadata.title} ({metadata.year})"
    else:
        filename = f"{surname}, {firstname} - {metadata.title}"

    return "".join(c for c in filename if c in valid_chars).rstrip()
