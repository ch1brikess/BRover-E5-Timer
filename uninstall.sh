#!/bin/bash

echo "Starting uninstallation of AlarmClock..."

systemctl stop alarm-clock.service
systemctl disable alarm-clock.service
echo "Service stopped and disabled."

rm -f /etc/systemd/system/alarm-clock.service
echo "Removed systemd service file."

systemctl daemon-reload
echo "Reloaded systemd daemon."

rm -f /usr/bin/alarm_clock
echo "Removed executable from /usr/bin/."

rm -f /etc/alarm_config.json
echo "Removed configuration file from /etc/."

echo "Uninstallation complete."