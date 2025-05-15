import pyautogui
from PIL import Image, ImageOps
import io
import cv2
import numpy as np
import os
import time
from .device_detector import DeviceDetector
import mss
import easyocr
import random

class ImageProcessor:
    def __init__(self):
        self._last_screenshot = None
        self._icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets/icons')
        self._device_detector = DeviceDetector()
        self._ocr_reader = easyocr.Reader(['en'])  # Initialize OCR reader

    def capture_screen(self):
        """
        捕获当前屏幕截图并存储在内存中
        
        Returns:
            PIL.Image: 屏幕截图的PIL Image对象
        """
        # 使用pyautogui捕获屏幕
        screenshot = pyautogui.screenshot()
        # 将截图存储在实例变量中
        self._last_screenshot = screenshot
        return screenshot

    def get_last_screenshot(self):
        """
        获取最后一次截图的PIL Image对象
        
        Returns:
            PIL.Image: 最后一次截图的PIL Image对象，如果没有截图则返回None
        """
        return self._last_screenshot

    def get_last_screenshot_bytes(self):
        """
        获取最后一次截图的字节数据
        
        Returns:
            bytes: 最后一次截图的字节数据，如果没有截图则返回None
        """
        if self._last_screenshot is None:
            return None
        
        # 将PIL Image转换为字节数据
        img_byte_arr = io.BytesIO()
        self._last_screenshot.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def find_icon(self, icon_name, threshold=0.8):
        """
        在屏幕截图中查找指定图标的位置和尺寸，随机返回一个匹配的图标
        
        Args:
            icon_name (str): 图标文件名（不包含扩展名）
            threshold (float): 匹配阈值，范围0-1，越大要求匹配度越高
            
        Returns:
            dict: 包含图标位置和尺寸信息的字典，格式如下：
                {
                    "name": str,  # 图标名称
                    "position": {
                        "x": int,  # 图标左上角x坐标
                        "y": int,  # 图标左上角y坐标
                        "width": int,  # 图标宽度
                        "height": int  # 图标高度
                    },
                    "center": {
                        "x": int,  # 图标中心点x坐标
                        "y": int   # 图标中心点y坐标
                    },
                    "confidence": float  # 匹配度
                }
            如果没有找到匹配的图标，返回None
        """
        
        # 获取最新的屏幕截图
        screen = cv2.cvtColor(np.array(self.capture_screen()), cv2.COLOR_RGB2BGR)
            
        # 构建图标文件路径
        icon_path = os.path.join(self._icons_dir, f"{icon_name}.png")
        if not os.path.exists(icon_path):
            raise FileNotFoundError(f"图标文件不存在: {icon_path}")
            
        # 读取图标
        icon = cv2.imread(icon_path)
        icon_gray = cv2.cvtColor(icon, cv2.COLOR_RGB2BGR)

        # 获取图标尺寸
        icon_height, icon_width = icon.shape[:2]
        
        # 使用模板匹配
        result = cv2.matchTemplate(screen, icon, cv2.TM_CCOEFF_NORMED)


        # 查找所有匹配位置
        locations = np.where(result >= threshold)
        matches = []
        
        # 将匹配位置转换为列表
        for pt in zip(*locations[::-1]):
            # 计算中心点坐标
            center_x = pt[0] + icon_width // 2
            center_y = pt[1] + icon_height // 2
            
            match = {
                "name": os.path.splitext(icon_name)[0],
                "position": {
                    "x": int(pt[0] // 2),  # 除以2适应Retina显示
                    "y": int(pt[1] // 2),
                    "width": int(icon_width // 2),
                    "height": int(icon_height // 2)
                },
                "center": {
                    "x": int(center_x // 2),
                    "y": int(center_y // 2)
                },
                "confidence": float(result[pt[1], pt[0]])
            }
            matches.append(match)
            
        # 按置信度从高到低排序
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        print(f"======{icon_name} confidence=====", matches)
        # 如果有匹配的图标，返回置信度最高的一个
        if matches:
            return matches[0]
            return None

    def recognize_number(self, region: dict) -> str:
        """
        识别指定区域的数字
        
        Args:
            region (dict): 区域信息，格式为：
                {
                    'top': int,    # 区域顶部y坐标
                    'left': int,   # 区域左侧x坐标
                    'width': int,  # 区域宽度
                    'height': int  # 区域高度
                }
                
        Returns:
            str: 识别到的数字字符串，如果识别失败则返回空字符串
        """
        try:
            # 使用mss截取指定区域
            with mss.mss() as sct:
                screenshot = sct.grab(region)
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
            
            # 保存原始截图
            img.save('temp/original.png')
            
            # 图像增强处理
            img = img.resize((img.width * 10, img.height * 10), Image.LANCZOS)  # 放大图像
            img = ImageOps.grayscale(img)  # 转换为灰度图
            
            # 保存放大和灰度处理后的图像
            img.save('temp/enhanced.png')
            
            # 转为OpenCV格式处理二值化
            img_cv = np.array(img)
            _, binary = cv2.threshold(img_cv, 150, 255, cv2.THRESH_BINARY)
            
            # 保存二值化后的图像
            cv2.imwrite('temp/binary.png', binary)
            
            # 使用easyocr识别数字
            results = self._ocr_reader.readtext(binary)

            # 提取识别结果
            result = ""
            if results:
                result = results[0][1]
            
            # 删除临时文件
            # try:
            #     os.remove('temp/original.png')
            #     os.remove('temp/enhanced.png')
            #     os.remove('temp/binary.png')
            # except Exception as e:
            #     print(f"Error deleting temporary files: {str(e)}")
            
            return result
            
        except Exception as e:
            print(f"Error recognizing number: {str(e)}")
            return ""