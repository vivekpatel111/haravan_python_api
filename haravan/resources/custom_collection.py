from ..base import HaravanResource
from haravan import mixins
import haravan


class CustomCollection(HaravanResource, mixins.Metafields, mixins.Events):

    def products(self):
        return haravan.Product.find(collection_id=self.id)

    def add_product(self, product):
        return haravan.Collect.create({'collection_id': self.id, 'product_id': product.id})

    def remove_product(self, product):
        collect = haravan.Collect.find_first(collection_id=self.id, product_id=product.id)
        if collect:
            collect.destroy()
