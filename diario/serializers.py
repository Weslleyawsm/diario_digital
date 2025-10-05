from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone, dates
from datetime import datetime, timedelta, time, date
from .models import EntradaDiario

class Validators:

    @staticmethod
    def validate_date(data):
        if not data:
            raise ValidationError({'mensagem': 'Data no formato incorreto!'})
        try:
            data_formatada = datetime.strptime(data, '%d/%m/%Y').date()
            hoje = date.today()
            if data_formatada <= hoje:
                raise ValidationError({'mensagem': 'A data deve ser futura!'})

            dates_bd = EntradaDiario.objects.filter(data__gte=hoje).values_list('data', flat=True)
            if data_formatada in dates_bd:
                raise ValidationError({'mensagem': 'Já existe uma data cadastrada!'})

            return data_formatada
        except ValueError as e:
            return ValidationError({'mensagem': str(e)})
