from ..base import HaravanResource
from haravan import mixins
import haravan


class SmartCollection(HaravanResource, mixins.Metafields, mixins.Events):

    def products(self):
        return haravan.Product.find(collection_id=self.id)
