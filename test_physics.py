from physics import get_air_density, get_lift, get_required_cl, get_cd, get_stall_speed

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

    assert round(lift, 2) == round(weight, 2)

def test_drag_polar_equation():
    cd0 = 0.02
    k = 0.05
    cl = 2

    result = get_cd(cl, cd0, k)
    assert round(result, 4) == 0.22

def test_stall_speed_is_positive():
    weight = 800
    air_density = 1.225
    wing_area = 16
    cl_max = 1.5

    stall_speed = get_stall_speed(weight, air_density, wing_area, cl_max)
    assert stall_speed > 0

def test_stall_speed_increases_with_altitude():
    weight = 800
    wing_area = 16
    cl_max = 1.5

    sea_level_density = 1.225      # sea level
    high_altitude_density = 0.9    # roughly 3000m altitude — thinner air

    stall_speed_sea_level = get_stall_speed(weight, sea_level_density, wing_area, cl_max)
    stall_speed_high_alt = get_stall_speed(weight, high_altitude_density, wing_area, cl_max)

    assert stall_speed_high_alt > stall_speed_sea_level