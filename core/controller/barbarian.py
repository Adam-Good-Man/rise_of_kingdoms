import time
import random
from core.task.index import Task
from core.utils.common import CommonController

class BarbarianController:
    def __init__(self):
        self.common = CommonController()
        self.task = Task()
        self.total_hunt_count = 0  # 记录总打野次数
        self.max_troops = 2 # 配置最多出动的打野部队数量
        self.max_hunts = 0  # 0 means unlimited
        self.running = False
        self.poi_treat = None
        self.is_paused = False  # 是否处于暂停状态

    def stop(self) -> None:
        """Stop the hunting process"""
        self.running = False

    def handle_heal(self) -> None:
        """
        处理治愈逻辑：
        1. 随机等待5, 10秒
        2. 检测并点击city
        3. 检测并点击treat（如果存在）
        4. 检测并点击heal
        5. 如果检测到quick_replenish则点击，然后点击confirm，再次点击heal
        """
        if self.is_paused:
            return

        print("\n=== 开始执行治愈任务 ===")
        self.is_paused = True
        
        try:
            # 随机等待5, 10秒
            wait_time = random.randint(1, 2)
            print(f"治愈...")
            time.sleep(wait_time)
            
            # 检测并点击city
            print("检测city...")
            if self.common.quick_click_icon("city"):
                print("找到并点击city")
                time.sleep(random.uniform(1, 2))
                
                # 检测并点击treat
                print("检测treat...")
                treat_poi = self.common.find_icon("treat")
                if treat_poi:
                    print("找到并点击treat", treat_poi)
                    self.common._mouse.click_at(treat_poi["position"]["x"], treat_poi["position"]["y"])
                    self.poi_treat = treat_poi

                    time.sleep(random.uniform(1, 2))
                    
                    # 检测并点击heal
                    print("检测heal...")
                    if self.common.quick_click_icon("heal"):
                        print("找到并点击heal")
                        time.sleep(random.uniform(1, 2))
                        
                        # 检测quick_replenish
                        print("检测quick_replenish...")
                        if self.common.quick_click_icon("quick_replenish"):
                            print("找到并点击quick_replenish")
                            time.sleep(random.uniform(1, 2))
                            
                            # 检测并点击confirm
                            print("检测confirm...")
                            if self.common.quick_click_icon("confirm", 1, 0.48):
                                print("找到并点击confirm")
                                time.sleep(random.uniform(1, 2))
                                
                                # 再次检测并点击heal
                                print("再次检测heal...")
                                if self.common.quick_click_icon("heal"):
                                    print("找到并点击heal")
                                    time.sleep(random.uniform(1, 2))
                else:
                    print("未找到treat, 但是尝试领取已治愈的士兵")
                    if self.poi_treat:
                        self.common._mouse.click_at(self.poi_treat["position"]["x"], self.poi_treat["position"]["y"])
                
        finally:
            self.is_paused = False
            print("=== 治愈任务执行完成 ===")

    def handle_other_actions(self) -> None:
        """
        处理其他行为：
        1. 随机选择1-2个其他行为执行
        2. 执行完成后重新生成随机除数
        """
        if self.is_paused:
            return

        print("\n=== 开始执行其他行为 ===")
        self.is_paused = True
        
        try:
            # 其他行为列表
            other_actions = [
                (self.task.common_task.handle_help, "帮助"),
                (self.task.common_task.handle_emoji, "表情"),
                (self.task.common_task.random_march, "随机行军"),
                (self.task.common_task.claim_rewards, "领取奖励"),
                (self.task.common_task.handle_bag_and_use, "背包使用"),
                (self.task.common_task.handle_email_and_read, "邮件阅读"),
                (self.task.common_task.handle_task_rewards, "任务奖励"),
                (self.task.common_task.handle_vip_rewards, "VIP奖励"),
                (self.task.common_task.handle_alliance_rewards, "联盟奖励"),
                (self.task.common_task.handle_villagers_rewards, "村民奖励"),
                (self.task.scout_task.scout_fog, "探索迷雾")
            ]
            
            # 随机选择1-3个其他行为
            num_actions = random.randint(1, 3)
            selected_actions = random.sample(other_actions, num_actions)
            
            for action, name in selected_actions:
                print(f"\n执行{name}")
                action()
                time.sleep(random.uniform(1, 2))
            
        finally:
            self.is_paused = False
            print("=== 其他行为执行完成 ===")

    def loop_hunt(self):
        """
        循环执行打野操作
        1. 使用normal_hunt开始打野
        2. 每5-10次打野后随机选择新的打野方式
        3. 当总打野次数对随机数(5-10)取余为0时执行其他行为
        4. 连续失败5次则退出
        """
        print("\n=== 开始循环打野 ===")
        self.running = True
        self.total_hunt_count = 0

        # 打野方式列表
        hunt_methods = [
            (self.task.barbarian_task.normal_hunt, "普通打野"),
            (self.task.barbarian_task.scroll_to_find_barbarian, "滚动寻找野蛮人")
        ]
        
        # 初始化计数器
        consecutive_failures = 0
        current_hunt_method = hunt_methods[0]  # 默认使用普通打野
        
        # 设置初始随机次数
        next_method_change = random.randint(5, 10)
        next_stagnation_check = random.randint(8, 20)  # 随机设置stagnation检查间隔
        
        try:
            while self.running:

                # 如果打野次数达到一定数量，则退出， 转而执行 其他 循环任务
                if self.total_hunt_count >= random.randint(1, 10):
                    break

                # 如果正在执行其他任务，跳过本次循环
                if self.is_paused:
                    time.sleep(1)
                    continue

                # 检查部队状态
                current_troops = self.common.check_troop_status()

                if current_troops >= self.max_troops:
                    if not self.common.wait_for_stagnation():
                        time.sleep(random.uniform(10, 20))
                        continue
                
                # 检查是否需要暂停
                if random.uniform(1, 100) >= 90:
                    print(f"达到治愈条件，当前打野次数: {self.total_hunt_count}")
                    self.handle_heal()
                    continue

                # 检查是否需要执行其他行为
                if random.uniform(1, 100) >= 90:
                    print(f"达到其他行为条件，当前打野次数: {self.total_hunt_count}")
                    self.handle_other_actions()
                    continue
                
                # 执行当前打野方式
                print(f"\n执行{current_hunt_method[1]}")
                if current_hunt_method[0]():
                    consecutive_failures = 0  # 重置连续失败计数
                    self.total_hunt_count += 1
                    print(f"打野成功，当前计数: {self.total_hunt_count}")

                else:
                    consecutive_failures += 1
                    print(f"打野失败，连续失败次数: {consecutive_failures}")
                
                # 检查是否需要更换打野方式
                if self.total_hunt_count % next_method_change == 0: 
                    print("\n更换打野方式")
                    # 随机选择新的打野方式（确保与当前不同）
                    available_methods = [m for m in hunt_methods if m != current_hunt_method]
                    current_hunt_method = random.choice(available_methods)
                    next_method_change = random.randint(5, 10)
                    print(f"新的打野方式: {current_hunt_method[1]}")
                
                # 检查是否需要检查stagnation和back按钮
                if self.total_hunt_count % next_stagnation_check == 0:
                    print("\n检查stagnation和back按钮")
                    if self.common.quick_click_icon("stagnation", threshold=0.65):
                        print("找到并点击stagnation按钮")
                        time.sleep(random.uniform(0.5, 1))
                        if self.common.quick_click_icon("back"):
                            print("找到并点击back按钮")
                    next_stagnation_check = random.randint(6, 12)  # 重新随机设置下次检查间隔
                    print(f"下次stagnation检查计数: {next_stagnation_check}")
                
                # 检查连续失败次数
                if consecutive_failures >= 5:
                    print("\n连续失败5次，程序退出")
                    break
                
                # 每次打野后等待一段时间
                time.sleep(random.uniform(5, 10))
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
        finally:
            self.running = False
            print("\n循环打野结束")
