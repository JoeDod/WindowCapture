import mss
import win32gui, win32ui, win32con
import cv2 as cv
import numpy as np
import time


class WindowCapture:

    def __init__(self, window_title):
        self.sct = mss.mss()
        self.win32gui = win32gui
        self.win32ui = win32ui
        self.win32con = win32con
        self.hwnd = self.win32gui.FindWindow(None, window_title)
        if not self.hwnd:
            raise ValueError(f"窗口 '{self.window_title}' 未找到")

    def capture_screen(self, use_background=True):
        """
        默认使用 Win32 API 进行后台截图
        """
        if use_background:
            return self._capture_background()
        return self.sct.grab(self.win32gui.GetWindowRect(self.hwnd))

    def _capture_background(self):
        left, top, right, bottom = self.win32gui.GetWindowRect(self.hwnd)
        width = right - left
        height = bottom - top

        # 检查窗口句柄有效性
        if not self.hwnd:
            raise ValueError(f"窗口 '{self.window_title}' 的句柄无效")

        # 获取设备上下文
        hWndDC = self.win32gui.GetWindowDC(self.hwnd)
        mfcDC = self.win32ui.CreateDCFromHandle(hWndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitmap = self.win32ui.CreateBitmap()
        saveBitmap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitmap)

        # 截图
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0),
                      self.win32con.SRCCOPY)
        bitmap_data = saveBitmap.GetBitmapBits(True)

        # 释放资源
        if saveBitmap:
            self.win32gui.DeleteObject(saveBitmap.GetHandle())
        if saveDC:
            saveDC.DeleteDC()
        if mfcDC:
            mfcDC.DeleteDC()
        if hWndDC:
            self.win32gui.ReleaseDC(self.hwnd, hWndDC)

        # 转换为 OpenCV 格式
        image = np.frombuffer(bitmap_data, dtype='uint8')
        image.shape = (height, width, 4)
        return cv.cvtColor(image, cv.COLOR_BGRA2BGR)

    def display_window(self):
        frame_delay = 1 / 60
        while True:
            frame = self.capture_screen()
            cv.imshow("", frame)
            if cv.waitKey(1) & 0xFF == ord("q"):
                cv.destroyAllWindows()
                break
            time.sleep(frame_delay)

    def save_screenshot(self, file_path):
        cv.imwrite(file_path, self.capture_screen())


if __name__ == "__main__":
    window_capture = WindowCapture('原神')
    window_capture.display_window()
