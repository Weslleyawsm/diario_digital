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
from django.db.models import Count


class Tarefas:
    @staticmethod
    def definir_tarefas_futuras(request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                date = data.get("date")
                """if not date:
                    return JsonResponse({"error": "Nenhuma data selecionada"})"""
                #troquei o validate_date_df por validate_date_consulta pra fazer um teste. mas tenho que voltar dps por validate_date_df
                date_formatado = Validators.validate_date_consulta(date)

                tipo = data.get('tarefa_tipo')
                if tipo not in ['PR', 'SC']: #tarefa pra vc fazer dps: crie uma validação para tipos de tarefas no serializers.py
                    return JsonResponse({'error': 'Tipo desconhecido'}, status=400)

                descricao = data.get('descricao')
                #validate_date = Validators.validate_date(date)

                entrada, created = EntradaDiario.objects.get_or_create(data=date_formatado)
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

    @staticmethod
    def consultar_dias(request):
        if request.method == "GET":
            try:
                date_params = request.GET.get("date")
                date_formatado = Validators.validate_date_consulta(date_params)

                date_bd = EntradaDiario.objects.filter(data=date_formatado).first()
                if date_bd is None:
                    return JsonResponse({"error": "Não há tarefas para esse dia!"})
                id_date = date_bd.id

                list_tarefas = []
                tarefas = Tarefa.objects.filter(entrada_diario_id=id_date).values("id", "tipo", "descricao", "concluida")
                for tarefa in tarefas:
                    dict_tarefa = {
                        'id': tarefa['id'],
                        'tipo': tarefa['tipo'],
                        'descricao': tarefa['descricao'],
                        'concluida': tarefa['concluida'],
                    }
                    list_tarefas.append(dict_tarefa)
                return JsonResponse({f"Tarefas do dia {date_formatado.strftime('%d/%m/%Y')}": list_tarefas})
            except ValidationError:
                return JsonResponse({"error": "Nenhuma data selecionada"})
        else:
            return JsonResponse({"error": "Nenhuma data selecionada"})

    @staticmethod
    def metricas_tarefas(request):
        if request.method == "GET":
            periodo = request.GET.get("periodo")
            try:
                date_hoje, date_subtraido = Validators.validate_date_periodo(periodo)

                # ✅ Usando 'tarefas' (com S)
                data_periodo = EntradaDiario.objects.filter(
                    data__gte=date_subtraido
                ).annotate(
                    quantidade=Count('tarefas')  # ← Aqui!
                ).values('data', 'quantidade').order_by('-data')

                # Formatar datas
                list_dias = [
                    {
                        'date': entrada['data'].strftime("%d/%m/%Y"),
                        'quantidade': entrada['quantidade']
                    }
                    for entrada in data_periodo
                ]

                return JsonResponse({'data': list_dias})

            except ValidationError as e:
                return JsonResponse({"error": f"Nenhuma data selecionada {str(e)}"})
        else:
            return JsonResponse({'mensagem': 'Metodo não permitido.'})
