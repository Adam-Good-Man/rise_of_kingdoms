import core.task.scout as scout
import core.task.train as train
import core.task.common as common
import core.task.barbarian as barbarian
class Task:
    def __init__(self):
        self.scout_task = scout.ScoutTask()
        self.train_task = train.TrainTask()
        self.common_task = common.CommonTask()
        self.barbarian_task = barbarian.BarbarianTask()