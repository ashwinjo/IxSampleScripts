import re
import csv
 
def get_as_path(as_string):
    text = as_string.split(",")[0].strip()
 
    numbers = re.findall(r'\d+', text)
    return  "{"+'_'.join(numbers)+"}"
 
def write_to_csv(data, file_path):
    # Open the CSV file in write mode
    with open(file_path, 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile)
       
        # Write the header row (if needed)
        header = ["#Version:1","","","","","","",""]  # Replace with your column names
        writer.writerow(header)
       
        header = ['#','Prefix/Mask','Nexthop','MED','LocalPref','Weight','ASPath','Origin']  # Replace with your column names
        writer.writerow(header)
       
        # Write the data rows
        for row in data:
            writer.writerow(row)

def get_data():
    # Replace with path to the route table file 
    with open("juniper-ier-bgp.txt", "r+") as f:
       
        list_of_lines = f.readlines()
        for line in list_of_lines:
            if "*[BGP" in line:
                s_line = line.split()
                # ['1.0.4.0/22', '*[BGP/170]', '4d', '13:21:43,', 'MED', '80', 'localpref', '300', 'from', '104.44.3.13']
                prefix_mask =  s_line[0]
                med = s_line[5][:-1]
                local_pref = s_line[7][:-1]
                index = list_of_lines.index(line)
                aspath = get_as_path(list_of_lines[index+1])
                ##,Prefix/Mask,Nexthop,MED,LocalPref,Weight,ASPath,Origin
                # e,54.235.146.0/24,0.0.0.0,0,0,0,{48048_16074_17903_28958},i
                data.append(["e",prefix_mask,"0.0.0.0",med, local_pref, "0", aspath, "i"])
    return data
       
 
if __name__ == "__main__":
    data = []
    # Replace with path to the store the converted file to
    file_path = 'output.csv'
    data_to_write = get_data()
    write_to_csv(data_to_write, file_path)            
