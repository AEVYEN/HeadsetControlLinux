import hid

VID, PID = 0x0ECB, 0x20A2

for d in hid.enumerate(VID, PID):
    print(f"usage_page=0x{d['usage_page']:04X} usage=0x{d['usage']:04X} "
          f"interface={d['interface_number']}")
    print(f"  path={d['path']}")