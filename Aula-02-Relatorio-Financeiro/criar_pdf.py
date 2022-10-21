from fpdf import FPDF


class PDF(FPDF):

    def header(self):

        self.image('img/logo.png', 10, 8, 40)
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
