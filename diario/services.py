from json import JSONDecodeError
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import EntradaDiario, Tarefa
from django.utils import timezone
from datetime import datetime, date
import json
from django.http import JsonResponse
from .serializers import Validators

class Tarefas:
    @staticmethod
    def definir_tarefas_futuras(request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                date = data.get("date")
                if not date:
                    return JsonResponse({"error": "Nenhuma data selecionada"})

                tipo = data.get('tarefa_tipo')
                if tipo not in ['PR', 'SC']: #tarefa pra vc fazer dps: crie uma validação para tipos de tarefas no serializers.py
                    return JsonResponse({'error': 'Tipo desconhecido'}, status=400)

                descricao = data.get('descricao')
                #validate_date = Validators.validate_date(date)

                entrada, created = EntradaDiario.objects.get_or_create(data=datetime.strptime(date, '%d/%m/%Y').date())
                tarefa_add = Tarefa.objects.create(entrada_diario=entrada, tipo=tipo, descricao=descricao)

                return JsonResponse({
                    'mensagem': 'Tarefa adicionada.',
                    'id': tarefa_add.id,
                    'entrada_diario': tarefa_add.entrada_diario.id,
                    'tipo': tarefa_add.tipo,
                    'descricao': tarefa_add.descricao,
                })

            except JSONDecodeError:
                return JsonResponse({"error": "JSONDecodeError"}, status=400)
        else:
            return JsonResponse({
                'mensagem': 'Metodo não permitido.',
            })
