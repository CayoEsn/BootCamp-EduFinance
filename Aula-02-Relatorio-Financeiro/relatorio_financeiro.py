from criar_pdf import PDF
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from bcb import currency
from bcb import sgs
from matplotlib.dates import date2num
import warnings
from fpdf import FPDF
from selenium import webdriver
from criar_pdf import montar_pdf
import mplcyberpunk

warnings.filterwarnings('ignore')


def pegando_dados_di(url):
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
    sem_conexao = True

    while sem_conexao:
        try:
            driver.get(url)
            sem_conexao = False
        except:
            pass

    local_tabela = '''
    //div[@id = "containerPop"]//div[@id = "pageContent"]//form//table//tbody//tr[3]//td[3]//table
    '''

    local_indice = '''
    //div[@id = "containerPop"]//div[@id = "pageContent"]//form//table//tbody//tr[3]//td[1]//table
    '''

    elemento = driver.find_element("xpath", local_tabela)
    elemento_indice = driver.find_element("xpath", local_indice)
    html_tabela = elemento.get_attribute('outerHTML')
    html_indice = elemento_indice.get_attribute('outerHTML')

    driver.quit()

    tabela = pd.read_html(html_tabela)[0]
    indice = pd.read_html(html_indice)[0]

    return tabela, indice


def tratando_dados_di(df_dados, indice):
    df_dados.columns = df_dados.loc[0]
    df_dados = df_dados['ÚLT. PREÇO']
    df_dados = df_dados.drop(0, axis=0)
    indice.columns = indice.loc[0]

    indice = indice.drop(0, axis=0)
    df_dados.index = indice['VENCTO']
    df_dados = df_dados.astype(int)
    df_dados = df_dados[df_dados != 0]
    df_dados = df_dados / 1000

    return df_dados


def transformando_codigo_em_data(df):
    lista_datas = []

    for indice in df.index:
        letra = indice[0]
        ano = indice[1:3]
        mes = legenda[letra]
        data = f"{mes}-{ano}"
        data = datetime.strptime(data, "%b-%y")
        lista_datas.append(data)

    df.index = lista_datas

    return df


# pegando dados do yahoo finance.
indices = ['^BVSP', '^GSPC']

hoje = datetime.now()
um_ano_atras = hoje - timedelta(days=366)

dados_mercado = pdr.get_data_yahoo(indices, start=um_ano_atras, end=hoje)

dados_fechamento = dados_mercado['Adj Close']
dados_fechamento.columns = ["Ibov", "S&P500"]
dados_fechamento = dados_fechamento.dropna()

dados_anuais = dados_fechamento.resample("Y").last()
dados_mensais = dados_fechamento.resample("M").last()

retorno_diario = dados_fechamento.pct_change().dropna()
retorno_mes_a_mes = dados_mensais.pct_change().dropna()
retorno_mes_a_mes = retorno_mes_a_mes.iloc[1:, :]
retorno_no_ano = dados_anuais.pct_change().dropna()

fechamento_de_dia = retorno_diario.iloc[-1, :]
volatilidade_12m_ibov = retorno_diario['Ibov'].std() * np.sqrt(252)
volatilidade_12m_sp = retorno_diario['S&P500'].std() * np.sqrt(252)

fig, ax = plt.subplots()

plt.style.use("cyberpunk")

ax.plot(dados_fechamento.index, dados_fechamento['Ibov'])
ax.grid(False)
plt.savefig('./graphics/ibov.png', dpi=300)
# plt.show()

fig, ax = plt.subplots()
plt.style.use("cyberpunk")
ax.plot(dados_fechamento.index, dados_fechamento['S&P500'])
ax.grid(False)
plt.savefig('./graphics/sp.png', dpi=300)
# plt.show()

data_inicial = dados_fechamento.index[0]

if datetime.now().hour < 10:
    data_final = dados_fechamento.index[-1]
else:
    data_final = dados_fechamento.index[-2]

data_inicial = data_inicial.strftime("%d/%m/%Y")
data_final = data_final.strftime("%d/%m/%Y")

url_mais_att = f'''http://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/SistemaPregao1.asp?
pagetype=pop&caminho=Resumo%20Estat%EDstico%20-%20Sistema%20Preg%E3o&Data={data_final}
&Mercadoria=DI1'''

url_mais_antiga = f'''http://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/SistemaPregao1.asp?
pagetype=pop&caminho=Resumo%20Estat%EDstico%20-%20Sistema%20Preg%E3o&Data={data_inicial}
&Mercadoria=DI1'''

di_mais_recente, indice_di_mais_recente = pegando_dados_di(url=url_mais_att)
di_mais_antigo, indice_di_mais_antigo = pegando_dados_di(url=url_mais_antiga)

dados_di_recente_tratado = tratando_dados_di(
    di_mais_recente, indice_di_mais_recente)
dados_di_antigo_tratado = tratando_dados_di(
    di_mais_antigo, indice_di_mais_antigo)

legenda = pd.Series(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    index=['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z'])

dados_di_recente_tratado = transformando_codigo_em_data(
    dados_di_recente_tratado)
dados_di_antigo_tratado = transformando_codigo_em_data(dados_di_antigo_tratado)

fig, ax = plt.subplots()
plt.style.use("cyberpunk")
ax.set_ylim(3.5, 15)
ax.plot(dados_di_recente_tratado.index, dados_di_recente_tratado.values,
        label=f"Curva {data_final}", marker='o')
ax.plot(dados_di_antigo_tratado.index, dados_di_antigo_tratado.values,
        label=f"Curva {data_inicial}", marker='o')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.legend()
ax.grid(False)
plt.savefig('./graphics/juros.png', dpi=300)
# plt.show()

selic = sgs.get({'selic': 432}, start='2010-01-01')

fig, ax = plt.subplots()
plt.style.use("cyberpunk")
ax.plot(selic.index, selic['selic'])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.grid(False)
plt.savefig('./graphics/selic.png', dpi=300)
# plt.show()

inflacao = sgs.get({'ipca': 433,
                    'igp-m': 189}, start=um_ano_atras + timedelta(180))

datas_numericas = date2num(inflacao.index)

fig, ax = plt.subplots()
ax.bar(datas_numericas - 7, inflacao['ipca'], label="IPCA", width=7)
ax.bar(datas_numericas, inflacao['igp-m'], label="IGP-M", width=7)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.xaxis_date()
formato_data = mdates.DateFormatter('%b-%y')
ax.xaxis.set_major_formatter(formato_data)
ax.grid(False)
plt.axhline(y=0, color='w')
plt.legend()
plt.savefig('./graphics/inflacao.png', dpi=300)
# plt.show()

dolar = currency.get('USD', start=um_ano_atras, end=datetime.now())

dolar_mensal = dolar.resample("M").last()
dolar_anual = dolar.resample("Y").last()

dolar_diario = dolar.pct_change().dropna()
fechamento_de_dia_dolar = dolar_diario.iloc[-1, :]

retorno_mes_a_mes_dolar = dolar_mensal.pct_change().dropna()
retorno_mes_a_mes_dolar = retorno_mes_a_mes_dolar.iloc[1:, :]

retorno_no_ano_dolar = dolar_anual.pct_change().dropna()

volatilidade_12m_dolar = dolar_diario['USD'].std() * np.sqrt(252)

fig, ax = plt.subplots()
plt.style.use("cyberpunk")
ax.plot(dolar.index, dolar['USD'])
ax.yaxis.set_major_formatter('R${x:1.2f}')
ax.grid(False)
plt.savefig('./graphics/dolar.png', dpi=300)
# plt.show()

meses = []
for indice in retorno_mes_a_mes.index:
    mes = indice.strftime("%b")
    meses.append(mes)

# Definindo config básicas do PDF

montar_pdf('aula2.pdf', data_final, fechamento_de_dia, fechamento_de_dia_dolar, meses, retorno_mes_a_mes,
           retorno_mes_a_mes_dolar,
           retorno_no_ano, retorno_no_ano_dolar, volatilidade_12m_ibov, volatilidade_12m_sp, volatilidade_12m_dolar)
