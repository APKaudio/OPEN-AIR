




Fuction - Zone clicked or Group Clicked  
it take the frequencies in the zone.   Min and max and creates a new start and stop variable 
knowing the min and max you know the center and the span.   
The span should be >0   IE if there is only one device.   So we add 10mhz to the from and 10 Mhz to the end and get a new span with buffers
these buffers allow us to have a wider POV
handle_marker_place_all_beg(app_instance, marker_freqs_mhz, console_print_func): from the util yakety yak handler should be called to setup the new StopAsyncIteration





LOOP  GET MARKER DATA() 

that is based on knowing if the orchestration is active
    Check in every 2 seconds IF the tab is open and all the buttons can be seen 
        .orchestrator logic.... log_check_in(self, source_file):
        log_task_event(self, source_file, event)
                    it needs to check in on the orchestrator display

                    orchestrator_logic.py file   get_status 

                    if the status is runnging.... We know all the devices in the zone  so it should then take the center frequency of the device 

                    Check focus device()

                    marker_freqs_mhz = 
                            calll this fucntion of place all 
                            response = handle_marker_place_all_beg(self.app_instance, marker_freqs_mhz, self.console_print_func)
                    
                    it will return the values oo up to 6 markers at a time. 

                    then the markers come back with the peak.    The peaks need to be stored in the CSV markers.CSV in the corresponding PEAK colum 
                    Once a batch of six is done, the progress bar and the peak on the button need to be updated  needs to be updated 
                    then it should move onto the next 6 then next 6 then next six and loop continually   

                    once all the peaks in the zone are done 
                                    handle_trace_data_beg(app_instance, trace_number, start_freq_mhz, stop_freq_mhz, console_print_func)
                                    for trace 1 

                                    then after ffter 3 loops it should calle for trace 2
                                    then after 5 loops it should call  for trace 3  



                        "

    it should set the center to the device that is selected 



end loop  

Function FOCUSDEVICE()

        when a device button is clicked while in this loop - OR if the loop is not running 
                            if runnning interupt the peak scan 
                            if not running do it anyways 
                            it should set the center to the device frequency   handle_freq_center_span_beg ( span based on the tab_markers_child_controls.py )
                                it should get  handle_trace_data_beg(app_instance, trace_number, start_freq_mhz, stop_freq_mhz, console_print_func)
                                for trace 1 2 and 3 
                            it should do this "FOCUS" forever until the device is unselected OR a new zone has been chosen 

