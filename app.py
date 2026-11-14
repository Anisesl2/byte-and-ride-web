
import streamlit as st
import html
import re
from supabase import create_client

# ---------------------------------
# CONFIGURACIÓN
# ---------------------------------

st.set_page_config(
    page_title="FAMILY BIKE | Rutas en moto",
    page_icon="🏍️",
    layout="wide"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Se mantiene el dominio interno para conservar
# las cuentas de usuario que ya hemos creado.
AUTH_DOMAIN = "users.byteandride.invalid"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------------------------
# DISEÑO FAMILY BIKE
# ---------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --orange: #f0a43a;
    --orange-light: #ffc36b;
    --background: #0c0e12;
    --card: #171a20;
    --border: #30343d;
    --muted: #a3a8b2;
}

.stApp {
    background: var(--background);
    color: #f5f5f5;
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1320px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* ---------------------------------
   PORTADA PRINCIPAL
--------------------------------- */

.hero {
    position: relative;
    overflow: hidden;
    min-height: 440px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding: 65px 7%;
    margin-bottom: 38px;
    border-radius: 24px;
    border: 1px solid #343943;

    background-image:
        linear-gradient(
            90deg,
            rgba(8, 10, 14, 0.96) 0%,
            rgba(8, 10, 14, 0.82) 38%,
            rgba(8, 10, 14, 0.25) 100%
        ),
        linear-gradient(
            0deg,
            rgba(8, 10, 14, 0.55),
            transparent 60%
        ),
        url("https://images.unsplash.com/photo-1781950878596-a16655127d7b?auto=format&fit=crop&w=2400&q=85");

    background-size: cover;
    background-position: center 55%;
    box-shadow: 0 20px 65px rgba(0,0,0,0.35);
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 720px;
}

.hero h1 {
    color: white;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: clamp(65px, 10vw, 112px);
    font-weight: 900;
    letter-spacing: 2px;
    line-height: 0.9;
    margin: 0 0 22px 0;
    text-shadow: 0 5px 25px rgba(0,0,0,0.4);
}

.hero h1 span {
    color: var(--orange);
}

.hero-description {
    color: #e1e3e8;
    font-size: clamp(15px, 2vw, 19px);
    line-height: 1.7;
    max-width: 520px;
    margin-bottom: 25px;
}

.hero-line {
    width: 75px;
    height: 4px;
    background: var(--orange);
    border-radius: 5px;
    margin-bottom: 23px;
}

.hero-tagline {
    color: white;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 3px;
}

/* ---------------------------------
   TÍTULOS
--------------------------------- */

.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 37px;
    font-weight: 800;
    color: white;
    margin: 25px 0 5px 0;
    letter-spacing: 1px;
}

.section-title span {
    color: var(--orange);
}

.section-subtitle {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 24px;
    line-height: 1.6;
}

/* ---------------------------------
   TARJETAS DE RUTA
--------------------------------- */

.route-card {
    background: linear-gradient(145deg, #1c2027, #14171c);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 23px;
    min-height: 185px;
    margin-bottom: 18px;
    transition: all .25s ease;
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.route-card:hover {
    border-color: var(--orange);
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(240,164,58,0.09);
}

.route-number {
    color: var(--orange);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 3px;
}

.route-name {
    color: #ffffff;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 27px;
    font-weight: 700;
    margin: 15px 0 22px 0;
    line-height: 1.1;
}

.route-link {
    display: inline-block;
    background: var(--orange);
    color: #151515 !important;
    text-decoration: none !important;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 1px;
    padding: 12px 17px;
    border-radius: 7px;
    transition: all .2s ease;
}

.route-link:hover {
    background: var(--orange-light);
    transform: translateY(-2px);
}

/* ---------------------------------
   ESTADÍSTICAS
--------------------------------- */

.stat-box {
    background: linear-gradient(145deg, #1b1f26, #14171c);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 22px 12px;
    text-align: center;
    transition: border .2s ease;
}

.stat-box:hover {
    border-color: var(--orange);
}

.stat-number {
    color: var(--orange);
    font-size: 32px;
    font-weight: 900;
}

.stat-label {
    color: #aeb3bd;
    font-size: 11px;
    letter-spacing: 1.5px;
    font-weight: 700;
    margin-top: 5px;
}

/* ---------------------------------
   ACCESO Y FORMULARIOS
--------------------------------- */

div[data-testid="stTextInput"] input,
div[data-testid="stTextInputRootElement"] input,
div[data-testid="stTextInput"] input[type="password"] {
    background: #1b1e24;
    color: white;
    border: 1px solid #414650;
    border-radius: 9px;
}

div[data-testid="stTextInput"] input:focus {
    border-color: var(--orange);
    box-shadow: 0 0 0 1px var(--orange);
}

.stButton button,
.stFormSubmitButton button {
    background: var(--orange);
    color: #171717;
    border: none;
    border-radius: 9px;
    font-weight: 900;
    letter-spacing: 1px;
    min-height: 43px;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: var(--orange-light);
    color: #111;
    border: none;
}

/* ---------------------------------
   PESTAÑAS
--------------------------------- */

button[data-baseweb="tab"] {
    color: #c3c6ce;
    font-weight: 700;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--orange);
}

div[data-baseweb="tab-highlight"] {
    background-color: var(--orange);
}

/* ---------------------------------
   PIE DE PÁGINA
--------------------------------- */

.footer {
    text-align: center;
    color: #858a94;
    border-top: 1px solid #30343c;
    padding-top: 28px;
    margin-top: 55px;
    font-size: 12px;
    line-height: 1.9;
}

.footer strong {
    color: white;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 25px;
    letter-spacing: 3px;
}

.footer span {
    color: var(--orange);
}

/* ---------------------------------
   MÓVILES
--------------------------------- */

@media (max-width: 768px) {

    .block-container {
        padding-top: 0.7rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        min-height: 340px;
        padding: 38px 25px;
        border-radius: 17px;
        background-position: center;
    }

    .hero h1 {
        font-size: 65px;
    }

    .hero-description {
        font-size: 14px;
    }

    .section-title {
        font-size: 30px;
    }

    .route-card {
        min-height: 160px;
    }
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------
# PORTADA FAMILY BIKE
# ---------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-content">

        <h1>
            FAMILY<br>
            <span>BIKE</span>
        </h1>

        <div class="hero-line"></div>

        <div class="hero-description">
            No importa el destino. Lo importante es el camino.
            Descubre nuevas carreteras, encuentra tu próxima
            aventura y disfruta cada kilómetro.
        </div>

        <div class="hero-tagline">
            TU MOTO · TU RUTA · TU LIBERTAD
        </div>

    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------
# FUNCIONES DE AUTENTICACIÓN
# ---------------------------------

def email_interno(username):
    return f"{username}@{AUTH_DOMAIN}"


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

    for key in [
        "access_token",
        "refresh_token",
        "username"
    ]:
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
        '<div class="section-title">BIENVENIDO A <span>FAMILY BIKE</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Accede a tu cuenta o regístrate para descubrir nuevas rutas.'
        '</div>',
        unsafe_allow_html=True
    )

    tab_login, tab_registro = st.tabs([
        "INICIAR SESIÓN",
        "CREAR CUENTA"
    ])

    # ---------------------------------
    # INICIAR SESIÓN
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
                "ENTRAR EN FAMILY BIKE",
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

                        st.success("¡Bienvenido a Family Bike!")
                        st.rerun()

                    else:

                        st.error("Supabase no ha devuelto una sesión.")

                except Exception as e:

                    st.error("No se ha podido iniciar sesión.")
                    st.code(str(e))

    # ---------------------------------
    # CREAR CUENTA
    # ---------------------------------

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
                "UNIRME A FAMILY BIKE",
                use_container_width=True
            )

        if boton_registro:

            username = nuevo_usuario.strip().lower()

            if not re.fullmatch(r"[a-z0-9_]{3,24}", username):

                st.error(
                    "El usuario debe tener entre 3 y 24 caracteres. "
                    "Utiliza letras, números o guion bajo."
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

                        st.success("¡Ya formas parte de Family Bike!")
                        st.rerun()

                    else:

                        st.warning(
                            "Supabase ha recibido el registro, "
                            "pero no ha devuelto una sesión. "
                            "Prueba a iniciar sesión."
                        )

                except Exception as e:

                    st.error("ERROR AL CREAR LA CUENTA")
                    st.write(
                        "Supabase ha devuelto el siguiente mensaje:"
                    )
                    st.code(str(e))

    # ---------------------------------
    # PIE DE PÁGINA SIN SESIÓN
    # ---------------------------------

    st.markdown("""
    <div class="footer">
        <strong>FAMILY BIKE</strong><br>
        <span>CARRETERA · AVENTURA · LIBERTAD</span><br>
        © FAMILY BIKE
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ---------------------------------
# USUARIO AUTENTICADO
# ---------------------------------

col_usuario, col_salir = st.columns([4, 1])

with col_usuario:

    st.markdown(
        f"### 🏍️ Bienvenido a Family Bike, "
        f"{html.escape(st.session_state['username'])}"
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

except Exception as e:

    st.error("No se han podido cargar las rutas desde Supabase.")
    st.code(str(e))
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
    '<div class="section-title">EXPLORA <span>LAS RUTAS</span></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Tu próxima aventura está a un clic. Elige una ruta y disfruta del camino.'
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
            <div class="route-number">FAMILY BIKE · RUTA {indice + 1:02d}</div>
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

            st.markdown(
                tarjeta,
                unsafe_allow_html=True
            )


# ---------------------------------
# PIE DE PÁGINA
# ---------------------------------

st.markdown("""
<div class="footer">
    <strong>FAMILY BIKE</strong><br>
    <span>CARRETERA · AVENTURA · LIBERTAD</span><br>
    © FAMILY BIKE
</div>
""", unsafe_allow_html=True)
