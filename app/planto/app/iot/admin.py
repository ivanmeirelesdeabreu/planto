from django.contrib import admin
from .models import Dispositivo, LeituraUmidade, ConfiguracaoIrrigacao, ComandoIrrigacao, ExecucaoIrrigacao

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nome','uuid','ativo','data_criacao','ultimo_contato')
    readonly_fields = ('token_hash',)
    search_fields = ('nome','uuid')
    list_filter = ('ativo',)

@admin.register(LeituraUmidade)
class LeituraAdmin(admin.ModelAdmin):
    list_display = ('dispositivo','uuid','data_hora','umidade','bateria','data_recebimento')
    search_fields = ('uuid',)
    list_filter = ('dispositivo',)

@admin.register(ConfiguracaoIrrigacao)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('dispositivo','uuid','umidade_minima','segundos_irrigacao','intervalo_minimo_minutos','ativo','data_criacao')
    list_filter = ('ativo','dispositivo')

@admin.register(ComandoIrrigacao)
class ComandoAdmin(admin.ModelAdmin):
    list_display = ('dispositivo','uuid','status','origem','segundos_irrigacao','data_criacao','data_envio','data_confirmacao')
    list_filter = ('status','origem','dispositivo')
    search_fields = ('uuid',)

@admin.register(ExecucaoIrrigacao)
class ExecucaoAdmin(admin.ModelAdmin):
    list_display = ('dispositivo','uuid','comando','data_inicio','data_fim','segundos_executados','sucesso','data_registro')
    list_filter = ('sucesso','dispositivo')
    search_fields = ('uuid',)
