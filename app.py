# app.py
# Flight Performance Analyzer - Web Server

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


@app.route("/", methods=["GET", "POST"])
def home():
    results = None

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
        }

    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)