import flet as ft

def create_history_view(page, db, palette):
    COLOR_DARK = palette["dark"]
    COLOR_MUTED = palette["muted"]
    COLOR_ICE = palette["ice"]

    # Kontener na listę elementów historii
    history_list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=480)

    def show_details_dialog(doc_id, data):
        def close_dialog(e):
            page.overlay.remove(dialog_container)
            page.update()

        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=COLOR_DARK, size=28),
                    ft.Text(data.get("title", "Szczegóły operacji"), size=18, weight=ft.FontWeight.BOLD, color=COLOR_DARK)
                ], spacing=10),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text(f"Typ operacji: {data.get('type', '-')}", size=14, weight=ft.FontWeight.W_600, color=COLOR_MUTED),
                ft.Text(f"Klucze: a = {data.get('key_a')}, b = {data.get('key_b')}", size=14, color=COLOR_DARK),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                ft.Text("Tekst wejściowy:", weight=ft.FontWeight.BOLD, color=COLOR_DARK, size=13),
                ft.Container(
                    content=ft.Text(data.get("input_text", ""), size=13, selectable=True),
                    padding=10, bgcolor=COLOR_ICE, border_radius=8, width=float("inf")
                ),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                ft.Text("Wynik operacji:", weight=ft.FontWeight.BOLD, color=COLOR_DARK, size=13),
                ft.Container(
                    content=ft.Text(data.get("result_text", ""), size=13, selectable=True),
                    padding=10, bgcolor=COLOR_ICE, border_radius=8, width=float("inf")
                ),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    ft.Button(
                        "Zamknij", 
                        on_click=close_dialog,
                        bgcolor=COLOR_DARK,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            border=ft.Border.all(1, COLOR_MUTED),
            width=480,
            shadow=ft.BoxShadow(blur_radius=25, spread_radius=5, color="#22000000", offset=ft.Offset(0, 10))
        )

        dialog_container = ft.Container(
            content=dialog_content,
            alignment=ft.Alignment.CENTER,
            bgcolor="#40000000",
            expand=True
        )

        page.overlay.append(dialog_container)
        page.update()

    def delete_record(doc_id):
        try:
            if db:
                db.collection("crypto_operations").document(doc_id).delete()
            load_history() # Odświeżenie listy po usunięciu
        except Exception as err:
            print(f"Błąd usuwania: {err}")

    def load_history():
        history_list_container.controls.clear()
        try:
            if not db:
                history_list_container.controls.append(
                    ft.Text("Brak połączenia z bazą Firebase.", color=ft.Colors.RED_800)
                )
                page.update()
                return

            docs = db.collection("crypto_operations").stream()
            records = []
            for doc in docs:
                d = doc.to_dict()
                d["id"] = doc.id
                records.append(d)

            # Sortowanie lokalne po dacie (najnowsze na górze)
            records.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            if not records:
                history_list_container.controls.append(
                    ft.Container(
                        content=ft.Text("Brak zapisanych operacji w historii.", color=COLOR_MUTED, italic=True),
                        alignment=ft.Alignment.CENTER,
                        padding=20
                    )
                )
            else:
                for rec in records:
                    doc_id = rec["id"]
                    title = rec.get("title", "Bez tytułu")
                    op_type = rec.get("type", "Operacja")
                    timestamp = rec.get("timestamp")
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "Bez daty"

                    card = ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.LOCK if op_type == "Szyfrowanie" else ft.Icons.LOCK_OPEN,
                                color=COLOR_DARK,
                                size=24
                            ),
                            ft.Column([
                                ft.Text(title, weight=ft.FontWeight.BOLD, color=COLOR_DARK, size=14),
                                ft.Text(f"{op_type} • {time_str}", color=COLOR_MUTED, size=12)
                            ], expand=True, spacing=2),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY,
                                    icon_color=COLOR_DARK,
                                    tooltip="Podgląd",
                                    on_click=lambda e, id=doc_id, data=rec: show_details_dialog(id, data)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Usuń",
                                    on_click=lambda e, id=doc_id: delete_record(id)
                                )
                            ], spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=12,
                        bgcolor=COLOR_ICE,
                        border_radius=10,
                        border=ft.Border.all(1, COLOR_MUTED),
                        width=float("inf")
                    )
                    history_list_container.controls.append(card)

        except Exception as err:
            history_list_container.controls.append(
                ft.Text(f"Błąd pobierania historii: {str(err)}", color=ft.Colors.RED_800)
            )
        page.update()

    # Załaduj historię przy wejściu w widok
    load_history()

    return ft.Column([
        ft.Row([
            ft.Text("Historia operacji w chmurze", size=20, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
            ft.IconButton(icon=ft.Icons.REFRESH, icon_color=COLOR_DARK, tooltip="Odśwież", on_click=lambda e: load_history())
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
        history_list_container
    ], spacing=10)