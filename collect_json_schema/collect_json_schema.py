from marshmallow import Schema, fields


class CollectJSONSchema(Schema):
    """Schema for Collect."""

    url = fields.String(required=True)
    payload_id = fields.String()
