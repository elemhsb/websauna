import uuid
from pyramid_web20.utils.slug import slug_to_uuid
from pyramid_web20.utils.slug import uuid_to_slug


def test_uuid_slug():
    """Make short slugs for 64-bit UUID ids."""
    _uuid = uuid.uuid4()

    _uuid2 = slug_to_uuid(uuid_to_slug(_uuid))
    assert _uuid == _uuid2