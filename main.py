from base64 import b64decode, b64encode


a = b64encode(bytes('BAACAgIAAxkBAAIM_GWuD8eEVlqncXRywStBkJCQKb00AALoOgACJdBxSel3nRHKsflgNAQ', 'utf-8'))
print(str(b64decode(a)).split('\'')[1])