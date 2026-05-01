from django.utils import timezone
from rest_framework import serializers

from .models import Dispositivo, LeituraUmidade, ComandoIrrigacao, ExecucaoIrrigacao, ConfiguracaoIrrigacao
from .utils import hash_token


class LeituraCreateSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    data_hora = serializers.DateTimeField()
    umidade = serializers.DecimalField(max_digits=5, decimal_places=2)
    bateria = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    payload_json = serializers.JSONField(required=False, allow_null=True)

    def validate(self, attrs):
        token = attrs.get('token')
        token_hash = hash_token(token)
        dispositivo = Dispositivo.objects.filter(token_hash=token_hash, ativo=True).first()
        if not dispositivo:
            raise serializers.ValidationError('Token inválido ou dispositivo inativo.')
        attrs['dispositivo'] = dispositivo
        attrs['token_hash'] = token_hash
        return attrs

    def create(self, validated_data):
        dispositivo = validated_data['dispositivo']
        dispositivo.ultimo_contato = timezone.now()
        dispositivo.save(update_fields=['ultimo_contato'])

        leitura = LeituraUmidade.objects.create(
            dispositivo=dispositivo,
            data_hora=validated_data['data_hora'],
            umidade=validated_data['umidade'],
            bateria=validated_data.get('bateria'),
            payload_json=validated_data.get('payload_json'),
        )
        return leitura


class ComandoPollSerializer(serializers.Serializer):
    comando_id = serializers.UUIDField(allow_null=True)
    ligar_bomba = serializers.BooleanField()
    segundos = serializers.IntegerField(required=False, allow_null=True)


class ExecucaoConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    comando_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=['FINALIZADO','ERRO','EXECUTANDO'])
    segundos_executados = serializers.IntegerField(required=False, allow_null=True)
    mensagem = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payload_json = serializers.JSONField(required=False, allow_null=True)
    data_inicio = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        token_hash = hash_token(attrs['token'])
        dispositivo = Dispositivo.objects.filter(token_hash=token_hash, ativo=True).first()
        if not dispositivo:
            raise serializers.ValidationError('Token inválido ou dispositivo inativo.')

        comando = ComandoIrrigacao.objects.filter(uuid=attrs['comando_id'], dispositivo=dispositivo).first()
        if not comando:
            raise serializers.ValidationError('Comando não encontrado para este dispositivo.')

        attrs['dispositivo'] = dispositivo
        attrs['comando'] = comando
        return attrs


class AdminDispositivoCreateSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=100)
    descricao = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AdminConfiguracaoSerializer(serializers.Serializer):
    umidade_minima = serializers.DecimalField(max_digits=5, decimal_places=2)
    segundos_irrigacao = serializers.IntegerField()
    intervalo_minimo_minutos = serializers.IntegerField(required=False, default=30)
    ativo = serializers.BooleanField(required=False, default=True)


class AdminComandoManualSerializer(serializers.Serializer):
    segundos_irrigacao = serializers.IntegerField()
    observacao = serializers.CharField(required=False, allow_blank=True, allow_null=True)
