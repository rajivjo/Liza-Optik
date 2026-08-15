def transposition(sph, cyl, axis):
    new_sph = round(sph + cyl, 2)
    new_cyl = round(-cyl, 2)
    new_axis = (axis + 90) % 180
    if new_axis == 0:
        new_axis = 180
    return new_sph, new_cyl, new_axis

def sphere_equivalent(sph, cyl):
    return round(sph + (cyl / 2), 2)

def bvd_compensation(power, bvd_mm=12):
    if abs(power) < 4.0:
        return power
    d = bvd_mm / 1000
    compensated = power / (1 - d * power)
    return round(compensated, 2)

def near_power(sph, add):
    return round(sph + add, 2)

def total_pd(pd_right, pd_left):
    return round(pd_right + pd_left, 1)

def near_pd(distance_pd):
    return round(distance_pd - 3, 1)

def add_estimator(age):
    if age < 40:
        return 0.0
    elif age <= 44:
        return 1.00
    elif age <= 49:
        return 1.50
    elif age <= 54:
        return 2.00
    else:
        return 2.50

def prism_prentice(power, decentration_mm):
    decentration_cm = decentration_mm / 10
    return round(abs(power) * decentration_cm, 2)

def cl_power(sph, cyl, axis, bvd_mm=12):
    se = sphere_equivalent(sph, cyl)
    cl = bvd_compensation(se, bvd_mm)
    return cl
