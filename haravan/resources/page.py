from ..base import HaravanResource
from haravan import mixins


class Page(HaravanResource, mixins.Metafields, mixins.Events):
    pass
