from json import JSONDecodeError
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import EntradaDiario, Tarefa
from .services import Tarefas
from django.utils import timezone
from datetime import datetime, date
import json
from django.http import JsonResponse

@csrf_exempt
def adicionar_tarefas(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            entrada, created = EntradaDiario.objects.get_or_create(data=date.today())

            tipo = data.get('tipo')
            if tipo not in ['PR', 'SC']:
                return JsonResponse({'error': 'Tipo desconhecido'}, status=400)

            descricao = data.get('descricao')
            if descricao is None:
                descricao = ''
            tarefa_add = Tarefa.objects.create(entrada_diario=entrada, tipo=tipo, descricao=descricao)

            return JsonResponse({
                'mensagem': 'Tarefa adicionada.',
                'id': tarefa_add.id,
                'entrada_diario': tarefa_add.entrada_diario.id,
                'tipo': tarefa_add.tipo,
                'descricao': tarefa_add.descricao,
            })

        except JSONDecodeError as e:
            return JsonResponse({
                'error': str(e),
            }, status=500)

        except Exception as e:
            return JsonResponse({'mensagem': str(e)}, status=500)

    else:
        return JsonResponse({
            'mensagem': 'Metodo não permitido.',
        })

@csrf_exempt
def toggle_tarefa(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id = data.get('id')
            concluida = data.get('concluida')

            if concluida == False:
                tarefa_update = Tarefa.objects.filter(id=id).update(concluida=True)
            else:
                tarefa_update = Tarefa.objects.filter(id=id).update(concluida=False)

            tarefa = Tarefa.objects.get(id=id)
            return JsonResponse({
                'mensagem': 'Tarefa atualizada.',
                'id': tarefa.id,
                'tarefa': tarefa.descricao,
                'concluida': tarefa.concluida
            })

        except JSONDecodeError as e:
            return JsonResponse({e})
        except Exception as e:
            return JsonResponse({'mensagem': str(e)}, status=500)
    else:
        return JsonResponse({'mensagem': 'metodo não permitido.'})
@csrf_exempt
def atualizar_descricao(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            id = data.get('id')
            descricao = data.get('descricao')

            if descricao:
                tarefa = Tarefa.objects.filter(id=id).update(descricao=descricao)
            else:
                JsonResponse({'mensagem': 'Não foi passado nenhuma descricao.'})

            tarefa_atualizada = Tarefa.objects.get(id=id)
            pontuacao = tarefa_atualizada.entrada_diario.calcular_pontuacao()
            return JsonResponse({
                'mensagem': 'Tarefa atualizada.',
                'id': tarefa_atualizada.id,
                'tarefa': tarefa_atualizada.descricao,
                'concluida': tarefa_atualizada.concluida,
                'pontuacao': pontuacao
            })


        except Exception as e:
            return JsonResponse({'mensagem': str(e)}, status=500)
    else:
        return JsonResponse({'mensagem': 'metodo não permitido.'})

@csrf_exempt
def remover_tarefa(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id = data.get('id')
            tarefa = Tarefa.objects.get(id=id)
            tarefa.delete()
            return JsonResponse({
                'mensagem': 'Tarefa removida.',
                'id': id,
                'tarefa': tarefa.descricao,
            })

        except JSONDecodeError as e:
            return JsonResponse({'error': e})
        except Exception as e:
            return JsonResponse({'mensagem error': str(e)}, status=500)
    else:
        return JsonResponse({'mensagem': 'metodo não permitido.'})

@csrf_exempt
def campos_gratidao(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id = data.get('id')
            preciso_melhorar_em = data.get('preciso_melhorar_em')
            coisa_que_me_orgulho = data.get('coisa_que_me_orgulho')
            gratidao = data.get('gratidao')
            reflexao = data.get('reflexao')

            if not id:
                return JsonResponse({'mensagem': 'Passe o ID'})

            diario = EntradaDiario.objects.get(id=id)
            entrada_diario = EntradaDiario.objects.filter(id=id).update(
                          preciso_melhorar_em=preciso_melhorar_em,
                          coisa_que_me_orgulho=coisa_que_me_orgulho,
                          gratidao=gratidao,
                          reflexao=reflexao)
            return JsonResponse({
                'mensagem': 'Diario atualizado',
                'id': diario.id,
                'preciso_melhorar_em': preciso_melhorar_em,
                'coisa_que_me_orgulho': coisa_que_me_orgulho,
                'gratidao': gratidao,
                'reflexao': reflexao
            })

        except JSONDecodeError as e:
            return JsonResponse({'error': e})
        except Exception as e:
            return JsonResponse({'mensagem error': str(e)}, status=500)
    else:
        return JsonResponse({'mensagem': 'metodo não permitido.'})


def pagina_diario(request):
    entrada, created = EntradaDiario.objects.get_or_create(data=date.today())
    tarefas = Tarefa.objects.filter(entrada_diario=entrada).order_by('ordem')
    pontuacao = entrada.calcular_pontuacao()

    # Converter tarefas para JSON
    tarefas_json = json.dumps([{
        'id': t.id,
        'tipo': t.tipo,
        'descricao': t.descricao,
        'concluida': t.concluida
    } for t in tarefas])

    context = {
        'entrada': entrada,
        'tarefas': tarefas_json,
        'pontuacao': pontuacao,
        'data_hoje': date.today(),
    }

    return render(request, 'index.html', context)

@csrf_exempt
def definir_tarefas_futuras(request):
    return Tarefas.definir_tarefas_futuras(request)
