using Dates

# Parse travis API logs with a very specific structure. Apologies if you're looking at this -- this is a 5-minute hack.

# Example usage: julia parse.jl cleaned/devops devops
# Produces category,name,pass_rate,fail_rate,error_rate

function number_of_9s(pct::Float64)
    log(10, 1 / (1.0 - pct))
end

function process_travis_log(fname::String, category::String, project::String)
    lines = readlines(open(fname))
    time_in_status = Dict()

    last_time = nothing
    time_in_status["passed:"] = 0
    time_in_status["failed:"] = 0
    time_in_status["errored:"] = 0
    time_in_status["canceled:"] = 0
    time_in_status["started:"] = 0
    for line in lines
        # print(line)
        parts = split(line)        
        time_str = string(parts[1], ' ', parts[2])
        if time_str == "not yet" # indicates aborted build.
            continue
        else
            time = DateTime(time_str, "y-m-d H:M:S")
        end
        status = parts[4]

        # Compute delta from last build result.
        if last_time != nothing
            diff = div(int(last_time - time),1000) # difference in seconds
            if diff < 0
                # println("ERROR $fname $last_time $time")
            else
                time_in_status[status] += diff
            end
        end
        last_time = time
    end
    total_time = time_in_status["passed:"] + time_in_status["failed:"] + time_in_status["errored:"]
    pass_rate = time_in_status["passed:"] / total_time
    fail_rate = time_in_status["failed:"] / total_time
    error_rate = time_in_status["errored:"] / total_time
    nines = number_of_9s(pass_rate)
    println("$category,$project,$pass_rate,$fail_rate,$error_rate,$nines")
end

# Run on one directory. Not recurisve.
function process_logs(dir::String, category::String)
    for f in readdir(dir)
        if !ismatch(r"Gemfile.*",f)
            process_travis_log(string(dir,"/",f), category, f)
        end
    end
end

process_logs(ARGS[1], ARGS[2])
