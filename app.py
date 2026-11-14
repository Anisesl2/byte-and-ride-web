
import streamlit as st
import html
import re
import resend
from datetime import date, time
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

AUTH_DOMAIN = "users.byteandride.invalid"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

IMAGEN_PREDETERMINADA = (
    "https://images.unsplash.com/photo-1558981806-ec527fa84c39"
    "?auto=format&fit=crop&w=1000&q=80"
)


# ---------------------------------
# DISEÑO
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

.event-card {
    background: #1b1e24;
    border: 1px solid #343840;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 18px;
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
div[data-testid="stTextInputRootElement"] input,
div[data-testid="stTextInput"] input[type="password"],
div[data-testid="stTextArea"] textarea {
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
    <div class="hero-label">MOTORCYCLE ROUTES • ADVENTURE • FAMILY</div>
    <h1>FAMILY BIKE</h1>
    <p>Las mejores rutas para disfrutar de la carretera.</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------
# FUNCIONES DE AUTENTICACIÓN
# ---------------------------------

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

    return True


def guardar_datos_contacto(user_id, email_contacto, avisos_email):

    respuesta = (
        supabase.table("profiles")
        .update({
            "email_contacto": email_contacto.strip().lower(),
            "avisos_email": bool(avisos_email)
        })
        .eq("id", user_id)
        .execute()
    )

    return respuesta


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


# ---------------------------------
# RESEND: ENVÍO DE CORREO DE PRUEBA
# ---------------------------------

def enviar_correo_prueba():

    api_key = st.secrets.get("RESEND_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encuentra RESEND_API_KEY en los Secrets de Streamlit."
        )

    resend.api_key = api_key

    resultado = resend.Emails.send({
        "from": "FAMILY BIKE <onboarding@resend.dev>",
        "to": ["delivered@resend.dev"],
        "subject": "Prueba de correo - FAMILY BIKE",
        "html": """
            <div style="
                font-family:Arial,sans-serif;
                background:#101114;
                color:white;
                padding:30px;
                border-radius:12px;
            ">
                <h1 style="color:#f0a43a;">
                    FAMILY BIKE
                </h1>

                <h2>Prueba de conexión correcta</h2>

                <p>
                    Resend está conectado correctamente
                    con nuestra aplicación.
                </p>

                <p>
                    El sistema de correo está preparado
                    para futuras notificaciones de rutas.
                </p>
            </div>
        """,
        "text": (
            "FAMILY BIKE: prueba de conexión correcta "
            "con el servicio Resend."
        )
    })

    return resultado


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


# ---------------------------------
# REGISTRO E INICIO DE SESIÓN
# ---------------------------------

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

                        st.error("Supabase no ha devuelto una sesión.")

                except Exception:

                    st.error("No se ha podido iniciar sesión.")
                    st.info("Comprueba el usuario y la contraseña.")

    # ---------------------------------
    # CREAR CUENTA
    # ---------------------------------

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

                            st.warning(
                                "Comprueba que has ejecutado el SQL de "
                                "configuración de profiles."
                            )

                            st.code(str(error_perfil))

                    else:

                        st.warning(
                            "Supabase ha recibido el registro, pero no ha "
                            "devuelto una sesión. Inicia sesión con tu usuario "
                            "y contraseña. El correo de contacto tendrá que "
                            "guardarse después de iniciar sesión."
                        )

                except Exception as e:

                    st.error("ERROR AL CREAR LA CUENTA")
                    st.write(
                        "Supabase ha devuelto el siguiente mensaje:"
                    )
                    st.code(str(e))

    st.markdown("""
    <div class="footer">
        <strong>FAMILY BIKE</strong><br><br>
        CARRETERA · AVENTURA · LIBERTAD<br>
        © FAMILY BIKE
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ---------------------------------
# USUARIO AUTENTICADO
# ---------------------------------

usuario_id = st.session_state.get("user_id")
username_actual = st.session_state["username"]

col_usuario, col_salir = st.columns([4, 1])

with col_usuario:

    st.markdown(
        f"### 🏍️ Bienvenido, {html.escape(username_actual)}"
    )

with col_salir:

    if st.button(
        "CERRAR SESIÓN",
        use_container_width=True
    ):

        cerrar_sesion()
        st.rerun()


# ---------------------------------
# PANEL DE PRUEBA DE RESEND
# ---------------------------------

with st.expander("📧 PRUEBA DEL SISTEMA DE CORREO"):

    st.write(
        "Comprueba que FAMILY BIKE puede conectarse "
        "correctamente con Resend."
    )

    st.caption(
        "Esta prueba utiliza la dirección especial de simulación "
        "de Resend. No envía un correo a tu bandeja personal."
    )

    if st.button(
        "ENVIAR CORREO DE PRUEBA",
        key="boton_prueba_resend"
    ):

        try:

            resultado = enviar_correo_prueba()

            email_id = (
                resultado.get("id")
                if isinstance(resultado, dict)
                else getattr(resultado, "id", None)
            )

            st.success(
                "¡Conexión con Resend correcta!"
            )

            if email_id:
                st.code(f"ID del envío: {email_id}")

        except Exception as e:

            st.error(
                "No se ha podido enviar la prueba."
            )

            st.code(str(e))


if not usuario_id:

    st.error(
        "No se ha podido identificar tu usuario. "
        "Vuelve a iniciar sesión."
    )

    st.stop()


# ---------------------------------
# CARGAR RUTAS DESDE SUPABASE
# ---------------------------------

try:

    respuesta = (
        supabase.table("rutas")
        .select("id,nombre,url,imagen_url")
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


# ---------------------------------
# PESTAÑAS PRINCIPALES
# ---------------------------------

tab_rutas, tab_quedadas = st.tabs([
    "🏍️ EXPLORAR RUTAS",
    "📅 QUEDADAS MOTERAS"
])


# =================================
# PESTAÑA DE RUTAS
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

        st.caption(
            f"Mostrando {len(rutas_filtradas)} rutas"
        )

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

                st.image(
                    imagen,
                    use_container_width=True
                )

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
# PESTAÑA DE QUEDADAS
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

    with st.expander(
        "➕ CREAR UNA NUEVA QUEDADA",
        expanded=False
    ):

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

            if (
                tipo_destino == "Ruta del catálogo"
                and nombres_rutas
            ):

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
                placeholder=(
                    "Cuenta cómo será la ruta, kilómetros, "
                    "paradas, recomendaciones..."
                )
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

                st.error(
                    "Introduce el nombre de la ruta o destino."
                )

            elif not punto_encuentro.strip():

                st.error("Indica el punto de encuentro.")

            elif (
                imagen_quedada.strip()
                and not imagen_quedada.strip().startswith(
                    ("https://", "http://")
                )
            ):

                st.error(
                    "La dirección de la fotografía no es válida."
                )

            else:

                imagen_final = imagen_quedada.strip()

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

                    supabase.table("quedadas").insert(
                        nueva_quedada
                    ).execute()

                    st.success(
                        "¡Quedada publicada correctamente!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "No se ha podido publicar la quedada."
                    )

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

        st.error(
            "No se han podido cargar las quedadas."
        )

        st.code(str(e))
        quedadas = []


    # ---------------------------------
    # CARGAR ASISTENTES Y PERFILES
    # ---------------------------------

    asistentes_por_quedada = {}
    nombres_usuarios = {}

    if quedadas:

        ids_quedadas = [
            q["id"] for q in quedadas
        ]

        try:

            respuesta_asistentes = (
                supabase.table("asistentes")
                .select("quedada_id,usuario_id")
                .in_("quedada_id", ids_quedadas)
                .execute()
            )

            todos_asistentes = (
                respuesta_asistentes.data or []
            )

            ids_usuarios = set()

            for asistente in todos_asistentes:

                qid = asistente["quedada_id"]
                uid = asistente["usuario_id"]

                asistentes_por_quedada.setdefault(
                    qid, []
                ).append(uid)

                ids_usuarios.add(uid)

            ids_usuarios.update(
                q["creador_id"] for q in quedadas
            )

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
                "de los asistentes. Comprueba los permisos "
                "de la tabla profiles."
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

            asistentes = asistentes_por_quedada.get(
                qid,
                []
            )

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
                f"🕘 **Hora:** {str(quedada['hora'])[:5]}"
            )

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

                    url_ruta = ruta_correspondiente.get(
                        "url",
                        ""
                    )

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

            with st.expander("Ver quién va"):

                if asistentes:

                    for uid in asistentes:

                        nombre_asistente = nombres_usuarios.get(
                            uid,
                            "Motero"
                        )

                        st.write(
                            f"🏍️ {nombre_asistente}"
                        )

                else:

                    st.write(
                        "Todavía no hay asistentes."
                    )

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

                            st.success(
                                "Has cancelado tu asistencia."
                            )

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

                            supabase.table("asistentes").insert({
                                "quedada_id": qid,
                                "usuario_id": usuario_id
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

                    st.caption(
                        "Esta es tu quedada"
                    )

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

                            st.success(
                                "Quedada cancelada."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "No se ha podido cancelar la quedada."
                            )

                            st.code(str(e))

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


# ---------------------------------
# PIE DE PÁGINA
# ---------------------------------

st.markdown("""
<div class="footer">
    <strong>FAMILY BIKE</strong><br><br>
    CARRETERA · AVENTURA · LIBERTAD<br>
    © FAMILY BIKE
</div>
""", unsafe_allow_html=True)
