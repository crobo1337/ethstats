import argparse

"""
set up simple parser to take log path as an input
"""
parser = argparse.ArgumentParser(description='get usage from logfile')
parser.add_argument('logfile')
args=parser.parse_args()

"""
grab only the line containing the stats we care about
"""
def get_usage_lines(logfile):
    usage = []
    pointer = 0
    with open(logfile, 'r') as log:
        lines = log.readlines()
        for line in lines:
            if 'Uptime' in line:
                words=line.split()
                usage.append({'pointer': pointer, \
                              'uptime_days': words[2], \
                              'uptime_hms': words[3], \
                              'power_usage': words[5]})
                pointer +=1
    return usage #returns list of dicts

"""
 We need to find when the counters are reset in the log by looking for 0h 0m and <59sec
"""
def find_restarts(usage):
    restarts = []
    for value in usage:
        split_val = value['uptime_hms'].split(":")

        if split_val[0] == '00' \
        and split_val[1] == '00' \
        and int(split_val[2]) <=59 \
        and value['uptime_days'] == '0d':
            restarts.append(value['pointer'])
    return restarts # returns a list of every pointer AFTER a restart

"""
The easiest way to do this is watch for a low value and then move back one
occurance in our list, to find the maximum value of the previous run.
"""
def get_max_usage_before_restart(usage, restarts):
    last_entries_before_restart = []
    for restart in restarts:
        if restart != 0:
            last_entries_before_restart.append(usage[restart-1])
    return last_entries_before_restart

"""
convert all times down to seconds and add to totals
"""
def add_up_usage(usage, last_entries_before_restart):
    power = 0.0
    uptime = 0
    for entry in last_entries_before_restart:
        split_time = entry['uptime_hms'].split(":")
        total_seconds = (int(split_time[0])*3600)+ \
                        (int(split_time[1])*60)+ \
                        (int(split_time[2])) + \
                        (int(entry['uptime_days'].strip('d'))*86400)
        power = power + float(entry['power_usage'])
        uptime = uptime + total_seconds
    return {'uptime': uptime, 'power_usage': power}


"""
convert total seconds back to D:HH:MM:SS for readability
"""
def convert_sec_to_dhms(time):
    # convert seconds to day, hour, minutes and seconds
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return {"D": day, "H": hour, "M": minutes, "S": seconds,}


"""
Main logic
"""
def main(logfile):
    usage = get_usage_lines(logfile)
    restarts = find_restarts(usage)
    max_usage_before_restart = get_max_usage_before_restart(usage, restarts)
    totals = add_up_usage(usage, max_usage_before_restart)
    uptime = convert_sec_to_dhms(totals['uptime'])


    print(f"----Total Usage----")
    print(f"Days:{uptime['D']}")
    print(f"Hours:{uptime['H']}")
    print(f"Minutes:{uptime['M']}")
    print(f"Seconds:{uptime['S']}")
    print(f"Total Power Consumption: {totals['power_usage']} kwH")
    print(f"miner restarted {len(restarts)} times during this period")
    print("-------------------")


main(args.logfile)


## watch for next 'uptime' value of <59 seconds and count that as a restart
##take value from last entry before restart and add it to total usage numbers
