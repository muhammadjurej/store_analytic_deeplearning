from datetime import datetime

def time_():
      e = datetime.now()
      hour = e.hour
      minute = e.minute
      second = e.second
      
      return f"{hour}:{minute}:{second}"

def calculate_time(strat, end):
      t1 = datetime.strptime(strat, "%H:%M:%S")
      t2 = datetime.strptime(end, "%H:%M:%S")
      return int((t2 - t1).total_seconds())