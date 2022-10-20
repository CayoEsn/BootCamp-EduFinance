import profile
from criar_pdf import PDF
import pandas as pd
import numpy as np
from pandas._config import display
from pandas_datareader import data as pdr
from datetime import datetime
from datetime import timedelta
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import mplcyberpunk
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import requests
from bcb import currency
from bcb import sgs
from matplotlib.dates import date2num
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.options import Options
import warnings
from fpdf import FPDF


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

warnings.filterwarnings('ignore')

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

# print(volatilidade_12m_ibov)
# print(volatilidade_12m_sp)

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


def pegando_dados_di(url):
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
    driver.get("https://dev.to")
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

    indice_di = indice['VENCTO']

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


class PDF(FPDF):

    def header(self):
        self.image('./imgs/logo.png', 10, 8, 40)
        self.set_font('Arial', 'B', 20)
        self.ln(15)
        self.set_draw_color(35, 155, 132)  # cor RGB
        self.cell(15, ln=False)
        self.cell(150, 15, f"Relatório de mercado {data_final}",
                  border=True, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)  # espaço ate o final da folha
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"{self.page_no()}/{{nb}}", align="C")


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

print(selic)

fig, ax = plt.subplots()
plt.style.use("cyberpunk")
ax.plot(selic.index, selic['selic'])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.grid(False)
plt.savefig('./graphics/selic.png', dpi=300)
# plt.show()

inflacao = sgs.get({'ipca': 433,
                    'igp-m': 189}, start=um_ano_atras + timedelta(180))

print(inflacao)

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
print(dolar)

dolar_mensal = dolar.resample("M").last()
dolar_anual = dolar.resample("Y").last()

dolar_diario = dolar.pct_change().dropna()
fechamento_de_dia_dolar = dolar_diario.iloc[-1, :]

print(fechamento_de_dia_dolar)

retorno_mes_a_mes_dolar = dolar_mensal.pct_change().dropna()
retorno_mes_a_mes_dolar = retorno_mes_a_mes_dolar.iloc[1:, :]

print(retorno_mes_a_mes_dolar)

retorno_no_ano_dolar = dolar_anual.pct_change().dropna()

print(retorno_no_ano_dolar)

volatilidade_12m_dolar = dolar_diario['USD'].std() * np.sqrt(252)

print(volatilidade_12m_dolar)

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

# meses

# Definindo config básicas do PDF

pdf = PDF("P", "mm", "Letter")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_fill_color(255, 255, 255)
pdf.set_draw_color(35, 155, 132)

# pdf.output('aula2.pdf')

pdf.image('./imgs/nave1.png', x=115, y=70, w=75, h=33)
pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 10, "1 - Ações e câmbio", ln=True, border=False, fill=False)
pdf.ln(2)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "1.1 Fechamento do mercado", ln=True, border=False, fill=True)

pdf.ln(7)

pdf.set_font('Arial', '', 13)
pdf.cell(25, 15, " Ibovespa", ln=False, border=True, fill=True)
pdf.cell(20, 15, f" {str(round(fechamento_de_dia[0] * 100, 2))}%", ln=True,
         border=True, fill=False)

# fechamento s&p500
pdf.cell(25, 15, " S&P500", ln=False, border=True, fill=True)
pdf.cell(
    20, 15, f" {str(round(fechamento_de_dia[1] * 100, 2))}%", ln=True, border=True, fill=False)

# fechamento Dólar
pdf.cell(25, 15, " Dólar", ln=False, border=True, fill=True)
pdf.cell(
    20, 15, f" {str(round(fechamento_de_dia_dolar[0] * 100, 2))}%", ln=True, border=True, fill=False)

pdf.ln(7)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.2 Gráficos Ibovespa, S&P500 e Dólar",
         ln=True, border=False, fill=False)

pdf.cell(95, 15, "Ibovespa", ln=False, border=False, fill=False, align="C")
pdf.cell(100, 15, "S&P500", ln=True, border=False, fill=False, align="C")
pdf.image("./graphics/ibov.png", w=80, h=70, x=20, y=160)
pdf.image("./graphics/sp.png", w=80, h=70, x=115, y=160)

pdf.ln(130)

pdf.cell(0, 15, "Dólar", ln=True, border=False, fill=False, align="C")
pdf.image("./graphics/dolar.png", w=100, h=75, x=58)

pdf.ln(2)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.3 Rentabilidade mês a mês",
         ln=True, border=False, fill=False)

# escrevendo os meses
pdf.cell(17, 10, "", ln=False, border=False, fill=True, align="C")

for mes in meses:
    pdf.cell(16, 10, mes, ln=False, border=True, fill=True, align="C")

pdf.ln(10)

pdf.cell(17, 10, "Ibov", ln=False, border=True, fill=True, align="C")

pdf.set_font('Arial', '', 12)
for rent in retorno_mes_a_mes['Ibov']:
    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%",
             ln=False, border=True, align="C")

pdf.ln(10)

# escrevendo o S&P

pdf.cell(17, 10, "S&P500", ln=False, border=True, fill=True, align="C")

pdf.set_font('Arial', '', 12)
for rent in retorno_mes_a_mes['S&P500']:
    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%",
             ln=False, border=True, align="C")

pdf.ln(10)

# escrevendo o Dólar

pdf.cell(17, 10, "Dólar", ln=False, border=True, fill=True, align="C")

pdf.set_font('Arial', '', 12)
for rent in retorno_mes_a_mes_dolar['USD']:
    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%",
             ln=False, border=True, align="C")

pdf.ln(10)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.4 Rentabilidade no ano",
         ln=True, border=False, fill=False)

# rent anual ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 10, "Ibovespa", ln=False, border=True, fill=True, align="C")
pdf.cell(
    20, 10, f" {str(round(retorno_no_ano.iloc[0, 0] * 100, 2))}%", ln=True, border=True, align="C")

# rent anual S&P
pdf.cell(25, 10, "S&P500", ln=False, border=True, fill=True, align="C")
pdf.cell(
    20, 10, f" {str(round(retorno_no_ano.iloc[0, 1] * 100, 2))}%", ln=True, border=True, align="C")

# rent anual Dólar
pdf.cell(25, 10, "Dólar", ln=False, border=True, fill=True, align="C")
pdf.cell(
    20, 10, f" {str(round(retorno_no_ano_dolar.iloc[0, 0] * 100, 2))}%", ln=True, border=True, align="C")

pdf.ln(20)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.5 Volatilidade 12M", ln=True, border=False, fill=False)

# vol ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 10, "Ibovespa", ln=False, border=True, fill=True, align="C")
pdf.cell(20, 10, f" {str(round(volatilidade_12m_ibov * 100, 2))}%",
         ln=True, border=True, align="C")

# vol s&p500
pdf.cell(25, 10, "S&P500", ln=False, border=True, fill=True, align="C")
pdf.cell(20, 10, f" {str(round(volatilidade_12m_sp * 100, 2))}%",
         ln=True, border=True, align="C")

# vol dolar
pdf.cell(25, 10, "Dólar", ln=False, border=True, fill=True, align="C")
pdf.cell(20, 10, f" {str(round(volatilidade_12m_dolar * 100, 2))}%",
         ln=True, border=True, align="C")

pdf.image('./imgs/nave2.png', x=115, y=45, w=70, h=70, type='', link='')

pdf.ln(7)

pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 15, "2 - Dados econômicos", ln=True, border=False, fill=False)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "2.1 Curva de juros", ln=True, border=False, fill=False)
pdf.image("./graphics/juros.png", w=125, h=100, x=40, y=140)

pdf.ln(135)

pdf.cell(0, 15, "2.2 Inflacão", ln=True, border=False, fill=False)
pdf.image("./graphics/inflacao.png", w=110, h=90, x=40)

pdf.cell(0, 15, "2.3 Selic", ln=True, border=False, fill=False)
pdf.image("./graphics/selic.png", w=110, h=90, x=40)

pdf.output('aula2.pdf')
