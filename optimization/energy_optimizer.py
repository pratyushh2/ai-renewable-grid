def optimize_energy(solar_power, demand_dict):

    PRIORITY = [
        "Assembly",
        "Government Offices",
        "Capital Complex",
        "Residential",
        "Solar Farm"
    ]

    allocation = {}
    remaining_power = solar_power

    for zone in PRIORITY:

        demand = demand_dict.get(zone, 0)

        if remaining_power >= demand:
            allocation[zone] = demand
            remaining_power -= demand
        else:
            allocation[zone] = remaining_power
            remaining_power = 0

    return allocation