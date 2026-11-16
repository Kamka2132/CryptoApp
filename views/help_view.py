import flet as ft

def create_help_view(page: ft.Page, palette):
    COLOR_DARK = palette["dark"]
    COLOR_MUTED = palette["muted"]
    COLOR_ICE = palette["ice"]

    def section_card(title, content, icon):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=COLOR_DARK, size=22),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=COLOR_DARK)
                ], spacing=10),
                ft.Divider(height=10, color=COLOR_MUTED),
                ft.Text(content, size=14, color=COLOR_DARK, selectable=True)
            ], spacing=8),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border.all(1, COLOR_MUTED),
            width=float("inf"),
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=1,
                color="#10000000",
                offset=ft.Offset(0, 4)
            )
        )

    return ft.Column([
        ft.Text("Centrum pomocy i instrukcja obsługi", size=22, weight=ft.FontWeight.BOLD, color=COLOR_DARK),
        ft.Text("Witaj w aplikacji CryptoApp! Poniżej znajdziesz wskazówki dotyczące nawigacji oraz działania szyfru afinicznego.", size=14, color=COLOR_MUTED),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        
        section_card(
            "1. Nawigacja po aplikacji",
            "• Szyfrowanie - służy do przekształcania tekstu jawnego w szyfrogram za pomocą kluczy 'a' oraz 'b'.\n"
            "• Deszyfrowanie - służy do odwracania procesu szyfrowania i przywracania oryginalnego tekstu.\n"
            "• Historia - zawiera listę zapisanych operacji pobraną bezpośrednio z bezpiecznej bazy danych w chmurze (Firebase).\n"
            "• Pomoc - aktualna zakładka – instrukcja oraz opis działania programu.",
            ft.Icons.NAVIGATION
        ),
        
        section_card(
            "2. Zasada działania szyfru afinicznego",
            "Szyfr afiniczny to rodzaj monoalfabetycznego szyfru podstawieniowego, w którym każda litera jest przekształcana za pomocą funkcji matematycznej liniowej:\n\n"
            "• Szyfrowanie: E(x) = (ax + b) mod 26\n"
            "• Deszyfrowanie: D(x) = a⁻¹(x - b) mod 26\n\n"
            "! Ważny wymóg - klucz 'a' musi być względnie pierwszy z rozmiarem alfabetu (26), co oznacza, że ich największy wspólny dzielnik (NWD / GCD) musi wynosić 1. Aplikacja automatycznie pilnuje tej zasady i wyświetli komunikat o błędzie, jeśli podasz niepoprawną wartość.",
            ft.Icons.LOCK_OUTLINE
        ),

        section_card(
            "3. Obsługa plików i zapis w chmurze",
            "• Wczytywanie z pliku - możesz wgrać gotowy tekst do przetworzenia za pomocą przycisku wczytywania. Obsługiwane formaty to: .txt, .pdf, .docx, .odt oraz .doc.\n"
            "• Zapis w chmurze - po wykonaniu operacji możesz kliknąć przycisk zapisu, aby przesłać tytuł, klucze oraz wynik do bazy Firebase Firestore.",
            ft.Icons.UPLOAD_FILE
        ),

    ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)