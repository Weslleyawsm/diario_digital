from django.db import models
from django.utils import timezone



class EntradaDiario(models.Model):
    data = models.DateField(unique=True, default=timezone.now)
    preciso_melhorar_em = models.TextField(blank=True, null=True)
    coisa_que_me_orgulho = models.TextField(blank=True, null=True)
    gratidao = models.TextField(blank=True, null=True)
    reflexao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Entrada de Diário"
        verbose_name_plural = "Entradas de Diário"
        ordering = ['-data']

    def __str__(self):
        return f"Diário de {self.data.strftime('%d/%m/%Y')}"

    def calcular_pontuacao(self):
        tarefas = self.tarefas.all()
        principais_concluidas = tarefas.filter(tipo='PR', concluida=True).count()
        secundarias_concluidas = tarefas.filter(tipo='SC', concluida=True).count()

        total_principais = tarefas.filter(tipo='PR').count()
        total_secundarias = tarefas.filter(tipo='SC').count()

        pontos_conquistados = (principais_concluidas * 3) + (secundarias_concluidas * 1)
        pontos_maximos = (total_principais * 3) + (total_secundarias * 1)

        return {
            'conquistada': pontos_conquistados,
            'maxima': pontos_maximos,
        }

class Tarefa(models.Model):
    TIPO_CHOICES = [
        ('PR', 'Principal'),
        ('SC', 'Secundária'),
    ]
    entrada_diario = models.ForeignKey(EntradaDiario, on_delete=models.CASCADE, related_name='tarefas')
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default='PR')
    descricao = models.TextField(blank=True, null=True)
    concluida = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['ordem', 'criado_em']

    def __str__(self):
        tipo_texto = "Principal" if self.tipo == 'PR' else "Secundária"
        status = "✓" if self.concluida else "○"
        return f"{status} [{tipo_texto}] {self.descricao[:50]}"

    def pontos(self):
        """Retorna quantos pontos esta tarefa vale"""
        return 3 if self.tipo == 'PR' else 1