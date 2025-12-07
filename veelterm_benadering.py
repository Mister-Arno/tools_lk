import random

def generate_geogebra_piecewise_approximation_smooth(allow_coincident_zeros=False):
    """
    Generates the GeoGebra function rule for a piecewise function
    approximating a cubic function using two parabolas, ensuring:
    1. Integer coordinates for zeros and extrema (vertices).
    2. A smooth (fluent) transition at the connection point.
    """

    possible_coords = list(range(-8, 9))
    possible_y_extrema = [y for y in possible_coords if y != 0]

    # --- 1. Select Zeros (x1, x2, x3) ---

    # The connection point x2 must be chosen first.
    x2 = random.choice(possible_coords)

    # Filter for x-coordinates that have the same parity as x2.
    # This ensures the vertex x-coordinates (xv1 and xv2) are integers.
    same_parity_coords = [x for x in possible_coords if (x - x2) % 2 == 0 and x != x2]

    if len(same_parity_coords) < 2:
        return "Error: Could not find suitable integer zeros for smooth integer extrema."

    # Select x1 and x3 from the filtered list
    if allow_coincident_zeros:
        x_ends = random.choices(same_parity_coords, k=2)
    else:
        x_ends = random.sample(same_parity_coords, k=2)

    x1, x3 = x_ends[0], x_ends[1]

    # Sort the zeros for proper piecewise definition (x1 < x2 < x3)
    x_zeros = sorted([x1, x2, x3])
    x1, x2, x3 = x_zeros[0], x_zeros[1], x_zeros[2]

    # --- 2. Calculate Integer Extrema Coordinates ---

    # Vertex 1 (for P1)
    xv1 = (x1 + x2) / 2  # Guaranteed to be an integer
    yv1 = random.choice(possible_y_extrema)

    # Vertex 2 (for P2)
    xv2 = (x2 + x3) / 2  # Guaranteed to be an integer
    # For a smooth transition, yv2 must be -yv1
    yv2 = -yv1

    # --- 3. Calculate Parabola Coefficients (a1 and a2) ---

    # Parabola 1: P1(x) = a1 * (x - x1) * (x - x2)
    # Passes through (xv1, yv1)
    a1_numerator = yv1
    a1_denominator = (xv1 - x1) * (xv1 - x2)
    a1 = a1_numerator / a1_denominator

    # Parabola 2: P2(x) = a2 * (x - x2) * (x - x3)
    # Enforce smoothness: a2 = a1 * (x2 - x1) / (x2 - x3)
    a2 = a1 * (x2 - x1) / (x2 - x3)

    # --- 4. Construct the GeoGebra Rule ---

    p1_func = f"{a1} * (x - {x1}) * (x - {x2})"
    p2_func = f"{a2} * (x - {x2}) * (x - {x3})"

    condition = f"x <= {x2}"
    geogebra_rule = f"If[{condition}, {p1_func}, {p2_func}]"

    summary = {
        "x1": x1, "x2": x2, "x3": x3,
        "xv1": xv1, "yv1": yv1,
        "xv2": xv2, "yv2": yv2,
        "a1": a1, "a2": a2,
        "rule": geogebra_rule
    }

    return summary

# Example usage
result = generate_geogebra_piecewise_approximation_smooth(allow_coincident_zeros=False)
print(result)