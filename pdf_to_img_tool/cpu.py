import psutil
from time import sleep
def get_free_cpu_count():
    # Get the total number of logical CPUs
    total_cpus = psutil.cpu_count(logical=True)
    
    # Get the number of busy CPUs
    busy_cpus = psutil.cpu_percent(interval=1) / 100 * total_cpus  # Average CPU usage over a 1-second interval
    
    # Calculate free CPUs
    free_cpus = total_cpus - busy_cpus
    return total_cpus, busy_cpus, free_cpus

def cpu_check(stop_event):
    while not stop_event.is_set():  # Check if the stop event is set
        total_cpus, busy_cpus, free_cpus = get_free_cpu_count()
        print(f" Total CPUs: {total_cpus},\n Busy CPUs: {busy_cpus:.2f},\n Free CPUs: {free_cpus:.2f}")
        print('*'*66)
        sleep(1)  # Wait for 1 second before checking again

if __name__ == "__main__":
    total, busy, free = get_free_cpu_count()
    print(f"Total CPUs: {total}")
    print(f"Busy CPUs: {busy:.2f}")
    print(f"Free CPUs: {free:.2f}")
    print(f"Free CPUs: {free=:}")
    
