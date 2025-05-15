from typing import Optional
import time
import random
import math
import pyautogui
from core.utils.index import Utils

class CommonTask:
    def __init__(self):
        self.utils = Utils()
    
    def get_reward_number(self) -> Optional[str]:
        """
        检测并识别奖励区域的数值
        
        Returns:
            Optional[str]: 识别到的数值，如果未找到或识别失败则返回 None
        """
        # 查找 rewards 图标
        rewards_data = self.utils.common.find_icon("rewards")
        if not rewards_data:
            print("未找到 rewards 图标")
            return None
            
        # 计算目标区域的位置和尺寸
        target_x = rewards_data["position"]["x"] + rewards_data["position"]["width"] // 2
        target_y = rewards_data["position"]["y"] - 30
        target_width = 60
        target_height = 60
        
        print(f"计算得到奖励数值区域: x={target_x}, y={target_y}, width={target_width}, height={target_height}")
        
        # 调用 recognize_number 识别该区域的数值
        number = self.utils.common.recognize_number({
            "top": target_y, 
            "left": target_x, 
            "width": target_width, 
            "height": target_height
        })
        if number is not None:
            print(f"识别到奖励数值: {number}")
        else:
            print("未能识别到奖励数值")
            
        return number

    def claim_rewards(self) -> bool:
        """
        领取奖励
        1. 获取奖励数量
        2. 如果数量大于0，点击rewards图标
        3. 在新界面中点击claim按钮指定次数
        4. 处理可能的cancel按钮
        
        Returns:
            bool: 是否成功完成领取过程
        """
        # 获取奖励数量
        reward_number = self.get_reward_number()
        if reward_number is None:
            print("未能识别到奖励数量，跳过领取")
            return False
            
        try:
            reward_count = int(reward_number)
        except ValueError:
            print(f"奖励数量格式错误: {reward_number}")
            return False
            
        if reward_count <= 0:
            print("奖励数量为0或负数，无需领取")
            return False
            
        print(f"开始领取 {reward_count} 个奖励")
        
        # 点击rewards图标
        if not self.utils.common.quick_click_icon("rewards"):
            print("未能点击rewards图标")
            return False
            
        time.sleep(random.uniform(0.8, 2))  # 等待界面切换
        
        # 点击claim按钮指定次数
        for i in range(reward_count):
            print(f"点击claim按钮 ({i+1}/{reward_count})")
            claim_data = self.utils.common.find_icon("claim")
            if not claim_data:
                print("未找到claim按钮")
                return False
            self.utils.common.quick_click_center(claim_data)
            # 因为检测按钮需要一点时间， 所以这里的 随机等待只是为了增加一个随机性
            time.sleep(random.uniform(0.1, 0.6))
                
        # 处理可能的cancel按钮
        self.utils.emergency.handle_cancel_buttons()
        
        print("奖励领取完成")
        return True

    def random_march_logic(self) -> bool:
        """
        随机选择行军方式
        1. 检查 new_troop, stagnation, march2 按钮的存在情况
        2. 如果有可用的按钮，随机选择一个进行点击
        3. 根据选择的按钮执行相应的后续操作
        
        Returns:
            bool: 是否成功执行行军
        """
        # 检查各个按钮是否存在
        new_troop_data = self.utils.common.find_icon("new_troop")
        stagnation_data = self.utils.common.find_icon("stagnation", 0.65)
        march2_data = self.utils.common.find_icon("march2")
        
        # 统计存在的按钮
        available_buttons = []
        if new_troop_data:
            available_buttons.append(("new_troop", new_troop_data))
        if stagnation_data:
            available_buttons.append(("stagnation", stagnation_data))
        if march2_data:
            available_buttons.append(("march2", march2_data))
            
        if not available_buttons:
            print("未找到任何可用的行军按钮")
            return False
            
        # 随机选择一个按钮
        selected_button, button_data = random.choice(available_buttons)
        print(f"随机选择行军按钮: {selected_button}")
        
        # 点击选中的按钮
        self.utils.common.quick_click_center(button_data)
        time.sleep(random.uniform(0.5, 1))
        
        # 根据不同的按钮执行后续操作
        if selected_button == "new_troop":
            time.sleep(random.uniform(1, 2))
            if not self.utils.common.quick_click_icon("march"):
                print("未找到 march 按钮")
                return False
                
        elif selected_button == "march2":
            return True
            
        elif selected_button == "stagnation":
            time.sleep(random.uniform(1, 2))
            if not self.utils.common.quick_click_icon("march2"):
                return False
                
        print("行军操作完成")
        return True 
    
    def random_march(self) -> bool:
        """
        随机行军
        1. 随机选择行军方式
        2. 执行行军操作
        """
        march_position = self.utils.common.calculate_random_position()
        if march_position is None:
            print("随机位置行军失败")
            return False
        self.utils.mouse.move_to(march_position[0], march_position[1])
        time.sleep(random.uniform(0.5, 1)) 
        pyautogui.click()
        time.sleep(random.uniform(0.5, 1))

        march3_data = self.utils.common.find_icon("march3")
        if not march3_data:
            print("未找到 March 按钮")
            return False
        time.sleep(random.uniform(0.5, 1))

        self.utils.mouse.move_to(march3_data["center"]["x"] + random.uniform(-10, 10) , march3_data["center"]["y"] + random.uniform(-10, 10))
        time.sleep(random.uniform(0.5, 1))  # 短暂停顿
        pyautogui.click()
        time.sleep(random.uniform(0.5, 1))
        random_march_logic = self.random_march_logic()
        if not random_march_logic:
            print("随机行军失败")
            return False
            
        print("随机行军成功")
        return True

    def handle_emoji(self) -> bool:
        """
        处理表情互动
        1. 检查是否存在 stagnation 按钮
        2. 点击 stagnation 按钮
        3. 等待后检查是否存在 emoji 按钮
        4. 点击 emoji 按钮
        5. 在窗口中心点周围随机位置点击
        
        Returns:
            bool: 是否成功完成表情互动
        """
        # 检查是否存在 stagnation 按钮
        stagnation_data = self.utils.common.find_icon("stagnation")
        if not stagnation_data:
            print("未找到 stagnation 按钮")
            return False
            
        # 点击 stagnation 按钮
        print("找到 stagnation 按钮，开始点击")
        self.utils.common.quick_click_center(stagnation_data)
        
        # 随机等待 0.6-1.5 秒
        wait_time = random.uniform(0.6, 1.5)
        print(f"等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        
        # 检查是否存在 emoji 按钮
        emoji_data = self.utils.common.find_icon("emoji")
        if not emoji_data:
            print("未找到 emoji 按钮")
            return False
            
        # 点击 emoji 按钮
        print("找到 emoji 按钮，开始点击")
        self.utils.common.quick_click_center(emoji_data)
        
        # 获取窗口中心点
        center = self.utils.device_detector.get_window_center()
        if not center:
            print("无法获取窗口中心点")
            return False
            
        # 在中心点周围随机位置点击
        # 生成随机角度（0-360度）
        angle = random.uniform(0, 2 * math.pi)
        # 固定半径为100像素
        radius = 80
        
        # 计算随机点击位置
        click_x = int(center['x'] + radius * math.cos(angle))
        click_y = int(center['y'] + radius * math.sin(angle))
        
        print(f"在窗口边缘随机位置点击: ({click_x}, {click_y})")
        
        # 移动鼠标并点击
        self.utils.mouse.move_to(click_x, click_y)
        time.sleep(random.uniform(0.6, 1.2))  # 短暂停顿
        pyautogui.click()
        
        print("表情互动完成")
        return True

    def handle_help(self) -> bool:
        """
        检测并点击 help 按钮
        1. 检查是否存在 help 按钮
        2. 点击 help 按钮
        """
        # 检查是否存在 help 按钮
        help_data = self.utils.common.find_icon("help")
        if not help_data:
            print("未找到 help 按钮")
            return False
            
        # 点击 help 按钮
        print("找到 help 按钮，开始点击")
        self.utils.common.quick_click_center(help_data)
        
        # 随机等待 0.6-1.5 秒
        wait_time = random.uniform(0.6, 1.5)
        print(f"等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
     
        print("帮助操作完成")
        return True
    
    def handle_bag_and_use(self) -> bool:
        """
        处理背包和使用道具的逻辑
        1. 尝试点击bag按钮
        2. 如果没找到bag，先点击menu再试
        3. 在新界面中检测use按钮
        4. 如果找到use，随机点击1-10次
        5. 最后处理可能的cancel按钮
        """
        print("\n=== 开始处理背包和使用道具 ===")
        
        # 首先尝试直接点击bag
        if self.utils.common.quick_click_icon("bag"):
            print("成功点击bag按钮")
        else:
            print("未找到bag按钮，尝试先点击menu")
            # 如果没找到bag，先点击menu
            if self.utils.common.quick_click_icon("menu"):
                print("成功点击menu按钮")
                time.sleep(random.uniform(1, 2))  # 等待界面切换
                # 再次尝试点击bag
                if self.utils.common.quick_click_icon("bag"):
                    print("成功点击bag按钮")
                else:
                    print("点击menu后仍未找到bag按钮")
                    self.utils.emergency.handle_cancel_buttons()
                    return False
            else:
                print("未找到menu按钮")
                self.utils.emergency.handle_cancel_buttons()
                return False
        
        # 等待界面切换
        time.sleep(random.uniform(1, 2))
        
        # 检测开包次数
        random_click_times = random.randint(2, 20)

        # 随机选择方案一或方案二执行
        plan = random.choice(['plan1', 'plan2'])
        print(f"随机选择执行{plan}")
        
        if plan == 'plan1':
            # 方案一
            for i in range(random_click_times):
                if self.utils.common.quick_click_icon("use"):
                    print(f"成功点击use按钮")
                    time.sleep(random.uniform(0.5, 1))
                    self.utils.common.quick_click_icon("confirm")
                    time.sleep(random.uniform(0.5, 1))
                else:
                    print(f"未找到use按钮 {i+1}/{random_click_times}")
        else:
            # 方案二
            for i in range(random_click_times):
                if self.utils.common.quick_click_icon("add"):
                    print("成功点击add按钮")
                    time.sleep(random.uniform(0.5, 1))
            if self.utils.common.quick_click_icon("use"):
                print("成功点击use按钮")
                time.sleep(random.uniform(0.5, 1))
                self.utils.common.quick_click_icon("confirm")
                time.sleep(random.uniform(0.5, 1))
            else:
                print("未找到use按钮")
            
        # 处理可能的cancel按钮
        self.utils.emergency.handle_cancel_buttons()
        return True

    def handle_email_and_read(self) -> bool:
        """
        处理邮件和阅读的逻辑
        1. 尝试点击email按钮
        2. 如果没找到email，先点击menu再试
        3. 在新界面中检测report, alliance, system图标并随机顺序点击
        4. 最后点击read按钮
        5. 处理可能的cancel按钮
        """
        print("\n=== 开始处理邮件和阅读 ===")
        
        # 首先尝试直接点击email
        if self.utils.common.quick_click_icon("email"):
            print("成功点击email按钮")
        else:
            print("未找到email按钮，尝试先点击menu")
            # 如果没找到email，先点击menu
            if self.utils.common.quick_click_icon("menu"):
                print("成功点击menu按钮")
                time.sleep(random.uniform(1, 2))  # 等待界面切换
                # 再次尝试点击email
                if self.utils.common.quick_click_icon("email"):
                    print("成功点击email按钮")
                else:
                    print("点击menu后仍未找到email按钮")
                    self.utils.emergency.handle_cancel_buttons()
                    return False
            else:
                print("未找到menu按钮")
                self.utils.emergency.handle_cancel_buttons()
                return False
        
        # 等待界面切换
        time.sleep(random.uniform(1, 2))

        if self.utils.common.quick_click_icon("read"):
            print("成功点击read按钮")
        else:
            print("未找到read按钮")
            
        time.sleep(random.uniform(1, 2))
        
        # 检测report, alliance, system图标
        report_data = self.utils.common.find_icon("report")
        alliance_data = self.utils.common.find_icon("alliance")
        system_data = self.utils.common.find_icon("system")
        
        # 将找到的图标放入列表
        icons = []
        if report_data:
            icons.append(("report", report_data))
        if alliance_data:
            icons.append(("alliance", alliance_data))
        if system_data:
            icons.append(("system", system_data))
            
        # 随机打乱图标顺序
        random.shuffle(icons)
        
        # 按随机顺序点击图标
        for icon_name, icon_data in icons:
            print(f"点击{icon_name}图标")
            self.utils.common.quick_click_center(icon_data)
            time.sleep(random.uniform(1, 2))  # 短暂等待，避免点击太快
            # 检测并点击read按钮
            if self.utils.common.quick_click_icon("read"):
                print("成功点击read按钮")
            else:
                print("未找到read按钮")
        
        # 处理可能的cancel按钮
        self.utils.emergency.handle_cancel_buttons()
        return True

    def handle_task_rewards(self) -> bool:
        """
        处理任务奖励的领取逻辑
        1. 检测并点击task按钮
        2. 在新界面中检测并点击所有claim按钮
        """
        print("\n=== 开始处理任务奖励 ===")
        
        # 首先尝试直接点击task
        if self.utils.common.quick_click_icon("task"):
            print("成功点击task按钮")
        else:
            print("未找到task按钮")
            self.utils.emergency.handle_cancel_buttons()
            return False
        
        # 等待界面切换
        time.sleep(random.uniform(1, 2))
        
        # 检测并点击所有claim按钮
        while True:
            claim_data = self.utils.common.find_icon("claim")
            if not claim_data:
                print("未找到更多claim按钮")
                break
                
            print("找到claim按钮，开始点击")
            self.utils.common.quick_click_center(claim_data)
            time.sleep(random.uniform(1, 2))  # 短暂等待，避免点击太快
        
        # 处理可能的cancel按钮
        self.utils.emergency.handle_cancel_buttons()
        print("任务奖励处理完成")
        return True

    def handle_vip_rewards(self) -> bool:
        """
        处理VIP奖励和木箱的领取逻辑
        1. 检测并点击vip按钮
        2. 在新界面中随机顺序检测并点击claim和wood_chest
        3. 最后处理可能的cancel按钮
        """
        print("\n=== 开始处理VIP奖励和木箱 ===")
        
        # 首先尝试直接点击vip
        if self.utils.common.quick_click_icon("vip"):
            print("成功点击vip按钮")
        else:
            print("未找到vip按钮")
            self.utils.emergency.handle_cancel_buttons()
            return False
        
        # 等待界面切换
        time.sleep(random.uniform(1, 2))
        
        # 检测claim和wood_chest按钮
        claim_data = self.utils.common.find_icon("claim", 0.8)
        wood_chest_data = self.utils.common.find_icon("wood_chest")
        
        # 随机决定点击顺序
        buttons = []
        if claim_data:
            buttons.append(("claim", claim_data))
        if wood_chest_data:
            buttons.append(("wood_chest", wood_chest_data))
            
        # 随机打乱按钮顺序
        random.shuffle(buttons)
        
        # 按随机顺序点击按钮
        for button_name, button_data in buttons:
            print(f"点击{button_name}按钮")
            self.utils.common.quick_click_center(button_data)
            time.sleep(random.uniform(2, 4))  # 短暂等待，避免点击太快
        
        # 处理可能的cancel按钮
        self.utils.emergency.handle_cancel_buttons()
        print("VIP奖励和木箱处理完成")
        return True

    def handle_territory_rewards(self) -> bool:
        """
        处理联盟领土奖励的领取逻辑
        1. 检测并点击territory按钮
        2. 在新界面中检测并点击claim2按钮
        3. 处理可能的cancel按钮
        """
        print("\n=== 开始处理联盟领土奖励 ===")
        
        # 首先尝试直接点击territory
        if self.utils.common.quick_click_icon("territory"):
            print("成功点击territory按钮")
        else:
            print("未找到territory按钮")
            self.utils.emergency.handle_cancel_buttons()
            return False
        
        # 等待界面切换
        time.sleep(random.uniform(1, 2))
        
        # 检测并点击claim2按钮
        if self.utils.common.quick_click_icon("claim2"):
            print("成功点击claim2按钮")
        else:
            print("未找到claim2按钮")
        
        # 处理可能的cancel按钮
        if self.utils.common.quick_click_icon("cancel"):
            print("成功点击cancel按钮")
        else:
            print("未找到cancel按钮")

        print("联盟领土奖励处理完成")
        return True

    def handle_alliance_gifts(self) -> bool:
        """
        处理联盟礼物的领取逻辑
        1. 检测并点击gift按钮
        2. 在新界面中检测并点击claim_all按钮
        3. 处理可能的cancel按钮
        """
        print("\n=== 开始处理联盟礼物 ===")
        
        # 首先尝试直接点击gift
        if self.utils.common.quick_click_icon("gift"):
            print("成功点击gift按钮")
        else:
            print("未找到gift按钮")
            self.utils.emergency.handle_cancel_buttons()
            return False
        
        # 等待界面切换
        time.sleep(random.uniform(1, 2))
        
        # 检测并点击claim_all按钮
        if self.utils.common.quick_click_icon("claim_all"):
            print("成功点击claim_all按钮")
        else:
            print("未找到claim_all按钮")
        
        # 处理可能的cancel按钮
        if self.utils.common.quick_click_icon("cancel"):
            print("成功点击cancel按钮")
        else:
            print("未找到cancel按钮")
            
        print("联盟礼物处理完成")
        return True

    def handle_alliance_rewards(self) -> bool:
        """
        处理所有联盟奖励的领取逻辑
        1. 检测并点击alliance_icon按钮，如果没有则先点击menu
        2. 在新界面中随机顺序调用：
           - handle_territory_rewards
           - handle_alliance_gifts
        3. 处理可能的cancel按钮
        """
        print("\n=== 开始处理联盟奖励 ===")
        
        # 首先尝试直接点击alliance_icon
        if self.utils.common.quick_click_icon("alliance_icon"):
            print("成功点击alliance_icon按钮")
        else:
            print("未找到alliance_icon按钮，尝试先点击menu")
            # 如果没找到alliance_icon，先点击menu
            if self.utils.common.quick_click_icon("menu"):
                print("成功点击menu按钮")
                time.sleep(random.uniform(1, 2))  # 等待界面切换
                # 再次尝试点击alliance_icon
                if self.utils.common.quick_click_icon("alliance_icon"):
                    print("成功点击alliance_icon按钮")
                else:
                    print("点击menu后仍未找到alliance_icon按钮")
                    self.utils.emergency.handle_cancel_buttons()
                    return False
            else:
                print("未找到menu按钮")
                self.utils.emergency.handle_cancel_buttons()
                return False
        
        # 等待界面切换
        time.sleep(random.uniform(1, 2))
        
        # 创建奖励处理函数列表
        reward_functions = [
            (self.handle_territory_rewards, "领土奖励"),
            (self.handle_alliance_gifts, "联盟礼物")
        ]
        
        # 随机打乱函数顺序
        random.shuffle(reward_functions)
        
        # 按随机顺序执行奖励处理函数
        for func, name in reward_functions:
            print(f"\n开始处理{name}")
            func()
            time.sleep(random.uniform(0.5, 1.0))  # 短暂等待，避免操作太快
        
        # 处理可能的cancel按钮
        self.utils.emergency.handle_cancel_buttons()
        print("联盟奖励处理完成")
        return True

    def handle_villagers_rewards(self) -> bool:
        """
        处理村民奖励的领取逻辑
        1. 检查是否有map界面，如果没有则点击city
        2. 移动鼠标到游戏界面中心
        3. 按下左键并向左上角移动100-200像素
        4. 检测并点击villiagers_rewards按钮
        5. 循环检测并点击villager，直到没有检测到
        6. 检测并点击claim2按钮
        """
        print("\n=== 开始处理村民奖励 ===")
        
        # 检查是否有map界面
        map_data = self.utils.common.find_icon("map")
        if not map_data:
            print("未找到map界面，尝试点击city")
            if not self.utils.common.quick_click_icon("city"):
                print("未找到city按钮")
                return False
            time.sleep(random.uniform(1, 2))  # 等待界面切换
        
        # 获取窗口中心点
        center = self.utils.device_detector.get_window_center()
        if not center:
            print("无法获取窗口中心点")
            return False
            
        # 移动鼠标到中心点
        self.utils.mouse.move_to(center['x'], center['y'])
        time.sleep(random.uniform(0.3, 0.5))
        
        # 计算左上角移动距离（100-200像素）
        move_distance = random.uniform(100, 200)
        # 计算目标位置（左上角方向）
        target_x = int(center['x'] - move_distance)
        target_y = int(center['y'] - move_distance)
        
        # 使用pyautogui的dragTo函数进行拖动，指定使用左键
        pyautogui.dragTo(target_x, target_y, duration=random.uniform(0.5, 1.0), button='left')
        time.sleep(random.uniform(1, 2))  # 等待地图移动完成
        
        # 检测并点击villiagers_rewards按钮
        if self.utils.common.quick_click_icon("villagers_rewards"):
            print("成功点击villagers_rewards按钮")
        else:
            print("未找到villagers_rewards按钮")
            return False
            
        time.sleep(random.uniform(1, 2))  # 等待界面切换
        
        self.utils.mouse.move_to(center['x'], center['y'])

        time.sleep(random.uniform(1, 2))  # 等待界面切换
        # 循环检测并点击villager

        click_amount = 0
        max_click_amount = random.uniform(2, 5)
        while True:
            claim2_data = self.utils.common.find_icon("claim2")
            if not claim2_data:
                time.sleep(random.uniform(0.3, 0.5))
                pyautogui.click()
                click_amount += 1
                if click_amount > max_click_amount:
                    break
                time.sleep(random.uniform(1, 2))  # 等待界面响应
                continue
            break
            
        time.sleep(random.uniform(1, 2)) 
        # 检测并点击claim2按钮
        if self.utils.common.quick_click_icon("claim2"):
            print("成功点击claim2按钮")
        else:
            print("未找到claim2按钮")
            
        print("村民奖励处理完成")
        return True