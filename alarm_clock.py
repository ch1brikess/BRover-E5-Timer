import rclpy
from cyphal_ros2_bridge.msg import PowerButtons
from rclpy.node import Node
from cyphal_ros2_bridge.srv import CallHMIBeeper

import json
import threading
import time
from datetime import datetime, timedelta

# PROD BY QWEN STUDIO!!!!!!!!!!!!!!!!!!!!

class AlarmClock(Node):
    def __init__(self):
        super().__init__('AlarmClockNode')
        
        self.alarm_active = False
        self.alarm_times = []
        self.last_triggered_minute = None
        
        self.load_alarm_config()
        
        self.userbutton_sub = self.create_subscription(
            PowerButtons, 
            "/user_button", 
            self.userbutton_callback, 
            10
        )
        self.beeper_clt = self.create_client(CallHMIBeeper, "/hmi/beep")
        
        self.alarm_thread = threading.Thread(target=self.alarm_monitor_loop, daemon=True)
        self.alarm_thread.start()
        
    def load_alarm_config(self):
        try:
            with open('alarm_config.json', 'r') as f:
                config = json.load(f)
                self.alarm_times = config.get('times', [])
        except Exception:
            self.alarm_times = []

    def userbutton_callback(self, msg):
        if msg.user and self.alarm_active:
            self.alarm_active = False
        
    def get_next_alarm_delta(self):
        now = datetime.now()
        min_delta = None
        
        for time_str in self.alarm_times:
            try:
                h, m = map(int, time_str.split(':'))
                alarm_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if alarm_dt <= now:
                    alarm_dt += timedelta(days=1)
                delta = alarm_dt - now
                if min_delta is None or delta < min_delta:
                    min_delta = delta
            except ValueError:
                continue
        
        return min_delta

    def format_delta(self, delta):
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def alarm_monitor_loop(self):
        while rclpy.ok():
            now = datetime.now()
            current_time_str = now.strftime("%H:%M:%S")
            
            if not self.alarm_times:
                print(f"[{current_time_str}] будильники не заданы")
            else:
                delta = self.get_next_alarm_delta()
                next_str = self.format_delta(delta)
            
            hhmm = now.strftime("%H:%M")
            if hhmm in self.alarm_times and not self.alarm_active:
                if self.last_triggered_minute != hhmm:
                    self.last_triggered_minute = hhmm
                    alarm_thread = threading.Thread(target=self.trigger_alarm, daemon=True)
                    alarm_thread.start()
            
            time.sleep(1)

    def trigger_alarm(self):
        self.alarm_active = True
        while self.alarm_active:
            req = CallHMIBeeper.Request()
            req.beeper.duration = 0.5
            req.beeper.frequency = 2.0
            self.beeper_clt.call_async(req)
            time.sleep(0.6)


rclpy.init()
alarm = AlarmClock()
rclpy.spin(alarm)