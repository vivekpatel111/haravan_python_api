from ..base import HaravanResource
from haravan import mixins


class Variant(HaravanResource, mixins.Metafields):
    _prefix_source = "/admin/products/$product_id/"

    @classmethod
    def _prefix(cls, options={}):
        product_id = options.get("product_id")
        if product_id:
            return "/admin/products/%s" % (product_id)
        else:
            return "/admin"

    def save(self):
        if 'product_id' not in self._prefix_options:
            self._prefix_options['product_id'] = self.product_id
        return super(HaravanResource, self).save()
