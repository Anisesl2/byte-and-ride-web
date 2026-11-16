
import streamlit as st
import html
import re
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
TIENDA_URL = "https://payhip.com/b/YWPxa"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

/* FONDO GENERAL */
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

/* TEXTO GENERAL */
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

/* TÍTULOS */
h1, h2, h3, h4, h5, h6 {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
}

/* CABECERA */
.hero {
    background: linear-gradient(110deg, #000000, #171717);
    border: 1px solid #FFD400;
    border-radius: 22px;
    padding: 35px;
    margin-bottom: 30px;
    text-align: center;
}

/* TÍTULOS DE SECCIÓN */
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

/* TARJETAS */
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

/* ESTADÍSTICAS */
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

/* GARAJE Y COMUNIDAD */
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

/* TIENDA */
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

/* CAMPOS DE TEXTO */
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

/* SELECTORES */
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

/* HORARIOS Y FECHAS */
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

/* RADIO, CHECKBOX Y TOGGLE */
div[data-testid="stRadio"] *,
div[data-testid="stCheckbox"] *,
div[data-testid="stToggle"] * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

/* BOTONES */
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

/* PESTAÑAS */
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

/* EXPANDERS Y FORMULARIOS */
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

/* MENSAJES */
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

/* ERRORES */
div[data-testid="stAlert"][kind="error"] {
    background: #180000 !important;
    border: 1px solid #FF4545 !important;
}

div[data-testid="stAlert"][kind="error"] * {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

/* ÉXITO */
div[data-testid="stAlert"][kind="success"] {
    background: #101010 !important;
    border: 1px solid #FFD400 !important;
}

/* SUBIDA DE ARCHIVOS */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] * {
    background-color: #101010 !important;
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
    border-color: #806B00 !important;
}

/* BOTÓN INTERNO DEL SUBIDOR */
div[data-testid="stFileUploader"] button {
    background: #FFD400 !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* ENLACES */
a, a:visited {
    color: #FFD400 !important;
    -webkit-text-fill-color: #FFD400 !important;
}

/* IMÁGENES */
img {
    border-radius: 10px;
}

/* SEPARADORES */
hr {
    border-color: #806B00 !important;
}

/* PIE DE PÁGINA */
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
        "user_id"
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
# ACCESO Y REGISTRO
# =========================================================

if not autenticado:

    col_izquierda, col_logo, col_derecha = st.columns([1, 2, 1])

    with col_logo:
        st.image(LOGO_URL, width=320)

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

    tab_login, tab_registro = st.tabs([
        "INICIAR SESIÓN",
        "CREAR CUENTA"
    ])

    with tab_login:

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

except Exception:
    st.warning(
        "No se ha podido cargar la fotografía del garaje."
    )


# =========================================================
# CABECERA
# =========================================================

col_usuario, col_moto, col_salir = st.columns([2, 2, 1])

with col_usuario:

    st.markdown(
        f"""
        <div class="garaje-card">
            <div class="garaje-titulo">🏍️ MI GARAJE</div>
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


col1, col2, col3 = st.columns(3)

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

with col2:
    st.markdown(
        """
        <div class="stat-box">
            <div class="stat-number">🏍️</div>
            <div class="stat-label">ESPÍRITU MOTERO</div>
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
# PESTAÑAS
# =========================================================

tab_rutas, tab_quedadas, tab_garaje, tab_comunidad, tab_tienda = st.tabs([
    "🏍️ EXPLORAR RUTAS",
    "📅 QUEDADAS MOTERAS",
    "🏁 MI GARAJE",
    "👥 COMUNIDAD",
    "🛒 TIENDA"
])


# =========================================================
# PESTAÑA RUTAS
# =========================================================

with tab_rutas:

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
# PESTAÑA QUEDADAS
# =========================================================

with tab_quedadas:

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
    # RADIO FUERA DEL FORMULARIO PARA ACTUALIZACIÓN DINÁMICA
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
# PESTAÑA MI GARAJE
# =========================================================

with tab_garaje:

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
# PESTAÑA COMUNIDAD
# =========================================================

with tab_comunidad:

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
# PESTAÑA TIENDA
# =========================================================

with tab_tienda:

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
# PIE DE PÁGINA
# =========================================================

st.markdown("""
<div class="footer">
    <strong>FAMILY BIKE</strong><br><br>
    CARRETERA · AVENTURA · LIBERTAD<br>
    © FAMILY BIKE
</div>
""", unsafe_allow_html=True)
