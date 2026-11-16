import streamlit as st
import streamlit.components.v1 as components
import html
import re
import json
import mimetypes
import xml.etree.ElementTree as ET
from datetime import date, time, datetime, timezone
from supabase import create_client

# =========================================================
# CONFIGURACIÓN
# =========================================================
st.set_page_config(page_title="FAMILY BIKE | Rutas en moto",
                   page_icon="🏍️", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
AUTH_DOMAIN = "users.byteandride.invalid"
BUCKET_FAMILYBIKE = "familybike"
TIENDA_URL = "https://payhip.com/b/YWPxa"
FACEBOOK_URL = "https://m.facebook.com/groups/1646146103973952/?ref=share"
ADMIN_USER_ID = "5837c2b2-915d-428b-85bb-786528285a06"

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
# DISEÑO
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
:root{--negro:#000;--card:#101010;--amarillo:#FFD400;--borde:#806B00}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{background:#000!important;color:#FFD400!important;font-family:Inter,sans-serif!important}
header[data-testid="stHeader"]{background:#000!important}
.block-container{max-width:1250px;padding-top:2rem;padding-bottom:3rem}
.stApp p,.stApp span,.stApp label,.stApp li,.stApp small,.stApp strong,.stApp div,
.stMarkdown,.stMarkdown p,[data-testid="stCaptionContainer"]{color:#FFD400!important;-webkit-text-fill-color:#FFD400!important}
h1,h2,h3,h4,h5,h6{color:#FFD400!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:800!important}
.section-title{font-family:'Barlow Condensed',sans-serif;font-size:34px;font-weight:800;color:#FFD400;margin:25px 0 5px}
.section-subtitle{font-size:14px;margin-bottom:22px}
.hero,.route-card,.event-card,.garaje-card,.community-card,.stat-box,.tienda-card{
 background:#101010!important;border:1px solid #806B00!important;border-radius:15px;padding:20px;margin-bottom:18px}
.route-name,.garaje-titulo,.community-name{font-family:'Barlow Condensed',sans-serif;font-size:25px;font-weight:800}
.route-number,.stat-label,.garaje-subtitulo,.community-label{font-size:12px;letter-spacing:1px}
.stat-box{text-align:center}.stat-number{font-size:30px;font-weight:800}
.tienda-card{text-align:center;border-color:#FFD400!important}.tienda-titulo{font-size:32px;font-weight:800}
.menu-intro{text-align:center;background:linear-gradient(135deg,#101010,#1B1B1B);border:1px solid #806B00;border-radius:18px;padding:22px;margin:22px 0}
.menu-intro-title{font-family:'Barlow Condensed',sans-serif;font-size:32px;font-weight:800}
input,textarea,div[data-baseweb="select"],div[data-baseweb="select"]>div{
 background:#101010!important;color:#FFD400!important;border:1px solid #806B00!important}
input::placeholder,textarea::placeholder{color:#B99B00!important}
div[data-baseweb="popover"],div[data-baseweb="menu"],div[data-baseweb="calendar"],
div[data-baseweb="calendar"] *{background:#101010!important;color:#FFD400!important}
.stButton>button,.stFormSubmitButton>button,.stLinkButton>a{
 background:#FFD400!important;color:#000!important;border:1px solid #FFD400!important;border-radius:9px!important;font-weight:800!important}
.stButton>button *, .stFormSubmitButton>button *, .stLinkButton>a *{color:#000!important}
div[data-testid="stButton"] button[kind="secondary"]{
 min-height:82px;width:100%;white-space:normal;border-radius:15px;font-size:18px;
 font-weight:800;border:1px solid #FFD400;background:#101010!important;color:#FFD400!important}
div[data-testid="stButton"] button[kind="secondary"] *{color:#FFD400!important}
div[data-testid="stExpander"],div[data-testid="stForm"]{background:#101010!important;border:1px solid #806B00!important;border-radius:10px}
div[data-testid="stExpander"] summary,div[data-testid="stExpander"] summary *{background:#101010!important;color:#FFD400!important}
div[data-testid="stAlert"]{background:#101010!important;border:1px solid #FFD400!important}
div[data-testid="stAlert"] *{color:#FFD400!important}
div[data-testid="stFileUploader"],div[data-testid="stFileUploader"] *{background:#101010!important;color:#FFD400!important}
div[data-testid="stFileUploader"] button{background:#FFD400!important;color:#000!important}
a,a:visited{color:#FFD400!important}
img{border-radius:10px}hr{border-color:#806B00!important}
.footer{text-align:center;border-top:1px solid #806B00;padding-top:25px;margin-top:50px;font-size:12px}
@media(max-width:600px){.block-container{padding-left:.8rem;padding-right:.8rem;padding-top:1rem}.section-title{font-size:29px}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNCIONES GENERALES Y STORAGE
# =========================================================
def email_interno(username):
    return f"{username}@{AUTH_DOMAIN}"

def email_valido(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", (email or "").strip()))

def escapar(valor):
    return html.escape(str(valor or ""))

def guardar_sesion(response, username):
    session = getattr(response, "session", None)
    if session is None:
        return False
    st.session_state["access_token"] = session.access_token
    st.session_state["refresh_token"] = session.refresh_token
    st.session_state["username"] = username
    user = getattr(response, "user", None) or getattr(session, "user", None)
    if user is not None:
        st.session_state["user_id"] = user.id
    return True

def guardar_datos_contacto(user_id, email_contacto, avisos_email):
    return supabase.table("profiles").update({
        "email_contacto": email_contacto.strip().lower(),
        "avisos_email": bool(avisos_email)
    }).eq("id", user_id).execute()

def cerrar_sesion():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    for key in ["access_token","refresh_token","username","user_id","seccion_activa"]:
        st.session_state.pop(key, None)

def subir_archivo_storage(archivo, carpeta, prefijo):
    extension = archivo.name.rsplit(".", 1)[-1].lower() if "." in archivo.name else "bin"
    nombre = (f"{carpeta}/{prefijo}_"
              f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.{extension}")
    mime = archivo.type or mimetypes.guess_type(archivo.name)[0] or "application/octet-stream"
    supabase.storage.from_(BUCKET_FAMILYBIKE).upload(
        nombre, archivo.getvalue(),
        file_options={"content-type": mime, "upsert": "false"}
    )
    resultado = supabase.storage.from_(BUCKET_FAMILYBIKE).get_public_url(nombre)
    if isinstance(resultado, dict):
        url = resultado.get("publicUrl") or resultado.get("publicURL")
    else:
        url = str(resultado)
    if not url or not url.startswith("http"):
        raise ValueError("Supabase no ha devuelto la URL pública del archivo.")
    return url, nombre

# =========================================================
# NOTIFICACIONES DE QUEDADAS
# =========================================================
def crear_notificaciones_quedada(quedada_id, creador_id):
    perfiles = (supabase.table("profiles").select("id,email_contacto,avisos_email")
                .eq("avisos_email", True).execute().data or [])
    ahora = datetime.now(timezone.utc).isoformat()
    filas = []
    for perfil in perfiles:
        email = (perfil.get("email_contacto") or "").strip().lower()
        if perfil.get("id") != creador_id and email_valido(email):
            filas.append({
                "quedada_id": quedada_id, "profile_id": perfil["id"],
                "email_destino": email, "estado": "pendiente",
                "intentos": 0, "proximo_intento": ahora
            })
    if filas:
        supabase.table("notificaciones_quedadas").insert(filas).execute()
    return {"creadas": len(filas), "omitidas": len(perfiles)-len(filas)}

# =========================================================
# FUNCIONES DE RUTAS DEL CATÁLOGO
# =========================================================
def numero_ruta(ruta):
    coincidencia = re.search(r"\bruta\s*#?\s*(\d+)",
                             str(ruta.get("nombre","")), re.I)
    return int(coincidencia.group(1)) if coincidencia else None

def ordenar_rutas(lista):
    return sorted(lista, key=lambda r: (
        numero_ruta(r) is None, numero_ruta(r) or 999999,
        str(r.get("nombre","")).lower()))

# =========================================================
# GPX / KML: LECTURA DE TRACKS Y WAYPOINTS
# =========================================================
def parsear_gpx(contenido):
    raiz = ET.fromstring(contenido)
    puntos = []
    for nodo in raiz.iter():
        etiqueta = nodo.tag.rsplit("}", 1)[-1].lower()
        if etiqueta in ("trkpt", "rtept", "wpt"):
            lat = nodo.attrib.get("lat")
            lon = nodo.attrib.get("lon")
            if lat is None or lon is None:
                continue
            nombre = ""
            for hijo in nodo:
                if hijo.tag.rsplit("}",1)[-1].lower() == "name":
                    nombre = (hijo.text or "").strip()
                    break
            puntos.append({
                "nombre": nombre or ("Punto " + str(len(puntos)+1)),
                "latitud": float(lat), "longitud": float(lon),
                "tipo": "inicio" if not puntos else "intermedio"
            })
    return puntos

def parsear_kml(contenido):
    raiz = ET.fromstring(contenido)
    puntos = []
    for nodo in raiz.iter():
        if nodo.tag.rsplit("}",1)[-1].lower() == "coordinates":
            texto = nodo.text or ""
            for elemento in re.split(r"\s+", texto.strip()):
                if not elemento:
                    continue
                partes = elemento.split(",")
                if len(partes) < 2:
                    continue
                lon, lat = float(partes[0]), float(partes[1])
                puntos.append({
                    "nombre": "Punto " + str(len(puntos)+1),
                    "latitud": lat, "longitud": lon,
                    "tipo": "inicio" if not puntos else "intermedio"
                })
    return puntos

def parsear_archivo_ruta(archivo):
    contenido = archivo.getvalue()
    extension = archivo.name.rsplit(".",1)[-1].lower()
    if extension == "gpx":
        puntos = parsear_gpx(contenido)
        formato = "gpx"
    elif extension == "kml":
        puntos = parsear_kml(contenido)
        formato = "kml"
    else:
        raise ValueError("Formato no admitido. Utiliza GPX o KML.")
    # Quitar duplicados consecutivos y validar coordenadas
    limpios = []
    anterior = None
    for p in puntos:
        lat, lon = p["latitud"], p["longitud"]
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        clave = (round(lat,7), round(lon,7))
        if clave != anterior:
            limpios.append(p)
            anterior = clave
    if len(limpios) < 2:
        raise ValueError("El archivo no contiene al menos dos coordenadas válidas.")
    limpios[0]["tipo"] = "inicio"
    limpios[-1]["tipo"] = "destino"
    return formato, limpios

def parsear_puntos_manual(texto):
    puntos = []
    for numero, linea in enumerate((texto or "").splitlines(), 1):
        linea = linea.strip()
        if not linea:
            continue
        partes = [x.strip() for x in linea.split(",")]
        if len(partes) != 3:
            raise ValueError(f"Línea {numero}: utiliza nombre,latitud,longitud.")
        nombre, lat_s, lon_s = partes
        lat, lon = float(lat_s), float(lon_s)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Línea {numero}: coordenadas fuera de rango.")
        puntos.append({"nombre": nombre or f"Punto {numero}",
                       "latitud": lat, "longitud": lon,
                       "tipo": "intermedio"})
    if len(puntos) >= 2:
        puntos[0]["tipo"] = "inicio"
        puntos[-1]["tipo"] = "destino"
    return puntos

def mostrar_mapa(puntos, mapa_id="mapa"):
    if not puntos or len(puntos) < 2:
        st.info("Todavía no hay suficientes coordenadas para dibujar el recorrido.")
        return
    datos = [{
        "lat": float(p["latitud"]), "lon": float(p["longitud"]),
        "name": str(p.get("nombre") or "Punto")
    } for p in puntos]
    datos_json = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html_mapa = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <style>html,body{{margin:0;padding:0;background:#000}}
    #map{{height:430px;width:100%;border:1px solid #806B00;border-radius:12px}}
    .leaflet-popup-content-wrapper,.leaflet-popup-tip{{background:#101010;color:#FFD400}}
    </style></head><body><div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
    const pts={datos_json};
    const map=L.map('map');
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
      {{maxZoom:19,attribution:'&copy; OpenStreetMap'}}).addTo(map);
    const coords=pts.map(p=>[p.lat,p.lon]);
    const line=L.polyline(coords,{{color:'#FFD400',weight:5,opacity:.9}}).addTo(map);
    pts.forEach((p,i)=>L.marker([p.lat,p.lon]).addTo(map)
      .bindPopup((i+1)+'. '+String(p.name).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]))));
    map.fitBounds(line.getBounds(),{{padding:[25,25]}});
    </script></body></html>
    """
    components.html(html_mapa, height=445, scrolling=False)

# =========================================================
# ADMINISTRACIÓN Y DATOS DE RUTAS DE COMUNIDAD
# =========================================================
def comprobar_admin(user_id):
    try:
        resultado = (supabase.table("familybike_admins").select("user_id")
                    .eq("user_id", user_id).limit(1).execute())
        return bool(resultado.data)
    except Exception as error:
        st.error("No se ha podido verificar el permiso de administrador.")
        st.code(str(error))
        return False

def cargar_puntos_ruta(ruta_id):
    return (supabase.table("rutas_comunidad_puntos")
            .select("id,ruta_id,orden,nombre,tipo,latitud,longitud")
            .eq("ruta_id", ruta_id).order("orden").execute().data or [])

def cargar_perfiles(ids):
    if not ids:
        return {}
    respuesta = (supabase.table("profiles")
                 .select("id,username,moto_foto_url")
                 .in_("id", list(set(ids))).execute())
    return {p["id"]:p for p in (respuesta.data or [])}

def insertar_ruta_comunidad(datos, puntos):
    respuesta = supabase.table("rutas_comunidad").insert(datos).execute()
    filas = respuesta.data or []
    if not filas:
        raise ValueError("Supabase no devolvió la ruta creada.")
    ruta_id = filas[0]["id"]
    if puntos:
        filas_puntos = []
        for orden, punto in enumerate(puntos, 1):
            filas_puntos.append({
                "ruta_id": ruta_id, "orden": orden,
                "nombre": punto["nombre"], "tipo": punto.get("tipo","intermedio"),
                "latitud": float(punto["latitud"]),
                "longitud": float(punto["longitud"])
            })
        supabase.table("rutas_comunidad_puntos").insert(filas_puntos).execute()
    return ruta_id

def toggle_favorito(ruta_id, user_id, ya_favorita):
    consulta = supabase.table("rutas_comunidad_favoritos")
    if ya_favorita:
        consulta.delete().eq("ruta_id", ruta_id).eq("user_id", user_id).execute()
    else:
        consulta.insert({"ruta_id":ruta_id,"user_id":user_id}).execute()

# =========================================================
# RESTAURAR SESIÓN
# =========================================================
autenticado = False
if st.session_state.get("access_token") and st.session_state.get("refresh_token"):
    try:
        supabase.auth.set_session(st.session_state["access_token"],
                                  st.session_state["refresh_token"])
        usuario = supabase.auth.get_user().user
        st.session_state["user_id"] = usuario.id
        if not st.session_state.get("username"):
            meta = getattr(usuario,"user_metadata",{}) or {}
            st.session_state["username"] = meta.get("username","motero")
        autenticado = True
    except Exception:
        cerrar_sesion()

# =========================================================
# ACCESO Y REGISTRO
# =========================================================
if not autenticado:
    c1, logo, c2 = st.columns([1,2,1])
    with logo:
        st.image(LOGO_URL, width=320)
    st.markdown('<div class="section-title">ACCESO A FAMILY BIKE</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Regístrate o inicia sesión para descubrir nuestras rutas.</div>',unsafe_allow_html=True)
    tab_login, tab_registro = st.tabs(["INICIAR SESIÓN","CREAR CUENTA"])
    with tab_login:
        with st.form("form_login"):
            usuario_login = st.text_input("Nombre de usuario",placeholder="Tu nombre de usuario")
            password_login = st.text_input("Contraseña",type="password")
            boton_login = st.form_submit_button("ENTRAR",use_container_width=True)
        if boton_login:
            username = usuario_login.strip().lower()
            if not username or not password_login:
                st.error("Introduce tu usuario y contraseña.")
            elif not re.fullmatch(r"[a-z0-9_]{3,24}",username):
                st.error("El nombre de usuario no es válido.")
            else:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email":email_interno(username),"password":password_login})
                    if guardar_sesion(response,username):
                        st.session_state["seccion_activa"]="menu"
                        st.rerun()
                    st.error("Supabase no ha devuelto una sesión.")
                except Exception:
                    st.error("Usuario o contraseña incorrectos. Comprueba tus datos.")
    with tab_registro:
        st.caption("El correo indicado será tu dirección de contacto. Accederás con usuario y contraseña.")
        with st.form("form_registro"):
            nuevo_usuario=st.text_input("Elige un nombre de usuario",placeholder="Ejemplo: motero_01")
            email_contacto=st.text_input("Tu correo electrónico real",placeholder="nombre@ejemplo.com")
            nueva_password=st.text_input("Elige una contraseña",type="password")
            repetir_password=st.text_input("Repite la contraseña",type="password")
            aceptar_avisos=st.checkbox("Acepto recibir por correo avisos de nuevas rutas y novedades.")
            boton_registro=st.form_submit_button("CREAR CUENTA",use_container_width=True)
        if boton_registro:
            username=nuevo_usuario.strip().lower()
            email_real=email_contacto.strip().lower()
            if not re.fullmatch(r"[a-z0-9_]{3,24}",username):
                st.error("El usuario debe tener entre 3 y 24 caracteres: letras, números o guion bajo.")
            elif not email_valido(email_real):
                st.error("Introduce un correo electrónico válido.")
            elif len(nueva_password)<8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            elif nueva_password!=repetir_password:
                st.error("Las contraseñas no coinciden.")
            else:
                try:
                    response=supabase.auth.sign_up({
                        "email":email_interno(username),"password":nueva_password,
                        "options":{"data":{"username":username}}})
                    if guardar_sesion(response,username):
                        guardar_datos_contacto(st.session_state["user_id"],email_real,aceptar_avisos)
                        st.session_state["seccion_activa"]="menu"
                        st.success("Cuenta creada correctamente.")
                        st.rerun()
                    st.warning("Registro recibido. Inicia sesión con tu usuario y contraseña.")
                except Exception as error:
                    st.error("ERROR AL CREAR LA CUENTA")
                    st.code(str(error))
    components.html(f"""
    <a href="{FACEBOOK_URL}" target="_blank" rel="noopener noreferrer"
    style="display:flex;align-items:center;gap:14px;padding:16px;background:#101010;
    border:1px solid #1877F2;border-radius:14px;text-decoration:none;font-family:Arial">
    <span style="background:#1877F2;color:white;border-radius:50%;padding:10px 15px;font-size:22px">f</span>
    <span><b style="color:#FFD400">ÚNETE A NUESTRA COMUNIDAD</b><br>
    <small style="color:#ccc">FAMILY BIKE · Grupo oficial de Facebook</small></span></a>
    """,height=80)
    st.markdown('<div class="footer"><b>FAMILY BIKE</b><br><br>CARRETERA · AVENTURA · LIBERTAD<br>© FAMILY BIKE</div>',unsafe_allow_html=True)
    st.stop()

# =========================================================
# USUARIO, PERFIL Y ADMIN
# =========================================================
usuario_id=st.session_state.get("user_id")
username_actual=st.session_state.get("username","Motero")
if not usuario_id:
    st.error("No se ha podido identificar tu usuario. Vuelve a iniciar sesión.")
    st.stop()
if "seccion_activa" not in st.session_state:
    st.session_state["seccion_activa"]="menu"
es_admin=comprobar_admin(usuario_id)

try:
    perfil=(supabase.table("profiles").select("moto_foto_url,username")
            .eq("id",usuario_id).maybe_single().execute().data or {})
    foto_moto_actual=perfil.get("moto_foto_url")
except Exception as error:
    foto_moto_actual=None
    st.warning("No se ha podido cargar el perfil.")
    st.code(str(error))

# CABECERA
cu, cm, cs=st.columns([2,2,1])
with cu:
    st.markdown(f'<div class="garaje-card"><div class="garaje-titulo">🏍️ FAMILY BIKE</div><div>Usuario: <b>{escapar(username_actual)}</b></div><div>Bienvenido a FAMILY BIKE</div></div>',unsafe_allow_html=True)
with cm:
    if foto_moto_actual:
        st.image(foto_moto_actual,caption="Tu motocicleta",use_container_width=True)
    else:
        st.markdown('<div class="garaje-card"><div class="garaje-titulo">MI MOTOCICLETA</div><div>Añade tu foto desde Mi garaje.</div></div>',unsafe_allow_html=True)
with cs:
    if st.button("CERRAR SESIÓN",use_container_width=True):
        cerrar_sesion()
        st.rerun()

# CARGAR CATÁLOGO
try:
    rutas=ordenar_rutas(supabase.table("rutas").select("id,nombre,url,imagen_url").execute().data or [])
except Exception as error:
    st.error("No se han podido cargar las rutas.")
    st.code(str(error))
    st.stop()

try:
    total_quedadas=supabase.table("quedadas").select("id",count="exact").eq("estado","abierta").gte("fecha",date.today().isoformat()).execute().count or 0
except Exception:
    total_quedadas=0

a,b=st.columns(2)
with a:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{len(rutas)}</div><div class="stat-label">RUTAS DISPONIBLES</div></div>',unsafe_allow_html=True)
with b:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{total_quedadas}</div><div class="stat-label">PRÓXIMAS QUEDADAS</div></div>',unsafe_allow_html=True)

# =========================================================
# MENÚ
# =========================================================
if st.session_state["seccion_activa"]=="menu":
    st.markdown('<div class="menu-intro"><div class="menu-intro-title">🏍️ ¿QUÉ TE APETECE HACER?</div><div>Selecciona una sección para continuar.</div></div>',unsafe_allow_html=True)
    menu_items=[
        ("🏍️ EXPLORAR RUTAS","rutas"),("📅 QUEDADAS MOTERAS","quedadas"),
        ("🏁 MI GARAJE","garaje"),("👥 COMUNIDAD","comunidad"),
        ("🗺️ RUTAS DE LA COMUNIDAD","rutas_comunidad"),("🛒 TIENDA FAMILY BIKE","tienda")]
    for fila in range(0,len(menu_items),2):
        cols=st.columns(2)
        for col,(label,seccion) in zip(cols,menu_items[fila:fila+2]):
            with col:
                if st.button(label,key=f"menu_{seccion}",type="secondary",use_container_width=True):
                    st.session_state["seccion_activa"]=seccion
                    st.rerun()
else:
    if st.button("← VOLVER AL MENÚ PRINCIPAL",key="volver_menu",type="secondary",use_container_width=True):
        st.session_state["seccion_activa"]="menu"
        st.rerun()

# =========================================================
# EXPLORAR RUTAS CATÁLOGO
# =========================================================
if st.session_state["seccion_activa"]=="rutas":
    st.markdown('<div class="section-title">EXPLORA LAS RUTAS</div><div class="section-subtitle">Encuentra tu próximo destino y disfruta de la carretera.</div>',unsafe_allow_html=True)
    busqueda=st.text_input("Buscar ruta",placeholder="Escribe el nombre de una ruta...",key="buscar_ruta")
    filtradas=[r for r in rutas if busqueda.lower() in str(r.get("nombre","")).lower()]
    if not filtradas:
        st.info("No hay rutas que coincidan con tu búsqueda.")
    else:
        cols=st.columns(3)
        for i,ruta in enumerate(filtradas):
            with cols[i%3]:
                imagen=ruta.get("imagen_url") or IMAGEN_PREDETERMINADA
                st.image(imagen,use_container_width=True)
                st.markdown(f'<div class="route-card"><div class="route-number">RUTA {i+1:02d}</div><div class="route-name">{escapar(ruta.get("nombre"))}</div></div>',unsafe_allow_html=True)
                url=ruta.get("url") or ""
                if url.startswith(("https://","http://")):
                    st.link_button("VER RECORRIDO ↗",url,use_container_width=True)

# =========================================================
# QUEDADAS MOTERAS
# =========================================================
if st.session_state["seccion_activa"]=="quedadas":
    st.markdown('<div class="section-title">QUEDADAS MOTERAS</div><div class="section-subtitle">Organiza una salida, invita a otros moteros y comparte carretera.</div>',unsafe_allow_html=True)
    with st.expander("➕ CREAR UNA NUEVA QUEDADA"):
        tipo=st.radio("Tipo de salida",["Ruta del catálogo","Destino libre"],horizontal=True,key="tipo_destino_quedada")
        destino=(st.selectbox("Selecciona una ruta",[r.get("nombre","") for r in rutas],key="ruta_catalogo_quedada")
                 if tipo=="Ruta del catálogo" and rutas else "")
        if tipo=="Destino libre":
            destino=st.text_input("Escribe tu ruta o destino",key="destino_libre_quedada")
        with st.form("form_nueva_quedada"):
            fecha_q=st.date_input("Fecha",value=date.today(),min_value=date.today(),format="DD/MM/YYYY")
            hora_q=st.time_input("Primera hora de salida",value=time(9,0))
            punto=st.text_input("Primer punto de encuentro")
            add2=st.checkbox("Añadir una segunda hora de salida")
            hora2=st.time_input("Segunda hora",value=time(10,0),key="hora_salida_2")
            punto2=st.text_input("Punto de encuentro segunda salida",key="punto_salida_2")
            add3=st.checkbox("Añadir una tercera hora de salida")
            hora3=st.time_input("Tercera hora",value=time(11,0),key="hora_salida_3")
            punto3=st.text_input("Punto de encuentro tercera salida",key="punto_salida_3")
            descripcion=st.text_area("Descripción de la salida")
            telefono=st.text_input("Teléfono de contacto del organizador")
            cartel=st.file_uploader("Cartel o fotografía (opcional)",type=["jpg","jpeg","png","webp"],key="cartel_quedada")
            imagen_alt=st.text_input("O URL de una fotografía (opcional)")
            publicar=st.form_submit_button("PUBLICAR QUEDADA",use_container_width=True)
        if publicar:
            if not destino.strip():
                st.error("Introduce el nombre de la ruta o destino.")
            elif not punto.strip() or (add2 and not punto2.strip()) or (add3 and not punto3.strip()):
                st.error("Completa todos los puntos de encuentro.")
            elif imagen_alt.strip() and not imagen_alt.strip().startswith(("https://","http://")):
                st.error("La URL de la fotografía no es válida.")
            else:
                try:
                    imagen_final=imagen_alt.strip()
                    if tipo=="Ruta del catálogo" and not imagen_final:
                        imagen_final=next((r.get("imagen_url") or "" for r in rutas if r.get("nombre")==destino),"")
                    cartel_url=""
                    if cartel:
                        cartel_url,_=subir_archivo_storage(cartel,f"quedadas/{usuario_id}","cartel")
                        imagen_final=cartel_url
                    elif imagen_final:
                        cartel_url=imagen_final
                    nueva={"creador_id":usuario_id,"ruta_nombre":destino.strip(),
                           "es_ruta_catalogo":tipo=="Ruta del catálogo","fecha":fecha_q.isoformat(),
                           "hora":hora_q.strftime("%H:%M:%S"),"punto_encuentro":punto.strip(),
                           "descripcion":descripcion.strip(),"imagen_url":imagen_final,
                           "cartel_url":cartel_url,"telefono_organizador":telefono.strip(),"estado":"abierta"}
                    filas=supabase.table("quedadas").insert(nueva).execute().data or []
                    if not filas: raise ValueError("Supabase no devolvió la quedada creada.")
                    qid=filas[0]["id"]
                    horarios=[{"quedada_id":qid,"hora":hora_q.strftime("%H:%M:%S"),"punto_encuentro":punto.strip()}]
                    if add2: horarios.append({"quedada_id":qid,"hora":hora2.strftime("%H:%M:%S"),"punto_encuentro":punto2.strip()})
                    if add3: horarios.append({"quedada_id":qid,"hora":hora3.strftime("%H:%M:%S"),"punto_encuentro":punto3.strip()})
                    supabase.table("horarios_quedadas").insert(horarios).execute()
                    st.success("¡Quedada publicada correctamente!")
                    try:
                        avisos=crear_notificaciones_quedada(qid,usuario_id)
                        st.info(f"Notificaciones pendientes creadas: {avisos['creadas']}")
                    except Exception as err:
                        st.warning("La quedada se publicó, pero falló la creación de notificaciones.")
                        st.code(str(err))
                    st.rerun()
                except Exception as error:
                    st.error("No se ha podido publicar la quedada.")
                    st.code(str(error))

    try:
        quedadas=(supabase.table("quedadas").select(
            "id,creador_id,ruta_nombre,es_ruta_catalogo,fecha,hora,punto_encuentro,descripcion,"
            "imagen_url,cartel_url,telefono_organizador,estado,created_at")
            .eq("estado","abierta").gte("fecha",date.today().isoformat()).order("fecha").execute().data or [])
    except Exception as error:
        st.error("No se han podido cargar las quedadas.")
        st.code(str(error)); quedadas=[]
    ids_q=[q["id"] for q in quedadas]
    horarios_por={}
    asistentes_por={}
    perfiles={}
    if ids_q:
        try:
            hs=supabase.table("horarios_quedadas").select("id,quedada_id,hora,punto_encuentro").in_("quedada_id",ids_q).order("hora").execute().data or []
            for h in hs: horarios_por.setdefault(h["quedada_id"],[]).append(h)
            asistentes=supabase.table("asistentes").select("quedada_id,usuario_id,horario_id").in_("quedada_id",ids_q).execute().data or []
            for x in asistentes: asistentes_por.setdefault(x["quedada_id"],[]).append(x)
            ids_users={x["usuario_id"] for x in asistentes}|{q["creador_id"] for q in quedadas}
            perfiles=cargar_perfiles(ids_users)
        except Exception as error:
            st.warning("No se han podido cargar todos los horarios o asistentes.")
            st.code(str(error))
    if not quedadas:
        st.info("Todavía no hay quedadas publicadas. ¡Organiza la primera!")
    for q in quedadas:
        qid=q["id"]; creador=q["creador_id"]
        asistentes=asistentes_por.get(qid,[])
        mi_asistencia=next((x for x in asistentes if str(x["usuario_id"])==str(usuario_id)),None)
        perfil_creador=perfiles.get(creador,{})
        imagen=q.get("cartel_url") or q.get("imagen_url") or IMAGEN_PREDETERMINADA
        with st.container(border=True):
            st.image(imagen,use_container_width=True)
            st.markdown(f"## 🏍️ {escapar(q.get('ruta_nombre'))}")
            st.write(f"📅 **Fecha:** {q.get('fecha')}  ·  **Organiza:** {escapar(perfil_creador.get('username','Motero'))}")
            if q.get("telefono_organizador"):
                tel=re.sub(r"[^0-9+]","",q["telefono_organizador"])
                st.markdown(f"📞 **Contacto:** {escapar(q['telefono_organizador'])} · [Llamar](tel:{tel})")
            if q.get("descripcion"): st.write(q["descripcion"])
            hs=horarios_por.get(qid) or [{"id":None,"hora":q.get("hora","09:00"),"punto_encuentro":q.get("punto_encuentro","")}]
            st.markdown("#### 🕘 HORARIOS Y PUNTOS DE SALIDA")
            for h in hs: st.write(f"🕘 **{str(h.get('hora',''))[:5]}** — 📍 {h.get('punto_encuentro','')}")
            if q.get("es_ruta_catalogo"):
                r=next((x for x in rutas if x.get("nombre")==q.get("ruta_nombre")),None)
                if r and str(r.get("url","")).startswith("http"): st.link_button("VER RECORRIDO EN GOOGLE MAPS ↗",r["url"])
            st.write(f"**🏍️ Moteros apuntados: {len(asistentes)}**")
            with st.expander("👥 VER QUIÉN VA"):
                if not asistentes: st.write("Todavía no hay asistentes.")
                for x in asistentes:
                    p=perfiles.get(x["usuario_id"],{})
                    st.write("🏍️ "+str(p.get("username","Motero")))
            if mi_asistencia:
                hs_ids=[h for h in hs if h.get("id") is not None]
                if hs_ids:
                    actual=next((i for i,h in enumerate(hs_ids) if str(h["id"])==str(mi_asistencia.get("horario_id"))),0)
                    elegido=st.selectbox("Cambiar horario",range(len(hs_ids)),
                        format_func=lambda i:f"{str(hs_ids[i]['hora'])[:5]} — {hs_ids[i]['punto_encuentro']}",
                        index=actual,key=f"cambiar_horario_{qid}")
                    c1,c2=st.columns(2)
                    with c1:
                        if st.button("CAMBIAR HORARIO",key=f"guardar_horario_{qid}",use_container_width=True):
                            try:
                                supabase.table("asistentes").update({"horario_id":hs_ids[elegido]["id"]}).eq("quedada_id",qid).eq("usuario_id",usuario_id).execute()
                                st.success("Horario actualizado."); st.rerun()
                            except Exception as error: st.error(str(error))
                    with c2:
                        if st.button("CANCELAR MI ASISTENCIA",key=f"salir_{qid}",use_container_width=True):
                            try:
                                supabase.table("asistentes").delete().eq("quedada_id",qid).eq("usuario_id",usuario_id).execute()
                                st.success("Asistencia cancelada."); st.rerun()
                            except Exception as error: st.error(str(error))
                else:
                    if st.button("CANCELAR MI ASISTENCIA",key=f"salir_{qid}"):
                        supabase.table("asistentes").delete().eq("quedada_id",qid).eq("usuario_id",usuario_id).execute(); st.rerun()
            else:
                opciones=range(len(hs))
                elegido=st.selectbox("Selecciona hora y punto de salida",opciones,
                    format_func=lambda i:f"{str(hs[i]['hora'])[:5]} — {hs[i]['punto_encuentro']}",
                    key=f"elegir_horario_{qid}")
                if st.button("🏍️ ME APUNTO",key=f"apuntarme_{qid}",use_container_width=True):
                    try:
                        supabase.table("asistentes").insert({"quedada_id":qid,"usuario_id":usuario_id,
                            "horario_id":hs[elegido].get("id")}).execute()
                        st.success("¡Ya estás apuntado!"); st.rerun()
                    except Exception as error:
                        st.error("No se ha podido registrar la asistencia. Puede que ya estés apuntado.")
                        st.code(str(error))
            if str(creador)==str(usuario_id):
                if st.button("CANCELAR QUEDADA",key=f"cancelar_{qid}",use_container_width=True):
                    try:
                        supabase.table("quedadas").update({"estado":"cancelada"}).eq("id",qid).eq("creador_id",usuario_id).execute()
                        st.success("Quedada cancelada."); st.rerun()
                    except Exception as error: st.error(str(error))

# =========================================================
# MI GARAJE
# =========================================================
if st.session_state["seccion_activa"]=="garaje":
    st.markdown('<div class="section-title">🏁 MI GARAJE</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="garaje-card"><div class="garaje-titulo">GARAJE DE {escapar(username_actual.upper())}</div><div>Tu motocicleta en FAMILY BIKE.</div></div>',unsafe_allow_html=True)
    if foto_moto_actual: st.image(foto_moto_actual,use_container_width=True,caption=f"Motocicleta de {username_actual}")
    else: st.info("Todavía no has añadido una fotografía.")
    foto=st.file_uploader("Añadir o cambiar fotografía",type=["jpg","jpeg","png","webp"],key="foto_moto_garaje")
    if foto:
        st.image(foto,caption="Vista previa",use_container_width=True)
        if st.button("GUARDAR EN MI GARAJE",use_container_width=True):
            try:
                url,_=subir_archivo_storage(foto,f"garaje/{usuario_id}","moto")
                supabase.table("profiles").update({"moto_foto_url":url}).eq("id",usuario_id).execute()
                st.success("Fotografía guardada."); st.rerun()
            except Exception as error: st.error("No se ha podido guardar la fotografía."); st.code(str(error))

# =========================================================
# COMUNIDAD
# =========================================================
if st.session_state["seccion_activa"]=="comunidad":
    st.markdown('<div class="section-title">👥 COMUNIDAD FAMILY BIKE</div>',unsafe_allow_html=True)
    st.write("Conoce a otros moteros de FAMILY BIKE y descubre sus motocicletas.")
    try:
        perfiles_all=supabase.table("profiles").select("id,username,moto_foto_url").order("username").execute().data or []
        miembros=[p for p in perfiles_all if str(p.get("moto_foto_url","")).startswith(("http://","https://"))]
        st.markdown(f'<div class="stat-box"><div class="stat-number">{len(miembros)}</div><div class="stat-label">MOTEROS CON FOTOGRAFÍA EN SU GARAJE</div></div>',unsafe_allow_html=True)
        cols=st.columns(3)
        for i,p in enumerate(miembros):
            with cols[i%3]:
                with st.container(border=True):
                    st.image(p["moto_foto_url"],use_container_width=True)
                    st.markdown(f'<div class="community-name">{escapar(p.get("username","Motero"))}</div><div class="community-label">🏍️ MIEMBRO FAMILY BIKE</div>',unsafe_allow_html=True)
                    if str(p["id"])==str(usuario_id): st.caption("★ TU MOTOCICLETA")
        if not miembros: st.info("Todavía no hay fotografías de motocicletas. ¡Sé el primero!")
    except Exception as error:
        st.error("No se ha podido cargar la comunidad."); st.code(str(error))

# =========================================================
# RUTAS DE LA COMUNIDAD
# =========================================================
if st.session_state["seccion_activa"]=="rutas_comunidad":
    st.markdown('<div class="section-title">🗺️ RUTAS DE LA COMUNIDAD</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Comparte recorridos GPX/KML, descubre rutas de otros moteros y guarda tus favoritas.</div>',unsafe_allow_html=True)
    pestañas=["EXPLORAR","PUBLICAR RUTA","MIS RUTAS","FAVORITOS"]
    if es_admin: pestañas.append("ADMINISTRAR")
    tabs=st.tabs(pestañas)

    # EXPLORAR: solo aprobadas
    with tabs[0]:
        busqueda_com=st.text_input("Buscar rutas de la comunidad",key="buscar_comunidad",placeholder="Título, origen o destino...")
        try:
            publicadas=(supabase.table("rutas_comunidad")
                        .select("id,user_id,titulo,origen,destino,descripcion,google_maps_url,kilometros,duracion_minutos,imagen_url,archivo_ruta_url,formato_archivo,created_at")
                        .eq("estado","aprobada").order("created_at",desc=True).execute().data or [])
            publicadas=[r for r in publicadas if busqueda_com.lower() in " ".join(str(r.get(k) or "") for k in ["titulo","origen","destino","descripcion"]).lower()]
            favoritos=(supabase.table("rutas_comunidad_favoritos").select("ruta_id").eq("user_id",usuario_id).execute().data or [])
            fav_ids={x["ruta_id"] for x in favoritos}
            perfiles_pub=cargar_perfiles([r["user_id"] for r in publicadas])
            if not publicadas: st.info("Todavía no hay rutas aprobadas. ¡Publica la primera!")
            for r in publicadas:
                rid=r["id"]; autor=perfiles_pub.get(r["user_id"],{})
                puntos=cargar_puntos_ruta(rid)
                with st.container(border=True):
                    if r.get("imagen_url"): st.image(r["imagen_url"],use_container_width=True)
                    st.markdown(f"### 🏍️ {escapar(r.get('titulo'))}")
                    st.write(f"**Origen:** {r.get('origen')}  ·  **Destino:** {r.get('destino')}")
                    st.caption(f"Publicada por {autor.get('username','Motero')} · {str(r.get('created_at',''))[:10]}")
                    if r.get("descripcion"): st.write(r["descripcion"])
                    datos=[]
                    if r.get("kilometros") is not None: datos.append(f"{r['kilometros']} km")
                    if r.get("duracion_minutos") is not None: datos.append(f"{r['duracion_minutos']} min")
                    if datos: st.write(" · ".join(datos))
                    if r.get("google_maps_url","").startswith(("https://","http://")):
                        st.link_button("ABRIR EN GOOGLE MAPS ↗",r["google_maps_url"])
                    if r.get("archivo_ruta_url","").startswith(("https://","http://")):
                        st.link_button(f"DESCARGAR ARCHIVO {str(r.get('formato_archivo') or '').upper()} ↗",r["archivo_ruta_url"])
                    if len(puntos)>=2:
                        with st.expander("VER MAPA Y PUNTOS DEL RECORRIDO"):
                            mostrar_mapa(puntos,f"mapa_publico_{rid}")
                            for p in puntos: st.write(f"{p['orden']}. {p['nombre']} — {p['latitud']:.6f}, {p['longitud']:.6f}")
                    c1,c2=st.columns([1,3])
                    with c1:
                        if st.button("★ QUITAR FAVORITO" if rid in fav_ids else "☆ AÑADIR FAVORITO",key=f"fav_{rid}"):
                            try:
                                toggle_favorito(rid,usuario_id,rid in fav_ids); st.rerun()
                            except Exception as error: st.error("No se pudo actualizar el favorito."); st.code(str(error))
        except Exception as error:
            st.error("No se han podido cargar las rutas aprobadas.")
            st.code(str(error))

    # PUBLICAR
    with tabs[1]:
        st.markdown("### PUBLICAR UNA NUEVA RUTA")
        st.info("Todas las rutas nuevas quedan PENDIENTES y no serán visibles para la comunidad hasta que un administrador las apruebe.")
        with st.form("form_publicar_ruta_comunidad"):
            titulo=st.text_input("Título de la ruta*",placeholder="Ejemplo: Sierra de Cádiz por Grazalema")
            origen=st.text_input("Origen*",placeholder="Ejemplo: San Fernando")
            destino=st.text_input("Destino*",placeholder="Ejemplo: Zahara de la Sierra")
            descripcion_ruta=st.text_area("Descripción",placeholder="Estado del firme, paradas, recomendaciones...")
            maps_url=st.text_input("Enlace de Google Maps (opcional)",placeholder="https://maps.google.com/...")
            ckm,cmin=st.columns(2)
            with ckm: km=st.number_input("Kilómetros (opcional)",min_value=0.0,step=1.0,value=0.0)
            with cmin: minutos=st.number_input("Duración en minutos (opcional)",min_value=0,step=5,value=0)
            foto_ruta=st.file_uploader("Fotografía de la ruta (opcional)",type=["jpg","jpeg","png","webp"],key="foto_ruta_comunidad")
            archivo_ruta=st.file_uploader("Archivo de recorrido GPX o KML (opcional)",type=["gpx","kml"],key="archivo_ruta_comunidad")
            st.markdown("**O introduce puntos manualmente** (una línea por punto: `nombre,latitud,longitud`).")
            puntos_manual=st.text_area("Puntos intermedios",placeholder="Salida,36.000000,-6.000000\nMirador,36.100000,-5.900000\nDestino,36.200000,-5.800000")
            enviar_ruta=st.form_submit_button("ENVIAR RUTA PARA APROBACIÓN",use_container_width=True)
        if enviar_ruta:
            if not titulo.strip() or not origen.strip() or not destino.strip():
                st.error("Título, origen y destino son obligatorios.")
            elif maps_url.strip() and not maps_url.strip().startswith(("https://","http://")):
                st.error("El enlace de Google Maps debe comenzar por http:// o https://.")
            else:
                try:
                    puntos=[]
                    formato=None
                    archivo_url=None
                    archivo_path=None
                    if archivo_ruta is not None:
                        formato,puntos=parsear_archivo_ruta(archivo_ruta)
                        archivo_url,archivo_path=subir_archivo_storage(archivo_ruta,f"rutas_comunidad/{usuario_id}","recorrido")
                    puntos_texto=parsear_puntos_manual(puntos_manual)
                    if puntos and puntos_texto:
                        st.warning("Se utilizarán los puntos del archivo GPX/KML; se ignoran los puntos manuales.")
                    elif puntos_texto:
                        puntos=puntos_texto
                    foto_url=None
                    if foto_ruta is not None:
                        foto_url,_=subir_archivo_storage(foto_ruta,f"rutas_comunidad/{usuario_id}","foto")
                    datos={
                        "user_id":usuario_id,"titulo":titulo.strip(),"origen":origen.strip(),
                        "destino":destino.strip(),"descripcion":descripcion_ruta.strip() or None,
                        "google_maps_url":maps_url.strip() or None,
                        "kilometros":float(km) if km>0 else None,
                        "duracion_minutos":int(minutos) if minutos>0 else None,
                        "imagen_url":foto_url,"archivo_ruta_url":archivo_url,
                        "archivo_ruta_path":archivo_path,"formato_archivo":formato,
                        "estado":"pendiente"
                    }
                    rid=insertar_ruta_comunidad(datos,puntos)
                    st.success("Ruta enviada correctamente. Queda pendiente de aprobación.")
                    st.caption(f"Referencia de la ruta: {rid}")
                    st.rerun()
                except Exception as error:
                    st.error("No se ha podido publicar la ruta.")
                    st.code(str(error))

    # MIS RUTAS
    with tabs[2]:
        st.markdown("### MIS RUTAS PUBLICADAS")
        try:
            mis=(supabase.table("rutas_comunidad")
                 .select("id,titulo,origen,destino,estado,motivo_rechazo,created_at,google_maps_url,archivo_ruta_url,formato_archivo")
                 .eq("user_id",usuario_id).order("created_at",desc=True).execute().data or [])
            if not mis: st.info("Todavía no has enviado ninguna ruta.")
            for r in mis:
                with st.container(border=True):
                    st.markdown(f"**{escapar(r.get('titulo'))}**")
                    st.write(f"{r.get('origen')} → {r.get('destino')}")
                    estado=r.get("estado","pendiente")
                    if estado=="aprobada": st.success("APROBADA · Visible para la comunidad")
                    elif estado=="rechazada":
                        st.error("RECHAZADA")
                        if r.get("motivo_rechazo"): st.write("Motivo: "+r["motivo_rechazo"])
                    else: st.warning("PENDIENTE DE REVISIÓN")
                    st.caption(str(r.get("created_at",""))[:10])
        except Exception as error:
            st.error("No se han podido cargar tus rutas.")
            st.code(str(error))

    # FAVORITOS
    with tabs[3]:
        st.markdown("### MIS RUTAS FAVORITAS")
        try:
            favs=supabase.table("rutas_comunidad_favoritos").select("ruta_id").eq("user_id",usuario_id).execute().data or []
            fav_ids=[x["ruta_id"] for x in favs]
            if not fav_ids: st.info("Todavía no has guardado rutas favoritas.")
            else:
                favoritas=supabase.table("rutas_comunidad").select("id,titulo,origen,destino,descripcion,google_maps_url,archivo_ruta_url,formato_archivo,kilometros,duracion_minutos,imagen_url,user_id").in_("id",fav_ids).eq("estado","aprobada").execute().data or []
                perfiles_fav=cargar_perfiles([r["user_id"] for r in favoritas])
                for r in favoritas:
                    with st.container(border=True):
                        if r.get("imagen_url"): st.image(r["imagen_url"],use_container_width=True)
                        st.markdown(f"**{escapar(r['titulo'])}**")
                        st.write(f"{r['origen']} → {r['destino']}")
                        st.caption("Por "+perfiles_fav.get(r["user_id"],{}).get("username","Motero"))
                        if r.get("google_maps_url"): st.link_button("GOOGLE MAPS ↗",r["google_maps_url"])
                        if st.button("QUITAR DE FAVORITOS",key=f"del_fav_{r['id']}"):
                            toggle_favorito(r["id"],usuario_id,True); st.rerun()
        except Exception as error:
            st.error("No se han podido cargar tus favoritos.")
            st.code(str(error))

    # ADMINISTRAR
    if es_admin:
        with tabs[4]:
            st.markdown("### MODERACIÓN DE RUTAS")
            st.caption("Solo los usuarios registrados en familybike_admins pueden aprobar o rechazar publicaciones.")
            try:
                pendientes=(supabase.table("rutas_comunidad")
                            .select("id,user_id,titulo,origen,destino,descripcion,google_maps_url,kilometros,duracion_minutos,imagen_url,archivo_ruta_url,formato_archivo,created_at")
                            .eq("estado","pendiente").order("created_at").execute().data or [])
                perfiles_pend=cargar_perfiles([r["user_id"] for r in pendientes])
                if not pendientes: st.success("No hay rutas pendientes de revisión.")
                for r in pendientes:
                    rid=r["id"]; puntos=cargar_puntos_ruta(rid)
                    with st.container(border=True):
                        st.markdown(f"### {escapar(r['titulo'])}")
                        st.write(f"**Origen:** {r['origen']} · **Destino:** {r['destino']}")
                        st.caption(f"Autor: {perfiles_pend.get(r['user_id'],{}).get('username','Motero')} · {str(r.get('created_at',''))[:10]}")
                        if r.get("descripcion"): st.write(r["descripcion"])
                        if r.get("imagen_url"): st.image(r["imagen_url"],use_container_width=True)
                        if r.get("google_maps_url"): st.link_button("ABRIR GOOGLE MAPS ↗",r["google_maps_url"])
                        if r.get("archivo_ruta_url"): st.link_button("DESCARGAR GPX/KML ↗",r["archivo_ruta_url"])
                        if len(puntos)>=2:
                            with st.expander("VER MAPA DEL RECORRIDO"):
                                mostrar_mapa(puntos,f"mapa_admin_{rid}")
                        motivo=st.text_input("Motivo del rechazo (solo si rechazas)",key=f"motivo_{rid}")
                        ca,cr=st.columns(2)
                        with ca:
                            if st.button("✓ APROBAR RUTA",key=f"aprobar_{rid}",use_container_width=True):
                                try:
                                    supabase.table("rutas_comunidad").update({
                                        "estado":"aprobada","revisado_por":usuario_id,
                                        "revisado_at":datetime.now(timezone.utc).isoformat(),
                                        "motivo_rechazo":None
                                    }).eq("id",rid).eq("estado","pendiente").execute()
                                    st.success("Ruta aprobada y publicada.")
                                    st.rerun()
                                except Exception as error:
                                    st.error("No se ha podido aprobar la ruta."); st.code(str(error))
                        with cr:
                            if st.button("✕ RECHAZAR RUTA",key=f"rechazar_{rid}",use_container_width=True):
                                if not motivo.strip():
                                    st.error("Escribe un motivo para el rechazo.")
                                else:
                                    try:
                                        supabase.table("rutas_comunidad").update({
                                            "estado":"rechazada","revisado_por":usuario_id,
                                            "revisado_at":datetime.now(timezone.utc).isoformat(),
                                            "motivo_rechazo":motivo.strip()
                                        }).eq("id",rid).eq("estado","pendiente").execute()
                                        st.warning("Ruta rechazada.")
                                        st.rerun()
                                    except Exception as error:
                                        st.error("No se ha podido rechazar la ruta."); st.code(str(error))
            except Exception as error:
                st.error("No se han podido cargar las rutas pendientes.")
                st.code(str(error))

# =========================================================
# TIENDA
# =========================================================
if st.session_state["seccion_activa"]=="tienda":
    st.markdown('<div class="section-title">🛒 TIENDA FAMILY BIKE</div>',unsafe_allow_html=True)
    st.markdown('<div class="tienda-card"><div class="tienda-titulo">🏍️ TIENDA FAMILY BIKE</div><div>Equípate para tus próximas aventuras. Visita nuestra tienda y descubre lo que tenemos preparado.</div></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2: st.link_button("🛒 ENTRAR EN LA TIENDA",TIENDA_URL,use_container_width=True)
    st.caption("La tienda se abrirá en Payhip.")

# =========================================================
# PIE DE PÁGINA
# =========================================================
st.markdown('<div class="footer"><b>FAMILY BIKE</b><br><br>CARRETERA · AVENTURA · LIBERTAD<br>© FAMILY BIKE</div>',unsafe_allow_html=True)
