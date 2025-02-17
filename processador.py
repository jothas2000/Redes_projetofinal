import pandas as pd

#solicita o nome do arquivo CSV ao usuário
print("Digite o nome do arquivo CSV gerado pelo Wireshark:")
arquivo = input()

#carregar o CSV gerado pelo Wireshark
df = pd.read_csv(arquivo)

#selecionar as colunas relevantes
df = df[["Time", "Source", "Destination", "Protocol", "Length"]]

#filtrar apenas os protocolos TCP e ICMP
df = df[df["Protocol"].isin(["TCP", "ICMP"])]

#ordenar por tempo para manter a sequência cronológica
df = df.sort_values(by=["Time"])

#criar um identificador único para cada fluxo
df["Flow"] = df["Source"] + " → " + df["Destination"] + " (" + df["Protocol"] + ")"

#agrupar os dados por fluxo e calcular estatísticas
aggregated = df.groupby("Flow").agg(
    duration=("Time", lambda x: round(x.max() - x.min(), 2)),  #duração do fluxo
    total_packet_size=("Length", "sum"),  #soma do tamanho de todos os pacotes
    avg_packet_size=("Length", lambda x: round(x.mean(), 2)),  #tamanho médio dos pacotes
    min_packet_size=("Length", "min"),  #tamanho mínimo do pacote
    max_packet_size=("Length", "max"),  #tamanho máximo do pacote
    avg_time_interval=("Time", lambda x: round(x.diff().mean(), 6)),  #média dos intervalos
    min_time_interval=("Time", lambda x: round(x.diff().min(), 6)),  #menor intervalo
    max_time_interval=("Time", lambda x: round(x.diff().max(), 6)),  #maior intervalo
)

#calcula a media de bits por segundo fazendo a conversão de bytes para bits antes e arrendondando duas casa decimais
aggregated["avg_packet_rate"] = (aggregated["total_packet_size"] * 8) / aggregated["duration"]
aggregated["avg_packet_rate"] = aggregated["avg_packet_rate"].round(2)  # Arredondar para 2 casas decimais

#ajusta a ordem das colunas
aggregated = aggregated.reset_index()
column_order = ["Flow", "duration", "total_packet_size", "avg_packet_size",
                "min_packet_size", "max_packet_size", "avg_time_interval",
                "min_time_interval", "max_time_interval", "avg_packet_rate"]
aggregated = aggregated[column_order]

#renomeia colunas para português
aggregated.columns = [
    "Fluxo", "Duração (s)", "Tamanho Total (B)", "Tamanho Médio (B)", 
    "Tamanho Mínimo (B)", "Tamanho Máximo (B)", "Média Intervalo (s)",
    "Min Intervalo (s)", "Max Intervalo (s)", "Taxa Média (bps)"
]

#salva o arquivo do fluxo processado separando as colunas por ;
aggregated.to_csv("fluxo_processado.csv", index=False, sep=";", encoding="utf-8")

#Exibe as 10 primeiras linhas no terminal
print("Processamento concluído! Arquivo salvo como 'fluxo_processado.csv'.\n")
print(aggregated.head(10))
