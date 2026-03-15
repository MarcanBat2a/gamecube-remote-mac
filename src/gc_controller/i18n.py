"""
Internationalization (i18n) module.

Provides a simple gettext-style translation system. The English text is used
as the lookup key; translations are stored in per-language dictionaries.

Usage:
    from .i18n import _
    label = _("Ready to Connect")

Strings containing placeholders use .format() AFTER translation:
    label = _("Connected: {}").format(mac)
"""

# ── Current language ────────────────────────────────────────────────
_current_language: str = "en"

SUPPORTED_LANGUAGES = {
    "en": "English",
    "fr": "Français",
}


def set_language(lang: str) -> None:
    """Set the active language. Falls back to English if not supported."""
    global _current_language
    _current_language = lang if lang in SUPPORTED_LANGUAGES else "en"


def get_language() -> str:
    """Return the current language code."""
    return _current_language


def _(text: str) -> str:
    """Translate *text* to the current language.

    Returns the original text if no translation exists or the language is English.
    """
    if _current_language == "en":
        return text
    table = _TRANSLATIONS.get(_current_language)
    if table is None:
        return text
    return table.get(text, text)


# ── French translations ────────────────────────────────────────────

_FR: dict[str, str] = {
    # ── Window title ──
    "NSO GameCube Controller Pairing App": "NSO GameCube Controller — Appairage",
    # ── Controller UI (controller_ui.py) ──
    "Controller {}": "Manette {}",
    "Ready to Connect": "Prêt à connecter",
    "Connect USB": "Connexion USB",
    "Pair New Wireless Controller": "Appairer une manette sans fil",
    "Calibration Wizard": "Assistant de calibration",
    # ── Connection status (app.py) ──
    "No unclaimed controllers found": "Aucune manette disponible trouvée",
    "Disconnect USB": "Déconnecter USB",
    "No free slots available": "Aucun emplacement libre",
    "Initializing...": "Initialisation…",
    "Pairing cancelled": "Appairage annulé",
    "No devices found": "Aucun appareil trouvé",
    "Connecting...": "Connexion…",
    "Disconnect": "Déconnecter",
    "Connected: {}": "Connecté : {}",
    "Connected via BLE": "Connecté via BLE",
    "Error: {}": "Erreur : {}",
    "Scanning for known controllers...": "Recherche des manettes connues…",
    "Found known controller: {}": "Manette connue trouvée : {}",
    "Auto-connected via BLE": "Auto-connecté via BLE",
    "Pair New Controller": "Appairer une manette",
    "BLE disconnected — reconnecting...": "BLE déconnecté — reconnexion…",
    "Reconnecting...": "Reconnexion…",
    "Reconnected via BLE": "Reconnecté via BLE",
    "Controller disconnected — reconnecting...": "Manette déconnectée — reconnexion…",
    "Reconnected": "Reconnecté",
    "Connected & Ready": "Connecté et prêt",
    "Waiting for Dolphin...": "En attente de Dolphin…",
    "DSU :{} — Ready": "DSU :{} — Prêt",
    "New controller — starting calibration...": "Nouvelle manette — début de la calibration…",
    # ── BLE error dialogs (app.py) ──
    "BLE Error": "Erreur BLE",
    "Error": "Erreur",
    "Emulation Error": "Erreur d'émulation",
    "Settings": "Paramètres",
    "Failed to start BLE service:\n{}": "Échec du démarrage du service BLE :\n{}",
    "BLE service failed to start.\n\n"
    "Authentication may have been cancelled.": "Le service BLE n'a pas pu démarrer.\n\n"
    "L'authentification a peut-être été annulée.",
    "Failed to initialize BLE:\n{}\n\n"
    "Make sure a Bluetooth adapter is connected.": "Échec de l'initialisation BLE :\n{}\n\n"
    "Vérifiez qu'un adaptateur Bluetooth est connecté.",
    "Connection failed": "Échec de la connexion",
    # ── Emulation errors (app.py / virtual_gamepad.py) ──
    "Emulation not available for mode '{}'.\n{}": "Émulation non disponible pour le mode « {} ».\n{}",
    "Failed to start emulation: {}": "Échec du démarrage de l'émulation : {}",
    "Failed to start DSU emulation: {}": "Échec du démarrage de l'émulation DSU : {}",
    "Failed to start pipe emulation: {}": "Échec du démarrage de l'émulation pipe : {}",
    "Settings saved successfully!": "Paramètres enregistrés avec succès !",
    "Failed to save settings: {}": "Échec de l'enregistrement : {}",
    # Virtual gamepad error messages (individual sentence keys)
    "DSU server mode should always be available.": "Le mode serveur DSU devrait toujours être disponible.",
    "Dolphin pipe emulation is only supported on macOS and Linux.": "L'émulation Dolphin pipe n'est supportée que sur macOS et Linux.",
    "Could not create Dolphin pipe '{}' in any detected Dolphin directory.": "Impossible de créer le pipe Dolphin « {} » dans un répertoire Dolphin détecté.",
    "Xbox 360 controller emulation is not supported on macOS.": "L'émulation de manette Xbox 360 n'est pas supportée sur macOS.",
    "macOS does not allow user-space creation of virtual HID game controllers.": "macOS ne permet pas la création de périphériques HID virtuels.",
    # ── Calibration wizard (calibration.py / app.py) ──
    "Continue": "Continuer",
    "Move sticks to all extremes, then click Continue": "Déplacez les sticks dans toutes les directions, puis cliquez Continuer",
    "Release both triggers, then click Continue": "Relâchez les deux gâchettes, puis cliquez Continuer",
    "Push LEFT trigger to analog max (before click)": "Poussez la gâchette GAUCHE au maximum analogique (avant le clic)",
    "Fully press LEFT trigger past the bump": "Enfoncez complètement la gâchette GAUCHE au-delà du cran",
    "Fully press RIGHT trigger past the bump": "Enfoncez complètement la gâchette DROITE au-delà du cran",
    "Push RIGHT trigger to analog max (before click)": "Poussez la gâchette DROITE au maximum analogique (avant le clic)",
    "Calibrate Triggers": "Calibrer les gâchettes",
    "Trigger calibration completed": "Calibration des gâchettes terminée",
    # ── Settings dialog (ui_settings_dialog.py) ──
    "Emulation Mode": "Mode d'émulation",
    "Xbox 360": "Xbox 360",
    "Dolphin Pipe": "Dolphin Pipe",
    "DSU Server": "Serveur DSU",
    "Trigger Mode": "Mode des gâchettes",
    "100% at bump": "100 % au cran",
    "100% at press": "100 % à fond",
    "Auto-connect USB at startup": "Auto-connexion USB au démarrage",
    "Auto-scan BLE at startup": "Auto-scan BLE au démarrage",
    "Minimize to system tray": "Réduire dans la barre système",
    "Save": "Enregistrer",
    "Stop Emulation": "Arrêter l'émulation",
    "Start Emulation": "Démarrer l'émulation",
    "Test Rumble": "Tester la vibration",
    "Paired Controllers": "Manettes appairées",
    "About": "À propos",
    "Source Code on GitHub": "Code source sur GitHub",
    "Credits & Special Thanks": "Crédits et remerciements",
    "No paired controllers": "Aucune manette appairée",
    "Forget": "Oublier",
    "Forget All": "Tout oublier",
    "Language": "Langue",
    # ── BLE device picker (ui_ble_dialog.py) ──
    "Select BLE Controller": "Sélectionner une manette BLE",
    "Select a controller to connect:": "Sélectionnez une manette à connecter :",
    "Name": "Nom",
    "Address": "Adresse",
    "Signal": "Signal",
    "(unknown)": "(inconnu)",
    "Cancel": "Annuler",
    "Connect": "Connecter",
    # ── BLE scan wizard (ui_ble_scan_wizard.py) ──
    "Wireless Controller Setup": "Configuration de la manette sans fil",
    "Step 1 of 2: Environment Scan": "Étape 1 sur 2 : Scan de l'environnement",
    "Make sure your controller is OFF or not in pairing mode.\n"
    "This scan captures nearby Bluetooth devices.": "Assurez-vous que votre manette est ÉTEINTE ou pas en mode appairage.\n"
    "Ce scan capture les appareils Bluetooth à proximité.",
    "Scan": "Scanner",
    "Scanning environment...": "Scan de l'environnement…",
    "Found {} nearby device(s).": "{} appareil(s) à proximité trouvé(s).",
    "Step 2 of 2: Controller Scan": "Étape 2 sur 2 : Scan de la manette",
    "Now press and hold the pairing button on your controller.\n"
    "Wait for the LED to flash, then click Scan.": "Appuyez et maintenez le bouton d'appairage de votre manette.\n"
    "Attendez que la LED clignote, puis cliquez Scanner.",
    "Scanning for new devices...": "Recherche de nouveaux appareils…",
    "No New Devices Detected": "Aucun nouvel appareil détecté",
    "No new Bluetooth devices appeared between scans.\n"
    "Make sure your controller is in pairing mode\n"
    "(LED should be flashing) and try again.": "Aucun nouvel appareil Bluetooth n'est apparu entre les scans.\n"
    "Assurez-vous que votre manette est en mode appairage\n"
    "(la LED doit clignoter) et réessayez.",
    "Retry": "Réessayer",
    "Multiple New Devices Found": "Plusieurs nouveaux appareils détectés",
    "Select your controller from the new devices:": "Sélectionnez votre manette parmi les nouveaux appareils :",
    "Back": "Retour",
    # ── Connection manager (connection_manager.py) ──
    "Looking for device...": "Recherche de l'appareil…",
    "Device not found": "Appareil non trouvé",
    "Device found": "Appareil trouvé",
    "Sending initialization data...": "Envoi des données d'initialisation…",
    "Sending LED data...": "Envoi des données LED…",
    "USB initialization complete": "Initialisation USB terminée",
    "USB initialization failed: {}": "Échec de l'initialisation USB : {}",
    "Connecting via HID...": "Connexion via HID…",
    "Connected via HID": "Connecté via HID",
    "Failed to connect via HID": "Échec de la connexion HID",
    "HID connection failed: {}": "Échec de la connexion HID : {}",
    # ── System tray (app.py) ──
    "Show": "Afficher",
    "Quit": "Quitter",
    "NSO GC Controller": "NSO GC Controller",
}

# ── Translation table registry ──────────────────────────────────────
_TRANSLATIONS: dict[str, dict[str, str]] = {
    "fr": _FR,
}
