import boto3


def obter_tamanho_arquivo(bucket, key):
	cliente_s3 = boto3.client('s3')
	return cliente_s3.head_object(Bucket=bucket, Key=key)['ContentLength']


def obter_cabecalho_csv(bucket, key):
	cliente_s3 = boto3.client('s3')
	resposta = cliente_s3.get_object(Bucket=bucket, Key=key)
	return next(resposta['Body'].iter_lines())


def gerar_range_bytes(tamanho_arquivo, byte_inicial):
	lista_dicionarios = []
	lista_range = list(range(byte_inicial, tamanho_arquivo, 200000000))
	for posicao, byte_numero in enumerate(lista_range):
		try:
			lista_dicionarios.append({
				'inicio': byte_numero + 1,
				'fim': lista_range[posicao + 1]
			})
		except Exception as e:
			lista_dicionarios.append({
				'inicio': byte_numero + 1,
				'fim': tamanho_arquivo
			})


	return lista_dicionarios


def lambda_handler(event, context):
	tamanho_arquivo = obter_tamanho_arquivo(event['bucket'], event['key'])
	cabecalho = obter_cabecalho_csv(event['bucket'], event['key'])

	dados_range = gerar_range_bytes(tamanho_arquivo, len(cabecalho))
	lista_cabecalho = cabecalho.decode().replace('"','').split(';')
	return [
		{'cabecalho': lista_cabecalho, 'bucket': event['bucket'], 'key': event['key'], **dados} 
		for dados in dados_range
	]