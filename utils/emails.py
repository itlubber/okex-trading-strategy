import json
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
import config
from datetime import datetime


def send_email(title, message, _subtype="plain"):
    """
    title: 邮件标题
    info: 邮件内容信息
    """
    smtp = SMTP_SSL(config.email_options.get("host"), config.email_options.get("port"))
    # smtp.set_debuglevel(0)
    smtp.login(config.email_options.get("account"), config.email_options.get("passphrase"))

    if _subtype == "html":
        msg = MIMEText(message, "html", 'utf-8')
    else:
        msg = MIMEText(message, "plain", 'utf-8')
    msg["Subject"] = Header("策略服务通知")
    msg["From"] = Header("策略服务<okex@quant.com>", 'utf-8')
    msg["To"] = Header(f"<{'>,<'.join(config.email_options.get('receivers'))}>", 'utf-8')
    smtp.sendmail(config.email_options.get("email"),  config.email_options.get("receivers"), msg.as_string())
    smtp.quit()


def write_response_html(request_object, response_object):
    msg = """
            <html>
                <head>
                </head>
                <body>
                    <h2>响应时间</h2>
                    <p style="padding: 5px;margin: 5px;background: #282c34;color: #c678dd;">{}</p>
                    <h1>服务端响应信息</h1>
                    <pre style="padding: 5px;margin: 5px;background: #282c34;color: #c678dd;">{}</pre>
                    <h1>应用端请求信息</h1>
                    <pre style="padding: 5px;margin: 5px;background: #282c34;color: #c678dd;">{}</pre>
                </body>
            </html>
          """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(response_object, indent=4), json.dumps(request_object, indent=4))
    send_email(f"策略服务请求响应通知", msg, _subtype="html")