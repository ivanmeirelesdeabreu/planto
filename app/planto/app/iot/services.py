from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from .models import ConfiguracaoIrrigacao, ComandoIrrigacao


@transaction.atomic
def avaliar_e_criar_comando_auto(dispositivo, umidade_atual):
    """Regra automática: se umidade < mínima e respeitado intervalo mínimo, cria comando PENDENTE."""
    config = (ConfiguracaoIrrigacao.objects
              .filter(dispositivo=dispositivo, ativo=True)
              .order_by('-data_criacao')
              .first())
    if not config:
        return None

    if umidade_atual >= config.umidade_minima:
        return None

    janela = timezone.now() - timedelta(minutes=config.intervalo_minimo_minutos)
    existe_recente = ComandoIrrigacao.objects.filter(
        dispositivo=dispositivo,
        data_criacao__gte=janela,
    ).exclude(status=ComandoIrrigacao.Status.ERRO).exists()

    if existe_recente:
        return None

    cmd = ComandoIrrigacao.objects.create(
        dispositivo=dispositivo,
        segundos_irrigacao=config.segundos_irrigacao,
        status=ComandoIrrigacao.Status.PENDENTE,
        origem=ComandoIrrigacao.Origem.AUTO,
    )
    return cmd
