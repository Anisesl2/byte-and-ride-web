                            "La quedada y sus datos relacionados "
                            "se han eliminado."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "No se ha podido completar la eliminación. "
                            "Comprueba las políticas RLS de Supabase."
                        )
                        st.code(str(error))

        except Exception as error:

            st.error("No se han podido cargar las quedadas.")
            st.code(str(error))


    # =====================================================
    # ADMINISTRAR NOTICIAS
    # =====================================================

    with tab_noticias:

        st.markdown("### PUBLICAR NOTICIA")

        st.write(
            "Las noticias activas aparecerán en la página principal "
            "de FAMILY BIKE para todos los usuarios."
        )

        with st.form("admin_form_nueva_noticia"):

            titulo_noticia_nueva = st.text_input(
                "Título de la noticia",
                max_chars=150,
                placeholder="Ejemplo: Próxima concentración motera"
            )

            contenido_noticia_nueva = st.text_area(
                "Contenido de la noticia",
                height=160,
                placeholder="Escribe aquí el contenido..."
            )

            fijar_noticia_nueva = st.checkbox(
                "Fijar noticia en la parte superior",
                value=True
            )

            publicar_noticia = st.form_submit_button(
                "📢 PUBLICAR NOTICIA",
                use_container_width=True
            )

        if publicar_noticia:

            titulo_limpio = titulo_noticia_nueva.strip()
            contenido_limpio = contenido_noticia_nueva.strip()

            if not titulo_limpio or not contenido_limpio:

                st.error(
                    "Debes introducir un título y un contenido."
                )

            else:

                try:

                    supabase.table("familybike_noticias").insert({
                        "titulo": titulo_limpio,
                        "contenido": contenido_limpio,
                        "activo": True,
                        "fijado": fijar_noticia_nueva,
                        "creado_por": usuario_id,
                        "updated_at": datetime.now(
                            timezone.utc
                        ).isoformat()
                    }).execute()

                    st.success("Noticia publicada correctamente.")
                    st.rerun()

                except Exception as error:

                    st.error("No se ha podido publicar la noticia.")
                    st.code(str(error))

        st.divider()
        st.markdown("### GESTIONAR NOTICIAS PUBLICADAS")

        try:

            respuesta_todas_noticias = (
                supabase.table("familybike_noticias")
                .select(
                    "id,titulo,contenido,activo,fijado,"
                    "creado_por,created_at,updated_at"
                )
                .order("created_at", desc=True)
                .execute()
            )

            todas_noticias = (
                respuesta_todas_noticias.data or []
            )

            if not todas_noticias:

                st.info("Todavía no hay noticias publicadas.")

            else:

                for noticia in todas_noticias:

                    noticia_id = noticia.get("id")

                    estado_noticia = (
                        "ACTIVA"
                        if noticia.get("activo")
                        else "INACTIVA"
                    )

                    with st.expander(
                        f"📢 {noticia.get('titulo')} · {estado_noticia}"
                    ):

                        with st.form(
                            f"form_editar_noticia_{noticia_id}"
                        ):

                            titulo_editado = st.text_input(
                                "Título",
                                value=noticia.get("titulo") or "",
                                key=f"titulo_edit_{noticia_id}"
                            )

                            contenido_editado = st.text_area(
                                "Contenido",
                                value=noticia.get("contenido") or "",
                                height=150,
                                key=f"contenido_edit_{noticia_id}"
                            )

                            noticia_activa_editada = st.checkbox(
                                "Noticia visible en la página principal",
                                value=bool(noticia.get("activo")),
                                key=f"activa_edit_{noticia_id}"
                            )

                            noticia_fijada_editada = st.checkbox(
                                "Fijar en la parte superior",
                                value=bool(noticia.get("fijado")),
                                key=f"fijada_edit_{noticia_id}"
                            )

                            guardar_edicion = st.form_submit_button(
                                "💾 GUARDAR CAMBIOS",
                                use_container_width=True
                            )

                        if guardar_edicion:

                            if (
                                not titulo_editado.strip()
                                or not contenido_editado.strip()
                            ):

                                st.error(
                                    "El título y el contenido son obligatorios."
                                )

                            else:

                                try:

                                    supabase.table(
                                        "familybike_noticias"
                                    ).update({
                                        "titulo": titulo_editado.strip(),
                                        "contenido": contenido_editado.strip(),
                                        "activo": noticia_activa_editada,
                                        "fijado": noticia_fijada_editada,
                                        "updated_at": datetime.now(
                                            timezone.utc
                                        ).isoformat()
                                    }).eq(
                                        "id",
                                        noticia_id
