from ..base import HaravanResource


class Fulfillment(HaravanResource):
    _prefix_source = "/admin/orders/$order_id/"

    def cancel(self):
        self._load_attributes_from_response(self.post("cancel"))

    def complete(self):
        self._load_attributes_from_response(self.post("complete"))
