from ..base import HaravanResource
from haravan import mixins
import haravan

class Policy(HaravanResource, mixins.Metafields, mixins.Events):
  pass
