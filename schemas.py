from marshmallow import Schema, fields


class CollectSchema(Schema):
    """Schema for Collect."""

    url = fields.String()
    payload_id = fields.String()
