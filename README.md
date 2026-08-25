# Flight Performance Analyzer

A Python-based tool that models aerodynamic forces and evaluates aircraft
performance under different flight conditions. Built as an independent
engineering software project, combining aerospace fundamentals with a
working Python backend and web interface.

![Flight Performance Analyzer Dashboard](screenshot.png)

## What it does

Given an aircraft's physical/aerodynamic properties and a set of flight
conditions (altitude, airspeed), the analyzer calculates:

- Air density (via the ISA atmospheric model)
- Weight, Lift, and Drag
- Lift-to-drag ratio
- Stall speed
- Thrust-to-weight ratio
- Excess thrust
- Rate of climb

It also generates performance curves across a range of airspeeds:

- Lift vs Airspeed
- Drag vs Airspeed
- Lift-to-Drag Ratio vs Airspeed
- Rate of Climb vs Airspeed

## Physics model and assumptions

The analyzer assumes steady, level (unaccelerated) flight. Under this
assumption, Lift must equal Weight, so the lift coefficient (CL) is
calculated as whatever value is required to balance the aircraft's
weight at the given airspeed and altitude, rather than being chosen
freely.

Core equations used:

- Weight: W = m * g
- Lift: L = 0.5 * rho * V^2 * S * CL
- Drag: D = 0.5 * rho * V^2 * S * CD
- Drag polar: CD = CD0 + k * CL^2
- Stall speed: V_stall = sqrt(2W / (rho * S * CL_max))
- Rate of climb (excess power method): ROC = (T - D) * V / W

Air density is calculated using a simplified International Standard
Atmosphere (ISA) model, valid for altitudes 0-11,000 m (the
troposphere), where temperature decreases linearly with altitude.

## Project structure

- `physics.py` - Core physics engine (air density, lift, drag,
  performance calculations)
- `plots.py` - Generates and saves performance curve graphs
- `app.py` - Flask web server, connects the physics engine to a
  browser-based input form
- `templates/index.html` - Web form for entering aircraft parameters
  and flight conditions, and displaying results

## How to run it

1. Install dependencies: