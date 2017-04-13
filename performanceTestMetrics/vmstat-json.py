# this is based on `vmstat -t -n <interval in sec>`


import fileinput
import sys
import json


def validate_and_define_field_names(field_names) :
    """ this is going to check that this vmstat command is 
        returning the fields like we are expecting.  Centos 6 to 
        centos 7 are different for example.. 
        Note that this does not validate timestamp.  All fields after these
        first 17 are timestamp..  that we want to handle differently
        """
    EXPECTED_FIELDS = ['r','b','swpd','free','buff','cache','si','so','bi',
                       'bo','in','cs','us','sy','id','wa','st']
    for i, name in enumerate(EXPECTED_FIELDS):
        if name != field_names[i] :
            raise ValueError( "Execting field %s at index %d but found %s" % (name,i,field_names[i]) )

    return ['procs_r','procs_b','mem_swpd','mem_free','mem_buff','mem_cache',
            'swap_in', 'swap_out','io_in','io_out','system_in','system_cs',
            'cpu_user','cpu_sys','cpu_idle','cpu_wait','cpu_st']


def write_json(field_names, fields):
    field_len = len(fields)
    if field_len <= 17:
        ValueError("Expecting more than 17 fields, are you sure you are printing the timestamp? ")
    # treat the last fields as timestamp.  different systems have different standards.
    # for example  date time and time zone vs date and time.
    timestamp = ' '.join(fields[-(field_len-17):])
    field_dict = dict(zip(field_names, fields))
    splunk_msg = { "ts": timestamp, "app": "vmstat","level":"INFO"}
    splunk_msg.update(field_dict)

    print(json.dumps(splunk_msg))


if sys.version[0] > 2 or sys.version[2] > 6 :
    for line_idx, line in enumerate(sys.stdin.readline()):
        line = line.strip()
        if line_idx ==0 :
            if not line.startswith("procs"):
                raise ValueError("The first line needs to be Procs")
        elif line_idx ==1 :  # field names
            if not line.startswith('r'):
                raise ValueError("the second line should be the line of headings")
            field_names = validate_and_define_field_names(line.split())


        elif line_idx== 2: # toss the "since boot" line.
            pass
        else :
            fields = line.split()
            write_json(field_names,fields)

else: # system greater than python 2.6
    for line_idx,line in enumerate(fileinput.input()):
        line = line.strip()
        if line_idx ==0 :
            if not line.startswith("procs"):
                raise ValueError("The first line needs to be Procs")
        elif line_idx ==1 :  # field names
            if not line.startswith('r'):
                raise ValueError("the second line should be the line of headings")
            field_names = validate_and_define_field_names(line.split())


        elif line_idx== 2: # toss the "since boot" line.
            pass
        else :
            fields = line.split()
            write_json(field_names,fields)


