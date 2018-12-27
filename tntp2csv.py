with open("ChicagoSketch_trips.tntp.txt", "r") as f:
    outFile = open("demand.dat", "w")  # IVT, WT, WK, TR
    tmpOut = "origin\tdest\tdemand"
    outFile.write(tmpOut + "\n")
    for line in f:
        line = line.rstrip()  # we're not interested in the newline at the end
        if not line:  # empty line, skip
            continue
        if line.startswith("Origin"):
            origin_no = int(line[7:].strip())  # grab the integer following Origin
        else:
            elements = line.split(";")  # get our elements by splitting by semi-colon
            for element in elements:  # loop through each of them:
                if not element:  # we're not interested in the last element
                    continue
                element_no, element_value = element.split(":")  # get our pair
                # beware, these two are now most likely padded strings!
                # that's why we'll strip them from whitespace and convert to integer/float
                if(origin_no != int(element_no.strip())):
                    tmpOut = str(origin_no) + "\t" + str(element_no.strip()) + "\t" + element_value.strip()
                    outFile.write(tmpOut + "\n")
    outFile.close()

                    #od[(origin_no, int(element_no.strip()))] = 2*float(element_value.strip())
                    #staz.add(origin_no)


