import win32com.client as win32

outlook = win32.Dispatch('outlook.application')
email = outlook.CreateItem(0)

email.To = "botcamp@edufinance.com.br"
email.Subject = "Relatório diário"
email.Body = '''Segue em anexo o relatório diário.

Abs, Brenno

'''

anexo = r"C:/Users/lsiqu/lancamento_2-main/aula2.pdf"

email.Attachments.Add(anexo)

email.Send()
