#include <iostream>
#include <optional>
#include <fstream>

#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/IOKitLib.h>

std::optional<SInt64> GetValueAsSInt64(CFDictionaryRef description,
                                        CFStringRef key) {
  std::optional<SInt64> value;
  CFNumberRef number = (CFNumberRef) CFDictionaryGetValue(description, key);

  SInt64 v;
  if (number && CFNumberGetValue(number, kCFNumberSInt64Type, &v)) {
    value.emplace(v);
  }

  return value;
}

class PowerLogger{
public:
    static constexpr SInt64 kInterval = 60;
    
    PowerLogger(){
        output_file << "Current capacity, Max Capacity, Power.Mac.BatteryDischarge" << std::endl;
    }
    
    void Schedule(){
        CFRunLoopTimerContext timer_context = CFRunLoopTimerContext();
        timer_context.info = this;
        CFRunLoopTimerRef log_timer = CFRunLoopTimerCreate(NULL,                // allocator
                                                        1,  // fire time
                                                        kInterval,  // interval
                                                        0,                   // flags
                                                        0,                   // priority
                                                        PrintTemp,
                                                        &timer_context);
        
        CFRunLoopRef loop = CFRunLoopGetCurrent();
        CFRunLoopAddTimer(loop, log_timer, kCFRunLoopDefaultMode);
        CFRunLoopRun();
    }
    
private:
    
    static void PrintTemp(CFRunLoopTimerRef timer, void* info){
        PowerLogger* logger = reinterpret_cast<PowerLogger*>(info);
        
        CFMutableDictionaryRef dict;
        kern_return_t result = IORegistryEntryCreateCFProperties(logger->powerSource, &dict,0, 0);
        
        if (result != KERN_SUCCESS) {
            std::cerr << "Could not query power source!";
        }
        
        std::optional<SInt64> current_capacity =
              GetValueAsSInt64(dict, CFSTR("AppleRawCurrentCapacity"));
        std::optional<SInt64> max_capacity =
            GetValueAsSInt64(dict, CFSTR("AppleRawMaxCapacity"));
        
        if (!current_capacity.has_value() || !max_capacity.has_value()) {
            std::cerr << "Could not query power source!";
        }
        
        CFRelease(dict);
        
        if(logger->last_capacity != 0){
            SInt64 difference = logger->last_capacity - current_capacity.value();
            SInt64 discharge = static_cast<double>(difference) / max_capacity.value() * 10000;

            logger->output_file << current_capacity.value() << "," << max_capacity.value() << "," << discharge  << std::endl;
        }
        logger->last_capacity = current_capacity.value();
        
    }
    
    std::ofstream output_file = std::ofstream("battery_discharge.csv", std::ofstream::trunc);
    SInt64 last_capacity = 0;
    io_service_t powerSource = IOServiceGetMatchingService(kIOMasterPortDefault, IOServiceMatching("IOPMPowerSource"));
};

int main(int argc, const char * argv[]) {
    PowerLogger power_logger;
    power_logger.Schedule();
    return 0;
}
