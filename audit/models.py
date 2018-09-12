# Copyright (c) 2018 Igino Corona, Pluribus One SRL;
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

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.template.defaultfilters import truncatewords
from django.utils.html import format_html
import hashlib
import PyPDF2
from collections import OrderedDict

HINT_TYPES = OrderedDict([
                            ('suggestion', _("Suggestions")),
                            ('issue', _("Issues")),
                            ('warning', _("Warnings")),
                        ])

class Hint:

    def __init__(self, obj, text, hint_type):
        self.text = text
        self.obj = obj
        self.hint_type = hint_type
        try:
            self.obj_class = self.obj.__class__._meta.verbose_name.title()
        except:
            self.obj_class = ''
        assert(hint_type in HINT_TYPES)

    def __str__(self):
        return format_html("{} {} {}", self.text, self.obj_class, getattr(self.obj, 'admin_change_link', str(self.obj)))


class HintList:

    def __init__(self):
        self.list = OrderedDict((hint, []) for hint in HINT_TYPES.keys())

    def append(self, obj):
        assert(isinstance(obj, Hint))
        self.list[obj.hint_type].append(obj)

    def extend(self, hint_list):
        assert (isinstance(hint_list, HintList))
        for key, objs in hint_list.list.items():
            self.list[key].extend(objs)

    def get_items(self):
        return [(key, HINT_TYPES[key], hint_list) for key, hint_list in self.list.items()]

    def set_admin_change_link(self, admin_change_link):
        for hint_list in self.list.values():
            for hint in hint_list:
                try:
                    hint.obj.admin_change_link = admin_change_link(hint.obj, str(hint.obj))
                except:
                    pass

    @property
    def is_empty(self):
        for l in self.list.values():
            if len(l) > 0:
                return False
        return True


class Base(models.Model):
    last_update = models.DateTimeField(auto_now=True, verbose_name=_("Last Update"))

    def get_hints(self):
        return HintList()

    class Meta:
        abstract = True


class NameDesc(Base):
    name = models.CharField(unique=True,
                            max_length=100,
                            verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"), blank=True)

    def short_description(self):
        return truncatewords(self.description, 50)
    short_description.short_description = _("Description")

    def get_hints(self):
        hints = HintList()
        if not self.description:
            hints.append(Hint(obj=self, text=_("Missing description on"), hint_type='warning'))
        return hints

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Organization(NameDesc):
    email = models.EmailField(verbose_name=_("Email"))
    address = models.CharField(max_length=50, verbose_name=_("Address"))
    country = models.CharField(max_length=200, verbose_name=_("Country"))
    telephone = models.CharField(max_length=50, verbose_name=_("Telephone"))
    statute = models.CharField(max_length=200, verbose_name=_("Statute"))
    third_country = models.BooleanField(verbose_name=_("Third Country"), help_text=_("Mark this field if the organization resides in a country outside of the European Union (EU) and the European Economic Area (EEA)."))
    international = models.BooleanField(verbose_name=_("International"), help_text=_("Mark this field if the organization and its subordinate bodies are governed by public international law"))

    class Meta:
        abstract = True

def media_file_name(instance, filename):
    return 'documents/{}.pdf'.format(instance.name)

class PDFDocument(NameDesc):
    document = models.FileField(verbose_name=_("Document File"), upload_to=media_file_name)
    md5sum = models.CharField(blank=True, verbose_name=_("MD5Sum"), max_length=36)

    def clean(self): # PDF file validation
        try:
            PyPDF2.PdfFileReader(self.document)
        except Exception as e:
            raise ValidationError(_("Only PDF files are accepted"))

    def save(self, *args, **kwargs):
        if not self.pk:  # file is new
            md5 = hashlib.md5()
            for chunk in self.document.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        super(PDFDocument, self).save(*args, **kwargs)

class List(NameDesc):
    classification = models.CharField(blank=True, max_length=100, verbose_name=_("Classification"),
                                      help_text=_("Insert a general classification for this entry (if any)"))
    article = models.PositiveIntegerField(null=True, blank=True,
                                          verbose_name=_("GDPR Article"),
                                          help_text=_("Reference to GDPR Article (if any)"))
    url = models.URLField(blank=True,
                          verbose_name=_("Reference URL"),
                          help_text=_("Reference URL (if any)")
                          )

    def __str__(self):
        if self.classification:
            return "{} - {}".format(self.classification, self.name)
        else:
            return super(List, self).__str__()

    class Meta:
        abstract = True



class ProcessingLegal(List):
    class Meta:
        verbose_name = _("Legal Base for Processing")
        verbose_name_plural = _("Legal Bases for Processing")


class ProcessingPurpose(List):
    class Meta:
        verbose_name = _("Purpose of Processing")
        verbose_name_plural = _("Purposes of Processing")


class ProcessingType(List):
    class Meta:
        verbose_name = _("Type of Processing")
        verbose_name_plural = _("Types of Processing")


class DataCategory(List):
    special = models.BooleanField(verbose_name=_("Special Category"),
                                  help_text=_("Mark this field if the Data Category is special. "
                                  "The processing of this data category shall normally be prohibited."))

    class Meta:
        verbose_name = _("Functional Data Category")
        verbose_name_plural = _("Functional Data Categories")


class ProcessingActivityClassificationDocument(PDFDocument):
    class Meta:
        verbose_name = _("Processing Activity Classification Document")
        verbose_name_plural = _("Processing Activity Classification Documents")


class ProcessingActivityClassificationLevel(List):
    document = models.ForeignKey(ProcessingActivityClassificationDocument, null=True, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Processing Activity Classification Document"))

    class Meta:
        verbose_name = _("Processing Activity Classification Level")
        verbose_name_plural = _("Processing Activity Classification Levels")


class RecipientCategory(List):
    class Meta:
        verbose_name = _("Recipient Category")
        verbose_name_plural = _("Recipient Categories")


class NatureOfTransferToThirdCountry(List):
    class Meta:
        verbose_name = _("Nature of Transfer to third-country/international organization")
        verbose_name_plural = _("Natures of Transfer to third-country/international organization")


class DataSubjectCategory(List):
    vulnerable = models.BooleanField(verbose_name=_("Vulnerable Category"),
                                     help_text=_("Indicates whether the data subjects are considered a vulnerable category. "
                                         "Mark this flag if the data subjects involved are in a situation in which there is a lack of "
                                         "parity in the relationship between the data subject and the controller, such as children, employees, patients, etc."
                                         "Unmark this flag if none of the categories as mentioned above are involved."))

    class Meta:
        verbose_name = _("Data Subject Category")
        verbose_name_plural = _("Data Subject Categories")


class ThirdParty(Organization):
    category =  models.ForeignKey(RecipientCategory, on_delete=models.DO_NOTHING,
                                  verbose_name=_("Category"),
                                  help_text=_("In the context of consent-base processing, to comply with Articles 13 and 14 "
                                  "of the GDPR, controllers will need to provide a full list of recipients or categories of recipients including processors."))
    third_country_transfer = models.ForeignKey(NatureOfTransferToThirdCountry, blank=True, null=True, on_delete=models.DO_NOTHING,
                                               verbose_name=_("Nature of Transfer to third-country/international organization"),
                                               help_text=_("Please specify why the data is transferred to this third-country/international organization"))
    appropriate_safeguards = models.TextField(verbose_name=_("Appropriate Data Safeguards"), blank=True,
                                              help_text=_("In case of data transfer to a third country/international "
                                              "organization & transfer based on GDPR Article 49(2), list the documents that "
                                              "clarify the appropriate safeguards and where these documents are stored."))

    def get_hints(self):
        hints = super().get_hints()
        if self.third_country_transfer:
            hints.extend(self.third_country_transfer.get_hints())
            if not self.appropriate_safeguards:
                hints.append(Hint(obj=self, text=_("No appropriate safeguards have been specified for third-country/international data transfers"), hint_type='issue'))
        return hints

    def clean(self):
        # TODO: add other validation, e.g., EU country/international
        if self.third_country_transfer and (not (self.third_country or self.international)):
            raise ValidationError(_("This organization is not marked as third country or international. If you want to set the nature of transfer to third country/international organization, please first flag one of these fields."))

    class Meta:
        verbose_name = _("Third-party Organization")
        verbose_name_plural = _("Third-party Organizations")

class AuditUser(Base):
    user = models.OneToOneField(User, verbose_name=_("Registered User"), on_delete=models.CASCADE)

    def __str__(self):
        if self.user.first_name:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        return self.user.username

    class Meta:
        abstract = True

class DataProtectionOfficer(AuditUser):
    address = models.CharField(max_length=50, verbose_name=_("Address"))
    telephone = models.CharField(max_length=50, verbose_name=_("Telephone"))
    staff = models.BooleanField(verbose_name=_("Part of Staff"),
                                help_text=_('Is DPO part of the controller organization staff?'))

    def get_hints(self):
        hints = super().get_hints()
        if self.staff:
            hints.append(Hint(obj=self, text=_("DPO is part of the staff of the controller organization. You should be able to demonstrate that the DPO is an independent person."), hint_type='warning'))
        return hints

    class Meta:
        verbose_name = _("Data Protection Officer (DPO)")
        verbose_name_plural = _("Data Protection Officers (DPOs)")


class DPIA(PDFDocument):
    class Meta:
        verbose_name = _("Data protection Impact Assessment (DPIA)")
        verbose_name_plural = _("Data protection Impact Assessments (DPIAs)")


class DataSubjectRights(PDFDocument):
    class Meta:
        verbose_name = _("Data Subject Rights Document")
        verbose_name_plural = _("Data Subject Rights Documents")


class ProcessorContract(PDFDocument):
    processor = models.ForeignKey(ThirdParty, on_delete=models.DO_NOTHING,
                                     verbose_name=_("Processor"),
                                     help_text=_("Third-party organization with which the Contract has been signed."))

    def get_hints(self):
        hints = super().get_hints()
        hints.extend(self.processor.get_hints())
        return hints

    class Meta:
        verbose_name = _("Processor Contract")
        verbose_name_plural = _("Processor Contracts")


RISK_CHOICES = (
                (0, _("Unknown")),
                (1, _("Low")),
                (2, _("Mid")),
                (3, _("High")),
                )

class CommonRiskHint:

    def get_hints(self):
        hints = super().get_hints()
        if self.risk == 0:
            hints.append(Hint(obj=self, text=_("Unknown risk to personal data for"), hint_type='issue'))
        if not self.data_set.count():
            hints.append(Hint(obj=self, text=_("No data audit for"), hint_type='error'))
        if not self.risk_mitigation:
            hints.append(Hint(obj=self, text=_("No description of risk mitigation measures for"), hint_type='warning'))
        return hints

class DataManagementPolicy(NameDesc, CommonRiskHint):
    processor_contracts = models.ManyToManyField(ProcessorContract,
                                    verbose_name=_("Data Processor Contracts"),
                                    help_text=_(
                                        "If the data is ACTUALLY transferred to OTHER organizations (e.g., Data Processors), "
                                        "please upload the contract that regulates this data transfer, and relevant information about each third-party organization."),
                                    blank=True)
    retention = models.IntegerField(null=True, blank=True, verbose_name=_("Retention period for the processed data, in Days"))
    risk_mitigation = models.TextField(blank=True, verbose_name=_("Risk Mitigation Measures"),
                                        help_text=_("Information about the risk mitigation measures related to the data processing, against Data Breaches."))
    risk = models.PositiveSmallIntegerField(default=0, verbose_name=_("Residual Risk"), choices=RISK_CHOICES,
                                            help_text=_("Indicate the residual risk to the fundamental rights and freedoms of data subjects, "
                                            "given the mitigation measures that have been put in place."))
    subject_rights = models.ForeignKey(DataSubjectRights, null=True, blank=True, on_delete=models.DO_NOTHING,
                            verbose_name=_("Data Subject Rights"),
                            help_text=_("Reference the documents that determine the procedures intended to guard the rights of data subjects. "
                                        "The document should also indicate which special measures have been taken to enforce/support " 
                                        "the exercising of the rights of data subjects."))
    subject_notification = models.TextField(blank=True, verbose_name=_("Data Subject Notification"),
                                      help_text=_("Indicate how data subjects are notified that their data have been registered."))
    comments = models.TextField(blank=True, verbose_name=_("Comments"),
                                help_text=_("Please put any comments to the data management policy."))

    def get_hints(self):
        hints = super().get_hints()
        if self.risk >= 2:
            hints.append(Hint(obj=self, text=_("Mid/high residual data management risk for"), hint_type='issue'))
        if self.retention is None:
            hints.append(Hint(obj=self,
                              text=_("No retention value specified for"),
                              hint_type='issue'))
        if self.subject_rights:
            hints.extend(self.subject_rights.get_hints())
        else:
            hints.append(Hint(obj=self,
                              text=_("Missing description of the procedures adopted to safeguard the rights of data subjects on"),
                              hint_type='warning'))
        if not self.subject_notification:
            hints.append(Hint(obj=self,
                              text=_("Missing description of the notification procedures to data subjects for"),
                              hint_type='warning'))

        for contract in self.processor_contracts.all():
            hints.extend(contract.get_hints())

        return hints

    class Meta:
        verbose_name = _("Data Management Policy")
        verbose_name_plural = _("Data Management Policies")


class DataBreachDetection(NameDesc, CommonRiskHint):
    risk_mitigation = models.TextField(blank=True, verbose_name=_("Risk Mitigation Measures"),
                                        help_text=_("Information about the risk mitigation measures related to the detection of data breaches"))
    risk = models.PositiveSmallIntegerField(default=0, verbose_name=_("Residual Risk"), choices=RISK_CHOICES,
                                            help_text=_("Indicate the residual risk of missing a data breach due to lacking detection measures/technology"))
    comments = models.TextField(blank=True, verbose_name=_("Comments"),
                                help_text=_("Please put any comments to the data management policy."))

    def get_hints(self):
        hints = super().get_hints()
        if self.risk >= 2:
            hints.append(Hint(obj=self, text=_("Mid/high residual risk of missing data breaches for"), hint_type='issue'))
        return hints

    class Meta:
        verbose_name = _("Data Breach Detection")
        verbose_name_plural = _("Data Breach Detection")


class DataBreachResponse(NameDesc, CommonRiskHint):
    risk_mitigation = models.TextField(blank=True, verbose_name=_("Risk Mitigation Measures"),
                                        help_text=_("Information about the risk mitigation measures for the response to data breaches. "
                                                    "To this end, a suitable incident response plan should be put in place, that include the"
                                                    "mandatory notification of data breaches to supervisory authority and all involved parties."))
    risk = models.PositiveSmallIntegerField(default=0, verbose_name=_("Residual Risk"), choices=RISK_CHOICES,
                                            help_text=_("Indicate the residual risk of not responding properly to a data breach due to lacking detection measures/technology."))
    comments = models.TextField(blank=True, verbose_name=_("Comments"),
                                help_text=_("Please put any comments to the data management policy."))


    def get_hints(self):
        hints = super().get_hints()
        if self.risk >= 2:
            hints.append(Hint(obj=self, text=_("Mid/high residual risk for data breach response on"), hint_type='issue'))
        return hints

    class Meta:
        verbose_name = _("Incident Response Plan")
        verbose_name_plural = _("Incident Response Plan")


class Data(NameDesc):
    category = models.ForeignKey(DataCategory, on_delete=models.DO_NOTHING,
                                 verbose_name=_("Data Category"))
    subject_category = models.ManyToManyField(DataSubjectCategory,
                                              verbose_name=_("Data Subject Category"))
    source = models.TextField(blank=True, verbose_name=_("Original Data Source"),
                              help_text=_("Indicate the source of the data if not the data subjects themselves."))
    comments = models.TextField(verbose_name=_("Comments"),
                                help_text=_("Please put any comments to the data audit."),
                                blank=True)
    risk = models.PositiveSmallIntegerField(default=0, verbose_name=_("Inherent Risk"), choices=RISK_CHOICES,
                                       help_text=_("Indicate the inherent risk to the fundamental rights and freedoms of data subjects associated to the data audit."))
    management = models.ForeignKey(DataManagementPolicy, null=True, blank=True, on_delete=models.DO_NOTHING,
                                   verbose_name=_("Data Management Policy"))
    breach_detection = models.ForeignKey(DataBreachDetection, null=True, blank=True,
                                         verbose_name=_("Data Breach Detection"),
                                   on_delete=models.DO_NOTHING,)
    breach_response = models.ForeignKey(DataBreachResponse, null=True, blank=True,
                                        verbose_name=_("Incident Response Plan"),
                                   on_delete=models.DO_NOTHING,)
    dpia = models.ForeignKey(DPIA, null=True, blank=True, on_delete=models.DO_NOTHING,
                             verbose_name=_("Data protection Impact Assessment"),
                             help_text=_("If the processing activity probably entails a high risk for the fundamental "
                                         "rights and freedoms of data subjects, a DPIA must be completed (GDPR Article 35)."))

    def get_processing_activities(self):
        return ", ".join([a.name for a in self.processingactivity_set.all()])
    get_processing_activities.short_description = _("Processing Activities")

    def get_hints(self):
        hints = super().get_hints()
        if not self.processingactivity_set.count():
            hints.append(Hint(obj=self, text=_("No processing activity associated to"), hint_type='error'))
        if not self.management:
            hints.append(Hint(obj=self, text=_("No data management policy specified for"), hint_type='issue'))
        else:
            hints.extend(self.management.get_hints())

        if self.subject_category.count():
            for cat in self.subject_category.all():
                hints.extend(cat.get_hints())
        else:
            hints.append(Hint(obj=self, text=_("No subject categories specified for"), hint_type='warning'))

        if self.risk >= 2: # MID/HIGH INHERENT RISK LEVEL
            if not self.breach_detection:
                hints.append(Hint(obj=self, text=_("Mid/High inherent risk, but no data breach detection technology specified for"), hint_type='issue'))
            if not self.breach_response:
                hints.append(Hint(obj=self, text=_("Mid/High inherent risk, but no data breach response plan specified for"), hint_type='issue'))
            if self.risk >= 3 and (not self.dpia): # INHERENTLY HIGH RISK LEVEL
                hints.append(Hint(obj=self, text=_("Mid/High inherent risk, but no Data Protection Impact Assessment specified for"), hint_type='issue'))
        elif self.risk == 0:
            hints.append(Hint(obj=self, text=_("Unknown inherent risk level for"), hint_type='issue'))
        if self.breach_detection:
            hints.extend(self.breach_detection.get_hints())
        if self.breach_response:
            hints.extend(self.breach_response.get_hints())
        if self.dpia:
            hints.extend(self.dpia.get_hints())
        return hints

    class Meta:
        verbose_name = _("Data Audit")
        verbose_name_plural = _("Data Audits")

class ProcessingActivity(NameDesc):
    data_audit = models.ManyToManyField(Data, blank=True, verbose_name=_("Data Audit"),
                                        help_text=_("Specify the data handled by this activity (output of a data audit process)."))
    purpose = models.ForeignKey(ProcessingPurpose, on_delete=models.DO_NOTHING,
                                verbose_name=_("Purpose"))
    proc_type = models.ForeignKey(ProcessingType, on_delete=models.DO_NOTHING,
                                  verbose_name=_("Processing Type"),)
    start_date = models.DateField(null=True, blank=True,
                                  verbose_name=_("Start Date"),)
    end_date = models.DateField(null=True, blank=True,
                                verbose_name=_("End Date"),
                                help_text=_("Processing end date, if applicable. By filling in this date, you are declaring that processing ceases as of that date."))
    legal = models.ForeignKey(ProcessingLegal, on_delete=models.DO_NOTHING,
                              verbose_name=_("Legal Base for Processing"),
                              help_text=_("What is the Legal Base for Processing? It is mandatory!"))
    technology = models.TextField(blank=True, verbose_name=_("Technology"), help_text=_("How the activity is performed. Description of the technologies, applications, and software employed in the processing activity."), null=True)
    alternate_activity = models.ForeignKey('self', null=True, blank=True, on_delete=models.DO_NOTHING,
                                           verbose_name=_("Alternate Activity"),
                                           help_text=_("Where appropriate, reference the processing activity that replaces the terminated activity. This creates a history in the registry. "
                                            "This may be of use when the legal basis of a processing activity shifts, for instance as the result of a statutory change."))
    comments = models.TextField(blank=True, verbose_name=_("Comments"),
                                help_text=_("Please put any comments to the processing activity."))

    classification = models.ForeignKey(ProcessingActivityClassificationLevel,  on_delete=models.DO_NOTHING,
                                       verbose_name=_("Classification Level"),
                                       help_text=_("Indicate the classification level of the "
                                                  "processing activity according to the organization's "
                                                  "classification system (choose the highest in case multiple are "
                                                  "involved)."),
                                       null=True,
                                       blank=True)

    def get_hints(self):
        hints = super().get_hints()
        if not self.get_business_process():
            hints.append(Hint(obj=self, text=_("No business process associated to"), hint_type='error'))
        if not self.start_date:
            hints.append(Hint(obj=self, text=_("Missing start date for"), hint_type='warning'))
        if not self.technology:
            hints.append(Hint(obj=self, text=_("Missing description of technology for"), hint_type='warning'))
        if self.data_audit.count():
            for data in self.data_audit.all():
                hints.extend(data.get_hints())
        else:
            hints.append(Hint(obj=self, text=_("Please specify at least one data audit for"), hint_type='suggestion'))
        return hints

    def get_business_process(self):
        try:
            return self.businessprocess_set.all()[0]
        except:
            return None
    get_business_process.short_description = _('Business Process')

    def clean(self):
        try:
            if self.outsourcing.processor == self.get_business_process().get_organization():
                raise ValidationError(
                    _("Outsourcing prefigures the assignment of the processing activity to another organization"))
        except ValidationError:
            raise
        except:
            pass

    class Meta:
        verbose_name = _("Processing Activity")
        verbose_name_plural = _("Processing Activities")

class BusinessOwner(AuditUser):

    def get_business(self):
        return ", ".join([b.name for b in self.businessprocess_set.all()])

    def get_hints(self):
        hints = super().get_hints()
        if not self.self.businessprocess_set.count():
            hints.append(Hint(obj=self, text=_("No business process associated with"), hint_type='error'))
        return hints

    class Meta:
        verbose_name = _("Business Owner")
        verbose_name_plural = _("Business Owners")

class BusinessProcess(NameDesc):
    owner = models.ForeignKey(BusinessOwner, null=True, blank=True, on_delete=models.DO_NOTHING,
                              verbose_name=_("Process Owner"),
                              help_text=_("Please indicate who is responsible for and manages this business process."))
    activities = models.ManyToManyField(ProcessingActivity, blank=True,
                                        verbose_name=_("Processing Activities"),
                                        help_text=_("You should insert all processing activities that may handle personal data are part of the business process (e.g., Collection of Curriculum Vitae)"))

    def get_organization(self):
        try:
            return self.yourorganization_set.all()[0]
        except:
            return None
    get_organization.short_description = _('Organization')

    def clean(self):
        """We could avoid such check using ForeignKey on each activity instead of a ManyToMany in this obj.
        However, to exploit the admin interface it is much more intuitive to use a ManyToMany in this obj and perform this additional check."""
        if self.pk is None:
            return
        for activity in self.activities.all():
            other_business = activity.businessprocess_set.all().exclude(pk=self.pk).all()
            if other_business.count():
                raise ValidationError(_("Activity {} is already assigned to another Business Process: {}").format(activity, other_business[0]))

    def get_hints(self):
        hints = super().get_hints()
        if not self.get_organization():
            hints.append(Hint(obj=self, text=_("No organization associated to"), hint_type='error'))
        if not self.owner:
            hints.append(Hint(obj=self, text=_("No owner for"), hint_type='warning'))
        if self.activities.count():
            for activity in self.activities.all():
                hints.extend(activity.get_hints())
        else:
            hints.append(Hint(obj=self, text=_("Please specify at least one processing activity for"), hint_type='suggestion'))
        return hints

    class Meta:
        verbose_name = _("Business Process")
        verbose_name_plural = _("Business Processes")


class YourOrganization(Organization):
    officer = models.ForeignKey(DataProtectionOfficer, null=True, blank=True, on_delete=models.DO_NOTHING,
                                verbose_name=_("Data Protection Officer (DPO)"),
                                help_text=_("Please insert the Data Protection Officer (if any). A data protection officer (DPO) may be mandatory for "
                                "public authorities, or if certain types of processing activities are carried out by the organization. The DPO must be independent, an expert in data protection, adequately "
                                "resourced, and report to the highest management level."))
    business = models.ManyToManyField(BusinessProcess, blank=True,
                                      verbose_name=_("Business Processes"),
                                      help_text=_("You should insert each business process in the Organization that may handle personal data (e.g., Human Resources)"))
    public_authority = models.BooleanField(verbose_name=_("Public Authority"),
                                           help_text=_(
                                               "Mark this field if the organization is a public authority (except for courts acting in their judicial capacity)"))
    monitoring = models.BooleanField(verbose_name=_("Large-scale Monitoring"),
                                     help_text=_(
                                         "Mark this field if the organization's core activities require large scale, regular and systematic monitoring of individuals (for example, online behaviour tracking)"))
    special_category = models.BooleanField(verbose_name=_("Special Data"),
                                     help_text=_(
                                         "Mark this field if the organization's core activities consist of processing on a large scale of special category data, or data relating to criminal convictions and offences"))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hints = None

    def get_business_processes(self):
        return self.business.count()
    get_business_processes.short_description = _("Business Processes")

    def clean(self):
        """We could avoid such check using ForeignKey on each business instead of a ManyToMany in this obj.
        However, to exploit the admin interface it is much more intuitive to use a ManyToMany in this obj and perform this additional check."""
        if self.pk is None:
            return
        for process in self.business.all():
            other_orgs = process.yourorganization_set.all().exclude(pk=self.pk).all()
            if other_orgs.count():
                raise ValidationError(_("Business Process {} is already assigned to another Organization: {}").format(process, other_orgs[0]))


    def get_hints(self):
        hints = super().get_hints()
        if (not self.officer) and (self.public_authority or self.monitoring or self.special_category):
            if self.public_authority:
                text = _("Public authorities ")
            elif self.monitoring:
                text = _("When systematic, large-scale monitoring of individuals is performed as core activity, Organizations ")
            elif self.special_category:
                text = _("When large-scale processing of special data about individuals is performed as core activity, Organizations ")
            hints.append(Hint(obj=self, text=_("{} must appoint a Data Protection Officer").format(text), hint_type='issue'))
        if self.business.count():
            for process in self.business.all():
                hints.extend(process.get_hints())
        else:
            hints.append(Hint(obj=self, text=_("Please insert at least one business process into"), hint_type='suggestion'))
        return hints


    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Your Organizations")


