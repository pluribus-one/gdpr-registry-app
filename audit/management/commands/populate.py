from django.core.management.base import BaseCommand
from audit import models
from registry import settings
import json

class Command(BaseCommand):
    help = 'Load Predefined lists'

    def add_arguments(self, parser):
        parser.add_argument('fpath', type=str)

    def handle(self, *args, **options):
        fpath = input('Enter a suitable JSON list file (list.en.json or list.it.json): ')
        with open(fpath) as f:
            d = json.load(f)
        key_class = [
                     {'Indicative List of Purpose Types': models.ProcessingPurpose},
                     {'Basis for Processing': models.ProcessingLegal},
                     {'Indicative List of Functional Data Categories': models.DataCategory},
                     {'Type of Processing': models.ProcessingType},
                     {'Indicative List of Recipient Categories': models.RecipientCategory},
                     {'Nature of Transfer to Third Country/International Organization': models.NatureOfTransferToThirdCountry},
                     {'Indicative List of Data Subject Categories': models.DataSubjectCategory},
                     ]
        for _dict in key_class:
            for key, model in _dict.items():
                data = d[key]
                for cat, values in data.items():
                    for value in values:
                        name = value.get('name')
                        try:
                            obj = model.objects.get(name=name)
                            for k, v in value.items():
                                setattr(obj, k, v)
                        except model.DoesNotExist:
                            obj = model(classification=cat, **value)
                        obj.save()
                        self.stdout.write(self.style.SUCCESS('Successfully saved %s "%s"' % (model, name)))