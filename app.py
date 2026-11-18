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
# VALORACIONES Y COMPARTIR RUTAS — FAMILY BIKE
# =========================================================

FAMILYBIKE_PUBLIC_URL = "https://www.familybike.es/"


def fb_clave_ruta(ruta):
    return f"{ruta.get('_origen', 'catalogo')}:{ruta['id']}"


def fb_enlace_ruta(ruta):
    return FAMILYBIKE_PUBLIC_URL.rstrip("/") + "/?" + urlencode({"ruta": fb_clave_ruta(ruta)})


def fb_panel_opiniones(ruta, usuario_id, admin=False):
    clave = fb_clave_ruta(ruta)
    with st.expander("⭐ VALORAR · 💬 COMENTAR · 📲 COMPARTIR", expanded=False):
        try:
            votos = (supabase.table("familybike_valoraciones")
                     .select("usuario_id,puntuacion").eq("ruta_clave", clave).execute()).data or []
            comentarios = (supabase.table("familybike_comentarios")
                           .select("id,usuario_id,contenido,created_at")
                           .eq("ruta_clave", clave).order("created_at", desc=True)
                           .limit(100).execute()).data or []
        except Exception:
            st.warning("Las opiniones todavía no están disponibles. Ejecuta primero el SQL de instalación.")
            return

        media = sum(int(v["puntuacion"]) for v in votos) / len(votos) if votos else 0
        st.markdown(f"**⭐ {media:.1f}/5** · {len(votos)} valoraciones · {len(comentarios)} comentarios")
        anterior = next((int(v["puntuacion"]) for v in votos if v["usuario_id"] == usuario_id), 0)
        with st.form(f"fb_voto_{clave}"):
            nota = st.select_slider("Tu valoración", options=[1, 2, 3, 4, 5],
                                    value=anterior or 5, key=f"fb_nota_{clave}")
            if st.form_submit_button("⭐ Guardar valoración"):
                try:
                    supabase.table("familybike_valoraciones").upsert({
                        "ruta_clave": clave, "usuario_id": usuario_id,
                        "puntuacion": int(nota)
                    }, on_conflict="ruta_clave,usuario_id").execute()
                    st.success("Valoración guardada.")
                    st.rerun()
                except Exception:
                    st.error("No se ha podido guardar la valoración. Revisa las políticas RLS.")

        with st.form(f"fb_comentario_{clave}", clear_on_submit=True):
            contenido = st.text_area("Tu comentario", max_chars=1000,
                                     key=f"fb_texto_{clave}", placeholder="¿Qué te pareció la ruta?")
            if st.form_submit_button("💬 Publicar comentario"):
                if not contenido.strip():
                    st.warning("Escribe un comentario antes de publicarlo.")
                else:
                    try:
                        supabase.table("familybike_comentarios").insert({
                            "ruta_clave": clave, "usuario_id": usuario_id,
                            "contenido": contenido.strip()
                        }).execute()
                        st.success("Comentario publicado.")
                        st.rerun()
                    except Exception:
                        st.error("No se ha podido publicar el comentario.")

        if comentarios:
            ids = list({c["usuario_id"] for c in comentarios})
            try:
                perfiles = (supabase.table("profiles").select("id,username")
                           .in_("id", ids).execute()).data or []
                nombres = {p["id"]: p.get("username") or "Motero" for p in perfiles}
            except Exception:
                nombres = {}
            for c in comentarios:
                st.markdown(f"**{html.escape(nombres.get(c['usuario_id'], 'Motero'))}** · "
                            f"{html.escape(str(c.get('created_at',''))[:10])}")
                st.write(c["contenido"])
                if c["usuario_id"] == usuario_id or admin:
                    if st.button("🗑️ Eliminar comentario", key=f"fb_del_{c['id']}"):
                        try:
                            supabase.table("familybike_comentarios").delete().eq("id", c["id"]).execute()
