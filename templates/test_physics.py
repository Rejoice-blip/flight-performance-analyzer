from physics import get_air_density

def test_sea_level_density():
    result = get_air_density(0)
    assert round(result, 4) == 1.2250
    def test_lift_equals_weight_in_level_flight():
    weight = 800  # arbitrary test value, in Newtons
    air_density = 1.225
    velocity = 50
    wing_area = 16

    cl = get_required_cl(weight, air_density, velocity, wing_area)
    lift = get_lift(air_density, velocity, wing_area, cl)

    assert round(lift, 2) == round(weight, 2)from physics import get_air_density, get_lift, get_required_cl