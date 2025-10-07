from django.urls import path
from . import views, services

urlpatterns = [
    path('', views.pagina_diario, name='pagina_diario'),
    path('api/tarefa/adicionar/', views.adicionar_tarefas, name='adicionar_tarefas'),
    path('api/tarefa/toggle/', views.toggle_tarefa, name='toggle_tarefa'),
    path('api/tarefa/atualizar-descricao/', views.atualizar_descricao, name='atualizar_descricao'),
    path('api/tarefa/remover/', views.remover_tarefa, name='remover_tarefa'),
    path('api/diario/campos-reflexao/', views.campos_gratidao, name='campos_gratidao'),
    path('api/diario/tarefas-futuras/', views.definir_tarefas_futuras, name='definir_tarefas_futuras'),
    path('api/diario/consultar-tarefas/', views.consultar_tarefas, name='consultar_tarefas'),
]
