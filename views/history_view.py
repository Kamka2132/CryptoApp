import flet as ft

def create_history_view(page: ft.Page, db, palette, on_load_operation=None):
    COLOR_DARK = palette["dark"]
    COLOR_MUTED = palette["muted"]
    COLOR_ICE = palette["ice"]

    def show_message_dialog(title, message, is_error=False):
        def close_dialog(e):
            page.overlay.remove(dialog_container)
            page.update()

        dialog_content = ft.Container(
            content=ft.Column([
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text(message, size=15, color=COLOR_DARK, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    ft.Button(
                        "OK", 
                        on_click=close_dialog,
                        bgcolor=COLOR_DARK,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ], alignment=ft.MainAxisAlignment.CENTER) 
            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            border=ft.Border.all(1, COLOR_MUTED),
            width=380,
            shadow=ft.BoxShadow(blur_radius=25, spread_radius=5, color="#22000000", offset=ft.Offset(0, 10))
        )

        dialog_container = ft.Container(content=dialog_content, alignment=ft.Alignment.CENTER, bgcolor="#40000000", expand=True)
        page.overlay.append(dialog_container)
        page.update()

    def show_details_dialog(item):
        def close_dialog(e):
            page.overlay.remove(dialog_container)
            page.update()

        def load_to_editor(e):
            page.overlay.remove(dialog_container)
            page.update()
            if on_load_operation:
                on_load_operation(item)

        header_row = ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=COLOR_DARK, size=24),
                ft.Text(item.get("title", "Szczegóły operacji"), size=18, weight=ft.FontWeight.BOLD, color=COLOR_DARK)
            ], spacing=10, expand=True),
            ft.IconButton(icon=ft.Icons.CLOSE, icon_color=COLOR_DARK, tooltip="Zamknij", on_click=close_dialog)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        content_column = ft.Column([
            ft.Text(f"Typ operacji: {item.get('type', '-')}", size=14, color=COLOR_DARK, weight=ft.FontWeight.W_500),
            ft.Text(f"Klucze: a = {item.get('key_a', '-')}, b = {item.get('key_b', '-')}", size=14, color=COLOR_DARK, weight=ft.FontWeight.W_500),
            ft.Divider(height=10, color=COLOR_MUTED),
            
            ft.Text("Tekst wejściowy:", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
            ft.Container(
                content=ft.ListView([ft.Text(item.get("input_text", ""), size=13, color=COLOR_DARK)], expand=True, padding=5),
                padding=5, bgcolor=COLOR_ICE, border_radius=8, border=ft.Border.all(1, COLOR_MUTED), height=110, clip_behavior=ft.ClipBehavior.HARD_EDGE
            ),
            
            ft.Divider(height=10, color=COLOR_MUTED),
            
            ft.Text("Wynik operacji:", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
            ft.Container(
                content=ft.ListView([ft.Text(item.get("result_text", ""), size=13, color=COLOR_DARK)], expand=True, padding=5),
                padding=5, bgcolor=COLOR_ICE, border_radius=8, border=ft.Border.all(1, COLOR_MUTED), height=110, clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        dialog_content = ft.Container(
            content=ft.Column([
                header_row,
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                content_column,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    ft.Button("Wczytaj do edytora", icon=ft.Icons.DOWNLOAD, on_click=load_to_editor, bgcolor=COLOR_DARK, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.Button("Zamknij", on_click=close_dialog, bgcolor=COLOR_MUTED, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
            ], tight=True),
            padding=20, bgcolor=ft.Colors.WHITE, border_radius=15, border=ft.Border.all(1, COLOR_MUTED), width=550, height=630,
            shadow=ft.BoxShadow(blur_radius=25, spread_radius=5, color="#22000000", offset=ft.Offset(0, 10))
        )

        dialog_container = ft.Container(content=dialog_content, alignment=ft.Alignment.CENTER, bgcolor="#40000000", expand=True)
        page.overlay.append(dialog_container)
        page.update()

    def fetch_history():
        if not db:
            return []
        try:
            docs = db.collection("crypto_operations").order_by("timestamp", direction="DESCENDING").stream()
            history_list = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                history_list.append(data)
            return history_list
        except Exception as err:
            print(f"Błąd pobierania historii: {err}")
            return []

    listView = ft.ListView(expand=1, spacing=10, padding=10)

    def load_cards():
        listView.controls.clear()
        items = fetch_history()
        if not items:
            listView.controls.append(ft.Text("Brak zapisanych operacji w chmurze.", color=COLOR_DARK, italic=True))
        else:
            for item in items:
                card = ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.LOCK if item.get("type") == "Szyfrowanie" else ft.Icons.LOCK_OPEN, color=COLOR_DARK),
                            ft.Column([
                                ft.Text(item.get("title", "Bez tytułu"), weight=ft.FontWeight.BOLD, color=COLOR_DARK),
                                ft.Text(f"{item.get('type', '-')} • {str(item.get('timestamp', ''))[:16]}", size=12, color=COLOR_MUTED),
                            ], spacing=2)
                        ], spacing=15),
                        ft.Row([
                            ft.IconButton(icon=ft.Icons.VISIBILITY, icon_color=COLOR_DARK, tooltip="Pokaż szczegóły", on_click=lambda e, it=item: show_details_dialog(it)),
                            ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_700, tooltip="Usuń", on_click=lambda e, doc_id=item["id"]: delete_item(doc_id)),
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15, bgcolor=ft.Colors.WHITE, border_radius=10, border=ft.Border.all(1, COLOR_MUTED)
                )
                listView.controls.append(card)
        page.update()

    def delete_item(doc_id):
        try:
            db.collection("crypto_operations").document(doc_id).delete()
            load_cards()
        except Exception as err:
            show_message_dialog("Błąd", f"Nie udało się usunąć wpisu:\n{err}", is_error=True)

    load_cards()

    return ft.Column([
        ft.Row([
            ft.Text("Historia operacji w chmurze", size=20, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
            ft.IconButton(icon=ft.Icons.REFRESH, icon_color=COLOR_DARK, tooltip="Odśwież", on_click=lambda e: load_cards())
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(height=10, color=COLOR_MUTED),
        listView
    ], expand=True, spacing=10, scroll=ft.ScrollMode.AUTO)