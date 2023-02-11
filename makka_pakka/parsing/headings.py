class HeadingStyle:
    """Enum of heading style e.g [heading_name] is SINGLE_HEADING, [[name]] is
    a DOUBLE_HEADING."""

    NO_HEADING = 0
    SINGLE_HEADING = 1
    DOUBLE_HEADING = 2


class HeadingType:
    """Heading type defines the type of code expected below, and therefore how
    to parse this data, e.g [[data]] is DATA, [[code]] is CODE, [[gadget]] is
    gadget."""

    DATA = 0
    CODE = 1
    GADGET = 2
