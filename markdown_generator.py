"""
markdown_generator.py — Generador de Markdown enriquecido para cursos de Udemy.
Crea un archivo completo 'FULL_COURSE.md' con Tabla de Contenidos interactiva (TOC),
secciones estructuradas y formato optimizado para Obsidian, Notion, VS Code y GitHub.
"""

import re
from pathlib import Path


def slugify_anchor(text):
    """Genera un ancla compatible con GitHub, Obsidian y CommonMark."""
    text = re.sub(r'[^a-zA-Z0-9_\-]+', '-', str(text).strip())
    return text.strip('-').lower()


def generate_course_markdown(course_title, sections_data, output_dir):
    """
    Genera 'FULL_COURSE.md' en output_dir con TOC navegable y todas las lecciones.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    total_lectures = sum(len(sec.get("lectures", [])) for sec in sections_data)
    total_words = sum(
        sum(lec.get("word_count", 0) for lec in sec.get("lectures", []))
        for sec in sections_data
    )
    total_hours = round(total_words / 130 / 60, 1)

    md_lines = []
    md_lines.append(f"# 🎓 {course_title}\n")
    md_lines.append(f"> **Resumen del Curso:** {len(sections_data)} secciones | {total_lectures} lecciones | {total_words:,} palabras (~{total_hours} horas de lectura)\n")
    md_lines.append("---\n")

    # Tabla de Contenidos (TOC)
    md_lines.append("## 📑 Tabla de Contenidos\n")
    for sec in sections_data:
        sec_title = sec.get("title", "")
        sec_anchor = slugify_anchor(sec_title)
        md_lines.append(f"- **[{sec_title}](#{sec_anchor})**")
        for lec in sec.get("lectures", []):
            num = lec.get("num", "")
            title = lec.get("title", "")
            words = lec.get("word_count", 0)
            mins = max(1, round(words / 130)) if words > 0 else 0
            lec_anchor = slugify_anchor(f"leccion-{num}-{title}")
            md_lines.append(f"  - [{num} - {title}](#{lec_anchor}) `(~{mins} min)`")
    md_lines.append("\n---\n")

    # Cuerpo del Curso
    for sec in sections_data:
        sec_title = sec.get("title", "")
        sec_anchor = slugify_anchor(sec_title)
        md_lines.append(f'<a id="{sec_anchor}"></a>')
        md_lines.append(f"\n## 📂 {sec_title}\n")
        md_lines.append("---\n")

        for lec in sec.get("lectures", []):
            num = lec.get("num", "")
            title = lec.get("title", "")
            words = lec.get("word_count", 0)
            mins = max(1, round(words / 130)) if words > 0 else 0
            lec_anchor = slugify_anchor(f"leccion-{num}-{title}")

            md_lines.append(f'<a id="{lec_anchor}"></a>')
            md_lines.append(f"### [{num}] {title}\n")
            md_lines.append(f"⏱️ **Tiempo estimado:** ~{mins} min | 📖 **Palabras:** {words}\n")

            # Ideas Clave si existen
            key_points = lec.get("key_points", [])
            if key_points:
                md_lines.append("> 💡 **Puntos Clave & Ideas Principales:**")
                for kp in key_points:
                    clean_kp = kp.replace("\n", " ").strip()
                    md_lines.append(f"> - {clean_kp}")
                md_lines.append("")

            # Texto
            text = lec.get("text", "")
            if text:
                md_lines.append(text.strip() + "\n")
            else:
                md_lines.append("*(Sin transcripción de texto para esta lección)*\n")

            md_lines.append("\n[🔼 Volver al índice](#-tabla-de-contenidos)\n")
            md_lines.append("---\n")

    md_file = output_path / "FULL_COURSE.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return md_file
