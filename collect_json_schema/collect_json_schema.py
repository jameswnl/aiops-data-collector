from marshmallow import Schema, fields


class CollectJSONSchema(Schema):
    """Schema for Collect."""

    url = fields.String()
    payload_id = fields.String()
