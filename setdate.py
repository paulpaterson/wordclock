import subprocess
import datetime


def set_system_date(target_time: datetime.datetime) -> None:
    # Format the date and time for the date command (adjust the format as needed)
    date_string = target_time.strftime("%Y/%m/%d %H:%M:%S")

    #
    # Set the system clock
    try:
        # Execute the date command with sudo
        subprocess.run(['sudo', 'date', '-s', date_string], check=True)
        print(f"System date and time set to: {target_time}")
    except subprocess.CalledProcessError as e:
        print(f"Error setting system date and time: {e}")

    # 
    # Set the Hardware clock
    try:
        subprocess.run(['sudo', 'hwclock', '-w'], check=True)
        print(f'Set the hardware clock to {target_time}')
    except subprocess.CalledProcessError as e:
        print(f'Error setting the hardware data: {e}')


if __name__ == "__main__":
    # Define the desired date and time
    target_time = datetime.datetime(year=2025, month=12, day=25, hour=10, minute=30, second=0)
    set_system_date(target_time)


