from typing import Optional, Dict, Any
from ..cache.cache import Cache
import json
import os
import random
import numpy as np
import math
import pyautogui
import time
from .mouse_controller import MouseController
from .device_detector import DeviceDetector
from .image_processor import ImageProcessor


class CommonController:
    def __init__(self):
        self._image_processor = ImageProcessor()
        self.device_detector = DeviceDetector()
        self._last_click_pos = None  # 记录上次点击的位置
        self._cache = Cache(cache_dir="temp/cache/icons")
        self._cache_icons = self._load_cache_config()
        self.max_troops = 2 # 配置最多出动的打野部队数量
        self._mouse = MouseController()
      
    def _load_cache_config(self) -> list:
        """
        从配置文件加载需要缓存的图标列表
        
        Returns:
            list: 需要缓存的图标列表
        """
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('cache_icons', [])
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return []
    
    def find_icon(self, icon_name: str, threshold: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        查找图标，根据配置决定是否使用缓存
        
        Args:
            icon_name (str): 图标名称
            threshold (float): 匹配阈值，范围0-1，越大要求匹配度越高
            
        Returns:
            Optional[Dict[str, Any]]: 图标信息，如果未找到则返回None
        """
        # 如果图标在缓存列表中，使用缓存
        if icon_name in self._cache_icons:
            # 构建缓存键
            cache_key = f"icon_{icon_name}_{threshold}"
            
            # 尝试从缓存中获取
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 缓存中不存在，使用图像处理器查找
            result = self._image_processor.find_icon(icon_name, threshold)
            
            # 如果找到图标，存入缓存
            if result is not None:
                self._cache.set(cache_key, result)
            
            return result
            
        # 默认不使用缓存
        return self._image_processor.find_icon(icon_name, threshold)

    def click_icon(self, icon_data: Dict) -> None:
        """
        根据图标位置信息，使用正态分布生成随机点击位置并执行点击
        
        Args:
            icon_data: 图标位置信息字典，格式如下：
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
        """
        # 获取位置信息
        pos = icon_data["position"]
        center = icon_data["center"]
        
        # 计算区域边界
        left = pos["x"]
        right = pos["x"] + pos["width"]
        top = pos["y"]
        bottom = pos["y"] + pos["height"]
        
        # 计算标准差，使用区域尺寸的1/4作为标准差
        # 这样大约95%的点会落在中心区域
        std_x = pos["width"] / 4
        std_y = pos["height"] / 4
        
        # 使用正态分布生成随机位置
        # 生成多个候选点，选择最接近中心的一个
        num_candidates = 5
        candidates = []
        
        for _ in range(num_candidates):
            # 使用正态分布生成随机偏移
            offset_x = int(np.random.normal(0, std_x))
            offset_y = int(np.random.normal(0, std_y))
            
            # 计算候选点坐标
            candidate_x = center["x"] + offset_x
            candidate_y = center["y"] + offset_y
            
            # 确保点在区域内
            candidate_x = max(left, min(right, candidate_x))
            candidate_y = max(top, min(bottom, candidate_y))
            
            # 计算到中心的距离
            distance = ((candidate_x - center["x"]) ** 2 + 
                       (candidate_y - center["y"]) ** 2) ** 0.5
            
            candidates.append(((candidate_x, candidate_y), distance))
        
        # 选择最接近中心的点
        # 使用softmax函数将距离转换为概率
        distances = np.array([d for _, d in candidates])
        probs = np.exp(-distances) / np.sum(np.exp(-distances))
        
        # 根据概率选择点
        selected_idx = np.random.choice(len(candidates), p=probs)
        click_x, click_y = candidates[selected_idx][0]
        
        # 移动鼠标到目标位置
        self._mouse.move_to(click_x, click_y)
        
        # 添加一个短暂的停顿，模拟人类点击前的犹豫
        time.sleep(random.uniform(0.05, 0.15))
        
        # 执行点击
        pyautogui.click()

    def clear_cache(self) -> None:
        """Clear all cached icons"""
        print("Clearing icon cache...")
        self._cache.clear()
        print("Icon cache cleared successfully")

    def get_troop_count(self) -> str:
        """
        检测当前已出动的部队数量
        
        Returns:
            str: 已出动的部队数量，如果检测失败则返回空字符串
        """
        try:
            # 查找 troop_flag 图标
            troop_flag = self.find_icon("troop_flag")
            if troop_flag is None:
                print("获取已出动部队数量失败")
                return ""
            
            # 获取 troop_flag 的位置信息
            pos = troop_flag["position"]
            
            # 设置数字识别区域
            # 起始点为 troop_flag 的右侧
            region = {
                'top': pos["y"],
                'left': pos["x"] + pos["width"],
                'width': 50,  # 固定宽度
                'height': 25  # 固定高度
            }
            
            # 识别数字并直接返回结果
            return self._image_processor.recognize_number(region)
                
        except Exception as e:
            print(f"Error getting troop count: {str(e)}")
            return ""
    
    def check_troop_status(self) -> int:
        """
        检查当前部队状态
        
        Returns:
            int: 当前出动部队数
        """
        try:
            # 获取当前出动部队数（分数形式）
            troop_fraction = self.get_troop_count()
            # 从分数中提取分子（当前出动部队数）并转换为整数
            current_troops = int(troop_fraction.split('/')[0]) if '/' in troop_fraction else 0
            
            return current_troops
        except Exception as e:
            print(f"Error checking troop status: {str(e)}")
            return 0
        
    def quick_click_center(self, icon_data: dict, need_move: bool = True) -> None:
        """
        在图标中心点半径10像素范围内随机点击
        如果连续调用，只在第一次移动鼠标，后续直接点击
        
        Args:
            icon_data: 图标位置信息字典
            need_move: 是否需要移动鼠标，默认True
        """
        # 获取中心点坐标
        center_x = icon_data["center"]["x"]
        center_y = icon_data["center"]["y"]
        
        # 如果是第一次点击或中心点发生变化，需要重新计算点击位置
        if need_move and (self._last_click_pos is None or 
            self._last_click_pos["center_x"] != center_x or 
            self._last_click_pos["center_y"] != center_y):
            
            # 生成随机角度和距离（距离不超过10像素）
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, 20)
            
            # 计算随机点击位置
            click_x = int(center_x + distance * math.cos(angle))
            click_y = int(center_y + distance * math.sin(angle))
            
            # 移动鼠标到新位置
            self._mouse.move_to(click_x, click_y)
            
            # 缓存位置信息
            self._last_click_pos = {
                "center_x": center_x,
                "center_y": center_y,
                "click_x": click_x,
                "click_y": click_y
            }
        
        # 直接点击，不需要移动鼠标
        pyautogui.click()

    def quick_click_icon(self, icon_name: str, click_times: int = 1, threshold: float = 0.65) -> bool:
        """
        快速多次点击指定图标
        
        Args:
            icon_name: 图标名称
            click_times: 点击次数，默认1次
            threshold: 匹配阈值，默认0.65
            
        Returns:
            bool: 是否成功找到并点击图标
        """
        # 查找图标
        icon_data = self.find_icon(icon_name, threshold)
        if icon_data is None:
            return False
            
        # 将点击次数转换为整数
        print(f"找到图标: {icon_name}，开始点击 {click_times} 次")
        
        # 执行多次点击
        for i in range(click_times):
            # 第一次点击需要移动鼠标，后续直接点击
            self.quick_click_center(icon_data, need_move=(i == 0))
            if i < click_times - 1:  # 最后一次点击后不需要等待
                time.sleep(random.uniform(0.5, 1))  # 随机等待0.15-0.5秒
                
        return True
    

    def wait_for_stagnation(self) -> bool:
        """
        等待并检测stagnation图标或部队数量变化
        
        Returns:
            bool: 是否检测到stagnation图标或部队数量减少
        """
        try:
            while True:
                # 检查stagnation图标
                if self.find_icon('stagnation'):
                    return True
                
                # 检查当前部队数量
                current_troops = self.check_troop_status()
                if current_troops < self.max_troops:
                    print(f"Troop count decreased to {current_troops}, continuing hunt...")
                    return True
                    
                # 随机等待1-3分钟
                wait_time = random.uniform(10, 30)
                print(f"Waiting {wait_time:.1f} seconds before next check...")
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"Error waiting for stagnation: {str(e)}")
            return False

    def calculate_random_position(self) -> tuple[int, int] | None:
         # 获取窗口信息
        window_info = self.device_detector.get_window_info()
        if not window_info:
            print("未找到游戏窗口")
            return None
        
        # 计算可点击区域范围
        start_x = window_info["window"]["position"]["x"] + 300
        start_y = window_info["window"]["position"]["y"] + 300
        area_width = window_info["window"]["size"]["width"] - 600
        area_height = window_info["window"]["size"]["height"] - 600 
        
        if area_width <= 0 or area_height <= 0:
            print("计算得到的可点击区域无效")
            return None
            
        # 生成随机位置
        target_x = random.randint(start_x, start_x + area_width)
        target_y = random.randint(start_y, start_y + area_height)
        
        return (target_x, target_y)
    
    def recognize_number(self, region: dict) -> str:
        return self._image_processor.recognize_number(region)