def validate_prescription(sph, cyl, axis, add=None, pd=None):
    errors = []

    if not (-20.0 <= sph <= 20.0):
        errors.append("SPH mesti antara -20.00 hingga +20.00")

    if not (-10.0 <= cyl <= 10.0):
        errors.append("CYL mesti antara -10.00 hingga +10.00")

    if cyl != 0 and not (0 <= axis <= 180):
        errors.append("AXIS mesti antara 0° hingga 180°")

    if cyl != 0 and axis == 0:
        errors.append("AXIS tidak boleh 0° jika ada CYL — semak semula")

    if add is not None and not (0 <= add <= 4.0):
        errors.append("ADD mesti antara 0 hingga +4.00")

    if pd is not None and not (50 <= pd <= 80):
        errors.append("PD mesti antara 50mm hingga 80mm")

    return errors
