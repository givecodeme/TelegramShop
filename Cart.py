import requests
import json
# car = {}


class Cart(object):
    def __init__(self, chat_id):
        self.chat_id = str(chat_id)
        with open('db.json') as file:
            data = json.load(file)
        try:
            data[self.chat_id]
        except:
            data[self.chat_id] = {}
            with open('db.json', 'w') as w:
                json.dump(data, w, ensure_ascii=False)
        self.ids = data[self.chat_id]

    def __getitem__(self, key):
        with open('db.json') as file:
            data = json.load(file)
        return data[self.chat_id][key]

    def __setitem__(self, key, value):
        with open('db.json') as file:
            data = json.load(file)
        data[self.chat_id][key] = value
        with open('db.json', 'w') as w:
            json.dump(data, w, ensure_ascii=False)

    def add(self, id, quantity=1):
        url = 'http://127.0.0.1:8000/api/product/'+id
        product = requests.get(url).json()
        with open('db.json') as file:
            data = json.load(file)

        if id not in self.ids:
            self[id] = {
                'name': product['name'],
                'quantity': 1,
                'price': int(product['price']),
                #  'sale_price': int(product.sale_price),
            }
        else:
            self[id] = {
                'name': product['name'],
                'quantity': self[id]['quantity'] + 1,
                'price': int(product['price']),
                #  'sale_price': int(product.sale_price),
            }

        return self[id]

    def change(self, product, quantity):
        product_id = str(product.id)
        self.cart[product_id]['quantity'] = quantity
        self.cart[product_id]['total_price'] = int(
            self.cart[product_id]['price']) * self.cart[product_id]['quantity']

        self.cart[product_id]['total_sale'] = int(
            self.cart[product_id]['sale_price']) * self.cart[product_id]['quantity']
        self.save()

    # def save(self):
    #     self.session[settings.CART_SESSION_ID] = self.cart
        # self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self[product_id]
            # self.save()

    def __iter__(self):
        with open('db.json') as file:
            data = json.load(file)
            for item in data[self.chat_id].values():
                item['total_price'] = item['price'] * item['quantity']
                # item['total_sale'] = item['sale_price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self)

    def get_total_price(self):
        # with open('db.json', 'wr') as file:
        return "{:,}".format(sum(item['price'] * item['quantity'] for item in self)).replace(',', ' ')

    # def get_total_sale_price(self):
    #     return sum(Decimal(item['sale_price']) * item['quantity'] for item in self.cart.values())

    # def get_sale(self):
    #     return self.get_total_sale_price() - self.get_total_price()

    def clear(self):
        with open('db.json') as file:
            data = json.load(file)
        data[self.chat_id] = {}
        with open('db.json', 'w') as file:
            json.dump(data, file, ensure_ascii=False)
