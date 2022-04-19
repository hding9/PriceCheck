from requests_html import HTMLSession
from email.message import EmailMessage
import smtplib
import getpass
import logging
import time
import random


class EmailService:
    def __init__(self, server, port, fromAddress, password) -> None:
        self.server = server
        self.port = port
        self.fromAddress = fromAddress
        self.password = password


    def buildMessage(self, toAddress, subject, content) -> EmailMessage:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.fromAddress
        msg['To'] = toAddress
        msg.set_content(content)

        return msg


    def sendMessage(self, toAddress, subject, content) -> None:
        with smtplib.SMTP(self.server, self.port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            try:
                smtp.login(self.fromAddress, self.password)
                logging.info('Login Successful!')
                msg = self.buildMessage(toAddress, subject, content)
                smtp.send_message(msg)
                logging.info('Email sent!')
            except:
                logging.error('Login Failed!')

    
def getProduct(url, platform='Amazon') -> dict:
    s = HTMLSession()
    r = s.get(url)
    r.html.render(sleep=1)

    if platform == 'Amazon':
        product = {
            'title': r.html.xpath('//*[@id="productTitle"]', first=True).text,
            # 'price': r.html.xpath('//*[@id="priceblock_ourprice"]', first=True).text
            'price': r.html.xpath('//*[@class="a-offscreen"]', first=True).text
        }

    elif platform == 'Drop':
        product = {
            'title': r.html.xpath('//meta[@property="og:title"]', first=True).text,
            'price': r.html.find('.Text__type--price__1mumP', first=True).text
        }
    
    else:
        raise NotImplementedError(f"{platform} is not implemented.")

    # logging.debug(f"{product['price']=}")
    print(f"{product['price']=}")

    return product


def getValue(price, currency='$') -> float:
    value = price.replace(currency, '')
    value = float(value)

    return value


def getEmailPassword(fromAddress):
    return getpass.getpass(f'Password for {fromAddress}: ')


def main() -> None:
    # url = 'https://www.amazon.com/Western-Digital-Red-Hard-Drive/dp/B07D3N95GS/ref=sr_1_3?dchild=1&keywords=western+digital+red+pro&qid=1620013917&sr=8-3'
    url = 'https://drop.com/buy/drop-redsuns-gmk-red-samurai-keycap-set?defaultSelectionIds=966786'
    previous_value = 1000.00
    email_server = ''   #'smtp.office365.com'
    user_email = ''     # 'xxx@outlook.com'
    to_email = ''       # 'xxx@gmail.com'
    port = 587
    subject = 'Price Drop!'

    logging.basicConfig(format='%(asctime)-27s %(levelname)s:%(message)s', level=logging.INFO)

    ems = EmailService(email_server, port, user_email, getEmailPassword(user_email))

    while(True):
        logging.info('Requesting product information...')
        product = getProduct(url, platform='Drop')
        logging.info('Retrieved product information.')
        current_value = getValue(product['price'])

        if current_value < previous_value:
            content = f'Current price: {current_value:.2f}. Price DROPPED from {previous_value:.2f}!'
            logging.info(content)
            ems.sendMessage(to_email, subject, content)
        elif current_value > previous_value:
            logging.info(f'Current price: {current_value:.2f}. Price RAISED from {previous_value:.2f}.')
        else:
            logging.info(f'Current price: {current_value:.2f}.')

        previous_value = current_value

        sleep_time = random.randint(7200, 14400)
        logging.info(f'Sleeping fro {int(sleep_time/60)} minutes.')
        time.sleep(sleep_time)


if __name__ == '__main__':
    main()