import platform
import subprocess
import pyautogui
from typing import Optional, Dict
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID
)

class DeviceDetector:
    def __init__(self):
        self._scale_factor = self._detect_scale_factor()
        self._window_info = None
        self._target_app_name = "RiseOfKingdoms"  # 目标应用名称

    def _detect_scale_factor(self):
        """
        检测设备的缩放因子
        
        Returns:
            float: 设备的缩放因子
        """
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return 2.0
        elif system == "Windows":
            # Windows 的缩放因子检测可以在这里添加
            return 1.0
        else:
            # Linux 或其他系统
            return 1.0

    def get_scale_factor(self):
        """
        获取设备的缩放因子
        
        Returns:
            float: 设备的缩放因子
        """
        return self._scale_factor

    def adjust_coordinates(self, x, y):
        """
        调整坐标值
        
        Args:
            x (int): 原始x坐标
            y (int): 原始y坐标
            
        Returns:
            tuple: (调整后的x坐标, 调整后的y坐标)
        """
        scale = self.get_scale_factor()
        return int(x / scale), int(y / scale)

    def adjust_dimensions(self, width, height):
        """
        调整尺寸值
        
        Args:
            width (int): 原始宽度
            height (int): 原始高度
            
        Returns:
            tuple: (调整后的宽度, 调整后的高度)
        """
        scale = self.get_scale_factor()
        return int(width / scale), int(height / scale) 
    
    def _get_window_info(self) -> Optional[Dict[str, int]]:
        """
        获取 Rise of Kingdoms 游戏窗口的位置和尺寸信息（内部方法）
        
        Returns:
            Optional[Dict[str, int]]: 包含窗口位置、尺寸和中心点信息的字典
        """
        # 获取所有在屏幕上的窗口
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        
        for window in window_list:
            app_name = window.get('kCGWindowOwnerName', '')
            if app_name != self._target_app_name:
                continue  # 跳过不是目标应用的窗口
            
            bounds = window.get('kCGWindowBounds', {})
            
            # 提取窗口位置和尺寸信息
            x = int(bounds.get('X', 0))
            y = int(bounds.get('Y', 0))
            width = int(bounds.get('Width', 0))
            height = int(bounds.get('Height', 0))
            
            # 计算窗口中心点
            center_x = x + width // 2
            center_y = y + height // 2
            
            # 构建窗口信息
            return {
                "window": {
                    "position": {
                        "x": x,
                        "y": y
                    },
                    "size": {
                        "width": width,
                        "height": height
                    },
                    "center": {
                        "x": center_x,
                        "y": center_y
                    }
                }
            }
        
        return None  # 未找到游戏窗口
    
    def get_window_info(self, use_cache: bool = True) -> Optional[Dict[str, int]]:
        """
        获取 Rise of Kingdoms 游戏窗口的位置和尺寸信息
        
        Args:
            use_cache: 是否使用缓存，默认为True
            
        Returns:
            Optional[Dict[str, int]]: 包含窗口位置、尺寸和中心点信息的字典，格式为：
                {
                    "window": {
                        "position": {
                            "x": int,  # 窗口左上角x坐标
                            "y": int   # 窗口左上角y坐标
                        },
                        "size": {
                            "width": int,   # 窗口宽度
                            "height": int   # 窗口高度
                        },
                        "center": {
                            "x": int,  # 窗口中心点x坐标
                            "y": int   # 窗口中心点y坐标
                        }
                    }
                }
            如果未找到游戏窗口，返回 None
        """
        # 如果使用缓存且缓存存在，直接返回缓存的信息
        if use_cache and self._window_info is not None:
            return self._window_info
            
        # 不使用缓存或缓存不存在，重新获取窗口信息
        window_info = self._get_window_info()
        
        # 如果使用缓存，更新缓存
        if use_cache:
            self._window_info = window_info
            
        return window_info
    
    def get_window_center(self) -> Optional[Dict[str, int]]:
        """
        获取游戏窗口中心点坐标
        
        Returns:
            Optional[Dict[str, int]]: 包含窗口中心点坐标的字典，格式为：
                {
                    'x': int,  # 中心点x坐标
                    'y': int   # 中心点y坐标
                }
            如果未找到游戏窗口，返回 None
        """
        window_info = self.get_window_info()
        if window_info is None:
            return None
            
        return {
            'x': window_info["window"]["center"]["x"],
            'y': window_info["window"]["center"]["y"]
        }
    