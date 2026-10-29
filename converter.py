"""
converter.py — Conversor de cursos ya descargados (.txt) a Dashboard HTML Interactivo y Markdown.
Permite actualizar cualquier carpeta existente de transcripciones al nuevo formato interactivo
con ordenación natural, detección de codificación y soporte de IDs únicos.
"""

import os
import sys
import re
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from html_generator import generate_interactive_html, extract_key_points
from markdown_generator import generate_course_markdown


def natural_sort_key(path_or_str):
    """
    Ordenación natural para que '2 - Lección' vaya antes que '10 - Lección'.
    """
    name = path_or_str.name if hasattr(path_or_str, "name") else str(path_or_str)
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', name)]


def safe_read_file(path):
    """
    Lee un archivo de texto con detección defensiva de codificación (UTF-8 -> CP1252 -> Latin-1).
    """
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except Exception:
        return ""

    for enc in ["utf-8", "utf-8-sig", "cp1252", "latin-1"]:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def convert_local_course_directory(course_dir_path):
    """
    Lee una carpeta existente de un curso con subcarpetas de secciones y archivos .txt,
    y genera 'index.html', 'course_data.js' y 'FULL_COURSE.md'.
    """
    course_path = Path(course_dir_path)
    if not course_path.exists() or not course_path.is_dir():
        print(f"[!] La ruta no existe o no es una carpeta: {course_dir_path}")
        return False

    course_title = course_path.name
    print(f"\n[🔄] Procesando carpeta del curso: {course_title}")

    # Detectar si hay subcarpetas de secciones o si los archivos están directos
    raw_subdirs = [d for d in course_path.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))]
    subdirs = sorted(raw_subdirs, key=natural_sort_key)
    sections_data = []

    if subdirs:
        # Modo con secciones organizadas en carpetas
        for s_idx, s_dir in enumerate(subdirs, 1):
            raw_files = [f for f in s_dir.iterdir() if f.is_file() and f.suffix.lower() == ".txt"]
            txt_files = sorted(raw_files, key=natural_sort_key)
            if not txt_files:
                continue

            lectures = []
            for l_idx, f in enumerate(txt_files, 1):
                name = f.stem
                m = re.match(r"^(\d+)\s*-\s*(.+)$", name)
                if m:
                    num = m.group(1).zfill(3)
                    title = m.group(2).strip()
                else:
                    num = f"{l_idx:03d}"
                    title = name.strip()

                text = safe_read_file(f).strip()
                words = len(text.split())
                key_pts = extract_key_points(text, max_points=3)
                uid = f"s{s_idx:02d}_l{num}"

                lectures.append({
                    "id": uid,
                    "num": num,
                    "title": title,
                    "text": text,
                    "word_count": words,
                    "key_points": key_pts
                })

            if lectures:
                sections_data.append({
                    "id": s_idx,
                    "title": s_dir.name,
                    "lectures": lectures
                })

    else:
        # Modo plano (todos los txt en la raíz del curso)
        raw_files = [f for f in course_path.iterdir() if f.is_file() and f.suffix.lower() == ".txt" and f.name.lower() != "requirements.txt"]
        txt_files = sorted(raw_files, key=natural_sort_key)
        lectures = []
        for l_idx, f in enumerate(txt_files, 1):
            name = f.stem
            m = re.match(r"^(\d+)\s*-\s*(.+)$", name)
            num = m.group(1).zfill(3) if m else f"{l_idx:03d}"
            title = m.group(2).strip() if m else name.strip()
            text = safe_read_file(f).strip()
            words = len(text.split())
            uid = f"s01_l{num}"

            lectures.append({
                "id": uid,
                "num": num,
                "title": title,
                "text": text,
                "word_count": words,
                "key_points": extract_key_points(text, max_points=3)
            })

        if lectures:
            sections_data.append({
                "id": 1,
                "title": "01 - Contenido General",
                "lectures": lectures
            })

    if not sections_data:
        print("  [!] No se encontraron archivos de transcripción .txt válidos en la carpeta.")
        return False

    total_lectures = sum(len(s["lectures"]) for s in sections_data)
    print(f"  [+] Se encontraron {len(sections_data)} secciones y {total_lectures} lecciones estructuradas correctamente.")

    # 1. Generar HTML Interactivo (index.html + course_data.js)
    html_file = generate_interactive_html(course_title, sections_data, course_path)
    print(f"  ✔ [HTML Interactivo] Creado: {html_file}")

    # 2. Generar Markdown enriquecido (FULL_COURSE.md)
    md_file = generate_course_markdown(course_title, sections_data, course_path)
    print(f"  ✔ [Markdown Completo] Creado: {md_file}")

    print(f"  🎉 ¡Conversión completada con éxito para '{course_title}'!\n")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
        convert_local_course_directory(target_dir)
    else:
        print("Uso: python converter.py <ruta_a_la_carpeta_del_curso>")
