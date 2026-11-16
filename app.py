
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

.stApp,
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

.hero {
    background: linear-gradient(110deg, #080808, #202020);
    border: 1px solid var(--amarillo);
    border-radius: 22px;
    padding: 35px;
    margin-bottom: 30px;
    text-align: center;
}

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

.route-card,
.event-card,
.garaje-card,
.community-card,
.stat-box,
.tienda-card,
.collaborator-card {
    background: var(--negro-card);
    border: 1px solid var(--borde);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 18px;
}

.route-card:hover,
.community-card:hover,
.collaborator-card:hover {
    border-color: var(--amarillo);
}

.route-number {
    color: var(--amarillo) !important;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.route-name,
.garaje-titulo,
.community-name,
.tienda-titulo {
    color: var(--amarillo) !important;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    font-weight: 800;
}

.stat-box {
    text-align: center;
}

.stat-number {
    color: var(--amarillo) !important;
    font-size: 30px;
    font-weight: 800;
}

.stat-label,
.garaje-subtitulo,
.community-label {
    color: var(--amarillo-suave) !important;
    font-size: 12px;
}

.community-name {
    text-align: center;
    margin-top: 12px;
}

.community-label {
    text-align: center;
    font-weight: 700;
}

.tienda-card {
    text-align: center;
    padding: 28px;
    border-color: var(--amarillo);
}

.tienda-titulo {
    font-size: 32px;
}

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

div[data-testid="stTextInput"] input,
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
}

div[data-baseweb="select"] > div {
    background: var(--negro-card);
    border-color: var(--borde);
}

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
    border-color: var(--amarillo-secundario);
}

button[data-baseweb="tab"] {
    color: var(--amarillo-suave) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--amarillo) !important;
    border-bottom-color: var(--amarillo) !important;
}

div[data-testid="stCheckbox"] label,
div[data-testid="stRadio"] label {
    color: var(--amarillo-suave) !important;
}

div[data-testid="stExpander"],
div[data-testid="stForm"] {
    background: var(--negro-card);
    border: 1px solid var(--borde);
    border-radius: 12px;
    padding: 12px;
}

div[data-testid="stAlert"] {
    background: #292929 !important;
    border: 2px solid #FFD400 !important;
    border-radius: 12px !important;
}

div[data-testid="stAlert"] *,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #FFF2A6 !important;
}

div[data-testid="stFileUploader"] {
    background: #171717 !important;
    border: 1px solid #FFD400 !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

div[data-testid="stFileUploader"] * {
    color: #FFFFFF !important;
}

div[data-testid="stFileUploader"] button {
    color: #111111 !important;
    background: #FFD400 !important;
}
</style>
""", unsafe_allow_html=True)


# =================================
# PORTADA
# =================================

col_izquierda, col_logo, col_derecha = st.columns([1, 2, 1])

with col_logo:
    st.image(LOGO_URL, width=320)


# =================================
# AUTENTICACIÓN
# =================================

def email_interno(username):
    return f"{username}@{AUTH_DOMAIN}"


def email_valido(email):
    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
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

        metadata = getattr(user, "user_metadata", {}) or {}

        st.session_state["tipo_cuenta"] = metadata.get(
            "tipo_cuenta",
            "motero"
        )

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
        "tipo_cuenta"
    ]:
        st.session_state.pop(key, None)


# =================================
# FUNCIONES DE COLABORADORES
# =================================

def obtener_colaborador(usuario_id):

    respuesta = (
        supabase.table("colaboradores")
        .select("*")
        .eq("usuario_id", usuario_id)
        .maybe_single()
        .execute()
    )

    return respuesta.data or {}


def guardar_colaborador(usuario_id, datos):

    existente = obtener_colaborador(usuario_id)

    datos_guardar = dict(datos)

    if existente:

        return (
            supabase.table("colaboradores")
            .update(datos_guardar)
            .eq("usuario_id", usuario_id)
            .execute()
        )

    datos_guardar["usuario_id"] = usuario_id

    return (
        supabase.table("colaboradores")
        .insert(datos_guardar)
        .execute()
    )


def subir_foto_colaborador(archivo, usuario_id):

    extension = archivo.name.rsplit(".", 1)[-1].lower()

    if extension not in ["jpg", "jpeg", "png", "webp"]:
        raise ValueError("Formato de imagen no permitido.")

    nombre_archivo = (
        f"colaboradores/{usuario_id}/"
        f"negocio_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
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

    resultado = (
        supabase.storage
        .from_(BUCKET_FAMILYBIKE)
        .get_public_url(nombre_archivo)
    )

    if isinstance(resultado, dict):
        url = (
            resultado.get("publicUrl")
            or resultado.get("publicURL")
        )
    else:
        url = str(resultado)

    if not url or not url.startswith("http"):
        raise ValueError("No se ha podido obtener la URL de la imagen.")

    return url


def validar_url(url):

    url = (url or "").strip()

    if not url:
        return True

    return url.startswith(("https://", "http://"))


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

    creadas = len(respuesta_insert.data or [])

    return {
        "creadas": creadas,
        "omitidas": len(perfiles) - creadas
    }


# =================================
# ORDENACIÓN DE RUTAS
# =================================

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

        metadata = getattr(
            usuario_actual,
            "user_metadata",
            {}
        ) or {}

        if not st.session_state.get("username"):
            st.session_state["username"] = metadata.get(
                "username",
                "motero"
            )

        st.session_state["tipo_cuenta"] = metadata.get(
            "tipo_cuenta",
            "motero"
        )

        autenticado = True

    except Exception:
        cerrar_sesion()


# =================================
# REGISTRO E INICIO DE SESIÓN
# =================================

if not autenticado:

    st.markdown(
        '<div class="section-title">ACCESO A FAMILY BIKE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Regístrate o inicia sesión para descubrir FAMILY BIKE.'
        '</div>',
        unsafe_allow_html=True
    )

    tab_login, tab_registro = st.tabs([
        "INICIAR SESIÓN",
        "CREAR CUENTA"
    ])

    # ---------------------------------
    # LOGIN
    # ---------------------------------

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
                        "No se ha podido iniciar sesión. "
                        "Comprueba el usuario y la contraseña."
                    )

    # ---------------------------------
    # REGISTRO
    # ---------------------------------

    with tab_registro:

        st.caption(
            "El correo indicado será tu dirección de contacto. "
            "Accederás con tu nombre de usuario y contraseña."
        )

        with st.form("form_registro"):

            tipo_cuenta = st.radio(
                "¿Cómo quieres registrarte?",
                ["Motero", "Empresa colaboradora"],
                horizontal=True
            )

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

                tipo_guardado = (
                    "empresa"
                    if tipo_cuenta == "Empresa colaboradora"
                    else "motero"
                )

                try:

                    response = supabase.auth.sign_up({
                        "email": email_interno(username),
                        "password": nueva_password,
                        "options": {
                            "data": {
                                "username": username,
                                "tipo_cuenta": tipo_guardado
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
                                "¡Cuenta creada correctamente!"
                            )

                            if tipo_guardado == "empresa":
                                st.info(
                                    "Tu cuenta de empresa está creada. "
                                    "Ya puedes completar tu ficha de colaborador."
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
                            "devuelto una sesión. Inicia sesión cuando puedas."
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
username_actual = st.session_state.get("username", "motero")
tipo_cuenta_actual = st.session_state.get("tipo_cuenta", "motero")

if not usuario_id:

    st.error(
        "No se ha podido identificar tu usuario. "
        "Vuelve a iniciar sesión."
    )

    st.stop()


# =================================
# CARGAR PERFIL Y FOTO DE MOTO
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
# CABECERA DEL USUARIO
# =================================

col_usuario, col_moto, col_salir = st.columns([2, 2, 1])

with col_usuario:

    tipo_etiqueta = (
        "EMPRESA COLABORADORA"
        if tipo_cuenta_actual == "empresa"
        else "MOTERO"
    )

    st.markdown(
        f"""
        <div class="garaje-card">
            <div class="garaje-titulo">🏍️ FAMILY BIKE</div>
            <div class="garaje-subtitulo">
                Usuario: <strong>{html.escape(username_actual)}</strong>
            </div>
            <div class="garaje-subtitulo">
                Tipo de cuenta: {tipo_etiqueta}
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

    elif tipo_cuenta_actual == "motero":

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

    st.error("No se han podido cargar las rutas.")
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
# PESTAÑAS PRINCIPALES
# =================================

tab_rutas, tab_quedadas, tab_garaje, tab_comunidad, tab_colaboradores, tab_tienda = st.tabs([
    "🏍️ EXPLORAR RUTAS",
    "📅 QUEDADAS MOTERAS",
    "🏁 MI GARAJE",
    "👥 COMUNIDAD",
    "🤝 COLABORADORES",
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
        'Encuentra tu próximo destino y disfruta de la carretera.'
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

                if validar_url(url_original) and url_original:

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

    with st.expander("➕ CREAR UNA NUEVA QUEDADA"):

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

            hora_quedada = st.time_input(
                "Hora de salida",
                value=time(9, 0)
            )

            punto_encuentro = st.text_input(
                "Punto de encuentro",
                placeholder="Ejemplo: Gasolinera de San Fernando"
            )

            descripcion = st.text_area(
                "Descripción de la salida",
                placeholder="Cuenta cómo será la ruta, kilómetros, paradas..."
            )

            imagen_quedada = st.text_input(
                "URL de una fotografía (opcional)",
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

                st.error("Indica el punto de encuentro.")

            elif not validar_url(imagen_quedada):

                st.error("La dirección de la fotografía no es válida.")

            else:

                imagen_final = imagen_quedada.strip()

                if tipo_destino == "Ruta del catálogo" and not imagen_final:

                    ruta_seleccionada = next(
                        (
                            r for r in rutas
                            if r.get("nombre") == nombre_final
                        ),
                        {}
                    )

                    imagen_final = ruta_seleccionada.get("imagen_url") or ""

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
                    "estado": "abierta"
                }

                try:

                    respuesta_nueva = (
                        supabase.table("quedadas")
                        .insert(nueva_quedada)
                        .execute()
                    )

                    filas_guardadas = respuesta_nueva.data or []

                    if not filas_guardadas:
                        raise ValueError("No se ha recibido la quedada creada.")

                    quedada_id = filas_guardadas[0].get("id")

                    if not quedada_id:
                        raise ValueError("No se ha recibido el ID de la quedada.")

                    st.success("¡Quedada publicada correctamente!")

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
                                "notificaciones pendientes."
                            )

                        else:

                            st.info(
                                "No hay usuarios con avisos activados "
                                "y correo válido."
                            )

                        if omitidas > 0:
                            st.caption(
                                f"{omitidas} perfiles no han generado "
                                "una notificación."
                            )

                    except Exception as error_avisos:

                        st.warning(
                            "La quedada se publicó, pero no se pudieron "
                            "crear las notificaciones."
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
                "imagen_url,estado,created_at"
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
    # ASISTENTES Y PERFILES
    # ---------------------------------

    asistentes_por_quedada = {}
    nombres_usuarios = {}

    if quedadas:

        ids_quedadas = [q["id"] for q in quedadas]

        try:

            respuesta_asistentes = (
                supabase.table("asistentes")
                .select("quedada_id,usuario_id")
                .in_("quedada_id", ids_quedadas)
                .execute()
            )

            todos_asistentes = respuesta_asistentes.data or []
            ids_usuarios = set()

            for asistente in todos_asistentes:

                qid = asistente["quedada_id"]
                uid = asistente["usuario_id"]

                asistentes_por_quedada.setdefault(qid, []).append(uid)
                ids_usuarios.add(uid)

            ids_usuarios.update(q["creador_id"] for q in quedadas)

            if ids_usuarios:

                respuesta_perfiles = (
                    supabase.table("profiles")
                    .select("id,username")
                    .in_("id", list(ids_usuarios))
                    .execute()
                )

                for perfil in respuesta_perfiles.data or []:

                    nombres_usuarios[perfil["id"]] = (
                        perfil.get("username", "Motero")
                    )

        except Exception:

            st.warning(
                "No se han podido cargar todos los nombres "
                "de los asistentes."
            )


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
            estoy_apuntado = usuario_id in asistentes

            creador_nombre = nombres_usuarios.get(
                creador_id,
                "Motero"
            )

            imagen = quedada.get("imagen_url")

            if (
                not isinstance(imagen, str)
                or not imagen.startswith(("https://", "http://"))
            ):
                imagen = IMAGEN_PREDETERMINADA

            with st.container(border=True):

                st.image(imagen, use_container_width=True)

                st.markdown(
                    f"## 🏍️ {html.escape(quedada['ruta_nombre'])}"
                )

                st.markdown(f"📅 **Fecha:** {quedada['fecha']}")
                st.markdown(f"🕘 **Hora:** {str(quedada['hora'])[:5]}")

                st.markdown(
                    f"📍 **Punto de encuentro:** "
                    f"{html.escape(quedada['punto_encuentro'])}"
                )

                st.markdown(
                    f"👤 **Organiza:** {html.escape(creador_nombre)}"
                )

                if quedada.get("descripcion"):
                    st.write(quedada["descripcion"])

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

                        if validar_url(url_ruta) and url_ruta:

                            st.link_button(
                                "VER RECORRIDO EN GOOGLE MAPS ↗",
                                url_ruta
                            )

                st.divider()

                st.markdown(
                    f"**🏍️ Moteros apuntados: {len(asistentes)}**"
                )

                with st.expander("Ver quién va"):

                    if asistentes:

                        for uid in asistentes:
                            st.write(
                                f"🏍️ {nombres_usuarios.get(uid, 'Motero')}"
                            )

                    else:
                        st.write("Todavía no hay asistentes.")

                col_apuntarse, col_estado = st.columns([2, 2])

                with col_apuntarse:

                    if estoy_apuntado:

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

                            except Exception as e:

                                st.error("No se ha podido cancelar.")
                                st.code(str(e))

                    else:

                        if st.button(
                            "🏍️ ME APUNTO",
                            key=f"apuntarme_{qid}",
                            use_container_width=True
                        ):

                            try:

                                supabase.table("asistentes").insert({
                                    "quedada_id": qid,
                                    "usuario_id": usuario_id
                                }).execute()

                                st.success("¡Ya estás apuntado!")
                                st.rerun()

                            except Exception as e:

                                st.error(
                                    "No se ha podido registrar tu asistencia."
                                )

                                st.code(str(e))

                with col_estado:

                    if creador_id == usuario_id:

                        st.caption("Esta es tu quedada")

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

                            except Exception as e:

                                st.error("No se ha podido cancelar.")
                                st.code(str(e))


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

        st.info(
            "Todavía no tienes una fotografía de tu motocicleta."
        )

    st.divider()

    st.markdown(
        '<div class="garaje-titulo">📸 AÑADIR O CAMBIAR FOTOGRAFÍA</div>',
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
            caption="Vista previa",
            use_container_width=True
        )

        if st.button(
            "GUARDAR EN MI GARAJE",
            use_container_width=True,
            key="guardar_foto_moto"
        ):

            try:

                extension = foto_moto.name.rsplit(".", 1)[-1].lower()

                nombre_archivo = (
                    f"garaje/{usuario_id}/moto_"
                    f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
                    f".{extension}"
                )

                supabase.storage.from_(BUCKET_FAMILYBIKE).upload(
                    nombre_archivo,
                    foto_moto.getvalue(),
                    file_options={
                        "content-type": foto_moto.type,
                        "upsert": "false"
                    }
                )

                resultado_url = (
                    supabase.storage
                    .from_(BUCKET_FAMILYBIKE)
                    .get_public_url(nombre_archivo)
                )

                if isinstance(resultado_url, dict):

                    url_foto = (
                        resultado_url.get("publicUrl")
                        or resultado_url.get("publicURL")
                    )

                else:

                    url_foto = str(resultado_url)

                if not url_foto or not url_foto.startswith("http"):
                    raise ValueError("No se ha recibido la URL de la fotografía.")

                supabase.table("profiles").update({
                    "moto_foto_url": url_foto
                }).eq("id", usuario_id).execute()

                st.success("¡Fotografía guardada correctamente!")
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
        '<div class="section-subtitle">'
        'Conoce a otros moteros y descubre sus motocicletas.'
        '</div>',
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

        miembros = []

        for perfil in todos_los_perfiles:

            foto = perfil.get("moto_foto_url")

            if (
                isinstance(foto, str)
                and foto.startswith(("https://", "http://"))
            ):
                miembros.append(perfil)

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

        if not miembros:

            st.info(
                "Todavía no hay moteros que hayan subido "
                "la fotografía de su motocicleta."
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
                            st.caption("★ TU MOTOCICLETA")

    except Exception as error_comunidad:

        st.error("No se ha podido cargar la comunidad.")
        st.code(str(error_comunidad))


# =================================
# COLABORADORES FAMILY BIKE
# =================================

with tab_colaboradores:

    st.markdown(
        '<div class="section-title">🤝 COLABORADORES FAMILY BIKE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Negocios y empresas que apoyan a nuestra comunidad motera.'
        '</div>',
        unsafe_allow_html=True
    )

    # ---------------------------------
    # PANEL DE EMPRESA
    # ---------------------------------

    if tipo_cuenta_actual == "empresa":

        st.markdown("### 🏢 PANEL DE MI NEGOCIO")

        try:

            colaborador = obtener_colaborador(usuario_id)

        except Exception as error:

            colaborador = {}

            st.error("No se ha podido cargar tu ficha.")
            st.code(str(error))


        if colaborador.get("imagen_url"):

            st.image(
                colaborador["imagen_url"],
                width=260,
                caption="Imagen actual de tu negocio"
            )

        with st.form("form_editar_colaborador"):

            nombre_empresa = st.text_input(
                "Nombre comercial",
                value=colaborador.get("nombre", "")
            )

            descripcion_empresa = st.text_area(
                "Descripción de tu negocio",
                value=colaborador.get("descripcion", ""),
                placeholder="Presenta tu empresa a la comunidad motera..."
            )

            servicios_empresa = st.text_area(
                "Productos, servicios y ofertas",
                value=colaborador.get("servicios", ""),
                placeholder="Taller, neumáticos, accesorios, equipamiento..."
            )

            direccion_empresa = st.text_input(
                "Dirección",
                value=colaborador.get("direccion", "")
            )

            telefono_empresa = st.text_input(
                "Teléfono",
                value=colaborador.get("telefono", "")
            )

            whatsapp_empresa = st.text_input(
                "WhatsApp",
                value=colaborador.get("whatsapp", "")
            )

            web_empresa = st.text_input(
                "Página web",
                value=colaborador.get("web", "")
            )

            instagram_empresa = st.text_input(
                "Instagram",
                value=colaborador.get("instagram", "")
            )

            foto_empresa = st.file_uploader(
                "Fotografía o logotipo de tu negocio",
                type=["jpg", "jpeg", "png", "webp"],
                key="foto_colaborador"
            )

            guardar_empresa = st.form_submit_button(
                "GUARDAR MI NEGOCIO",
                use_container_width=True
            )

        if guardar_empresa:

            if not nombre_empresa.strip():

                st.error("Introduce el nombre de tu negocio.")

            elif not validar_url(web_empresa):

                st.error("La dirección de la página web no es válida.")

            else:

                try:

                    imagen_url = colaborador.get("imagen_url", "")

                    if foto_empresa:

                        imagen_url = subir_foto_colaborador(
                            foto_empresa,
                            usuario_id
                        )

                    datos = {
                        "nombre": nombre_empresa.strip(),
                        "descripcion": descripcion_empresa.strip(),
                        "servicios": servicios_empresa.strip(),
                        "direccion": direccion_empresa.strip(),
                        "telefono": telefono_empresa.strip(),
                        "whatsapp": whatsapp_empresa.strip(),
                        "web": web_empresa.strip(),
                        "instagram": instagram_empresa.strip(),
                        "imagen_url": imagen_url,
                        "activo": True,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }

                    guardar_colaborador(usuario_id, datos)

                    st.success(
                        "¡Tu negocio está publicado en FAMILY BIKE!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error("No se ha podido guardar tu negocio.")
                    st.code(str(error))

    else:

        st.info(
            "¿Tienes un negocio relacionado con el mundo de la moto? "
            "Puedes crear una cuenta de empresa registrándote como "
            "Empresa colaboradora."
        )


    # ---------------------------------
    # CATÁLOGO PÚBLICO
    # ---------------------------------

    st.divider()

    st.markdown("### 🏍️ NUESTROS COLABORADORES")

    try:

        respuesta_colaboradores = (
            supabase.table("colaboradores")
            .select(
                "id,usuario_id,nombre,descripcion,imagen_url,"
                "servicios,direccion,telefono,whatsapp,web,instagram"
            )
            .eq("activo", True)
            .order("nombre")
            .execute()
        )

        colaboradores = respuesta_colaboradores.data or []

    except Exception as error:

        colaboradores = []

        st.error("No se han podido cargar los colaboradores.")
        st.code(str(error))


    if not colaboradores:

        st.info(
            "Todavía no hay empresas colaboradoras. "
            "¡Pronto tendremos nuevos negocios!"
        )

    else:

        st.caption(
            f"{len(colaboradores)} negocios colaboradores"
        )

        columnas_colaboradores = st.columns(2)

        for indice, empresa in enumerate(colaboradores):

            nombre = empresa.get("nombre") or "Negocio colaborador"
            imagen = empresa.get("imagen_url")
            descripcion = empresa.get("descripcion") or ""
            servicios = empresa.get("servicios") or ""

            with columnas_colaboradores[indice % 2]:

                with st.container(border=True):

                    if (
                        isinstance(imagen, str)
                        and imagen.startswith(("https://", "http://"))
                    ):

                        st.image(
                            imagen,
                            use_container_width=True
                        )

                    else:

                        st.markdown("### 🏢")

                    st.markdown(
                        f"### {html.escape(nombre)}"
                    )

                    if descripcion:
                        st.write(descripcion)

                    if servicios:

                        st.markdown("**SERVICIOS Y OFERTAS**")
                        st.write(servicios)

                    if empresa.get("direccion"):
                        st.write(f"📍 {empresa['direccion']}")

                    if empresa.get("telefono"):
                        st.write(f"☎️ {empresa['telefono']}")

                    if empresa.get("whatsapp"):

                        whatsapp = re.sub(
                            r"\D",
                            "",
                            empresa["whatsapp"]
                        )

                        if whatsapp:

                            st.link_button(
                                "CONTACTAR POR WHATSAPP",
                                f"https://wa.me/{whatsapp}",
                                use_container_width=True
                            )

                    if empresa.get("web"):

                        web = empresa["web"].strip()

                        if validar_url(web) and web:

                            st.link_button(
                                "VISITAR PÁGINA WEB",
                                web,
                                use_container_width=True
                            )

                    if empresa.get("instagram"):

                        instagram = empresa["instagram"].strip()

                        if instagram.startswith("@"):
                            instagram = instagram[1:]

                        instagram = re.sub(
                            r"[^a-zA-Z0-9._]",
                            "",
                            instagram
                        )

                        if instagram:

                            st.link_button(
                                "VER INSTAGRAM",
                                f"https://www.instagram.com/{instagram}/",
                                use_container_width=True
                            )


# =================================
# TIENDA
# =================================

with tab_tienda:

    st.markdown(
        '<div class="section-title">🛒 TIENDA FAMILY BIKE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Accede a nuestra tienda y descubre los productos disponibles.'
        '</div>',
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
