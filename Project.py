import gc
import pyb
import cotask
import task_share


def readComm():
    """
    Task which reads motor commands
    """
    
    # define location of csv file
    file_path = './motor_commands.csv'
    
    with open(file_path, 'r') as file:
        while True:
            line_Str = file.readline().split(',')
            if len(line_Str) > 1:
                share0.put (float(line_Str[0]))
                share1.put (float(line_Str[1]))
                share2.put (float(line_Str[2]))
                share3.put (float(line_Str[3]))
                share4.put (int(line_Str[4][0]))
            else:
                break
            yield (0)


# TODO: Actually write motor commands!
def writeComm ():
    """
    Task which writes motor commands
    """
    while True:
        # Replace print motor commands with write motor commands to motor
        print ("Motor0: {:}, Motor1: {:}, Motor2: {:}, Motor3: {:}, Grab: {:}".format (share0.get(),share1.get(),share2.get(),share3.get(),share4.get()), end='');
        print ('')

        yield (0)


if __name__ == "__main__":
    share0 = task_share.Share ('f', thread_protect = False, name = "Motor 0")
    share1 = task_share.Share ('f', thread_protect = False, name = "Motor 1")
    share2 = task_share.Share ('f', thread_protect = False, name = "Motor 2")
    share3 = task_share.Share ('f', thread_protect = False, name = "Motor 3")
    share4 = task_share.Share ('B', thread_protect = False, name = "Grab")
    
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    taskRead = cotask.Task (readComm, name = 'Task_Read', priority = 1, 
                         period = 100, profile = True, trace = False)
    taskWrite = cotask.Task (writeComm, name = 'Task_Write', priority = 2, 
                         period = 100, profile = True, trace = False)
    cotask.task_list.append (taskRead)
    cotask.task_list.append (taskWrite)
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if any 
    # character is received through the serial port
    vcp = pyb.USB_VCP ()
    while not vcp.any ():
        cotask.task_list.pri_sched ()

    # Empty the comm port buffer of the character(s) just pressed
    vcp.read ()

    # Print a table of task data and a table of shared information data
    print ('\n' + str (cotask.task_list))
    print (task_share.show_all ())
    print (task1.get_trace ())
    print ('\r\n')