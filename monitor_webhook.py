"""
Monitor webhook activity in real-time
"""
import time
import subprocess
import sys

print("🔍 Monitoring Nino webhook activity...")
print("📱 Send a WhatsApp message to test!")
print("=" * 60)
print()

# Watch the process output
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n✅ Monitoring stopped")
