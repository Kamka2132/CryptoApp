import asyncio
import flet as ft
from views.encrypt_view import create_encrypt_view
from views.decrypt_view import create_decrypt_view
from views.history_view import create_history_view
from views.help_view import create_help_view
from database.firebase_db import db

# Paleta kolorów (Stormy Morning)
PALETTE = {
    "dark": "#2c3e50",
    "muted": "#7f8c8d",
    "ice": "#ecf0f1",
    "selected_bg": "#D0E1F9",
    "background": "#bdc3c7"
}

async def main(page: ft.Page):
    page.title = "CryptoApp - Szyfr Afiniczny"
    
    # Minimalne wymiary oraz pełna responsywność okna
    page.window.min_width = 650
    page.window.min_height = 650
    page.window.width = 850
    page.window.height = 800
    page.window.resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 20

    def load_main_app(e):
        page.clean()
        page.padding = 20
        page.bgcolor = PALETTE["background"]

        content_area = ft.Container(
            content=None,
            expand=True
        )

        current_tab = {"name": "szyfr"}

        # Definicje przycisków zakładek (Segmented Tabs w stylu pigułek)
        tab_szyfr = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCK, size=15, color=PALETTE["dark"]),
                ft.Text("Szyfrowanie", color=PALETTE["dark"], weight=ft.FontWeight.W_500, size=13)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
            bgcolor=PALETTE["selected_bg"],
            padding=8,
            expand=True,
            alignment=ft.Alignment.CENTER,
            ink=True
        )

        tab_deszyfr = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCK_OPEN, size=15, color=PALETTE["dark"]),
                ft.Text("Deszyfrowanie", color=PALETTE["dark"], weight=ft.FontWeight.W_500, size=13)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=8,
            expand=True,
            alignment=ft.Alignment.CENTER,
            ink=True
        )

        tab_historia = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=15, color=PALETTE["dark"]),
                ft.Text("Historia", color=PALETTE["dark"], weight=ft.FontWeight.W_500, size=13)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=8,
            expand=True,
            alignment=ft.Alignment.CENTER,
            ink=True
        )

        tab_pomoc = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HELP_OUTLINE, size=15, color=PALETTE["dark"]),
                ft.Text("Pomoc", color=PALETTE["dark"], weight=ft.FontWeight.W_500, size=13)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=8,
            expand=True,
            alignment=ft.Alignment.CENTER,
            ink=True
        )

        # Obsługa ładowania wpisu z historii do odpowiedniego edytora
        def handle_load_operation(item):
            op_type = item.get("type")
            if op_type == "Szyfrowanie":
                tab_szyfr.bgcolor = PALETTE["selected_bg"]
                tab_deszyfr.bgcolor = ft.Colors.TRANSPARENT
                tab_historia.bgcolor = ft.Colors.TRANSPARENT
                tab_pomoc.bgcolor = ft.Colors.TRANSPARENT
                content_area.content = create_encrypt_view(page, db, PALETTE, initial_data=item)
                current_tab["name"] = "szyfrowanie"
            else:
                tab_deszyfr.bgcolor = PALETTE["selected_bg"]
                tab_szyfr.bgcolor = ft.Colors.TRANSPARENT
                tab_historia.bgcolor = ft.Colors.TRANSPARENT
                tab_pomoc.bgcolor = ft.Colors.TRANSPARENT
                content_area.content = create_decrypt_view(page, db, PALETTE, initial_data=item)
                current_tab["name"] = "deszyfrowanie"
            page.update()

        hist_view_instance = create_history_view(page, db, PALETTE, on_load_operation=handle_load_operation)
        
        try:
            help_view_instance = create_help_view(page, PALETTE)
        except Exception:
            help_view_instance = ft.Column([
                ft.Text("Pomoc i instrukcja", size=18, weight=ft.FontWeight.BOLD, color=PALETTE["dark"]),
                ft.Text("Szyfr afiniczny to klasyczny szyfr podstawieniowy...", color=PALETTE["dark"])
            ], scroll=ft.ScrollMode.AUTO, expand=True)

        def update_tabs(selected):
            current_tab["name"] = selected
            
            tab_szyfr.bgcolor = ft.Colors.TRANSPARENT
            tab_deszyfr.bgcolor = ft.Colors.TRANSPARENT
            tab_historia.bgcolor = ft.Colors.TRANSPARENT
            tab_pomoc.bgcolor = ft.Colors.TRANSPARENT

            if selected == "szyfrowanie":
                tab_szyfr.bgcolor = PALETTE["selected_bg"]
                content_area.content = create_encrypt_view(page, db, PALETTE)
            elif selected == "deszyfrowanie":
                tab_deszyfr.bgcolor = PALETTE["selected_bg"]
                content_area.content = create_decrypt_view(page, db, PALETTE)
            elif selected == "historia":
                tab_historia.bgcolor = PALETTE["selected_bg"]
                content_area.content = hist_view_instance
            elif selected == "pomoc":
                tab_pomoc.bgcolor = PALETTE["selected_bg"]
                content_area.content = help_view_instance
            
            page.update()

        tab_szyfr.on_click = lambda e: update_tabs("szyfrowanie")
        tab_deszyfr.on_click = lambda e: update_tabs("deszyfrowanie")
        tab_historia.on_click = lambda e: update_tabs("historia")
        tab_pomoc.on_click = lambda e: update_tabs("pomoc")

        content_area.content = create_encrypt_view(page, db, PALETTE)

        segmented_tabs = ft.Container(
            content=ft.Row(
                [tab_szyfr, tab_deszyfr, tab_historia, tab_pomoc], 
                alignment=ft.MainAxisAlignment.CENTER, 
                spacing=0
            ),
            border=ft.Border.all(1, PALETTE["muted"]),
            border_radius=20,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            width=540,
            bgcolor=ft.Colors.WHITE
        )

        main_card = ft.Container(
            content=ft.Column([
                ft.Text("Aplikacja kryptograficzna", size=24, weight=ft.FontWeight.BOLD, color=PALETTE["dark"], text_align=ft.TextAlign.CENTER),
                ft.Text("Szyfr afiniczny z przekształceniem liniowym E(x) = (ax + b) mod n", size=13, color=PALETTE["muted"], text_align=ft.TextAlign.CENTER),
                ft.Divider(height=15, color=PALETTE["muted"]),
                ft.Row([segmented_tabs], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                content_area
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            padding=25,
            expand=True,
            border=ft.Border.all(1, PALETTE["muted"]),
            shadow=ft.BoxShadow(
                blur_radius=25,
                spread_radius=5,
                color="#15000000",
                offset=ft.Offset(0, 10)
            )
        )

        page.add(main_card)
        page.update()

    # --- EKRAN POWITALNY (INTRO) ---
    intro_gif = ft.Image(
        src="assets/introCryptoApp.gif",
        fit="contain",
        width=600,
        height=600
    )

    gif_container = ft.Container(
        content=intro_gif,
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=ft.Colors.WHITE
    )

    start_button = ft.Button(
        "ZACZYNAJMY",
        icon=ft.Icons.PLAY_ARROW,
        on_click=load_main_app,
        bgcolor=PALETTE["dark"],
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=20
        ),
        width=220,
        visible=False
    )

    button_container = ft.Container(
        content=start_button,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=40,
        visible=False
    )

    intro_stack = ft.Stack([
        gif_container,
        button_container
    ], expand=True)

    page.add(intro_stack)
    page.update()

    # --- 5 SEKUND INTRO ---
    await asyncio.sleep(5)

    gif_container.visible = False
    button_container.visible = True
    start_button.visible = True
    page.update()

if __name__ == "__main__":
    ft.run(main)