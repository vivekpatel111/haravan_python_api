from ..base import HaravanResource
from haravan import mixins
import haravan


class Blog(HaravanResource, mixins.Metafields, mixins.Events):

    def articles(self):
        return haravan.Article.find(blog_id=self.id)
