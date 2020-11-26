# Copyright (c) 2020 Igino Corona, Pluribus One SRL;
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see https://www.gnu.org/licenses/

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from audit import models

admin.site.site_header = _('GDPR Registry App')
admin.site.site_title = admin.site.site_header
admin.index_title = admin.site.site_header


def link(url, text, target_blank=False):
    target = 'target="_blank"' if target_blank else ''
    return format_html('<a href="{url}" {target}>{text}</a>', url=url, target=target, text=text)

def admin_url(app_label, model_name, page, args=()):
    return reverse('admin:{}_{}_{}'.format(app_label, model_name, page), args=args)

def admin_url_for_obj(obj, page, args=()):
    return admin_url(obj._meta.app_label, obj._meta.model_name, page, args=args)

def admin_change_url(obj):
    return admin_url_for_obj(obj, page='change', args=(obj.pk,))

def admin_add_link(model_name, text, app='audit', page='add'):
    url = admin_url(app, model_name, page)
    return link(url=url, text=text)

def admin_changelist_url(obj):
    return admin_url_for_obj(obj, page='changelist')

def admin_change_link(obj, text):
    if not obj:
        return "-"
    return link(url=admin_change_url(obj), text=text)

def admin_changelist_link(obj, text):
    return link(url=admin_changelist_url(obj), text=text)


class Common:

    def admin_changelist_count(self, manytomany):
        items = manytomany.all()
        count = items.count()
        if count:
            return admin_changelist_link(items[0], count)
        else:
            return None

class UserAdmin(admin.ModelAdmin, Common):
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    list_display = ('name', 'surname', 'username',)

    def name(self, obj):
        return obj.user.first_name
    name.short_description = _("Name")
    name.admin_order_field = 'user__first_name'

    def surname(self, obj):
        return obj.user.last_name
    surname.short_description = _("Surname")
    surname.admin_order_field = 'user__last_name'

    def username(self, obj):
        return obj.user.username
    username.short_description = _("Username")
    username.admin_order_field = 'user__username'


class BaseAdmin(admin.ModelAdmin, Common):
    search_fields = ('name', 'description',)
    list_display = ('name', 'short_description')


class ListAdmin(BaseAdmin):
    add_fields = ('classification',)
    search_fields = BaseAdmin.search_fields + add_fields
    list_display = BaseAdmin.list_display + add_fields


class PDFDocumentAdmin(BaseAdmin):
    list_display = ('md5sum',) + BaseAdmin.list_display


@admin.register(models.BusinessProcess)
class BusinessProcessAdmin(BaseAdmin):
    search_fields = BaseAdmin.search_fields + ('owner',)
    list_display = BaseAdmin.list_display + ('owner_link', 'organization', 'activity_link')

    def organization(self, obj):
        for o in obj.yourorganization_set.all():
            return admin_change_link(o, o)
    organization.short_description = _("Organization")

    def owner_link(self, obj):
        return admin_change_link(obj.owner, obj.owner)
    owner_link.short_description = _("Business Owner")

    def activity_link(self, obj):
        return self.admin_changelist_count(obj.activities)
    activity_link.short_description = _("Processing Activities")


@admin.register(models.DataCategory)
class DataCategoryAdmin(ListAdmin):
    pass


@admin.register(models.ProcessingPurpose)
class ProcessingPurposeAdmin(ListAdmin):
    pass


@admin.register(models.ProcessingType)
class ProcessingTypeAdmin(ListAdmin):
    pass


@admin.register(models.ProcessingLegal)
class ProcessingLegalAdmin(ListAdmin):
    pass


@admin.register(models.ProcessingActivityClassificationLevel)
class ProcessingActivityClassificationLevelAdmin(ListAdmin):
    pass


@admin.register(models.NatureOfTransferToThirdCountry)
class NatureOfTransferToThirdCountryAdmin(ListAdmin):
    pass


@admin.register(models.RecipientCategory)
class RecipientCategoryAdmin(ListAdmin):
    pass


@admin.register(models.DataSubjectCategory)
class DataSubjectCategoryAdmin(ListAdmin):
    list_display = ListAdmin.list_display + ('vulnerable',)

@admin.register(models.DPIA)
class DPIAAdmin(PDFDocumentAdmin):
    pass


@admin.register(models.DataSubjectRights)
class DataSubjectRightsAdmin(PDFDocumentAdmin):
    pass


@admin.register(models.Data)
class DataAdmin(BaseAdmin):
    search_fields = BaseAdmin.search_fields
    list_display = BaseAdmin.list_display + ('processing_activities', 'category', 'risk', 'is_managed', 'has_breach_detection', 'has_breach_response', 'dpia_bool')

    def is_managed(self, instance):
        return bool(instance.management)
    is_managed.short_description = _('Managed')
    is_managed.boolean = True

    def has_breach_detection(self, instance):
        return bool(instance.breach_detection)
    has_breach_detection.short_description = _('Breach Detection')
    has_breach_detection.boolean = True

    def has_breach_response(self, instance):
        return bool(instance.breach_response)
    has_breach_response.short_description = _('Breach Response')
    has_breach_response.boolean = True

    def processing_activities(self, obj):
        return self.admin_changelist_count(obj.processingactivity_set)
    processing_activities.short_description = _('Activities')

    def dpia_bool(self, obj):
        return bool(obj.dpia)
    dpia_bool.boolean = True
    dpia_bool.short_description = _("DPIA")


@admin.register(models.ProcessingActivity)
class ProcessingActivityAdmin(BaseAdmin):
    search_fields = BaseAdmin.search_fields + ('purpose__name', 'proc_type__name',)
    list_display = BaseAdmin.list_display + ('business_process',
                                              'legal', 'data_audit_link', 'start_date', 'end_date',)

    def business_process(self, obj):
        for o in obj.businessprocess_set.all():
            return admin_change_link(o, o)
    business_process.short_description = _("Business Process")


    def data_audit_link(self, obj):
        return self.admin_changelist_count(obj.data_audit)
    data_audit_link.short_description = _("Data Audits")


@admin.register(models.DataProtectionOfficer)
class DataProtectionOfficerAdmin(UserAdmin):
    other_fields = ('address', 'telephone', 'staff')
    search_fields = UserAdmin.search_fields + other_fields
    list_display = UserAdmin.list_display + other_fields + ('organizations',)

    def organizations(self, obj):
        return self.admin_changelist_count(obj.yourorganization_set)
    organizations.short_description = _("Organizations")


@admin.register(models.BusinessOwner)
class BusinessOwnerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('business',)

    def business(self, obj):
        return self.admin_changelist_count(obj.businessprocess_set)
    business.short_description = _("Business Processes")


@admin.register(models.ProcessorContract)
class ProcessorContractAdmin(PDFDocumentAdmin):
    list_display = PDFDocumentAdmin.list_display + ('processor',)


class OrganizationAdmin(BaseAdmin):
    search_fields = BaseAdmin.search_fields + ('email', 'address', 'country', 'statute')
    list_display = search_fields


@admin.register(models.ThirdParty)
class ThirdPartyAdmin(OrganizationAdmin):
    add_fields = ('category',)
    search_fields = OrganizationAdmin.search_fields + add_fields
    list_display = OrganizationAdmin.list_display + add_fields + ('third_country_transfer',)


@admin.register(models.YourOrganization)
class YourOrganizationAdmin(OrganizationAdmin):
    list_display = OrganizationAdmin.list_display + ('officer_link', 'business_processes', 'report')

    def officer_link(self, obj):
        return admin_change_link(obj.officer, obj.officer)
    officer_link.short_description = _("Data Protection Officer")

    def business_processes(self, obj):
        return self.admin_changelist_count(obj.business)
    business_processes.short_description = _("Business Processes")

    def report(self, obj):
        return link(url=reverse('report', kwargs={'org_pk': obj.pk}), target_blank=True, text=_("Create"))
    report.short_description = _("PDF Report")





class RiskAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ('risk',)


@admin.register(models.DataManagementPolicy)
class DataManagementPolicyAdmin(RiskAdmin):
    list_display = RiskAdmin.list_display + ('retention',)


@admin.register(models.DataBreachDetection)
class DataBreachDetectionAdmin(RiskAdmin):
    pass


@admin.register(models.DataBreachResponse)
class DataBreachResponseAdmin(RiskAdmin):
    pass
