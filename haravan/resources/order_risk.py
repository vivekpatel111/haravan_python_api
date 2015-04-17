from ..base import HaravanResource

class OrderRisk(HaravanResource):
  _prefix_source = "/admin/orders/$order_id/"
  _plural = "risks"
