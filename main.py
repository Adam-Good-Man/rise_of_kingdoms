import time
import random
import traceback
from core.controller.index import Controller
from core.task.scout import ScoutTask
def main():
    """Test the scout_fog functionality"""
    try:
        print("开始运行")
        controller = Controller()
        scout_task = ScoutTask()

        # icon_data = controller.barbarian.common.find_icon("scout_camp")
        # print(icon_data)

        # scout_task.loop_scout()
        while True:
            controller.barbarian.loop_hunt()
            time.sleep(random.uniform(1, 2))

            scout_task.loop_scout()
            time.sleep(random.uniform(1, 2))
            
            # controller.barbarian.task.common_task.handle_bag_and_use()
            # icon_data = controller.barbarian.common.find_icon("ax", 0.5)
            # print(icon_data)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序发生错误: {str(e)}")
        traceback.print_exc()
    finally:
        print("\n程序结束")

if __name__ == "__main__":
    main() 