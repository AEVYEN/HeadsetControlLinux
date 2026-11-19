import hid

VID, PID = 0x0ECB, 0x20A2
path = next(d["path"] for d in hid.enumerate(VID, PID) if d["usage_page"] == 0xFF13)

dev = hid.device()
dev.open_path(path)
for rid, length in [(0x47, 2), (0x4A, 2), (0x5C, 2), (0x67, 2)]:
    try:
        data = dev.get_feature_report(rid, 64)[:length]
        print(f"{rid:02X}={data[1]:02X}", end="  ")
    except OSError as e:
        print(f"{rid:02X}=hata", end="  ")
print()
dev.close()