import re
from xml.etree.ElementTree import Element
import Levenshtein as LN
import random
import xml.etree.ElementTree as ET
from datetime import datetime
import itertools

class ResponseError(Exception):
    pass 


def log(string_to_log:str):
    # don't like opening and closing this all the time but still the best way
    with open("log.txt", "a") as log_file:
        log_file.write(string_to_log);
        log_file.write("\n");

# __init__()
root = ET.parse("responses.xml").getroot();
log("\nNEW CHAT AT TIME: ")
log(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# Function to get input
def get_input(question:str = "") -> str:
    x = input(question).lower();
    log(x);
    return x

# Function to print output 
def print_output(output:str): 
    log(f"Outputed: {output}")
    print(output)

# Function to parse input for various tags returns list of tags found
def parse_input(input_msg:str, levenshtein_cutoff:int = 1000) -> list[Element]:
    valid_responses:list[Element] = [];
    closest_tag:Element|None = None;
    closest_distance:int = levenshtein_cutoff + 0xffff;
    response:Element;
    for response in root.findall("reposnse"):
        if response.tag != "reposnse":
            print(f"skipped response with tag {response.tag} ")
        # assert(type(response) != Element, "response was not an element");
        tags_elements = response.findall("tag");
        # if type(tags_elements) != list:
        #     print(f"skipped {tags_elements} because type was {type(tags_elements)}")
        #     continue;
        if len(tags_elements) == 0:
            tags = response.findall("tags"); # only ever one
            assert(len(tags) == 1 );
            messylist = [x.text.split(",") for x in tags if type(x.text) == str]
            tags = messylist[0];
        else:
            tags = [x.text for x in tags_elements if type(x.text) == str];
        for tag in tags:
            if(re.search(tag, input_msg, flags=re.IGNORECASE) != None):
                valid_responses.append(response);
            elif(len(valid_responses) == 0 ):
                dist = LN.distance(tag.lower(), input_msg.lower(), score_cutoff=closest_distance) # type: ignore
                closest_tag = response if dist and dist < closest_distance else closest_tag;
                closest_distance = dist if dist and dist < closest_distance else closest_distance;
    if len(valid_responses) == 0 and levenshtein_cutoff > closest_distance :
        if closest_tag != None:
            valid_responses.append(closest_tag); 
    # for x in tags_found:
        # print(f"from list found: {x.attrib}")
    log(str(valid_responses));
    return valid_responses;

def get_reponse(input_tag:Element) -> str: # type: ignore throws exception not none
    assert input_tag.tag == "reposnse", f"expected response tag reposnse, but got {input_tag.tag}";
    x = input_tag.findall("reply");
    if len(x) > 1:
        returnValue = random.choice(x).text;
        if returnValue != None:
            return returnValue;
        else:
            raise ResponseError;
    elif len(x) == 1:
        returnValue = x[0].text;
        if returnValue != None:
            return returnValue;
        else:
            raise ResponseError("reply had no text value");
    elif len(x) == 0:
        raise ResponseError("Got zero replies out of response");

def get_default_repsonse() -> str:
    #pick default
    a = root.find("default_reposnse");
    assert(a!=None);
    b = a.findall("reply");
    ret = random.choice(b).text;
    if ret != None:
        return ret;
    raise ResponseError;


if __name__ == "__main__":
    welcome_msg:str = "New chat, send a message: ";
    while True:
        user_input:str = get_input(welcome_msg)
        welcome_msg = "";
        log(f"user: {user_input}")

        x:list[Element] = parse_input(user_input);
        temp_response:str = "";
        if len(x) > 0:
            i:int = 0;
            chosen_response:Element = random.choice(x);
            log(f"Chosen tag was {chosen_response}")
            if chosen_response.tag != "reposnse":
                raise ResponseError;
            temp_response:str = get_reponse(chosen_response);
        
        response:str = temp_response if temp_response != "" else get_default_repsonse();
        print_output(response)
