import random


def generate_routefile():
    random.seed(42)
    steps = 3600

    p_ne = 1. / 40
    p_ns = 1. / 40
    p_nw = 1. / 40

    p_se = 1. / 40
    p_sn = 1. / 40
    p_sw = 1. / 40

    p_wn = 1. / 30
    p_we = 1. / 20
    p_ws = 1. / 30

    p_en = 1. / 30
    p_es = 1. / 30
    p_ew = 1. / 20

    with open("../generated.rou.xml", "w") as f:
        print("""<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <route edges="-9 -9.191.77 7" color="yellow" id="en"/>
    <route edges="-9 -9.191.77 3" color="yellow" id="es"/>
    <route edges="-9 -9.191.77 11" color="yellow" id="ew"/>
    <route edges="-7 -7.191.49 9" color="yellow" id="ne"/>
    <route edges="-7 -7.191.49 3" color="yellow" id="ns"/>
    <route edges="-7 -7.191.49 11" color="yellow" id="nw"/>
    <route edges="-3 -3.213.65 9" color="yellow" id="se"/>
    <route edges="-3 -3.213.65 7" color="yellow" id="sn"/>
    <route edges="-3 -3.213.65 11" color="yellow" id="sw"/>
    <route edges="-11 -11.149.92 9" color="yellow" id="we"/>
    <route edges="-11 -11.149.92 7" color="yellow" id="wn"/>
    <route edges="-11 -11.149.92 3" color="yellow" id="ws"/>
""", file=f)

        veh_num = 0
        for i in range(steps):
            for id_, prob in {'ne': p_ne, 'ns': p_ns, 'nw': p_nw, 'se': p_se, 'sn': p_sn, 'sw': p_sw, 'wn': p_wn,
                              'we': p_we, 'ws': p_ws, 'en': p_en, 'es': p_es, 'ew': p_ew}.items():
                if random.uniform(0, 1) < prob:
                    print(f'    <vehicle id="{veh_num}" route="{id_}" depart="{i}" />', file=f)
                    veh_num += 1

        print("</routes>", file=f)


if __name__ == '__main__':
    generate_routefile()
