# physics.py
# Flight Performance Analyzer - Physics Engine
# This file calculates air density, weight, lift, drag, stall speed,
# lift-to-drag ratio, thrust-to-weight ratio, excess thrust, and
# rate of climb for an aircraft in steady, level flight.

# --- Constants (values that never change) ---
T0 = 288.15       # Sea-level standard temperature, in Kelvin (15°C)
P0 = 101325       # Sea-level standard pressure, in Pascals
LAPSE_RATE = 0.0065   # How fast temperature drops per meter of altitude (K/m)
R = 287.05        # Specific gas constant for dry air (J/(kg*K))
G = 9.80665       # Gravitational acceleration (m/s^2)


def get_air_density(altitude_m):
    """
    Calculates air density at a given altitude using the ISA model.
    Valid for altitudes 0 to 11,000 m (the troposphere).
    """
    temperature = T0 - LAPSE_RATE * altitude_m
    pressure = P0 * (temperature / T0) ** (G / (LAPSE_RATE * R))
    density = pressure / (R * temperature)
    return density


def get_weight(mass_kg):
    """
    Calculates weight from mass using W = m * g.
    """
    weight = mass_kg * G
    return weight


def get_lift(air_density, velocity, wing_area, cl):
    """
    Calculates lift using L = 0.5 * rho * V^2 * S * CL
    """
    lift = 0.5 * air_density * velocity**2 * wing_area * cl
    return lift


def get_drag(air_density, velocity, wing_area, cd):
    """
    Calculates drag using D = 0.5 * rho * V^2 * S * CD
    """
    drag = 0.5 * air_density * velocity**2 * wing_area * cd
    return drag


def get_required_cl(weight, air_density, velocity, wing_area):
    """
    Calculates the CL needed for Lift to equal Weight
    (steady, level flight) at a given speed and altitude.
    """
    cl = weight / (0.5 * air_density * velocity**2 * wing_area)
    return cl


def get_cd(cl, cd0, k):
    """
    Calculates CD using the drag polar equation:
    CD = CD0 + k * CL^2
    """
    cd = cd0 + k * cl**2
    return cd


def get_stall_speed(weight, air_density, wing_area, cl_max):
    """
    Calculates the minimum speed before the aircraft stalls.
    V_stall = sqrt(2 * W / (rho * S * CL_max))
    """
    stall_speed = (2 * weight / (air_density * wing_area * cl_max)) ** 0.5
    return stall_speed


def get_lift_to_drag_ratio(lift, drag):
    """
    Calculates the lift-to-drag ratio, a measure of aerodynamic efficiency.
    """
    ld_ratio = lift / drag
    return ld_ratio


def get_thrust_to_weight_ratio(max_thrust, weight):
    """
    Calculates the thrust-to-weight ratio — how much thrust the
    aircraft has available relative to its weight.
    """
    twr = max_thrust / weight
    return twr


def get_excess_thrust(max_thrust, drag):
    """
    Calculates excess thrust: the thrust left over after overcoming drag.
    This is what's available to accelerate or climb.
    """
    excess_thrust = max_thrust - drag
    return excess_thrust


def get_rate_of_climb(excess_thrust, velocity, weight):
    """
    Calculates rate of climb using the excess power method:
    ROC = (excess thrust * velocity) / weight
    """
    roc = (excess_thrust * velocity) / weight
    return roc


if __name__ == "__main__":
    # --- Sample aircraft parameters ---
    mass_kg = 1200
    wing_area_m2 = 16.2
    cd0 = 0.027            # zero-lift drag coefficient
    k = 0.045              # induced drag factor
    cl_max = 1.4           # maximum lift coefficient before stall
    max_thrust_n = 2500    # maximum available thrust, in Newtons
    altitude_m = 2000
    velocity_ms = 60

    # --- Run the calculations ---
    rho = get_air_density(altitude_m)
    weight = get_weight(mass_kg)
    cl = get_required_cl(weight, rho, velocity_ms, wing_area_m2)
    cd = get_cd(cl, cd0, k)
    lift = get_lift(rho, velocity_ms, wing_area_m2, cl)
    drag = get_drag(rho, velocity_ms, wing_area_m2, cd)
    stall_speed = get_stall_speed(weight, rho, wing_area_m2, cl_max)
    ld_ratio = get_lift_to_drag_ratio(lift, drag)
    twr = get_thrust_to_weight_ratio(max_thrust_n, weight)
    excess_thrust = get_excess_thrust(max_thrust_n, drag)
    roc = get_rate_of_climb(excess_thrust, velocity_ms, weight)

    # --- Print the results ---
    print(f"Air density: {rho:.4f} kg/m^3")
    print(f"Weight: {weight:.2f} N")
    print(f"Required CL: {cl:.4f}")
    print(f"CD: {cd:.4f}")
    print(f"Lift: {lift:.2f} N")
    print(f"Drag: {drag:.2f} N")
    print(f"Stall speed: {stall_speed:.2f} m/s")
    print(f"Lift-to-drag ratio: {ld_ratio:.2f}")
    print(f"Thrust-to-weight ratio: {twr:.3f}")
    print(f"Excess thrust: {excess_thrust:.2f} N")
    print(f"Rate of climb: {roc:.2f} m/s")