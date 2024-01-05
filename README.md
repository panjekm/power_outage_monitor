# POWER OUTAGE MONITOR

## Tips and tricks
- Make sure you symlink the power_monitor.service to systemd -> /etc/systemd/system
- Make sure the service is enabled so it starts at boot: sudo systemctl enable power_monitor.service
- Important is that it waits for the NTP timesync to happen, otherwise we might get an old date (condition on this is in .service file)