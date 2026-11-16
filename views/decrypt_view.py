import flet as ft
import math
from datetime import datetime
from tkinter import Tk, filedialog
from crypto.affine import decrypt_text
from pypdf import PdfReader
import docx
from odf import text, teletype
from odf.opendocument import load

def extract_text_from_file(file_path: str) -> str:
    ext = file_path.lower().split('.')[-1]
    if ext == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == "pdf":
        reader = PdfReader(file_path)
        extracted_pages = []
        for page_pdf in reader.pages:
            t = page_pdf.extract_text()
            if t:
                extracted_pages.append(t)
        return "\n".join(extracted_pages)
    elif ext == "docx":
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text])
    elif ext == "odt":
        doc = load(file_path)
        paragraphs = doc.getElementsByType(text.P)
        extracted = []
        for p in paragraphs:
            t = teletype.extractText(p)
            if t:
                extracted.append(t)
        return "\n".join(extracted)
    elif ext == "doc":
        with open(file_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")
            clean_text = "".join([ch if (32 <= ord(ch) <= 126 or ch in "\n\r\t") else " " for ch in content])
            return " ".join(clean_text.split())
    else:
        raise ValueError("Nieobsługiwany format pliku.")

def create_decrypt_view(page: ft.Page, db, palette, initial_data=None):
    COLOR_DARK = palette["dark"]
    COLOR_MUTED = palette["muted"]
    COLOR_ICE = palette["ice"]

    def show_message_dialog(title, message, is_error=False):
        def close_dialog(e):
            page.overlay.remove(dialog_container)
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
            shadow=ft.BoxShadow(blur_radius=25, spread_radius=5, color="#22000000", offset=ft.Offset(0, 10))
        )

        dialog_container = ft.Container(content=dialog_content, alignment=ft.Alignment.CENTER, bgcolor="#40000000", expand=True)
        page.overlay.append(dialog_container)
        page.update()

    def validate_key_a(e):
        if not dec_a.value:
            return
        try:
            val = int(dec_a.value)
        except ValueError:
            show_message_dialog("Błąd", "Wpisz liczbę całkowitą.", is_error=True)
            dec_a.value = "5"
            page.update()
            return

        if math.gcd(val, 26) != 1:
            show_message_dialog("Błąd", f"Liczba {val} musi być względnie pierwsza z 26!", is_error=True)
            dec_a.value = "5"
            page.update()
            return

    def validate_key_b(e):
        if not dec_b.value:
            return
        try:
            int(dec_b.value)
        except ValueError:
            show_message_dialog("Błąd", "Wpisz liczbę całkowitą.", is_error=True)
            dec_b.value = "8"
            page.update()

    default_title = initial_data.get("title", f"Deszyfrowanie_{datetime.now().strftime('%Y-%m-%d_%H:%M')}") if initial_data else f"Deszyfrowanie_{datetime.now().strftime('%Y-%m-%d_%H:%M')}"
    default_a = str(initial_data.get("key_a", "5")) if initial_data else "5"
    default_b = str(initial_data.get("key_b", "8")) if initial_data else "8"
    default_input = initial_data.get("input_text", "") if initial_data else ""
    default_result = initial_data.get("result_text", "Brak wyniku...") if initial_data else "Brak wyniku..."

    dec_title = ft.TextField(label="Tytuł operacji", value=default_title, border_radius=10, prefix_icon=ft.Icons.TITLE, border_color=COLOR_MUTED, color=COLOR_DARK, expand=True)
    dec_a = ft.TextField(label="Klucz a", value=default_a, border_radius=10, border_color=COLOR_MUTED, color=COLOR_DARK, tooltip="Musi być względnie pierwszy z 26", on_blur=validate_key_a, on_submit=validate_key_a, expand=True)
    dec_b = ft.TextField(label="Klucz b", value=default_b, border_radius=10, border_color=COLOR_MUTED, color=COLOR_DARK, on_blur=validate_key_b, on_submit=validate_key_b, expand=True)
    
    dec_input = ft.TextField(label="Szyfrogram", value=default_input, multiline=True, min_lines=6, max_lines=6, border_radius=10, border_color=COLOR_MUTED, color=COLOR_DARK, expand=True)
    dec_result = ft.TextField(value=default_result, label="Wynik operacji", multiline=True, read_only=True, min_lines=6, max_lines=6, border_radius=10, border_color=COLOR_MUTED, bgcolor=COLOR_ICE, color=COLOR_DARK, expand=True)
    
    def pick_file(e):
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(title="Wybierz plik z szyfrogramem", filetypes=[("Wszystkie pliki", "*.*")])
        root.destroy()
        if not file_path:
            return
        try:
            content = extract_text_from_file(file_path)
            dec_input.value = content
            page.update()
        except Exception as err:
            show_message_dialog("Błąd odczytu pliku", str(err), is_error=True)

    btn_pick_file = ft.Button("Wczytaj z pliku", icon=ft.Icons.UPLOAD_FILE, on_click=pick_file, bgcolor=COLOR_DARK, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))

    def on_decrypt(e):
        try:
            a = int(dec_a.value)
            b = int(dec_b.value)
            if math.gcd(a, 26) != 1:
                show_message_dialog("Błąd", f"Liczba {a} musi być względnie pierwsza z 26!", is_error=True)
                return
            res = decrypt_text(dec_input.value, a, b)
            dec_result.value = res
            dec_result.color = COLOR_DARK
        except Exception as err:
            dec_result.value = f"Błąd: {str(err)}"
            dec_result.color = ft.Colors.RED_800
        page.update()

    def on_save_decrypt(e):
        try:
            if not db:
                raise Exception("Brak połączenia z bazą.")
            a = int(dec_a.value)
            if math.gcd(a, 26) != 1:
                show_message_dialog("Błąd", f"Liczba {a} musi być względnie pierwsza z 26!", is_error=True)
                return
            doc_data = {
                "title": dec_title.value,
                "type": "Deszyfrowanie",
                "key_a": a,
                "key_b": int(dec_b.value),
                "input_text": dec_input.value,
                "result_text": dec_result.value,
                "timestamp": datetime.now()
            }
            db.collection("crypto_operations").add(doc_data)
            show_message_dialog("Sukces!", "Zapisano odszyfrowany tekst.")
        except Exception as err:
            show_message_dialog("Błąd", f"Błąd zapisu do chmury:\n{str(err)}", is_error=True)

    btn_style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))

    top_fields_row = ft.ResponsiveRow([
        ft.Column([dec_title], col={"xs": 12, "sm": 12, "md": 6}),
        ft.Column([dec_a], col={"xs": 12, "sm": 6, "md": 3}),
        ft.Column([dec_b], col={"xs": 12, "sm": 6, "md": 3}),
    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    text_fields_container = ft.ResponsiveRow([
        ft.Column([dec_input], col={"xs": 12, "sm": 12, "md": 6}),
        ft.Column([dec_result], col={"xs": 12, "sm": 12, "md": 6}),
    ], spacing=15)

    return ft.Column([
        ft.Row([ft.Text("Deszyfrowanie tekstu", size=20, weight=ft.FontWeight.BOLD, color=COLOR_DARK)], alignment=ft.MainAxisAlignment.START),
        top_fields_row,
        ft.Row([btn_pick_file], alignment=ft.MainAxisAlignment.END),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        text_fields_container,
        ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
        # Wymuszenie idealnego wyśrodkowania dolnych przycisków
        ft.Row([
            ft.Row([
                ft.Button("Odszyfruj tekst", icon=ft.Icons.LOCK_OPEN, on_click=on_decrypt, width=220, bgcolor=COLOR_DARK, color=ft.Colors.WHITE, style=btn_style),
                ft.Button("Zapisz w chmurze", icon=ft.Icons.CLOUD_UPLOAD, on_click=on_save_decrypt, width=220, bgcolor=COLOR_MUTED, color=ft.Colors.WHITE, style=btn_style),
            ], spacing=30, alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=10, scroll=ft.ScrollMode.AUTO)