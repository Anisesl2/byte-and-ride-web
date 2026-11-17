import streamlit as st
import streamlit.components.v1 as components
import html
import re
import base64
import hashlib
import json
import secrets
import threading
import time as time_module
from urllib.parse import urlparse, unquote, urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import date, time, datetime, timezone
from supabase import create_client


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="FAMILY BIKE | Rutas en moto",
    page_icon="🏍️",
    layout="wide"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

AUTH_DOMAIN = "users.byteandride.invalid"
BUCKET_FAMILYBIKE = "familybike"
TIENDA_URL = "https://payhip.com/Kardiaqo"
FACEBOOK_URL = "https://m.facebook.com/groups/1646146103973952/?ref=share"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# OAuth Google PKCE: los verificadores se guardan temporalmente en el servidor.
# No se guardan tokens ni verificadores en la URL del navegador.
GOOGLE_REDIRECT_URL = "https://byte-and-ride-web-bbzmzh8vkhdgmhztvreddr.streamlit.app/"


@st.cache_resource
def almacen_oauth_google():
    return {"flujos": {}, "lock": threading.RLock()}


def iniciar_google_oauth():
    nonce = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")

    almacen = almacen_oauth_google()
    with almacen["lock"]:
        ahora = time_module.time()
        for clave, registro in list(almacen["flujos"].items()):
            if ahora - registro["creado"] > 600:
                almacen["flujos"].pop(clave, None)
        almacen["flujos"][nonce] = {
            "verifier": verifier, "creado": ahora
        }

    retorno = GOOGLE_REDIRECT_URL + "?" + urlencode({"fb_oauth": nonce})
    parametros = urlencode({
        "provider": "google",
        "redirect_to": retorno,
        "code_challenge": challenge,
        "code_challenge_method": "s256",
    })
    return SUPABASE_URL.rstrip("/") + "/auth/v1/authorize?" + parametros


def completar_google_oauth():
    codigo = st.query_params.get("code")
    nonce = st.query_params.get("fb_oauth")
    error_google = st.query_params.get("error_description") or st.query_params.get("error")

    if not nonce and not error_google:
        return None

    if error_google:
        st.query_params.clear()
        return "Google ha cancelado el acceso o ha devuelto un error. Inténtalo de nuevo."

    if not codigo or not nonce:
        st.query_params.clear()
        return "No se ha recibido el código de autorización de Google."

    almacen = almacen_oauth_google()
    with almacen["lock"]:
        registro = almacen["flujos"].pop(nonce, None)

    if not registro or time_module.time() - registro["creado"] > 600:
        st.query_params.clear()
        return "El acceso de Google ha caducado. Pulsa de nuevo el botón."

    try:
        datos = json.dumps({
            "auth_code": codigo,
            "code_verifier": registro["verifier"]
        }).encode("utf-8")
        peticion = Request(
            SUPABASE_URL.rstrip("/") + "/auth/v1/token?grant_type=pkce",
            data=datos,
            headers={
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urlopen(peticion, timeout=20) as respuesta:
            sesion = json.load(respuesta)

        access_token = sesion["access_token"]
        refresh_token = sesion["refresh_token"]
        # Verificar la identidad en Supabase, sin confiar en parámetros del navegador.
        supabase.auth.set_session(access_token, refresh_token)
        usuario = supabase.auth.get_user().user
        if usuario is None:
            raise ValueError("Supabase no ha confirmado la identidad.")

        metadata = getattr(usuario, "user_metadata", {}) or {}
        email_real = (getattr(usuario, "email", "") or "").strip().lower()
        base = re.sub(r"[^a-z0-9_]", "_", email_real.split("@")[0])
        base = base.strip("_")[:14] or "motero"
        username_propuesto = (base + "_" + usuario.id.replace("-", "")[:8])[:24]
        username = metadata.get("username") or username_propuesto

        # Si existe el perfil, se respeta su nombre. Si no, se intenta crearlo.
        # La tabla puede tener un trigger de creación automática: en ese caso
        # no se duplica el registro.
        try:
            perfil = (
                supabase.table("profiles")
                .select("username")
                .eq("id", usuario.id)
                .maybe_single()
                .execute()
            )
            if perfil.data:
                username = perfil.data.get("username") or username
                if not perfil.data.get("username"):
                    supabase.table("profiles").update({
                        "username": username
                    }).eq("id", usuario.id).execute()
            else:
                supabase.table("profiles").insert({
                    "id": usuario.id,
                    "username": username,
                    "email_contacto": email_real,
                    "avisos_email": False
                }).execute()
        except Exception:
            # No bloquear una autenticación válida por permisos RLS del perfil.
            pass

        st.session_state["access_token"] = access_token
        st.session_state["refresh_token"] = refresh_token
        st.session_state["user_id"] = usuario.id
        st.session_state["username"] = username
        st.session_state["seccion_activa"] = "menu"
        st.query_params.clear()
        st.rerun()

    except HTTPError as error:
        st.query_params.clear()
        return "No se ha podido completar el acceso con Google (HTTP {}).".format(error.code)
    except Exception:
        st.query_params.clear()
        return "No se ha podido completar el acceso con Google. Inténtalo de nuevo."



IMAGEN_PREDETERMINADA = (
    "https://images.unsplash.com/photo-1558981806-ec527fa84c39"
    "?auto=format&fit=crop&w=1000&q=80"
)

LOGO_URL = (
    "https://nwjnludwqpopcqksntxz.supabase.co/"
    "storage/v1/object/public/familybike/"
    "316e4e3c-b185-459b-b5d2-944d34cad79e.jpeg"
)


# =========================================================
# DISEÑO FAMILY BIKE: NEGRO Y AMARILLO
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --negro: #000000;
    --negro-card: #101010;
    --negro-hover: #1B1B1B;
    --amarillo: #FFD400;
    --amarillo-claro: #FFE45C;
    --amarillo-oscuro: #DDB600;
    --borde: #806B00;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #000000 !important;
    color: #FFD400 !important;
    font-family: 'Inter', sans-serif !important;
}

header[data-testid="stHeader"] {
    background: #000000 !important;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp li,
.stApp small,
.stApp strong,
.stApp em,
.stApp b,
.stApp div,
.stMarkdown,
.stMarkdown p,
.stMarkdown span,
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
}

.hero {
    background: linear-gradient(110deg, #000000, #171717);
    border: 1px solid #FFD400;
    border-radius: 22px;
    padding: 35px;
    margin-bottom: 30px;
    text-align: center;
}

.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 34px;
    font-weight: 800;
    color: #FFD400 !important;
    margin: 25px 0 5px 0;
}

.section-subtitle {
    color: #FFD400 !important;
    font-size: 14px;
    margin-bottom: 22px;
}

.route-card,
.event-card,
.garaje-card,
.community-card,
.stat-box,
.tienda-card {
    background: #101010 !important;
    border: 1px solid #806B00 !important;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 18px;
    color: #FFD400 !important;
}

.route-number {
    color: #FFD400 !important;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.route-name {
    color: #FFD400 !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    font-weight: 700;
    margin: 12px 0;
}

.stat-box {
    text-align: center;
}

.stat-number {
    color: #FFD400 !important;
    font-size: 30px;
    font-weight: 800;
}

.stat-label {
    color: #FFD400 !important;
    font-size: 12px;
    letter-spacing: 1px;
}

.garaje-titulo,
.community-name {
    color: #FFD400 !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    font-weight: 800;
}

.garaje-subtitulo,
.community-label {
    color: #FFD400 !important;
    font-size: 14px;
}

.community-name,
.community-label {
    text-align: center;
}

.tienda-card {
    background: linear-gradient(135deg, #101010, #1B1B1B) !important;
    border: 1px solid #FFD400 !important;
    text-align: center;
}

.tienda-titulo {
    color: #FFD400 !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 32px;
    font-weight: 800;
}

.tienda-texto {
    color: #FFD400 !important;
    font-size: 16px;
    margin-top: 12px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
input,
textarea {
    background: #101010 !important;
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    border: 1px solid #806B00 !important;
    border-radius: 9px !important;
    caret-color: #FFD400 !important;
}

input::placeholder,
textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
    color: #B99B00 !important;
    -webkit-text-fill-color: #B99B00 !important;
    opacity: 1 !important;
}

div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-baseweb="menu"],
li[data-baseweb="menu"] {
    background: #101010 !important;
    color: #FFD400 !important;
}

div[data-baseweb="select"] *,
div[data-baseweb="menu"] *,
div[data-baseweb="popover"] * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

div[data-testid="stTimeInput"],
div[data-testid="stDateInput"],
div[data-testid="stTimeInput"] *,
div[data-testid="stDateInput"] *,
div[data-testid="stDatePicker"],
div[data-testid="stDatePicker"] *,
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    background-color: #101010 !important;
}

div[data-baseweb="calendar"],
div[data-baseweb="calendar"] *,
div[data-baseweb="popover"] {
    background: #101010 !important;
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

div[data-baseweb="calendar"] button {
    color: #FFD400 !important;
}

div[data-testid="stRadio"] *,
div[data-testid="stCheckbox"] *,
div[data-testid="stToggle"] * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

.stButton > button,
.stFormSubmitButton > button,
.stLinkButton > a {
    background: #FFD400 !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    border: 1px solid #FFD400 !important;
    border-radius: 9px !important;
    font-weight: 800 !important;
}

.stButton > button *,
.stFormSubmitButton > button *,
.stLinkButton > a * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stLinkButton > a:hover {
    background: #DDB600 !important;
    border-color: #DDB600 !important;
}

div[data-testid="stButton"] button[kind="secondary"] {
    min-height: 86px !important;
    width: 100% !important;
    white-space: normal !important;
    border-radius: 15px !important;
    font-size: 19px !important;
    line-height: 1.25 !important;
    font-weight: 800 !important;
    border: 1px solid #FFD400 !important;
    background: #101010 !important;
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    padding: 15px 10px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 8px rgba(255, 212, 0, 0.10);
}

div[data-testid="stButton"] button[kind="secondary"] * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: #242000 !important;
    border: 2px solid #FFD400 !important;
    transform: translateY(-2px);
}

button[data-baseweb="tab"] {
    color: #FFD400 !important;
    background: #000000 !important;
}

button[data-baseweb="tab"] * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #FFD400 !important;
}

div[data-testid="stExpander"] {
    background: #101010 !important;
    border: 1px solid #806B00 !important;
    border-radius: 10px !important;
}

div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary * {
    background: #101010 !important;
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

div[data-testid="stForm"] {
    background: #101010 !important;
    border: 1px solid #806B00 !important;
    border-radius: 12px !important;
    padding: 18px;
}

div[data-testid="stAlert"] {
    background: #101010 !important;
    border: 1px solid #FFD400 !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
}

div[data-testid="stAlert"] *,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

div[data-testid="stAlert"][kind="error"] {
    background: #180000 !important;
    border: 1px solid #FF4545 !important;
}

div[data-testid="stAlert"][kind="error"] * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

div[data-testid="stAlert"][kind="success"] {
    background: #101010 !important;
    border: 1px solid #FFD400 !important;
}

div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] * {
    background-color: #101010 !important;
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    border-color: #806B00 !important;
}

div[data-testid="stFileUploader"] button {
    background: #FFD400 !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

a, a:visited {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

img {
    border-radius: 10px;
}

hr {
    border-color: #806B00 !important;
}

.footer,
.footer * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    background: #000000 !important;
}

.footer {
    text-align: center;
    border-top: 1px solid #806B00;
    padding-top: 25px;
    margin-top: 50px;
    font-size: 12px;
}

.menu-intro {
    text-align: center;
    background: linear-gradient(135deg, #101010, #1B1B1B);
    border: 1px solid #806B00;
    border-radius: 18px;
    padding: 22px 15px;
    margin: 22px 0;
}

.menu-intro-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #FFD400 !important;
}

.menu-intro-text {
    color: #D8D8D8 !important;
    font-size: 14px;
    margin-top: 6px;
}

.news-card {
    background: linear-gradient(135deg, #171500, #101010);
    border: 1px solid #FFD400;
    border-left: 5px solid #FFD400;
    border-radius: 13px;
    padding: 18px;
    margin: 12px 0 20px 0;
}

.news-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    font-weight: 800;
    color: #FFD400;
}

.admin-info {
    background: #101010;
    border: 1px solid #806B00;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
}

@media (max-width: 600px) {
    .block-container {
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        padding-top: 1rem;
    }

    .section-title {
        font-size: 29px;
    }

    div[data-testid="stButton"] button[kind="secondary"] {
        min-height: 82px !important;
        font-size: 16px !important;
        padding: 12px 6px !important;
    }

    .menu-intro-title {
        font-size: 28px;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCIONES GENERALES
# =========================================================

def email_interno(username):
    return f"{username}@{AUTH_DOMAIN}"


def email_valido(email):
    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email.strip()
        )
    )


def escapar(valor):
    return html.escape(str(valor or ""))


def guardar_sesion(response, username):
    session = getattr(response, "session", None)

    if session is None:
        return False

    st.session_state["access_token"] = session.access_token
    st.session_state["refresh_token"] = session.refresh_token
    st.session_state["username"] = username

    user = getattr(response, "user", None)

    if user is None:
        user = getattr(session, "user", None)

    if user is not None:
        st.session_state["user_id"] = user.id

    return True


def guardar_datos_contacto(user_id, email_contacto, avisos_email):
    return (
        supabase.table("profiles")
        .update({
            "email_contacto": email_contacto.strip().lower(),
            "avisos_email": bool(avisos_email)
        })
        .eq("id", user_id)
        .execute()
    )


def cerrar_sesion():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    for key in [
        "access_token",
        "refresh_token",
        "username",
        "user_id",
        "seccion_activa"
    ]:
        st.session_state.pop(key, None)


def subir_archivo_storage(archivo, carpeta, prefijo):
    extension = archivo.name.rsplit(".", 1)[-1].lower()

    nombre_archivo = (
        f"{carpeta}/"
        f"{prefijo}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        f".{extension}"
    )

    supabase.storage.from_(BUCKET_FAMILYBIKE).upload(
        nombre_archivo,
        archivo.getvalue(),
        file_options={
            "content-type": archivo.type,
            "upsert": "false"
        }
    )

    resultado_url = (
        supabase.storage
        .from_(BUCKET_FAMILYBIKE)
        .get_public_url(nombre_archivo)
    )

    if isinstance(resultado_url, dict):
        url = (
            resultado_url.get("publicUrl")
            or resultado_url.get("publicURL")
        )
    else:
        url = str(resultado_url)

    if not url or not url.startswith("http"):
        raise ValueError(
            "Supabase no ha devuelto la dirección pública del archivo."
        )

    return url


# =========================================================
# PROPUESTAS DE RUTAS DE LA COMUNIDAD
# =========================================================

def enlace_google_maps_valido(url):
    """Acepta enlaces HTTPS oficiales de Google Maps, sin redirecciones externas."""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        return (
            parsed.scheme == "https"
            and not parsed.username
            and not parsed.password
            and host in {
                "www.google.com", "google.com", "maps.google.com",
                "maps.app.goo.gl", "goo.gl", "www.google.es", "google.es"
            }
            and bool(parsed.path and parsed.path != "/")
        )
    except (ValueError, AttributeError):
        return False


# =========================================================
# FUNCIONES DE ADMINISTRACIÓN
# =========================================================

def comprobar_es_admin(user_id):
    """
    Comprueba los permisos consultando familybike_admins.
    No utiliza nombres de usuario ni identificadores fijos.
    """
    try:
        respuesta = (
            supabase.table("familybike_admins")
            .select("user_id")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        return bool(respuesta.data)

    except Exception:
        return False


def obtener_ruta_storage(url, carpeta_permitida=None):
    """
    Obtiene la ruta interna de un archivo únicamente si pertenece
    al bucket FAMILY BIKE de este proyecto.

    Nunca elimina archivos de URLs externas.
    """
    if not isinstance(url, str) or not url.startswith("https://"):
        return None

    try:
        parsed = urlparse(url)

        host_esperado = urlparse(SUPABASE_URL).netloc

        if parsed.netloc != host_esperado:
            return None

        prefijo = f"/storage/v1/object/public/{BUCKET_FAMILYBIKE}/"

        if not parsed.path.startswith(prefijo):
            return None

        ruta = unquote(parsed.path[len(prefijo):])

        if not ruta:
            return None

        if carpeta_permitida and not ruta.startswith(carpeta_permitida):
            return None

        return ruta

    except Exception:
        return None


def eliminar_archivo_storage(url, carpeta_permitida=None):
    """
    Elimina un archivo de Storage solo cuando la URL corresponde
    al bucket y carpeta autorizados.
    """
    ruta = obtener_ruta_storage(
        url,
        carpeta_permitida=carpeta_permitida
    )

    if not ruta:
        return False

    supabase.storage.from_(BUCKET_FAMILYBIKE).remove([ruta])
    return True


def cargar_noticias_activas():
    respuesta = (
        supabase.table("familybike_noticias")
        .select(
            "id,titulo,contenido,activo,fijado,created_at"
        )
        .eq("activo", True)
        .order("fijado", desc=True)
        .order("created_at", desc=True)
        .execute()
    )

    return respuesta.data or []


def eliminar_quedada_completa(quedada):
    """
    Elimina los registros relacionados con una quedada:
    notificaciones, asistentes, horarios y finalmente la quedada.
    También elimina sus imágenes propias del bucket.
    """
    qid = quedada.get("id")

    if not qid:
        raise ValueError("La quedada no tiene identificador.")

    # 1. Notificaciones asociadas
    (
        supabase.table("notificaciones_quedadas")
        .delete()
        .eq("quedada_id", qid)
        .execute()
    )

    # 2. Inscripciones y asistentes
    (
        supabase.table("asistentes")
        .delete()
        .eq("quedada_id", qid)
        .execute()
    )

    # 3. Horarios
    (
        supabase.table("horarios_quedadas")
        .delete()
        .eq("quedada_id", qid)
        .execute()
    )

    # 4. Eliminar quedada
    (
        supabase.table("quedadas")
        .delete()
        .eq("id", qid)
        .execute()
    )

    # 5. Eliminar las fotografías propias de la quedada.
    # Las imágenes externas y las del catálogo no se eliminan.
    urls = {
        quedada.get("cartel_url"),
        quedada.get("imagen_url")
    }

    for url in urls:
        if url:
            try:
                eliminar_archivo_storage(
                    url,
                    carpeta_permitida="quedadas/"
                )
            except Exception:
                # La quedada ya está eliminada. Un fallo de Storage
                # no debe ocultar ese resultado.
                pass


def eliminar_foto_garaje(perfil):
    """
    Elimina la foto de moto del usuario y limpia su perfil.
    """
    user_id = perfil.get("id")
    foto_url = perfil.get("moto_foto_url")

    if not user_id:
        raise ValueError("No se ha encontrado el usuario.")

    if foto_url:
        eliminar_archivo_storage(
            foto_url,
            carpeta_permitida="garaje/"
        )

    (
        supabase.table("profiles")
        .update({"moto_foto_url": None})
        .eq("id", user_id)
        .execute()
    )


# =========================================================
# NOTIFICACIONES
# =========================================================

def crear_notificaciones_quedada(quedada_id, creador_id):

    if not quedada_id:
        raise ValueError("No se ha recibido el ID de la quedada.")

    respuesta_perfiles = (
        supabase.table("profiles")
        .select("id,email_contacto,avisos_email")
        .eq("avisos_email", True)
        .execute()
    )

    perfiles = respuesta_perfiles.data or []
    notificaciones = []

    ahora_utc = datetime.now(timezone.utc).isoformat()

    for perfil in perfiles:

        profile_id = perfil.get("id")

        if profile_id == creador_id:
            continue

        email_destino = (
            perfil.get("email_contacto") or ""
        ).strip().lower()

        if not email_valido(email_destino):
            continue

        notificaciones.append({
            "quedada_id": quedada_id,
            "profile_id": profile_id,
            "email_destino": email_destino,
            "estado": "pendiente",
            "intentos": 0,
            "proximo_intento": ahora_utc
        })

    if not notificaciones:
        return {
            "creadas": 0,
            "omitidas": len(perfiles)
        }

    respuesta_insert = (
        supabase.table("notificaciones_quedadas")
        .insert(notificaciones)
        .execute()
    )

    creadas = len(respuesta_insert.data or [])

    return {
        "creadas": creadas,
        "omitidas": len(perfiles) - creadas
    }


# =========================================================
# FUNCIONES DE RUTAS
# =========================================================

def numero_ruta(ruta):
    nombre = str(ruta.get("nombre", "")).strip()

    coincidencia = re.search(
        r"\bruta\s*#?\s*(\d+)",
        nombre,
        re.IGNORECASE
    )

    if coincidencia:
        return int(coincidencia.group(1))

    return None


def ordenar_rutas(lista_rutas):
    return sorted(
        lista_rutas,
        key=lambda ruta: (
            numero_ruta(ruta) is None,
            numero_ruta(ruta)
            if numero_ruta(ruta) is not None
            else 999999,
            str(ruta.get("nombre", "")).lower()
        )
    )


# El callback de Google debe procesarse antes de restaurar la sesión.
error_acceso_google = completar_google_oauth()


# =========================================================
# RESTAURAR SESIÓN
# =========================================================

autenticado = False

if (
    st.session_state.get("access_token")
    and st.session_state.get("refresh_token")
):
    try:

        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"]
        )

        respuesta_usuario = supabase.auth.get_user()
        usuario_actual = respuesta_usuario.user

        st.session_state["user_id"] = usuario_actual.id

        if not st.session_state.get("username"):

            metadata = getattr(
                usuario_actual,
                "user_metadata",
                {}
            ) or {}

            st.session_state["username"] = metadata.get(
                "username",
                "motero"
            )

        autenticado = True

    except Exception:
        cerrar_sesion()


# =========================================================
# FAMILY BIKE · REDISEÑO MOBILE FIRST (SOLO PRESENTACIÓN)
# =========================================================
st.markdown("""
<style>
:root {
    --fb-bg:#101419;
    --fb-surface:#1b222b;
    --fb-card:#242c36;
    --fb-accent:#FFD400;
    --fb-text:#f5f7fb;
    --fb-muted:#b7c0cd;
    --fb-line:#35404d;
}
html,body,.stApp,[data-testid="stAppViewContainer"],
[data-testid="stMain"],[data-testid="stMainBlockContainer"],
header[data-testid="stHeader"] {
    background:var(--fb-bg)!important;
}
.stApp,.stApp p,.stApp span,.stApp label,.stApp li,
.stApp small,.stApp strong,.stApp em,.stApp b,
.stApp div,.stMarkdown,.stMarkdown p,.stMarkdown span,
.stCaption,[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color:var(--fb-text)!important;
    -webkit-text-fill-color:var(--fb-text)!important;
}
h1,h2,h3,h4,h5,h6,.section-title,.route-name,
.garaje-titulo,.community-name,.tienda-titulo {
    color:var(--fb-text)!important;
    -webkit-text-fill-color:var(--fb-text)!important;
}
.section-subtitle,.menu-intro-text,.garaje-subtitulo,
.community-label,.stat-label,.tienda-texto,
[data-testid="stCaptionContainer"] p {
    color:var(--fb-muted)!important;
    -webkit-text-fill-color:var(--fb-muted)!important;
}
.block-container {
    max-width:1050px!important;
    padding-top:1rem!important;
    padding-bottom:2rem!important;
}
.hero,.menu-intro {
    background:linear-gradient(130deg,#222d39,#111820)!important;
    border:1px solid var(--fb-line)!important;
    border-radius:20px!important;
    padding:22px!important;
    margin-bottom:16px!important;
    text-align:left!important;
}
.menu-intro-title {font-size:clamp(22px,5vw,35px)!important;line-height:1.08!important}
.route-card,.event-card,.garaje-card,.community-card,.stat-box,
.tienda-card,.news-card {
    background:var(--fb-surface)!important;
    border:1px solid var(--fb-line)!important;
    border-radius:16px!important;
    padding:14px!important;
    margin-bottom:12px!important;
}
.route-number,.stat-number {color:var(--fb-accent)!important;-webkit-text-fill-color:var(--fb-accent)!important}
div[data-testid="stButton"] button[kind="secondary"] {
    min-height:64px!important;
    border-radius:14px!important;
    background:var(--fb-card)!important;
    border:1px solid var(--fb-line)!important;
    color:var(--fb-text)!important;
    -webkit-text-fill-color:var(--fb-text)!important;
    font-size:clamp(12px,3.5vw,16px)!important;
    padding:12px 8px!important;
    box-shadow:none!important;
}
div[data-testid="stButton"] button[kind="secondary"] * {
    color:var(--fb-text)!important;
    -webkit-text-fill-color:var(--fb-text)!important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    background:#303b49!important;
    border-color:var(--fb-accent)!important;
    transform:none!important;
}
.stButton>button[kind="primary"],
.stFormSubmitButton>button,.stLinkButton>a {
    background:var(--fb-accent)!important;
    border-color:var(--fb-accent)!important;
    color:#111820!important;
    -webkit-text-fill-color:#111820!important;
}
.stFormSubmitButton>button *,.stLinkButton>a * {
    color:#111820!important;-webkit-text-fill-color:#111820!important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
input,textarea {
    background:#202833!important;
    color:var(--fb-text)!important;
    -webkit-text-fill-color:var(--fb-text)!important;
    border:1px solid var(--fb-line)!important;
    caret-color:var(--fb-accent)!important;
}
input::placeholder,textarea::placeholder {
    color:var(--fb-muted)!important;
    -webkit-text-fill-color:var(--fb-muted)!important;
}
div[data-testid="stExpander"],div[data-testid="stForm"] {
    background:var(--fb-surface)!important;
    border:1px solid var(--fb-line)!important;
    border-radius:14px!important;
}
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary * {
    background:var(--fb-surface)!important;
    color:var(--fb-text)!important;
    -webkit-text-fill-color:var(--fb-text)!important;
}
button[data-baseweb="tab"] {background:transparent!important;color:var(--fb-text)!important}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom:3px solid var(--fb-accent)!important;
}
div[data-testid="stImage"] img {
    border-radius:12px!important;
    object-fit:cover!important;
    max-height:185px!important;
    width:100%!important;
}
div[data-testid="stAlert"] {background:#202833!important;border-color:var(--fb-line)!important}
div[data-testid="stAlert"] * {color:var(--fb-text)!important;-webkit-text-fill-color:var(--fb-text)!important}
@media(max-width:640px) {
    .block-container {padding-left:12px!important;padding-right:12px!important}
    [data-testid="stHorizontalBlock"] {gap:8px!important}
    .hero,.menu-intro {padding:16px!important}
    .section-title {font-size:26px!important}
    .route-name,.garaje-titulo,.community-name {font-size:20px!important}
    .route-card,.event-card,.garaje-card,.community-card {padding:12px!important}
    div[data-testid="stImage"] img {max-height:135px!important}
    div[data-testid="stButton"] button[kind="secondary"] {
        min-height:66px!important;font-size:12px!important;line-height:1.3!important
    }
    div[data-testid="stForm"] {padding:10px!important}
}
</style>
""",unsafe_allow_html=True)


# =========================================================
# FAMILY BIKE · IDENTIDAD VISUAL EN ACCESO Y REGISTRO
# =========================================================
st.markdown("""
<style>
/* Mantiene el logotipo original amarillo de FAMILY BIKE. */
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) {
    max-width: 680px !important;
}
.fb-login-marker {display:none}
/* Tarjetas de autenticación con la misma paleta del panel de usuario. */
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) [data-testid="stTabs"] {
    background:#1b222b!important;
    border:1px solid #35404d!important;
    border-radius:18px!important;
    padding:12px!important;
}
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) [data-testid="stForm"] {
    background:#242c36!important;
    border:1px solid #35404d!important;
    border-radius:14px!important;
    padding:16px!important;
}
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) button[data-baseweb="tab"][aria-selected="true"] {
    color:#FFD400!important;
    -webkit-text-fill-color:#FFD400!important;
}
/* El icono oficial multicolor de Google es un SVG embebido, sin dependencias externas. */
.st-key-fb_google_login a, .st-key-fb_google_registro a {
    display:flex!important;
    justify-content:center!important;
    align-items:center!important;
    gap:12px!important;
    background:#ffffff!important;
    color:#202124!important;
    -webkit-text-fill-color:#202124!important;
    border:1px solid #dadce0!important;
    border-radius:12px!important;
    font-weight:700!important;
    min-height:52px!important;
    text-decoration:none!important;
}
.st-key-fb_google_login a *, .st-key-fb_google_registro a * {
    color:#202124!important;
    -webkit-text-fill-color:#202124!important;
}
.st-key-fb_google_login a::before, .st-key-fb_google_registro a::before {
    content:"";
    width:21px;
    height:21px;
    flex-shrink:0;
    display:inline-block;
    background-image:url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"%3E%3Cpath fill="%23EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/%3E%3Cpath fill="%234285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.25 5.48-4.75 7.18l7.73 6C44.43 38.03 46.98 31.88 46.98 24.55z"/%3E%3Cpath fill="%23FBBC05" d="M10.53 28.59A14.41 14.41 0 0 1 9.75 24c0-1.59.27-3.13.76-4.59l-7.98-6.19A23.9 23.9 0 0 0 0 24c0 3.87.93 7.51 2.56 10.78l7.97-6.19z"/%3E%3Cpath fill="%2334A853" d="M24 48c6.48 0 11.93-2.13 15.91-5.8l-7.73-6C30.03 37.65 27.28 38.5 24 38.5c-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/%3E%3C/svg%3E');
    background-repeat:no-repeat;
    background-size:contain;
}
@media(max-width:640px) {
    [data-testid="stMainBlockContainer"]:has(.fb-login-marker) [data-testid="stTabs"] {padding:8px!important}
    [data-testid="stMainBlockContainer"]:has(.fb-login-marker) [data-testid="stForm"] {padding:12px!important}
}
</style>
""",unsafe_allow_html=True)



# Estilo de acceso antes del renderizado, incluso cuando st.stop() corta la página.
st.markdown("""<style>
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) {max-width:720px!important;}
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) .st-key-fb_google_login a,
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) .st-key-fb_google_registro a {background:#fff!important;border:1px solid #dadce0!important;color:#202124!important;-webkit-text-fill-color:#202124!important;}
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) .st-key-fb_google_login a:hover,
[data-testid="stMainBlockContainer"]:has(.fb-login-marker) .st-key-fb_google_registro a:hover {background:#f1f3f4!important;}
</style>""",unsafe_allow_html=True)

st.markdown("""<style>
.fb-logo-acceso {
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    width:100%!important;
    margin:8px auto 20px!important;
}
.fb-logo-acceso img {
    display:block!important;
    width:min(100%, 340px)!important;
    height:auto!important;
    max-height:190px!important;
    object-fit:contain!important;
    margin:0 auto!important;
}
@media(max-width:640px) {
    .fb-logo-acceso {margin:12px auto 22px!important;}
    .fb-logo-acceso img {width:min(86vw, 290px)!important;max-height:175px!important;}
}
</style>""", unsafe_allow_html=True)

# =========================================================
# ACCESO Y REGISTRO
# =========================================================

if not autenticado:

    st.markdown('<span class="fb-login-marker"></span>', unsafe_allow_html=True)

    # Logo original centrado y ampliado en móvil y escritorio.
    st.markdown(
        '<div class="fb-logo-acceso">'
        f'<img src="{LOGO_URL}" alt="FAMILY BIKE">'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">ACCESO A FAMILY BIKE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Regístrate o inicia sesión para descubrir nuestras rutas.'
        '</div>',
        unsafe_allow_html=True
    )

    if error_acceso_google:
        st.error(error_acceso_google)

    tab_login, tab_registro = st.tabs([
        "INICIAR SESIÓN",
        "CREAR CUENTA"
    ])

    with tab_login:

        st.link_button(
            "INICIAR SESIÓN CON GOOGLE",
            iniciar_google_oauth(),
            use_container_width=True,
            key="fb_google_login"
        )
        st.caption("O entra con tu usuario y contraseña de siempre.")

        with st.form("form_login"):

            usuario_login = st.text_input(
                "Nombre de usuario",
                placeholder="Tu nombre de usuario"
            )

            password_login = st.text_input(
                "Contraseña",
                type="password"
            )

            boton_login = st.form_submit_button(
                "ENTRAR",
                use_container_width=True
            )

        if boton_login:

            username = usuario_login.strip().lower()

            if not username or not password_login:

                st.error("Introduce tu usuario y contraseña.")

            elif not re.fullmatch(r"[a-z0-9_]{3,24}", username):

                st.error("El nombre de usuario no es válido.")

            else:

                try:

                    response = supabase.auth.sign_in_with_password({
                        "email": email_interno(username),
                        "password": password_login
                    })

                    if guardar_sesion(response, username):
                        st.session_state["seccion_activa"] = "menu"
                        st.success("Sesión iniciada correctamente.")
                        st.rerun()
                    else:
                        st.error(
                            "Supabase no ha devuelto una sesión."
                        )

                except Exception:
                    st.error(
                        "Usuario o contraseña incorrectos. "
                        "Comprueba tus datos e inténtalo de nuevo."
                    )

    with tab_registro:

        st.link_button(
            "CREAR CUENTA CON GOOGLE",
            iniciar_google_oauth(),
            use_container_width=True,
            key="fb_google_registro"
        )
        st.caption("O crea tu cuenta con usuario y contraseña.")

        st.caption(
            "El correo indicado será tu dirección de contacto. "
            "Seguirás accediendo con tu nombre de usuario y contraseña."
        )

        with st.form("form_registro"):

            nuevo_usuario = st.text_input(
                "Elige un nombre de usuario",
                placeholder="Ejemplo: motero_01"
            )

            email_contacto = st.text_input(
                "Tu correo electrónico real",
                placeholder="nombre@ejemplo.com"
            )

            nueva_password = st.text_input(
                "Elige una contraseña",
                type="password"
            )

            repetir_password = st.text_input(
                "Repite la contraseña",
                type="password"
            )

            aceptar_avisos = st.checkbox(
                "Acepto recibir por correo electrónico avisos "
                "de nuevas rutas y novedades de FAMILY BIKE."
            )

            boton_registro = st.form_submit_button(
                "CREAR CUENTA",
                use_container_width=True
            )

        if boton_registro:

            username = nuevo_usuario.strip().lower()
            email_real = email_contacto.strip().lower()

            if not re.fullmatch(r"[a-z0-9_]{3,24}", username):

                st.error(
                    "El usuario debe tener entre 3 y 24 caracteres. "
                    "Utiliza letras, números o guion bajo."
                )

            elif not email_valido(email_real):

                st.error(
                    "Introduce una dirección de correo electrónico válida."
                )

            elif len(nueva_password) < 8:

                st.error(
                    "La contraseña debe tener al menos 8 caracteres."
                )

            elif nueva_password != repetir_password:

                st.error("Las contraseñas no coinciden.")

            else:

                try:

                    response = supabase.auth.sign_up({
                        "email": email_interno(username),
                        "password": nueva_password,
                        "options": {
                            "data": {
                                "username": username
                            }
                        }
                    })

                    if guardar_sesion(response, username):

                        user_id_nuevo = st.session_state.get("user_id")

                        guardar_datos_contacto(
                            user_id_nuevo,
                            email_real,
                            aceptar_avisos
                        )

                        st.session_state["seccion_activa"] = "menu"

                        st.success(
                            "¡Cuenta creada correctamente! "
                            "Tus datos de contacto se han guardado."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Supabase ha recibido el registro, pero no ha "
                            "devuelto una sesión. Inicia sesión con tu usuario "
                            "y contraseña."
                        )

                except Exception as error:

                    st.error("ERROR AL CREAR LA CUENTA")
                    st.code(str(error))

    # -----------------------------------------------------
    # ACCESO DIRECTO A FACEBOOK
    # -----------------------------------------------------

    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                * { box-sizing: border-box; }

                body {
                    margin: 0;
                    padding: 10px 0;
                    background: transparent;
                    font-family: Arial, sans-serif;
                }

                .facebook-community {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 14px;
                    width: 100%;
                    padding: 15px 18px;
                    background: #101010;
                    border: 1px solid #1877F2;
                    border-radius: 14px;
                    text-decoration: none;
                    transition: background 0.2s ease;
                }

                .facebook-community:hover {
                    background: #1B1B1B;
                }

                .facebook-icon {
                    width: 42px;
                    height: 42px;
                    min-width: 42px;
                    display: block;
                }

                .facebook-copy {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                    text-align: left;
                }

                .facebook-title {
                    color: #FFD400;
                    font-size: 19px;
                    font-weight: 800;
                    letter-spacing: 0.4px;
                }

                .facebook-subtitle {
                    color: #C9C9C9;
                    font-size: 12px;
                    font-weight: 500;
                }

                .facebook-arrow {
                    color: #1877F2;
                    font-size: 24px;
                    font-weight: bold;
                    margin-left: auto;
                }

                @media (max-width: 600px) {
                    .facebook-community {
                        gap: 10px;
                        padding: 13px 10px;
                    }

                    .facebook-icon {
                        width: 36px;
                        height: 36px;
                        min-width: 36px;
                    }

                    .facebook-title { font-size: 16px; }
                    .facebook-subtitle { font-size: 10px; }
                }
            </style>
        </head>

        <body>
            <a class="facebook-community"
               href="https://m.facebook.com/groups/1646146103973952/?ref=share"
               target="_blank"
               rel="noopener noreferrer"
               aria-label="Abrir grupo de Facebook FAMILY BIKE">

                <svg class="facebook-icon"
                     xmlns="http://www.w3.org/2000/svg"
                     viewBox="0 0 48 48"
                     role="img"
                     aria-label="Facebook">

                    <circle cx="24" cy="24" r="24" fill="#1877F2"/>

                    <path
                        fill="#FFFFFF"
                        d="M27.6 40V26.1h4.7l.7-5.4h-5.4v-3.4
                        c0-1.6.5-2.7 2.7-2.7h2.9v-4.8
                        c-.5-.1-2.3-.2-4.3-.2
                        -4.3 0-7.3 2.6-7.3 7.5v3.6h-4.9v5.4h4.9V40z"
                    />
                </svg>

                <span class="facebook-copy">
                    <span class="facebook-title">
                        ÚNETE A NUESTRA COMUNIDAD
                    </span>
                    <span class="facebook-subtitle">
                        FAMILY BIKE · Grupo oficial de Facebook
                    </span>
                </span>

                <span class="facebook-arrow">↗</span>
            </a>
        </body>
        </html>
        """,
        height=100,
        scrolling=False
    )

    st.markdown("""
    <div class="footer">
        <strong>FAMILY BIKE</strong><br><br>
        CARRETERA · AVENTURA · LIBERTAD<br>
        © FAMILY BIKE
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# USUARIO AUTENTICADO
# =========================================================

usuario_id = st.session_state.get("user_id")
username_actual = st.session_state.get("username", "Motero")

if not usuario_id:
    st.error(
        "No se ha podido identificar tu usuario. "
        "Vuelve a iniciar sesión."
    )
    st.stop()

if "seccion_activa" not in st.session_state:
    st.session_state["seccion_activa"] = "menu"


# =========================================================
# COMPROBAR SI ES ADMINISTRADOR
# =========================================================

es_admin = comprobar_es_admin(usuario_id)

# Si alguien intenta entrar manualmente en administración
# sin estar registrado como administrador, se le devuelve al menú.
if (
    st.session_state.get("seccion_activa") == "administracion"
    and not es_admin
):
    st.session_state["seccion_activa"] = "menu"


# =========================================================
# CARGAR PERFIL
# =========================================================

perfil_garaje = {}
foto_moto_actual = None

try:

    respuesta_perfil = (
        supabase.table("profiles")
        .select("moto_foto_url,username")
        .eq("id", usuario_id)
        .maybe_single()
        .execute()
    )

    perfil_garaje = respuesta_perfil.data or {}
    foto_moto_actual = perfil_garaje.get("moto_foto_url")
    if perfil_garaje.get("username"):
        st.session_state["username"] = perfil_garaje["username"]
        username_actual = perfil_garaje["username"]

except Exception:
    st.warning(
        "No se ha podido cargar la fotografía del garaje."
    )


# =========================================================
# EDICIÓN DE PERFIL (GOOGLE Y USUARIO/CONTRASEÑA)
# =========================================================

if st.session_state.get("seccion_activa") == "perfil":
    st.markdown("## 👤 EDITAR MI PERFIL")
    st.info("Puedes cambiar tu nombre público sin cambiar tu cuenta de acceso ni perder tus rutas, garaje o permisos.")

    with st.form("formulario_editar_nombre", clear_on_submit=False):
        nombre_nuevo = st.text_input(
            "Nombre de usuario público",
            value=username_actual,
            max_chars=24,
            help="Entre 3 y 24 caracteres: letras minúsculas, números y guion bajo."
        )
        guardar_nombre = st.form_submit_button(
            "GUARDAR NOMBRE DE USUARIO", use_container_width=True
        )

    if guardar_nombre:
        nombre_nuevo = nombre_nuevo.strip().lower()
        if not re.fullmatch(r"[a-z0-9_]{3,24}", nombre_nuevo):
            st.error("El nombre debe tener entre 3 y 24 caracteres y solo letras minúsculas, números o guion bajo.")
        elif nombre_nuevo == username_actual:
            st.info("Ya estás utilizando ese nombre.")
        else:
            try:
                # Comprobación informativa; la unicidad definitiva debe
                # estar garantizada por una restricción UNIQUE en PostgreSQL.
                existe = (
                    supabase.table("profiles")
                    .select("id")
                    .eq("username", nombre_nuevo)
                    .limit(1)
                    .execute()
                )
                if any(fila.get("id") != usuario_id for fila in (existe.data or [])):
                    st.error("Ese nombre de usuario ya está ocupado. Elige otro.")
                else:
                    resultado = (
                        supabase.table("profiles")
                        .update({"username": nombre_nuevo})
                        .eq("id", usuario_id)
                        .select("id,username")
                        .execute()
                    )
                    filas = resultado.data or []
                    if not filas or filas[0].get("username") != nombre_nuevo:
                        st.error("No se ha podido actualizar el perfil. Revisa las políticas RLS de Supabase.")
                    else:
                        st.session_state["username"] = nombre_nuevo
                        st.session_state["aviso_perfil_actualizado"] = True
                        st.rerun()
            except Exception as error:
                # Evitar mostrar detalles internos de la base de datos.
                if "23505" in str(error) or "duplicate key" in str(error).lower():
                    st.error("Ese nombre de usuario ya está ocupado.")
                else:
                    st.error("No se ha podido guardar el nombre. Comprueba la conexión y los permisos de tu perfil.")

    if st.session_state.pop("aviso_perfil_actualizado", False):
        st.success("Nombre de usuario actualizado correctamente. Tu cuenta sigue vinculada al mismo acceso.")

    st.caption("La fotografía de tu motocicleta se sigue gestionando desde MI GARAJE.")


# =========================================================
# CABECERA
# =========================================================

col_usuario, col_moto, col_salir = st.columns([2, 2, 1])

with col_usuario:

    st.markdown(
        f"""
        <div class="garaje-card">
            <div class="garaje-titulo">🏍️ FAMILY BIKE</div>
            <div class="garaje-subtitulo">
                Usuario: <strong>{escapar(username_actual)}</strong>
            </div>
            <div class="garaje-subtitulo">
                Bienvenido a FAMILY BIKE
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_moto:

    if foto_moto_actual:
        st.image(
            foto_moto_actual,
            caption="Tu motocicleta",
            use_container_width=True
        )
    else:
        st.markdown(
            """
            <div class="garaje-card">
                <div class="garaje-titulo">MI MOTOCICLETA</div>
                <div class="garaje-subtitulo">
                    Todavía no has añadido una fotografía.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with col_salir:

    if st.button("CERRAR SESIÓN", use_container_width=True):
        cerrar_sesion()
        st.rerun()


# =========================================================
# CARGAR RUTAS
# =========================================================

try:

    respuesta_rutas = (
        supabase.table("rutas")
        .select("id,nombre,url,imagen_url")
        .execute()
    )

    rutas = ordenar_rutas(respuesta_rutas.data or [])

    # Las propuestas solo son públicas tras aprobación.
    try:
        propuestas_aprobadas = (
            supabase.table("familybike_rutas_propuestas")
            .select("id,nombre,url")
            .eq("estado", "aprobada")
            .execute()
        ).data or []
        rutas = ordenar_rutas(
            rutas + [
                {"id": item["id"], "nombre": item["nombre"],
                 "url": item["url"], "imagen_url": IMAGEN_PREDETERMINADA}
                for item in propuestas_aprobadas
            ]
        )
    except Exception:
        # Mantener operativas las rutas originales si la tabla no existe aún.
        pass

except Exception as error:

    st.error("No se han podido cargar las rutas desde Supabase.")
    st.code(str(error))
    st.stop()


# =========================================================
# ESTADÍSTICAS
# =========================================================

try:

    respuesta_quedadas = (
        supabase.table("quedadas")
        .select("id", count="exact")
        .eq("estado", "abierta")
        .gte("fecha", date.today().isoformat())
        .execute()
    )

    total_quedadas = respuesta_quedadas.count or 0

except Exception:
    total_quedadas = 0


col1, col3 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-number">{len(rutas)}</div>
            <div class="stat-label">RUTAS DISPONIBLES</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-number">{total_quedadas}</div>
            <div class="stat-label">PRÓXIMAS QUEDADAS</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# NOTICIAS EN LA PÁGINA PRINCIPAL
# =========================================================

if st.session_state["seccion_activa"] == "menu":

    try:
        noticias_inicio = cargar_noticias_activas()

        if noticias_inicio:

            st.markdown(
                '<div class="section-title">📢 NOTICIAS FAMILY BIKE</div>',
                unsafe_allow_html=True
            )

            for noticia in noticias_inicio:

                titulo_noticia = escapar(noticia.get("titulo"))
                contenido_noticia = escapar(noticia.get("contenido"))

                st.markdown(
                    f"""
                    <div class="news-card">
                        <div class="news-title">
                            📢 {titulo_noticia}
                        </div>
                        <div style="margin-top:10px; white-space:pre-wrap;">
                            {contenido_noticia}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception:
        # La página principal sigue funcionando si las noticias
        # no están disponibles temporalmente.
        pass


# =========================================================
# MENÚ PRINCIPAL FAMILY BIKE
# =========================================================

if st.session_state["seccion_activa"] == "menu":

    st.markdown(
        """
        <div class="menu-intro">
            <div class="menu-intro-title">
                TU PRÓXIMA AVENTURA EMPIEZA AQUÍ
            </div>
            <div class="menu-intro-text">
                Descubre rutas, comparte kilómetros y conecta con la comunidad motera.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # FILA 1: RUTAS Y QUEDADAS
    menu_col1, menu_col2 = st.columns(2, gap="medium")

    with menu_col1:
        if st.button(
            "🏍️\nEXPLORAR RUTAS",
            key="menu_rutas",
            type="secondary",
            use_container_width=True
        ):
            st.session_state["seccion_activa"] = "rutas"
            st.rerun()

    with menu_col2:
        if st.button(
            "📅\nQUEDADAS MOTERAS",
            key="menu_quedadas",
            type="secondary",
            use_container_width=True
        ):
            st.session_state["seccion_activa"] = "quedadas"
            st.rerun()

    st.write("")

    # FILA 2: GARAJE Y COMUNIDAD
    menu_col3, menu_col4 = st.columns(2, gap="medium")

    with menu_col3:
        if st.button(
            "🏁\nMI GARAJE",
            key="menu_garaje",
            type="secondary",
            use_container_width=True
        ):
            st.session_state["seccion_activa"] = "garaje"
            st.rerun()

    with menu_col4:
        if st.button(
            "👥\nCOMUNIDAD",
            key="menu_comunidad",
            type="secondary",
            use_container_width=True
        ):
            st.session_state["seccion_activa"] = "comunidad"
            st.rerun()

    st.write("")

    # ACCESO DIRECTO A PROPONER UNA RUTA
    if st.button(
        "📍  SUBIR MI RUTA · GOOGLE MAPS",
        key="menu_subir_ruta",
        type="secondary",
        use_container_width=True
    ):
        st.session_state["abrir_propuesta_ruta"] = True
        st.session_state["seccion_activa"] = "rutas"
        st.rerun()

    # PERFIL PERSONAL
    if st.button(
        "👤  EDITAR MI PERFIL",
        key="menu_editar_perfil",
        type="secondary",
        use_container_width=True
    ):
        st.session_state["seccion_activa"] = "perfil"
        st.rerun()

    # FILA 3: TIENDA
    if st.button(
        "🛒  TIENDA FAMILY BIKE",
        key="menu_tienda",
        type="secondary",
        use_container_width=True
    ):
        st.session_state["seccion_activa"] = "tienda"
        st.rerun()

    # FILA 4: ADMINISTRACIÓN, SOLO PARA ADMINISTRADORES
    if es_admin:

        st.write("")

        if st.button(
            "⚙️  ADMINISTRACIÓN FAMILY BIKE",
            key="menu_administracion",
            type="secondary",
            use_container_width=True
        ):
            st.session_state["seccion_activa"] = "administracion"
            st.rerun()


# =========================================================
# NAVEGACIÓN: BOTÓN VOLVER AL MENÚ
# =========================================================

else:

    if st.button(
        "← VOLVER AL MENÚ PRINCIPAL",
        key="volver_menu",
        type="secondary",
        use_container_width=True
    ):
        st.session_state["seccion_activa"] = "menu"
        st.rerun()


# =========================================================
# SECCIÓN EXPLORAR RUTAS
# =========================================================

if st.session_state["seccion_activa"] == "rutas":

    st.markdown(
        '<div class="section-title">EXPLORA LAS RUTAS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Encuentra tu próximo destino y sal a disfrutar de la carretera.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.expander(
        "➕ COMPARTIR UNA RUTA DE GOOGLE MAPS",
        expanded=st.session_state.pop("abrir_propuesta_ruta", False)
    ):
        st.caption(
            "Comparte una ruta que hayas realizado. No se publicará "
            "hasta que un administrador la apruebe."
        )
        with st.form("form_proponer_ruta", clear_on_submit=True):
            nombre_propuesto = st.text_input(
                "Nombre de la ruta", max_chars=120,
                placeholder="Ej.: Ruta por la Sierra de Cádiz"
            )
            enlace_propuesto = st.text_input(
                "Enlace de Google Maps",
                placeholder="https://maps.app.goo.gl/..."
            )
            descripcion_propuesta = st.text_area(
                "Descripción (opcional)", max_chars=1000
            )
            enviar_propuesta = st.form_submit_button(
                "ENVIAR PARA REVISIÓN", use_container_width=True
            )

        if enviar_propuesta:
            if len(nombre_propuesto.strip()) < 3:
                st.error("Escribe un nombre de al menos 3 caracteres.")
            elif not enlace_google_maps_valido(enlace_propuesto):
                st.error("Introduce un enlace HTTPS válido de Google Maps.")
            else:
                try:
                    supabase.table("familybike_rutas_propuestas").insert({
                        "usuario_id": usuario_id,
                        "nombre": nombre_propuesto.strip(),
                        "url": enlace_propuesto.strip(),
                        "descripcion": descripcion_propuesta.strip(),
                    }).execute()
                    st.success("Ruta enviada. Está pendiente de aprobación.")
                except Exception as error:
                    st.error("No se ha podido enviar la ruta. Comprueba la configuración de Supabase.")
                    st.code(str(error))

        try:
            mis_propuestas = (
                supabase.table("familybike_rutas_propuestas")
                .select("nombre,estado")
                .eq("usuario_id", usuario_id)
                .order("created_at", desc=True)
                .limit(30)
                .execute()
            ).data or []
            if mis_propuestas:
                st.markdown("**Estado de tus propuestas**")
                for propuesta in mis_propuestas:
                    st.write(f"• {propuesta['nombre']} — {propuesta['estado']}")
        except Exception:
            pass

    busqueda = st.text_input(
        "Buscar ruta",
        placeholder="Escribe el nombre de una ruta...",
        key="buscar_ruta"
    )

    rutas_filtradas = [
        ruta for ruta in rutas
        if busqueda.lower() in ruta.get("nombre", "").lower()
    ]

    if not rutas:
        st.warning("Todavía no hay rutas disponibles.")

    elif not rutas_filtradas:
        st.info("No hay rutas que coincidan con tu búsqueda.")

    else:

        st.caption(f"Mostrando {len(rutas_filtradas)} rutas")

        columnas = st.columns(3)

        for indice, ruta in enumerate(rutas_filtradas):

            nombre = ruta.get("nombre", "Ruta sin nombre")
            url_original = ruta.get("url", "")
            imagen = ruta.get("imagen_url")

            if (
                not isinstance(imagen, str)
                or not imagen.startswith(("https://", "http://"))
            ):
                imagen = IMAGEN_PREDETERMINADA

            with columnas[indice % 3]:

                st.image(imagen, use_container_width=True)

                st.markdown(
                    f"""
                    <div class="route-card">
                        <div class="route-number">
                            RUTA {indice + 1:02d}
                        </div>
                        <div class="route-name">
                            {escapar(nombre)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if (
                    isinstance(url_original, str)
                    and url_original.startswith(("https://", "http://"))
                ):
                    st.link_button(
                        "VER RECORRIDO ↗",
                        url_original,
                        use_container_width=True
                    )


# =========================================================
# SECCIÓN QUEDADAS MOTERAS
# =========================================================

if st.session_state["seccion_activa"] == "quedadas":

    st.markdown(
        '<div class="section-title">QUEDADAS MOTERAS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Organiza una salida, invita a otros moteros y comparte carretera.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # CREAR QUEDADA
    # -----------------------------------------------------

    with st.expander("➕ CREAR UNA NUEVA QUEDADA", expanded=False):

        nombres_rutas = [
            ruta.get("nombre", "Ruta sin nombre")
            for ruta in rutas
        ]

        tipo_destino = st.radio(
            "¿Qué tipo de salida quieres organizar?",
            ["Ruta del catálogo", "Destino libre"],
            horizontal=True,
            key="tipo_destino_quedada"
        )

        ruta_elegida = ""
        destino_libre = ""

        if tipo_destino == "Ruta del catálogo":

            if nombres_rutas:

                ruta_elegida = st.selectbox(
                    "Selecciona una ruta",
                    nombres_rutas,
                    key="ruta_catalogo_quedada"
                )

            else:

                st.warning(
                    "No hay rutas en el catálogo. "
                    "Selecciona Destino libre para escribir tu destino."
                )

        else:

            destino_libre = st.text_input(
                "Escribe tu ruta o destino",
                placeholder="Ejemplo: Grazalema, Sierra de Cádiz...",
                key="destino_libre_quedada"
            )

        with st.form("form_nueva_quedada"):

            fecha_quedada = st.date_input(
                "Fecha de la quedada",
                value=date.today(),
                min_value=date.today(),
                format="DD/MM/YYYY"
            )

            hora_quedada = st.time_input(
                "Primera hora de salida",
                value=time(9, 0)
            )

            punto_encuentro = st.text_input(
                "Primer punto de encuentro",
                placeholder="Ejemplo: Gasolinera de San Fernando"
            )

            st.markdown("#### HORARIOS ADICIONALES")

            anadir_horario_2 = st.checkbox(
                "Añadir una segunda hora de salida"
            )

            hora_2 = st.time_input(
                "Segunda hora de salida",
                value=time(10, 0),
                key="hora_salida_2"
            )

            punto_2 = st.text_input(
                "Punto de encuentro de la segunda salida",
                placeholder="Ejemplo: Gasolinera de Cádiz",
                key="punto_salida_2"
            )

            anadir_horario_3 = st.checkbox(
                "Añadir una tercera hora de salida"
            )

            hora_3 = st.time_input(
                "Tercera hora de salida",
                value=time(11, 0),
                key="hora_salida_3"
            )

            punto_3 = st.text_input(
                "Punto de encuentro de la tercera salida",
                placeholder="Ejemplo: Área de servicio",
                key="punto_salida_3"
            )

            descripcion = st.text_area(
                "Descripción de la salida",
                placeholder=(
                    "Cuenta cómo será la ruta, kilómetros, "
                    "paradas, recomendaciones..."
                )
            )

            telefono_organizador = st.text_input(
                "Teléfono de contacto del organizador",
                placeholder="Ejemplo: 600123456"
            )

            cartel_quedada = st.file_uploader(
                "Subir cartel o fotografía de la quedada (opcional)",
                type=["jpg", "jpeg", "png", "webp"],
                key="cartel_quedada"
            )

            imagen_url_alternativa = st.text_input(
                "O URL de una fotografía (opcional)",
                placeholder="https://..."
            )

            publicar = st.form_submit_button(
                "PUBLICAR QUEDADA",
                use_container_width=True
            )

        if publicar:

            nombre_final = (
                ruta_elegida
                if tipo_destino == "Ruta del catálogo"
                else destino_libre.strip()
            )

            if not nombre_final:

                st.error("Introduce el nombre de la ruta o destino.")

            elif not punto_encuentro.strip():

                st.error("Indica el primer punto de encuentro.")

            elif anadir_horario_2 and not punto_2.strip():

                st.error(
                    "Indica el punto de encuentro de la segunda salida."
                )

            elif anadir_horario_3 and not punto_3.strip():

                st.error(
                    "Indica el punto de encuentro de la tercera salida."
                )

            elif (
                imagen_url_alternativa.strip()
                and not imagen_url_alternativa.strip().startswith(
                    ("https://", "http://")
                )
            ):

                st.error("La dirección de la fotografía no es válida.")

            else:

                try:

                    imagen_final = imagen_url_alternativa.strip()

                    if (
                        tipo_destino == "Ruta del catálogo"
                        and not imagen_final
                    ):

                        ruta_seleccionada = next(
                            (
                                r for r in rutas
                                if r.get("nombre") == nombre_final
                            ),
                            {}
                        )

                        imagen_final = (
                            ruta_seleccionada.get("imagen_url") or ""
                        )

                    cartel_url = ""

                    if cartel_quedada is not None:

                        cartel_url = subir_archivo_storage(
                            cartel_quedada,
                            f"quedadas/{usuario_id}",
                            "cartel"
                        )

                        imagen_final = cartel_url

                    elif imagen_final:
                        cartel_url = imagen_final

                    nueva_quedada = {
                        "creador_id": usuario_id,
                        "ruta_nombre": nombre_final,
                        "es_ruta_catalogo": (
                            tipo_destino == "Ruta del catálogo"
                        ),
                        "fecha": fecha_quedada.isoformat(),
                        "hora": hora_quedada.strftime("%H:%M:%S"),
                        "punto_encuentro": punto_encuentro.strip(),
                        "descripcion": descripcion.strip(),
                        "imagen_url": imagen_final,
                        "cartel_url": cartel_url,
                        "telefono_organizador": (
                            telefono_organizador.strip()
                        ),
                        "estado": "abierta"
                    }

                    respuesta_nueva = (
                        supabase.table("quedadas")
                        .insert(nueva_quedada)
                        .execute()
                    )

                    filas_guardadas = respuesta_nueva.data or []

                    if not filas_guardadas:
                        raise ValueError(
                            "Supabase no ha devuelto la quedada creada."
                        )

                    quedada_guardada = filas_guardadas[0]
                    quedada_id = quedada_guardada.get("id")

                    if not quedada_id:
                        raise ValueError(
                            "No se ha recibido el identificador de la quedada."
                        )

                    horarios = [
                        {
                            "quedada_id": quedada_id,
                            "hora": hora_quedada.strftime("%H:%M:%S"),
                            "punto_encuentro": punto_encuentro.strip()
                        }
                    ]

                    if anadir_horario_2:
                        horarios.append({
                            "quedada_id": quedada_id,
                            "hora": hora_2.strftime("%H:%M:%S"),
                            "punto_encuentro": punto_2.strip()
                        })

                    if anadir_horario_3:
                        horarios.append({
                            "quedada_id": quedada_id,
                            "hora": hora_3.strftime("%H:%M:%S"),
                            "punto_encuentro": punto_3.strip()
                        })

                    respuesta_horarios = (
                        supabase.table("horarios_quedadas")
                        .insert(horarios)
                        .execute()
                    )

                    if len(respuesta_horarios.data or []) != len(horarios):
                        st.warning(
                            "La quedada se ha creado, pero comprueba "
                            "que se hayan guardado todos los horarios."
                        )

                    st.success("¡Quedada publicada correctamente!")

                    try:

                        resultado_avisos = crear_notificaciones_quedada(
                            quedada_id,
                            usuario_id
                        )

                        creadas = resultado_avisos["creadas"]

                        if creadas > 0:
                            st.success(
                                f"📬 Se han registrado {creadas} "
                                "notificaciones pendientes."
                            )
                        else:
                            st.info(
                                "No hay usuarios con avisos activados "
                                "y correo válido."
                            )

                    except Exception as error_avisos:

                        st.warning(
                            "La quedada se ha publicado, pero no se han "
                            "podido crear las notificaciones."
                        )

                        st.code(str(error_avisos))

                    st.rerun()

                except Exception as error:

                    st.error("No se ha podido publicar la quedada.")
                    st.code(str(error))


    # -----------------------------------------------------
    # CARGAR QUEDADAS
    # -----------------------------------------------------

    try:

        respuesta_quedadas = (
            supabase.table("quedadas")
            .select(
                "id,creador_id,ruta_nombre,es_ruta_catalogo,"
                "fecha,hora,punto_encuentro,descripcion,"
                "imagen_url,cartel_url,telefono_organizador,"
                "estado,created_at"
            )
            .eq("estado", "abierta")
            .gte("fecha", date.today().isoformat())
            .order("fecha")
            .execute()
        )

        quedadas = respuesta_quedadas.data or []

    except Exception as error:

        st.error("No se han podido cargar las quedadas.")
        st.code(str(error))
        quedadas = []


    # -----------------------------------------------------
    # CARGAR HORARIOS
    # -----------------------------------------------------

    horarios_por_quedada = {}

    if quedadas:

        ids_quedadas = [q["id"] for q in quedadas]

        try:

            respuesta_horarios = (
                supabase.table("horarios_quedadas")
                .select("id,quedada_id,hora,punto_encuentro")
                .in_("quedada_id", ids_quedadas)
                .order("hora")
                .execute()
            )

            for horario in respuesta_horarios.data or []:

                horarios_por_quedada.setdefault(
                    horario["quedada_id"],
                    []
                ).append(horario)

        except Exception as error:

            st.warning(
                "No se han podido cargar los horarios adicionales."
            )
            st.code(str(error))


    # -----------------------------------------------------
    # CARGAR ASISTENTES Y PERFILES
    # -----------------------------------------------------

    asistentes_por_quedada = {}
    perfiles_usuarios = {}

    if quedadas:

        try:

            respuesta_asistentes = (
                supabase.table("asistentes")
                .select("quedada_id,usuario_id,horario_id")
                .in_("quedada_id", ids_quedadas)
                .execute()
            )

            todos_asistentes = respuesta_asistentes.data or []
            ids_usuarios = set()

            for asistente in todos_asistentes:

                qid = asistente["quedada_id"]
                uid = asistente["usuario_id"]

                asistentes_por_quedada.setdefault(
                    qid, []
                ).append(asistente)

                ids_usuarios.add(uid)

            ids_usuarios.update(
                q["creador_id"] for q in quedadas
            )

            if ids_usuarios:

                respuesta_perfiles = (
                    supabase.table("profiles")
                    .select("id,username,moto_foto_url")
                    .in_("id", list(ids_usuarios))
                    .execute()
                )

                for perfil in respuesta_perfiles.data or []:
                    perfiles_usuarios[perfil["id"]] = perfil

        except Exception as error:

            st.warning(
                "No se han podido cargar todos los asistentes y perfiles."
            )
            st.code(str(error))


    # -----------------------------------------------------
    # MOSTRAR QUEDADAS
    # -----------------------------------------------------

    if not quedadas:

        st.info(
            "Todavía no hay quedadas publicadas. "
            "¡Anímate a organizar la primera!"
        )

    else:

        st.markdown("### PRÓXIMAS SALIDAS")

        for quedada in quedadas:

            qid = quedada["id"]
            creador_id = quedada["creador_id"]

            asistentes = asistentes_por_quedada.get(qid, [])

            asistente_actual = next(
                (
                    a for a in asistentes
                    if str(a["usuario_id"]) == str(usuario_id)
                ),
                None
            )

            estoy_apuntado = asistente_actual is not None

            perfil_creador = perfiles_usuarios.get(creador_id, {})
            creador_nombre = perfil_creador.get("username", "Motero")

            imagen = (
                quedada.get("cartel_url")
                or quedada.get("imagen_url")
            )

            if (
                not isinstance(imagen, str)
                or not imagen.startswith(("https://", "http://"))
            ):
                imagen = IMAGEN_PREDETERMINADA

            st.markdown('<div class="event-card">', unsafe_allow_html=True)

            st.image(imagen, use_container_width=True)

            st.markdown(
                f"## 🏍️ {escapar(quedada.get('ruta_nombre'))}"
            )

            st.markdown(
                f"📅 **Fecha:** {escapar(quedada.get('fecha'))}"
            )

            st.markdown(
                f"👤 **Organiza:** {escapar(creador_nombre)}"
            )

            telefono = (
                quedada.get("telefono_organizador") or ""
            ).strip()

            if telefono:

                telefono_limpio = re.sub(r"[^0-9+]", "", telefono)

                st.markdown(
                    f"📞 **Teléfono del organizador:** "
                    f"`{escapar(telefono)}`"
                )

                if telefono_limpio:
                    st.markdown(
                        f'<a href="tel:{telefono_limpio}" '
                        'style="color:#FFD400;font-weight:bold;">'
                        '📲 LLAMAR AL ORGANIZADOR</a>',
                        unsafe_allow_html=True
                    )

            if quedada.get("descripcion"):
                st.write(quedada["descripcion"])

            # HORARIOS
            horarios = horarios_por_quedada.get(qid, [])

            if not horarios:

                horarios = [{
                    "id": None,
                    "quedada_id": qid,
                    "hora": quedada.get("hora", "09:00:00"),
                    "punto_encuentro": quedada.get(
                        "punto_encuentro",
                        ""
                    )
                }]

            st.markdown("#### 🕘 HORARIOS Y PUNTOS DE SALIDA")

            for horario in horarios:

                hora_texto = str(horario.get("hora") or "")[:5]
                punto_texto = horario.get("punto_encuentro") or ""

                st.markdown(
                    f"🕘 **{escapar(hora_texto)}** "
                    f"— 📍 {escapar(punto_texto)}"
                )

            # MAPA DE RUTA
            if quedada.get("es_ruta_catalogo"):

                ruta_correspondiente = next(
                    (
                        r for r in rutas
                        if r.get("nombre") == quedada.get("ruta_nombre")
                    ),
                    None
                )

                if ruta_correspondiente:

                    url_ruta = ruta_correspondiente.get("url", "")

                    if (
                        isinstance(url_ruta, str)
                        and url_ruta.startswith(("https://", "http://"))
                    ):

                        st.link_button(
                            "VER RECORRIDO EN GOOGLE MAPS ↗",
                            url_ruta
                        )

            st.divider()

            st.markdown(
                f"**🏍️ Moteros apuntados: {len(asistentes)}**"
            )

            # ASISTENTES
            with st.expander("👥 VER QUIÉN VA"):

                if asistentes:

                    for asistente in asistentes:

                        uid = asistente["usuario_id"]
                        perfil = perfiles_usuarios.get(uid, {})

                        nombre_asistente = (
                            perfil.get("username") or "Motero"
                        )

                        foto_asistente = perfil.get("moto_foto_url")
                        horario_asistente = asistente.get("horario_id")

                        horario_elegido = next(
                            (
                                h for h in horarios
                                if str(h.get("id")) == str(horario_asistente)
                                and h.get("id") is not None
                            ),
                            None
                        )

                        col_foto, col_datos = st.columns([1, 4])

                        with col_foto:

                            if (
                                isinstance(foto_asistente, str)
                                and foto_asistente.startswith(
                                    ("https://", "http://")
                                )
                            ):
                                st.image(
                                    foto_asistente,
                                    width=75
                                )
                            else:
                                st.markdown("🏍️")

                        with col_datos:

                            st.markdown(
                                f"**{escapar(nombre_asistente)}**"
                            )

                            if horario_elegido:
                                st.caption(
                                    "Salida elegida: "
                                    f"{str(horario_elegido.get('hora'))[:5]} "
                                    "— "
                                    f"{escapar(horario_elegido.get('punto_encuentro'))}"
                                )
                            else:
                                st.caption(
                                    "Horario pendiente de selección "
                                    "o inscripción antigua."
                                )

                else:

                    st.write("Todavía no hay asistentes.")

            # INSCRIPCIÓN
            st.markdown("#### 🏍️ TU INSCRIPCIÓN")

            if estoy_apuntado:

                horario_actual_id = asistente_actual.get("horario_id")
                indice_actual = 0

                for i, horario in enumerate(horarios):

                    if (
                        horario.get("id") is not None
                        and str(horario.get("id")) == str(horario_actual_id)
                    ):
                        indice_actual = i
                        break

                opciones_horarios = [
                    (
                        f"{str(h.get('hora'))[:5]} — "
                        f"{h.get('punto_encuentro', '')}"
                    )
                    for h in horarios
                ]

                nuevo_horario_indice = st.selectbox(
                    "Puedes cambiar tu horario de salida",
                    options=list(range(len(horarios))),
                    format_func=lambda i: opciones_horarios[i],
                    index=indice_actual,
                    key=f"cambiar_horario_{qid}"
                )

                col_cambiar, col_cancelar = st.columns(2)

                with col_cambiar:

                    if st.button(
                        "CAMBIAR HORARIO",
                        key=f"guardar_horario_{qid}",
                        use_container_width=True
                    ):

                        try:

                            horario_nuevo = horarios[nuevo_horario_indice]
                            horario_nuevo_id = horario_nuevo.get("id")

                            if horario_nuevo_id is None:

                                st.warning(
                                    "Este horario antiguo no tiene "
                                    "un identificador asociado."
                                )

                            else:

                                (
                                    supabase.table("asistentes")
                                    .update({
                                        "horario_id": horario_nuevo_id
                                    })
                                    .eq("quedada_id", qid)
                                    .eq("usuario_id", usuario_id)
                                    .execute()
                                )

                                st.success("Horario actualizado.")
                                st.rerun()

                        except Exception as error:

                            st.error("No se ha podido cambiar el horario.")
                            st.code(str(error))

                with col_cancelar:

                    if st.button(
                        "CANCELAR MI ASISTENCIA",
                        key=f"salir_{qid}",
                        use_container_width=True
                    ):

                        try:

                            (
                                supabase.table("asistentes")
                                .delete()
                                .eq("quedada_id", qid)
                                .eq("usuario_id", usuario_id)
                                .execute()
                            )

                            st.success("Has cancelado tu asistencia.")
                            st.rerun()

                        except Exception as error:

                            st.error(
                                "No se ha podido cancelar la asistencia."
                            )
                            st.code(str(error))

            else:

                opciones_horarios = [
                    (
                        f"{str(h.get('hora'))[:5]} — "
                        f"{h.get('punto_encuentro', '')}"
                    )
                    for h in horarios
                ]

                horario_elegido_indice = st.selectbox(
                    "Selecciona tu hora y punto de salida",
                    options=list(range(len(horarios))),
                    format_func=lambda i: opciones_horarios[i],
                    key=f"elegir_horario_{qid}"
                )

                if st.button(
                    "🏍️ ME APUNTO",
                    key=f"apuntarme_{qid}",
                    use_container_width=True
                ):

                    try:

                        horario_seleccionado = horarios[
                            horario_elegido_indice
                        ]

                        horario_id = horario_seleccionado.get("id")

                        datos_asistente = {
                            "quedada_id": qid,
                            "usuario_id": usuario_id,
                            "horario_id": horario_id
                        }

                        supabase.table("asistentes").insert(
                            datos_asistente
                        ).execute()

                        st.success(
                            "¡Ya estás apuntado a la quedada!"
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "No se ha podido registrar tu asistencia. "
                            "Puede que ya estés apuntado."
                        )

                        st.code(str(error))

            # ACCIONES DEL ORGANIZADOR
            if str(creador_id) == str(usuario_id):

                st.divider()
                st.caption("Esta es tu quedada.")

                if st.button(
                    "CANCELAR QUEDADA",
                    key=f"cancelar_{qid}",
                    use_container_width=True
                ):

                    try:

                        (
                            supabase.table("quedadas")
                            .update({"estado": "cancelada"})
                            .eq("id", qid)
                            .eq("creador_id", usuario_id)
                            .execute()
                        )

                        st.success("Quedada cancelada.")
                        st.rerun()

                    except Exception as error:

                        st.error("No se ha podido cancelar la quedada.")
                        st.code(str(error))

            st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SECCIÓN MI GARAJE
# =========================================================

if st.session_state["seccion_activa"] == "garaje":

    st.markdown(
        '<div class="section-title">🏁 MI GARAJE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="garaje-card">
            <div class="garaje-titulo">
                🏍️ GARAJE DE {escapar(username_actual.upper())}
            </div>
            <div class="garaje-subtitulo">
                Tu motocicleta y tu espacio en FAMILY BIKE.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="garaje-titulo">MI MOTOCICLETA</div>',
        unsafe_allow_html=True
    )

    if foto_moto_actual:

        st.image(
            foto_moto_actual,
            use_container_width=True,
            caption=f"Motocicleta de {username_actual}"
        )

    else:

        st.markdown(
            """
            <div class="garaje-card">
                <div class="garaje-titulo">
                    🏍️ TODAVÍA NO TIENES UNA FOTOGRAFÍA
                </div>
                <p>
                    Añade una imagen de tu motocicleta para que
                    aparezca en tu garaje cada vez que entres.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        '<div class="garaje-titulo">📸 AÑADIR O CAMBIAR FOTOGRAFÍA</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="garaje-subtitulo">
            Selecciona una fotografía de tu moto.
            Si ya tienes una guardada, podrás sustituirla.
        </div>
        """,
        unsafe_allow_html=True
    )

    foto_moto = st.file_uploader(
        "Selecciona la fotografía",
        type=["jpg", "jpeg", "png", "webp"],
        key="foto_moto_garaje"
    )

    if foto_moto:

        st.image(
            foto_moto,
            caption="Vista previa de la fotografía",
            use_container_width=True
        )

        if st.button(
            "GUARDAR EN MI GARAJE",
            use_container_width=True,
            key="guardar_foto_moto"
        ):

            try:

                url_foto = subir_archivo_storage(
                    foto_moto,
                    f"garaje/{usuario_id}",
                    "moto"
                )

                supabase.table("profiles").update({
                    "moto_foto_url": url_foto
                }).eq(
                    "id",
                    usuario_id
                ).execute()

                st.success(
                    "¡Fotografía guardada correctamente en tu garaje!"
                )

                st.rerun()

            except Exception as error:

                st.error("No se ha podido guardar la fotografía.")
                st.code(str(error))

    st.caption("Formatos permitidos: JPG, JPEG, PNG y WEBP.")


# =========================================================
# SECCIÓN COMUNIDAD
# =========================================================

if st.session_state["seccion_activa"] == "comunidad":

    # CHAT GENERAL: únicamente para sesiones autenticadas.
    st.markdown("### 💬 CHAT GENERAL FAMILY BIKE")
    st.caption("Sala común de la comunidad · Solo usuarios registrados")
    try:
        respuesta_chat = (
            supabase.table("familybike_chat_mensajes")
            .select("id,usuario_id,contenido,created_at")
            .order("created_at", desc=True)
            .limit(60)
            .execute()
        )
        mensajes_chat = list(reversed(respuesta_chat.data or []))
        ids_autores = list({m["usuario_id"] for m in mensajes_chat if m.get("usuario_id")})
        nombres_chat = {}
        if ids_autores:
            respuesta_autores = (
                supabase.table("profiles")
                .select("id,username")
                .in_("id", ids_autores)
                .execute()
            )
            nombres_chat = {
                str(p["id"]): p.get("username") or "Motero"
                for p in (respuesta_autores.data or [])
            }

        with st.container(border=True):
            if not mensajes_chat:
                st.info("Todavía no hay mensajes. ¡Inaugura el chat motero!")
            for mensaje in mensajes_chat:
                es_mio = str(mensaje.get("usuario_id")) == str(usuario_id)
                nombre_autor = nombres_chat.get(
                    str(mensaje.get("usuario_id")), "Motero"
                )
                fecha_mensaje = str(mensaje.get("created_at") or "")[:16].replace("T", " ")
                with st.chat_message("user" if es_mio else "assistant"):
                    st.caption(f"{'Tú' if es_mio else nombre_autor} · {fecha_mensaje} UTC")
                    st.write(mensaje.get("contenido") or "")
                    if es_admin:
                        if st.button(
                            "🗑️ Eliminar mensaje",
                            key=f"chat_eliminar_{mensaje['id']}"
                        ):
                            supabase.table("familybike_chat_mensajes").delete().eq(
                                "id", mensaje["id"]
                            ).execute()
                            st.rerun()

        if st.button("🔄 Actualizar mensajes", key="chat_actualizar"):
            st.rerun()

        with st.form("chat_formulario", clear_on_submit=True):
            nuevo_mensaje = st.text_area(
                "Escribe tu mensaje",
                max_chars=1000,
                height=80,
                placeholder="¿Quién se apunta a la próxima ruta?"
            )
            enviar_chat = st.form_submit_button(
                "💬 ENVIAR MENSAJE",
                use_container_width=True
            )
        if enviar_chat:
            texto_chat = nuevo_mensaje.strip()
            if not texto_chat:
                st.warning("Escribe un mensaje antes de enviarlo.")
            elif len(texto_chat) > 1000:
                st.error("El mensaje supera los 1.000 caracteres.")
            else:
                try:
                    supabase.table("familybike_chat_mensajes").insert({
                        "usuario_id": usuario_id,
                        "contenido": texto_chat,
                    }).execute()
                    st.rerun()
                except Exception as error:
                    st.error(f"No se pudo enviar el mensaje: {error}")
    except Exception as error:
        st.error("No se pudo cargar el chat. Ejecuta primero el SQL de configuración.")
        st.code(str(error))

    st.divider()

    st.markdown(
        '<div class="section-title">👥 COMUNIDAD FAMILY BIKE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Conoce a otros moteros de FAMILY BIKE y descubre sus motocicletas.
        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        respuesta_comunidad = (
            supabase.table("profiles")
            .select("id,username,moto_foto_url")
            .order("username")
            .execute()
        )

        todos_los_perfiles = respuesta_comunidad.data or []

        miembros = [
            perfil for perfil in todos_los_perfiles
            if (
                isinstance(perfil.get("moto_foto_url"), str)
                and perfil["moto_foto_url"].startswith(
                    ("https://", "http://")
                )
            )
        ]

        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-number">{len(miembros)}</div>
                <div class="stat-label">
                    MOTEROS CON FOTOGRAFÍA EN SU GARAJE
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        if not miembros:

            st.info(
                "Todavía no hay moteros que hayan subido "
                "la fotografía de su motocicleta. ¡Sé el primero!"
            )

        else:

            columnas_miembros = st.columns(3)

            for indice, miembro in enumerate(miembros):

                nombre_miembro = miembro.get("username") or "Motero"
                foto_miembro = miembro.get("moto_foto_url")

                es_mi_perfil = (
                    str(miembro.get("id")) == str(usuario_id)
                )

                with columnas_miembros[indice % 3]:

                    with st.container(border=True):

                        st.image(
                            foto_miembro,
                            use_container_width=True
                        )

                        st.markdown(
                            f"""
                            <div class="community-name">
                                {escapar(nombre_miembro)}
                            </div>
                            <div class="community-label">
                                🏍️ MIEMBRO FAMILY BIKE
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if es_mi_perfil:

                            st.markdown(
                                """
                                <div class="community-label">
                                    ★ TU MOTOCICLETA
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

    except Exception as error:

        st.error("No se ha podido cargar la comunidad.")

        st.warning(
            "Comprueba los permisos de lectura de profiles "
            "y que existan username y moto_foto_url."
        )

        st.code(str(error))


# =========================================================
# SECCIÓN TIENDA
# =========================================================

if st.session_state["seccion_activa"] == "tienda":

    st.markdown(
        '<div class="section-title">🛒 TIENDA FAMILY BIKE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Accede a nuestra tienda y descubre los productos disponibles.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tienda-card">
            <div class="tienda-titulo">
                🏍️ TIENDA FAMILY BIKE
            </div>
            <div class="tienda-texto">
                Equípate para tus próximas aventuras.
                Visita nuestra tienda y descubre lo que tenemos preparado.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_izquierda, col_boton, col_derecha = st.columns([1, 2, 1])

    with col_boton:

        st.link_button(
            "🛒 ENTRAR EN LA TIENDA",
            TIENDA_URL,
            use_container_width=True
        )

    st.caption("La tienda se abrirá en Payhip.")


# =========================================================
# SECCIÓN ADMINISTRACIÓN FAMILY BIKE
# =========================================================

if st.session_state["seccion_activa"] == "administracion":

    # Comprobación adicional en cada entrada a esta sección
    if not comprobar_es_admin(usuario_id):
        st.error("No tienes permisos para acceder a esta sección.")
        st.session_state["seccion_activa"] = "menu"
        st.stop()

    st.markdown(
        '<div class="section-title">⚙️ ADMINISTRACIÓN FAMILY BIKE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Panel de control general. Todos los administradores
            tienen los mismos permisos.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_rutas, tab_usuarios, tab_garajes, tab_quedadas, tab_noticias, tab_admins = st.tabs([
        "🗺️ RUTAS PENDIENTES",
        "👥 USUARIOS",
        "🏍️ GARAJES",
        "📅 QUEDADAS",
        "📢 NOTICIAS",
        "👑 ADMINISTRADORES"
    ])

    with tab_rutas:
        st.markdown("### MODERACIÓN DE RUTAS")
        try:
            pendientes = (
                supabase.table("familybike_rutas_propuestas")
                .select("id,nombre,url,descripcion,usuario_id,created_at")
                .eq("estado", "pendiente")
                .order("created_at")
                .execute()
            ).data or []
            st.metric("Pendientes de revisión", len(pendientes))
            if not pendientes:
                st.success("No hay rutas pendientes.")
            for propuesta in pendientes:
                with st.container(border=True):
                    st.markdown(f"**{escapar(propuesta['nombre'])}**")
                    if propuesta.get("descripcion"):
                        st.write(propuesta["descripcion"])
                    st.caption(f"Usuario: {propuesta['usuario_id']}")
                    if enlace_google_maps_valido(propuesta["url"]):
                        st.link_button("ABRIR GOOGLE MAPS", propuesta["url"])
                    col_aprobar, col_rechazar = st.columns(2)
                    with col_aprobar:
                        if st.button("✅ APROBAR", key=f"aprobar_{propuesta['id']}",
                                     use_container_width=True):
                            try:
                                supabase.table("familybike_rutas_propuestas").update(
                                    {"estado": "aprobada"}
                                ).eq("id", propuesta["id"]).eq(
                                    "estado", "pendiente"
                                ).execute()
                                st.rerun()
                            except Exception as error:
                                st.error(f"No se pudo aprobar: {error}")
                    with col_rechazar:
                        if st.button("❌ RECHAZAR", key=f"rechazar_{propuesta['id']}",
                                     use_container_width=True):
                            try:
                                supabase.table("familybike_rutas_propuestas").update(
                                    {"estado": "rechazada"}
                                ).eq("id", propuesta["id"]).eq(
                                    "estado", "pendiente"
                                ).execute()
                                st.rerun()
                            except Exception as error:
                                st.error(f"No se pudo rechazar: {error}")
        except Exception as error:
            st.error("No se pudieron cargar las propuestas. Ejecuta primero el SQL adjunto.")
            st.code(str(error))

    # =====================================================
    # ESTADÍSTICAS DE USUARIOS REGISTRADOS
    # =====================================================

    with tab_usuarios:
        st.markdown("### 👥 USUARIOS REGISTRADOS")
        st.caption("Nombres de acceso. Las rutas aprobadas se conservan al eliminar una cuenta.")

        try:
            # Se usa el cliente normal para la lista, respetando RLS.
            perfiles = []
            offset = 0
            while True:
                pagina = (
                    supabase.table("profiles")
                    .select("id,username")
                    .order("username")
                    .range(offset, offset + 499)
                    .execute()
                ).data or []
                perfiles.extend(pagina)
                if len(pagina) < 500:
                    break
                offset += 500

            st.metric("Total de perfiles", len(perfiles))
            filtro_usuario = st.text_input(
                "🔎 Buscar por nombre de usuario",
                key="admin_buscar_usuario"
            ).strip().casefold()
            visibles = [
                p for p in perfiles
                if filtro_usuario in (p.get("username") or "").casefold()
            ]
            st.caption(f"Mostrando {len(visibles)} usuarios")

            for perfil in visibles:
                uid = str(perfil["id"])
                nombre = perfil.get("username") or "Sin nombre"
                with st.expander(f"👤 {nombre}"):
                    if uid == str(usuario_id):
                        st.info("No puedes eliminar tu propia cuenta desde este panel.")
                        continue

                    confirmar = st.checkbox(
                        f"Confirmo que quiero eliminar la cuenta de {nombre}",
                        key=f"confirmar_borrado_usuario_{uid}"
                    )
                    if st.button(
                        "🗑️ ELIMINAR USUARIO",
                        key=f"borrar_usuario_{uid}",
                        disabled=not confirmar,
                        use_container_width=True
                    ):
                        try:
                            # Verificar identidad y rol en el servidor, no solo en la UI.
                            token = st.session_state.get("access_token")
                            if not token:
                                raise ValueError("Sesión caducada. Vuelve a iniciar sesión.")
                            usuario_verificado = supabase.auth.get_user(token).user
                            if str(usuario_verificado.id) != str(usuario_id):
                                raise PermissionError("Identidad de sesión no válida.")

                            clave_admin = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY")
                            if not clave_admin:
                                raise ValueError(
                                    "Falta SUPABASE_SERVICE_ROLE_KEY en los secretos de Streamlit."
                                )
                            cliente_admin = create_client(SUPABASE_URL, clave_admin)
                            permiso = (
                                cliente_admin.table("familybike_admins")
                                .select("user_id")
                                .eq("user_id", usuario_verificado.id)
                                .limit(1).execute()
                            ).data or []
                            if not permiso:
                                raise PermissionError("No tienes permisos de administrador.")

                            # Conserva las rutas aprobadas, desvinculándolas de la cuenta.
                            cliente_admin.table("familybike_rutas_propuestas").update({
                                "usuario_id": None
                            }).eq("usuario_id", uid).eq(
                                "estado", "aprobada"
                            ).execute()

                            # Supabase Auth elimina la cuenta. Las demás relaciones
                            # se rigen por las FK de la base de datos.
                            cliente_admin.auth.admin.delete_user(uid)
                            st.success(f"Cuenta {nombre} eliminada. Rutas aprobadas conservadas.")
                            st.rerun()
                        except Exception as error:
                            st.error(
                                "No se ha completado la eliminación. "
                                "Comprueba la configuración y las relaciones de Supabase."
                            )
                            st.code(str(error))

        except Exception as error:
            st.error("No se ha podido cargar el directorio de usuarios.")
            st.code(str(error))


    # =====================================================
    # ADMINISTRAR GARAJES
    # =====================================================

    with tab_garajes:

        st.markdown("### GESTIÓN DE GARAJES")
        st.write(
            "Consulta los garajes de los usuarios y elimina "
            "fotografías cuando sea necesario."
        )

        try:

            respuesta_garajes = (
                supabase.table("profiles")
                .select("id,username,moto_foto_url")
                .order("username")
                .execute()
            )

            perfiles_garajes = respuesta_garajes.data or []

            perfiles_con_foto = [
                p for p in perfiles_garajes
                if p.get("moto_foto_url")
            ]

            st.metric(
                "Fotografías de motocicletas",
                len(perfiles_con_foto)
            )

            if not perfiles_con_foto:

                st.info("Todavía no hay fotografías en los garajes.")

            else:

                for perfil in perfiles_con_foto:

                    nombre = perfil.get("username") or "Usuario"
                    foto = perfil.get("moto_foto_url")
                    uid = perfil.get("id")

                    with st.expander(
                        f"🏍️ {nombre} · {str(uid)[:8]}"
                    ):

                        if foto:
                            st.image(
                                foto,
                                use_container_width=True
                            )

                        st.caption(f"Usuario: {uid}")

                        confirmar_foto = st.checkbox(
                            "Confirmo que quiero eliminar esta fotografía",
                            key=f"confirmar_foto_{uid}"
                        )

                        if st.button(
                            "🗑️ ELIMINAR FOTOGRAFÍA",
                            key=f"eliminar_foto_{uid}",
                            disabled=not confirmar_foto,
                            use_container_width=True
                        ):

                            try:

                                eliminar_foto_garaje(perfil)

                                st.success(
                                    f"Fotografía de {nombre} eliminada."
                                )

                                st.rerun()

                            except Exception as error:

                                st.error(
                                    "No se ha podido eliminar la fotografía."
                                )
                                st.code(str(error))

        except Exception as error:

            st.error("No se han podido cargar los garajes.")
            st.code(str(error))


    # =====================================================
    # ADMINISTRAR QUEDADAS
    # =====================================================

    with tab_quedadas:

        st.markdown("### GESTIÓN DE TODAS LAS QUEDADAS")

        st.warning(
            "La eliminación es definitiva. Se borrarán también "
            "sus asistentes, horarios, notificaciones y fotografías "
            "almacenadas en FAMILY BIKE."
        )

        try:

            respuesta_admin_quedadas = (
                supabase.table("quedadas")
                .select(
                    "id,creador_id,ruta_nombre,es_ruta_catalogo,"
                    "fecha,hora,punto_encuentro,descripcion,"
                    "imagen_url,cartel_url,telefono_organizador,"
                    "estado,created_at"
                )
                .order("fecha", desc=True)
                .execute()
            )

            todas_quedadas_admin = (
                respuesta_admin_quedadas.data or []
            )

            st.metric(
                "Quedadas registradas",
                len(todas_quedadas_admin)
            )

            if not todas_quedadas_admin:

                st.info("No hay quedadas registradas.")

            else:

                # Obtener nombres de los organizadores
                ids_creadores = list({
                    q.get("creador_id")
                    for q in todas_quedadas_admin
                    if q.get("creador_id")
                })

                nombres_creadores = {}

                if ids_creadores:

                    respuesta_creadores = (
                        supabase.table("profiles")
                        .select("id,username")
                        .in_("id", ids_creadores)
                        .execute()
                    )

                    for perfil in respuesta_creadores.data or []:
                        nombres_creadores[perfil["id"]] = (
                            perfil.get("username") or "Motero"
                        )

                opciones_quedadas = {
                    (
                        f"{q.get('fecha', 'Sin fecha')} | "
                        f"{q.get('ruta_nombre', 'Sin nombre')} | "
                        f"{nombres_creadores.get(q.get('creador_id'), 'Motero')} | "
                        f"{q.get('estado', 'Sin estado')} | "
                        f"ID {str(q.get('id'))[:8]}"
                    ): q
                    for q in todas_quedadas_admin
                }

                seleccion_quedada = st.selectbox(
                    "Selecciona la quedada que quieres consultar",
                    options=list(opciones_quedadas.keys()),
                    key="admin_seleccion_quedada"
                )

                quedada_admin = opciones_quedadas[seleccion_quedada]
                qid_admin = quedada_admin.get("id")

                st.markdown("---")
                st.markdown(
                    f"#### 🏍️ {escapar(quedada_admin.get('ruta_nombre'))}"
                )

                st.write(
                    f"**Fecha:** {quedada_admin.get('fecha')}"
                )

                st.write(
                    f"**Hora principal:** "
                    f"{str(quedada_admin.get('hora') or '')[:5]}"
                )

                st.write(
                    f"**Organizador:** "
                    f"{nombres_creadores.get(quedada_admin.get('creador_id'), 'Motero')}"
                )

                st.write(
                    f"**Estado:** {quedada_admin.get('estado')}"
                )

                st.write(
                    f"**Punto de encuentro:** "
                    f"{quedada_admin.get('punto_encuentro') or 'No indicado'}"
                )

                if quedada_admin.get("descripcion"):
                    st.write(
                        f"**Descripción:** {quedada_admin.get('descripcion')}"
                    )

                imagen_admin = (
                    quedada_admin.get("cartel_url")
                    or quedada_admin.get("imagen_url")
                )

                if imagen_admin:
                    st.image(
                        imagen_admin,
                        caption="Imagen o cartel de la quedada",
                        use_container_width=True
                    )

                # Mostrar horarios
                try:

                    respuesta_horarios_admin = (
                        supabase.table("horarios_quedadas")
                        .select("id,hora,punto_encuentro")
                        .eq("quedada_id", qid_admin)
                        .order("hora")
                        .execute()
                    )

                    horarios_admin = (
                        respuesta_horarios_admin.data or []
                    )

                    st.markdown("#### HORARIOS")

                    if horarios_admin:

                        for h in horarios_admin:
                            st.write(
                                f"🕘 {str(h.get('hora') or '')[:5]} "
                                f"— {h.get('punto_encuentro') or ''}"
                            )

                    else:
                        st.info(
                            "No hay horarios adicionales registrados."
                        )

                except Exception as error:
                    st.warning("No se pudieron consultar los horarios.")
                    st.code(str(error))

                # Mostrar asistentes
                try:

                    respuesta_asistentes_admin = (
                        supabase.table("asistentes")
                        .select("usuario_id,horario_id")
                        .eq("quedada_id", qid_admin)
                        .execute()
                    )

                    asistentes_admin = (
                        respuesta_asistentes_admin.data or []
                    )

                    st.markdown(
                        f"#### ASISTENTES ({len(asistentes_admin)})"
                    )

                    if asistentes_admin:

                        ids_asistentes_admin = [
                            a.get("usuario_id")
                            for a in asistentes_admin
                            if a.get("usuario_id")
                        ]

                        respuesta_perfiles_admin = (
                            supabase.table("profiles")
                            .select("id,username")
                            .in_(
                                "id",
                                ids_asistentes_admin
                            )
                            .execute()
                        )

                        nombres_asistentes_admin = {
                            p["id"]: p.get("username", "Motero")
                            for p in (
                                respuesta_perfiles_admin.data or []
                            )
                        }

                        for asistente in asistentes_admin:
                            st.write(
                                "🏍️ "
                                + escapar(
                                    nombres_asistentes_admin.get(
                                        asistente.get("usuario_id"),
                                        "Motero"
                                    )
                                )
                            )

                    else:
                        st.info("Esta quedada no tiene asistentes.")

                except Exception as error:
                    st.warning("No se pudieron consultar los asistentes.")
                    st.code(str(error))

                st.divider()

                confirmar_borrado_quedada = st.checkbox(
                    "Confirmo que quiero eliminar definitivamente "
                    "esta quedada y todos sus datos relacionados.",
                    key=f"confirmar_borrar_quedada_{qid_admin}"
                )

                if st.button(
                    "🗑️ ELIMINAR QUEDADA COMPLETA",
                    key=f"admin_borrar_quedada_{qid_admin}",
                    disabled=not confirmar_borrado_quedada,
                    use_container_width=True
                ):

                    try:

                        eliminar_quedada_completa(quedada_admin)

                        st.success(
                            "La quedada y sus datos relacionados "
                            "se han eliminado."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "No se ha podido completar la eliminación. "
                            "Comprueba las políticas RLS de Supabase."
                        )
                        st.code(str(error))

        except Exception as error:

            st.error("No se han podido cargar las quedadas.")
            st.code(str(error))


    # =====================================================
    # ADMINISTRAR NOTICIAS
    # =====================================================

    with tab_noticias:

        st.markdown("### PUBLICAR NOTICIA")

        st.write(
            "Las noticias activas aparecerán en la página principal "
            "de FAMILY BIKE para todos los usuarios."
        )

        with st.form("admin_form_nueva_noticia"):

            titulo_noticia_nueva = st.text_input(
                "Título de la noticia",
                max_chars=150,
                placeholder="Ejemplo: Próxima concentración motera"
            )

            contenido_noticia_nueva = st.text_area(
                "Contenido de la noticia",
                height=160,
                placeholder="Escribe aquí el contenido..."
            )

            fijar_noticia_nueva = st.checkbox(
                "Fijar noticia en la parte superior",
                value=True
            )

            publicar_noticia = st.form_submit_button(
                "📢 PUBLICAR NOTICIA",
                use_container_width=True
            )

        if publicar_noticia:

            titulo_limpio = titulo_noticia_nueva.strip()
            contenido_limpio = contenido_noticia_nueva.strip()

            if not titulo_limpio or not contenido_limpio:

                st.error(
                    "Debes introducir un título y un contenido."
                )

            else:

                try:

                    supabase.table("familybike_noticias").insert({
                        "titulo": titulo_limpio,
                        "contenido": contenido_limpio,
                        "activo": True,
                        "fijado": fijar_noticia_nueva,
                        "creado_por": usuario_id,
                        "updated_at": datetime.now(
                            timezone.utc
                        ).isoformat()
                    }).execute()

                    st.success("Noticia publicada correctamente.")
                    st.rerun()

                except Exception as error:

                    st.error("No se ha podido publicar la noticia.")
                    st.code(str(error))

        st.divider()
        st.markdown("### GESTIONAR NOTICIAS PUBLICADAS")

        try:

            respuesta_todas_noticias = (
                supabase.table("familybike_noticias")
                .select(
                    "id,titulo,contenido,activo,fijado,"
                    "creado_por,created_at,updated_at"
                )
                .order("created_at", desc=True)
                .execute()
            )

            todas_noticias = (
                respuesta_todas_noticias.data or []
            )

            if not todas_noticias:

                st.info("Todavía no hay noticias publicadas.")

            else:

                for noticia in todas_noticias:

                    noticia_id = noticia.get("id")

                    estado_noticia = (
                        "ACTIVA"
                        if noticia.get("activo")
                        else "INACTIVA"
                    )

                    with st.expander(
                        f"📢 {noticia.get('titulo')} · {estado_noticia}"
                    ):

                        with st.form(
                            f"form_editar_noticia_{noticia_id}"
                        ):

                            titulo_editado = st.text_input(
                                "Título",
                                value=noticia.get("titulo") or "",
                                key=f"titulo_edit_{noticia_id}"
                            )

                            contenido_editado = st.text_area(
                                "Contenido",
                                value=noticia.get("contenido") or "",
                                height=150,
                                key=f"contenido_edit_{noticia_id}"
                            )

                            noticia_activa_editada = st.checkbox(
                                "Noticia visible en la página principal",
                                value=bool(noticia.get("activo")),
                                key=f"activa_edit_{noticia_id}"
                            )

                            noticia_fijada_editada = st.checkbox(
                                "Fijar en la parte superior",
                                value=bool(noticia.get("fijado")),
                                key=f"fijada_edit_{noticia_id}"
                            )

                            guardar_edicion = st.form_submit_button(
                                "💾 GUARDAR CAMBIOS",
                                use_container_width=True
                            )

                        if guardar_edicion:

                            if (
                                not titulo_editado.strip()
                                or not contenido_editado.strip()
                            ):

                                st.error(
                                    "El título y el contenido son obligatorios."
                                )

                            else:

                                try:

                                    supabase.table(
                                        "familybike_noticias"
                                    ).update({
                                        "titulo": titulo_editado.strip(),
                                        "contenido": contenido_editado.strip(),
                                        "activo": noticia_activa_editada,
                                        "fijado": noticia_fijada_editada,
                                        "updated_at": datetime.now(
                                            timezone.utc
                                        ).isoformat()
                                    }).eq(
                                        "id",
                                        noticia_id
                                    ).execute()

                                    st.success("Noticia actualizada.")
                                    st.rerun()

                                except Exception as error:

                                    st.error(
                                        "No se ha podido actualizar la noticia."
                                    )
                                    st.code(str(error))

                        st.divider()

                        confirmar_eliminar_noticia = st.checkbox(
                            "Confirmo que quiero eliminar esta noticia",
                            key=f"confirmar_noticia_{noticia_id}"
                        )

                        if st.button(
                            "🗑️ ELIMINAR NOTICIA",
                            key=f"borrar_noticia_{noticia_id}",
                            disabled=not confirmar_eliminar_noticia,
                            use_container_width=True
                        ):

                            try:

                                supabase.table(
                                    "familybike_noticias"
                                ).delete().eq(
                                    "id",
                                    noticia_id
                                ).execute()

                                st.success("Noticia eliminada.")
                                st.rerun()

                            except Exception as error:

                                st.error(
                                    "No se ha podido eliminar la noticia."
                                )
                                st.code(str(error))

        except Exception as error:

            st.error("No se han podido cargar las noticias.")
            st.code(str(error))


    # =====================================================
    # ADMINISTRAR ADMINISTRADORES
    # =====================================================

    with tab_admins:

        st.markdown("### ADMINISTRADORES DE FAMILY BIKE")

        st.write(
            "Todos los administradores tienen los mismos permisos. "
            "Puedes añadir o retirar administradores utilizando "
            "su nombre de usuario."
        )

        try:

            respuesta_admins = (
                supabase.table("familybike_admins")
                .select("user_id,created_at")
                .execute()
            )

            lista_admins = respuesta_admins.data or []

            ids_admins = [
                admin.get("user_id")
                for admin in lista_admins
                if admin.get("user_id")
            ]

            perfiles_admins = {}

            if ids_admins:

                respuesta_perfiles_admins = (
                    supabase.table("profiles")
                    .select("id,username")
                    .in_("id", ids_admins)
                    .execute()
                )

                perfiles_admins = {
                    p["id"]: p
                    for p in (
                        respuesta_perfiles_admins.data or []
                    )
                }

            st.metric(
                "Administradores actuales",
                len(lista_admins)
            )

            for admin in lista_admins:

                admin_id = admin.get("user_id")
                perfil_admin = perfiles_admins.get(admin_id, {})

                nombre_admin = (
                    perfil_admin.get("username")
                    or "Usuario sin perfil"
                )

                es_admin_actual = (
                    str(admin_id) == str(usuario_id)
                )

                col_nombre, col_id, col_estado = st.columns([2, 2, 1])

                with col_nombre:
                    st.markdown(
                        f"**👑 {escapar(nombre_admin)}**"
                    )

                with col_id:
                    st.caption(str(admin_id))

                with col_estado:
                    if es_admin_actual:
                        st.caption("Tu cuenta")

            st.divider()

            # AÑADIR ADMINISTRADOR
            st.markdown("#### ➕ AÑADIR ADMINISTRADOR")

            with st.form("form_anadir_admin"):

                username_nuevo_admin = st.text_input(
                    "Nombre de usuario de la cuenta",
                    placeholder="Escribe el usuario exacto"
                )

                anadir_admin = st.form_submit_button(
                    "AÑADIR ADMINISTRADOR",
                    use_container_width=True
                )

            if anadir_admin:

                username_busqueda = (
                    username_nuevo_admin.strip().lower()
                )

                if not re.fullmatch(
                    r"[a-z0-9_]{3,24}",
                    username_busqueda
                ):

                    st.error("Introduce un nombre de usuario válido.")

                else:

                    try:

                        respuesta_usuario_admin = (
                            supabase.table("profiles")
                            .select("id,username")
                            .eq("username", username_busqueda)
                            .maybe_single()
                            .execute()
                        )

                        perfil_nuevo_admin = (
                            respuesta_usuario_admin.data
                        )

                        if not perfil_nuevo_admin:

                            st.error(
                                "No se ha encontrado ningún usuario "
                                "con ese nombre."
                            )

                        else:

                            nuevo_admin_id = perfil_nuevo_admin["id"]

                            if str(nuevo_admin_id) in [
                                str(i) for i in ids_admins
                            ]:

                                st.info(
                                    "Ese usuario ya es administrador."
                                )

                            else:

                                supabase.table(
                                    "familybike_admins"
                                ).insert({
                                    "user_id": nuevo_admin_id
                                }).execute()

                                st.success(
                                    f"{username_busqueda} ya es "
                                    "administrador de FAMILY BIKE."
                                )

                                st.rerun()

                    except Exception as error:

                        st.error(
                            "No se ha podido añadir el administrador. "
                            "Comprueba los permisos RLS."
                        )
                        st.code(str(error))

            st.divider()

            # ELIMINAR ADMINISTRADOR
            st.markdown("#### ➖ RETIRAR ADMINISTRADOR")

            if len(lista_admins) <= 1:

                st.warning(
                    "No puedes eliminar al último administrador."
                )

            else:

                opciones_eliminar_admin = {}

                for admin in lista_admins:

                    admin_id = admin.get("user_id")
                    perfil_admin = perfiles_admins.get(admin_id, {})

                    nombre_admin = (
                        perfil_admin.get("username")
                        or "Usuario sin perfil"
                    )

                    etiqueta = (
                        f"{nombre_admin} "
                        f"({str(admin_id)[:8]})"
                    )

                    opciones_eliminar_admin[etiqueta] = admin_id

                admin_seleccionado_label = st.selectbox(
                    "Selecciona el administrador que quieres retirar",
                    options=list(opciones_eliminar_admin.keys()),
                    key="admin_seleccionar_eliminar"
                )

                admin_seleccionado_id = (
                    opciones_eliminar_admin[
                        admin_seleccionado_label
                    ]
                )

                confirmar_eliminar_admin = st.checkbox(
                    "Confirmo que quiero retirar los permisos "
                    "de esta cuenta.",
                    key="confirmar_eliminar_admin"
                )

                if st.button(
                    "➖ RETIRAR PERMISOS DE ADMINISTRADOR",
                    disabled=not confirmar_eliminar_admin,
                    use_container_width=True
                ):

                    try:

                        (
                            supabase.table("familybike_admins")
                            .delete()
                            .eq("user_id", admin_seleccionado_id)
                            .execute()
                        )

                        st.success(
                            "Los permisos de administrador se han retirado."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "No se ha podido retirar el administrador. "
                            "La base de datos también protege al último."
                        )
                        st.code(str(error))

        except Exception as error:

            st.error(
                "No se ha podido consultar la lista de administradores."
            )
            st.code(str(error))




# =========================================================
# PIE DE PÁGINA
# =========================================================

st.markdown("""
<div class="footer">
    <strong>FAMILY BIKE</strong><br><br>
    CARRETERA · AVENTURA · LIBERTAD<br>
    © FAMILY BIKE
</div>
""", unsafe_allow_html=True)
