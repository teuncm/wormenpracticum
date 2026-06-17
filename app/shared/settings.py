import ctypes
import sys

from PySide6.QtCore import QCoreApplication, QSettings

from app.shared.constants import APP_ORG, APP_TITLE

APP_USER_MODEL_ID = f"{APP_ORG}.{APP_TITLE}"


def configure_app_identity() -> None:
    """Set stable app identity for native OS-backed settings."""
    QCoreApplication.setOrganizationName(APP_ORG)
    QCoreApplication.setApplicationName(APP_TITLE)


def configure_windows_app_user_model_id() -> None:
    """Set the Windows taskbar identity used for icon grouping/caching."""
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_USER_MODEL_ID
        )
    except Exception:
        pass


def create_app_settings() -> QSettings:
    """Create persistent user settings stored in the native system location."""
    return QSettings(
        QSettings.Format.NativeFormat,
        QSettings.Scope.UserScope,
        APP_ORG,
        APP_TITLE,
    )
