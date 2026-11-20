def find_period(trial_distance, trial_number):
    filename = f"{trial_distance}mmTrial{trial_number}.csv"

    with open(filename, "r") as f:
        data = f.readlines()

    OFFSET = int(data[1].split(",")[0]) # timestamp starts from a certain number, rather than zero

    for i in range(1, len(data)):   # basic formatting to make data usable
        data[i] = data[i].split(",")
        # time = int(data[i][0])
        time = int(data[i][0]) - OFFSET   # updating time (in milis) by calibrating to offset
        data[i][0] = time
        data[i][1] = float(data[i][1].strip())

    times = [i[0] for i in data][1:]
    acc = [i[1] for i in data][1:]

    mean = sum(acc) / len(acc)
    k = 10
    peak_times = []
    N = 0   # Number of peaks
    CUTOFF = 15000
    TOTAL_N = 11    # total number of peaks we want to sample
    CYCLES_N = TOTAL_N - 1      # number of cycles we want to sample

    for i in range(k, len(acc) - k):
        if N == TOTAL_N:
            break

        if times[i] > CUTOFF:

            # acc[i] > mean ensures that the code doesnt detect "noise" well below the peak
            # max(acc[i-k : i+k+1]), finds the highest value i.e the peak, within a window of k values

            if acc[i] > mean and acc[i] == max(acc[i-k : i+k+1]):
                # (times[i] - peak_times[-1] > 200) ensures that there is only one peak per cycle
                # difference should be greater than 200 ms (to ensure they are in separate cycles)

                if not peak_times or times[i] - peak_times[-1] > 200:
                    peak_times.append(times[i])
                    N += 1

    for i in range(len(peak_times)):
        peak_times[i] += OFFSET

    # print(peak_times)
    print(peak_times)
    print(f"Number of Cycles in Sample: {CYCLES_N}")

    # to find number of intervals, we need to subtract 1 from number of peaks
    period = (peak_times[-1] - peak_times[0])/CYCLES_N
    print(f"Period: {period}")

    return period

DISTANCE_INTERVAL = 12
NUMBER_OF_DISTANCES = 11
TRIAL_NUMBERS = 3       # number of trials for each distance
file = open("00 periods.txt", "a")
trials_sum = 0

for i in range(NUMBER_OF_DISTANCES):
    file.write(f"\nFor distance of {i * DISTANCE_INTERVAL}mm: \n")
    for x in range(1, TRIAL_NUMBERS + 1):
        period = find_period(i * DISTANCE_INTERVAL, x)
        trials_sum += period
        file.write(f"Trial {x} = {period}\n")
    
    # We round to account for the "Floating-point precision error" (and match sig digs ofc)
    avg = round(trials_sum/TRIAL_NUMBERS, 1)
    file.write(f"Average period = {avg}\n")
    trials_sum = 0

file.close()
