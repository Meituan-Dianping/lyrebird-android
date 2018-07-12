#coding=utf-8

from lyrebird_android.android_helper import Device
import lyrebird_android.android_helper as ah
from unittest import TestCase
import unittest, os


class TestAndroidHelper(TestCase):

    def test_anr_checker(self):
        ANR_TEST_DATA = [
        "03-15 17:16:06.049 864 2787 I WindowManager: Input event dispatching timed out sending to com.example.lee.test/com.example.lee.test.MainActivity. Reason: Waiting to send non-key event because the touched window has not finished processing certain input events that were delivered to it over 500.0ms ago. Wait queue length: 32. Wait queue head age: 5736.5ms.",
        "03-15 17:16:09.190 864 877 E ActivityManager: ANR in com.example.lee.test (com.example.lee.test/.MainActivity)",
        "03-15 17:16:09.190 864 877 E ActivityManager: PID: 16384",
        "03-15 17:16:09.190 864 877 E ActivityManager: Reason: Input dispatching timed out (Waiting to send non-key event because the touched window has not finished processing certain input events that were delivered to it over 500.0ms ago. Wait queue length: 32. Wait queue head age: 5736.5ms.)"
                ]
        ah.check_android_home()
        d = Device('192.168.56.101:5555')

        for line in ANR_TEST_DATA:
            Device.anr_checker(d, line)
        self.assertTrue(os.path.exists(str(d.anr_file)), 'Traces.txt NOT FOUND!')

    def test_crash_checker(self):
        CRASH_TEST_DATA = [
            "--------- beginning of crash",
            "03-15 11:38:27.668 11593 11593 E AndroidRuntime: FATAL EXCEPTION: main",
            "03-15 11:38:27.668 11593 11593 E AndroidRuntime: Process: com.example.lee.test, PID: 11593",
            "03-15 11:38:27.668 11593 11593 E AndroidRuntime: java.lang.IllegalStateException: Could not execute method for android:onClick",
            "03-15 11:38:27.677 864 3838 W ActivityManager: Force finishing activity com.example.lee.test/.MainActivity"
        ]
        d = Device('192.168.56.101:5555')
        for line in CRASH_TEST_DATA:
            Device.crash_checker(d, line)
        self.assertTrue(len(d._crash_file_list), 'Crash log NOT CREATE!')

if __name__ == '__main__':
    unittest.main()