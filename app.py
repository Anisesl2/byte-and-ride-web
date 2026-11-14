
import streamlit as st
import html
import re
from supabase import create_client

# ---------------------------------
# CONFIGURACIÓN
# ---------------------------------

st.set_page_config(
    page_title="BYTE & RIDE | Rutas en moto",
    page_icon="🏍️",
    layout="wide"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Dominio técnico interno: no se muestra a los usuarios.
AUTH_DOMAIN = "users.byteandride.invalid"

def crear_cliente():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = crear_cliente()

# ---------------------------------
# ESTILOS
# ---------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: #101114;
    color: #f5f5f5;
    font-family: 'Inter', sans-serif;
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
    background: linear-gradient(110deg, #17191e, #292d34);
    border: 1px solid #393d45;
    border-radius: 22px;
    padding: 55px 35px;
    margin-bottom: 30px;
    text-align: center;
}

.hero-label {
    color: #f0a43a;
    letter-spacing: 5px;
    font-size: 13px;
    font-weight: 700;
}

.hero h1 {
    color: white;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: clamp(48px, 8vw, 82px);
    font-weight: 800;
    letter-spacing: 3px;
    margin: 12px 0;
}

.hero p {
    color: #bfc2c8;
    font-size: 17px;
    margin-bottom: 0;
}

.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 34px;
    font-weight: 700;
    color: white;
    margin: 25px 0 5px 0;
}

.section-subtitle {
    color: #999da5;
    font-size: 14px;
    margin-bottom: 22px;
}

.route-card {
    background: #1b1e24;
    border: 1px solid #343840;
    border-radius: 15px;
    padding: 22px;
    min-height: 175px;
    margin-bottom: 18px;
    transition: all .2s ease;
}

.route-card:hover {
    border-color: #f0a43a;
    transform: translateY(-3px);
}

.route-number {
    color: #f0a43a;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.route-name {
    color: #ffffff;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    font-weight: 700;
    margin: 12px 0 20px 0;
}

.route-link {
    display: inline-block;
    background: #f0a43a;
    color: #151515 !important;
    text-decoration: none !important;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    padding: 11px 16px;
    border-radius: 7px;
}

.route-link:hover {
    background: #ffc36b;
}

.stat-box {
    background: #1b1e24;
    border: 1px solid #343840;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
}

.stat-number {
    color: #f0a43a;
    font-size: 30px;
    font-weight: 800;
}

.stat-label {
    color: #aeb1b8;
    font-size: 12px;
    letter-spacing: 1px;
}

.footer {
    text-align: center;
    color: #777b83;
    border-top: 1px solid #30333a;
    padding-top: 25px;
    margin-top: 50px;
    font-size: 12px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input {
    background: #1b1e24;
    color: white;
    border: 1px solid #414650;
    border-radius: 9px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# PORTADA
# ---------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-label">MOTORCYCLE ROUTES • ADVENTURE • FREEDOM</div>
    <h1>BYTE & RIDE</h1>
    <p>Las mejores rutas para disfrutar de la carretera.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------
# FUNCIONES DE AUTENTICACIÓN
# ---------------------------------

def email_interno(username):
    return f"{username.lower()}@{AUTH_DOMAIN}"


def guardar_sesion(response, username):
    session = getattr(response, "session", None)

    if session is None:
        return False

    st.session_state["access_token"] = session.access_token
    st.session_state["refresh_token"] = session.refresh_token
    st.session_state["username"] = username

    return True


def cerrar_sesion():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    for key in ["access_token", "refresh_token", "username"]:
        st.session_state.pop(key, None)


# ---------------------------------
# RESTAURAR SESIÓN
# ---------------------------------

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

        supabase.auth.get_user()
        autenticado = True

    except Exception:
        cerrar_sesion()


# ---------------------------------
# REGISTRO E INICIO DE SESIÓN
# ---------------------------------

if not autenticado:

    st.markdown(
        '<div class="section-title">ACCESO A BYTE & RIDE</div>',
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
                type="password",
                placeholder="Tu contraseña"
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
                st.error("El nombre de usuario no tiene un formato válido.")

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
                        st.error("No se ha podido iniciar la sesión.")

                except Exception:
                    st.error("Usuario o contraseña incorrectos.")

    with tab_registro:

        with st.form("form_registro"):

            nuevo_usuario = st.text_input(
                "Elige un nombre de usuario",
                placeholder="Ejemplo: motero_01"
            )

            nueva_password = st.text_input(
                "Elige una contraseña",
                type="password"
            )

            repetir_password = st.text_input(
                "Repite la contraseña",
                type="password"
            )

            boton_registro = st.form_submit_button(
                "CREAR CUENTA",
                use_container_width=True
            )

        if boton_registro:

            username = nuevo_usuario.strip().lower()

            if not re.fullmatch(r"[a-z0-9_]{3,24}", username):
                st.error(
                    "El usuario debe tener entre 3 y 24 caracteres. "
                    "Solo letras, números y guion bajo."
                )

            elif len(nueva_password) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")

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
                        st.success("¡Cuenta creada correctamente!")
                        st.rerun()
                    else:
                        st.success(
                            "Registro recibido. Ahora inicia sesión "
                            "con tu usuario y contraseña."
                        )

                except Exception:
                    st.error(
                        "No se ha podido crear la cuenta. "
                        "Comprueba si el nombre de usuario ya existe."
                    )

    st.markdown("""
    <div class="footer">
        <strong>BYTE & RIDE</strong><br><br>
        CARRETERA · AVENTURA · LIBERTAD<br>
        © BYTE & RIDE
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ---------------------------------
# USUARIO AUTENTICADO
# ---------------------------------

col_usuario, col_salir = st.columns([4, 1])

with col_usuario:
    st.markdown(
        f"### 🏍️ Bienvenido, {html.escape(st.session_state['username'])}"
    )

with col_salir:
    if st.button("CERRAR SESIÓN", use_container_width=True):
        cerrar_sesion()
        st.rerun()


# ---------------------------------
# CARGAR RUTAS DESDE SUPABASE
# ---------------------------------

try:
    respuesta = (
        supabase.table("rutas")
        .select("id,nombre,url")
        .order("id")
        .execute()
    )

    rutas = respuesta.data or []

except Exception:
    st.error("No se han podido cargar las rutas desde Supabase.")
    st.stop()


# ---------------------------------
# ESTADÍSTICAS
# ---------------------------------

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
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">📍</div>
        <div class="stat-label">GOOGLE MAPS</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------
# CATÁLOGO DE RUTAS
# ---------------------------------

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
    placeholder="Escribe el nombre de una ruta..."
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

        nombre = html.escape(
            ruta.get("nombre", "Ruta sin nombre")
        )

        url_original = ruta.get("url", "")

        if not url_original.startswith(("https://", "http://")):
            continue

        url = html.escape(url_original, quote=True)

        tarjeta = f"""
        <div class="route-card">
            <div class="route-number">RUTA {indice + 1:02d}</div>
            <div class="route-name">{nombre}</div>
            <a class="route-link"
               href="{url}"
               target="_blank"
               rel="noopener noreferrer">
               VER RECORRIDO ↗
            </a>
        </div>
        """

        with columnas[indice % 3]:
            st.markdown(tarjeta, unsafe_allow_html=True)


# ---------------------------------
# PIE DE PÁGINA
# ---------------------------------

st.markdown("""
<div class="footer">
    <strong>BYTE & RIDE</strong><br><br>
    CARRETERA · AVENTURA · LIBERTAD<br>
    © BYTE & RIDE
</div>
""", unsafe_allow_html=True)
