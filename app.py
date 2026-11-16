
import streamlit as st
import html
import re
from datetime import date, time, datetime, timezone
from supabase import create_client

# =================================
# CONFIGURACIÓN
# =================================

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


# =================================
# DISEÑO
# =================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --negro: #0B0B0B;
    --negro-card: #171717;
    --negro-hover: #222222;
    --amarillo: #FFD400;
    --amarillo-secundario: #F0B900;
    --amarillo-suave: #FFF2A6;
    --texto: #FFF8D6;
    --borde: #494000;
}

.stApp {
    background: var(--negro);
    color: var(--texto);
    font-family: 'Inter', sans-serif;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp p,
.stApp label,
.stApp span,
.stApp div {
    color: var(--texto);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--amarillo) !important;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* PORTADA */

.hero {
    background: linear-gradient(110deg, #080808, #202020);
    border: 1px solid var(--amarillo);
    border-radius: 22px;
    padding: 35px;
    margin-bottom: 30px;
    text-align: center;
}

.hero-label {
    color: var(--amarillo) !important;
    letter-spacing: 5px;
    font-size: 13px;
    font-weight: 700;
}

.hero p {
    color: var(--amarillo-suave) !important;
    font-size: 17px;
}

/* TÍTULOS */

.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 34px;
    font-weight: 700;
    color: var(--amarillo) !important;
    margin: 25px 0 5px 0;
}

.section-subtitle {
    color: var(--amarillo-suave) !important;
    font-size: 14px;
    margin-bottom: 22px;
}

/* RUTAS */

.route-card {
    background: var(--negro-card);
    border: 1px solid var(--borde);
    border-radius: 15px;
    padding: 22px;
    min-height: 175px;
    margin-bottom: 18px;
}

.route-card:hover {
    border-color: var(--amarillo);
}

.route-number {
    color: var(--amarillo) !important;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.route-name {
    color: var(--amarillo-suave) !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    font-weight: 700;
    margin: 12px 0 20px 0;
}

/* ESTADÍSTICAS */

.stat-box {
    background: var(--negro-card);
    border: 1px solid var(--borde);
    border-radius: 12px;
    padding: 18px;
    text-align: center;
}

.stat-number {
    color: var(--amarillo) !important;
    font-size: 30px;
    font-weight: 800;
}

.stat-label {
    color: var(--amarillo-suave) !important;
    font-size: 12px;
    letter-spacing: 1px;
}

/* QUEDADAS */

.event-card {
    background: var(--negro-card);
    border: 1px solid var(--borde);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 18px;
}

.schedule-card {
    background: #222222;
    border: 1px solid #FFD400;
    border-radius: 10px;
    padding: 12px;
    margin: 8px 0;
}

/* GARAJE */

.garaje-card {
    background: #171717;
    border: 1px solid #FFD400;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0 18px 0;
}

.garaje-titulo {
    color: #FFD400 !important;
    font-size: 23px;
    font-weight: 800;
    font-family: 'Barlow Condensed', sans-serif;
}

.garaje-subtitulo {
    color: #FFF2A6 !important;
    font-size: 14px;
    margin-top: 7px;
}

.garaje-card p,
.garaje-card div,
.garaje-card span,
.garaje-card strong {
    color: #FFFFFF !important;
}

/* COMUNIDAD */

.community-card {
    background: #171717;
    border: 1px solid #494000;
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 18px;
}

.community-name {
    color: #FFD400 !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    font-weight: 800;
    text-align: center;
    margin-top: 12px;
}

.community-label {
    color: #FFF2A6 !important;
    font-size: 11px;
    font-weight: 700;
    text-align: center;
    margin-top: 5px;
}

.community-you {
    color: #FFD400 !important;
    font-size: 11px;
    font-weight: 800;
    text-align: center;
    margin-top: 7px;
}

/* TIENDA */

.tienda-card {
    background: linear-gradient(135deg, #171717, #292929);
    border: 1px solid #FFD400;
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    margin: 20px 0;
}

.tienda-titulo {
    color: #FFD400 !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 32px;
    font-weight: 800;
}

.tienda-texto {
    color: #FFF2A6 !important;
    font-size: 16px;
    margin-top: 12px;
}

/* PIE */

.footer {
    text-align: center;
    color: var(--amarillo-suave) !important;
    border-top: 1px solid var(--borde);
    padding-top: 25px;
    margin-top: 50px;
    font-size: 12px;
}

.footer strong {
    color: var(--amarillo) !important;
}

/* CAMPOS */

div[data-testid="stTextInput"] input,
div[data-testid="stTextInputRootElement"] input,
div[data-testid="stTextArea"] textarea {
    background: var(--negro-card) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid var(--borde);
    border-radius: 9px;
}

div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
    color: #BDBDBD !important;
    -webkit-text-fill-color: #BDBDBD !important;
    opacity: 1 !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--amarillo);
    box-shadow: 0 0 0 1px var(--amarillo);
}

/* SELECTORES */

div[data-baseweb="select"] > div {
    background: var(--negro-card);
    border-color: var(--borde);
    color: var(--amarillo-suave);
}

div[data-baseweb="popover"],
div[data-baseweb="menu"] {
    background: var(--negro-card);
}

div[data-baseweb="menu"] li {
    color: var(--amarillo-suave);
}

/* BOTONES */

.stButton > button,
.stFormSubmitButton > button,
.stLinkButton > a {
    background: var(--amarillo);
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    border: 1px solid var(--amarillo);
    border-radius: 9px;
    font-weight: 800;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stLinkButton > a:hover {
    background: var(--amarillo-secundario);
    color: #111111 !important;
    border-color: var(--amarillo-secundario);
}

/* PESTAÑAS */

button[data-baseweb="tab"] {
    color: var(--amarillo-suave) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--amarillo) !important;
    border-bottom-color: var(--amarillo) !important;
}

/* CHECKBOX Y RADIO */

div[data-testid="stCheckbox"] label,
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label *,
div[data-testid="stRadio"] label * {
    color: var(--amarillo-suave) !important;
}

/* EXPANDERS */

div[data-testid="stExpander"] {
    background: var(--negro-card);
    border: 1px solid var(--borde);
    border-radius: 10px;
}

div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary span {
    color: var(--amarillo) !important;
}

/* FORMULARIOS */

div[data-testid="stForm"] {
    background: var(--negro-card);
    border: 1px solid var(--borde);
    border-radius: 12px;
    padding: 18px;
}

/* MENSAJES GENERALES */

div[data-testid="stAlert"] {
    background: #292929 !important;
    border: 2px solid #FFD400 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    opacity: 1 !important;
}

div[data-testid="stAlert"] *,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] li,
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] * {
    color: #FFFFFF !important;
    opacity: 1 !important;
    visibility: visible !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

div[data-testid="stAlert"] svg {
    color: #FFD400 !important;
    fill: #FFD400 !important;
}

/* ERRORES: CONTRASTE REFORZADO */

div[data-testid="stAlert"]:has(svg[data-testid="stIconError"]),
div[data-testid="stAlert"]:has([data-testid="stIconError"]) {
    background: #421515 !important;
    border: 2px solid #FF5555 !important;
}

div[data-testid="stAlert"]:has(svg[data-testid="stIconError"]) *,
div[data-testid="stAlert"]:has([data-testid="stIconError"]) * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}

/* MENSAJE DE ERROR DE ACCESO PERSONALIZADO */

.login-error {
    background: #421515;
    border: 2px solid #FF5555;
    border-radius: 12px;
    padding: 15px;
    margin: 12px 0;
    color: #FFFFFF !important;
    font-weight: 600;
}

.login-error strong,
.login-error p,
.login-error span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* CAPTIONS */

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
.stCaption {
    color: #FFF2A6 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #FFF2A6 !important;
}

/* SUBIDA DE FOTOGRAFÍAS */

div[data-testid="stFileUploader"] {
    background: #171717 !important;
    border: 1px solid #FFD400 !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

div[data-testid="stFileUploader"] *,
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] small {
    color: #FFFFFF !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

div[data-testid="stFileUploader"] button {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    background: #FFD400 !important;
}

hr {
    border-color: var(--borde) !important;
}
</style>
""", unsafe_allow_html=True)


# =================================
# FUNCIONES GENERALES
# =================================

def mostrar_error_login(mensaje):
    st.markdown(
        f"""
        <div class="login-error">
            ⚠️ <strong>Error de acceso</strong>
            <p>{html.escape(str(mensaje))}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def email_interno(username):
    return f"{username}@{AUTH_DOMAIN}"


def email_valido(email):
    return bool(
        re.fullmatch(
            r"[^@\\s]+@[^@\\s]+\\.[^@\\s]+",
            email.strip()
        )
    )


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


def subir_archivo_storage(archivo, carpeta, nombre_base):

    if not archivo:
        return None

    extension = archivo.name.rsplit(".", 1)[-1].lower()

    extensiones_permitidas = ["jpg", "jpeg", "png", "webp"]

    if extension not in extensiones_permitidas:
        raise ValueError("Formato de imagen no permitido.")

    nombre_archivo = (
        f"{carpeta}/{nombre_base}_"
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
            "Supabase no ha devuelto la dirección pública de la imagen."
        )

    return url


# =================================
# NOTIFICACIONES DE QUEDADAS
# =================================

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

    return {
        "creadas": len(respuesta_insert.data or []),
        "omitidas": len(perfiles) - len(respuesta_insert.data or [])
    }


# =================================
# RUTAS
# =================================

def numero_ruta(ruta):

    nombre = str(ruta.get("nombre", "")).strip()

    coincidencia = re.search(
        r"\\bruta\\s*#?\\s*(\\d+)",
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
            numero_ruta(ruta) if numero_ruta(ruta) is not None else 999999,
            str(ruta.get("nombre", "")).lower()
        )
    )


# =================================
# RESTAURAR SESIÓN
# =================================

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


# =================================
# LOGIN Y REGISTRO
# =================================

if not autenticado:

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

                mostrar_error_login(
                    "Introduce tu usuario y contraseña."
                )

            elif not re.fullmatch(r"[a-z0-9_]{3,24}", username):

                mostrar_error_login(
                    "El nombre de usuario no es válido."
                )

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

                        mostrar_error_login(
                            "Supabase no ha devuelto una sesión."
                        )

                except Exception:

                    mostrar_error_login(
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

                mostrar_error_login(
                    "El usuario debe tener entre 3 y 24 caracteres. "
                    "Utiliza letras, números o guion bajo."
                )

            elif not email_valido(email_real):

                mostrar_error_login(
                    "Introduce una dirección de correo electrónico válida."
                )

            elif len(nueva_password) < 8:

                mostrar_error_login(
                    "La contraseña debe tener al menos 8 caracteres."
                )

            elif nueva_password != repetir_password:

                mostrar_error_login(
                    "Las contraseñas no coinciden."
                )

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

                        try:

                            guardar_datos_contacto(
                                user_id_nuevo,
                                email_real,
                                aceptar_avisos
                            )

                            st.success(
                                "¡Cuenta creada correctamente! "
                                "Tu correo y tus preferencias se han guardado."
                            )

                            st.rerun()

                        except Exception as error_perfil:

                            st.error(
                                "La cuenta se ha creado, pero no se han "
                                "podido guardar los datos de contacto."
                            )

                            st.code(str(error_perfil))

                    else:

                        st.warning(
                            "Supabase ha recibido el registro, pero no ha "
                            "devuelto una sesión. Inicia sesión con tu usuario "
                            "y contraseña."
                        )

                except Exception as e:

                    st.error("ERROR AL CREAR LA CUENTA")
                    st.code(str(e))

    st.markdown("""
    <div class="footer">
        <strong>FAMILY BIKE</strong><br><br>
        CARRETERA · AVENTURA · LIBERTAD<br>
        © FAMILY BIKE
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =================================
# USUARIO AUTENTICADO
# =================================

usuario_id = st.session_state.get("user_id")
username_actual = st.session_state["username"]

if not usuario_id:

    st.error(
        "No se ha podido identificar tu usuario. "
        "Vuelve a iniciar sesión."
    )
    st.stop()


# =================================
# PERFIL Y FOTO DE MOTO
# =================================

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


# =================================
# CABECERA
# =================================

col_usuario, col_moto, col_salir = st.columns([2, 2, 1])

with col_usuario:

    st.markdown(
        f"""
        <div class="garaje-card">
            <div class="garaje-titulo">🏍️ MI GARAJE</div>
            <div class="garaje-subtitulo">
                Usuario: <strong>{html.escape(username_actual)}</strong>
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
                <div class="garaje-subtitulo">
                    Puedes subirla desde la pestaña Mi garaje.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with col_salir:

    if st.button("CERRAR SESIÓN", use_container_width=True):
        cerrar_sesion()
        st.rerun()


# =================================
# CARGAR RUTAS
# =================================

try:

    respuesta = (
        supabase.table("rutas")
        .select("id,nombre,url,imagen_url")
        .execute()
    )

    rutas = ordenar_rutas(respuesta.data or [])

except Exception as e:

    st.error("No se han podido cargar las rutas desde Supabase.")
    st.code(str(e))
    st.stop()


# =================================
# ESTADÍSTICAS
# =================================

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

    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(rutas)}</div>
        <div class="stat-label">RUTAS DISPONIBLES</div>
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">🏍️</div>
        <div class="stat-label">ESPÍRITU MOTERO</div>
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{total_quedadas}</div>
        <div class="stat-label">PRÓXIMAS QUEDADAS</div>
    </div>
    """, unsafe_allow_html=True)


# =================================
# PESTAÑAS
# =================================

tab_rutas, tab_quedadas, tab_garaje, tab_comunidad, tab_tienda = st.tabs([
    "🏍️ EXPLORAR RUTAS",
    "📅 QUEDADAS MOTERAS",
    "🏁 MI GARAJE",
    "👥 COMUNIDAD",
    "🛒 TIENDA"
])


# =================================
# EXPLORAR RUTAS
# =================================

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
                            {html.escape(nombre)}
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


# =================================
# QUEDADAS MOTERAS
# =================================

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

    # ---------------------------------
    # CREAR QUEDADA
    # ---------------------------------

    with st.expander("➕ CREAR UNA NUEVA QUEDADA", expanded=False):

        nombres_rutas = [
            ruta.get("nombre", "Ruta sin nombre")
            for ruta in rutas
        ]

        with st.form("form_nueva_quedada"):

            tipo_destino = st.radio(
                "¿Qué tipo de salida quieres organizar?",
                ["Ruta del catálogo", "Destino libre"],
                horizontal=True
            )

            if tipo_destino == "Ruta del catálogo" and nombres_rutas:

                ruta_elegida = st.selectbox(
                    "Selecciona una ruta",
                    nombres_rutas
                )

                destino_libre = ""

            else:

                ruta_elegida = ""

                destino_libre = st.text_input(
                    "Nombre del destino o ruta",
                    placeholder="Ejemplo: Grazalema, Sierra de Cádiz..."
                )

            fecha_quedada = st.date_input(
                "Fecha de la quedada",
                value=date.today(),
                min_value=date.today(),
                format="DD/MM/YYYY"
            )

            st.markdown("#### 🕘 HORARIOS DE SALIDA")

            st.caption(
                "El primer horario es obligatorio. Puedes añadir "
                "hasta dos horarios adicionales."
            )

            hora_quedada = st.time_input(
                "Primera hora de salida",
                value=time(9, 0),
                key="hora_principal"
            )

            punto_encuentro = st.text_input(
                "Primer punto de encuentro",
                placeholder="Ejemplo: Gasolinera de San Fernando"
            )

            st.divider()

            segunda_salida = st.checkbox(
                "Añadir un segundo horario de salida"
            )

            hora_segunda = st.time_input(
                "Segunda hora",
                value=time(10, 0),
                key="hora_segunda"
            )

            punto_segundo = st.text_input(
                "Punto de encuentro del segundo horario",
                placeholder="Ejemplo: Área de servicio de Jerez"
            )

            tercera_salida = st.checkbox(
                "Añadir un tercer horario de salida"
            )

            hora_tercera = st.time_input(
                "Tercera hora",
                value=time(11, 0),
                key="hora_tercera"
            )

            punto_tercero = st.text_input(
                "Punto de encuentro del tercer horario",
                placeholder="Ejemplo: Rotonda de entrada a Arcos"
            )

            st.divider()

            telefono_organizador = st.text_input(
                "Teléfono de contacto del organizador",
                placeholder="Ejemplo: 600123456"
            )

            descripcion = st.text_area(
                "Descripción de la salida",
                placeholder=(
                    "Cuenta cómo será la ruta, kilómetros, "
                    "paradas, recomendaciones..."
                )
            )

            cartel_quedada = st.file_uploader(
                "📸 Cartel o fotografía de la quedada",
                type=["jpg", "jpeg", "png", "webp"],
                help="Sube el cartel de la ruta desde tu dispositivo."
            )

            publicar = st.form_submit_button(
                "PUBLICAR QUEDADA",
                use_container_width=True
            )

        if cartel_quedada:
            st.image(
                cartel_quedada,
                caption="Vista previa del cartel",
                use_container_width=True
            )

        if publicar:

            nombre_final = (
                ruta_elegida
                if tipo_destino == "Ruta del catálogo"
                else destino_libre.strip()
            )

            telefono_limpio = re.sub(
                r"[^0-9+]",
                "",
                telefono_organizador.strip()
            )

            horarios_nuevos = [
                {
                    "hora": hora_quedada.strftime("%H:%M:%S"),
                    "punto_encuentro": punto_encuentro.strip()
                }
            ]

            if segunda_salida:

                horarios_nuevos.append({
                    "hora": hora_segunda.strftime("%H:%M:%S"),
                    "punto_encuentro": punto_segundo.strip()
                })

            if tercera_salida:

                horarios_nuevos.append({
                    "hora": hora_tercera.strftime("%H:%M:%S"),
                    "punto_encuentro": punto_tercero.strip()
                })

            if not nombre_final:

                st.error("Introduce el nombre de la ruta o destino.")

            elif not punto_encuentro.strip():

                st.error("Indica el primer punto de encuentro.")

            elif segunda_salida and not punto_segundo.strip():

                st.error("Indica el punto de encuentro del segundo horario.")

            elif tercera_salida and not punto_tercero.strip():

                st.error("Indica el punto de encuentro del tercer horario.")

            elif len(telefono_limpio) > 20:

                st.error("El teléfono introducido no es válido.")

            elif telefono_limpio and len(re.sub(r"\\D", "", telefono_limpio)) < 9:

                st.error("Introduce un teléfono de contacto válido.")

            else:

                try:

                    imagen_catalogo = ""

                    if tipo_destino == "Ruta del catálogo":

                        ruta_seleccionada = next(
                            (
                                r for r in rutas
                                if r.get("nombre") == nombre_final
                            ),
                            {}
                        )

                        imagen_catalogo = (
                            ruta_seleccionada.get("imagen_url") or ""
                        )

                    # SUBIR CARTEL A STORAGE

                    cartel_url = ""

                    if cartel_quedada:

                        cartel_url = subir_archivo_storage(
                            cartel_quedada,
                            f"quedadas/{usuario_id}",
                            "cartel"
                        )

                    nueva_quedada = {
                        "creador_id": usuario_id,
                        "ruta_nombre": nombre_final,
                        "es_ruta_catalogo": (
                            tipo_destino == "Ruta del catálogo"
                        ),
                        "fecha": fecha_quedada.isoformat(),
                        "hora": horarios_nuevos[0]["hora"],
                        "punto_encuentro": horarios_nuevos[0]["punto_encuentro"],
                        "descripcion": descripcion.strip(),
                        "imagen_url": cartel_url or imagen_catalogo,
                        "cartel_url": cartel_url,
                        "telefono_organizador": telefono_limpio,
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

                    # GUARDAR TODOS LOS HORARIOS

                    filas_horarios = []

                    for horario in horarios_nuevos:

                        filas_horarios.append({
                            "quedada_id": quedada_id,
                            "hora": horario["hora"],
                            "punto_encuentro": horario["punto_encuentro"]
                        })

                    supabase.table("horarios_quedadas").insert(
                        filas_horarios
                    ).execute()

                    st.success("¡Quedada publicada correctamente!")

                    # GENERAR NOTIFICACIONES

                    try:

                        resultado_avisos = crear_notificaciones_quedada(
                            quedada_id=quedada_id,
                            creador_id=usuario_id
                        )

                        creadas = resultado_avisos["creadas"]
                        omitidas = resultado_avisos["omitidas"]

                        if creadas > 0:

                            st.success(
                                f"📬 Se han registrado {creadas} "
                                "notificaciones pendientes. "
                                "Puedes enviarlas desde Google Colab."
                            )

                        else:

                            st.info(
                                "La quedada se ha publicado, pero no hay "
                                "usuarios con avisos activados y correo válido."
                            )

                        if omitidas > 0:

                            st.caption(
                                f"{omitidas} perfiles no han generado "
                                "una notificación."
                            )

                    except Exception as error_avisos:

                        st.warning(
                            "La quedada se ha publicado, pero no se han "
                            "podido crear las notificaciones."
                        )
                        st.code(str(error_avisos))

                    st.rerun()

                except Exception as e:

                    st.error("No se ha podido publicar la quedada.")
                    st.code(str(e))


    # ---------------------------------
    # CARGAR QUEDADAS
    # ---------------------------------

    try:

        respuesta = (
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

        quedadas = respuesta.data or []

    except Exception as e:

        st.error("No se han podido cargar las quedadas.")
        st.code(str(e))
        quedadas = []


    # ---------------------------------
    # CARGAR HORARIOS
    # ---------------------------------

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

                qid = horario["quedada_id"]

                horarios_por_quedada.setdefault(
                    qid, []
                ).append(horario)

        except Exception as e:

            st.warning(
                "No se han podido cargar los horarios adicionales. "
                "Se intentará mostrar el horario principal de cada quedada."
            )
            st.code(str(e))


    # ---------------------------------
    # CARGAR ASISTENTES Y PERFILES
    # ---------------------------------

    asistentes_por_quedada = {}
    perfiles_usuarios = {}

    if quedadas:

        ids_quedadas = [q["id"] for q in quedadas]

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

        except Exception as e:

            st.warning(
                "No se han podido cargar todos los asistentes y sus fotografías."
            )
            st.code(str(e))


    # ---------------------------------
    # MOSTRAR QUEDADAS
    # ---------------------------------

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

            mi_inscripcion = next(
                (
                    a for a in asistentes
                    if str(a["usuario_id"]) == str(usuario_id)
                ),
                None
            )

            creador_perfil = perfiles_usuarios.get(
                creador_id,
                {}
            )

            creador_nombre = creador_perfil.get(
                "username",
                "Motero"
            )

            imagen = (
                quedada.get("cartel_url")
                or quedada.get("imagen_url")
            )

            if (
                not isinstance(imagen, str)
                or not imagen.startswith(("https://", "http://"))
            ):
                imagen = IMAGEN_PREDETERMINADA

            horarios = horarios_por_quedada.get(qid, [])

            # COMPATIBILIDAD CON QUEDADAS ANTIGUAS

            if not horarios:

                horarios = [{
                    "id": None,
                    "quedada_id": qid,
                    "hora": quedada.get("hora", "09:00:00"),
                    "punto_encuentro": quedada.get("punto_encuentro", "")
                }]

            st.markdown(
                '<div class="event-card">',
                unsafe_allow_html=True
            )

            st.image(
                imagen,
                use_container_width=True
            )

            st.markdown(
                f"## 🏍️ {html.escape(quedada['ruta_nombre'])}"
            )

            st.markdown(
                f"📅 **Fecha:** {quedada['fecha']}"
            )

            st.markdown(
                f"👤 **Organiza:** {html.escape(creador_nombre)}"
            )

            telefono = quedada.get("telefono_organizador") or ""

            if telefono:

                telefono_seguro = re.sub(
                    r"[^0-9+]",
                    "",
                    str(telefono)
                )

                st.markdown(
                    f"📞 **Teléfono del organizador:** "
                    f"[{html.escape(telefono)}](tel:{telefono_seguro})"
                )

            if quedada.get("descripcion"):
                st.write(quedada["descripcion"])

            # MOSTRAR HORARIOS

            st.markdown("### 🕘 HORARIOS Y PUNTOS DE SALIDA")

            for indice_horario, horario in enumerate(horarios):

                hora_texto = str(horario.get("hora", ""))[:5]
                punto_texto = horario.get("punto_encuentro", "")

                st.markdown(
                    f"""
                    <div class="schedule-card">
                        <strong>🏍️ Salida {indice_horario + 1}</strong><br>
                        🕘 {html.escape(hora_texto)}<br>
                        📍 {html.escape(punto_texto)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ENLACE A LA RUTA

            if quedada.get("es_ruta_catalogo"):

                ruta_correspondiente = next(
                    (
                        r for r in rutas
                        if r.get("nombre") == quedada["ruta_nombre"]
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

            # MOSTRAR ASISTENTES CON FOTO

            with st.expander("👥 VER QUIÉN VA"):

                if asistentes:

                    for asistente in asistentes:

                        uid = asistente["usuario_id"]

                        perfil_asistente = perfiles_usuarios.get(
                            uid,
                            {}
                        )

                        nombre_asistente = perfil_asistente.get(
                            "username",
                            "Motero"
                        )

                        foto_asistente = perfil_asistente.get(
                            "moto_foto_url"
                        )

                        horario_asistente = next(
                            (
                                h for h in horarios
                                if h.get("id") == asistente.get("horario_id")
                            ),
                            None
                        )

                        if horario_asistente:

                            hora_asistente = str(
                                horario_asistente.get("hora", "")
                            )[:5]

                        else:

                            hora_asistente = str(
                                quedada.get("hora", "")
                            )[:5]

                        col_foto, col_nombre = st.columns([1, 4])

                        with col_foto:

                            if (
                                isinstance(foto_asistente, str)
                                and foto_asistente.startswith(("https://", "http://"))
                            ):

                                st.image(
                                    foto_asistente,
                                    width=75
                                )

                            else:

                                st.markdown("🏍️")

                        with col_nombre:

                            st.markdown(
                                f"**{html.escape(nombre_asistente)}**"
                            )

                            st.caption(
                                f"Salida: {hora_asistente}"
                            )

                else:

                    st.write("Todavía no hay asistentes.")

            # INSCRIPCIÓN Y CAMBIO DE HORARIO

            st.markdown("### 🏍️ PARTICIPAR EN ESTA QUEDADA")

            opciones_horarios = []

            for indice_horario, horario in enumerate(horarios):

                hora_texto = str(horario.get("hora", ""))[:5]
                punto_texto = horario.get("punto_encuentro", "")

                opciones_horarios.append(
                    f"Salida {indice_horario + 1} · {hora_texto} · {punto_texto}"
                )

            horario_actual_id = (
                mi_inscripcion.get("horario_id")
                if mi_inscripcion
                else None
            )

            indice_actual = 0

            for indice_horario, horario in enumerate(horarios):

                if horario.get("id") == horario_actual_id:
                    indice_actual = indice_horario
                    break

            horario_elegido = st.selectbox(
                "Selecciona tu horario de salida",
                options=list(range(len(horarios))),
                format_func=lambda i: opciones_horarios[i],
                index=indice_actual,
                key=f"horario_usuario_{qid}"
            )

            col_apuntarse, col_estado = st.columns([2, 2])

            with col_apuntarse:

                if mi_inscripcion:

                    if st.button(
                        "ACTUALIZAR MI HORARIO",
                        key=f"actualizar_{qid}",
                        use_container_width=True
                    ):

                        try:

                            horario_seleccionado = horarios[horario_elegido]

                            supabase.table("asistentes").update({
                                "horario_id": horario_seleccionado.get("id")
                            }).eq(
                                "quedada_id", qid
                            ).eq(
                                "usuario_id", usuario_id
                            ).execute()

                            st.success(
                                "Tu horario de salida se ha actualizado."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "No se ha podido actualizar tu horario."
                            )
                            st.code(str(e))

                    if st.button(
                        "CANCELAR MI ASISTENCIA",
                        key=f"salir_{qid}",
                        use_container_width=True
                    ):

                        try:

                            supabase.table("asistentes").delete().eq(
                                "quedada_id", qid
                            ).eq(
                                "usuario_id", usuario_id
                            ).execute()

                            st.success("Has cancelado tu asistencia.")
                            st.rerun()

                        except Exception as e:

                            st.error(
                                "No se ha podido cancelar la asistencia."
                            )
                            st.code(str(e))

                else:

                    if st.button(
                        "🏍️ ME APUNTO",
                        key=f"apuntarme_{qid}",
                        use_container_width=True
                    ):

                        try:

                            horario_seleccionado = horarios[horario_elegido]

                            supabase.table("asistentes").insert({
                                "quedada_id": qid,
                                "usuario_id": usuario_id,
                                "horario_id": horario_seleccionado.get("id")
                            }).execute()

                            st.success(
                                "¡Ya estás apuntado a la quedada!"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "No se ha podido registrar tu asistencia."
                            )
                            st.code(str(e))

            with col_estado:

                if creador_id == usuario_id:

                    st.caption("Esta es tu quedada.")

                    if st.button(
                        "CANCELAR QUEDADA",
                        key=f"cancelar_{qid}",
                        use_container_width=True
                    ):

                        try:

                            supabase.table("quedadas").update({
                                "estado": "cancelada"
                            }).eq(
                                "id", qid
                            ).eq(
                                "creador_id", usuario_id
                            ).execute()

                            st.success("Quedada cancelada.")
                            st.rerun()

                        except Exception as e:

                            st.error("No se ha podido cancelar la quedada.")
                            st.code(str(e))

            st.markdown('</div>', unsafe_allow_html=True)


# =================================
# MI GARAJE
# =================================

with tab_garaje:

    st.markdown(
        '<div class="section-title">🏁 MI GARAJE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="garaje-card">
            <div class="garaje-titulo">
                🏍️ GARAJE DE {html.escape(username_actual.upper())}
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


# =================================
# COMUNIDAD
# =================================

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
                and perfil["moto_foto_url"].startswith(("https://", "http://"))
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

                nombre_miembro = str(
                    miembro.get("username") or "Motero"
                )

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
                                {html.escape(nombre_miembro)}
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
                                <div class="community-you">
                                    ★ TU MOTOCICLETA
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

    except Exception as error_comunidad:

        st.error("No se ha podido cargar la comunidad.")

        st.warning(
            "Comprueba los permisos de lectura de la tabla profiles "
            "y que existan las columnas username y moto_foto_url."
        )

        st.code(str(error_comunidad))


# =================================
# TIENDA
# =================================

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


# =================================
# PIE DE PÁGINA
# =================================

st.markdown("""
<div class="footer">
    <strong>FAMILY BIKE</strong><br><br>
    CARRETERA · AVENTURA · LIBERTAD<br>
    © FAMILY BIKE
</div>
""", unsafe_allow_html=True)
