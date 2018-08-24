from lyrebird_android.android_helper import Device
import pytest


def test_package_name(self):
    device_info_str = "00c34258893533x       device usb:337641472X product:bullhead model:Nexus_5X device:bullhead transport_id:24"
    device_info_dict = Device.from_adb_line(device_info_str)
    assert len(device_info_dict.model) > 0 