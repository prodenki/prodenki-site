"""Site-wide settings. Edit these values, then run `python3 build.py`.

Empty strings switch a feature off: no phone -> no call button,
no GA4 id -> no analytics and no cookie banner, and so on.
"""

SITE = {
    "domain": "https://prodenki.pt",
    "name": "ProDenki",
    "legal_name": "ProDenki — Engenharia & Automação Industrial",
    "email": "geral@prodenki.pt",

    # Fill these in: they show in the header, footer, floating buttons and Google data.
    "phone": "",            # e.g. "+351 912 345 678"
    "whatsapp": "",         # digits only, with country code, e.g. "351912345678"
    "street": "",           # e.g. "Rua da Indústria, 10"
    "postal_code": "",      # e.g. "2710-000"
    "city": "",             # e.g. "Sintra"
    "region": "",           # e.g. "Lisboa"
    # Link to the company system (button in the header and footer). Empty = no button.
    "system_url": "https://sistema.prodenki.pt/app/",

    "linkedin": "https://www.linkedin.com/company/prodenki/",  # LinkedIn company page
    # Parent group and partner sites (logos link to them, open in a new tab).
    "setair_url": "https://setair.pt",
    "weg_url": "https://www.weg.net/institutional/PT/pt/",
    "facebook": "",
    "instagram": "",

    # Quote form: Web3Forms key for geral@prodenki.pt (requests are delivered there).
    "web3forms_key": "9dea9b12-7491-46cc-8c91-bd3f5d45e029",

    # Measurement (from the marketing plan). Leave empty until the accounts exist.
    "ga4_id": "",           # e.g. "G-XXXXXXXXXX"
    "gtm_id": "",           # e.g. "GTM-XXXXXXX" (use either GTM or GA4)
    "meta_pixel_id": "",    # e.g. "123456789012345"

    # WEG: True shows a "Pedir orçamento WEG" button and a "Fornecimento de material WEG"
    # option in the quote form (selling WEG equipment separately). Off: WEG only inside our panels.
    "weg_separate_supply": False,

    # GitHub repository that holds this site, e.g. "prodenki/prodenki-site".
    # When set, the photo panel is published at /admin.
    "github_repo": "prodenki/prodenki-site",

    "google_site_verification": "FFmLolDcKQV4cdhwDUYdcAcqK84yxFcfA5gAY-p9neM",
}

# Language order in the switcher; the first one is served at the site root.
LANGS = ["pt", "en", "es"]
