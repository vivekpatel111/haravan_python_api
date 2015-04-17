from ..base import HaravanResource


class ApplicationCharge(HaravanResource):

    def activate(self):
        self._load_attributes_from_response(self.post("activate"))
