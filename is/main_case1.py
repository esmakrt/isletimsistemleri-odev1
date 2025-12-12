import csv
import threading
import re
import copy

# ADIM 1: Surec (Process) Sinifi
class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        
        # Oncelikleri sayiya ceviriyoruz (kucuk sayi = yuksek oncelik)
        if priority.strip().lower() == 'high':
            self.priority = 1
        elif priority.strip().lower() == 'normal':
            self.priority = 2
        else:
            self.priority = 3

        # Degiskenleri baslatiyoruz
        self.start_time = 0
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.remaining_time = self.burst_time

    def __repr__(self):
        return f"Process(ID={self.pid}, Arrive={self.arrival_time}, Burst={self.burst_time}, Priority={self.priority})"

# ADIM 2: Dosya Okuma
def load_processes(filename):
    process_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader) # Basligi atla
            for row in reader:
                if not row: continue
                new_process = Process(row[0], row[1], row[2], row[3])
                process_list.append(new_process)
        print(f"{filename} basariyla yuklendi. Toplam {len(process_list)} surec var.")
        return process_list
    except FileNotFoundError:
        print(f"HATA: {filename} dosyasi bulunamadi!")
        return []

# --- ALGORITMALAR ---

def schedule_FCFS(process_list):
    processes = copy.deepcopy(process_list)
    processes.sort(key=lambda x: x.arrival_time)
    
    current_time = 0
    gantt_chart = ""
    
    print("\n FCFS Simulasyonu")
    
    for p in processes:
        if current_time < p.arrival_time:
            gantt_chart += f"[{current_time}]--IDLE--[{p.arrival_time}]"
            current_time = p.arrival_time
            
        p.start_time = current_time
        p.completion_time = current_time + p.burst_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        
        gantt_chart += f"[{current_time}]--{p.pid}--[{p.completion_time}]"
        current_time = p.completion_time

    return processes, gantt_chart

def schedule_SJF_NonPreemptive(process_list):
    processes = copy.deepcopy(process_list)
    current_time = 0
    completed_processes = []
    gantt_chart = ""
    
    print("\n Non-Preemptive SJF Simulasyonu")
    
    while len(completed_processes) < len(processes):
        ready_queue = []
        for p in processes:
            if p.arrival_time <= current_time and p not in completed_processes:
                ready_queue.append(p)
        
        if not ready_queue:
            gantt_chart += f"[{current_time}]--IDLE--"
            remaining_processes = [p for p in processes if p not in completed_processes]
            next_arrival = min(remaining_processes, key=lambda x: x.arrival_time).arrival_time
            gantt_chart += f"[{next_arrival}]"
            current_time = next_arrival
            continue

        shortest_job = min(ready_queue, key=lambda x: x.burst_time)
        
        shortest_job.start_time = current_time
        shortest_job.completion_time = current_time + shortest_job.burst_time
        shortest_job.turnaround_time = shortest_job.completion_time - shortest_job.arrival_time
        shortest_job.waiting_time = shortest_job.turnaround_time - shortest_job.burst_time
        
        gantt_chart += f"[{current_time}]--{shortest_job.pid}--[{shortest_job.completion_time}]"
        current_time = shortest_job.completion_time
        completed_processes.append(shortest_job)

    return completed_processes, gantt_chart

def schedule_Priority_NonPreemptive(process_list):
    processes = copy.deepcopy(process_list)
    current_time = 0
    completed_processes = []
    gantt_chart = ""
    
    print("\n Non-Preemptive Priority Simulasyonu")
    
    while len(completed_processes) < len(processes):
        ready_queue = [p for p in processes if p.arrival_time <= current_time and p not in completed_processes]
        
        if not ready_queue:
            gantt_chart += f"[{current_time}]--IDLE--"
            remaining = [p for p in processes if p not in completed_processes]
            next_arrival = min(remaining, key=lambda x: x.arrival_time).arrival_time
            gantt_chart += f"[{next_arrival}]"
            current_time = next_arrival
            continue

        selected_process = min(ready_queue, key=lambda x: (x.priority, x.arrival_time))
        
        selected_process.start_time = current_time
        selected_process.completion_time = current_time + selected_process.burst_time
        selected_process.turnaround_time = selected_process.completion_time - selected_process.arrival_time
        selected_process.waiting_time = selected_process.turnaround_time - selected_process.burst_time
        
        gantt_chart += f"[{current_time}]--{selected_process.pid}--[{selected_process.completion_time}]"
        current_time = selected_process.completion_time
        completed_processes.append(selected_process)

    return completed_processes, gantt_chart

def schedule_SJF_Preemptive(process_list):
    processes = copy.deepcopy(process_list)
    current_time = 0
    completed = 0
    n = len(processes)
    gantt_chart = ""
    last_process_id = None 
    
    print("\n Preemptive SJF (SRTF) Simulasyonu")
    
    while completed < n:
        ready_queue = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not ready_queue:
            if last_process_id != "IDLE":
                gantt_chart += f"[{current_time}]--IDLE--"
                last_process_id = "IDLE"
            current_time += 1
            continue

        current_process = min(ready_queue, key=lambda x: x.remaining_time)
        
        if current_process.start_time == 0 and current_process.remaining_time == current_process.burst_time:
             current_process.start_time = current_time
             
        current_process.remaining_time -= 1
        current_time += 1
        
        if last_process_id != current_process.pid:
            gantt_chart += f"[{current_time-1}]--{current_process.pid}--"
            last_process_id = current_process.pid
        
        if current_process.remaining_time == 0:
            completed += 1
            current_process.completion_time = current_time
            current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
            gantt_chart += f"[{current_time}]"
            last_process_id = None

    return processes, gantt_chart

def schedule_RoundRobin(process_list, time_quantum=4):
    processes = copy.deepcopy(process_list)
    queue = []
    current_time = 0
    completed_processes = []
    remaining_processes = sorted(processes, key=lambda x: x.arrival_time)
    gantt_chart = ""
    
    print(f"\n Round Robin (Quantum={time_quantum}) Simulasyonu")
    
    while queue or remaining_processes:
        for p in remaining_processes[:]:
            if p.arrival_time <= current_time:
                queue.append(p)
                remaining_processes.remove(p)
            else:
                break
                
        if not queue:
            gantt_chart += f"[{current_time}]--IDLE--"
            current_time = remaining_processes[0].arrival_time
            continue

        current_process = queue.pop(0)
        exec_time = min(current_process.remaining_time, time_quantum)
        
        if current_process.remaining_time == current_process.burst_time:
            current_process.start_time = current_time
            
        gantt_chart += f"[{current_time}]--{current_process.pid}--"
        current_process.remaining_time -= exec_time
        current_time += exec_time
        gantt_chart += f"[{current_time}]"
        
        for p in remaining_processes[:]:
            if p.arrival_time <= current_time:
                queue.append(p)
                remaining_processes.remove(p)
        
        if current_process.remaining_time > 0:
            queue.append(current_process)
        else:
            current_process.completion_time = current_time
            current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
            completed_processes.append(current_process)
            
    return completed_processes, gantt_chart

def schedule_Priority_Preemptive(process_list):
    processes = copy.deepcopy(process_list)
    current_time = 0
    completed = 0
    n = len(processes)
    gantt_chart = ""
    last_process_id = None 
    
    print("\n Preemptive Priority Simulasyonu")
    
    while completed < n:
        ready_queue = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not ready_queue:
            if last_process_id != "IDLE":
                gantt_chart += f"[{current_time}]--IDLE--"
                last_process_id = "IDLE"
            current_time += 1
            continue

        current_process = min(ready_queue, key=lambda x: (x.priority, x.arrival_time))
        
        if current_process.start_time == 0 and current_process.remaining_time == current_process.burst_time:
             current_process.start_time = current_time
             
        current_process.remaining_time -= 1
        current_time += 1
        
        if last_process_id != current_process.pid:
            gantt_chart += f"[{current_time-1}]--{current_process.pid}--"
            last_process_id = current_process.pid
        
        if current_process.remaining_time == 0:
            completed += 1
            current_process.completion_time = current_time
            current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
            gantt_chart += f"[{current_time}]"
            last_process_id = None

    return processes, gantt_chart

#YAZDIRMA VE CALISTIRMA

def write_output(filename, algorithm_name, processes, gantt_chart):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"--- {algorithm_name} Sonuclari ---\n")
        f.write("\nZaman Cizelgesi:\n")
        f.write(gantt_chart + "\n")
        f.write("-" * 50 + "\n")
        
        # Bekleme Sureleri Hesabi
        total_wait = sum(p.waiting_time for p in processes)
        max_wait = max(p.waiting_time for p in processes) # Max Bekleme
        n = len(processes)
        avg_wait = total_wait / n
        
        # Tamamlanma Sureleri Hesabi
        total_turnaround = sum(p.turnaround_time for p in processes)
        max_turnaround = max(p.turnaround_time for p in processes) # Max Tamamlanma
        avg_turnaround = total_turnaround / n
        
        # Dosyaya Yazdirma
        f.write(f"Maksimum Bekleme Suresi: {max_wait}\n")
        f.write(f"Ortalama Bekleme Suresi: {avg_wait:.2f}\n")
        f.write(f"Maksimum Tamamlanma Suresi: {max_turnaround}\n")
        f.write(f"Ortalama Tamamlanma Suresi: {avg_turnaround:.2f}\n")
        
        f.write("\nThroughput (T anina kadar biten is sayisi):\n")
        targets = [50, 100, 150, 200]
        for t in targets:
            count = sum(1 for p in processes if p.completion_time <= t)
            f.write(f"  T={t} => {count} islem tamamlandi\n")
            
        segments = re.findall(r'P\d+', gantt_chart)
        num_switches = max(0, len(segments) - 1)
        f.write(f"\nToplam Baglam Degistirme Sayisi: {num_switches}\n")
        
        total_burst = sum(p.burst_time for p in processes)
        last_completion = max(p.completion_time for p in processes)
        overhead = num_switches * 0.001
        total_duration = last_completion + overhead
        utilization = (total_burst / total_duration) * 100 if total_duration > 0 else 0
        
        f.write(f"CPU Verimliligi: %{utilization:.4f}\n")
    
    print(f"✅ {algorithm_name} tamamlandi. Sonuclar '{filename}' dosyasina yazildi.")

def run_fcfs(processes):
    results, chart = schedule_FCFS(processes)
    write_output("FCFS_Sonuc_case1.txt", "FCFS", results, chart)

def run_sjf_non_preemptive(processes):
    results, chart = schedule_SJF_NonPreemptive(processes)
    write_output("SJF_NonPreemptive_Sonuc_case1.txt", "Non-Preemptive SJF", results, chart)

def run_priority_non_preemptive(processes):
    results, chart = schedule_Priority_NonPreemptive(processes)
    write_output("Priority_NonPreemptive_Sonuc_case1.txt", "Non-Preemptive Priority", results, chart)

def run_sjf_preemptive(processes):
    results, chart = schedule_SJF_Preemptive(processes)
    write_output("SJF_Preemptive_Sonuc_case1.txt", "Preemptive SJF (SRTF)", results, chart)

def run_round_robin(processes):
    results, chart = schedule_RoundRobin(processes, time_quantum=4)
    write_output("RoundRobin_Sonuc_case1.txt", "Round Robin", results, chart)

def run_priority_preemptive(processes):
    results, chart = schedule_Priority_Preemptive(processes)
    write_output("Priority_Preemptive_Sonuc_case1.txt", "Preemptive Priority", results, chart)

if __name__ == "__main__":
   
    # Kullanıcıdan dosya ismini istiyoruz (input ile)
    dosya_adi = input("Lütfen okunacak dosya adını yazın (Örn: case1.csv): ")

    # Eğer kullanıcı bir şey yazmadan Enter'a basarsa otomatik case1.csv'yi seçer
    if dosya_adi == "":
        dosya_adi = "case1.csv"
    all_processes = load_processes(dosya_adi)
    
    if all_processes:
        print("--- MULTITHREADING MODU BASLATILIYOR (CASE 1) ---")
        print("Tum algoritmalar ayni anda calisacak...\n")
        
        threads = []
        threads.append(threading.Thread(target=run_fcfs, args=(all_processes,)))
        threads.append(threading.Thread(target=run_sjf_non_preemptive, args=(all_processes,)))
        threads.append(threading.Thread(target=run_priority_non_preemptive, args=(all_processes,)))
        threads.append(threading.Thread(target=run_sjf_preemptive, args=(all_processes,)))
        threads.append(threading.Thread(target=run_round_robin, args=(all_processes,)))
        threads.append(threading.Thread(target=run_priority_preemptive, args=(all_processes,)))
        
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        print("\n--- TUM SIMULASYONLAR TAMAMLANDI ---")
        print("Lutfen klasordeki .txt dosyalarini kontrol edin.")