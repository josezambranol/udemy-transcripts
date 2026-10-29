#!/usr/bin/env python3
"""
==============================================================================
UDEMY TRANSCRIPTS PRO — Descarga, Transcripción y Centro de Estudio Interactivo
==============================================================================
Descarga las transcripciones de cualquier curso de Udemy en:
  1. 🌐 HTML Interactivo (Dashboard autónomo con buscador, notas, progreso y modo oscuro).
  2. 📝 Markdown enriquecido (FULL_COURSE.md con Tabla de Contenidos interactiva).
  3. 📄 Archivos de texto limpio (.txt por video o unificado).

Usa un navegador real (Playwright Chromium) para reutilizar tu sesión y atravesar
la protección Cloudflare de Udemy sin bloqueos.
==============================================================================
"""

import argparse
import html
import json
import os
import re
import sys
import textwrap
import time
from pathlib import Path

# Compatibilidad de caracteres UTF-8 en consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("✗ Falta Playwright. Instálalo con:\n"
             "    pip3 install playwright\n"
             "    python3 -m playwright install chromium")

from html_generator import generate_interactive_html, extract_key_points
from markdown_generator import generate_course_markdown
from converter import convert_local_course_directory

DEFAULT_BASE_URL = "https://www.udemy.com"
BASE_URL = "https://www.udemy.com"
API = f"{BASE_URL}/api-2.0"
PROFILE_DIR = Path.home() / ".cache" / "udemy-transcripts-profile"


def set_portal(url_or_subdomain):
    """Configura dinámicamente el portal base (soporta Udemy Business como seti.udemy.com)."""
    global BASE_URL, API
    if not url_or_subdomain:
        return
    url = url_or_subdomain.strip()
    if not url.startswith("http"):
        if "." in url:
            url = f"https://{url}"
        else:
            url = f"https://{url}.udemy.com"
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc or parsed.path
    BASE_URL = f"https://{domain}".rstrip("/")
    API = f"{BASE_URL}/api-2.0"


def print_banner():
    print("=" * 76)
    print("      🎓 UDEMY TRANSCRIPTS PRO — ESTUDIO INTERACTIVO & TRANSCRIPCIÓN 🎓")
    print("=" * 76)
    print("  Convierte cursos en Dashboards Web Interactivos, Markdown y Texto Limpio.")
    print("=" * 76)
    print()


def goto_cf(page, url, wait=25):
    """Navega de forma no bloqueante y espera a que Cloudflare resuelva su challenge si aparece."""
    try:
        page.goto(url, wait_until="commit", timeout=25000)
    except Exception:
        pass
    for _ in range(wait):
        t = (page.title() or "").lower()
        if "just a moment" not in t and "un momento" not in t and "moment" not in t:
            return
        time.sleep(1)


def api_get(page, url):
    """fetch same-origin desde la página real → atraviesa Cloudflare, da JSON."""
    txt = page.evaluate(
        """async (u) => {
            const r = await fetch(u, {headers: {'Accept': 'application/json'},
                                      credentials: 'include'});
            return await r.text();
        }""", url)
    try:
        return json.loads(txt)
    except (json.JSONDecodeError, TypeError):
        return None


def _logged_user(page):
    me = api_get(page, f"{API}/users/me/?fields%5Buser%5D=title")
    if me and isinstance(me.get("id"), int) and me["id"] > 0:
        return me
    return None


def ensure_login(page):
    goto_cf(page, f"{BASE_URL}/")
    me = _logged_user(page)
    if me:
        portal_name = "Udemy Business" if BASE_URL != DEFAULT_BASE_URL else "Udemy"
        print(f"  ✔ Sesión activa detectada ({portal_name}): {me.get('title') or me.get('id')}")
        return True

    print(f"\n▶ Inicia sesión en la ventana del navegador ({BASE_URL}).")
    if BASE_URL != DEFAULT_BASE_URL:
        print(f"  🏢 Portal Corporativo: {BASE_URL}")
    else:
        print("  💡 Si usas cuenta de empresa (ej. seti.udemy.com), puedes navegar a tu portal en la ventana.")
    print("  ⚠️ Si aparece la pantalla de verificación ('Un momento...' / 'Verify you are human'),")
    print("     marca la casilla en la ventana para continuar.")
    input("\n  Cuando ya estés dentro de tu cuenta en Udemy, vuelve aquí y pulsa ENTER… ")

    # Si el usuario navegó a un portal corporativo en la ventana, sincronizarlo
    try:
        current_url = page.url
        if ".udemy.com" in current_url:
            set_portal(current_url)
    except Exception:
        pass

    goto_cf(page, f"{BASE_URL}/")
    me = _logged_user(page)
    if not me:
        sys.exit("✗ No detecto sesión iniciada. Vuelve a intentarlo o pasa tu token con --token.")
    portal_name = "Udemy Business" if BASE_URL != DEFAULT_BASE_URL else "Udemy"
    print(f"  ✔ Sesión activa detectada ({portal_name}): {me.get('title') or me.get('id')}")
    return True


def fetch_all_subscribed_courses(page):
    """Obtiene la lista completa de cursos inscritos del usuario."""
    url = (f"{API}/users/me/subscribed-courses/"
           "?fields%5Bcourse%5D=id,title,url&page_size=100&ordering=-last_accessed")
    rows = []
    while url:
        data = api_get(page, url)
        if not data:
            break
        rows.extend(data.get("results", []))
        url = data.get("next")
    return rows


def list_courses(page):
    rows = fetch_all_subscribed_courses(page)
    if not rows:
        sys.exit("✗ No pude leer tus cursos o la lista está vacía.")
    print(f"\nTienes {len(rows)} cursos inscritos:\n")
    for idx, c in enumerate(rows, 1):
        print(f"  [{idx:2d}] (ID: {c['id']}) {c['title']}")
    print("\nPuedes descargar cualquiera ejecutando:")
    print("  udemy <id-o-URL>")


def resolve_course_id(page, arg):
    if arg.isdigit():
        return arg
    m = re.search(r"/course/([^/?#]+)", arg)
    slug = m.group(1) if m else arg.strip("/").split("/")[-1]
    # 1) buscar el slug entre tus cursos inscritos
    url = (f"{API}/users/me/subscribed-courses/"
           "?fields%5Bcourse%5D=id,url&page_size=100")
    while url:
        data = api_get(page, url)
        if not data:
            break
        for c in data.get("results", []):
            curl = c.get("url") or ""
            if f"/course/{slug}/" in curl or curl.rstrip("/").endswith("/" + slug):
                return str(c["id"])
        url = data.get("next")
    # 2) fallback: parsear el HTML de la landing del curso
    goto_cf(page, f"{BASE_URL}/course/{slug}/")
    content = page.content()
    for pat in (r'data-clp-course-id="(\d+)"', r'courseId\D{0,8}(\d+)',
                r'/course/(\d+)/'):
        m = re.search(pat, content)
        if m:
            return m.group(1)
    sys.exit("✗ No pude resolver el course_id. Usa  udemy --list  para ver el id "
             "y pásalo directo:  udemy <id>.")


def fetch_curriculum(page, course_id):
    fields = (
        "&fields%5Blecture%5D=title,object_index,asset"
        "&fields%5Bchapter%5D=title,object_index"
        "&fields%5Basset%5D=asset_type,captions,title"
        "&fields%5Bcaption%5D=url,locale_id,video_label,file_name"
    )
    url = (f"{API}/courses/{course_id}/subscriber-curriculum-items/"
           f"?page_size=200{fields}")
    items = []
    while url:
        data = api_get(page, url)
        if not data:
            sys.exit("✗ No pude leer el temario (¿estás inscrito en el curso?).")
        items.extend(data.get("results", []))
        url = data.get("next")
    return items


def pick_caption(captions, langs):
    if not captions:
        return None
    for want in langs:
        for c in captions:
            if (c.get("locale_id") or "").lower().startswith(want.lower()):
                return c
    return captions[0]


def vtt_to_text(vtt, width=100, include_timestamps=False):
    """
    Limpia el archivo .vtt eliminando cabeceras, marcas de tiempo y etiquetas de formato WebVTT.
    Si include_timestamps=True, conserva las marcas de tiempo en formato [MM:SS].
    """
    lines = []
    current_time = ""
    for raw in vtt.splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or line.isdigit() or line.startswith(("NOTE", "STYLE", "Kind:", "Language:")):
            continue
        if "-->" in line:
            if include_timestamps:
                m = re.search(r"(\d{2}:)?(\d{2}:\d{2})\.\d+", line)
                if m:
                    current_time = f"[{m.group(2)}] "
            continue

        # Limpiar etiquetas WebVTT comunes sin destruir sintaxis de código como <T> o <div>
        line = re.sub(r'<\/?(?:c(?:\.[a-zA-Z0-9_-]+)*|v\s+[^>]*|b|i|u|ruby|rt|lang|span|\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?)[^>]*>', '', line, flags=re.IGNORECASE)
        line = html.unescape(line).strip()
        if line:
            if include_timestamps and current_time:
                line = current_time + line
                current_time = ""
            if not lines or lines[-1] != line:
                lines.append(line)

    if include_timestamps:
        return "\n".join(lines)

    text = re.sub(r"\s+", " ", " ".join(lines)).strip()
    text = re.sub(r"(?<=[.!?])\s+", "\n", text)
    if width and width > 0:
        text = "\n".join(textwrap.fill(p, width) if p else "" for p in text.split("\n"))
    return text


def safe_name(name):
    name = re.sub(r'[/\\:*?"<>|]', "-", name or "").strip()
    return re.sub(r"\s+", " ", name)[:120]


# ==============================================================================
# MENÚ INTERACTIVO EN TERMINAL
# ==============================================================================

def interactive_terminal_flow(page):
    """
    Flujo interactivo cuando no se pasan argumentos por consola.
    """
    print_banner()
    if BASE_URL != DEFAULT_BASE_URL:
        print(f"  🏢 Portal Corporativo Activo: {BASE_URL}")
    print("• Comprobando sesión activa en Udemy...")
    ensure_login(page)

    print("\n• Obteniendo tus cursos inscritos...")
    courses = fetch_all_subscribed_courses(page)

    if not courses:
        print("[!] No se encontraron cursos suscritos en esta cuenta.")
        manual = input(">> ¿Deseas ingresar la URL de un curso manualmente? (s/n): ").strip().lower()
        if manual == 's':
            course_input = input(">> Ingresa la URL o ID del curso: ").strip()
            return course_input, {"html": True, "md": True, "txt": True, "skip_existing": True}
        return None, None

    print("\n" + "=" * 76)
    print("  📚 TUS CURSOS DE UDEMY DISPONIBLES:")
    print("=" * 76)
    for idx, c in enumerate(courses, 1):
        print(f"    [{idx:2d}] {c['title']} (ID: {c['id']})")
    print("    [C ] 🔄 Convertir carpeta ya descargada a HTML Interactivo / Markdown")
    print("    [M ] 🔗 Ingresar URL o ID manualmente")
    print("    [0 ] ❌ Salir")
    print("=" * 76)

    choice = input("\n>> Selecciona el número del curso que deseas transcribir: ").strip()
    if choice == "0":
        return None, None

    if choice.upper() == "C":
        default_dir = str(Path.home() / "OneDrive" / "Desktop" / "Udemy-Transcripts")
        if not os.path.exists(default_dir):
            default_dir = str(Path.home() / "Udemy-Transcripts")
        print(f"\nCarpeta sugerida: {default_dir}")
        folder = input(f">> Ingresa la ruta de la carpeta del curso a convertir: ").strip()
        if not folder:
            folder = default_dir
        convert_local_course_directory(folder)
        return None, None

    if choice.upper() == "M":
        course_arg = input(">> Ingresa la URL o ID del curso: ").strip()
    elif choice.isdigit() and 1 <= int(choice) <= len(courses):
        course_arg = str(courses[int(choice) - 1]["id"])
    else:
        print("[!] Selección no válida.")
        return None, None

    # Opciones de formato
    print("\n" + "-" * 76)
    print("  🎨 ¿QUÉ FORMATOS DESEAS GENERAR?")
    print("-" * 76)
    print("    [1] 🌟 Completo: HTML Interactivo + Markdown + TXT (Recomendado)")
    print("    [2] 🌐 Solo HTML Interactivo (Dashboard de Estudio)")
    print("    [3] 📝 Solo Markdown (FULL_COURSE.md con Índice interactivo)")
    print("    [4] 📄 Solo Texto plano (.txt por lección)")
    print("    [5] 📑 Todo el curso en UN solo archivo .txt")
    print("-" * 76)
    fmt = input(">> Selecciona una opción (1-5, default 1): ").strip() or "1"

    config = {
        "html": fmt in ("1", "2"),
        "md": fmt in ("1", "3"),
        "txt_per_video": fmt in ("1", "4"),
        "txt_single": fmt == "5",
        "skip_existing": True,
        "timestamps": False,
        "sections": None
    }

    # Preguntar por secciones específicas
    sec_filter = input("\n>> ¿Descargar todas las secciones? [ENTER para Sí, o escribe ej. 1,2,3]: ").strip()
    if sec_filter:
        config["sections"] = [int(s.strip()) for s in sec_filter.split(",") if s.strip().isdigit()]

    return course_arg, config


# ==============================================================================
# MOTOR PRINCIPAL DE DESCARGA Y PROCESAMIENTO
# ==============================================================================

def process_course_download(page, context, course_arg, options):
    """
    Descarga transcripciones del curso y genera los formatos seleccionados.
    """
    print("\n• Resolviendo curso...")
    course_id = resolve_course_id(page, course_arg)
    info = api_get(page, f"{API}/courses/{course_id}/?fields%5Bcourse%5D=title")
    title = (info or {}).get("title", f"curso-{course_id}")
    print(f"  → {title} (ID: {course_id})")

    # Carpetas de destino
    desktop_udemy = Path.home() / "OneDrive" / "Desktop" / "Udemy-Transcripts"
    default_base = desktop_udemy if desktop_udemy.parent.exists() else Path.home() / "Udemy-Transcripts"
    udemy_dir = Path(options.get("out")) if options.get("out") else default_base
    udemy_dir.mkdir(parents=True, exist_ok=True)

    course_dir = udemy_dir / safe_name(title)
    course_dir.mkdir(parents=True, exist_ok=True)

    print("• Leyendo temario del curso...")
    items = fetch_curriculum(page, course_id)

    # Filtrar secciones si fue solicitado
    section_whitelist = options.get("sections")
    langs = options.get("lang", ["es", "en"])
    skip_existing = options.get("skip_existing", False)
    include_timestamps = options.get("timestamps", False)
    width = options.get("width", 100)

    # Estructuras para HTML y Markdown
    sections_data = []
    current_section_obj = None
    section_index = 0
    section_title = "00 - General"

    saved, skipped, skipped_exist = 0, 0, 0
    txt_single_parts = []

    total_lectures_count = sum(1 for it in items if it.get("_class") == "lecture" and (it.get("asset") or {}).get("asset_type") == "Video")
    processed_count = 0

    print(f"\n🚀 Iniciando procesamiento de {total_lectures_count} lecciones...")
    print(f"   Destino: {course_dir}\n")

    for it in items:
        klass = it.get("_class")

        # 1. Capítulo / Sección
        if klass == "chapter":
            ci = it.get("object_index") or (section_index + 1)
            section_index = ci
            section_title = f"{ci:02d} - {safe_name(it.get('title'))}"

            if section_whitelist and ci not in section_whitelist:
                current_section_obj = None
                continue

            current_section_obj = {
                "id": ci,
                "title": section_title,
                "lectures": []
            }
            sections_data.append(current_section_obj)
            continue

        # 2. Lección
        if klass != "lecture":
            continue

        asset = it.get("asset") or {}
        if asset.get("asset_type") != "Video":
            continue

        processed_count += 1
        li = it.get("object_index")
        num = f"{li:03d}" if isinstance(li, int) else f"{processed_count:03d}"
        ltitle = safe_name(it.get("title", f"leccion-{num}"))

        if section_whitelist and section_index not in section_whitelist:
            continue

        if not current_section_obj:
            current_section_obj = {
                "id": section_index or 1,
                "title": section_title,
                "lectures": []
            }
            sections_data.append(current_section_obj)

        sec_dir = course_dir / section_title
        txt_file = sec_dir / f"{num} - {ltitle}.txt"

        # Reanudación inteligente: saltar si ya existe
        uid = f"s{section_index:02d}_l{num}"
        if skip_existing and txt_file.exists() and txt_file.stat().st_size > 40:
            try:
                cached_text = txt_file.read_text(encoding="utf-8", errors="replace")
                current_section_obj["lectures"].append({
                    "id": uid,
                    "num": num,
                    "title": ltitle,
                    "text": cached_text,
                    "word_count": len(cached_text.split()),
                    "key_points": extract_key_points(cached_text, max_points=3)
                })
                skipped_exist += 1
                pct = int((processed_count / total_lectures_count) * 100)
                print(f"  [♻️ Ya existe] [{pct:2d}%] [{num}] {ltitle}")
                continue
            except Exception:
                pass

        cap = pick_caption(asset.get("captions") or [], langs)
        if not cap or not cap.get("url"):
            print(f"  [– Sin subtítulo] [{num}] {ltitle}")
            skipped += 1
            continue

        r = context.request.get(cap["url"])
        if not r.ok:
            print(f"  [✘ Error descarga] [{num}] {ltitle}")
            skipped += 1
            continue

        text = vtt_to_text(r.text(), width=width, include_timestamps=include_timestamps)
        words = len(text.split())
        key_pts = extract_key_points(text, max_points=3)

        # Guardar en estructura de datos
        current_section_obj["lectures"].append({
            "id": uid,
            "num": num,
            "title": ltitle,
            "text": text,
            "word_count": words,
            "key_points": key_pts
        })

        # Guardar en .txt individual si está activo
        if options.get("txt_per_video", True):
            sec_dir.mkdir(parents=True, exist_ok=True)
            txt_file.write_text(text + "\n", encoding="utf-8")

        # Acumular para .txt unificado
        if options.get("txt_single", False):
            txt_single_parts.append(f"{'='*70}\n[{num}] {section_title} — {ltitle}\n{'='*70}\n\n{text}")

        pct = int((processed_count / total_lectures_count) * 100)
        saved += 1
        print(f"  [✓] [{pct:2d}%] [{num}] {ltitle} ({cap.get('locale_id')})")
        time.sleep(0.15)

    print("\n" + "=" * 76)
    print(f"  🏁 DESCARGA FINALIZADA:")
    print(f"     - Transcripciones descargadas: {saved}")
    print(f"     - Ya existían (reutilizadas):  {skipped_exist}")
    print(f"     - Sin subtítulos disponibles:   {skipped}")
    print("=" * 76)

    # 1. Generar HTML Interactivo
    if options.get("html", True) and sections_data:
        print("\n• Generando Dashboard HTML Interactivo...")
        html_file = generate_interactive_html(title, sections_data, course_dir)
        print(f"  ✔ [HTML Interactivo] Creado: {html_file}")

    # 2. Generar Markdown Enriquecido (FULL_COURSE.md)
    if options.get("md", True) and sections_data:
        print("• Generando Markdown con Tabla de Contenidos (TOC)...")
        md_file = generate_course_markdown(title, sections_data, course_dir)
        print(f"  ✔ [Markdown Completo] Creado: {md_file}")

    # 3. Guardar .txt unificado si fue pedido
    if options.get("txt_single", False) and txt_single_parts:
        single_file = course_dir / f"{safe_name(title)}.txt"
        single_file.write_text(f"{title}\n\n" + "\n\n".join(txt_single_parts) + "\n", encoding="utf-8")
        print(f"  ✔ [Texto Unificado] Creado: {single_file}")

    print("\n" + "=" * 76)
    print(f"🎉 ¡TODO LISTO! Puedes abrir el centro de estudio interactivo en:")
    print(f"   file:///{str(course_dir / 'index.html').replace(os.sep, '/')}")
    print("=" * 76 + "\n")


def main():
    ap = argparse.ArgumentParser(description="Transcripciones de un curso de Udemy.")
    ap.add_argument("course", nargs="?", help="URL del curso, slug o course_id numérico")
    ap.add_argument("-p", "--portal", default=None,
                    help="Subdominio o URL corporativa de Udemy Business (ej: seti o https://seti.udemy.com)")
    ap.add_argument("--list", action="store_true", dest="do_list",
                    help="lista tus cursos suscritos y termina")
    ap.add_argument("--token", default=os.environ.get("UDEMY_TOKEN"),
                    help="access_token de la cookie (evita el login manual)")
    ap.add_argument("--lang", default="es,en")
    ap.add_argument("--out", default=None,
                    help="carpeta base de salida (default Desktop/Udemy-Transcripts)")
    ap.add_argument("--txt", action="store_true",
                    help="todo el curso en UN solo .txt")
    ap.add_argument("--no-html", action="store_true",
                    help="desactiva la generación del dashboard HTML")
    ap.add_argument("--no-md", action="store_true",
                    help="desactiva la generación del archivo Markdown")
    ap.add_argument("--skip-existing", action="store_true", default=True,
                    help="salta videos que ya tengan archivo generado (default: True)")
    ap.add_argument("--timestamps", action="store_true",
                    help="conserva marcas de tiempo en formato [MM:SS]")
    ap.add_argument("--convert-local", default=None,
                    help="convierte una carpeta descargada previamente a HTML y Markdown")
    ap.add_argument("--width", type=int, default=100,
                    help="ancho de línea del texto; 0 = sin ajustar (default 100)")
    ap.add_argument("--headless", action="store_true",
                    help="(NO recomendado: Udemy bloquea el modo headless con Cloudflare)")

    args = ap.parse_args()

    # Si se solicitó convertir una carpeta local existente
    if args.convert_local:
        convert_local_course_directory(args.convert_local)
        return

    # Sincronizar portal corporativo si se especificó
    if args.portal:
        set_portal(args.portal)
    elif args.course and ".udemy.com" in args.course:
        set_portal(args.course)

    # Detectar Google Chrome oficial para máxima compatibilidad con SSO y Cloudflare
    chrome_exe = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
    channel = "chrome" if chrome_exe.exists() else None

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=args.headless,
            channel=channel,
            viewport={"width": 1280, "height": 850},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-first-run",
                "--no-service-autorun"
            ]
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = window.chrome || { runtime: {} };
        """)

        if args.token:
            domain = urllib.parse.urlparse(BASE_URL).netloc
            cookies_to_add = [
                {"name": "access_token", "value": args.token, "domain": f".{domain}", "path": "/", "secure": True},
                {"name": "access_token", "value": args.token, "domain": ".udemy.com", "path": "/", "secure": True}
            ]
            context.add_cookies(cookies_to_add)

        page = context.pages[0] if context.pages else context.new_page()

        if args.do_list:
            ensure_login(page)
            list_courses(page)
            context.close()
            return

        if not args.course:
            course_arg, config = interactive_terminal_flow(page)
            if not course_arg:
                context.close()
                return
            options = {
                "out": args.out,
                "lang": [x.strip() for x in args.lang.split(",") if x.strip()],
                "width": args.width,
                **config
            }
        else:
            course_arg = args.course
            ensure_login(page)
            options = {
                "out": args.out,
                "lang": [x.strip() for x in args.lang.split(",") if x.strip()],
                "width": args.width,
                "html": not args.no_html,
                "md": not args.no_md,
                "txt_per_video": not args.txt,
                "txt_single": args.txt,
                "skip_existing": args.skip_existing,
                "timestamps": args.timestamps
            }

        process_course_download(page, context, course_arg, options)
        context.close()


if __name__ == "__main__":
    main()
