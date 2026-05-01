import uuid
from django.db import models


class Dispositivo(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    token_hash = models.CharField(max_length=255, unique=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultimo_contato = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = '"iot"."iot_dispositivo"'

    def __str__(self):
        return f"{self.nome} ({self.uuid})"


class LeituraUmidade(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, db_column='dispositivo_id', related_name='leituras')
    data_hora = models.DateTimeField()
    umidade = models.DecimalField(max_digits=5, decimal_places=2)
    bateria = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    payload_json = models.JSONField(blank=True, null=True)
    data_recebimento = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"iot"."leitura_umidade"'
        indexes = [
            models.Index(fields=['dispositivo','-data_hora'], name='idx_leitura_disp_data'),
            models.Index(fields=['-data_hora'], name='idx_leitura_data'),
        ]

    def __str__(self):
        return f"{self.dispositivo.nome} {self.data_hora} {self.umidade}%"


class ConfiguracaoIrrigacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, db_column='dispositivo_id', related_name='configuracoes')
    umidade_minima = models.DecimalField(max_digits=5, decimal_places=2)
    segundos_irrigacao = models.IntegerField()
    intervalo_minimo_minutos = models.IntegerField(default=30)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"iot"."configuracao_irrigacao"'

    def __str__(self):
        return f"Config {self.dispositivo.nome} (min={self.umidade_minima}, seg={self.segundos_irrigacao})"


class ComandoIrrigacao(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE'
        ENVIADO = 'ENVIADO'
        EXECUTANDO = 'EXECUTANDO'
        FINALIZADO = 'FINALIZADO'
        ERRO = 'ERRO'

    class Origem(models.TextChoices):
        AUTO = 'AUTO'
        MANUAL = 'MANUAL'
        AGENDADO = 'AGENDADO'

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, db_column='dispositivo_id', related_name='comandos')
    segundos_irrigacao = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    origem = models.CharField(max_length=20, choices=Origem.choices, default=Origem.AUTO)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField(blank=True, null=True)
    data_confirmacao = models.DateTimeField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        db_table = '"iot"."comando_irrigacao"'
        indexes = [
            models.Index(fields=['status'], name='idx_comando_status'),
            models.Index(fields=['dispositivo'], name='idx_comando_disp'),
        ]

    def __str__(self):
        return f"{self.dispositivo.nome} {self.status} {self.segundos_irrigacao}s"


class ExecucaoIrrigacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    comando = models.ForeignKey(ComandoIrrigacao, on_delete=models.CASCADE, db_column='comando_id', related_name='execucoes')
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, db_column='dispositivo_id', related_name='execucoes')
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField(blank=True, null=True)
    segundos_executados = models.IntegerField(blank=True, null=True)
    sucesso = models.BooleanField(blank=True, null=True)
    mensagem = models.TextField(blank=True, null=True)
    payload_json = models.JSONField(blank=True, null=True)
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"iot"."execucao_irrigacao"'
        indexes = [
            models.Index(fields=['dispositivo'], name='idx_execucao_disp'),
            models.Index(fields=['comando'], name='idx_execucao_cmd'),
        ]

    def __str__(self):
        return f"Exec {self.dispositivo.nome} ({self.sucesso})"
