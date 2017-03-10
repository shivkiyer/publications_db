import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def scrub_elements(input_string):
    """
    This function removes leading and trailing white spaces,
    trailing commas as these are the separators between
    BibTex fields, quotes and curly brackets as the value
    of BibTex fields can be enclosed within these. Also
    removed are forward slashes as they are Latex commands
    and the terminating new line character.
    """
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
        while input_string[-1]=="\n" or input_string[-1]=="\r":
            input_string = input_string[:-1]
            if not input_string:
                break

    return input_string


def extract_bibtex_entries(input_file):
    """
    Extract BibTex entires from any block of text.
    """
    collection_of_articles = []
    record = {}

    for line in input_file:
        line = scrub_elements(line)
        if line:
            # The BibTex entry for a publication starts with
            # @article or @inproceedings. So this is the
            # indication of a new publication.
            if line[0]=="@":
                if record:
                    collection_of_articles.append(record)
                record = {}

            new_item = line.split("=")
            if len(new_item)>1:
                if scrub_elements(new_item[0][0:5]).lower()=="title":
                    record["title"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:6]).lower()=="author":
                    record["author"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:8]).lower()=="journal":
                    record["journal"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:10]).lower()=="booktitle":
                    record["booktitle"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:5]).lower()=="year":
                    record["year"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:6]).lower()=="month":
                    record["month"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:7]).lower()=="volume":
                    record["volume"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:7]).lower()=="number":
                    record["number"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:6]).lower()=="pages":
                    record["pages"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:4]).lower()=="doi":
                    record["doi"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:9]).lower()=="abstract":
                    record["abstract"] = scrub_elements(new_item[1])

                if scrub_elements(new_item[0][0:9]).lower()=="keywords":
                    record["keywords"] = scrub_elements(new_item[1])

    return collection_of_articles


def read_ref_file():
    """
    This file reads the references in a text file which are
    in BibTex form. It checks for the fields that are present
    in every publication and adds them to a dictionary. The
    dictionary for each publication is added to a list.
    """

    input_file = open(os.path.join(BASE_DIR, 'input_data_file.txt'), "r")
    collection_of_articles = extract_bibtex_entries(input_file)
    return collection_of_articles



def main():
    collection_of_articles = read_ref_file()
    print(len(collection_of_articles))
    return


if __name__ ==  "__main__":
    main()
