import boto3
import csv
import uuid
from io import StringIO



def obter_dados_por_range(bucket, key, inicio, fim):
	cliente_s3 = boto3.client('s3')
	resposta = cliente_s3.get_object(Bucket=bucket, Key=key, Range=f'bytes={inicio}-{fim}')
	return resposta['Body'].read()

def processar_dados(dados_arquivo, event):
	lista_de_linhas = dados_arquivo.replace('"','').splitlines()
	primeira_linha = lista_de_linhas[0]
	ultima_linha = lista_de_linhas[-1]

	#Checando se há dados faltando na primeira linha
	if(len(primeira_linha.split(';')) != len(event['cabecalho'])):
		del lista_de_linhas[0]

	#Checando se há dados faltando na ultima linha
	if(len(ultima_linha.split(';')) != len(event['cabecalho'])):
		proximo_byte = event['fim'] + 1
		dados_segunda_chamada = obter_dados_por_range(
			event['bucket'], 
			event['key'], 
			proximo_byte,
			proximo_byte + 4000).decode()
		primeira_linha_segunda_chamada = dados_segunda_chamada.replace('"','').splitlines()[0]

		lista_de_linhas[-1] = f'{ultima_linha}{primeira_linha_segunda_chamada}'

	return lista_de_linhas

def lambda_handler(event, context):
	cliente_s3 = boto3.client('s3')
	dados = obter_dados_por_range(
		event['bucket'], 
		event['key'], 
		event['inicio'], 
		event['fim']
	)

	dados_processados = processar_dados(dados.decode(), event)
	with open('/tmp/temp.csv', 'w', newline='') as file:
		file.write(f"{';'.join(event['cabecalho'])}\n")
		file.write('\n'.join(dados_processados))


	s3 = boto3.resource('s3')
	s3.meta.client.upload_file('/tmp/temp.csv', 'brtips-opendata-covid', f"{event['key']}/{uuid.uuid4().hex}.csv")

	# dados_csv = f"{';'.join(event['cabecalho'])}\n"+'\n'.join(dados_processados)

	# arquivo_in_memory = StringIO(dados_csv)

	# cliente_s3 = boto3.client('s3')

	# cliente_s3.put_object(
	# 	Body=arquivo_in_memory.getvalue(), 
	# 	Bucket='brtips-opendata-covid', 
	# 	Key=f"{event['key']}/{uuid.uuid4().hex}.csv"
	# )
