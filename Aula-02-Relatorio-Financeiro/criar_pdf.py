from fpdf import FPDF


class PDF(FPDF):

    def header(self):
        self.image('imgs/logo.png', 10, 8, 40)
        self.set_font('Arial', 'B', 20)
        self.ln(15)
        self.set_draw_color(35, 155, 132)  # cor RGB
        self.cell(15, ln=False)
        self.cell(150, 15, f"Relatório de mercado {data}",
                  border=True, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)  # espaço ate o final da folha
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"{self.page_no()}/{{nb}}", align="C")


def montar_pdf(nome_arquivo_final, data_final, fechamento_de_dia, fechamento_de_dia_dolar, meses, retorno_mes_a_mes,
               retorno_mes_a_mes_dolar, retorno_no_ano, retorno_no_ano_dolar, volatilidade_12m_ibov,
               volatilidade_12m_sp, volatilidade_12m_dolar):
    global data
    data = data_final

    pdf = PDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(35, 155, 132)

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

    pdf.output(nome_arquivo_final)
