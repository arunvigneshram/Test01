chargers = [
    {
        "id": 1,
        "ip": "10.10.11.70",
        "port": "80",
        "type": 1,  # 1 - 11KW, 2 - 22KW
        "distributor": "A",
        "current_limit": 16,  # In amps for each phase
    },
]

distributors = [
    {
        "id": "A",
        "type": "Sub Distributor",
        "power_limit": 120,  # In KW for each phase
        "current_limit": 150,  # In amps for each phase
    },
    {
        "id": "B",
        "type": "Sub Distributor",
        "power_limit": 120,  # In KW for each phase
        "current_limit": 150,  # In amps for each phase
    },
    {
        "id": "C",
        "type": "Sub Distributor",
        "power_limit": 120,  # In KW for each phase
        "current_limit": 150,  # In amps for each phase
    },
    {
        "id": "M",
        "type": "Sub Distributor",
        "power_limit": 200,  # In KW for each phase
        "current_limit": 265,  # In amps for each phase
    },
]
