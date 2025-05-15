import sys
import time
import random
import pyautogui
from .common import CommonController
from .device_detector import DeviceDetector

class EmergencyController:
    def __init__(self):
        self.interrupt_count = 0
        self.common = CommonController()
        self.device_detector = DeviceDetector()

    def handle_interrupt(self) -> bool:
        """
        Handle hunt interruption
        1. Check for low energy and handle if needed
        2. Handle any cancel buttons
        3. If no low energy or cancel buttons, click center of game window
        4. Check if window position/size has changed
        5. Return True if should retry, False if should exit
        """
        print("\n处理中断...")
        
        # Check for low energy
        low_energy_handled = self.handle_low_energy()
        
        # Handle any cancel buttons
        cancel_handled = self.handle_cancel_buttons()
        
        # If no low energy or cancel buttons were handled, click center
        if not low_energy_handled and not cancel_handled:
            center = self.device_detector.get_window_center()
            if center:
                self.common._mouse.move_to(center['x'], center['y'])
                time.sleep(random.uniform(0.5, 1))
                pyautogui.click()
        
        # Check if window position/size has changed
        current_window = self.device_detector._get_window_info()
        cached_window = self.device_detector._window_info
        
        if current_window and cached_window:
            current_pos = current_window["window"]["position"]
            current_size = current_window["window"]["size"]
            cached_pos = cached_window["window"]["position"]
            cached_size = cached_window["window"]["size"]
            
            if (current_pos["x"] != cached_pos["x"] or 
                current_pos["y"] != cached_pos["y"] or 
                current_size["width"] != cached_size["width"] or 
                current_size["height"] != cached_size["height"]):
                
                print("检测到游戏窗口位置或尺寸发生变化")
                self.common.clear_cache()
                self.device_detector._window_info = None
        
        # Increment interrupt counter
        self.interrupt_count += 1
        
        if self.interrupt_count >= 5:
            print("连续中断5次，退出程序")
            sys.exit(1)
            
        print(f"中断恢复完成，当前中断次数: {self.interrupt_count}")
        return True
    
    def handle_cancel_buttons(self, max_attempts: int = 5) -> None:
        """
        处理可能出现的多个 cancel 按钮，最多处理 max_attempts 次
        
        Args:
            max_attempts: 最大尝试次数，默认5次
        """
        attempts = 0
        while attempts < max_attempts:
            # 查找 cancel 按钮
            cancel_data1 = self.common.find_icon("cancel")
            cancel_data2 = self.common.find_icon("cancel2")
            
            # 如果两个按钮都没找到，退出循环
            if cancel_data1 is None and cancel_data2 is None:
                break
                
            # 优先使用 cancel_data1，如果为空则使用 cancel_data2
            cancel_data = cancel_data1 if cancel_data1 is not None else cancel_data2
            
            # 找到任意一个 cancel 按钮，快速点击
            self.common.quick_click_center(cancel_data)
            
            # 等待一小段时间，让界面响应
            time.sleep(0.5)
            
            attempts += 1
            
        if attempts > 0:
            print(f"已处理 {attempts} 个 cancel 按钮")
   
            
    def handle_low_energy(self) -> None:
        """
        处理低能量情况
        1. 检查是否存在 replenish 按钮
        2. 如果存在，先检查 claim 按钮
        3. 如果找到 claim，点击一次后处理可能的 cancel 按钮
        4. 如果没有 claim，检查 use 按钮
        5. 如果找到 use，点击10次后处理可能的 cancel 按钮
        """
        # 首先检查是否存在 replenish 按钮
        replenish_data = self.common.find_icon("replenish")
        if replenish_data is None:
            print("未找到 replenish 按钮，无需处理低能量")
            return False
            
        print("检测到低能量状态")
        
        # 检查是否存在 claim 按钮
        if self.common.quick_click_icon("claim3"):
            time.sleep(random.uniform(0.5, 1))  # 等待界面响应
            self.handle_cancel_buttons()
            return True
        
        time.sleep(random.uniform(1, 2))    
        # 如果没有 claim 按钮，检查 use 按钮
        if self.common.quick_click_icon("use", random.randint(6, 12)):
            time.sleep(random.uniform(1, 2))  # 等待界面响应
            self.handle_cancel_buttons()
            return True
            
        print("未找到 claim 或 use 按钮， 说明已经耗尽所有能量， 程序退出")
        self.handle_cancel_buttons()

        sys.exit(1)