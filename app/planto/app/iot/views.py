from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from .models import Dispositivo, ComandoIrrigacao, ExecucaoIrrigacao, ConfiguracaoIrrigacao
from .serializers import (
    LeituraCreateSerializer,
    ComandoPollSerializer,
    ExecucaoConfirmSerializer,
    AdminDispositivoCreateSerializer,
    AdminConfiguracaoSerializer,
    AdminComandoManualSerializer,
)
from .services import avaliar_e_criar_comando_auto
from .utils import gerar_token_plano, hash_token


def _get_token_from_request(request):
    # Header tem prioridade
    token = request.headers.get('X-Device-Token')
    if token:
        return token
    auth = request.headers.get('Authorization')
    if auth and auth.lower().startswith('token '):
        return auth.split(' ', 1)[1].strip()
    # Depois, query param
    token = request.query_params.get('token')
    if token:
        return token
    # Por fim, body
    if isinstance(request.data, dict):
        return request.data.get('token')
    return None


class LeituraUmidadeCreateAPI(APIView):
    """POST /api/iot/leituras - recebe leitura do sensor e pode gerar comando automático."""

    def post(self, request):
        #serializer = LeituraCreateSerializer(data=request.data)


        serializer = LeituraCreateSerializer(
            data=request.data,
            context={"request": request}
        )


        serializer.is_valid(raise_exception=True)
        leitura = serializer.save()

        # Regra automática
        cmd = avaliar_e_criar_comando_auto(leitura.dispositivo, float(leitura.umidade))

        return Response({
            'leitura_id': str(leitura.uuid),
            'comando_criado': str(cmd.uuid) if cmd else None,
        }, status=status.HTTP_201_CREATED)


class ComandoPollAPI(APIView):
    """GET /api/iot/comandos - dispositivo consulta comandos pendentes."""

    def get(self, request):
        token = _get_token_from_request(request)
        if not token:
            return Response({'detail': 'Token é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        token_hash = hash_token(token)
        dispositivo = Dispositivo.objects.filter(token_hash=token_hash, ativo=True).first()
        if not dispositivo:
            return Response({'detail': 'Token inválido ou dispositivo inativo.'}, status=status.HTTP_401_UNAUTHORIZED)

        dispositivo.ultimo_contato = timezone.now()
        dispositivo.save(update_fields=['ultimo_contato'])

        cmd = (ComandoIrrigacao.objects
               .filter(dispositivo=dispositivo, status=ComandoIrrigacao.Status.PENDENTE)
               .order_by('data_criacao')
               .first())

        if not cmd:
            payload = {'comando_id': None, 'ligar_bomba': False, 'segundos': None}
            return Response(payload, status=status.HTTP_200_OK)

        cmd.status = ComandoIrrigacao.Status.ENVIADO
        cmd.data_envio = timezone.now()
        cmd.save(update_fields=['status','data_envio'])

        payload = {'comando_id': cmd.uuid, 'ligar_bomba': True, 'segundos': cmd.segundos_irrigacao}
        out = ComandoPollSerializer(payload)
        return Response(out.data, status=status.HTTP_200_OK)


class ExecucaoConfirmAPI(APIView):
    """POST /api/iot/execucoes - dispositivo confirma execução de irrigação."""

    def post(self, request):
        serializer = ExecucaoConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dispositivo = serializer.validated_data['dispositivo']
        comando = serializer.validated_data['comando']
        st = serializer.validated_data['status']

        # Atualiza comando
        if st == 'EXECUTANDO':
            comando.status = ComandoIrrigacao.Status.EXECUTANDO
            comando.save(update_fields=['status'])
            return Response({'detail': 'Status atualizado para EXECUTANDO.'}, status=status.HTTP_200_OK)

        comando.status = ComandoIrrigacao.Status.FINALIZADO if st == 'FINALIZADO' else ComandoIrrigacao.Status.ERRO
        comando.data_confirmacao = timezone.now()
        comando.save(update_fields=['status','data_confirmacao'])

        data_inicio = serializer.validated_data.get('data_inicio') or timezone.now()
        execucao = ExecucaoIrrigacao.objects.create(
            comando=comando,
            dispositivo=dispositivo,
            data_inicio=data_inicio,
            data_fim=timezone.now(),
            segundos_executados=serializer.validated_data.get('segundos_executados'),
            sucesso=(st == 'FINALIZADO'),
            mensagem=serializer.validated_data.get('mensagem'),
            payload_json=serializer.validated_data.get('payload_json'),
        )

        return Response({'execucao_id': str(execucao.uuid)}, status=status.HTTP_201_CREATED)


# --------------------------
# ADMIN APIs (para cadastro e comando manual)
# --------------------------

class AdminDispositivoCreateAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminDispositivoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_plano = gerar_token_plano()
        token_hash = hash_token(token_plano)

        disp = Dispositivo.objects.create(
            nome=serializer.validated_data['nome'],
            descricao=serializer.validated_data.get('descricao'),
            token_hash=token_hash,
        )
        return Response({
            'dispositivo_uuid': str(disp.uuid),
            'token': token_plano,
        }, status=status.HTTP_201_CREATED)


class AdminConfigSetAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, dispositivo_uuid):
        disp = Dispositivo.objects.filter(uuid=dispositivo_uuid).first()
        if not disp:
            return Response({'detail': 'Dispositivo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminConfiguracaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cfg = ConfiguracaoIrrigacao.objects.create(
            dispositivo=disp,
            umidade_minima=serializer.validated_data['umidade_minima'],
            segundos_irrigacao=serializer.validated_data['segundos_irrigacao'],
            intervalo_minimo_minutos=serializer.validated_data.get('intervalo_minimo_minutos', 30),
            ativo=serializer.validated_data.get('ativo', True),
        )

        return Response({'config_uuid': str(cfg.uuid)}, status=status.HTTP_201_CREATED)


class AdminComandoManualCreateAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, dispositivo_uuid):
        disp = Dispositivo.objects.filter(uuid=dispositivo_uuid).first()
        if not disp:
            return Response({'detail': 'Dispositivo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminComandoManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cmd = ComandoIrrigacao.objects.create(
            dispositivo=disp,
            segundos_irrigacao=serializer.validated_data['segundos_irrigacao'],
            origem=ComandoIrrigacao.Origem.MANUAL,
            status=ComandoIrrigacao.Status.PENDENTE,
            observacao=serializer.validated_data.get('observacao'),
        )

        return Response({'comando_uuid': str(cmd.uuid)}, status=status.HTTP_201_CREATED)
