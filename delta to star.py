"""
Delta-Star (Δ-Y) Connection Calculator
--------------------------------------
A menu-driven program for engineering students to analyse a three-phase
system with a DELTA-connected source feeding a STAR-connected load, a
delta-star transformer, and delta-to-star impedance conversion.

Balanced delta-star system (per-phase analysis):
    Source (delta) line voltage VL = source phase voltage
    Equivalent star voltage     Vph = VL / sqrt(3)
    Line current                IL = Vph / |Zline + Zload|
    Load phase voltage          V_load = IL * |Zload|
    Load line voltage           = sqrt(3) * V_load
    Load power                  P = 3 * IL^2 * R_load
    Source winding current      I_winding = IL / sqrt(3)
    Neutral current             = 0

Unbalanced delta-star system:
    Equivalent source phase voltages  Van = (Vab - Vca) / 3, etc.
    4-wire (neutral wire):            Ik = Vk / (Zline + Zk),  In = Ia + Ib + Ic
    3-wire (no neutral wire):         V_N'N = sum(Vk*Yk) / sum(Yk)
                                      Ik = (Vk - V_N'N) / (Zline + Zk)

Delta-star transformer:
    Secondary line voltage   VL2 = sqrt(3) * VL1 / a        (a = N1 / N2)
    Secondary phase voltage  = VL1 / a
    Secondary line current   IL2 = secondary phase current
    Primary line current     IL1 = sqrt(3) * IL2 / a
    Phase shift of 30 degrees between primary and secondary line voltages

Delta to star impedance conversion:
    Z_a = Z_ab * Z_ca / (Z_ab + Z_bc + Z_ca)
    Z_b = Z_ab * Z_bc / (Z_ab + Z_bc + Z_ca)
    Z_c = Z_bc * Z_ca / (Z_ab + Z_bc + Z_ca)
    Balanced case: Z_star = Z_delta / 3
"""

import cmath
import math

SQRT3 = math.sqrt(3)


# ---------------------------------------------------------------- input helpers
def get_positive_float(prompt):
    """Keep asking until the user enters a valid positive number."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("  Please enter a value greater than zero.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_nonneg_float(prompt):
    """Ask for a number that may be zero but not negative."""
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("  Please enter zero or a positive value.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_float(prompt):
    """Ask for any number (zero and negative values allowed)."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_impedance(label, who="Load"):
    """Ask for resistance and reactance of one phase; return complex Z.
    Reactance: positive for inductive, negative for capacitive."""
    r = get_positive_float(f"  {who} {label}: resistance R (ohm): ")
    x = get_float(f"  {who} {label}: reactance X (ohm, - for capacitive): ")
    return complex(r, x)


def get_line_impedance():
    """Ask for the impedance of each line conductor (may be zero)."""
    print("  Line (cable) impedance per phase - enter 0 and 0 if ignored:")
    r = get_nonneg_float("  Line resistance (ohm): ")
    x = get_nonneg_float("  Line reactance (ohm): ")
    return complex(r, x)


# ------------------------------------------------------------------ core maths
def delta_to_star(zab, zbc, zca):
    """Equivalent star impedances (Za, Zb, Zc) of any (balanced or not) delta."""
    total = zab + zbc + zca
    return zab * zca / total, zab * zbc / total, zbc * zca / total


def neutral_shift(voltages, impedances):
    """Millman's theorem: voltage between load neutral and source neutral."""
    admittances = [1 / z for z in impedances]
    numerator = sum(v * y for v, y in zip(voltages, admittances))
    return numerator / sum(admittances)


# ------------------------------------------------------------------- display
def show_polar(name, value, unit):
    """Print a complex quantity in polar form."""
    mag, ang = cmath.polar(value)
    print(f"  {name} = {mag:.3f} < {math.degrees(ang):.2f} deg {unit}")


def show_rect(name, z):
    """Print an impedance in rectangular form."""
    sign = "+" if z.imag >= 0 else "-"
    print(f"  {name} = {z.real:.3f} {sign} j{abs(z.imag):.3f} ohm")


def balanced_delta_star():
    v_l = get_positive_float("Source (delta) line voltage VL (V): ")
    z_line = get_line_impedance()
    z_load = get_impedance("(each star phase)")

    v_ph = v_l / SQRT3
    z_total = z_line + z_load
    i_l = v_ph / abs(z_total)
    v_load_ph = i_l * abs(z_load)
    v_load_line = SQRT3 * v_load_ph
    pf = z_load.real / abs(z_load)
    s_load = 3 * i_l ** 2 * abs(z_load)
    p_load = 3 * i_l ** 2 * z_load.real
    q_load = 3 * i_l ** 2 * z_load.imag
    p_loss = 3 * i_l ** 2 * z_line.real
    drop = (v_ph - v_load_ph) / v_ph * 100
    eff = p_load / (p_load + p_loss) * 100

    print("\n  ----- Balanced Delta-Star System -----")
    print(f"  Equivalent star source voltage = {v_ph:.3f} V")
    print(f"  Line current = phase current   = {i_l:.4f} A")
    print(f"  Source winding current         = {i_l / SQRT3:.4f} A (delta)")
    print(f"  Load phase voltage             = {v_load_ph:.3f} V")
    print(f"  Load line voltage              = {v_load_line:.3f} V")
    print(f"  Voltage drop in lines          = {drop:.2f} %")
    print(f"  Load power factor              = {pf:.4f} {'lagging' if z_load.imag > 0 else 'leading' if z_load.imag < 0 else '(unity)'}")
    print(f"  Load apparent power S          = {s_load:,.2f} VA")
    print(f"  Load active power P            = {p_load:,.2f} W")
    print(f"  Load reactive power Q          = {q_load:,.2f} VAR")
    print(f"  Line power loss                = {p_loss:,.2f} W")
    print(f"  Transmission efficiency        = {eff:.2f} %")
    print("  Neutral current                = 0 A (balanced load)")


def unbalanced_delta_star(four_wire):
    v_l = get_positive_float("Source (delta) line voltage VL (V): ")
    z_line = get_line_impedance()
    print("\n  Enter the load impedance of each star phase:")
    loads = [get_impedance("A"), get_impedance("B"), get_impedance("C")]

    # Delta source line voltages (ABC sequence, Vab as reference)
    vab = cmath.rect(v_l, 0)
    vbc = cmath.rect(v_l, math.radians(-120))
    vca = cmath.rect(v_l, math.radians(120))
    voltages = [(vab - vca) / 3, (vbc - vab) / 3, (vca - vbc) / 3]

    totals = [z_line + z for z in loads]
    v_nn = 0 if four_wire else neutral_shift(voltages, totals)
    currents = [(v - v_nn) / zt for v, zt in zip(voltages, totals)]
    v_loads = [i * z for i, z in zip(currents, loads)]
    p_total = sum(abs(i) ** 2 * z.real for i, z in zip(currents, loads))

    title = "4-wire" if four_wire else "3-wire"
    print(f"\n  ----- Unbalanced {title} Delta-Star System -----")
    for name, i in zip("abc", currents):
        show_polar(f"Line current I{name}", i, "A")
    for name, v in zip("abc", v_loads):
        show_polar(f"Load voltage V{name}n'", v, "V")
    if four_wire:
        show_polar("Neutral current In", sum(currents), "A")
    else:
        show_polar("Neutral shift V_N'N", v_nn, "V")
        print("  (Unequal load voltages appear because the load neutral floats.)")
    print(f"  Total load active power P = {p_total:,.2f} W")


def delta_star_transformer():
    v1 = get_positive_float("Primary (delta) line voltage VL1 (V): ")
    turns1 = get_positive_float("Primary turns per phase N1: ")
    turns2 = get_positive_float("Secondary turns per phase N2: ")
    kva = get_positive_float("Total three-phase rating (kVA): ")

    a = turns1 / turns2
    v2_ph = v1 / a
    v2_line = SQRT3 * v2_ph
    il2 = kva * 1000 / (SQRT3 * v2_line)
    il1 = kva * 1000 / (SQRT3 * v1)

    print("\n  ----- Delta-Star Transformer -----")
    print(f"  Turns ratio a = N1/N2        = {a:.4f}")
    print(f"  Primary phase voltage        = {v1:.3f} V (= line voltage)")
    print(f"  Secondary phase voltage      = {v2_ph:.3f} V")
    print(f"  Secondary line voltage       = {v2_line:.3f} V")
    print(f"  Line voltage ratio           = {v2_line / v1:.4f} (= sqrt(3)/a)")
    print(f"  Primary line current         = {il1:.3f} A")
    print(f"  Primary winding current      = {il1 / SQRT3:.3f} A")
    print(f"  Secondary line/phase current = {il2:.3f} A")
    print(f"  Rating of each transformer   = {kva / 3:.3f} kVA")
    print("  Phase shift of 30 degrees between primary and secondary line voltages.")
    print("  The star point gives a neutral for single-phase loads (3-phase 4-wire).")


def impedance_conversion():
    print("  1. Balanced delta (all three phases equal)")
    print("  2. Unbalanced delta (three different impedances)")
    while True:
        pick = input("  Enter 1 or 2: ").strip()
        if pick in ("1", "2"):
            break
        print("  Please enter 1 or 2.")

    print("\n  ----- Equivalent Star Impedances -----")
    if pick == "1":
        z = get_impedance("(balanced)", who="Delta")
        show_rect("Z_star (each phase)", z / 3)
    else:
        zab = get_impedance("AB", who="Delta")
        zbc = get_impedance("BC", who="Delta")
        zca = get_impedance("CA", who="Delta")
        za, zb, zc = delta_to_star(zab, zbc, zca)
        print()
        show_rect("Z_a", za)
        show_rect("Z_b", zb)
        show_rect("Z_c", zc)


def menu():
    print("\n" + "=" * 54)
    print("        DELTA-STAR CONNECTION CALCULATOR")
    print("=" * 54)
    print(" 1. Balanced delta-star system (with line impedance)")
    print(" 2. Unbalanced 4-wire delta-star (neutral current)")
    print(" 3. Unbalanced 3-wire delta-star (neutral shift)")
    print(" 4. Delta-star three-phase transformer")
    print(" 5. Delta to star impedance conversion")
    print(" 0. Exit")
    print("-" * 54)


def main():
    while True:
        menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            balanced_delta_star()
        elif choice == "2":
            unbalanced_delta_star(four_wire=True)
        elif choice == "3":
            unbalanced_delta_star(four_wire=False)
        elif choice == "4":
            delta_star_transformer()
        elif choice == "5":
            impedance_conversion()
        elif choice == "0":
            print("\nThank you for using the calculator. Goodbye!")
            break
        else:
            print("  Invalid choice. Please select from the menu.")


if __name__ == "__main__":
    main()
