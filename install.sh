#!/bin/bash

echo "Starting installation of AlarmClock..."

# 1. Copy Python script to /usr/bin
cp alarm_clock.py /usr/bin/alarm_clock
chmod +x /usr/bin/alarm_clock
echo "Copied alarm_clock.py to /usr/bin/"

# 2. Copy JSON config to /etc
cp alarm_config.json /etc/alarm_config.json
echo "Copied alarm_config.json to /etc/"

# 3. Create systemd service file
cat > /etc/systemd/system/alarm-clock.service <<EOF
[Unit]
Description=ROS2 Alarm Clock Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/bin/alarm_clock
Restart=on-failure
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

echo "Created systemd service file."

# 4. Reload systemd daemon
systemctl daemon-reload

# 5. Enable and start the service
systemctl enable alarm-clock.service
systemctl start alarm-clock.service

echo "Installation complete. Service started."
echo "To check logs: journalctl -u alarm-clock.service -f"
echo "To edit times: nano /etc/alarm_config.json (then run: systemctl restart alarm-clock)"