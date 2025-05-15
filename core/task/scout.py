import time
import random
from core.utils.index import Utils

class ScoutTask:
    def __init__(self):
        self.running = False  # 控制循环的标志
        self.scout_count = 0
        self.utils = Utils()

    def loop_scout(self):
        """
        无限循环执行探索迷雾任务
        1. 每轮探索后随机等待1-3分钟
        2. 遇到中断时调用handle_interrupt处理
        3. 连续5次中断后退出程序
        """
        print("\n=== 开始循环探索迷雾 ===")
        self.running = True
        self.scout_count = 0
        
        try:
            while self.running:
                # 如果探索次数达到一定数量，则退出
                if self.scout_count >= random.randint(1, 10):
                    break

                # 执行探索迷雾
                print("\n开始新一轮探索...")
                if not self.scout_fog():
                    if not self.utils.emergency.handle_interrupt():
                        print("中断处理失败，退出程序")
                        break
                    continue

                self.scout_count += 1
                # 重置中断计数器
                self.utils.emergency.interrupt_count = 0
                
                wait_time = random.randint(5, 10)
                print(f"已完成探索次数: {self.scout_count} 等待 {wait_time} 秒后继续...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
        finally:
            self.running = False
            print("\n循环探索结束")
    
    def stop(self):
        """停止循环探索"""
        self.running = False

    def scout_fog(self) -> bool:
        """
        执行探索迷雾的任务
        步骤：
        1. 检查并点击map图标
        2. 如果没有map，点击city后再次检查map
        3. 依次点击：scout_camp -> scout_icon -> scouting -> explore -> explore -> send
        
        Returns:
            bool: 是否成功完成探索
        """
        print("\n开始探索迷雾...")
        
        # 步骤1: 检查并点击map图标
        map_data_1 = self.utils.common.find_icon("map")
        if map_data_1 is None:
            print("未找到map图标，尝试点击city...")
            # 如果没找到map，点击city后再次检查
            if not self.utils.common.quick_click_icon("city"):
                print("未找到city图标，探索失败")
                return False
                
            time.sleep(random.uniform(1, 2))
            map_data_2 = self.utils.common.find_icon("map")
            if map_data_2 is None:
                print("点击city后仍未找到map图标，探索失败")
                return False
        
        time.sleep(random.uniform(1, 2))
        scout_camp_icon = self.utils.common.find_icon("scout_camp")
        if scout_camp_icon is None:
            print("未找到scout camp 图标，尝试调整游戏聚焦")
            map_data_3 = self.utils.common.find_icon("map")
            if map_data_3 is None:
                return False
            else:
                self.utils.common.quick_click_icon("map")
                time.sleep(random.uniform(1, 2))
                city_data = self.utils.common.find_icon("city")
                time.sleep(random.uniform(1, 2))
                if city_data is None:
                    return False
                else:
                    self.utils.common.quick_click_icon("city")
                    time.sleep(random.uniform(1, 2))
        
        # 步骤2: 依次点击各个按钮
        steps = [
            ("scout_camp", "侦察营"),
            ("scout_icon", "侦察图标"),
            ("scouting", "侦察按钮"),
            ("explore", "探索按钮"),
            ("explore", "再次探索按钮"),
            ("send", "发送按钮")
        ]
        
        time.sleep(random.uniform(1, 2))
        for icon_name, step_name in steps:
           

            time.sleep(random.uniform(1, 2))
            print(f"\n执行步骤: 点击{step_name}")
            if not self.utils.common.quick_click_icon(icon_name):
                if icon_name == "explore":
                    print("未找到探索按钮，等待60-120秒后重试")
                    time.sleep(random.uniform(60, 120))
                    return True
                print(f"未找到{step_name}，探索失败")
                return False
        
        print("迷雾探索完成")
        return True

    def scout_cave(self):
        pass