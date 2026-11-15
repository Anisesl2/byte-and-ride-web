
import os
import json
import html
import urllib.request
import urllib.error

from datetime import datetime, timezone, timedelta
from supabase import create_client


# ==================================================
# CONFIGURACIÓN
# ==================================================

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]

FAMILY_BIKE_URL = os.environ.get(
    "FAMILY_BIKE_URL",
    "https://familybike.es"
)

REMITENTE = "FAMILY BIKE <avisos@send.familybike.es>"

TABLA_NOTIFICACIONES = "notificaciones_quedadas"

MAX_NOTIFICACIONES = 50

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==================================================
# FECHAS
# ==================================================

def ahora():
    return datetime.now(timezone.utc)


def fecha_iso(valor):
    return valor.isoformat()


# ==================================================
# NORMALIZAR RESPUESTAS DE SUPABASE
# ==================================================

def convertir_registros(datos, origen):

    if datos is None:
        return []

    if isinstance(datos, str):

        datos = datos.strip()

        if not datos:
            print(f"{origen}: respuesta vacía.")
            return []

        try:
            datos = json.loads(datos)

        except json.JSONDecodeError as error:

            raise RuntimeError(
                f"{origen}: respuesta no válida. "
                f"{repr(datos[:1000])}. Error: {error}"
            )

    if isinstance(datos, dict):
        datos = [datos]

    if not isinstance(datos, list):

        raise RuntimeError(
            f"{origen}: formato inesperado. "
            f"Tipo: {type(datos).__name__}"
        )

    registros = []

    for indice, elemento in enumerate(datos):

        if isinstance(elemento, str):

            try:
                elemento = json.loads(elemento)

            except json.JSONDecodeError as error:

                raise RuntimeError(
                    f"{origen}: registro {indice} "
                    f"no contiene JSON válido: {error}"
                )

        if not isinstance(elemento, dict):

            raise RuntimeError(
                f"{origen}: registro {indice} "
                f"no es un diccionario."
            )

        registros.append(elemento)

    return registros


# ==================================================
# ENVÍO DE EMAIL CON RESEND
# ==================================================

def enviar_email(
    destinatario,
    asunto,
    contenido_html,
    contenido_texto,
    clave
):

    datos = {
        "from": REMITENTE,
        "to": [destinatario],
        "subject": asunto,
        "html": contenido_html,
        "text": contenido_texto
    }

    peticion = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(datos).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            "Idempotency-Key": clave
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            peticion,
            timeout=30
        ) as respuesta:

            contenido = respuesta.read().decode("utf-8")

            return json.loads(contenido)

    except urllib.error.HTTPError as error:

        detalle = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"Resend HTTP {error.code}: {detalle}"
        )

    except urllib.error.URLError as error:

        raise RuntimeError(
            f"Error de conexión con Resend: {error}"
        )


# ==================================================
# CONSTRUIR CORREO
# ==================================================

def construir_correo(quedada):

    nombre = html.escape(
        str(quedada.get("ruta_nombre") or "Nueva quedada")
    )

    fecha = html.escape(
        str(quedada.get("fecha") or "")
    )

    hora = html.escape(
        str(quedada.get("hora") or "")[:5]
    )

    punto = html.escape(
        str(quedada.get("punto_encuentro") or "")
    )

    descripcion = html.escape(
        str(quedada.get("descripcion") or "")
    )

    enlace = html.escape(
        FAMILY_BIKE_URL,
        quote=True
    )

    cuerpo = f"""
    <div style="background:#101114;color:#f5f5f5;
    padding:30px;font-family:Arial,sans-serif;
    border-radius:14px;max-width:600px;margin:auto;">

        <h1 style="color:#f0a43a;text-align:center;">
            FAMILY BIKE
        </h1>

        <h2>¡Nueva quedada motera!</h2>

        <p>
            Se ha publicado una nueva salida en FAMILY BIKE.
        </p>

        <div style="background:#1b1e24;padding:20px;
        border-radius:12px;border:1px solid #393d45;">

            <h2 style="color:#f0a43a;">
                🏍️ {nombre}
            </h2>

            <p>📅 <strong>Fecha:</strong> {fecha}</p>

            <p>🕘 <strong>Hora:</strong> {hora}</p>

            <p>
                📍 <strong>Punto de encuentro:</strong> {punto}
            </p>

            <p>{descripcion}</p>

        </div>

        <p style="text-align:center;margin-top:30px;">

            <a href="{enlace}"
            style="display:inline-block;background:#f0a43a;
            color:#151515;padding:14px 24px;
            border-radius:8px;text-decoration:none;
            font-weight:bold;">

                ENTRAR Y APUNTARME

            </a>

        </p>

        <p style="color:#999da5;font-size:12px;
        text-align:center;">

            Recibes este aviso porque tienes activadas
            las notificaciones de FAMILY BIKE.

        </p>

    </div>
    """

    texto = (
        "FAMILY BIKE - Nueva quedada motera\n\n"
        f"{quedada.get('ruta_nombre', '')}\n"
        f"Fecha: {quedada.get('fecha', '')}\n"
        f"Hora: {str(quedada.get('hora', ''))[:5]}\n"
        f"Punto de encuentro: "
        f"{quedada.get('punto_encuentro', '')}\n\n"
        f"{quedada.get('descripcion', '')}\n\n"
        f"Entra para apuntarte: {FAMILY_BIKE_URL}"
    )

    return cuerpo, texto


# ==================================================
# ACTUALIZAR NOTIFICACIÓN
# ==================================================

def actualizar_notificacion(notificacion_id, datos):

    (
        supabase.table(TABLA_NOTIFICACIONES)
        .update(datos)
        .eq("id", notificacion_id)
        .execute()
    )


# ==================================================
# PROCESAR NOTIFICACIONES
# ==================================================

def procesar():

    ahora_dt = ahora()

    ahora_texto = fecha_iso(ahora_dt)

    limite = fecha_iso(
        ahora_dt - timedelta(minutes=15)
    )

    print("--------------------------------")
    print("FAMILY BIKE - PROCESADOR DE EMAIL")
    print("--------------------------------")

    # ----------------------------------------------
    # RECUPERAR PROCESOS BLOQUEADOS
    # ----------------------------------------------

    print("Comprobando notificaciones bloqueadas...")

    (
        supabase.table(TABLA_NOTIFICACIONES)
        .update({
            "estado": "pendiente",
            "procesando_desde": None,
            "proximo_intento": ahora_texto
        })
        .eq("estado", "procesando")
        .lt("procesando_desde", limite)
        .execute()
    )

    # ----------------------------------------------
    # CONSULTAR NOTIFICACIONES PENDIENTES
    # ----------------------------------------------

    print("Consultando notificaciones pendientes...")

    respuesta = (
        supabase.table(TABLA_NOTIFICACIONES)
        .select(
            "id,quedada_id,profile_id,email_destino,intentos"
        )
        .eq("estado", "pendiente")
        .lte("proximo_intento", ahora_texto)
        .order("created_at")
        .limit(MAX_NOTIFICACIONES)
        .execute()
    )

    print(
        "Tipo de respuesta Supabase:",
        type(respuesta.data).__name__
    )

    print(
        "Contenido de respuesta:",
        repr(respuesta.data)[:1000]
    )

    notificaciones = convertir_registros(
        respuesta.data,
        "Consulta de notificaciones"
    )

    print(
        f"Notificaciones recuperadas: {len(notificaciones)}"
    )

    if notificaciones:
        print(
            "Campos detectados:",
            list(notificaciones[0].keys())
        )

    if len(notificaciones) > MAX_NOTIFICACIONES:

        raise RuntimeError(
            "Supabase ha devuelto más registros "
            "de los permitidos."
        )

    # ----------------------------------------------
    # CONTADORES
    # ----------------------------------------------

    enviados = 0
    omitidos = 0
    errores = 0

    # ----------------------------------------------
    # RECORRER NOTIFICACIONES
    # ----------------------------------------------

    for aviso in notificaciones:

        aviso_id = aviso.get("id")
        quedada_id = aviso.get("quedada_id")
        perfil_id = aviso.get("profile_id")

        if not aviso_id or not quedada_id or not perfil_id:

            print(
                f"Notificación incompleta: {aviso}"
            )

            errores += 1
            continue

        intentos = int(
            aviso.get("intentos") or 0
        ) + 1

        print(
            f"Procesando notificación {aviso_id}"
        )

        # ------------------------------------------
        # MARCAR COMO PROCESANDO
        # ------------------------------------------

        actualizar_notificacion(
            aviso_id,
            {
                "estado": "procesando",
                "procesando_desde": fecha_iso(ahora()),
                "intentos": intentos
            }
        )

        try:

            # --------------------------------------
            # BUSCAR PERFIL
            # --------------------------------------

            respuesta_perfil = (
                supabase.table("profiles")
                .select("email_contacto,avisos_email")
                .eq("id", perfil_id)
                .limit(1)
                .execute()
            )

            perfiles = convertir_registros(
                respuesta_perfil.data,
                "Consulta de perfil"
            )

            if not perfiles:

                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "omitido",
                        "procesando_desde": None,
                        "error_detalle": (
                            "No se encuentra el perfil."
                        )
                    }
                )

                omitidos += 1
                continue

            perfil = perfiles[0]

            if (
                not perfil.get("avisos_email")
                or not perfil.get("email_contacto")
            ):

                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "omitido",
                        "procesando_desde": None,
                        "error_detalle": (
                            "El usuario no tiene avisos activos."
                        )
                    }
                )

                omitidos += 1
                continue

            destinatario = (
                perfil["email_contacto"]
                .strip()
                .lower()
            )

            # --------------------------------------
            # BUSCAR QUEDADA
            # --------------------------------------

            respuesta_quedada = (
                supabase.table("quedadas")
                .select(
                    "id,ruta_nombre,fecha,hora,"
                    "punto_encuentro,descripcion,estado"
                )
                .eq("id", quedada_id)
                .limit(1)
                .execute()
            )

            quedadas = convertir_registros(
                respuesta_quedada.data,
                "Consulta de quedada"
            )

            if not quedadas:

                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "omitido",
                        "procesando_desde": None,
                        "error_detalle": (
                            "La quedada ya no existe."
                        )
                    }
                )

                omitidos += 1
                continue

            quedada = quedadas[0]

            if quedada.get("estado") != "abierta":

                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "omitido",
                        "procesando_desde": None,
                        "error_detalle": (
                            "La quedada ya no está abierta."
                        )
                    }
                )

                omitidos += 1
                continue

            # --------------------------------------
            # PREPARAR EMAIL
            # --------------------------------------

            actualizar_notificacion(
                aviso_id,
                {
                    "email_destino": destinatario
                }
            )

            cuerpo_html, cuerpo_texto = construir_correo(
                quedada
            )

            # --------------------------------------
            # ENVIAR EMAIL
            # --------------------------------------

            resultado = enviar_email(
                destinatario=destinatario,

                asunto=(
                    "Nueva quedada motera: "
                    f"{quedada.get('ruta_nombre') or 'FAMILY BIKE'}"
                ),

                contenido_html=cuerpo_html,

                contenido_texto=cuerpo_texto,

                clave=f"familybike-quedada-{aviso_id}"
            )

            # --------------------------------------
            # MARCAR COMO ENVIADO
            # --------------------------------------

            actualizar_notificacion(
                aviso_id,
                {
                    "estado": "enviado",
                    "resend_id": resultado.get("id"),
                    "sent_at": fecha_iso(ahora()),
                    "procesando_desde": None,
                    "error_detalle": None
                }
            )

            enviados += 1

            print(
                f"ENVIADO: {destinatario} "
                f"| Resend ID: {resultado.get('id')}"
            )

        except Exception as error:

            minutos = min(
                15 * (2 ** min(intentos - 1, 5)),
                360
            )

            proximo = fecha_iso(
                ahora() + timedelta(minutes=minutos)
            )

            try:

                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "pendiente",
                        "procesando_desde": None,
                        "proximo_intento": proximo,
                        "error_detalle": str(error)[:2000]
                    }
                )

            except Exception as error_bd:

                print(
                    "ERROR ACTUALIZANDO NOTIFICACIÓN:",
                    error_bd
                )

            errores += 1

            print(
                f"ERROR EN AVISO {aviso_id}: {error}"
            )

    # ----------------------------------------------
    # RESUMEN FINAL
    # ----------------------------------------------

    print("")
    print("================================")
    print("RESUMEN FAMILY BIKE")
    print("================================")

    print(
        f"Notificaciones recuperadas: {len(notificaciones)}"
    )

    print(f"Correos enviados: {enviados}")

    print(f"Notificaciones omitidas: {omitidos}")

    print(f"Errores: {errores}")

    print("================================")

    # ----------------------------------------------
    # INFORMAR DE ERRORES A GITHUB ACTIONS
    # ----------------------------------------------

    if errores > 0:

        raise RuntimeError(
            f"El procesador ha terminado con {errores} errores. "
            f"Enviados: {enviados}. "
            f"Omitidos: {omitidos}. "
            "Consulta los detalles anteriores."
        )


# ==================================================
# EJECUCIÓN
# ==================================================

if __name__ == "__main__":

    try:

        procesar()

    except Exception as error:

        print("")
        print("ERROR GENERAL DEL PROCESADOR:")
        print(str(error))

        raise
