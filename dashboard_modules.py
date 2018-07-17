from django.utils.translation import gettext_lazy as _
from jet.dashboard.modules import DashboardModule
from audit.models import YourOrganization, HintList, Hint
from audit.admin import admin_change_link, admin_add_link

class Stat(DashboardModule):
    title = _('Registry Status')
    template = 'dashboard_modules/stat.html'

    class Media:
        js = ('js/chart.bundle.js', 'js/utils.js')

    def init_with_context(self, context):
        hints = HintList()
        if not YourOrganization.objects.count():
            link = admin_add_link('yourorganization', _("First time here? Click to add your organization in the registry"))
            hints.append(Hint(obj="", hint_type='suggestion',
                        text=link))

        else:
            for org in YourOrganization.objects.all():
                hints.extend(org.get_hints())
            hints.set_admin_change_link(admin_change_link)
            suggestions = hints.list['suggestion']
            if not suggestions:
                hints.append(Hint(obj="", hint_type='suggestion',
                                 text=_("GDPR is a continuous process. Make sure that all your business processes and processing activities that manage personal data are updated in this registry.")))
        self.children = hints