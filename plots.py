# plots.py
# Flight Performance Analyzer - Visualization
# Generates Lift vs Airspeed, Drag vs Airspeed, and L/D vs Airspeed graphs.

import matplotlib.pyplot as plt
from physics import (
    get_air_density,
    get_weight,
    get_required_cl,
    get_cd,
    get_lift,
    get_drag,
    get_lift_to_drag_ratio,
    get_excess_thrust,
    get_rate_of_climb,
)

# --- Sample aircraft parameters (same as in physics.py) ---
mass_kg = 1200
wing_area_m2 = 16.2
cd0 = 0.027
k = 0.045
altitude_m = 2000
max_thrust_n = 2500

# --- Generate a range of airspeeds to test ---
airspeeds = list(range(20, 101, 2))   # from 20 to 100 m/s, in steps of 2

# --- Lists to store results at each airspeed ---
lift_values = []
drag_values = []
ld_values = []
roc_values = []

# --- Calculate lift, drag, and L/D at each airspeed ---
rho = get_air_density(altitude_m)
weight = get_weight(mass_kg)

for v in airspeeds:
    cl = get_required_cl(weight, rho, v, wing_area_m2)
    cd = get_cd(cl, cd0, k)
    lift = get_lift(rho, v, wing_area_m2, cl)
    drag = get_drag(rho, v, wing_area_m2, cd)
    ld_ratio = get_lift_to_drag_ratio(lift, drag)
    excess_thrust = get_excess_thrust(max_thrust_n, drag)
    roc = get_rate_of_climb(excess_thrust, v, weight)

    lift_values.append(lift)
    drag_values.append(drag)
    ld_values.append(ld_ratio)
    roc_values.append(roc)

    # --- Create the plots ---

# Plot 1: Lift vs Airspeed
plt.figure()
plt.plot(airspeeds, lift_values)
plt.xlabel("Airspeed (m/s)")
plt.ylabel("Lift (N)")
plt.title("Lift vs Airspeed")
plt.grid(True)

plt.savefig("lift_vs_airspeed.png")

# Plot 2: Drag vs Airspeed
plt.figure()
plt.plot(airspeeds, drag_values)
plt.xlabel("Airspeed (m/s)")
plt.ylabel("Drag (N)")
plt.title("Drag vs Airspeed")
plt.grid(True)

plt.savefig("drag_vs_airspeed.png")

# Plot 3: Lift-to-Drag Ratio vs Airspeed
plt.figure()
plt.plot(airspeeds, ld_values)
plt.xlabel("Airspeed (m/s)")
plt.ylabel("Lift-to-Drag Ratio")
plt.title("Lift-to-Drag Ratio vs Airspeed")
plt.grid(True)

# Plot 4: Rate of Climb vs Airspeed
plt.figure()
plt.plot(airspeeds, roc_values)
plt.xlabel("Airspeed (m/s)")
plt.ylabel("Rate of Climb (m/s)")
plt.title("Rate of Climb vs Airspeed")
plt.grid(True)
plt.savefig("roc_vs_airspeed.png")

plt.savefig("ld_ratio_vs_airspeed.png")
# --- Show all plots on screen ---
plt.show()