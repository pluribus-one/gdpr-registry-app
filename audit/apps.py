from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuditConfig(AppConfig):
    name = 'audit'
    verbose_name = _("Audit")


class AxesConfig(AppConfig):
    name = 'axes'
    verbose_name = _("Access Control")
