from invenio_db import db
from sqlalchemy import or_
from sqlalchemy_utils.models import Timestamp

from invenio_notify.errors import NotExistsError


# TOBEREMOVE
# class Pg1Model(db.Model, Timestamp):
#     __tablename__ = "pg1"
#
#     id = db.Column(db.Integer, primary_key=True)
#
#     message = db.Column(db.Text, nullable=False)
#     """The message content."""
#
#     @classmethod
#     def create(cls, data):
#         with db.session.begin_nested():
#             obj = cls(
#                 message=data.get("message"),
#                 # category=data.get("category"),
#                 # url_path=data.get("url_path"),
#                 # start_datetime=data.get("start_datetime"),
#                 # end_datetime=data.get("end_datetime"),
#                 # active=data.get("active"),
#             )
#             db.session.add(obj)
#
#         return obj
#
#     @classmethod
#     def commit(cls):
#         db.session.commit()
#
#     # @classmethod
#     # def search(cls, search_params, filters):
#     #     """Filter banners accordingly to query params."""
#     #     if filters == []:
#     #         filtered = db.session.query(BannerModel).filter()
#     #     else:
#     #         filtered = db.session.query(BannerModel).filter(or_(*filters))
#     #
#     #     banners = filtered.order_by(
#     #         search_params["sort_direction"](text(",".join(search_params["sort"])))
#     #     ).paginate(
#     #         page=search_params["page"],
#     #         per_page=search_params["size"],
#     #         error_out=False,
#     #     )
#     #
#     #     return banners
#
#     @classmethod
#     def search(cls, search_params, filters):
#         """Filter banners accordingly to query params."""
#         if filters == []:
#             results = db.session.query(Pg1Model).filter()
#         else:
#             results = db.session.query(Pg1Model).filter(or_(*filters))
#
#         # banners = filtered.order_by(
#         #     search_params["sort_direction"](text(",".join(search_params["sort"])))
#         # ).paginate(
#         #     page=search_params["page"],
#         #     per_page=search_params["size"],
#         #     error_out=False,
#         # )
#
#         return results


class NotifyInboxModel(db.Model, Timestamp):
    __tablename__ = "notify_inbox"

    id = db.Column(db.Integer, primary_key=True)

    raw = db.Column(db.Text, nullable=False)

    @classmethod
    def create(cls, data):
        with db.session.begin_nested():
            obj = cls(
                raw=data.get("raw"),
            )
            db.session.add(obj)

        return obj

    @classmethod
    def commit(cls):
        db.session.commit()

    @classmethod
    def search(cls, search_params, filters):
        """Filter banners accordingly to query params."""
        if filters == []:
            results = db.session.query(NotifyInboxModel).filter()
        else:
            results = db.session.query(NotifyInboxModel).filter(or_(*filters))

        return results

    @classmethod
    def get(cls, id):
        """Get banner by its id."""
        if obj := db.session.get(cls, id):
            return obj

        raise NotExistsError(id)

    @classmethod
    def delete(cls, obj):
        """Delete banner by its id."""
        with db.session.begin_nested():
            db.session.delete(obj)
