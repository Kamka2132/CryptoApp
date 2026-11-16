import flet as ft
import math
from datetime import datetime
from tkinter import Tk, filedialog
from crypto.affine import encrypt_text
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

def create_encrypt_view(page: ft.Page, db, palette, initial_data=None):
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
        if not enc_a.value:
            return
        try:
            val = int(enc_a.value)
        except ValueError:
            show_message_dialog("Błąd", "Wpisz liczbę całkowitą.", is_error=True)
            enc_a.value = "5"
            page.update()
            return

        if math.gcd(val, 26) != 1:
            show_message_dialog("Błąd", f"Liczba {val} musi być względnie pierwsza z 26!", is_error=True)
            enc_a.value = "5"
            page.update()
            return

    def validate_key_b(e):
        if not enc_b.value:
            return
        try:
            int(enc_b.value)
        except ValueError:
            show_message_dialog("Błąd", "Wpisz liczbę całkowitą.", is_error=True)
            enc_b.value = "8"
            page.update()

    default_title = initial_data.get("title", f"Szyfrowanie_{datetime.now().strftime('%Y-%m-%d_%H:%M')}") if initial_data else f"Szyfrowanie_{datetime.now().strftime('%Y-%m-%d_%H:%M')}"
    default_a = str(initial_data.get("key_a", "5")) if initial_data else "5"
    default_b = str(initial_data.get("key_b", "8")) if initial_data else "8"
    default_input = initial_data.get("input_text", "") if initial_data else ""
    default_result = initial_data.get("result_text", "Brak wyniku...") if initial_data else "Brak wyniku..."

    enc_title = ft.TextField(label="Tytuł operacji", value=default_title, border_radius=10, prefix_icon=ft.Icons.TITLE, border_color=COLOR_MUTED, color=COLOR_DARK, expand=True)
    enc_a = ft.TextField(label="Klucz a", value=default_a, border_radius=10, border_color=COLOR_MUTED, color=COLOR_DARK, tooltip="Musi być względnie pierwszy z 26", on_blur=validate_key_a, on_submit=validate_key_a, expand=True)
    enc_b = ft.TextField(label="Klucz b", value=default_b, border_radius=10, border_color=COLOR_MUTED, color=COLOR_DARK, on_blur=validate_key_b, on_submit=validate_key_b, expand=True)
    
    enc_input = ft.TextField(label="Tekst jawny", value=default_input, multiline=True, min_lines=6, max_lines=6, border_radius=10, border_color=COLOR_MUTED, color=COLOR_DARK, expand=True)
    enc_result = ft.TextField(value=default_result, label="Wynik operacji", multiline=True, read_only=True, min_lines=6, max_lines=6, border_radius=10, border_color=COLOR_MUTED, bgcolor=COLOR_ICE, color=COLOR_DARK, expand=True)
    
    def pick_file(e):
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(title="Wybierz plik z tekstem", filetypes=[("Wszystkie pliki", "*.*")])
        root.destroy()
        if not file_path:
            return
        try:
            content = extract_text_from_file(file_path)
            enc_input.value = content
            page.update()
        except Exception as err:
            show_message_dialog("Błąd odczytu pliku", str(err), is_error=True)

    btn_pick_file = ft.Button("Wczytaj z pliku", icon=ft.Icons.UPLOAD_FILE, on_click=pick_file, bgcolor=COLOR_DARK, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))

    def on_encrypt(e):
        try:
            a = int(enc_a.value)
            b = int(enc_b.value)
            if math.gcd(a, 26) != 1:
                show_message_dialog("Błąd", f"Liczba {a} musi być względnie pierwsza z 26!", is_error=True)
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
                raise Exception("Brak połączenia z bazą.")
            a = int(enc_a.value)
            if math.gcd(a, 26) != 1:
                show_message_dialog("Błąd", f"Liczba {a} musi być względnie pierwsza z 26!", is_error=True)
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

    # Estetyczny układ górny: Tytuł, Klucz a, Klucz b w jednym rzędzie responsywnym
    top_fields_row = ft.ResponsiveRow([
        ft.Column([enc_title], col={"xs": 12, "sm": 12, "md": 6}),
        ft.Column([enc_a], col={"xs": 12, "sm": 6, "md": 3}),
        ft.Column([enc_b], col={"xs": 12, "sm": 6, "md": 3}),
    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    text_fields_container = ft.ResponsiveRow([
        ft.Column([enc_input], col={"xs": 12, "sm": 12, "md": 6}),
        ft.Column([enc_result], col={"xs": 12, "sm": 12, "md": 6}),
    ], spacing=15)

    return ft.Column([
        ft.Row([ft.Text("Szyfrowanie tekstu", size=20, weight=ft.FontWeight.BOLD, color=COLOR_DARK)], alignment=ft.MainAxisAlignment.START),
        top_fields_row,
        ft.Row([btn_pick_file], alignment=ft.MainAxisAlignment.END),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        text_fields_container,
        ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
        # Wymuszenie idealnego wyśrodkowania dolnych przycisków
        ft.Row([
            ft.Row([
                ft.Button("Zaszyfruj tekst", icon=ft.Icons.LOCK, on_click=on_encrypt, width=220, bgcolor=COLOR_DARK, color=ft.Colors.WHITE, style=btn_style),
                ft.Button("Zapisz w chmurze", icon=ft.Icons.CLOUD_UPLOAD, on_click=on_save_encrypt, width=220, bgcolor=COLOR_MUTED, color=ft.Colors.WHITE, style=btn_style),
            ], spacing=30, alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=10, scroll=ft.ScrollMode.AUTO)