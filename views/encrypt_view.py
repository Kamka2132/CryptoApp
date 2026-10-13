import flet as ft
import math
from datetime import datetime
from crypto.affine import encrypt_text

def create_encrypt_view(page, db, palette):
    COLOR_DARK = palette["dark"]
    COLOR_MUTED = palette["muted"]
    COLOR_ICE = palette["ice"]

    def show_message_dialog(title, message, is_error=False):
        def close_dialog(e):
            page.overlay.remove(dialog_container)
            if not is_error:
                enc_input.value = ""          
                enc_result.value = "Brak wyniku..."  
                enc_result.color = COLOR_DARK
            page.update()

        icon = ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_600, size=30) if is_error else ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=30)
        title_color = ft.Colors.RED_800 if is_error else COLOR_DARK

        dialog_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    icon,
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=title_color)
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
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
            shadow=ft.BoxShadow(
                blur_radius=25,
                spread_radius=5,
                color="#22000000",
                offset=ft.Offset(0, 10)
            )
        )

        dialog_container = ft.Container(
            content=dialog_content,
            alignment=ft.Alignment.CENTER,
            bgcolor="#40000000",
            expand=True
        )

        page.overlay.append(dialog_container)
        page.update()

    # Funkcja sprawdzająca klucz po zatwierdzeniu Enterem lub wyjściu z pola (on_blur)
    def check_key_a(e):
        try:
            val = int(enc_a.value)
            if math.gcd(val, 26) != 1:
                show_message_dialog("Błąd", "Klucz 'a' musi być względnie pierwszy z rozmiarem alfabetu!", is_error=True)
        except ValueError:
            pass

    default_title = f"Szyfrowanie_{datetime.now().strftime('%Y-%m-%d_%H:%M')}"
    
    enc_title = ft.TextField(
        label="Tytuł operacji", 
        value=default_title, 
        border_radius=10, 
        prefix_icon=ft.Icons.TITLE,
        border_color=COLOR_MUTED,
        focused_border_color=COLOR_DARK
    )
    
    enc_a = ft.TextField(
        label="Klucz a", 
        value="5", 
        expand=True, 
        border_radius=10, 
        border_color=COLOR_MUTED,
        focused_border_color=COLOR_DARK,
        on_submit=check_key_a,  # Wywołanie po wciśnięciu Enter
        on_blur=check_key_a     # Wywołanie po przełączeniu/kliknięciu poza pole
    )
    
    enc_b = ft.TextField(
        label="Klucz b", 
        value="8", 
        expand=True, 
        border_radius=10, 
        border_color=COLOR_MUTED,
        focused_border_color=COLOR_DARK
    )
    
    enc_input = ft.TextField(
        label="Tekst jawny", 
        multiline=True, 
        min_lines=3, 
        max_lines=5, 
        border_radius=10,
        width=float("inf"),
        border_color=COLOR_MUTED,
        focused_border_color=COLOR_DARK
    )
    
    enc_result = ft.Text(value="Brak wyniku...", size=15, selectable=True)
    
    enc_result_box = ft.Container(
        content=enc_result,
        padding=15,
        bgcolor=COLOR_ICE,
        border_radius=10,
        border=ft.Border.all(1, COLOR_MUTED),
        width=float("inf")
    )

    def on_encrypt(e):
        try:
            a = int(enc_a.value)
            b = int(enc_b.value)
            if math.gcd(a, 26) != 1:
                show_message_dialog("Błąd", "Klucz 'a' musi być względnie pierwszy z rozmiarem alfabetu!", is_error=True)
                return
            res = encrypt_text(enc_input.value, a, b)
            enc_result.value = res
            enc_result.color = COLOR_DARK
        except Exception as err:
            enc_result.value = f"Błąd: {str(err)}"
            enc_result.color = ft.Colors.RED_800
        page.update()

    def on_save_encrypt(e):
        try:
            if not db:
                raise Exception("Brak połączenia z bazą Firebase.")
            a = int(enc_a.value)
            if math.gcd(a, 26) != 1:
                show_message_dialog("Błąd", "Klucz 'a' musi być względnie pierwszy z rozmiarem alfabetu!", is_error=True)
                return
            doc_data = {
                "title": enc_title.value,
                "type": "Szyfrowanie",
                "key_a": a,
                "key_b": int(enc_b.value),
                "input_text": enc_input.value,
                "result_text": enc_result.value,
                "timestamp": datetime.now()
            }
            db.collection("crypto_operations").add(doc_data)
            show_message_dialog("Sukces!", "Zapisano zaszyfrowany tekst.")
        except Exception as err:
            show_message_dialog("Błąd", f"Błąd zapisu do chmury:\n{str(err)}", is_error=True)

    btn_style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))

    return ft.Column([
        ft.Text("Szyfrowanie tekstu", size=20, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
        enc_title,
        ft.Row([enc_a, enc_b], spacing=15),
        enc_input,
        ft.Row([
            ft.Button("Zaszyfruj tekst", icon=ft.Icons.LOCK, on_click=on_encrypt, expand=1, bgcolor=COLOR_DARK, color=ft.Colors.WHITE, style=btn_style),
            ft.Button("Zapisz w chmurze", icon=ft.Icons.CLOUD_UPLOAD, on_click=on_save_encrypt, expand=1, bgcolor=COLOR_MUTED, color=ft.Colors.WHITE, style=btn_style),
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.Text("Wynik operacji:", weight=ft.FontWeight.W_600, color=COLOR_DARK),
        enc_result_box
    ], spacing=15)