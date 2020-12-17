from datetime import timedelta, date

from chalicelib.reservas.api import get_dias_a_reservar


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)



def test_group_reserves():
    """
        +-------+----------+----------+
        | Today |    Reserved Days    |
        |       | Group 1  |  Group 2 |
        +-------+----------+----------+
        | L     | L M X    | J V      |
        | M     | M X      | J V      |
        | X     | X        | J V      |
        | J     | L M X*   | J V      |
        | V     | L M X*   | V        |
        | S     | L M X*   | J V*     |
        | D     | L M X*   | J V*     |
        +-------+----------+----------+
    * For next week
    """
    MONDAY = date(2020, 12, 14)
    TUESDAY = date(2020, 12, 15)
    WEDNESDAY = date(2020, 12, 16)
    THURSDAY = date(2020, 12, 17)
    FRIDAY = date(2020, 12, 18)
    SATURDAY = date(2020, 12, 19)
    SUNDAY = date(2020, 12, 20)
    NEXT_MONDAY = date(2020, 12, 21)
    NEXT_TUESDAY = date(2020, 12, 22)
    NEXT_WEDNESDAY = date(2020, 12, 23)
    NEXT_THURSDAY = date(2020, 12, 24)
    NEXT_FRIDAY = date(2020, 12, 25)
    NEXT_SATURDAY = date(2020, 12, 26)
    NEXT_SUNDAY = date(2020, 12, 27)

    # Just to check we didn't mess  up
    assert MONDAY.weekday() == 0
    assert NEXT_MONDAY.weekday() == 0
    assert NEXT_SATURDAY.weekday() == 5
    assert NEXT_SUNDAY.weekday() == 6

    # Group 1
    assert get_dias_a_reservar(MONDAY, group=1)    == [MONDAY, TUESDAY, WEDNESDAY]
    assert get_dias_a_reservar(TUESDAY, group=1)   == [TUESDAY, WEDNESDAY]
    assert get_dias_a_reservar(WEDNESDAY, group=1) == [WEDNESDAY]

    assert get_dias_a_reservar(THURSDAY, group=1)  == [NEXT_MONDAY, NEXT_TUESDAY, NEXT_WEDNESDAY]
    assert get_dias_a_reservar(FRIDAY, group=1)    == [NEXT_MONDAY, NEXT_TUESDAY, NEXT_WEDNESDAY]
    assert get_dias_a_reservar(SATURDAY, group=1)  == [NEXT_MONDAY, NEXT_TUESDAY, NEXT_WEDNESDAY]
    assert get_dias_a_reservar(SUNDAY, group=1)    == [NEXT_MONDAY, NEXT_TUESDAY, NEXT_WEDNESDAY]

    # Group 2
    assert get_dias_a_reservar(MONDAY, group=2)    == [THURSDAY, FRIDAY]
    assert get_dias_a_reservar(TUESDAY, group=2)   == [THURSDAY, FRIDAY]
    assert get_dias_a_reservar(WEDNESDAY, group=2) == [THURSDAY, FRIDAY]
    assert get_dias_a_reservar(THURSDAY, group=2)  == [THURSDAY, FRIDAY]
    assert get_dias_a_reservar(FRIDAY, group=2)    == [FRIDAY]
    assert get_dias_a_reservar(SATURDAY, group=2)  == [NEXT_THURSDAY, NEXT_FRIDAY]
    assert get_dias_a_reservar(SUNDAY, group=2)    == [NEXT_THURSDAY, NEXT_FRIDAY]
