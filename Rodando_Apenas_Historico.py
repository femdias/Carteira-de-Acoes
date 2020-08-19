''' importando bibliotecas '''

import numpy as np
import pandas as pd
import datascience as ds
import datetime
from datetime import datetime
from pandas_datareader import data as web
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm
import time

''' importando o csv com as 'notas de corretagem' para uma tabela pandas '''

Notas_de_Corretagem0 = pd.read_csv(
    r'C:\Users\femdi\OneDrive\Documentos\python\Controle de Investimentos em Ações na Bolsa de Valores - Notas de Corretagem.csv',
    error_bad_lines=False)
# pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


''' selecionando apenas as colunas desejadas '''

Notas_de_Corretagem1 = Notas_de_Corretagem0[['Corretora',
                                             'Data',
                                             'Horário',
                                             'Operação',
                                             'Modalidade',
                                             'Papel',
                                             'Tipo Papel',
                                             'Quantidade',
                                             'Preço',
                                             'Custo Corretagem']]

# Formatando a Base

'''Trocando , por . nos números e os transformando em float'''

# preço
preço_novo = []
for i in np.arange(len(Notas_de_Corretagem1)):
    x = float(Notas_de_Corretagem0.iloc[i][9].replace(',', '.'))
    preço_novo = np.append(preço_novo, x)
# print(preço_novo)

# corretagem
corret_novo = []
for i in np.arange(len(Notas_de_Corretagem1)):
    x = float(Notas_de_Corretagem0.iloc[i][10].replace(',', '.'))
    corret_novo = np.append(corret_novo, x)
# print(corret_novo)

''' Arrumando a formatação da data  '''

# Data
data = []
for i in np.arange(len(Notas_de_Corretagem1)):
    x = datetime.strptime(Notas_de_Corretagem0.iloc[i][2], '%d/%m/%Y').date()
    data = np.append(data, x)
# print(data)


''' Tirando as colunas erradas e colocando as certas'''

Notas_de_Corretagem2 = Notas_de_Corretagem1.drop(columns={'Preço', 'Custo Corretagem', 'Data'})

Notas_de_Corretagem3 = Notas_de_Corretagem2.assign(Preço=preço_novo) \
    .assign(Custo_Corretagem=corret_novo) \
    .assign(Data=data)

''' Selecionando as colunas desejadas'''

Notas_de_Corretagem4 = Notas_de_Corretagem3[['Corretora',
                                             'Data',
                                             'Operação',
                                             'Modalidade',
                                             'Papel',
                                             'Tipo Papel',
                                             'Quantidade',
                                             'Preço',
                                             'Custo_Corretagem']]

'''Renomeando'''

Notas_de_Corretagem_meio = Notas_de_Corretagem4.rename(columns={"Custo_Corretagem": "Custo Corretagem"})


'''Trazendo a série do IBOVESPA a partir do primeira operação da base'''
'''A série traz todas as datas que a Bolsa esteve aberta'''

Serie_IBOV = pd.DataFrame()
tickers = ['^BVSP'] #ticker da IBOVESPA no Yahoo Finance
data = min(Notas_de_Corretagem_meio['Data'])
for i in tickers:
    Serie_IBOV[i] = round(web.get_data_yahoo(i, data)['Adj Close'], 2)   # adj close traz as cotações ajustadas por slip e dividendos
Serie_IBOV = Serie_IBOV.rename(columns ={'^BVSP': 'IBOV'})
pd.set_option('display.max_rows', None)
#print(Serie_IBOV)

'''Pegando coluna de datas'''

Serie_IBOV1=Serie_IBOV.reset_index(level=0)
Lista_Datas0=Serie_IBOV1['Date']

'''Formatando coluna de datas'''

Lista_Datas=[]
for i in np.arange(len(Lista_Datas0)):
    x=datetime.strptime(str(Lista_Datas0[i]), '%Y-%m-%d %H:%M:%S').date()
    Lista_Datas=np.append(Lista_Datas, x)
#print(Lista_Datas)


""" Calculando a rentabilidade de todos os dias da série, para compará-la com a série do IBOVESPA """

Lista_de_Rentabilidade = []

'''loop para todas as datas em que a Bolsa estava aberta'''
for v in tqdm(Lista_Datas):
    # selecionamos só as compras/vendas anteriores a tal data 'v'
    Notas_de_Corretagem5 = Notas_de_Corretagem_meio[(Notas_de_Corretagem_meio['Data'] <= v)]

    '''Criando variáveis importantes para a análise'''

    # valor bruto
    valor_bruto = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        x = (Notas_de_Corretagem5.loc[i]['Quantidade'] * Notas_de_Corretagem5.loc[i]['Preço'])
        valor_bruto = np.append(valor_bruto, x)
    # print(valor_bruto)

    # Taxa de Liquidação
    tx_liq = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        if Notas_de_Corretagem5.loc[i]['Modalidade'] == 'Swing':
            x = (valor_bruto[i]) * 0.000275
        elif Notas_de_Corretagem5.loc[i]['Modalidade'] == 'Day Trade':
            x = (valor_bruto[i]) * 0.0002
        tx_liq = np.append(tx_liq, x)
    # print(tx_liq)

    # Emolumentos
    emo = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        if Notas_de_Corretagem5.loc[i]['Modalidade'] == 'Swing':
            x = (valor_bruto[i]) * 0.00004115
        elif Notas_de_Corretagem5.loc[i]['Modalidade'] == 'Day Trade':
            x = (valor_bruto[i]) * 0.00004983
        emo = np.append(emo, x)
    # print(emo)

    # ISS
    iss = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        x = (Notas_de_Corretagem5.loc[i]['Custo Corretagem'] * 0.0965)
        iss = np.append(iss, x)
    # print(iss)

    # Custo Total
    ct = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        x = Notas_de_Corretagem5.loc[i]['Custo Corretagem'] + tx_liq[i] + emo[i] + iss[i]
        ct = np.append(ct, x)
    # print(ct)

    # Valor Líquido
    vl = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        if Notas_de_Corretagem5.loc[i]['Operação'] == 'Compra':
            x = valor_bruto[i] + ct[i]
        if Notas_de_Corretagem5.loc[i]['Operação'] == 'Venda':
            x = (valor_bruto[i] * (-1) + ct[i])
        vl = np.append(vl, x)
    # print(vl)

    # Preço Médio da Ordem
    pmo = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        x = vl[i] / Notas_de_Corretagem5.loc[i]['Quantidade']
        pmo = np.append(pmo, x)
    # print(pmo)

    # Saldo Posição
    sp = []
    for i in np.arange(len(Notas_de_Corretagem5)):
        if Notas_de_Corretagem5.loc[i]['Operação'] == 'Compra':
            x = Notas_de_Corretagem5.loc[i]['Quantidade']
        if Notas_de_Corretagem5.loc[i]['Operação'] == 'Venda':
            x = Notas_de_Corretagem5.loc[i]['Quantidade'] * (-1)
        sp = np.append(sp, x)
    # print(sp)


    '''Juntando novas variáveis com tabela de ações'''

    Notas_de_Corretagem6 = Notas_de_Corretagem5.assign(valor_bruto=valor_bruto) \
        .assign(Tx_Liquidação=tx_liq) \
        .assign(Emolumentos=emo) \
        .assign(ISS=iss) \
        .assign(Custo_Total=ct) \
        .assign(Valor_Líquido=vl) \
        .assign(PMdaOrdem=pmo) \
        .assign(Saldo_Posicao=sp)

    '''Criando mais variáveis '''

    # Estoque
    estoque = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        x = sum(Notas_de_Corretagem6.loc[j]['Saldo_Posicao'] for j in np.arange(0, i + 1) if
                Notas_de_Corretagem6.loc[j]['Papel'] == Notas_de_Corretagem6.loc[i]['Papel'])
        estoque = np.append(estoque, x)
    # print(estoque)

    # Ativo
    ativo0 = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        x = 0
        for j in np.arange(i, len(Notas_de_Corretagem6)):
            if estoque[j] == 0 and Notas_de_Corretagem6.loc[j]['Papel'] == Notas_de_Corretagem6.loc[i]['Papel']:
                x = x + 1
        ativo0 = np.append(ativo0, x)
    # print(ativo0)

    ativo = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        if ativo0[i] == 0:
            x = "Ativo"
        elif ativo0[i] != 0:
            x = "Inativo"
        ativo = np.append(ativo, x)
    # print(ativo)

    # Cesta
    cesta = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        x = Notas_de_Corretagem6.loc[i]['Papel'] + '_000' + str(int(ativo0[i]))
        cesta = np.append(cesta, x)
    # print(cesta)

    # Preço Médio da Cesta
    pmc = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        x = sum(Notas_de_Corretagem6.loc[j]['Valor_Líquido'] for j in np.arange(0, i + 1) if
                cesta[j] == cesta[i] and Notas_de_Corretagem6.loc[j]['Operação'] == 'Compra')
        y = sum(Notas_de_Corretagem6.loc[j]['Saldo_Posicao'] for j in np.arange(0, i + 1) if
                cesta[j] == cesta[i] and Notas_de_Corretagem6.loc[j]['Operação'] == 'Compra')
        z = x / y
        pmc = np.append(pmc, z)
    # print(pmc)

    # Lucro/Prejuizo
    lucro = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        if Notas_de_Corretagem6.loc[i]['Operação'] == 'Compra':
            x = 0
        elif Notas_de_Corretagem6.loc[i]['Operação'] == 'Venda':
            x = (-1) * (Notas_de_Corretagem6.loc[i]['Quantidade'] * (pmc[i] + Notas_de_Corretagem6.loc[i]['PMdaOrdem']))
        lucro = np.append(lucro, x)
    # print(lucro)

    # IR na Fonte
    ir = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        if Notas_de_Corretagem6.loc[i]['Operação'] == 'Venda' and Notas_de_Corretagem6.loc[i][
            'Modalidade'] == 'Swing' and lucro[i] > 0:
            x = lucro[i] * 0.000050
        elif Notas_de_Corretagem6.loc[i]['Operação'] == 'Venda' and Notas_de_Corretagem6.loc[i][
            'Modalidade'] == 'Day Trade' and lucro[i] > 0:
            x = lucro[i] * 0.01
        else:
            x = 0
        ir = np.append(ir, x)
    # print(ir)

    # IR FII
    irfii = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        if Notas_de_Corretagem6.loc[i]['Operação'] == 'Venda' and Notas_de_Corretagem6.loc[i]['Tipo Papel'] == 'FII' and \
                lucro[i] > 0:
            x = lucro[i] * 0.2
        else:
            x = 0
        irfii = np.append(irfii, x)
    # print(irfii)

    # IR ETF
    iretf = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        if Notas_de_Corretagem6.loc[i]['Operação'] == 'Venda' and Notas_de_Corretagem6.loc[i]['Tipo Papel'] == 'ETF' and \
                lucro[i] > 0:
            x = lucro[i] * 0.2
        else:
            x = 0
        iretf = np.append(iretf, x)
    # print(iretf)

    # IR Day Trade
    irdt = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        if Notas_de_Corretagem6.loc[i]['Operação'] == 'Venda' and Notas_de_Corretagem6.loc[i][
            'Tipo Papel'] == 'Day Trade' and lucro[i] > 0:
            x = lucro[i] * 0.20
        else:
            x = 0
        irdt = np.append(irdt, x)
    # print(irdt)

    # Mês de Referencia
    mês = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        x = str(Notas_de_Corretagem6.loc[i]['Data'].month) + '_' + str(Notas_de_Corretagem6.loc[i]['Data'].year)
        mês = np.append(mês, x)
    # print(mês)

    # Vendas no mês
    vendas = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        x = sum(Notas_de_Corretagem6.loc[j]['valor_bruto'] for j in np.arange(len(Notas_de_Corretagem6)) \
                if mês[j] == mês[i] and Notas_de_Corretagem6.loc[j]['Operação'] == 'Venda' \
                and Notas_de_Corretagem6.loc[j]['Tipo Papel'] == 'Ação')
        vendas = np.append(vendas, x)
    # print(vendas)

    # IR Normal
    irnormal = []
    for i in np.arange(len(Notas_de_Corretagem6)):
        if Notas_de_Corretagem6.loc[i]['Operação'] == 'Venda' and Notas_de_Corretagem6.loc[i][
            'Tipo Papel'] == 'Ação' and lucro[i] > 0 and vendas[i] > 20000:
            x = lucro[i] * 0.15
        else:
            x = 0
        irnormal = np.append(irnormal, x)
    # print(irnormal)

    '''Juntando novas variáveis com tabela de ações'''

    Notas_de_Corretagem7 = Notas_de_Corretagem6.assign(Estoque=estoque) \
        .assign(ir_nafonte=ir) \
        .assign(Ativo=ativo) \
        .assign(Cesta=cesta) \
        .assign(PMdaCesta=pmc) \
        .assign(lucro_prejuizo=lucro) \
        .assign(IR_FII=irfii) \
        .assign(IR_ETF=iretf) \
        .assign(IR_Normal=irnormal) \
        .assign(IR_Day_Trade=irdt) \
        .assign(mes=mês) \
        .assign(vendas_no_mes=vendas)



    '''Renomeando colunas, chegando na base final das Notas de Corretagem'''

    Notas_de_Corretagem = Notas_de_Corretagem7.rename(columns={"valor_bruto": "Valor Bruto",
                                                               "Tx_Liquidação": "Tx Liquidação",
                                                               "ir_nafonte": "IR na Fonte",
                                                               "Custo_Total": "Custo Total",
                                                               "Valor_Líquido": "Valor Líquido",
                                                               "PMdaOrdem": "Preço Médio Ordem",
                                                               "PMdaCesta": "Preço Médio Cesta",
                                                               "lucro_prejuizo": "Lucro Prejuízo",
                                                               "IR_FII": "IR FII",
                                                               "IR_ETF": "IR ETF",
                                                               "IR_Normal": "IR Normal",
                                                               "IR_Day_Trade": "IR Day Trade",
                                                               "mes": "Mês Referência",
                                                               "vendas_no_mes": "Vendas no Mês (Tipo Ação)",
                                                               "Saldo_Posicao": "Saldo Posição"
                                                               })





    '''Selecionando colunas para fazer uma base de Carteira'''

    Carteira0 = Notas_de_Corretagem[['Tipo Papel',
                                     'Papel',
                                     'Corretora',
                                     'Quantidade',
                                     'Preço',
                                     'Operação',
                                     'Data',
                                     'Preço Médio Cesta',
                                     'Mês Referência',
                                     'Preço Médio Ordem',
                                     'Cesta',
                                     'Ativo',
                                     'Saldo Posição',
                                     'Valor Líquido']]



    '''Agrupando em tipos de Papel, por soma da quantidade, vl liquido, max data ('última compra')e min data (1a compra)'''

    Carteira1 = Carteira0[(Carteira0['Ativo'] == 'Ativo') & (Carteira0['Corretora'] != '')] \
        [['Papel', 'Saldo Posição', 'Valor Líquido']].groupby('Papel').sum()

    Carteira2 = Carteira0[['Papel', 'Data']].groupby('Papel').min()

    Carteira3 = Carteira0[['Papel', 'Data']].groupby('Papel').max()

    Carteira4 = Carteira1.merge(Carteira2, how='left', left_on='Papel', right_on='Papel').merge(Carteira3, how='left',
                                                                                                left_on='Papel',
                                                                                                right_on='Papel')
    Carteira5 = Carteira4.rename(
        columns={"Data_x": "1a Compra", "Data_y": "Última Compra", "Saldo Posição": "Quantidade"})

    ''' fazendo a planilha de preços médios '''

    Preço_Medio0 = Notas_de_Corretagem[
        (Notas_de_Corretagem['Ativo'] == 'Ativo') & (Notas_de_Corretagem['Operação'] == 'Compra')]

    Preço_Medio1 = Preço_Medio0[['Papel', 'Preço Médio Cesta']]

    Preço_Medio = Preço_Medio1.drop_duplicates(subset='Papel', keep='last')


    '''Juntando coluna com o preço médio a base da carteira'''

    Carteira6 = Carteira5.merge(Preço_Medio, how='left', left_on='Papel', right_on='Papel').rename(
        columns={"Preço Médio Cesta": "Preço Médio"})





    '''Agora, procuramos as cotações atuais dos Papeis da caretira na base do Yahoo Fianace'''
    '''Lista com os Papeis 'tickers' da carteira'''
    Papeis = Carteira6.loc[:, 'Papel']

    '''Colocando '.SA' no final de toda sigla do papel, pois é assim que estão registrados na base do Yahoo Finance'''
    my_string = ".SA"
    PapeisSA = ["{}{}".format(i, my_string) for i in Papeis]

    '''Procurando os tickers na base do Yahoo'''
    prices0 = pd.DataFrame()
    tickers = PapeisSA
    data = v
    data2 = Lista_Datas[0]

    '''Caso há algum erro na base da Yahoo, o valor que retorna é uma média da cotação desde o primeiro dia da carteira'''
    for i in tickers:
        try:
            prices0[i] = round(web.get_data_yahoo(i, data, data)['Adj Close'], 2)
        except:
            prices0[i] = np.mean(round(web.get_data_yahoo(i, data2, data)['Adj Close'], 2))

    '''Invertendo colunas e linhas '''
    prices = prices0.T

    '''Mudando o index e fazendo uma coluna com as datas'''
    prices1 = prices.reset_index(level=0)
    prices2 = prices1.rename(columns={list(prices1)[1]: 'Preço Atual', "index": "Papel"}).replace({'Papel': r'.SA$'},
                                                                                                  {'Papel': ''},
                                                                                                  regex=True)
    '''Juntando com os preços atuais com a base da carteira'''
    Carteira7 = Carteira6.merge(prices2, how='left', left_on='Papel', right_on='Papel')



    '''Calculando variáveis novas com o Lucro, a Porcentagem de Variação do Preço, o Valor  Atual dos papeis
    e a Participação em % do papel na Carteira'''

    lucro = pd.Series()
    for i in np.arange(len(Carteira7)):
        x = Carteira7.loc[i]['Quantidade'] * Carteira7.loc[i]['Preço Atual'] - Carteira7.loc[i]['Valor Líquido']
        lucro = np.append(lucro, x)

    porcent = pd.Series()
    for i in np.arange(len(Carteira7)):
        x = ("{:.1%}".format((Carteira7.loc[i]['Preço Atual'] / Carteira7.loc[i]['Preço Médio']) - 1))
        porcent = np.append(porcent, x)

    vl_atual = pd.Series()
    for i in np.arange(len(Carteira7)):
        x = Carteira7.loc[i]['Quantidade'] * Carteira7.loc[i]['Preço Atual']
        vl_atual = np.append(vl_atual, x)
    # print(vl_atual)
    vl_atual_total = sum(vl_atual)

    participacao = pd.Series()
    for i in np.arange(len(Carteira7)):
        x = round(((Carteira7.loc[i]['Quantidade'] * Carteira7.loc[i]['Preço Atual']) / vl_atual_total), 2)
        participacao = np.append(participacao, x)


    '''Adicionando essas variáveis como colunas na base de carteira'''
    Carteira8 = Carteira7.assign(VL_Atual=vl_atual, Lucro_Prejuízo=lucro, Porc_Lucro_Prejuízo=porcent,
                                 Particip=participacao) \
        .rename(columns={'Lucro_Prejuízo': 'Lucro/Prejuízo', 'Porc_Lucro_Prejuízo': '%Lucro/Prejuízo', \
                         'Particip': 'Participação na Carteira', 'VL_Atual': 'Valor Líquido Atual'})


    '''Finalmente, calculando o lucro das ações já completas (compra+venda) e somando com a rentabilidade dos papeis
     atuais da carteira, para ter a Rentabilidade Total da Carteira em determinada data 'v' '''

    lucro = sum(Notas_de_Corretagem.loc[j]["Lucro Prejuízo"] for j in np.arange(len(Notas_de_Corretagem)))
    Rentabilidade = (sum(Carteira8["Valor Líquido Atual"]) + lucro) / sum(Carteira8["Valor Líquido"]) - 1

    ''' Juntando as rentabilidades da Carteira em todos os dias 'v' em que a bolsa estava aberta'''
    Lista_de_Rentabilidade = np.append(Lista_de_Rentabilidade, Rentabilidade)
    time.sleep(1)
'''Printando a Série de Rentabilidades'''
print(Lista_de_Rentabilidade)

Rentabilidades=pd.DataFrame()
Rentabilidades1=Rentabilidades.assign(Lista_Datas=Lista_Datas, Lista_de_Rentabilidade=Lista_de_Rentabilidade)
print(Rentabilidades1)

Rentabilidades1.to_csv(r'C:\Users\femdi\OneDrive\Documentos\Python\PyCharm\Carteira_de_Acoes\Rentabilidades.csv', index = False)

