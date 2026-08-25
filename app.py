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
    fig, ax = plt.subplots(facecolor="#500724")
    ax.set_facecolor("#3b0a2a")
    ax.plot(x_values, y_values, color="#ec4899", linewidth=2)
    ax.set_xlabel(xlabel, color="#f9a8d4")
    ax.set_ylabel(ylabel, color="#f9a8d4")
    ax.set_title(title, color="#fce7f3")
    ax.tick_params(colors="#f9a8d4")
    ax.grid(True, color="#831843")
    for spine in ax.spines.values():
        spine.set_color("#831843")

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
        # --- Read form inputs (all come in as text, so we convert to float) ---
        mass_kg = float(request.form["mass_kg"])
        wing_area_m2 = float(request.form["wing_area_m2"])
        max_thrust_n = float(request.form["max_thrust_n"])
        cd0 = float(request.form["cd0"])
        k = float(request.form["k"])
        cl_max = float(request.form["cl_max"])
        altitude_m = float(request.form["altitude_m"])
        airspeed_ms = float(request.form["airspeed_ms"])

        # --- Validate inputs: catch physically impossible values early ---
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

        # --- Only run calculations if all inputs are valid ---
        if not errors:
            # --- Run the physics engine, same as in physics.py ---
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

            # --- Sweep across a range of airspeeds for the graphs ---
            airspeeds = list(range(20, 101, 2))
            lift_values = []
            drag_values = []
            ld_values = []
            roc_values = []

            for v in airspeeds:
                v_cl = get_required_cl(weight, rho, v, wing_area_m2)
                v_cd = get_cd(v_cl, cd0, k)
                v_lift = get_lift(rho, v, wing_area_m2, v_cl)
                v_drag = get_drag(rho, v, wing_area_m2, v_cd)
                v_ld = get_lift_to_drag_ratio(v_lift, v_drag)
                v_excess_thrust = get_excess_thrust(max_thrust_n, v_drag)
                v_roc = get_rate_of_climb(v_excess_thrust, v, weight)

                lift_values.append(v_lift)
                drag_values.append(v_drag)
                ld_values.append(v_ld)
                roc_values.append(v_roc)

            # --- Generate the four graphs as embeddable images ---
            lift_plot = make_plot(airspeeds, lift_values, "Airspeed (m/s)", "Lift (N)", "Lift vs Airspeed")
            drag_plot = make_plot(airspeeds, drag_values, "Airspeed (m/s)", "Drag (N)", "Drag vs Airspeed")
            ld_plot = make_plot(airspeeds, ld_values, "Airspeed (m/s)", "Lift-to-Drag Ratio", "Lift-to-Drag Ratio vs Airspeed")
            roc_plot = make_plot(airspeeds, roc_values, "Airspeed (m/s)", "Rate of Climb (m/s)", "Rate of Climb vs Airspeed")

            # --- Package results into a dictionary to send to the HTML page ---
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
            }

    return render_template("index.html", results=results, errors=errors)


if __name__ == "__main__":
    app.run(debug=True)