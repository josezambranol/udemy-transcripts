"""
html_generator.py — Generador de Dashboard de Estudio HTML Interactivo Pro para cursos de Udemy.
Convierte transcripciones de cursos en una aplicación web interactiva autónoma, moderna y visual
(sin servidores, funciona 100% offline mediante file://).

Características:
- Transcripción estructurada en Bloques Didácticos con explicaciones pedagógicas.
- Puntos de Mejora y Buenas Prácticas intercalados en el texto.
- Imágenes e ilustraciones reales (Wikimedia Commons) y diagramas SVG embebidos en el flujo de lectura.
- Navegación fluida al pie de la lección (sin barra inferior flotante molesta).
- Motor de Investigación Autónoma en Fuentes Web (Wikipedia REST, DuckDuckGo, MDN, Git SCM) sin APIs de IA.
- Cajas de código con detección de sintaxis y copiado en 1 clic.
- Tarjetas interactivas de autoevaluación (Repaso Activo).
- Lector de voz offline integrado (Web Speech API).
- Modo Enfoque Zen (F).
- Cuaderno de notas por lección y exportación a Markdown.
- Seguridad anti-XSS (`escapeHtml`).
"""

import json
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    from knowledge_engine import enrich_course_with_knowledge
except ImportError:
    def enrich_course_with_knowledge(course_title, sections_data):
        return {"topics": [], "cards": [], "official_docs": [], "visuals": []}


def extract_key_points(text, max_points=4):
    """
    Extrae ideas clave y oraciones significativas de la transcripción para reforzar el estudio.
    """
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    candidates = []
    for s in sentences:
        s_clean = s.strip()
        if 40 <= len(s_clean) <= 180 and not s_clean.lower().startswith((
            "hola", "bueno", "bienvenidos", "en este video", "adiós", "suscríbete",
            "en la próxima lección", "vamos a empezar", "así que", "ok"
        )):
            candidates.append(s_clean)
        if len(candidates) >= max_points:
            break
    if not candidates and sentences:
        candidates = [s.strip() for s in sentences[:max_points] if len(s.strip()) > 25]
    return candidates


def generate_interactive_html(course_title, sections_data, output_dir):
    """
    Genera 'index.html' y 'course_data.js' en la carpeta del curso con enriquecimiento web y diseño premium.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Asegurar IDs únicos para cada lección
    for s_idx, sec in enumerate(sections_data, 1):
        for l_idx, lec in enumerate(sec.get("lectures", []), 1):
            if "id" not in lec:
                lec["id"] = f"s{s_idx:02d}_l{lec.get('num', f'{l_idx:03d}')}"

    total_lectures = sum(len(sec.get("lectures", [])) for sec in sections_data)
    total_words = sum(
        sum(lec.get("word_count", 0) for lec in sec.get("lectures", []))
        for sec in sections_data
    )

    external_knowledge = {"topics": [], "cards": [], "official_docs": [], "visuals": []}
    try:
        external_knowledge = enrich_course_with_knowledge(course_title, sections_data)
    except Exception as e:
        print(f"  [i] Nota: Modo sin conexión o no se pudo consultar fuentes web: {e}")

    course_data = {
        "title": course_title,
        "total_lectures": total_lectures,
        "total_sections": len(sections_data),
        "total_words": total_words,
        "external_knowledge": external_knowledge,
        "sections": sections_data
    }

    # Guardar course_data.js
    data_file = output_path / "course_data.js"
    with open(data_file, "w", encoding="utf-8") as f:
        f.write("const COURSE_DATA = " + json.dumps(course_data, ensure_ascii=False, indent=2) + ";\n")

    # Generar index.html
    html_content = f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{course_title} — Centro de Estudio Interactivo Pro</title>
  <style>
    :root {{
      --bg: #090e17;
      --bg-card: #121927;
      --bg-card-hover: #1b2438;
      --bg-sidebar: #060a12;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(56, 189, 248, 0.4);
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.18);
      --success: #10b981;
      --success-glow: rgba(16, 185, 129, 0.18);
      --warning: #f59e0b;
      --purple: #a855f7;
      --code-bg: #080c14;
      --radius: 12px;
      --font-size: 16px;
      --content-max-width: 840px;
    }}

    [data-theme="light"] {{
      --bg: #f8fafc;
      --bg-card: #ffffff;
      --bg-card-hover: #f1f5f9;
      --bg-sidebar: #f8fafc;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: rgba(0, 0, 0, 0.08);
      --border-focus: rgba(2, 132, 199, 0.4);
      --accent: #0284c7;
      --accent-glow: rgba(2, 132, 199, 0.12);
      --success: #059669;
      --success-glow: rgba(5, 150, 105, 0.12);
      --warning: #d97706;
      --purple: #7c3aed;
      --code-bg: #1e293b;
    }}

    [data-theme="sepia"] {{
      --bg: #fbf7ee;
      --bg-card: #f4ecd8;
      --bg-card-hover: #ebe1c5;
      --bg-sidebar: #efe7cf;
      --text: #433422;
      --text-muted: #7d6b53;
      --border: rgba(67, 52, 34, 0.12);
      --border-focus: rgba(154, 107, 50, 0.4);
      --accent: #9a6b32;
      --accent-glow: rgba(154, 107, 50, 0.15);
      --success: #2e7d32;
      --success-glow: rgba(46, 125, 50, 0.15);
      --warning: #b78103;
      --purple: #6d4c41;
      --code-bg: #2d2419;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      display: flex;
      height: 100vh;
      overflow: hidden;
      font-size: var(--font-size);
      -webkit-font-smoothing: antialiased;
    }}

    /* SIDEBAR */
    #sidebar {{
      width: 350px;
      min-width: 310px;
      max-width: 420px;
      background-color: var(--bg-sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      height: 100%;
      z-index: 20;
    }}

    .sidebar-header {{
      padding: 16px 18px 14px 18px;
      border-bottom: 1px solid var(--border);
    }}

    .course-badge-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}

    .course-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--accent-glow);
      color: var(--accent);
    }}

    .course-title {{
      font-size: 15px;
      font-weight: 700;
      line-height: 1.35;
      color: var(--text);
      margin-bottom: 12px;
      max-height: 42px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }}

    .progress-box {{
      background-color: var(--bg-card);
      border: 1px solid var(--border);
      padding: 8px 12px;
      border-radius: 8px;
    }}

    .progress-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 5px;
    }}

    .progress-bar-bg {{
      width: 100%;
      height: 6px;
      background-color: var(--border);
      border-radius: 3px;
      overflow: hidden;
    }}

    .progress-bar-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent), var(--success));
      border-radius: 3px;
      transition: width 0.3s ease;
    }}

    .search-container {{
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 6px;
    }}

    .search-input-wrap {{
      position: relative;
      flex: 1;
    }}

    .search-input {{
      width: 100%;
      padding: 8px 12px 8px 30px;
      border-radius: 7px;
      border: 1px solid var(--border);
      background-color: var(--bg-card);
      color: var(--text);
      font-size: 12.5px;
      outline: none;
    }}

    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }}

    .search-icon {{
      position: absolute;
      left: 10px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 12px;
      color: var(--text-muted);
      pointer-events: none;
    }}

    .filter-btn {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-muted);
      border-radius: 7px;
      padding: 0 9px;
      font-size: 11.5px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    .filter-btn.active {{
      background: var(--accent-glow);
      color: var(--accent);
      border-color: var(--accent);
    }}

    .curriculum-list {{
      flex: 1;
      overflow-y: auto;
      padding: 8px 10px;
    }}

    .section-group {{
      margin-bottom: 10px;
    }}

    .section-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 9px;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      cursor: pointer;
      border-radius: 6px;
      user-select: none;
    }}

    .section-header:hover {{
      background-color: var(--bg-card);
      color: var(--text);
    }}

    .section-title-text {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      padding-right: 6px;
    }}

    .lecture-item {{
      display: flex;
      align-items: center;
      padding: 7px 9px;
      margin: 2px 0;
      border-radius: 7px;
      cursor: pointer;
      font-size: 12.5px;
      gap: 8px;
      color: var(--text-muted);
      border: 1px solid transparent;
      position: relative;
    }}

    .lecture-item:hover {{
      background-color: var(--bg-card);
      color: var(--text);
    }}

    .lecture-item.active {{
      background: linear-gradient(90deg, var(--accent-glow), rgba(56, 189, 248, 0.05));
      color: var(--accent);
      font-weight: 600;
      border-color: rgba(56, 189, 248, 0.3);
    }}

    .lecture-item.active::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 6px;
      bottom: 6px;
      width: 3px;
      background: var(--accent);
      border-radius: 0 2px 2px 0;
    }}

    .lecture-item.completed .lecture-title-sub {{
      text-decoration: line-through;
      opacity: 0.55;
    }}

    .checkbox-round {{
      width: 16px;
      height: 16px;
      min-width: 16px;
      border-radius: 50%;
      border: 1.5px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .checkbox-round.checked {{
      background-color: var(--success);
      border-color: var(--success);
      color: white;
    }}

    .checkbox-round.checked::after {{
      content: "✔";
      font-size: 9px;
      font-weight: bold;
    }}

    .lecture-title-sub {{
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .badge-starred {{
      color: #eab308;
      font-size: 11px;
    }}

    /* MAIN VIEW */
    #main-content {{
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
      background-color: var(--bg);
      position: relative;
    }}

    .top-bar {{
      height: 52px;
      padding: 0 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background-color: var(--bg);
      z-index: 10;
    }}

    .top-bar-left {{
      display: flex;
      align-items: center;
      gap: 10px;
      overflow: hidden;
    }}

    .btn-toggle-sidebar {{
      background: none;
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 14px;
      padding: 5px 9px;
      border-radius: 6px;
      cursor: pointer;
    }}

    .top-steppers {{
      display: inline-flex;
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
    }}

    .btn-step {{
      background: var(--bg-card);
      border: none;
      color: var(--text-muted);
      padding: 5px 9px;
      cursor: pointer;
      font-size: 12px;
    }}

    .btn-step:hover:not(:disabled) {{
      background-color: var(--bg-card-hover);
      color: var(--text);
    }}

    .btn-step:disabled {{
      opacity: 0.3;
      cursor: not-allowed;
    }}

    .top-lecture-indicator {{
      font-size: 12.5px;
      color: var(--text-muted);
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .top-bar-right {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .btn-ctrl {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 12px;
      padding: 5px 9px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      font-weight: 500;
    }}

    .btn-ctrl:hover {{
      background-color: var(--bg-card-hover);
      border-color: var(--accent);
    }}

    .btn-ctrl.active {{
      background-color: var(--accent-glow);
      border-color: var(--accent);
      color: var(--accent);
    }}

    .btn-pill-done {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-muted);
      border-radius: 20px;
      padding: 4px 11px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}

    .btn-pill-done.is-done {{
      background: var(--success);
      color: white;
      border-color: var(--success);
    }}

    /* AUDIO TTS BAR */
    .audio-player-bar {{
      background: var(--bg-card);
      border-bottom: 1px solid var(--border);
      padding: 7px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      display: none;
    }}

    .audio-player-bar.active {{
      display: flex;
    }}

    .audio-controls {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .audio-speed-select {{
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 5px;
      padding: 2px 6px;
      font-size: 11px;
    }}

    /* READING AREA */
    .reading-scroll-area {{
      flex: 1;
      overflow-y: auto;
      padding: 32px 24px 60px 24px;
      display: flex;
      justify-content: center;
    }}

    .lecture-view-container {{
      width: 100%;
      max-width: var(--content-max-width);
    }}

    /* ZEN MODE */
    body.zen-mode #sidebar {{
      display: none !important;
    }}
    body.zen-mode .top-bar {{
      opacity: 0.75;
    }}
    body.zen-mode .reading-scroll-area {{
      padding-top: 45px;
    }}

    .lecture-meta-header {{
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }}

    .lecture-breadcrumbs {{
      font-size: 12px;
      color: var(--accent);
      font-weight: 600;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }}

    .lecture-main-title {{
      font-size: 27px;
      font-weight: 800;
      color: var(--text);
      line-height: 1.25;
      margin-bottom: 10px;
    }}

    .lecture-stats-badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      font-size: 11.5px;
      color: var(--text-muted);
    }}

    .stat-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background-color: var(--bg-card);
      padding: 3px 8px;
      border-radius: 5px;
      border: 1px solid var(--border);
    }}

    /* ========================================================================
       BLOQUES DE ESTUDIO DIDÁCTICOS, PUNTOS DE MEJORA E IMÁGENES INTERCALADAS
       ======================================================================== */
    .study-block {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 22px 24px;
      margin-bottom: 24px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }}

    .study-block-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--border);
    }}

    .study-block-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--accent);
    }}

    .study-block-body p {{
      font-size: inherit;
      line-height: 1.85;
      margin-bottom: 16px;
      color: var(--text);
    }}

    .study-block-body p:last-child {{
      margin-bottom: 0;
    }}

    /* CALLOUT DE PUNTOS DE MEJORA Y BUENAS PRÁCTICAS */
    .pro-improvement-card {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(6, 10, 18, 0.5));
      border: 1px solid rgba(16, 185, 129, 0.35);
      border-left: 4px solid var(--success);
      border-radius: 8px;
      padding: 14px 18px;
      margin: 18px 0;
      font-size: 13.5px;
      line-height: 1.6;
    }}

    .pro-improvement-header {{
      font-weight: 700;
      color: var(--success);
      margin-bottom: 5px;
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12.5px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    /* DESGLOSE DIDÁCTICO DEL BLOQUE */
    .block-breakdown-card {{
      background: rgba(56, 189, 248, 0.05);
      border: 1px solid rgba(56, 189, 248, 0.22);
      border-radius: 8px;
      padding: 14px 18px;
      margin: 18px 0 10px 0;
    }}

    .block-breakdown-title {{
      font-size: 12.5px;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .block-breakdown-list {{
      padding-left: 18px;
      font-size: 13px;
      line-height: 1.6;
      color: var(--text);
    }}

    .block-breakdown-list li {{
      margin-bottom: 5px;
    }}

    /* TARJETA DE IMAGEN ILUSTRADA INTERCALADA */
    .inline-illustrated-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      margin: 24px 0;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }}

    .inline-illustrated-img-wrapper {{
      min-height: 180px;
      max-height: 340px;
      background: #05080f;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      cursor: pointer;
    }}

    .inline-illustrated-img {{
      max-width: 100%;
      max-height: 340px;
      object-fit: contain;
      transition: transform 0.3s ease;
    }}

    .inline-illustrated-img:hover {{
      transform: scale(1.02);
    }}

    .inline-illustrated-footer {{
      padding: 12px 18px;
      background: rgba(255, 255, 255, 0.02);
      border-top: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .inline-illustrated-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text);
    }}

    .inline-illustrated-caption {{
      font-size: 11.5px;
      color: var(--text-muted);
      line-height: 1.4;
    }}

    /* DIAGRAMAS SVG */
    .visual-diagram-card {{
      background: linear-gradient(145deg, rgba(18, 25, 39, 0.8), rgba(11, 17, 28, 0.95));
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px 22px;
      margin: 24px 0;
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }}

    .diagram-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }}

    .diagram-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--accent);
      display: flex;
      align-items: center;
      gap: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .diagram-body {{
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 8px 0;
      overflow-x: auto;
    }}

    .diagram-svg {{
      max-width: 100%;
      height: auto;
    }}

    .diagram-caption {{
      font-size: 11.5px;
      color: var(--text-muted);
      text-align: center;
      margin-top: 8px;
    }}

    /* TABS */
    .study-tabs {{
      display: flex;
      gap: 6px;
      margin-bottom: 22px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
      overflow-x: auto;
    }}

    .tab-btn {{
      background: none;
      border: none;
      padding: 7px 13px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}

    .tab-btn:hover {{
      color: var(--text);
      background: var(--bg-card);
    }}

    .tab-btn.active {{
      background-color: var(--accent-glow);
      color: var(--accent);
    }}

    .tab-panel {{
      display: none;
    }}

    .tab-panel.active {{
      display: block;
    }}

    /* CODE BLOCKS */
    .code-block-card {{
      background-color: var(--code-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin: 14px 0;
      overflow: hidden;
    }}

    .code-header {{
      background: rgba(255,255,255,0.03);
      padding: 6px 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      font-family: monospace;
    }}

    .btn-copy-code {{
      background: none;
      border: 1px solid var(--border);
      color: var(--text-muted);
      border-radius: 4px;
      padding: 2px 7px;
      font-size: 10.5px;
      cursor: pointer;
    }}

    .btn-copy-code:hover {{
      color: var(--text);
      border-color: var(--accent);
    }}

    .code-content {{
      padding: 10px 14px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
      line-height: 1.55;
      color: #38bdf8;
      overflow-x: auto;
      white-space: pre-wrap;
    }}

    /* TAB: FUENTES WEB */
    .web-knowledge-section {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .web-search-box {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
    }}

    .web-search-title {{
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .web-search-desc {{
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }}

    .web-search-bar {{
      display: flex;
      gap: 8px;
    }}

    .web-search-input {{
      flex: 1;
      padding: 9px 12px;
      border-radius: 7px;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
      font-size: 13px;
      outline: none;
    }}

    .web-search-input:focus {{
      border-color: var(--accent);
    }}

    .btn-web-search {{
      background: var(--accent);
      color: #0b1120;
      border: none;
      font-weight: 700;
      padding: 0 16px;
      border-radius: 7px;
      cursor: pointer;
      font-size: 12.5px;
    }}

    .suggested-tags-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
      align-items: center;
    }}

    .tag-pill {{
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 2px 9px;
      font-size: 11px;
      color: var(--text-muted);
      cursor: pointer;
    }}

    .tag-pill:hover {{
      background: var(--accent-glow);
      color: var(--accent);
      border-color: var(--accent);
    }}

    .web-result-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      display: flex;
      gap: 16px;
      margin-top: 12px;
    }}

    .web-result-img {{
      width: 140px;
      height: 120px;
      object-fit: cover;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--bg);
      cursor: pointer;
    }}

    .web-result-content {{
      flex: 1;
    }}

    .web-result-title {{
      font-size: 16px;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 6px;
    }}

    .web-result-extract {{
      font-size: 13px;
      line-height: 1.6;
      color: var(--text);
      margin-bottom: 10px;
    }}

    .web-result-link {{
      font-size: 12px;
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .docs-links-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
      margin-top: 8px;
    }}

    .doc-link-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
      text-decoration: none;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .doc-link-card:hover {{
      border-color: var(--accent);
      background: var(--bg-card-hover);
    }}

    /* FLASHCARDS */
    .flashcards-container {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}

    .flashcard {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      cursor: pointer;
    }}

    .flashcard:hover {{
      border-color: var(--accent);
    }}

    .flashcard-q {{
      font-weight: 700;
      font-size: 13px;
      margin-bottom: 8px;
    }}

    .flashcard-hint {{
      font-size: 11px;
      color: var(--text-muted);
    }}

    .flashcard-a {{
      font-size: 12.5px;
      color: var(--accent);
      line-height: 1.5;
      display: none;
      padding-top: 8px;
      margin-top: 8px;
      border-top: 1px dashed var(--border);
    }}

    .flashcard.revealed .flashcard-a {{
      display: block;
    }}

    /* IDEAS CLAVE */
    .key-points-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 22px;
    }}

    .key-points-title {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .key-points-list {{
      padding-left: 18px;
      font-size: 13.5px;
      line-height: 1.65;
    }}

    .key-points-list li {{
      margin-bottom: 6px;
    }}

    /* NOTAS */
    .notes-box {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
    }}

    .notes-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}

    .notes-textarea {{
      width: 100%;
      min-height: 240px;
      background-color: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
      color: var(--text);
      font-family: inherit;
      font-size: 13.5px;
      line-height: 1.6;
      resize: vertical;
      outline: none;
    }}

    .notes-textarea:focus {{
      border-color: var(--accent);
    }}

    .notes-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      font-size: 11.5px;
      color: var(--text-muted);
    }}

    /* PIE DE LECCIÓN FLUIDO */
    .lesson-footer-nav {{
      margin-top: 48px;
      padding-top: 24px;
      border-top: 1px solid var(--border);
    }}

    .lesson-done-banner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 14px 18px;
      margin-bottom: 18px;
    }}

    .btn-finish-lesson {{
      background: var(--bg);
      border: 1.5px solid var(--border);
      color: var(--text);
      font-weight: 600;
      font-size: 13px;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 7px;
    }}

    .btn-finish-lesson:hover {{
      border-color: var(--success);
      color: var(--success);
    }}

    .btn-finish-lesson.done {{
      background: var(--success);
      border-color: var(--success);
      color: white;
    }}

    .nav-cards-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}

    .nav-step-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 14px 16px;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 4px;
      text-decoration: none;
      color: inherit;
    }}

    .nav-step-card:hover:not(.disabled) {{
      border-color: var(--accent);
      background: var(--bg-card-hover);
    }}

    .nav-step-card.disabled {{
      opacity: 0.35;
      cursor: not-allowed;
    }}

    .nav-step-card.next {{
      text-align: right;
      align-items: flex-end;
    }}

    .nav-card-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--text-muted);
      font-weight: 700;
    }}

    .nav-card-title {{
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }}

    @media (max-width: 650px) {{
      .nav-cards-grid {{
        grid-template-columns: 1fr;
      }}
      .web-result-card {{
        flex-direction: column;
      }}
      .web-result-img {{
        width: 100%;
        height: 160px;
      }}
    }}

    @media print {{
      #sidebar, .top-bar, .lesson-footer-nav, .study-tabs, .notes-box, .audio-player-bar, .visual-diagram-card, .web-knowledge-section {{
        display: none !important;
      }}
      body, #main-content, .reading-scroll-area {{
        height: auto !important;
        overflow: visible !important;
        background: white !important;
        color: black !important;
      }}
      .lecture-view-container {{
        max-width: 100% !important;
      }}
    }}
  </style>
</head>
<body>

  <!-- SIDEBAR -->
  <aside id="sidebar">
    <div class="sidebar-header">
      <div class="course-badge-row">
        <span class="course-badge">🎓 Curso Udemy</span>
        <button class="filter-btn" id="btn-filter-starred" title="Filtrar lecciones guardadas">⭐ Favoritas</button>
      </div>
      <h1 class="course-title" id="side-course-title">Cargando curso...</h1>
      <div class="progress-box">
        <div class="progress-labels">
          <span>Progreso de Estudio</span>
          <span id="progress-percent">0%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" id="progress-fill"></div>
        </div>
      </div>
    </div>

    <div class="search-container">
      <div class="search-input-wrap">
        <span class="search-icon">🔍</span>
        <input type="text" id="search-input" class="search-input" placeholder="Buscar lección o tema...">
      </div>
    </div>

    <div class="curriculum-list" id="curriculum-list"></div>
  </aside>

  <!-- MAIN VIEW -->
  <main id="main-content">
    <header class="top-bar">
      <div class="top-bar-left">
        <button class="btn-toggle-sidebar" id="btn-toggle-sidebar" title="Ocultar/Mostrar barra lateral">☰</button>
        <div class="top-steppers">
          <button class="btn-step" id="btn-step-prev" title="Lección Anterior">‹</button>
          <button class="btn-step" id="btn-step-next" title="Siguiente Lección">›</button>
        </div>
        <span class="top-lecture-indicator" id="top-lecture-indicator"></span>
      </div>

      <div class="top-bar-right">
        <button class="btn-pill-done" id="btn-top-done" title="Marcar como completada">
          <span>✔</span> <span>Completada</span>
        </button>
        <button class="btn-ctrl" id="btn-star-lecture" title="Guardar lección">⭐</button>
        <button class="btn-ctrl" id="btn-tts-toggle" title="Lector de voz offline">🎧 Audio</button>
        <button class="btn-ctrl" id="btn-zen-mode" title="Modo Enfoque / Zen (F)">🧘</button>
        <button class="btn-ctrl" id="btn-theme-toggle" title="Cambiar tema">🌓</button>
        <button class="btn-ctrl" id="btn-copy-text" title="Copiar texto">📋</button>
      </div>
    </header>

    <!-- BARRA REPRODUCTOR TTS -->
    <div class="audio-player-bar" id="audio-player-bar">
      <div class="audio-controls">
        <button class="btn-ctrl" id="btn-tts-play">▶️ Leer</button>
        <button class="btn-ctrl" id="btn-tts-pause">⏸️ Pausa</button>
        <button class="btn-ctrl" id="btn-tts-stop">⏹️ Stop</button>
        <label style="margin-left: 6px;">Velocidad:</label>
        <select class="audio-speed-select" id="audio-speed">
          <option value="0.85">0.85x</option>
          <option value="1.0" selected>1.0x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
        </select>
      </div>
      <span id="audio-status" style="color: var(--text-muted);">Listo para leer transcripción</span>
    </div>

    <!-- ÁREA DE LECTURA -->
    <div class="reading-scroll-area" id="scroll-area">
      <article class="lecture-view-container" id="lecture-container">
        <!-- Render dinámico aquí -->
      </article>
    </div>
  </main>

  <!-- DATOS DEL CURSO -->
  <script src="course_data.js"></script>

  <script>
    (function() {{
      if (typeof COURSE_DATA === "undefined") {{
        document.body.innerHTML = "<h2 style='padding:40px;text-align:center;'>Error: No se encontró 'course_data.js'. Asegúrate de ejecutar este archivo junto con los datos generados.</h2>";
        return;
      }}

      // Sanitización XSS
      function escapeHtml(str) {{
        if (str === null || str === undefined) return "";
        return String(str)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
      }}

      // Estado
      let flatLectures = [];
      let currentLectureIndex = 0;
      let filterStarredOnly = false;
      const STORAGE_KEY_PREFIX = "udemy_study_" + COURSE_DATA.title.replace(/[^a-zA-Z0-9]/g, "_");

      function getCompletedSet() {{
        try {{
          const raw = localStorage.getItem(STORAGE_KEY_PREFIX + "_completed_uids");
          return new Set(raw ? JSON.parse(raw) : []);
        }} catch(e) {{
          return new Set();
        }}
      }}

      function saveCompletedSet(set) {{
        localStorage.setItem(STORAGE_KEY_PREFIX + "_completed_uids", JSON.stringify(Array.from(set)));
      }}

      function getStarredSet() {{
        try {{
          const raw = localStorage.getItem(STORAGE_KEY_PREFIX + "_starred");
          return new Set(raw ? JSON.parse(raw) : []);
        }} catch(e) {{
          return new Set();
        }}
      }}

      function saveStarredSet(set) {{
        localStorage.setItem(STORAGE_KEY_PREFIX + "_starred", JSON.stringify(Array.from(set)));
      }}

      // Aplanar lecciones
      COURSE_DATA.sections.forEach((sec, sIdx) => {{
        sec.lectures.forEach((lec, lIdx) => {{
          const uid = lec.id || (`s${{sIdx + 1}}_l${{lec.num || lIdx}}`);
          flatLectures.push({{
            ...lec,
            uid: uid,
            sectionTitle: sec.title,
            sectionIndex: sIdx,
            globalIndex: flatLectures.length
          }});
        }});
      }});

      // Elementos DOM
      const sideCourseTitle = document.getElementById("side-course-title");
      const progressPercent = document.getElementById("progress-percent");
      const progressFill = document.getElementById("progress-fill");
      const curriculumList = document.getElementById("curriculum-list");
      const lectureContainer = document.getElementById("lecture-container");
      const searchInput = document.getElementById("search-input");
      const topIndicator = document.getElementById("top-lecture-indicator");
      const sidebar = document.getElementById("sidebar");
      const btnStar = document.getElementById("btn-star-lecture");
      const btnTopDone = document.getElementById("btn-top-done");
      const btnStepPrev = document.getElementById("btn-step-prev");
      const btnStepNext = document.getElementById("btn-step-next");
      const btnFilterStarred = document.getElementById("btn-filter-starred");

      sideCourseTitle.textContent = COURSE_DATA.title;

      function updateProgress() {{
        const completed = getCompletedSet();
        const total = flatLectures.length;
        const count = flatLectures.filter(fl => completed.has(fl.uid)).length;
        const pct = total > 0 ? Math.round((count / total) * 100) : 0;
        progressPercent.textContent = `${{pct}}% (${{count}}/${{total}})`;
        progressFill.style.width = `${{pct}}%`;
      }}

      // ========================================================================
      // DIAGRAMAS SVG REDISEÑADOS
      // ========================================================================
      function generateContextualDiagram(lec) {{
        const txt = (lec.text + " " + lec.title).toLowerCase();

        // 1. Git Workflow
        if (txt.includes("git") || txt.includes("commit") || txt.includes("branch") || txt.includes("repositor") || txt.includes("merge")) {{
          return `
            <div class="visual-diagram-card">
              <div class="diagram-header">
                <span class="diagram-title">📊 Esquema Conceptual: Flujo y Zonas de Git</span>
                <span class="stat-badge">Arquitectura</span>
              </div>
              <div class="diagram-body">
                <svg class="diagram-svg" viewBox="0 0 780 150" width="100%" height="140" xmlns="http://www.w3.org/2000/svg">
                  <!-- Nodo 1 -->
                  <rect x="15" y="20" width="160" height="95" rx="10" fill="#151f32" stroke="#38bdf8" stroke-width="1.8"/>
                  <text x="95" y="52" fill="#f8fafc" font-size="13" font-weight="700" text-anchor="middle">Working Tree</text>
                  <text x="95" y="74" fill="#94a3b8" font-size="11" text-anchor="middle">Archivos en Disco</text>
                  <rect x="42" y="86" width="106" height="18" rx="4" fill="rgba(56, 189, 248, 0.15)"/>
                  <text x="95" y="99" fill="#38bdf8" font-size="10" font-weight="600" text-anchor="middle">Modificados</text>

                  <path d="M 175 67 L 210 67" stroke="#38bdf8" stroke-width="2" stroke-dasharray="3,3"/>
                  <rect x="168" y="36" width="50" height="16" rx="4" fill="#060a12" stroke="#38bdf8" stroke-width="1"/>
                  <text x="193" y="48" fill="#38bdf8" font-size="9.5" font-weight="bold" text-anchor="middle">git add</text>

                  <!-- Nodo 2 -->
                  <rect x="210" y="20" width="160" height="95" rx="10" fill="#151f32" stroke="#f59e0b" stroke-width="1.8"/>
                  <text x="290" y="52" fill="#f8fafc" font-size="13" font-weight="700" text-anchor="middle">Staging Area</text>
                  <text x="290" y="74" fill="#94a3b8" font-size="11" text-anchor="middle">Índice Preparado</text>
                  <rect x="237" y="86" width="106" height="18" rx="4" fill="rgba(245, 158, 11, 0.15)"/>
                  <text x="290" y="99" fill="#f59e0b" font-size="10" font-weight="600" text-anchor="middle">Pre-commit</text>

                  <path d="M 370 67 L 405 67" stroke="#10b981" stroke-width="2" stroke-dasharray="3,3"/>
                  <rect x="363" y="36" width="50" height="16" rx="4" fill="#060a12" stroke="#10b981" stroke-width="1"/>
                  <text x="388" y="48" fill="#10b981" font-size="9.5" font-weight="bold" text-anchor="middle">commit</text>

                  <!-- Nodo 3 -->
                  <rect x="405" y="20" width="160" height="95" rx="10" fill="#151f32" stroke="#10b981" stroke-width="1.8"/>
                  <text x="485" y="52" fill="#f8fafc" font-size="13" font-weight="700" text-anchor="middle">Local Repo</text>
                  <text x="485" y="74" fill="#94a3b8" font-size="11" text-anchor="middle">Historial (.git HEAD)</text>
                  <rect x="432" y="86" width="106" height="18" rx="4" fill="rgba(16, 185, 129, 0.15)"/>
                  <text x="485" y="99" fill="#10b981" font-size="10" font-weight="600" text-anchor="middle">Instantánea</text>

                  <path d="M 565 67 L 600 67" stroke="#a855f7" stroke-width="2" stroke-dasharray="3,3"/>
                  <rect x="560" y="36" width="46" height="16" rx="4" fill="#060a12" stroke="#a855f7" stroke-width="1"/>
                  <text x="583" y="48" fill="#a855f7" font-size="9.5" font-weight="bold" text-anchor="middle">push</text>

                  <!-- Nodo 4 -->
                  <rect x="600" y="20" width="160" height="95" rx="10" fill="#151f32" stroke="#a855f7" stroke-width="1.8"/>
                  <text x="680" y="52" fill="#f8fafc" font-size="13" font-weight="700" text-anchor="middle">Remote Repo</text>
                  <text x="680" y="74" fill="#94a3b8" font-size="11" text-anchor="middle">GitHub / GitLab</text>
                  <rect x="627" y="86" width="106" height="18" rx="4" fill="rgba(168, 85, 247, 0.15)"/>
                  <text x="680" y="99" fill="#a855f7" font-size="10" font-weight="600" text-anchor="middle">Compartido</text>
                </svg>
              </div>
              <div class="diagram-caption">Ciclo de vida en Git: Los cambios viajan desde el directorio de trabajo hasta el repositorio remoto.</div>
            </div>
          `;
        }}

        // 2. Python / Algoritmos
        if (txt.includes("python") || txt.includes("función") || txt.includes("bucle") || txt.includes("lista") || txt.includes("variable")) {{
          return `
            <div class="visual-diagram-card">
              <div class="diagram-header">
                <span class="diagram-title">⚙️ Pipeline de Ejecución Lógica en Python</span>
                <span class="stat-badge">Mecánica</span>
              </div>
              <div class="diagram-body">
                <svg class="diagram-svg" viewBox="0 0 740 120" width="100%" height="110" xmlns="http://www.w3.org/2000/svg">
                  <rect x="15" y="20" width="155" height="80" rx="8" fill="#151f32" stroke="#38bdf8" stroke-width="1.8"/>
                  <text x="92" y="50" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">1. Datos / Entrada</text>
                  <text x="92" y="72" fill="#94a3b8" font-size="11" text-anchor="middle">Variables & Memoria</text>

                  <line x1="170" y1="60" x2="205" y2="60" stroke="#38bdf8" stroke-width="2"/>

                  <rect x="205" y="20" width="155" height="80" rx="8" fill="#151f32" stroke="#f59e0b" stroke-width="1.8"/>
                  <text x="282" y="50" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">2. Control de Flujo</text>
                  <text x="282" y="72" fill="#94a3b8" font-size="11" text-anchor="middle">if / else / bucles</text>

                  <line x1="360" y1="60" x2="395" y2="60" stroke="#f59e0b" stroke-width="2"/>

                  <rect x="395" y="20" width="155" height="80" rx="8" fill="#151f32" stroke="#10b981" stroke-width="1.8"/>
                  <text x="472" y="50" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">3. Métodos & Funciones</text>
                  <text x="472" y="72" fill="#94a3b8" font-size="11" text-anchor="middle">def() & Retorno</text>

                  <line x1="550" y1="60" x2="585" y2="60" stroke="#10b981" stroke-width="2"/>

                  <rect x="585" y="20" width="140" height="80" rx="8" fill="#151f32" stroke="#a855f7" stroke-width="1.8"/>
                  <text x="655" y="50" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">4. Objeto / Salida</text>
                  <text x="655" y="72" fill="#94a3b8" font-size="11" text-anchor="middle">Resultado Final</text>
                </svg>
              </div>
              <div class="diagram-caption">Pipeline computacional: Transformación secuencial de datos mediante estructuras lógicas y funciones.</div>
            </div>
          `;
        }}

        // 3. Web / Backend / SQL
        if (txt.includes("api") || txt.includes("http") || txt.includes("servidor") || txt.includes("cliente") || txt.includes("sql") || txt.includes("endpoint")) {{
          return `
            <div class="visual-diagram-card">
              <div class="diagram-header">
                <span class="diagram-title">🌐 Modelo Cliente - Servidor y Persistencia</span>
                <span class="stat-badge">Arquitectura Web</span>
              </div>
              <div class="diagram-body">
                <svg class="diagram-svg" viewBox="0 0 720 130" width="100%" height="120" xmlns="http://www.w3.org/2000/svg">
                  <rect x="20" y="20" width="175" height="85" rx="8" fill="#151f32" stroke="#38bdf8" stroke-width="1.8"/>
                  <text x="107" y="50" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Cliente / Frontend</text>
                  <text x="107" y="72" fill="#94a3b8" font-size="11" text-anchor="middle">Navegador o App</text>

                  <path d="M 195 48 L 270 48" stroke="#38bdf8" stroke-width="1.8"/>
                  <text x="232" y="42" fill="#38bdf8" font-size="9.5" text-anchor="middle">HTTP Request ➔</text>

                  <path d="M 270 78 L 195 78" stroke="#10b981" stroke-width="1.8"/>
                  <text x="232" y="92" fill="#10b981" font-size="9.5" text-anchor="middle">⬅ JSON Response</text>

                  <rect x="270" y="20" width="180" height="85" rx="8" fill="#151f32" stroke="#a855f7" stroke-width="1.8"/>
                  <text x="360" y="50" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Servidor Backend</text>
                  <text x="360" y="72" fill="#94a3b8" font-size="11" text-anchor="middle">Rutas & Controladores</text>

                  <path d="M 450 48 L 525 48" stroke="#f59e0b" stroke-width="1.8"/>
                  <text x="487" y="42" fill="#f59e0b" font-size="9.5" text-anchor="middle">SQL Query ➔</text>

                  <path d="M 525 78 L 450 78" stroke="#10b981" stroke-width="1.8"/>
                  <text x="487" y="92" fill="#10b981" font-size="9.5" text-anchor="middle">⬅ Dataset</text>

                  <rect x="525" y="20" width="175" height="85" rx="8" fill="#151f32" stroke="#f59e0b" stroke-width="1.8"/>
                  <text x="612" y="50" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Base de Datos</text>
                  <text x="612" y="72" fill="#94a3b8" font-size="11" text-anchor="middle">Tablas & Registros</text>
                </svg>
              </div>
              <div class="diagram-caption">Ciclo de vida de una petición HTTP y persistencia en base de datos relacional.</div>
            </div>
          `;
        }}

        // 4. Diagrama genérico
        return `
          <div class="visual-diagram-card">
            <div class="diagram-header">
              <span class="diagram-title">💡 Fases Metodológicas de la Lección</span>
              <span class="stat-badge">Pedagogía</span>
            </div>
            <div class="diagram-body">
              <svg class="diagram-svg" viewBox="0 0 680 100" width="100%" height="90" xmlns="http://www.w3.org/2000/svg">
                <rect x="15" y="15" width="180" height="65" rx="8" fill="#151f32" stroke="#38bdf8" stroke-width="1.8"/>
                <text x="105" y="43" fill="#f8fafc" font-size="12.5" font-weight="bold" text-anchor="middle">1. Fundamento Teórico</text>
                <text x="105" y="63" fill="#94a3b8" font-size="10.5" text-anchor="middle">Comprender el Por Qué</text>

                <line x1="195" y1="48" x2="250" y2="48" stroke="#38bdf8" stroke-width="2"/>

                <rect x="250" y="15" width="180" height="65" rx="8" fill="#151f32" stroke="#f59e0b" stroke-width="1.8"/>
                <text x="340" y="43" fill="#f8fafc" font-size="12.5" font-weight="bold" text-anchor="middle">2. Demostración Práctica</text>
                <text x="340" y="63" fill="#94a3b8" font-size="10.5" text-anchor="middle">Verlo Aplicado en Código</text>

                <line x1="430" y1="48" x2="485" y2="48" stroke="#f59e0b" stroke-width="2"/>

                <rect x="485" y="15" width="180" height="65" rx="8" fill="#151f32" stroke="#10b981" stroke-width="1.8"/>
                <text x="575" y="43" fill="#f8fafc" font-size="12.5" font-weight="bold" text-anchor="middle">3. Dominio & Retención</text>
                <text x="575" y="63" fill="#94a3b8" font-size="10.5" text-anchor="middle">Fijar en la Memoria</text>
              </svg>
            </div>
            <div class="diagram-caption">Fases del aprendizaje activo: Fundamento conceptual, experimentación y fijación mediante notas.</div>
          </div>
        `;
      }}

      // Detección de comandos
      function extractCodeSnippets(text) {{
        if (!text) return [];
        const lines = text.split("\\n");
        const snippets = [];
        const cmdPatterns = [
          /^(git\\s+[a-z0-9_-]+.*)/i,
          /^(python\\s+[a-z0-9_.-]+.*)/i,
          /^(npm\\s+[a-z0-9_-]+.*)/i,
          /^(pip\\s+install.*)/i,
          /^(docker\\s+[a-z0-9_-]+.*)/i,
          /^(SELECT\\s+.*\\s+FROM\\s+.*)/i,
          /^(def\\s+[a-zA-Z0-9_]+\\s*\\(.*\\):)/,
          /^(class\\s+[a-zA-Z0-9_]+.*:)/
        ];

        for (const line of lines) {{
          const clean = line.trim();
          for (const pat of cmdPatterns) {{
            if (pat.test(clean) && clean.length > 5 && clean.length < 150) {{
              if (!snippets.includes(clean)) snippets.push(clean);
              break;
            }}
          }}
          if (snippets.length >= 4) break;
        }}
        return snippets;
      }}

      // ========================================================================
      // MOTOR DE EXPLICACIÓN DE BLOQUES, PUNTOS DE MEJORA E IMÁGENES INTERCALADAS
      // ========================================================================
      function renderEnrichedTranscriptView(lec) {{
        const rawLines = (lec.text || "").split("\\n").map(l => l.trim()).filter(Boolean);
        if (rawLines.length === 0) {{
          return `<div class="study-block"><p><i>(Esta lección no contiene transcripción de texto disponible).</i></p></div>`;
        }}

        // Agrupar oraciones en párrafos de 3 líneas
        const paragraphs = [];
        for (let i = 0; i < rawLines.length; i += 3) {{
          paragraphs.push(rawLines.slice(i, i + 3).join(" "));
        }}

        // Agrupar párrafos en Bloques Didácticos de 3 párrafos (~150-200 palabras)
        const blocks = [];
        for (let i = 0; i < paragraphs.length; i += 3) {{
          blocks.push(paragraphs.slice(i, i + 3));
        }}

        // Colección de imágenes e ilustraciones de fuentes web
        const extKnowledge = COURSE_DATA.external_knowledge || {{}};
        const availableImages = [];
        (extKnowledge.visuals || []).forEach(v => {{
          if (v.url) availableImages.push({{ title: v.title, url: v.url, caption: v.caption }});
        }});
        (extKnowledge.cards || []).forEach(c => {{
          if (c.image) availableImages.push({{ title: c.title, url: c.image, caption: c.extract ? c.extract.slice(0, 110) + '...' : '' }});
        }});

        const blockTitles = [
          "Fundamento Conceptual & Contexto",
          "Mecánica Interna & Cómo Opera",
          "Demostración Práctica & Sintaxis",
          "Casos de Uso & Buenas Prácticas",
          "Puntos Críticos & Consolidación"
        ];

        // Consejos heurísticos de mejora según el tema
        const topicLower = (lec.title + " " + (lec.text || "")).toLowerCase();
        function getImprovementTip(bIdx) {{
          if (topicLower.includes("commit")) {{
            const tips = [
              "Buenas Prácticas de Commits: Haz commits atómicos enfocados en un único cambio lógico. Redacta el mensaje en presente imperativo (ej. 'Add user authentication').",
              "Optimización: Antes de confirmar con git commit, usa git status y git diff para inspeccionar exactamente qué archivos y líneas estás preparando."
            ];
            return tips[bIdx % tips.length];
          }}
          if (topicLower.includes("branch") || topicLower.includes("rama")) {{
            const tips = [
              "Estrategia de Ramas: Las ramas en Git son extremadamente ligeras (solo punteros de 41 bytes). Crea ramas nuevas sin miedo para cualquier experimento o feature.",
              "Convención de Nombres: Utiliza prefijos claros como feature/login, fix/header o docs/readme para mantener el repositorio ordenado en equipo."
            ];
            return tips[bIdx % tips.length];
          }}
          if (topicLower.includes("python") || topicLower.includes("función") || topicLower.includes("def")) {{
            const tips = [
              "Principio DRY (Don't Repeat Yourself): Si notas que copias y pegas lógica similar en más de dos lugares, extráela de inmediato a una función reutilizable.",
              "Eficiencia y Legibilidad: Utiliza nombres de variables descriptivos en snake_case y documenta funciones con docstrings claros explicando argumentos y retorno."
            ];
            return tips[bIdx % tips.length];
          }}
          // Genérico
          const genericTips = [
            "Memoria Activa: Tras leer este bloque, abre tu propia terminal o editor y escribe el comando o código por tu cuenta para afianzar la memoria muscular.",
            "Consolidación: Haz pausas regulares. Explicar con tus propias palabras lo que acabas de leer es la técnica más efectiva para recordar a largo plazo."
          ];
          return genericTips[bIdx % genericTips.length];
        }}

        let outputHtml = "";
        let imageIndex = 0;

        blocks.forEach((bParas, bIdx) => {{
          const bTitle = blockTitles[bIdx] || `Desarrollo y Práctica (Parte ${{bIdx + 1}})`;
          const tip = getImprovementTip(bIdx);

          // Párrafos del bloque con escape
          const parasHtml = bParas.map(p => `<p>${{escapeHtml(p)}}</p>`).join("");

          // Síntesis didáctica del bloque
          const blockSummaryPoints = bParas.map(p => {{
            const clean = p.trim().split(".")[0];
            return clean.length > 20 ? clean + "." : "";
          }}).filter(Boolean).slice(0, 2);

          outputHtml += `
            <section class="study-block">
              <div class="study-block-header">
                <span class="study-block-badge">📖 Bloque ${{bIdx + 1}}: ${{escapeHtml(bTitle)}}</span>
                <span style="font-size:11px; color:var(--text-muted);">~${{Math.max(1, Math.round(bParas.join(" ").split(" ").length / 130))}} min lectura</span>
              </div>

              <div class="study-block-body">
                ${{parasHtml}}
              </div>

              <!-- PUNTOS DE MEJORA Y BUENAS PRÁCTICAS -->
              <div class="pro-improvement-card">
                <div class="pro-improvement-header">
                  <span>⚡ Punto de Mejora & Buena Práctica</span>
                </div>
                <div>${{escapeHtml(tip)}}</div>
              </div>

              <!-- DESGLOSE DIDÁCTICO DEL BLOQUE -->
              ${{blockSummaryPoints.length > 0 ? `
                <div class="block-breakdown-card">
                  <div class="block-breakdown-title">
                    <span>📌 Desglose de lo Explicado:</span>
                  </div>
                  <ul class="block-breakdown-list">
                    ${{blockSummaryPoints.map(pt => `<li>${{escapeHtml(pt)}}</li>`).join("")}}
                  </ul>
                </div>
              ` : ''}}
            </section>
          `;

          // Intercalar Diagrama SVG conceptual entre Bloque 1 y Bloque 2
          if (bIdx === 0) {{
            outputHtml += generateContextualDiagram(lec);
          }}

          // Intercalar Imagen Real Ilustrada de Fuentes Web entre Bloque 2 y Bloque 3
          if (bIdx === 1 && availableImages.length > 0) {{
            const imgData = availableImages[imageIndex % availableImages.length];
            imageIndex++;
            outputHtml += `
              <div class="inline-illustrated-card">
                <div class="inline-illustrated-img-wrapper" onclick="window.open('${{imgData.url}}', '_blank')" title="Clic para ver en tamaño completo">
                  <img src="${{imgData.url}}" class="inline-illustrated-img" alt="${{escapeHtml(imgData.title)}}" loading="lazy">
                </div>
                <div class="inline-illustrated-footer">
                  <div class="inline-illustrated-title">🖼️ Ilustración Conceptual: ${{escapeHtml(imgData.title)}}</div>
                  <div class="inline-illustrated-caption">${{escapeHtml(imgData.caption)}} (Fuente: Documentación Abierta / Wikimedia Commons)</div>
                </div>
              </div>
            `;
          }}
        }});

        return outputHtml;
      }}

      // INVESTIGACIÓN WEB SIN IA
      window.searchWebConcept = async function(term) {{
        const container = document.getElementById("web-search-results");
        if (!container) return;
        const q = term || document.getElementById("web-concept-input").value.trim();
        if (!q) return;

        container.innerHTML = `<div style="padding:16px; text-align:center; color:var(--text-muted); font-size:13px;">🔍 Consultando Wikipedia y fuentes abiertas para "<b>${{escapeHtml(q)}}</b>"...</div>`;

        try {{
          let res = await fetch(`https://es.wikipedia.org/api/rest_v1/page/summary/${{encodeURIComponent(q)}}`);
          let data = null;
          if (res.ok) data = await res.json();

          if (!data || !data.extract || data.type === "disambiguation") {{
            let resEn = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${{encodeURIComponent(q)}}`);
            if (resEn.ok) data = await resEn.json();
          }}

          if (data && data.extract) {{
            const imgUrl = (data.originalimage && data.originalimage.source) || (data.thumbnail && data.thumbnail.source) || "";
            const pageUrl = (data.content_urls && data.content_urls.desktop && data.content_urls.desktop.page) || `https://es.wikipedia.org/wiki/${{encodeURIComponent(q)}}`;

            container.innerHTML = `
              <div class="web-result-card">
                ${{imgUrl ? `<img src="${{imgUrl}}" class="web-result-img" alt="${{escapeHtml(data.title)}}" onclick="window.open('${{imgUrl}}', '_blank')">` : ''}}
                <div class="web-result-content">
                  <div class="web-result-title">${{escapeHtml(data.title)}}</div>
                  <div class="web-result-extract">${{escapeHtml(data.extract)}}</div>
                  <a href="${{pageUrl}}" target="_blank" rel="noopener" class="web-result-link">
                    📖 Leer artículo completo en Wikipedia ➔
                  </a>
                </div>
              </div>
            `;
          }} else {{
            container.innerHTML = `
              <div style="padding:16px; background:var(--bg-card); border-radius:8px; border:1px solid var(--border); font-size:13px; color:var(--text-muted);">
                ℹ️ No se encontró un artículo directo para "<b>${{escapeHtml(q)}}</b>". Consulta en <a href="https://es.wikipedia.org/w/index.php?search=${{encodeURIComponent(q)}}" target="_blank" style="color:var(--accent);">Wikipedia</a> o en <a href="https://duckduckgo.com/?q=${{encodeURIComponent(q)}}" target="_blank" style="color:var(--accent);">DuckDuckGo</a>.
              </div>
            `;
          }}
        }} catch(e) {{
          container.innerHTML = `
            <div style="padding:14px; font-size:12.5px; color:var(--warning);">
              ⚠ No se pudo conectar a la red en este momento. Revisa tu conexión a internet para realizar búsquedas en vivo.
            </div>
          `;
        }}
      }};

      // Render del Sidebar
      function renderSidebar(filterText = "") {{
        curriculumList.innerHTML = "";
        const completed = getCompletedSet();
        const starred = getStarredSet();
        const query = filterText.toLowerCase().trim();

        COURSE_DATA.sections.forEach((sec) => {{
          const matchingLectures = sec.lectures.filter(lec => {{
            const uid = lec.id || (`s${{sec.id}}_l${{lec.num}}`);
            if (filterStarredOnly && !starred.has(uid)) return false;
            if (!query) return true;
            return (lec.title && lec.title.toLowerCase().includes(query)) ||
                   (lec.text && lec.text.toLowerCase().includes(query));
          }});

          if (matchingLectures.length === 0) return;

          const secGroup = document.createElement("div");
          secGroup.className = "section-group";

          const secHeader = document.createElement("div");
          secHeader.className = "section-header";
          secHeader.innerHTML = `
            <span class="section-title-text">${{escapeHtml(sec.title)}}</span>
            <span style="font-size:11px; opacity:0.7;">${{matchingLectures.length}}</span>
          `;
          secGroup.appendChild(secHeader);

          matchingLectures.forEach((lec) => {{
            const uid = lec.id || (`s${{sec.id}}_l${{lec.num}}`);
            const globalIdx = flatLectures.findIndex(fl => fl.uid === uid);
            const isDone = completed.has(uid);
            const isStarred = starred.has(uid);
            const isActive = globalIdx === currentLectureIndex;

            const lecItem = document.createElement("div");
            lecItem.className = `lecture-item ${{isActive ? "active" : ""}} ${{isDone ? "completed" : ""}}`;
            lecItem.innerHTML = `
              <div class="checkbox-round ${{isDone ? "checked" : ""}}" data-uid="${{escapeHtml(uid)}}"></div>
              <span class="lecture-title-sub">${{escapeHtml(lec.num)}} - ${{escapeHtml(lec.title)}}</span>
              ${{isStarred ? '<span class="badge-starred">⭐</span>' : ''}}
            `;

            lecItem.addEventListener("click", (e) => {{
              if (e.target.classList.contains("checkbox-round")) {{
                e.stopPropagation();
                toggleCompleted(uid);
                return;
              }}
              loadLecture(globalIdx);
            }});

            secGroup.appendChild(lecItem);
          }});

          curriculumList.appendChild(secGroup);
        }});
      }}

      function toggleCompleted(uid) {{
        const set = getCompletedSet();
        if (set.has(uid)) {{
          set.delete(uid);
        }} else {{
          set.add(uid);
        }}
        saveCompletedSet(set);
        updateProgress();
        renderSidebar(searchInput.value);
        updateDoneButtons();
      }}

      function updateDoneButtons() {{
        const current = flatLectures[currentLectureIndex];
        if (!current) return;
        const set = getCompletedSet();
        const isDone = set.has(current.uid);

        if (isDone) {{
          btnTopDone.classList.add("is-done");
          btnTopDone.innerHTML = "<span>✔</span> <span>Completada</span>";
        }} else {{
          btnTopDone.classList.remove("is-done");
          btnTopDone.innerHTML = "<span>○</span> <span>Marcar</span>";
        }}

        const footerBtn = document.getElementById("btn-footer-finish");
        if (footerBtn) {{
          if (isDone) {{
            footerBtn.classList.add("done");
            footerBtn.innerHTML = "✔ Lección Completada (Desmarcar)";
          }} else {{
            footerBtn.classList.remove("done");
            footerBtn.innerHTML = "✔ Marcar como Completada";
          }}
        }}
      }}

      function toggleStarred() {{
        const current = flatLectures[currentLectureIndex];
        if (!current) return;
        const set = getStarredSet();
        if (set.has(current.uid)) {{
          set.delete(current.uid);
          btnStar.classList.remove("active");
        }} else {{
          set.add(current.uid);
          btnStar.classList.add("active");
        }}
        saveStarredSet(set);
        renderSidebar(searchInput.value);
      }}

      // ========================================================================
      // CARGAR Y RENDERIZAR LECCIÓN
      // ========================================================================
      function loadLecture(index) {{
        if (index < 0 || index >= flatLectures.length) return;
        currentLectureIndex = index;
        const lec = flatLectures[index];
        const prevLec = index > 0 ? flatLectures[index - 1] : null;
        const nextLec = index < flatLectures.length - 1 ? flatLectures[index + 1] : null;

        topIndicator.textContent = `${{lec.sectionTitle}} › [${{lec.num}}] ${{lec.title}} (${{index + 1}} de ${{flatLectures.length}})`;

        // Snippets de comandos
        const snippets = extractCodeSnippets(lec.text || "");
        let codeBlocksHtml = "";
        if (snippets.length > 0) {{
          codeBlocksHtml = `
            <div class="callout-box" style="border-left-color:var(--purple); background:rgba(168,85,247,0.06); margin-bottom:20px;">
              <div style="font-weight:700; color:var(--text); margin-bottom:8px;">💻 Comandos y Sintaxis Destacada en esta Lección:</div>
              ${{snippets.map(s => `
                <div class="code-block-card">
                  <div class="code-header">
                    <span>SINTAXIS / COMANDO</span>
                    <button class="btn-copy-code" onclick="navigator.clipboard.writeText('${{escapeHtml(s)}}'); alert('¡Comando copiado!');">Copiar</button>
                  </div>
                  <div class="code-content">${{escapeHtml(s)}}</div>
                </div>
              `).join("")}}
            </div>
          `;
        }}

        // Puntos Clave Principales
        const keyPointsHtml = (lec.key_points && lec.key_points.length > 0)
          ? `
            <div class="key-points-card">
              <div class="key-points-title">💡 Puntos Clave & Ideas Principales</div>
              <ul class="key-points-list">
                ${{lec.key_points.map(pt => `<li>${{escapeHtml(pt)}}</li>`).join("")}}
              </ul>
            </div>
          `
          : "";

        // Transcripción enriquecida con Bloques, Puntos de Mejora e Imágenes
        const enrichedTranscriptHtml = renderEnrichedTranscriptView(lec);

        // Flashcards
        const flashcardsHtml = (lec.key_points && lec.key_points.length > 0)
          ? `
            <div style="margin-top:20px;">
              <div style="font-size:14px; font-weight:700; margin-bottom:10px;">🎯 Flashcards de Autoevaluación (Repaso Activo)</div>
              <div class="flashcards-container">
                ${{lec.key_points.slice(0, 3).map((kp, idx) => `
                  <div class="flashcard" onclick="this.classList.toggle('revealed')">
                    <div class="flashcard-q">❓ Pregunta de Repaso ${{idx + 1}}</div>
                    <div class="flashcard-hint">💡 Clic para revelar respuesta</div>
                    <div class="flashcard-a">${{escapeHtml(kp)}}</div>
                  </div>
                `).join("")}}
              </div>
            </div>
          `
          : "";

        // Tarjetas precargadas de conocimiento web
        const extKnowledge = COURSE_DATA.external_knowledge || {{}};
        const preloadedCards = (extKnowledge.cards || []).map(c => `
          <div class="web-result-card">
            ${{c.image ? `<img src="${{c.image}}" class="web-result-img" alt="${{escapeHtml(c.title)}}" onclick="window.open('${{c.image}}', '_blank')">` : ''}}
            <div class="web-result-content">
              <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted); margin-bottom:4px;">${{escapeHtml(c.source)}}</div>
              <div class="web-result-title">${{escapeHtml(c.title)}}</div>
              <div class="web-result-extract">${{escapeHtml(c.extract)}}</div>
              ${{c.url ? `<a href="${{c.url}}" target="_blank" rel="noopener" class="web-result-link">📖 Documentación oficial y artículo completo ➔</a>` : ''}}
            </div>
          </div>
        `).join("");

        // Enlaces oficiales
        const docsHtml = (extKnowledge.official_docs || []).map(d => `
          <a href="${{d.url}}" target="_blank" rel="noopener" class="doc-link-card">
            <span style="font-size:18px;">${{d.icon || '📚'}}</span>
            <div>
              <div style="font-size:12.5px; font-weight:700;">${{escapeHtml(d.name)}}</div>
              <div style="font-size:11px; color:var(--text-muted);">Manual oficial de referencia</div>
            </div>
          </a>
        `).join("");

        const suggestedWords = (lec.title.match(/[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}/g) || []).slice(0, 5);
        const savedNote = localStorage.getItem(STORAGE_KEY_PREFIX + "_note_" + lec.uid) || "";

        lectureContainer.innerHTML = `
          <header class="lecture-meta-header">
            <div class="lecture-breadcrumbs">${{escapeHtml(lec.sectionTitle)}}</div>
            <h1 class="lecture-main-title">[${{escapeHtml(lec.num)}}] ${{escapeHtml(lec.title)}}</h1>
            <div class="lecture-stats-badges">
              <span class="stat-badge">📖 ${{lec.word_count || 0}} palabras</span>
              <span class="stat-badge">⏱️ ~${{Math.max(1, Math.round((lec.word_count || 0) / 130))}} min</span>
              <span class="stat-badge">🆔 ${{escapeHtml(lec.uid)}}</span>
            </div>
          </header>

          <nav class="study-tabs">
            <button class="tab-btn active" data-tab="tab-content">📖 Transcripción y Estudio Enriquecido</button>
            <button class="tab-btn" data-tab="tab-web">🌐 Fuentes Web & Recursos</button>
            <button class="tab-btn" data-tab="tab-flashcards">🎯 Repaso Activo</button>
            <button class="tab-btn" data-tab="tab-notes">📝 Mis Notas</button>
          </nav>

          <!-- TAB 1: Transcripción Enriquecida con Bloques Didácticos, Mejoras e Ilustraciones -->
          <div class="tab-panel active" id="tab-content">
            ${{keyPointsHtml}}
            ${{codeBlocksHtml}}
            <div class="transcript-body">
              ${{enrichedTranscriptHtml}}
            </div>
          </div>

          <!-- TAB 2: Fuentes Web -->
          <div class="tab-panel" id="tab-web">
            <div class="web-knowledge-section">
              <div class="web-search-box">
                <div class="web-search-title">🌐 Investigador de Conceptos Web (Sin costo ni APIs de IA)</div>
                <div class="web-search-desc">
                  Consulta de forma autónoma Wikipedia, DuckDuckGo y repositorios de documentación oficial en tiempo real para ampliar cualquier concepto o diagrama de esta lección.
                </div>
                <div class="web-search-bar">
                  <input type="text" id="web-concept-input" class="web-search-input" placeholder="Escribe un concepto (ej. Git Rebase, Staging, Decoradores, API REST)...">
                  <button class="btn-web-search" onclick="searchWebConcept()">Investigar</button>
                </div>
                <div class="suggested-tags-row">
                  <span style="font-size:11px; color:var(--text-muted); font-weight:600;">Sugerencias de la lección:</span>
                  ${{suggestedWords.map(w => `<span class="tag-pill" onclick="searchWebConcept('${{escapeHtml(w)}}')">${{escapeHtml(w)}}</span>`).join("")}}
                </div>
                <div id="web-search-results"></div>
              </div>

              ${{preloadedCards ? `
                <div>
                  <div style="font-size:14px; font-weight:700; margin-bottom:10px;">📚 Conocimiento Enciclopédico & Diagramas Relacionados:</div>
                  <div style="display:flex; flex-direction:column; gap:12px;">${{preloadedCards}}</div>
                </div>
              ` : ''}}

              ${{docsHtml ? `
                <div>
                  <div style="font-size:14px; font-weight:700; margin-bottom:8px;">🔗 Documentación Oficial Recomendada:</div>
                  <div class="docs-links-grid">${{docsHtml}}</div>
                </div>
              ` : ''}}
            </div>
          </div>

          <!-- TAB 3: Flashcards -->
          <div class="tab-panel" id="tab-flashcards">
            ${{flashcardsHtml || '<p style="color:var(--text-muted); font-size:13px;">No hay preguntas automáticas para esta lección.</p>'}}
          </div>

          <!-- TAB 4: Notas -->
          <div class="tab-panel" id="tab-notes">
            <div class="notes-box">
              <div class="notes-header">
                <span style="font-size:14px; font-weight:700;">✏️ Mis Apuntes para esta Lección</span>
                <button class="btn-ctrl" id="btn-export-notes">📥 Exportar Todas (.md)</button>
              </div>
              <textarea class="notes-textarea" id="lecture-note-input" placeholder="Escribe aquí tus notas personales... Se guardan automáticamente.">${{escapeHtml(savedNote)}}</textarea>
              <div class="notes-footer">
                <span>Guardado automático local</span>
                <span id="note-save-status">✓ Al día</span>
              </div>
            </div>
          </div>

          <!-- PIE DE LECCIÓN FLUIDO -->
          <footer class="lesson-footer-nav">
            <div class="lesson-done-banner">
              <div>
                <div style="font-weight:700; font-size:13.5px;">¿Terminaste de estudiar esta lección?</div>
                <div style="font-size:12px; color:var(--text-muted);">Márcala para actualizar tu porcentaje global del curso.</div>
              </div>
              <button class="btn-finish-lesson" id="btn-footer-finish">
                ✔ Marcar como Completada
              </button>
            </div>

            <div class="nav-cards-grid">
              ${{prevLec ? `
                <div class="nav-step-card prev" id="card-nav-prev">
                  <span class="nav-card-label">⬅ Anterior</span>
                  <span class="nav-card-title">[${{escapeHtml(prevLec.num)}}] ${{escapeHtml(prevLec.title)}}</span>
                </div>
              ` : `
                <div class="nav-step-card disabled">
                  <span class="nav-card-label">⬅ Anterior</span>
                  <span class="nav-card-title">Inicio del curso</span>
                </div>
              `}}

              ${{nextLec ? `
                <div class="nav-step-card next" id="card-nav-next">
                  <span class="nav-card-label">Siguiente ➔</span>
                  <span class="nav-card-title">[${{escapeHtml(nextLec.num)}}] ${{escapeHtml(nextLec.title)}}</span>
                </div>
              ` : `
                <div class="nav-step-card disabled next">
                  <span class="nav-card-label">Siguiente ➔</span>
                  <span class="nav-card-title">Fin del temario 🎉</span>
                </div>
              `}}
            </div>
          </footer>
        `;

        // Listeners de pestañas
        lectureContainer.querySelectorAll(".tab-btn").forEach(btn => {{
          btn.addEventListener("click", () => {{
            lectureContainer.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            lectureContainer.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(btn.getAttribute("data-tab")).classList.add("active");
          }});
        }});

        // Listener notas
        const noteInput = document.getElementById("lecture-note-input");
        const noteStatus = document.getElementById("note-save-status");
        if (noteInput) {{
          noteInput.addEventListener("input", () => {{
            localStorage.setItem(STORAGE_KEY_PREFIX + "_note_" + lec.uid, noteInput.value);
            noteStatus.textContent = "Guardado ✓";
          }});
        }}

        const btnExportNotes = document.getElementById("btn-export-notes");
        if (btnExportNotes) {{
          btnExportNotes.addEventListener("click", exportAllNotes);
        }}

        const cardPrev = document.getElementById("card-nav-prev");
        if (cardPrev) cardPrev.addEventListener("click", () => loadLecture(index - 1));

        const cardNext = document.getElementById("card-nav-next");
        if (cardNext) cardNext.addEventListener("click", () => loadLecture(index + 1));

        const btnFooterFinish = document.getElementById("btn-footer-finish");
        if (btnFooterFinish) {{
          btnFooterFinish.addEventListener("click", () => toggleCompleted(lec.uid));
        }}

        const webInput = document.getElementById("web-concept-input");
        if (webInput) {{
          webInput.addEventListener("keydown", (e) => {{
            if (e.key === "Enter") searchWebConcept();
          }});
        }}

        const starred = getStarredSet();
        btnStar.classList.toggle("active", starred.has(lec.uid));

        stopTTS();
        document.getElementById("scroll-area").scrollTop = 0;

        btnStepPrev.disabled = index === 0;
        btnStepNext.disabled = index === flatLectures.length - 1;
        updateDoneButtons();
        renderSidebar(searchInput.value);
      }}

      // Exportar notas a markdown
      function exportAllNotes() {{
        let md = `# Notas de Estudio: ${{COURSE_DATA.title}}\\n\\n`;
        let count = 0;
        flatLectures.forEach(lec => {{
          const note = localStorage.getItem(STORAGE_KEY_PREFIX + "_note_" + lec.uid);
          if (note && note.trim()) {{
            count++;
            md += `## [${{lec.num}}] ${{lec.title}}\\n**Sección:** ${{lec.sectionTitle}}\\n\\n${{note}}\\n\\n---\\n\\n`;
          }}
        }});
        if (count === 0) {{
          alert("Aún no tienes notas escritas en ninguna lección.");
          return;
        }}
        const blob = new Blob([md], {{ type: "text/markdown;charset=utf-8" }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Notas_${{COURSE_DATA.title.replace(/[^a-zA-Z0-9]/g, "_")}}.md`;
        a.click();
      }}

      // AUDIO TTS
      const audioBar = document.getElementById("audio-player-bar");
      const btnTtsToggle = document.getElementById("btn-tts-toggle");
      const btnTtsPlay = document.getElementById("btn-tts-play");
      const btnTtsPause = document.getElementById("btn-tts-pause");
      const btnTtsStop = document.getElementById("btn-tts-stop");
      const audioSpeed = document.getElementById("audio-speed");
      const audioStatus = document.getElementById("audio-status");

      let synth = window.speechSynthesis;
      let currentUtterance = null;

      btnTtsToggle.addEventListener("click", () => {{
        audioBar.classList.toggle("active");
      }});

      function stopTTS() {{
        if (synth) synth.cancel();
        if (audioStatus) audioStatus.textContent = "Detenido";
      }}

      btnTtsStop.addEventListener("click", stopTTS);

      btnTtsPause.addEventListener("click", () => {{
        if (synth && synth.speaking) {{
          if (synth.paused) {{
            synth.resume();
            audioStatus.textContent = "Reproduciendo...";
          }} else {{
            synth.pause();
            audioStatus.textContent = "Pausado";
          }}
        }}
      }});

      btnTtsPlay.addEventListener("click", () => {{
        if (!synth) {{
          alert("Tu navegador no soporta síntesis de voz.");
          return;
        }}
        stopTTS();
        const current = flatLectures[currentLectureIndex];
        if (!current || !current.text) {{
          alert("No hay texto para leer en esta lección.");
          return;
        }}

        currentUtterance = new SpeechSynthesisUtterance(current.text);
        currentUtterance.rate = parseFloat(audioSpeed.value || "1.0");
        currentUtterance.lang = "es-ES";

        currentUtterance.onstart = () => {{
          audioStatus.textContent = "Leyendo...";
        }};
        currentUtterance.onend = () => {{
          audioStatus.textContent = "Finalizado";
        }};
        currentUtterance.onerror = () => {{
          audioStatus.textContent = "Detenido";
        }};

        synth.speak(currentUtterance);
      }});

      // CONTROLES Y EVENTOS
      btnStepPrev.addEventListener("click", () => loadLecture(currentLectureIndex - 1));
      btnStepNext.addEventListener("click", () => loadLecture(currentLectureIndex + 1));
      btnTopDone.addEventListener("click", () => {{
        const current = flatLectures[currentLectureIndex];
        if (current) toggleCompleted(current.uid);
      }});
      btnStar.addEventListener("click", toggleStarred);

      btnFilterStarred.addEventListener("click", () => {{
        filterStarredOnly = !filterStarredOnly;
        btnFilterStarred.classList.toggle("active", filterStarredOnly);
        renderSidebar(searchInput.value);
      }});

      let searchTimer = null;
      searchInput.addEventListener("input", (e) => {{
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {{
          renderSidebar(e.target.value);
        }}, 140);
      }});

      const btnZen = document.getElementById("btn-zen-mode");
      btnZen.addEventListener("click", () => {{
        document.body.classList.toggle("zen-mode");
        btnZen.classList.toggle("active", document.body.classList.contains("zen-mode"));
      }});

      window.addEventListener("keydown", (e) => {{
        if (document.activeElement.tagName === "INPUT" || document.activeElement.tagName === "TEXTAREA") return;
        if (e.key === "ArrowRight") loadLecture(currentLectureIndex + 1);
        if (e.key === "ArrowLeft") loadLecture(currentLectureIndex - 1);
        if (e.key === "f" || e.key === "F") btnZen.click();
        if (e.key === " ") {{
          e.preventDefault();
          const current = flatLectures[currentLectureIndex];
          if (current) toggleCompleted(current.uid);
        }}
      }});

      let sidebarVisible = true;
      document.getElementById("btn-toggle-sidebar").addEventListener("click", () => {{
        sidebarVisible = !sidebarVisible;
        sidebar.style.display = sidebarVisible ? "flex" : "none";
      }});

      const themes = ["dark", "light", "sepia"];
      let themeIdx = 0;
      document.getElementById("btn-theme-toggle").addEventListener("click", () => {{
        themeIdx = (themeIdx + 1) % themes.length;
        document.documentElement.setAttribute("data-theme", themes[themeIdx]);
      }});

      document.getElementById("btn-copy-text").addEventListener("click", () => {{
        const current = flatLectures[currentLectureIndex];
        if (current && current.text) {{
          navigator.clipboard.writeText(current.text).then(() => {{
            alert("📋 ¡Texto de la lección copiado al portapapeles!");
          }});
        }}
      }});

      // Inicialización
      updateProgress();
      renderSidebar();
      loadLecture(0);
    }})();
  </script>
</body>
</html>
"""
    index_file = output_path / "index.html"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return index_file
