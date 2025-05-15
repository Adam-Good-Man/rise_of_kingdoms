import pyautogui
import random
import math
import time
from typing import Tuple, List
import numpy as np

class MouseController:
    def __init__(self):
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.02  # 进一步减少操作间隔时间
        
        # 移动参数
        self._min_duration = 0.1  # 最小移动时间
        self._max_duration = 0.4  # 最大移动时间
        self._control_points = 4  # 控制点数量
        
        # 移动模式
        self._move_patterns = [
            self._direct_move,      # 直接移动
            self._curved_move,      # 曲线移动
            self._stutter_move,     # 停顿移动
            self._zigzag_move       # 不规则移动
        ]
    
    def _get_current_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        return pyautogui.position()
    
    def _generate_control_points(self, start: Tuple[int, int], end: Tuple[int, int], pattern: str = 'curved') -> List[Tuple[int, int]]:
        """
        生成贝塞尔曲线的控制点
        
        Args:
            start: 起始点坐标
            end: 终点坐标
            pattern: 移动模式
            
        Returns:
            List[Tuple[int, int]]: 控制点列表
        """
        points = [start]
        
        # 计算起点和终点之间的距离
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        # 根据距离调整控制点的范围
        max_offset = min(distance * 0.3, 100)  # 减小控制点最大偏移量，使路径更直接
        
        if pattern == 'direct':
            # 直接移动模式：控制点接近直线
            points.append(end)
            return points
            
        elif pattern == 'curved':
            # 曲线移动模式：生成平滑的曲线
            for _ in range(self._control_points - 2):
                t = random.random()
                base_x = start[0] + (end[0] - start[0]) * t
                base_y = start[1] + (end[1] - start[1]) * t
                
                # 添加较小的随机偏移
                offset_x = random.uniform(-max_offset, max_offset)
                offset_y = random.uniform(-max_offset, max_offset)
                
                points.append((int(base_x + offset_x), int(base_y + offset_y)))
                
        elif pattern == 'zigzag':
            # 不规则移动模式：生成锯齿状路径
            steps = random.randint(2, 4)  # 减少锯齿数量
            for i in range(1, steps):
                t = i / steps
                base_x = start[0] + (end[0] - start[0]) * t
                base_y = start[1] + (end[1] - start[1]) * t
                
                # 添加交替的偏移
                offset_x = max_offset if i % 2 == 0 else -max_offset
                offset_y = max_offset if i % 2 == 1 else -max_offset
                
                points.append((int(base_x + offset_x), int(base_y + offset_y)))
        
        points.append(end)
        return points
    
    def _bezier_curve(self, points: List[Tuple[int, int]], steps: int) -> List[Tuple[int, int]]:
        """
        生成贝塞尔曲线路径
        
        Args:
            points: 控制点列表
            steps: 路径点数量
            
        Returns:
            List[Tuple[int, int]]: 路径点列表
        """
        n = len(points) - 1
        path = []
        
        for t in np.linspace(0, 1, steps):
            x = y = 0
            for i, point in enumerate(points):
                coef = math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
                x += point[0] * coef
                y += point[1] * coef
            path.append((int(x), int(y)))
        
        return path
    
    def _add_human_noise(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        添加人类行为噪声
        
        Args:
            path: 原始路径点列表
            
        Returns:
            List[Tuple[int, int]]: 添加噪声后的路径点列表
        """
        noisy_path = []
        for point in path:
            # 减小噪声范围
            noise_x = random.uniform(-2, 2)
            noise_y = random.uniform(-2, 2)
            noisy_path.append((int(point[0] + noise_x), int(point[1] + noise_y)))
        return noisy_path
    
    def _direct_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], duration: float) -> None:
        """直接移动模式"""
        control_points = self._generate_control_points(start_pos, end_pos, 'direct')
        steps = max(int(duration * 50), 10)  # 增加步数，使移动更流畅
        path = self._bezier_curve(control_points, steps)
        path = self._add_human_noise(path)
        
        step_duration = duration / len(path)
        for point in path:
            pyautogui.moveTo(point[0], point[1])
            time.sleep(step_duration)
    
    def _curved_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], duration: float) -> None:
        """曲线移动模式"""
        control_points = self._generate_control_points(start_pos, end_pos, 'curved')
        steps = max(int(duration * 60), 15)  # 增加步数，使移动更流畅
        path = self._bezier_curve(control_points, steps)
        path = self._add_human_noise(path)
        
        step_duration = duration / len(path)
        for point in path:
            pyautogui.moveTo(point[0], point[1])
            time.sleep(step_duration)
    
    def _stutter_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], duration: float) -> None:
        """停顿移动模式"""
        # 先移动到中间点
        mid_x = (start_pos[0] + end_pos[0]) // 2
        mid_y = (start_pos[1] + end_pos[1]) // 2
        mid_pos = (mid_x, mid_y)
        
        # 第一段移动
        self._curved_move(start_pos, mid_pos, duration * 0.4)
        
        # 缩短停顿时间
        time.sleep(random.uniform(0.05, 0.15))
        
        # 第二段移动
        self._curved_move(mid_pos, end_pos, duration * 0.6)
    
    def _zigzag_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], duration: float) -> None:
        """不规则移动模式"""
        control_points = self._generate_control_points(start_pos, end_pos, 'zigzag')
        steps = max(int(duration * 70), 20)  # 增加步数，使移动更流畅
        path = self._bezier_curve(control_points, steps)
        path = self._add_human_noise(path)
        
        step_duration = duration / len(path)
        for point in path:
            pyautogui.moveTo(point[0], point[1])
            time.sleep(step_duration)
    
    def move_to(self, x: int, y: int) -> None:
        """
        移动鼠标到指定位置
        
        Args:
            x: 目标x坐标
            y: 目标y坐标
        """
        # 获取当前鼠标位置
        start_pos = self._get_current_position()
        end_pos = (x, y)
        
        # 随机生成移动时间（0.1-0.3秒）
        duration = random.uniform(0.1, 0.3)
        
        # 随机选择移动模式
        move_pattern = random.choice(self._move_patterns)
        move_pattern(start_pos, end_pos, duration)
    
    def click_at(self, x: int, y: int) -> None:
        """
        移动鼠标到指定位置并点击
        
        Args:
            x: 目标x坐标
            y: 目标y坐标
            duration: 移动持续时间（秒），如果为None则随机生成
        """
        self.move_to(x, y)
        # 添加一个短暂的停顿，模拟人类点击前的犹豫
        time.sleep(random.uniform(0.5, 1))
        pyautogui.click()

    def scroll_wheel(self, distance: int, direction: str = 'down') -> None:
        """
        控制鼠标滚轮滚动一次
        
        Args:
            distance: 滚动距离（像素）
            direction: 滚动方向，'up' 或 'down'，默认为 'down'
        """
        # 确定滚动方向
        scroll_amount = -distance if direction.lower() == 'up' else distance
        
        # 执行滚动
        pyautogui.scroll(scroll_amount) 
        
    def handle_scroll_wheel(self) -> bool:
        """
        滚动鼠标滚轮
        """
        self.scroll_wheel(30, 'up')