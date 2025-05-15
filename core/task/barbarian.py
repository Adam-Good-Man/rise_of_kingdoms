
import time
import random
import pyautogui
from core.utils.index import Utils

class BarbarianTask:
    def __init__(self):
        self.hunt_count = 0  # Initialize hunt counter
        self.utils = Utils()
    def click_search_icon(self) -> bool:
        """Step 1-2: Click search icon or map then search icon"""
        if self.utils.common.quick_click_icon("search_icon",  1, 0.8):
            return True
            
        if self.utils.common.quick_click_icon("map"):
            time.sleep(random.uniform(0.5, 1))  # Wait for map interface to load
            if self.utils.common.quick_click_icon("search_icon", 1, 0.8):
                return True
                
        return False

    def adjust_barbarian_level(self) -> bool:
        """Step 3: Randomly click add/minus buttons if adjustment needed"""

        if random.uniform(0, 10) > 7:
            return True

        total_clicks = random.randint(0, 3)
        if total_clicks == 0:
            return True
            
        mode = random.random()
        if mode < 0.3:  # 30% chance to only click add
            add_clicks = total_clicks
            minus_clicks = 0
        elif mode < 0.6:  # 30% chance to only click minus
            add_clicks = 0
            minus_clicks = total_clicks
        else:  # 40% chance to mix clicks
            add_clicks = random.randint(0, total_clicks)
            minus_clicks = total_clicks - add_clicks
        
        print(f"调整野蛮人等级: 加{add_clicks}次，减{minus_clicks}次")
        if add_clicks > 0:
            if not self.utils.common.quick_click_icon("add", click_times=add_clicks):
                return False
            time.sleep(random.uniform(0.5, 1))
        
        if minus_clicks > 0:
            if not self.utils.common.quick_click_icon("minus", click_times=minus_clicks):
                return False
            time.sleep(random.uniform(0.5, 1))
            
        return True

    def click_search_button(self) -> bool:
        """Step 4: Click search button"""
        time.sleep(random.uniform(0.5, 1))
        if not self.utils.common.quick_click_icon("search"):
            return False
        return True

    def click_center(self) -> bool:
        """Step 5: Move to window center and click"""
        time.sleep(random.uniform(0.5, 1))
        center = self.utils.device_detector.get_window_center()
        if not center:
            return False
        
        mouse = self.utils.mouse
        mouse.move_to(center['x'], center['y'])
        time.sleep(random.uniform(0.5, 1))
        pyautogui.click()
        return True

    def click_attack_button(self) -> bool:
        """Step 6: Find and click attack button"""
        time.sleep(random.uniform(0.5, 1))
        if not self.utils.common.quick_click_icon("attack"):
            return False
        return True
    
    def go_back(self) -> bool:
        """Step 7: Check for stagnation and march button"""
        center = self.utils.device_detector.get_window_center()
        if center:
            self.utils.mouse.move_to(center['x'], center['y'])
            time.sleep(random.uniform(0.5, 1))
            pyautogui.click()
        else:
            return False
        time.sleep(random.uniform(0.5, 1))
        if not self.utils.common.quick_click_icon("stagnation", 1,  0.65):
            return False
        
        time.sleep(random.uniform(0.5, 1))
        if not self.utils.common.quick_click_icon("back"):
            return False
        
        return True
    
    def handle_stagnation(self) -> bool:
        """Step 7: Check for stagnation and march button"""
        time.sleep(random.uniform(0.5, 1))
        stagnation_data = self.utils.common.find_icon("stagnation", threshold=0.65)
        if stagnation_data:
            self.utils.common.quick_click_icon("stagnation", 1,  0.65)
            time.sleep(random.uniform(0.5, 1))
            # 如果检测到危险战斗，则点击返回按钮
            hard_battle_data = self.utils.common.find_icon("hard_battle", threshold=0.7)
            if not hard_battle_data:
                if self.utils.common.quick_click_icon("march2"):
                    return True
            else:
                return self.go_back()
        return False

    def click_new_troop(self) -> bool:
        """Step 8: Click new troop button"""
        time.sleep(random.uniform(1, 2))
        if not self.utils.common.quick_click_icon("new_troop"):
            return False
        return True

    def click_march_button(self) -> bool:
        """Step 9: Find and click march button"""
        time.sleep(random.uniform(0.5, 1))
        if not self.utils.common.quick_click_icon("march"):
            return False
        return True

    def check_dangerous_battle(self) -> bool:
        """
        检查是否存在自杀任务或困难战斗
        
        Returns:
            bool: 如果检测到危险战斗返回True，否则返回False
        """
        # 检查自杀任务
        if self.utils.common.quick_click_icon("suicide_mission"):
            print("检测到自杀任务，取消并重新开始")
            self.utils.emergency.handle_cancel_buttons()
            return True
            
        # 检查困难战斗
        if self.utils.common.quick_click_icon("hard_battle"):
            print("检测到困难战斗，取消并重新开始")
            self.utils.emergency.handle_cancel_buttons()
            return True
            
        return False

    def click_hold_button(self) -> bool:
        """
        寻找并点击 hold 按钮
        基于 attack 按钮的位置计算 hold 按钮的位置：
        - x = attack_x - 10
        - y = attack_y + attack_height + 20
        
        Returns:
            bool: 是否成功点击 hold 按钮
        """
        # 首先找到 attack 按钮
        attack_data = self.utils.common.find_icon("attack")
        if not attack_data:
            print("未找到 attack 按钮，无法定位 hold 按钮")
            return False
        
        # 计算 hold 按钮的位置
        hold_x = attack_data["position"]["x"] - 5
        hold_y = attack_data["position"]["y"] + attack_data["position"]["height"] + 20
        
        # 移动鼠标并点击
        self.utils.mouse.move_to(hold_x, hold_y)
        time.sleep(random.uniform(0.5, 1))  # 短暂停顿
        pyautogui.click()
        
        print("已点击 hold 按钮")
        return True

    def scroll_to_find_barbarian(self) -> bool:
        """
        通过滚动鼠标滚轮寻找野蛮人
        1. 随机滚动距离（30-50）
        2. 检查是否存在野蛮人（ax图标）,  1, 0.7
        3. 如果找到则点击并继续后续步骤
        
        """
        print("\n开始滚动寻找野蛮人...")

        map_icon_data = self.utils.common.find_icon("map_icon")
        if map_icon_data is None:
            if self.utils.common.quick_click_icon("city"):
                time.sleep(random.uniform(1, 2))

        # 先将鼠标移动到窗口中心
        center = self.utils.device_detector.get_window_center()
        if not center:
            print("无法获取窗口中心点")
            return False
            
        self.utils.mouse.move_to(center['x'], center['y'])
        time.sleep(random.uniform(0.5, 1))
        self.utils.mouse.click_at(center['x'], center['y'])
        time.sleep(random.uniform(0.5, 1))
        
        max_attempts = 12  # 最大尝试次数
        for attempt in range(max_attempts):
            random_position = self.utils.common.calculate_random_position()
            if not random_position:
                print("无法获取随机位置")
                return False
            
            self.utils.mouse.move_to(random_position[0], random_position[1])
            time.sleep(random.uniform(0.5, 1))
            # 随机生成滚动距离
            scroll_distance = random.randint(20, 50)
            
            # 执行滚动
            self.utils.mouse.scroll_wheel(scroll_distance, 'up')
            time.sleep(random.uniform(0.2 , 0.6))  # 等待界面稳定
            
            # 检查是否存在野蛮人
            if self.utils.common.quick_click_icon("ax", 1, 0.5):
                time.sleep(random.uniform(0.5, 1))
                # 点击窗口中心点
                center = self.utils.device_detector.get_window_center()
                if not center:
                    return False
                
                self.utils.mouse.move_to(center['x'], center['y'])
                time.sleep(random.uniform(0.5, 1))
                pyautogui.click()
                time.sleep(random.uniform(0.5, 1))
                
                # 如果需要点击 hold 按钮
                # if random.uniform(1, 30) >= 28:
                #     print("点击 hold 按钮")
                #     if not self.click_hold_button():
                #         if not self.utils.emergency.handle_interrupt():
                #             return False
                #     time.sleep(random.uniform(0.5, 1))
                
                # 检查attack按钮
                if not self.click_attack_button():
                    return False
                
                # 执行后续步骤（复用normal_hunt中的步骤）
                time.sleep(random.uniform(1, 2))
                return self._execute_post_attack_steps()
            
            print("未找到野蛮人，继续滚动...")
        
        print("达到最大尝试次数，未找到野蛮人")
        print("检查是否中断处理")
        self.utils.emergency.handle_interrupt()
        
        return False

    def _execute_post_attack_steps(self) -> bool:
        """
        执行攻击后的步骤
        检查new_troop和stagnation按钮的存在情况：
        1. 如果两个按钮都存在，随机选择一个流程执行
        2. 如果只有一个按钮存在，执行对应的流程
        3. 如果都不存在，返回False
        """
        # 检查按钮是否存在
        new_troop_data = self.utils.common.find_icon("new_troop")
        new_troop_exists = new_troop_data is not None
        
        stagnation_data = self.utils.common.find_icon("stagnation", 0.65)
        stagnation_exists = stagnation_data is not None
        
        # 如果两个按钮都不存在
        if not new_troop_exists and not stagnation_exists:
            return False
            
        # 如果只有一个按钮存在，执行对应的流程
        print(f"new_troop_exists: {new_troop_exists}, stagnation_exists: {stagnation_exists}")
        if new_troop_exists and not stagnation_exists:
            if not self.click_new_troop():
                return False
            print("已点击新部队")

            time.sleep(random.uniform(1, 2))
            if self.check_dangerous_battle():
                wait_time = random.uniform(10, 30)
                print(f"检测到危险战斗，等待 {wait_time:.1f} 秒后继续...")
                time.sleep(wait_time)
                
            time.sleep(random.uniform(1,2))
            print("点击行军按钮")
            if not self.click_march_button():
                print("点击行军按钮失败")
                if not self.utils.emergency.handle_interrupt():
                    return False
                return False
                
        elif stagnation_exists and not new_troop_exists:
            if not self.handle_stagnation():
                return False
            time.sleep(random.uniform(1, 2))
                
        else:  # 两个按钮都存在，优先执行停滞流程
            if not self.handle_stagnation():
                time.sleep(random.uniform(1, 2))
                if self.check_dangerous_battle():
                    print("检测到危险战斗")
                wait_time = random.uniform(10, 30)
                if not self.click_new_troop():
                    time.sleep(random.uniform(1, 2))
                    if self.check_dangerous_battle():
                        print("检测到危险战斗")
                        time.sleep(random.uniform(10, 30))

        # 重置中断计数器
        self.utils.emergency.interrupt_count = 0
        return True

    def normal_hunt(self) -> None:
        """
        Execute normal hunting process by calling each step in sequence
        """
        self.hunt_count += 1
        print(f"\n开始第 {self.hunt_count} 轮狩猎")

        # Execute each step in sequence
        steps = [
            (self.click_search_icon, "点击搜索图标"),
            (self.adjust_barbarian_level, "调整野蛮人等级"),
            (self.click_search_button, "点击搜索按钮"),
            (self.click_center, "点击中心点"),
        ]

        # Execute initial steps
        for step_func, step_name in steps:
            print(f"\n执行步骤: {step_name}")
            if not step_func():
                if not self.utils.emergency.handle_interrupt():
                    return
                return  False
            time.sleep(random.uniform(0.5, 1))

        # 如果需要点击 hold 按钮
        
        # if random.uniform(1, 30) >= 28:
        #     print("\n执行步骤: 点击 hold 按钮")
        #     self.click_hold_button()
        #     time.sleep(random.uniform(0.5, 1))

        # 继续执行后续步骤
        if not self.click_attack_button():
            return  False
        
        time.sleep(random.uniform(1 , 2))
        # 执行后续步骤
        return self._execute_post_attack_steps()
    