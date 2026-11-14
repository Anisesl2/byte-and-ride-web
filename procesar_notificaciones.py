
import os
import json
import html
import urllib.request
import urllib.error

from datetime import datetime, timezone, timedelta
from supabase import create_client


# ---------------------------------
# CONFIGURACIÓN
# ---------------------------------

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]

FAMILY_BIKE_URL = os.environ.get(
    "FAMILY_BIKE_URL",
    "https://familybike.es"
)

REMITENTE = "FAMILY BIKE <avisos@send.familybike.es>"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def ahora():
    return datetime.now(timezone.utc)


def fecha_iso(valor):
    return valor.isoformat()


# ---------------------------------
# ENVÍO A RESEND
# ---------------------------------

def enviar_email(destinatario, asunto, contenido_html, contenido_texto, clave):

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
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Resend HTTP {error.code}: {detalle}"
        )


# ---------------------------------
# CONSTRUIR EL CORREO
# ---------------------------------

def construir_correo(quedada):

    nombre = html.escape(quedada.get("ruta_nombre") or "Nueva quedada")
    fecha = html.escape(str(quedada.get("fecha") or ""))
    hora = html.escape(str(quedada.get("hora") or "")[:5])
    punto = html.escape(quedada.get("punto_encuentro") or "")
    descripcion = html.escape(quedada.get("descripcion") or "")

    enlace = html.escape(FAMILY_BIKE_URL, quote=True)

    cuerpo = f"""
    <div style="
        background:#101114;
        color:#f5f5f5;
        padding:30px;
        font-family:Arial,sans-serif;
        border-radius:14px;
        max-width:600px;
        margin:auto;
    ">
        <h1 style="color:#f0a43a;text-align:center;">
            FAMILY BIKE
        </h1>

        <h2>¡Nueva quedada motera!</h2>

        <p>Se ha publicado una nueva salida en FAMILY BIKE.</p>

        <div style="
            background:#1b1e24;
            padding:20px;
            border-radius:12px;
            border:1px solid #393d45;
        ">
            <h2 style="color:#f0a43a;">🏍️ {nombre}</h2>

            <p>📅 <strong>Fecha:</strong> {fecha}</p>
            <p>🕘 <strong>Hora:</strong> {hora}</p>
            <p>📍 <strong>Punto de encuentro:</strong> {punto}</p>

            <p>{descripcion}</p>
        </div>

        <p style="text-align:center;margin-top:30px;">
            <a href="{enlace}" style="
                display:inline-block;
                background:#f0a43a;
                color:#151515;
                padding:14px 24px;
                border-radius:8px;
                text-decoration:none;
                font-weight:bold;
            ">
                ENTRAR Y APUNTARME
            </a>
        </p>

        <p style="color:#999da5;font-size:12px;text-align:center;">
            Recibes este aviso porque tienes activadas
            las notificaciones de FAMILY BIKE.
            Puedes desactivarlas desde tus preferencias de cuenta.
        </p>
    </div>
    """

    texto = (
        f"FAMILY BIKE - Nueva quedada motera\n\n"
        f"{quedada.get('ruta_nombre', '')}\n"
        f"Fecha: {quedada.get('fecha', '')}\n"
        f"Hora: {str(quedada.get('hora', ''))[:5]}\n"
        f"Punto de encuentro: {quedada.get('punto_encuentro', '')}\n\n"
        f"{quedada.get('descripcion', '')}\n\n"
        f"Entra para apuntarte: {FAMILY_BIKE_URL}"
    )

    return cuerpo, texto


# ---------------------------------
# ACTUALIZAR ESTADO
# ---------------------------------

def actualizar_notificacion(notificacion_id, datos):

    (
        supabase.table("notificaciones_quedadas")
        .update(datos)
        .eq("id", notificacion_id)
        .execute()
    )


# ---------------------------------
# PROCESAR COLA
# ---------------------------------

def procesar():

    ahora_dt = ahora()
    ahora_texto = fecha_iso(ahora_dt)

    # Recuperar procesos interrumpidos hace más de 15 minutos.
    limite = fecha_iso(ahora_dt - timedelta(minutes=15))

    (
        supabase.table("notificaciones_quedadas")
        .update({
            "estado": "pendiente",
            "procesando_desde": None,
            "proximo_intento": ahora_texto
        })
        .eq("estado", "procesando")
        .lt("procesando_desde", limite)
        .execute()
    )

    # Buscar avisos que ya toca procesar.
    respuesta = (
        supabase.table("notificaciones_quedadas")
        .select(
            "id,quedada_id,profile_id,email_destino,intentos"
        )
        .eq("estado", "pendiente")
        .lte("proximo_intento", ahora_texto)
        .order("created_at")
        .limit(50)
        .execute()
    )

    notificaciones = respuesta.data or []

    print(f"Notificaciones pendientes encontradas: {len(notificaciones)}")

    for aviso in notificaciones:

        aviso_id = aviso["id"]
        quedada_id = aviso["quedada_id"]
        perfil_id = aviso["profile_id"]

        intentos = int(aviso.get("intentos") or 0) + 1

        # Marcar como procesando.
        actualizar_notificacion(
            aviso_id,
            {
                "estado": "procesando",
                "procesando_desde": fecha_iso(ahora()),
                "intentos": intentos
            }
        )

        try:

            # Consultar el consentimiento actual.
            respuesta_perfil = (
                supabase.table("profiles")
                .select("email_contacto,avisos_email")
                .eq("id", perfil_id)
                .limit(1)
                .execute()
            )

            perfiles = respuesta_perfil.data or []

            if not perfiles:
                raise RuntimeError("No se encuentra el perfil del destinatario.")

            perfil = perfiles[0]

            if not perfil.get("avisos_email") or not perfil.get("email_contacto"):
                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "omitido",
                        "procesando_desde": None,
                        "error_detalle": "El usuario no tiene avisos activos."
                    }
                )
                continue

            destinatario = perfil["email_contacto"].strip().lower()

            # Consultar la quedada.
            respuesta_quedada = (
                supabase.table("quedadas")
                .select(
                    "id,ruta_nombre,fecha,hora,punto_encuentro,"
                    "descripcion,estado"
                )
                .eq("id", quedada_id)
                .limit(1)
                .execute()
            )

            quedadas = respuesta_quedada.data or []

            if not quedadas:
                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "omitido",
                        "procesando_desde": None,
                        "error_detalle": "La quedada ya no existe."
                    }
                )
                continue

            quedada = quedadas[0]

            if quedada.get("estado") != "abierta":
                actualizar_notificacion(
                    aviso_id,
                    {
                        "estado": "omitido",
                        "procesando_desde": None,
                        "error_detalle": "La quedada ya no está abierta."
                    }
                )
                continue

            # Usar el correo de contacto actualizado.
            actualizar_notificacion(
                aviso_id,
                {"email_destino": destinatario}
            )

            cuerpo_html, cuerpo_texto = construir_correo(quedada)

            resultado = enviar_email(
                destinatario=destinatario,
                asunto=f"Nueva quedada motera: {quedada['ruta_nombre']}",
                contenido_html=cuerpo_html,
                contenido_texto=cuerpo_texto,
                clave=f"familybike-quedada-{aviso_id}"
            )

            # Confirmar envío.
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

            print(f"Correo enviado a {destinatario}: {resultado.get('id')}")

        except Exception as error:

            # Reintentos progresivos: 15 min, 30 min, 1 h...
            minutos = min(15 * (2 ** min(intentos - 1, 5)), 360)

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
                print(f"Error guardando el reintento: {error_bd}")

            print(f"Error en aviso {aviso_id}: {error}")


if __name__ == "__main__":
    procesar()
