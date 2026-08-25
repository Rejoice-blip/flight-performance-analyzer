# app.py
# Flight Performance Analyzer - Web Server

import io
import base64
import matplotlib
matplotlib.use("Agg")  # use a non-interactive backend, since this runs on a server, not your screen
import matplotlib.pyplot as plt

from flask import Flask, render_template, request

from physics import (
    get_air_density,
    get_weight,
    get_required_cl,
    get_cd,
    get_lift,
    get_drag,
    get_stall_speed,
    get_lift_to_drag_ratio,
    get_thrust_to_weight_ratio,
    get_excess_thrust,
    get_rate_of_climb,
)

app = Flask(__name__)


def make_plot(x_values, y_values, xlabel, ylabel, title):
    """
    Creates a plot and returns it as a Base64-encoded string,
    which can be embedded directly in an HTML <img> tag.
    """
    fig, ax = plt.subplots(facecolor="#171412")
    ax.set_facecolor("#0a0a0a")
    ax.plot(x_values, y_values, color="#f59e0b", linewidth=2)
    ax.set_xlabel(xlabel, color="#fbbf24")
    ax.set_ylabel(ylabel, color="#fbbf24")
    ax.set_title(title, color="#f5e6d3")
    ax.tick_params(colors="#fbbf24")
    ax.grid(True, color="#292018")
    for spine in ax.spines.values():
        spine.set_color("#292018")

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return image_base64


@app.route("/", methods=["GET", "POST"])
def home():
    results = None
    errors = []

    if request.method == "POST":
        try:
            mass_kg = float(request.form["mass_kg"])
            wing_area_m2 = float(request.form["wing_area_m2"])
            max_thrust_n = float(request.form["max_thrust_n"])
            cd0 = float(request.form["cd0"])
            k = float(request.form["k"])
            cl_max = float(request.form["cl_max"])
            altitude_m = float(request.form["altitude_m"])
            airspeed_ms = float(request.form["airspeed_ms"])
        except ValueError:
            errors.append("All fields must contain valid numbers.")
            mass_kg = wing_area_m2 = max_thrust_n = cd0 = k = cl_max = altitude_m = airspeed_ms = 0

        if mass_kg <= 0:
            errors.append("Mass must be greater than 0.")
        if wing_area_m2 <= 0:
            errors.append("Wing area must be greater than 0.")
        if max_thrust_n <= 0:
            errors.append("Max thrust must be greater than 0.")
        if cd0 < 0:
            errors.append("CD0 cannot be negative.")
        if k <= 0:
            errors.append("Induced drag factor (k) must be greater than 0.")
        if cl_max <= 0:
            errors.append("CL max must be greater than 0.")
        if altitude_m < 0 or altitude_m > 11000:
            errors.append("Altitude must be between 0 and 11,000 m (model limit).")
        if airspeed_ms <= 0:
            errors.append("Airspeed must be greater than 0.")

        if not errors:
            try:
                rho = get_air_density(altitude_m)
                weight = get_weight(mass_kg)
                cl = get_required_cl(weight, rho, airspeed_ms, wing_area_m2)
                cd = get_cd(cl, cd0, k)
                lift = get_lift(rho, airspeed_ms, wing_area_m2, cl)
                drag = get_drag(rho, airspeed_ms, wing_area_m2, cd)
                stall_speed = get_stall_speed(weight, rho, wing_area_m2, cl_max)
                ld_ratio = get_lift_to_drag_ratio(lift, drag)
                twr = get_thrust_to_weight_ratio(max_thrust_n, weight)
                excess_thrust = get_excess_thrust(max_thrust_n, drag)
                roc = get_rate_of_climb(excess_thrust, airspeed_ms, weight)

                airspeeds = list(range(20, 101, 2))
                lift_values = []
                drag_values = []
                ld_values = []
                roc_values = []

                cl_fixed = 0.5

                for v in airspeeds:
                    v_cl = get_required_cl(weight, rho, v, wing_area_m2)
                    v_cd = get_cd(v_cl, cd0, k)
                    v_lift_level_flight = get_lift(rho, v, wing_area_m2, v_cl)
                    v_lift_fixed_cl = get_lift(rho, v, wing_area_m2, cl_fixed)
                    v_drag = get_drag(rho, v, wing_area_m2, v_cd)
                    v_ld = get_lift_to_drag_ratio(v_lift_level_flight, v_drag)
                    v_excess_thrust = get_excess_thrust(max_thrust_n, v_drag)
                    v_roc = get_rate_of_climb(v_excess_thrust, v, weight)

                    lift_values.append(v_lift_fixed_cl)
                    drag_values.append(v_drag)
                    ld_values.append(v_ld)
                    roc_values.append(v_roc)

                lift_plot = make_plot(airspeeds, lift_values, "Airspeed (m/s)", "Lift (N)", "Lift vs Airspeed (at fixed CL = 0.5)")
                drag_plot = make_plot(airspeeds, drag_values, "Airspeed (m/s)", "Drag (N)", "Drag vs Airspeed")
                ld_plot = make_plot(airspeeds, ld_values, "Airspeed (m/s)", "Lift-to-Drag Ratio", "Lift-to-Drag Ratio vs Airspeed")
                roc_plot = make_plot(airspeeds, roc_values, "Airspeed (m/s)", "Rate of Climb (m/s)", "Rate of Climb vs Airspeed")

                lift_at_max_speed = lift_values[-1]
                lift_at_min_speed = lift_values[0]

                min_drag = min(drag_values)
                min_drag_speed = airspeeds[drag_values.index(min_drag)]

                best_ld = max(ld_values)
                best_ld_speed = airspeeds[ld_values.index(best_ld)]

                best_roc = max(roc_values)
                best_roc_speed = airspeeds[roc_values.index(best_roc)]

                speed_vs_best_ld = round(airspeed_ms - best_ld_speed, 1)
                speed_vs_best_roc = round(airspeed_ms - best_roc_speed, 1)
                speed_vs_min_drag = round(airspeed_ms - min_drag_speed, 1)

                results = {
                    "air_density": round(rho, 4),
                    "weight": round(weight, 2),
                    "lift": round(lift, 2),
                    "drag": round(drag, 2),
                    "stall_speed": round(stall_speed, 2),
                    "ld_ratio": round(ld_ratio, 2),
                    "twr": round(twr, 3),
                    "excess_thrust": round(excess_thrust, 2),
                    "roc": round(roc, 2),
                    "lift_plot": lift_plot,
                    "drag_plot": drag_plot,
                    "ld_plot": ld_plot,
                    "roc_plot": roc_plot,
                    "lift_at_min_speed": round(lift_at_min_speed, 1),
                    "lift_at_max_speed": round(lift_at_max_speed, 1),
                    "min_speed": airspeeds[0],
                    "max_speed": airspeeds[-1],
                    "min_drag": round(min_drag, 1),
                    "min_drag_speed": min_drag_speed,
                    "best_ld": round(best_ld, 2),
                    "best_ld_speed": best_ld_speed,
                    "best_roc": round(best_roc, 2),
                    "best_roc_speed": best_roc_speed,
                    "your_speed": airspeed_ms,
                    "speed_vs_best_ld": speed_vs_best_ld,
                    "speed_vs_best_roc": speed_vs_best_roc,
                    "speed_vs_min_drag": speed_vs_min_drag,
                    "mass_kg": mass_kg,
                    "wing_area_m2": wing_area_m2,
                    "max_thrust_n": max_thrust_n,
                    "cd0": cd0,
                    "k": k,
                    "cl_max": cl_max,
                    "altitude_m": altitude_m,
                    "cl": round(cl, 4),
                    "cd": round(cd, 4),
                    "gravity": 9.81,
                }
            except Exception:
                errors.append("Something went wrong during calculation. Please check your inputs and try again.")

    return render_template("index.html", results=results, errors=errors)


if __name__ == "__main__":
    app.run(debug=True)