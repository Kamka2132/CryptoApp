import asyncio
import flet as ft
from views.encrypt_view import create_encrypt_view
from views.decrypt_view import create_decrypt_view
from views.history_view import create_history_view
from database.firebase_db import db

async def main(page: ft.Page):
    page.title = "CryptoApp – Szyfr Afiniczny"
    page.window.width = 950
    page.window.height = 850
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 20

    palette = {
        "dark": "#384959",
        "muted": "#6A89A7",
        "ice": "#BDDDFC",
        "selected_bg": "#D0E1F9"
    }

    def load_main_app(e):
        page.clean()
        page.padding = 20
        page.bgcolor = ft.Colors.WHITE

        content_area = ft.Container(
            content=create_encrypt_view(page, db, palette),
            expand=True
        )

        current_tab = {"name": "szyfr"}

        # Definicje zakładek ze standardowym, bezpiecznym zaokrągleniem
        tab_szyfr = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK, size=16, color=palette["dark"]),
                ft.Text("Szyfr", color=palette["dark"], weight=ft.FontWeight.W_500)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            bgcolor=palette["selected_bg"],
            padding=10,
            expand=True,
            alignment=ft.Alignment.CENTER,
            ink=True
        )

        tab_deszyfr = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCK_OPEN_OUTLINED, size=16, color=palette["dark"]),
                ft.Text("Deszyfr", color=palette["dark"], weight=ft.FontWeight.W_500)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=10,
            expand=True,
            alignment=ft.Alignment.CENTER,
            ink=True
        )

        tab_historia = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=16, color=palette["dark"]),
                ft.Text("Historia", color=palette["dark"], weight=ft.FontWeight.W_500)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=10,
            expand=True,
            alignment=ft.Alignment.CENTER,
            ink=True
        )

        def update_tabs(selected):
            current_tab["name"] = selected
            
            # Reset tła
            tab_szyfr.bgcolor = ft.Colors.TRANSPARENT
            tab_deszyfr.bgcolor = ft.Colors.TRANSPARENT
            tab_historia.bgcolor = ft.Colors.TRANSPARENT

            # Ustawienie aktywnego widoku i tła
            if selected == "szyfr":
                tab_szyfr.bgcolor = palette["selected_bg"]
                content_area.content = create_encrypt_view(page, db, palette)
            elif selected == "deszyfr":
                tab_deszyfr.bgcolor = palette["selected_bg"]
                content_area.content = create_decrypt_view(page, db, palette)
            elif selected == "historia":
                tab_historia.bgcolor = palette["selected_bg"]
                content_area.content = create_history_view(page, db, palette)
            
            page.update()

        tab_szyfr.on_click = lambda e: update_tabs("szyfr")
        tab_deszyfr.on_click = lambda e: update_tabs("deszyfr")
        tab_historia.on_click = lambda e: update_tabs("historia")

        # Pasek zakładek z obcięciem krawędzi (clip_behavior) idealnie dopasowującym środki
        segmented_tabs = ft.Container(
            content=ft.Row(
                [tab_szyfr, tab_deszyfr, tab_historia], 
                alignment=ft.MainAxisAlignment.CENTER, 
                spacing=0
            ),
            border=ft.Border.all(1, palette["muted"]),
            border_radius=20,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            width=400,
            bgcolor=ft.Colors.WHITE
        )

        main_card = ft.Container(
            content=ft.Column([
                ft.Text("Aplikacja Kryptograficzna", size=24, weight=ft.FontWeight.BOLD, color=palette["dark"], text_align=ft.TextAlign.CENTER),
                ft.Text("Szyfr Afiniczny z przekształceniem liniowym E(x) = (ax + b) mod n", size=13, color=palette["muted"], text_align=ft.TextAlign.CENTER),
                ft.Divider(height=20, color=palette["muted"]),
                ft.Row([segmented_tabs], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                content_area
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            padding=30,
            expand=True,
            border=ft.Border.all(1, palette["muted"]),
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
        src="assets/introEncryptoApp.gif",
        fit="contain",
        width=400,
        height=400
    )

    gif_container = ft.Container(
        content=intro_gif,
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=ft.Colors.WHITE
    )

    start_button = ft.Button(
        "START",
        icon=ft.Icons.PLAY_ARROW,
        on_click=load_main_app,
        bgcolor=palette["dark"],
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