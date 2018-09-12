from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard
from jet.dashboard.models import UserDashboardModule
from jet.utils import get_admin_site_name
from dashboard_modules import Stat
from django.urls import reverse


class IndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)

        site_name = get_admin_site_name(context)

        self.children.append(Stat())

        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _('Quick links'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_('Return to site'), '/'],
                [_('Change password'),
                 reverse('%s:password_change' % site_name)],
                [_('Log out'), reverse('%s:logout' % site_name)],
            ],
            column=0,
            order=0
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('auth.*',),
            column=1,
            order=0
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Administration'),
            models=('auth.*',),
            column=2,
            order=0
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            10,
            column=0,
            order=1
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            children=[
                {
                    'title': _('HOW TO WORK'),
                    'url': reverse('data_audit'),
                    'external': True,
                },
                {
                    'title': _('Pluribus One Technology'),
                    'url': 'https://gdpr.pluribus-one.it/{}/technology'.format(context.get('request').LANGUAGE_CODE),
                    'external': True,
                },
                {
                    'title': _('Pluribus One Services'),
                    'url': 'https://gdpr.pluribus-one.it/{}/services'.format(context.get('request').LANGUAGE_CODE),
                    'external': True,
                },
            ],
            column=2,
            order=1
        ))

    # def get_or_create_module_models(self, user):
    #     module_models = []
    #
    #     i = 0
    #
    #     for module in self.children:
    #         column = module.column if module.column is not None else i % self.columns
    #         order = module.order if module.order is not None else int(i / self.columns)
    #
    #         obj, created = UserDashboardModule.objects.get_or_create(
    #             title=module.title,
    #             app_label=self.app_label,
    #             user=user.pk,
    #             module=module.fullname(),
    #             column=column,
    #             order=order,
    #             settings=module.dump_settings(),
    #             children=module.dump_children()
    #         )
    #         module_models.append(obj)
    #         i += 1
    #
    #     return module_models
    #
    # def load_modules(self):
    #     module_models = self.get_or_create_module_models(self.context['request'].user)
    #
    #     loaded_modules = []
    #
    #     for module_model in module_models:
    #         module_cls = module_model.load_module()
    #         if module_cls is not None:
    #             module = module_cls(model=module_model, context=self.context)
    #             loaded_modules.append(module)
    #
    #     self.modules = loaded_modules