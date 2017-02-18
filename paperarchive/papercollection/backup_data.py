import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def scrub_elements(input_string):
    if input_string:
        while input_string[0]==" ":
            input_string = input_string[1:]
            if not input_string:
                break

    if input_string:
        while input_string[-1]==" ":
            input_string = input_string[:-1]
            if not input_string:
                break

    if input_string:
        while input_string[-1]==",":
            input_string = input_string[:-1]
            if not input_string:
                break
    
    if input_string:
        for count in range(len(input_string)-1, -1, -1):
            if input_string[count]=='"':
                input_string = input_string[:count] + input_string[count+1:]

    if input_string:
        for count in range(len(input_string)-1, -1, -1):
            if input_string[count]=='\\':
                input_string = input_string[:count] + input_string[count+1:]

    if input_string:
        for count in range(len(input_string)-1, -1, -1):
            if input_string[count]=="{":
                input_string = input_string[:count] + input_string[count+1:]

    if input_string:
        for count in range(len(input_string)-1, -1, -1):
            if input_string[count]=="}":
                input_string = input_string[:count] + input_string[count+1:]

    if input_string:
        while input_string[0]==" ":
            input_string = input_string[1:]
            if not input_string:
                break

    if input_string:
        while input_string[-1]==" ":
            input_string = input_string[:-1]
            if not input_string:
                break

    if input_string:
        while input_string[-1]=="\n" or input_string[-1]=="\r":
            input_string = input_string[:-1]
            if not input_string:
                break

    return input_string


def read_ref_file():
    input_file = open(os.path.join(BASE_DIR, 'input_data_file.txt'), "r")

    collection_of_articles = []
    record = {}

    for line in input_file:

        line = scrub_elements(line)

        if line:
            if line[0]=="@":
##                print "New entry"
                if record:
                    collection_of_articles.append(record)
                record = {}


            new_item = line.split("=")
            if len(new_item)>1:
                if scrub_elements(new_item[0][0:5]).lower()=="title":
##                    print scrub_elements(new_item[1])
                    record["title"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:6]).lower()=="author":
##                    print scrub_elements(new_item[1])
                    record["author"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:8]).lower()=="journal":
##                    print scrub_elements(new_item[1])
                    record["journal"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:10]).lower()=="booktitle":
##                    print scrub_elements(new_item[1])
                    record["booktitle"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:5]).lower()=="year":
##                    print scrub_elements(new_item[1])
                    record["year"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:6]).lower()=="month":
##                    print scrub_elements(new_item[1])
                    record["month"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:7]).lower()=="volume":
##                    print scrub_elements(new_item[1])
                    record["volume"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:7]).lower()=="number":
##                    print scrub_elements(new_item[1])
                    record["number"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:6]).lower()=="pages":
##                    print scrub_elements(new_item[1])
                    record["pages"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:4]).lower()=="doi":
##                    print scrub_elements(new_item[1])
                    record["doi"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:9]).lower()=="abstract":
##                    print scrub_elements(new_item[1])
                    record["abstract"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:9]).lower()=="keywords":
##                    print scrub_elements(new_item[1])
                    record["keywords"] = scrub_elements(new_item[1])

    return collection_of_articles



def main():
    collection_of_articles = read_ref_file()
    print len(collection_of_articles)
    return


if __name__ ==  "__main__":
    main()
