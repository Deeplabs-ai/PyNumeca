import os
import re


def read_mf(mf_file: str) -> dict:
    """
    :param mf_file: .mf file path
    :return: dictionary representing the specified .plan file

    Reading a Numeca .mf, extracting main results and exporting them as a python dictionary

    """
    if not os.path.isfile(mf_file):
        raise FileNotFoundError(f"{mf_file} does not exist")

    # Open the file and read its contents
    with open(mf_file, "r") as f:
        contents = f.read()

    # Regular expressions to match the desired values
    inlet_pressure_pattern = "Static_pressure\s+([\d\.]+)"
    inlet_temperature_pattern = "Static_temperature\s+([\d\.]+)"
    mass_flow_pattern = "Mass_flow\s+([\d\.]+)"
    rotational_speed_pattern = "Rotational_speed\s+([\d\.\-]+)"
    inlet_absolute_total_pressure_pattern = "Absolute_total_pressure\s+([\d\.]+)"
    inlet_absolute_total_temperature_pattern = "Absolute_total_temperature\s+([\d\.]+)"
    absolute_total_pressure_ratio_pattern = "Absolute_total_pressure_ratio\s+([\d\.]+)"
    isentropic_efficiency_pattern = "Isentropic_efficiency\s+([\d\.]+)"

    # Find the values using regular expressions
    inlet_pressure = float(re.search(inlet_pressure_pattern, contents).group(1))
    inlet_temperature = float(re.search(inlet_temperature_pattern, contents).group(1))
    mass_flow = float(re.search(mass_flow_pattern, contents).group(1))
    rotational_speed = abs(
        float(re.search(rotational_speed_pattern, contents).group(1))
    )
    inlet_absolute_total_pressure = float(
        re.search(inlet_absolute_total_pressure_pattern, contents).group(1)
    )
    inlet_absolute_total_temperature = float(
        re.search(inlet_absolute_total_temperature_pattern, contents).group(1)
    )
    absolute_total_pressure_ratio = float(
        re.search(absolute_total_pressure_ratio_pattern, contents).group(1)
    )
    isentropic_efficiency = float(
        re.search(isentropic_efficiency_pattern, contents).group(1)
    )

    # Convert rotational speed from rad/s to RPM
    rotational_speed_rpm = rotational_speed * 9.549296596425384

    # Creating output dictionary
    out = {}
    out["Ps_in"] = inlet_pressure
    out["Ts_in"] = inlet_temperature
    out["Pt_in"] = inlet_absolute_total_pressure
    out["Tt_in"] = inlet_absolute_total_temperature
    out["Mass_flow"] = mass_flow
    out["Beta_tt"] = absolute_total_pressure_ratio
    out["Eta_tt"] = isentropic_efficiency
    out["Omega"] = rotational_speed_rpm

    return out
