import csv 

def parse_rtb():
    with open ("/Users/ashwjosh/IxiaProjects/IxOS/Utilities/Python/route-table-inet0-0127.log") as f:
        file_lines = f.readlines()
        
    dict_values = {}

    list_of_dict_values = []

    for line in file_lines:
       
        s_line = line.split()
        if  s_line[0].startswith("*"): #Host Line
            #print(dict_values)
            if dict_values:
                list_of_dict_values.append(dict_values)
            dict_values = {}
            m = []
            #print(s_line[2])
            dict_values["ip"] = s_line[2]
            #print(s_line[2])
            
            print(s_line)
            
            if len(s_line) <= 7 and s_line[-1].lower() == "i":
                dict_values["END_CHAR"] = s_line[-1].lower()
            elif len(s_line) <= 7 and s_line[-1].lower() != "i":
                dict_values["END_CHAR"] = "i"
            else:
                for item in s_line[7:]:
                    try:
                        if "." in item:
                            item = item[:-2]
                        elif int(item):
                            item = str(item)
                        m.append(item)
                        
                    except:
                        if item not in ["\n", ""]:
                            if item.strip() == "?":
                                dict_values["END_CHAR"] = "i"
                            elif item.strip() == "E":
                                dict_values["END_CHAR"] = "e"
                            else:
                                dict_values["END_CHAR"] = item.strip().lower()
            
                dict_values["AS_PATH"] = "_".join(m)
                #print(",".join(m))
        #Finding Next hop
        for item in s_line:
            if '>' in item:
                dict_values.update({"NH": item[1:]})
            
    
                
        #list_of_dict_values.append(dict_values)
        
    return list_of_dict_values
     
def write_to_file(list_of_dict_values):
    """
    e,1.0.0.0/24,108.170.240.98,,,,<1>,i
    e,1.0.4.0/22,4.14.96.73,,,,<1>,i
    """
    # field names 
    fields = ["#", "Prefix/Mask" ,"Nexthop" ,"MED", "LocalPref","Weight","ASPath","Origin"] 
    rows = []
    for record in list_of_dict_values:
    # data rows of csv file 
        print(record)
        prefix_mask = record.get("ip")
        next_hop = record.get("NH")
        
        ap =  record.get("AS_PATH")
        end_char = record.get("END_CHAR")
        
        if not ap:
            ap = "1"
        as_path = f'<{ap}>'
       
        row = ["e", prefix_mask, next_hop,"","","",as_path,end_char]
        rows.append(row)
    
    # name of csv file 
    filename = "ipv4_route_records.csv"
        
    # writing to csv file 
    with open(filename, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(rows)    
            

list_of_dict_values = parse_rtb()
write_to_file(list_of_dict_values)
    
