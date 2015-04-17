from ..base import HaravanResource
from .customer import Customer


class CustomerSavedSearch(HaravanResource):

    def customers(cls, **kwargs):
        return Customer._build_list(cls.get("customers", **kwargs))
